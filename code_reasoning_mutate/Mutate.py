import json
import libcst as cst
from libcst.tool import dump
from mutators import *
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from tqdm import tqdm
import inspect
import imp
import subprocess
import time
import timeout_decorator
import colorit
import re
from itertools import permutations

def INFO_PRINT(prefix = 'INFO:', info = ''):
    prefix = colorit.color("[*] " + prefix, colorit.Colors.green)
    print(prefix, info)
def ERR_PRINT(prefix = 'ERROR:', info = ''):
    prefix = colorit.color("[*] " + prefix, colorit.Colors.red)
    print(prefix, info)
def CODE_PRINT(data):
    code = data["code"]
    id = data["id"]
    input = data["input"]
    output = data["output"]
    highlight_code = highlight(code, PythonLexer(), TerminalFormatter())
    print(f"[*] Id: {id}")
    print(f"[*] Input: {input}\n[*] Output: {output}")
    print(f"[*] Code:\n {highlight_code}")


def save_data(data, path):
    with open(path,'w') as f:
        for entry in data:
            json_line = json.dumps(entry)
            f.write(json_line + '\n')

def load_dataset(path):
    dataset = []
    with open(path, 'r') as f:
        for line in f.readlines():
            dataset.append(json.loads(line))
    #INFO_PRINT("Dataset loaded:", f"{len(dataset)} entries.")
    return dataset

@timeout_decorator.timeout(3)
def execute_code(code: str, input: str):
    with open('./tmp.py','w') as file:
        file.write(code)
    import tmp
    imp.reload(tmp)
    sig = inspect.signature(tmp.f)
    para_len = len(sig.parameters)
    if para_len:
        args = eval(input)
        #print(f"args = {args}, type = {type(args)}")
        if para_len == 1:
            output = tmp.f(args)
        else:
            output = tmp.f(*args)
    else:
        output = tmp.f()
    return output

def evaluate_code(mutated_code: str, input: str, output: str):
    try:
            output1 = execute_code(mutated_code, input)
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
        input = dataset[idx]["input"]
        output = dataset[idx]["output"]
        if "old_id" in dataset[idx].keys():
            original_id = dataset[idx]["old_id"]
        else:
            original_id = idx
        #CODE_PRINT(dataset[idx])
        try:
            new_code = mutate(code, mutator)
        except Exception as ex:
            ERR_PRINT('Error when mutating:',str(mutator))
            CODE_PRINT(dataset[idx])
            ERR_PRINT('Exception:\n',ex)
            exit(1)
        new_data = {'code': new_code, 
                    'input': input, 
                    'output': output, 
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
    multi_path = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/new_data/MultiMutated"
    for a in ASSIGN:
        for b in LOOP:
            for c in JUMP:
                MUTATORS = [a, b, c]
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
                save_data(new_dataset, f"{multi_path}/{max_str}.jsonl")
                err_idx = evaluate_dataset(f"{multi_path}/{max_str}.jsonl")
                #flag = input('Exclude them? [0/1]')
                flag = '1'
                if flag == '1':
                    exclude_dataset(f"{multi_path}/{new_name}.jsonl", err_idx)
                
if __name__ == "__main__":
    # Load the dataset
    DATASET = "/home/WORK/PAPER4/LLMreasoning/cruxeval/data/cruxeval.jsonl"

    ASSIGN = [AugAssign2Assign, Assign2Ternary, Add_IndependentVar, AssignUnfoldding, ConstantUnfoldding, StringUnfoldding]
    LOOP = [For2While]
    JUMP = [IfReverse, IfAddShortCircuiting]

    MultiMutate()


    
