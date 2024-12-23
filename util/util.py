import colorit
import os, sys, json, ijson

def INFO_PRINT(prefix = 'INFO:', info = ''):
    prefix = colorit.color("[*] " + prefix, colorit.Colors.green)
    print(prefix, info)

def ERR_PRINT(prefix = 'ERROR:', info = ''):
    prefix = colorit.color("[*] " + prefix, colorit.Colors.red)
    print(prefix, info)
    
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