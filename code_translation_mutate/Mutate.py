import json, ijson
import libcst as cst
from libcst.tool import dump
from tqdm import tqdm
import inspect
import traceback
#import imp
import subprocess
import time
import timeout_decorator
import colorit
import re
from itertools import permutations
import subprocess
import tempfile
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
import os
import sys
sys.path.append("..")
from util.mutators import *
from util.util import *
#from mutators import *

    
def CODE_PRINT(data):
    code = data["code"]
    id = data["id"]
    #language = data["language"]
    #test_IO = data["test_IO"]
    #input = test_IO[0]["input"]
    #output = test_IO[0]["output"]
    
    highlight_code = highlight(code, PythonLexer(), TerminalFormatter())

    print(f"[*] Id: {id}")
    #print(f"[*] Language: {language}")
    #print(f"[*] Input: {input}\n[*] Output: {output}")
    print(f"[*] Code:\n {highlight_code}")


@timeout_decorator.timeout(5)
def execute_code(code: str, input: str):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp:
        temp.write(code)
        temp_path = temp.name
    try:
        res = subprocess.run(['python', temp_path], 
                       input=input, 
                       capture_output=True, 
                       text=True)
    except Exception as e:
        ERR_PRINT('Execution error:', e)
        exit(1)
    finally:
        os.remove(temp_path)
        return res

def evaluate_code(mutated_code: str, input: str, output: str):
    try:
        output1 = execute_code(mutated_code, input).stdout
        #output1 = output1.stdout
    except Exception as e:
        print('str(Exception):\t', str(Exception))
        print('str(e):\t\t', str(e))
        print('repr(e):\t', repr(e))
        return False
    else:
        if '\\n' in output:
            output = output.replace('\\n','\n')
        if '\\\\' in output:
            output = output.replace('\\\\','\\')
        if output[0] == output[-1] == "'" :
            output1 = str(output1)
            output = output[1:-1]
            #return str(output1) == output[1:-1]
        if str(output1) != output:
            INFO_PRINT('Different results:', f"output = {output}, output1 = {output1}")
            return False
        return True

def mutate_dataset_once(mutator, dataset):
    new_dataset = []
    new_id = 0
    for idx in range(0, len(dataset)):
        code = dataset[idx]["code"]
        if dataset[idx]["id"] in SKIP_LIST:
            continue
        #test_IO = dataset[idx]["test_IO"]
        if "old_id" in dataset[idx].keys():
            original_id = dataset[idx]["old_id"]
        else:
            original_id = dataset[idx]["id"]
        #CODE_PRINT(dataset[idx])
        #if original_id in SKIP_LIST:
        #    continue
        if "import java" in code:
            continue
        try:
            new_code = mutate(code, mutator)
        except Exception as ex:
            ERR_PRINT('Error when mutating:',str(mutator))
            CODE_PRINT(dataset[idx])
            ERR_PRINT('Exception:\n',ex)
            traceback.print_exc()
            exit(1)
        new_data = {#'language': "Python",
                    'code': new_code, 
                    #'test_IO': test_IO,
                    'input': dataset[idx]["input"],
                    'output': dataset[idx]["output"],
                    'id':f"{mutator.__name__}_sample_from_{original_id}_to_{new_id}", 
                    'old_id':original_id}
        if new_code != code:
            #CODE_PRINT(new_data)
            new_dataset.append(new_data)
            new_id += 1
    INFO_PRINT(f"Mutated dataset with mutator {mutator.__name__}:", new_id+1)
    return new_dataset

def multi_mutate(mutators, dataset_path):
    dataset = load_dataset(dataset_path)
    for mutator in mutators:
        dataset = mutate_dataset_once(mutator, dataset)
    return dataset
    

def exclude_dataset(dataset_path, error_code_idx):
    dataset = load_dataset(dataset_path)
    new_dataset = []
    for idx,line in enumerate(dataset):
        if idx in error_code_idx:
            continue
        new_dataset.append(line)
    # Reindexing
    for idx,line in enumerate(new_dataset):
        new_line = re.sub(r'\d+$', str(idx), line['id'])
        line['id'] = new_line
    save_data(new_dataset, dataset_path)

