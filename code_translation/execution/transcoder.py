import json
import argparse
import os
import sys
import subprocess
from contextlib import contextmanager
from tqdm import tqdm

current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)

from util.helper import get_output_file_path_for_translation, modify_generated_content

from datasets import disable_progress_bar
disable_progress_bar()

@contextmanager
def change_dir(new_dir):
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    
    prev_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(prev_dir)


parser = argparse.ArgumentParser(description="A simple argument parser.")
parser.add_argument("--model", type=str, help="Model name")
parser.add_argument("--temp", type=float, help="Temperature")
parser.add_argument("--nsample", type=int, default=5, help="N sample in Pass@k")
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

file_path = get_output_file_path_for_translation("transcoder", model_name, mutate_method, temperature, current_time)

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

to_remove = []

for item in tqdm(samples):
    # 将各个变量解包
    old_id = item.get("id")
    code_type = item.get("code_type")
    test_code = item.get("code")
    generated_content = item.get("generated_content")
    success_flag = item.get("execution_success")
    raw_generated_content = item.get("raw_generated_content")

    generated_content = modify_generated_content(raw_generated_content)

    if "Java\n" in generated_content:
        generated_content = generated_content.replace("Java\n", "")

    if "static" not in generated_content:
        generated_content = generated_content.replace("public", "public static")

    ori_java_file_path = f'code_translation/Datasets/TransCoder/transcoder_evaluation_gfg/java/{old_id}.java'
    # 读取原始文件内容
    try:
        with open(ori_java_file_path, 'r') as file:
            content = file.read()
    except:
        to_remove.append(old_id)
        continue

    # 替换 //TOFILL 标记为生成的内容
    updated_content = content.replace('//TOFILL', generated_content)

    # 编译并执行 Java 代码
    try:     
        with change_dir('tmp_' + model_name.split("/")[-1]):    
             # 定义新文件路径
            tmp_model_name = model_name.split("/")[-1]
            java_file_path = f"{old_id}.java"

            # 将更新后的内容写入新的文件
            with open(java_file_path, 'w') as file:
                file.write(updated_content)
               
            compile_process = subprocess.run(['javac', java_file_path], check=True, capture_output=True, text=True, timeout=10)

            p = subprocess.Popen(f"java {old_id}", cwd=f"./", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            try:
                stdout, stderr_data = p.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                p.kill()
        
        if stdout: 
            n_success = "1"
            total = "2"
            try:
                n_success, total = stdout.decode().replace("#Results:", "").split(",")
                success_flag = True if int(n_success.strip()) == int(total.strip()) else False
            except:
                success_flag = False

    except subprocess.TimeoutExpired as e:
        print(f"Error: The process timed out. {e}")
    except subprocess.CalledProcessError as e:
        # print(f"Error: {e}")
        # print("Compilation or runtime error occurred.")
        pass

    item["generated_content"] = generated_content
    item["execution_success"] = success_flag

with open(file_path, "w", encoding="utf-8") as file:
    for item in samples:
        if item.get("id") not in to_remove:
            file.write(json.dumps(item) + "\n")