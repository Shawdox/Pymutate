import json
import argparse
import numpy as np
import os
import sys
from collections import defaultdict, Counter

current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)

from util.helper import get_output_file_path

def pass_at_k(n, c, k):
    """
    :param n: total number of samples
    :param c: number of correct samples
    :param k: k in pass@$k$
    """
    if n - c < k: return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

parser = argparse.ArgumentParser(description="A simple argument parser.")
parser.add_argument("--model", type=str, help="Model name")
parser.add_argument("--temp", type=float, help="Temperature")
parser.add_argument("--nsample", type=int, default=10, help="N sample in Pass@k")
parser.add_argument("--mutate", type=str, help="Mutate method")
parser.add_argument("--curtime", type=str, help="Current time")
parser.add_argument("--passatk", type=int, help="K of Pass@k")
args = parser.parse_args()

model_name = args.model
temperature = args.temp
nsample = args.nsample
mutate_method = args.mutate
current_time = args.curtime
passatk = args.passatk


file_path = get_output_file_path(model_name, mutate_method, temperature, current_time)

original_success_counts = defaultdict(int)
modified_success_counts = defaultdict(int)
original_success_passat = {}
modified_success_passat = {}


# 用于存储每行内容的列表
samples = []

# 逐行读取 jsonl 文件
with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        # 解析 JSON 数据
        try:
            record = json.loads(line.strip())
            samples.append(record)
        except:
            pass
        

for item in samples:
    # 将各个变量解包
    old_id = item.get("id")
    code_type = item.get("code_type")
    test_code = item.get("code")
    generated_content = item.get("generated_content")
    success_flag = item.get("execution_success")
    raw_generated_content = item.get("raw_generated_content")

    if code_type == "original" and success_flag == True:
        original_success_counts[old_id] += 1
    elif code_type == "modified" and success_flag == True:
        modified_success_counts[old_id] += 1


for id, count in original_success_counts.items():
    original_success_passat[id] = pass_at_k(nsample, count, passatk)

for id, count in modified_success_counts.items():
    modified_success_passat[id] = pass_at_k(nsample, count, passatk)

print(original_success_passat, modified_success_passat)


original_pass_at_k = sum(original_success_passat.values()) / (len(samples) / 2 / nsample) * 100
modified_pass_at_k = sum(modified_success_passat.values()) / (len(samples) / 2 / nsample) * 100

with open(file_path, 'a') as file:
    file.write(f"Original Pass@k: {original_pass_at_k}\n")
    file.write(f"Modified Pass@k: {modified_pass_at_k}\n")
    file.write(f"model: {model_name}\n")
    file.write(f"mutate method: {mutate_method}\n")
    file.write(f"temperature: {temperature}\n")