def evaluate_dataset(dataset_path):
    new_dataset = load_dataset(dataset_path)
    error_code_idx = []
    for idx in range(0, len(new_dataset)):
        code = new_dataset[idx]["code"]
        input = new_dataset[idx]["input"]
        output = new_dataset[idx]["output"]
        print(f"[*] {idx}/{len(new_dataset)}")
        if not evaluate_code(code, input, output):
            print(f'[*] Error generated code: {idx}')
            error_code_idx.append(idx)
    print(f"{len(error_code_idx)} problematic code generated: {error_code_idx}")
    return error_code_idx

def MultiMutate():
    res = dict()
    multi_path = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/code_reasoning/new_data/MultiMutated/two"
    for a in ASSIGN:
        for b in LOOP:
            for c in JUMP:
                #MUTATORS = [a, b, c]
                for MUTATORS in [[a,b],[a,c],[b,c]]:
                    INFO_PRINT('Choose mutators:',' '.join(map(lambda x:x.__name__, MUTATORS)))
                    perms = list(permutations(MUTATORS, len(MUTATORS)))
                    max_num = 0
                    max_str = ""
                    for idx, mutator_tuple in enumerate(perms):
                        tmp_str = ' -> '.join(map(lambda x:x.__name__, mutator_tuple))
                        INFO_PRINT(f'[{idx+1}/{len(perms)}]',f'Mutate with: {tmp_str}')
                        new_dataset = multi_mutate(mutator_tuple, DATASET)
                        new_name = "_".join(map(lambda x:x.__name__, mutator_tuple))
                        
                        max_num = len(new_dataset) if len(new_dataset) >= max_num else max_num
                        max_str = new_name if len(new_dataset) >= max_num else max_str

                    INFO_PRINT(info=f'max_num = {max_num}, {max_str}')
                    res[max_str] = max_num
                    save_data(new_dataset, f"{multi_path}/{max_str}_{max_num}.jsonl")
                #err_idx = evaluate_dataset(f"{multi_path}/{max_str}.jsonl")
                #flag = input('Exclude them? [0/1]')
                #flag = '1'
                #if flag == '1':
                #    exclude_dataset(f"{multi_path}/{new_name}.jsonl", err_idx)
    return res
                
if __name__ == "__main__":
    # Load the dataset
    SKIP_LIST = ['codeforces_379_A', 'atcoder_ABC150_D', 'Python/106']
    DATASET = "/home/WORK/PAPER4/LLMreasoning/cruxeval/data/cruxeval.jsonl"
    
    #DATASET = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/code_translation/Datasets/CodeLingua/avatar/avatar.jsonl"
    #DATASET = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/code_translation/Datasets/CodeLingua/codenet/codenet_python.jsonl"
    #DATASET = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/code_translation/Datasets/TransCoder/cleaned_testable_samples_python.jsonl"
    #DATASET = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/code_translation/Datasets/Humaneval-x/humanevalx-python.jsonl"
    #ASSIGN = [AugAssign2Assign, Assign2Ternary, Add_IndependentVar, AssignUnfoldding, ConstantUnfoldding, StringUnfoldding]
    ASSIGN = [ConstantUnfoldding]
    LOOP = [For2While]
    #JUMP = [IfReverse, IfAddShortCircuiting]
    JUMP = [IfAddShortCircuiting]

    res = MultiMutate()
    for str, num in res.items():
        print(str, num)
    #MUTATORS = ASSIGN + LOOP + JUMP
    
    #dataset = load_dataset(DATASET)
    #target_dir = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/code_translation/mutated_datasets/MultiMutated/CodeLingua"
    #for mutator in MUTATORS:
    #    new_dataset = mutate_dataset_once(mutator, dataset)
    #    save_data(new_dataset, target_dir+f"/{mutator.__name__}.jsonl")
