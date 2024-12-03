from tqdm import tqdm
from datasets import load_dataset
from openai import OpenAI
from fireworks.client import Fireworks
import random
from datetime import datetime
import json
import argparse
import traceback
import os
import requests
from util import mutate, timeout

prompt = f"""Based on the given Python code, which may contain errors, complete the assert statement with the output when executing the code on the given test case. Do NOT output any extra information, even if the function is incorrect or incomplete. Output "# done" after the assertion.
"""

parser = argparse.ArgumentParser(description="A simple argument parser example.")
parser.add_argument("--model", type=str, help="Model name")
parser.add_argument("--varlen", type=int, help="Substitute variable length")
parser.add_argument("--temp", type=float, help="Temperature")
parser.add_argument("--passat", type=int, help="Pass@")
parser.add_argument("--mutate", type=str, help="Mutate method")
args = parser.parse_args()

varlen = args.varlen
model_name = args.model
temperature = args.temp
passat = args.passat
mutate_method = args.mutate

# 获取当前时间
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
if "#" in model_name:
    simplified_model_name = model_name.split('/')[3].split('#')[0]
else:
    simplified_model_name = model_name.split('/')[-1]

if mutate_method == "VarRand":
    output_file = f"./result/{simplified_model_name}_{mutate_method}_varlen{varlen}_t{temperature}_pass@{passat}_{current_time}.jsonl"
else:
    output_file = f"./result/{simplified_model_name}_{mutate_method}_t{temperature}_pass@{passat}_{current_time}.jsonl"

# 加载数据集
ds = load_dataset("cruxeval-org/cruxeval")

# 初始化计数器
original_count = 0
new_count = 0


try:
    # 打开jsonl文件写入
    with open(output_file, 'w') as file:
        for i in tqdm(range(800)):
    
            # 准备原始代码和修改后的代码
            code = ds['test']['code'][i] + f"\nassert f({ds['test']['input'][i]}) =="
            if mutate_method == "VarRand":
                new_code = mutate.replace_variables_with_random(code, varlen, set(dir(__builtins__)))
            elif mutate_method == "VarNorm":
                new_code = mutate.replace_variables_with_norm(code, set(dir(__builtins__)))

            # 处理 original code 和 new_code，每个生成passat次
            for code_type, test_code in [("original", code), ("modified", new_code)]:
                success_flag = False  # 初始化成功标志
                
                # 重复生成passat次内容
                for _ in range(passat):

                    if "llama" in model_name:
                        for time in range(20):
                            try:
                                client = Fireworks(api_key="fw_3ZVvr8obFydXX2qt15w4rEec")
                                # 请求 LLM 生成内容
                                result = client.chat.completions.create(
                                    messages=[
                                        {
                                            'role': 'user',
                                            'content': prompt + test_code
                                        }
                                    ],
                                    model=model_name,
                                    temperature=temperature
                                )

                                generated_content = result.choices[0].message.content
                                break
                            except:
                                print("===SSL ERROR===")
                                pass
                    
                    else:
                        for time in range(20):
                            try:
                                client = Fireworks(api_key="fw_3ZVvr8obFydXX2qt15w4rEec")
                                result = client.completion.create(
                                    prompt=prompt + test_code,
                                    model=model_name,
                                    temperature=temperature
                                )
                                generated_content = result.choices[0].text
                                break
                            except:
                                print("===SSL ERROR===")
                                pass


                    # 针对gpt-4o-mini的问题，喜欢输出```和python
                    generated_content = generated_content.replace('`', '').replace('python', '')

                    if "code-llama" in model_name or "deepseek" in model_name:
                        generated_content = generated_content.split("\n", 1)[0]
                        test_code_base = test_code
                    else:
                        if "assert" in generated_content:
                            test_code_base = '\n'.join(test_code.strip().splitlines()[:-1]) + '\n'
                        else:
                            test_code_base = test_code
                    exec_code = test_code_base + generated_content

                    try:
                        timeout.exec_with_timeout(exec_code)  # 尝试执行代码
                        success_flag = True  # 执行成功
                    except:
                        # 有几个实在变量名替代有问题，特判了
                        if not success_flag and code_type == "modified" \
                            and i in [67, 182, 189, 304, 472, 516, 667, 670] \
                            and ds['test']['output'][i] in generated_content:
                            success_flag = True
                        pass


                    # 保存每次生成结果到文件
                    json.dump({
                        "code_type": code_type,
                        "code": test_code_base,
                        "generated_content": generated_content,
                        "execution_success": success_flag
                    }, file)
                    file.write('\n')

                    if success_flag == True:
                        break
                
                # 如果在passat次生成中有一次成功，则计数加1
                if success_flag:
                    if code_type == "original":
                        original_count += 1
                    else:
                        new_count += 1

            # 输出成功执行的次数
            file.write("i:" + str(i) + "  ")
            file.write("Original Count:" + str(original_count) + "  ")
            file.write("New Count:" + str(new_count) + "\n")

    print("Original Count:", original_count)  
    print("New Count:", new_count)

    with open(output_file, 'a') as file:
        file.write(f"Original Count: {original_count}\n")
        file.write(f"New Count: {new_count}\n")
        file.write(f"varlen: {varlen}\n")
        file.write(f"model: {simplified_model_name}\n")
        file.write(f"mutate method: {mutate_method}\n")
        file.write(f"temperature: {temperature}\n")
        file.write(f"passat: {passat}\n")

except Exception as e:
    traceback.print_exc()  
    error_message = traceback.format_exc()
    with open(output_file, 'a') as file:
        file.write(error_message)
    error_output_file = "./result/[ERROR]" + output_file.split("/")[2]
    os.rename(output_file, error_output_file)
