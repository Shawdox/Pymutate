import json
import argparse
import re
import os
import sys
import subprocess

current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)

from util.helper import get_output_file_path

def extract_method_name_java(code):
    # 匹配方法定义的正则表达式
    pattern = re.compile(r"(public|private|protected)?\s?(static)?\s?(\w+|\w+\[\])\s(\w+)\s?\(\s?([\w\s,]*?)\s?\)")
    
    # 查找匹配项
    method_info = pattern.findall(code)
    return method_info[0][3]

def modify_generated_content(generated_content):
    # 提取生成的 Java 函数
    new_sample = ""
    line_lst = [i for i in generated_content.strip().split("\n") if i.strip() != ""]

    start = False
    for line in line_lst:
        stripped_line = line.strip()
        if not start:
            if not re.match(r"^(public|private|protected|import|static)", stripped_line):
                continue
            else:
                start = True
        if not stripped_line or stripped_line == "}":
            break
        elif not line.startswith(" ") and stripped_line != "}":
            break
        else:
            new_sample += line + "\n"
    
    generated_content = new_sample.replace(extract_method_name_java(new_sample), "f_filled")
    return generated_content


parser = argparse.ArgumentParser(description="A simple argument parser.")
parser.add_argument("--model", type=str, help="Model name")
parser.add_argument("--temp", type=float, help="Temperature")
parser.add_argument("--nsample", type=int, default=10, help="N sample in Pass@k")
parser.add_argument("--mutate", type=str, help="Mutate method")
parser.add_argument("--curtime", type=str, help="Current time")
parser.add_argument("--sourlang", type=str, default="Python", help="Source language")
parser.add_argument("--tarlang", type=str, default="Java", help="Target language")

args = parser.parse_args()

model_name = args.model
temperature = args.temp
nsample = args.nsample
mutate_method = args.mutate
current_time = args.curtime
source_lang = args.sourlang
target_lang = args.tarlang

file_path = get_output_file_path(model_name, mutate_method, temperature, current_time)

# 用于存储每行内容的列表
samples = []

# 逐行读取 jsonl 文件
with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        # 解析 JSON 数据
        record = json.loads(line.strip())
        samples.append(record)

for item in samples:
    # 将各个变量解包
    old_id = item.get("id")
    code_type = item.get("code_type")
    test_code = item.get("code")
    generated_content = item.get("generated_content")
    success_flag = item.get("execution_success")
    raw_generated_content = item.get("raw_generated_content")

    generated_content = modify_generated_content(generated_content)

    ori_java_file_path = f'TransCoder/transcoder_evaluation_gfg/java/{id}.java'
    # 读取原始文件内容
    with open(ori_java_file_path, 'r') as file:
        content = file.read()

    # 替换 //TOFILL 标记为生成的内容
    updated_content = content.replace('//TOFILL', generated_content)

    # 定义新文件路径
    java_file_path = f"./tmp/{id}.java"

    # 将更新后的内容写入新的文件
    with open(java_file_path, 'w') as file:
        file.write(updated_content)

    # 编译并执行 Java 代码
    try:                        
        compile_process = subprocess.run(['javac', java_file_path], check=True, capture_output=True, text=True, timeout=10)

        p = subprocess.Popen(f"java {id}", cwd=f"./tmp", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        try:
            stdout, stderr_data = p.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            pass

        if stdout: 
            try:
                n_success, total = stdout.replace("#Results:", "").split(",")
                success_flag = True if n_success == total else False
            except:
                success_flag = False

    except subprocess.TimeoutExpired as e:
        print(f"Error: The process timed out. {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Compilation or runtime error occurred.")

    item["generated_content"] = generated_content
    item["execution_success"] = success_flag

with open(file_path, "w", encoding="utf-8") as file:
    for item in samples:
        file.write(json.dumps(item) + "\n")