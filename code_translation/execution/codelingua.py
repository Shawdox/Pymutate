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

from util.helper import get_output_file_path_for_translation, load_dataset_with_retry

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
parser.add_argument("--dataset", type=str, help="Dataset")
parser.add_argument("--model", type=str, help="Model name")
parser.add_argument("--temp", type=float, help="Temperature")
parser.add_argument("--nsample", type=int, default=10, help="N sample in Pass@k")
parser.add_argument("--mutate", type=str, help="Mutate method")
parser.add_argument("--curtime", type=str, help="Current time")
parser.add_argument("--sourlang", type=str, default="Python", help="Source language")
parser.add_argument("--tarlang", type=str, default="Java", help="Target language")

args = parser.parse_args()

dataset_name = args.dataset
model_name = args.model
temperature = args.temp
nsample = args.nsample
mutate_method = args.mutate
current_time = args.curtime
source_lang = args.sourlang
target_lang = args.tarlang



file_path = get_output_file_path_for_translation(dataset_name, model_name, mutate_method, temperature, current_time)
if dataset_name == "codenet":
    ds = load_dataset_with_retry("iidai/codenet")
elif dataset_name == "avatar":
    ds = load_dataset_with_retry("iidai/avatar")
else:
    print("Check dataset name.")
    sys.exit(1)

ds = ds['train'].filter(lambda x: x['language'] == 'Python')


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

for item in tqdm(samples):
    # 将各个变量解包
    old_id = item.get("id")
    code_type = item.get("code_type")
    test_code = item.get("code")
    generated_content = item.get("generated_content")
    success_flag = item.get("execution_success")
    raw_generated_content = item.get("raw_generated_content")

    # 根据 id 找到对应的 f_in 和 f_out
    test_io = ds.filter(lambda x: x['id'] == old_id)[0]['test_IO'] 
    f_in = test_io[0]['input']
    f_out = test_io[0]['output']

    # 提取生成的 Java 代码
    target_lang = target_lang.lower()
    if raw_generated_content.find(f"```{target_lang}") != -1:
        generated_content = raw_generated_content[raw_generated_content.find(f"```{target_lang}") + len(f"```{target_lang}"):]
        exec_code = generated_content[:generated_content.find("```")]
    else:
        exec_code = generated_content

    # 编译并执行 Java 代码
    try:
        with change_dir('tmp_' + model_name.split("/")[-1]):
            # 保存生成的 Java 代码到 Main.java 文件
            java_file_path = './Main.java'
            with open(java_file_path, 'w') as f:
                f.write(exec_code)
    
            # 编译 Java 代码
            compile_process = subprocess.run(['javac', java_file_path],\
                                 check=True, capture_output=True, text=True, timeout=10)
            p = subprocess.Popen(f"java Main", \
                    cwd=f"./", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            try:
                stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=20)
            except subprocess.TimeoutExpired:
                pass

        try:
            if float(stdout.decode())%1 == 0:
                stdout = str(int(float(stdout.decode())))
                f_out = str(int(float(f_out)))
            else:
                # find how many decimal points are there in the output
                stdout_temp = stdout.decode().strip()
                f_out_temp = f_out.strip()
                f_out_total_dec_points = len(f_out_temp.split(".")[1])
                stdout_total_dec_points = len(stdout_temp.split(".")[1])
                min_dec_points = min(f_out_total_dec_points, stdout_total_dec_points)

                stdout = str(round(float(stdout.decode()), min_dec_points))
                f_out = str(round(float(f_out), min_dec_points))

        except:
            try: # if stdout is already decoded as String, then pass
                stdout = stdout.decode()
            except:
                pass
        
        if(stdout.strip()==f_out.strip()):
            success_flag = True

    except subprocess.TimeoutExpired as e:
        print(f"Error: The process timed out. {e}")
    except subprocess.CalledProcessError as e:
        # print(f"Error: {e}")
        # print("Compilation or runtime error occurred.")
        pass

    item["generated_content"] = exec_code
    item["execution_success"] = success_flag

with open(file_path, "w", encoding="utf-8") as file:
    for item in samples:
        file.write(json.dumps(item) + "\n")