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
import eventlet
import colorit
import sys, traceback

DATASET = "/home/WORK/PAPER4/LLMreasoning/cruxeval/data/cruxeval.jsonl"

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
    INFO_PRINT("Dataset loaded:", f"{len(dataset)} entries.")
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
        id = dataset[idx]["id"]
        
        new_code = mutate(code, mutator)
        new_data = {'code': new_code, 
                    'input': input, 
                    'output': output, 
                    'id':f"{mutator.__name__}_sample_from_{idx}_to_{new_id}", 
                    'old_id':id}
        if new_code != code:
            #CODE_PRINT(new_data)
            new_dataset.append(new_data)
            new_id += 1
    INFO_PRINT(f"Mutate dataset with mutator {mutator.__name__}:", new_id+1)
    save_data(new_dataset, f'./new_data/{mutator.__name__}.jsonl')

def exclude_dataset(dataset_path, error_code_idx):
    dataset = load_dataset(dataset_path)
    new_dataset = []
    for idx,line in enumerate(dataset):
        if idx in error_code_idx:
            continue
        new_dataset.append(line)
    
    save_data(new_dataset, dataset_path)
        
        
# Load the dataset
SKIP_LIST = [289, 258, 375, 382, 452, 490, 711]
#MUTATORS = [For2While, AugAssign2Assign, Deadcode_Assign2Ternary, 
#            Deadcode_Add_IndependentVar, AssignUnfoldding, ConstantUnfoldding,]
MUTATORS = [AugAssign2Assign]
#dataset = []
#with open(DATASET, 'r') as f:
#    for line in f:
#        dataset.append(json.loads(line))
#INFO_PRINT("Dataset loaded:", f"{len(dataset)} entries.")
dataset = load_dataset(DATASET)

# mutate
#for mutator in MUTATORS:
#    mutate_dataset_once(mutator, dataset)

#num = 0
#for idx in range(0, len(dataset)):
#    code = dataset[idx]["code"]
#    input = dataset[idx]["input"]
#    output = dataset[idx]["output"]
#    if 'for ' in code:
#        num += 1
#print(f'num = {num}')
# Evaluate the code by running it
evaluate_dataset = "/home/WORK/PAPER4/LLMreasoning/mutate_CRUXEval/new_data/Deadcode_Assign2Ternary.jsonl"
new_dataset = load_dataset(evaluate_dataset)
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

exclude_dataset(evaluate_dataset, [48,65])
    
