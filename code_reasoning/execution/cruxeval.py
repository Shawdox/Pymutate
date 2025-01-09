import json
import argparse
import os
import sys

current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)

from util import timeout
from util.helper import get_output_file_path


parser = argparse.ArgumentParser(description="A simple argument parser.")
parser.add_argument("--model", type=str, help="Model name")
parser.add_argument("--temp", type=float, help="Temperature")
parser.add_argument("--nsample", type=int, default=10, help="N sample in Pass@k")
parser.add_argument("--mutate", type=str, help="Mutate method")
parser.add_argument("--curtime", type=str, help="Current time")
args = parser.parse_args()

model_name = args.model
temperature = args.temp
nsample = args.nsample
mutate_method = args.mutate
current_time = args.curtime


file_path = get_output_file_path(model_name, mutate_method, temperature, current_time)

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

    generated_content = generated_content.replace('`', '').replace('python', '').strip()
    if "==" in generated_content and \
        ('gpt' in model_name or 'llama-3.1' in model_name or 'deepseek' in model_name or 'qwen' in model_name):
        generated_content = generated_content.split("==")[-1].strip()
    generated_content = generated_content.split("\n", 1)[0].split("# done", 1)[0]

    exec_code = test_code + generated_content

    try:
        timeout.exec_with_timeout(exec_code)
        success_flag = True
    except Exception as e:
        pass

    item["generated_content"] = generated_content
    item["execution_success"] = success_flag

with open(file_path, "w", encoding="utf-8") as file:
    for item in samples:
        file.write(json.dumps(item) + "\n")