import time
import sys
import json
import re
import javalang
import traceback

from datasets import load_dataset
from openai import OpenAI
from fireworks.client import Fireworks


def load_dataset_with_retry(dataset_name, max_attempts=20, delay=1):
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt}: Trying to load the dataset...")
            ds = load_dataset(dataset_name)
            print("Dataset loaded successfully!")
            return ds
        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt < max_attempts - 1:
                print("Retrying...")
                time.sleep(delay)
            else:
                print("Max retries reached. Exiting the program.")
                sys.exit(1)


def load_mutate_codes(mutation_filename):
    mutate_codes = {}
    with open(mutation_filename, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            if 'code' in data and 'old_id' in data:
                old_id = int(str(data['old_id']).split("_")[-1])
                mutate_codes[old_id] = data['code']
    return mutate_codes

def load_mutate_codes_for_translation(mutation_filename):
    mutate_codes = {}
    with open(mutation_filename, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            if 'code' in data and 'old_id' in data:
                old_id = data['old_id']
                mutate_codes[old_id] = data['code']
    return mutate_codes


def get_output_file_path(model_name, mutate_method, temperature, current_time):
    if "#" in model_name:
        simplified_model_name = model_name.split('/')[3].split('#')[0]
    else:
        simplified_model_name = model_name.split('/')[-1]

    return f"code_reasoning/result/{simplified_model_name}_{mutate_method}_t{temperature}_{current_time}.jsonl"

def get_output_file_path_for_translation(dataset_name, model_name, mutate_method, temperature, current_time):
    if "#" in model_name:
        simplified_model_name = model_name.split('/')[3].split('#')[0]
    else:
        simplified_model_name = model_name.split('/')[-1]

    return f"code_translation/result/{dataset_name}_{simplified_model_name}_{mutate_method}_t{temperature}_{current_time}.jsonl"
    


def create_client(model_name):
    if "gpt" in model_name:
        return OpenAI(
            base_url="https://api.openai.com/v1",
            api_key="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"
        )
    elif model_name == "deepseek-chat":
        return OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key="sk-6cb72a4ef04a4b149fc3e2189b8c3ca4",
        )
    else:
        return Fireworks(api_key="fw_3ZfzgdBmufwmNxAGZyye6E8B")


def generate_content(client, model_name, prompt, temperature, max_attempts=20):
    for _ in range(max_attempts):
        try:
            if "gpt" in model_name \
                or "llama-v3" in model_name \
                or model_name == "deepseek-chat":
                result = client.chat.completions.create(
                    messages=[{'role': 'user', 'content': prompt}],
                    model=model_name,
                    temperature=temperature,
                    max_tokens=750
                )
                return result.choices[0].message.content
            else:
                result = client.completion.create(
                    prompt=prompt,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=750
                )
                return result.choices[0].text
        except Exception as e:
            print(e)
            time.sleep(1)
    return None

# def extract_method_name_java(code):
#     # 匹配方法定义的正则表达式
#     pattern = re.compile(r"(public|private|protected)?\s?(static)?\s?(\w+|\w+\[\])\s(\w+)\s?\(\s?([\w\s,]*?)\s?\)")
    
#     # 查找匹配项
#     method_info = pattern.findall(code)
#     return method_info[0][3]

# import re

# def extract_first_java_method(code):
#     lines = code.splitlines()
#     in_class = False
#     class_brace_count = 0
#     method_started = False
#     method_lines = []
#     in_method_def = False
    
#     method_pattern_start = re.compile(r'^\s*((public|private|protected|static|abstract|final|synchronized|transient|volatile|native|strictfp)\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
#     method_pattern_full = re.compile(r'^\s*((public|private|protected|static|abstract|final|synchronized|transient|volatile|native|strictfp)\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^\)]*\)\s*\{?')
#     class_pattern = re.compile(r'^\s*((public|private|protected|static|abstract|final|)\s+)*(class|interface)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{?')
    
#     for line in lines:
#         line = line.rstrip('\n')
        
#         if line.startswith('@'):
#             continue  # Skip annotation lines
        
#         if not in_class:
#             if class_pattern.match(line):
#                 in_class = True
#                 class_brace_count += line.count('{') - line.count('}')
#                 if class_brace_count == 0:
#                     in_class = False
#                 continue
#             if method_pattern_full.match(line):
#                 method_started = True
#                 method_lines.append(line)
#                 brace_count = line.count('{') - line.count('}')
#                 if brace_count == 0:
#                     method_started = False
#                     method_lines = []
#                 continue
#             if method_pattern_start.match(line):
#                 in_method_def = True
#                 method_lines.append(line)
#                 continue
#         if in_class:
#             if not method_started and not in_method_def:
#                 if method_pattern_full.match(line):
#                     method_started = True
#                     method_lines.append(line)
#                     brace_count = line.count('{') - line.count('}')
#                     if brace_count == 0:
#                         method_started = False
#                         method_lines = []
#                     continue
#                 if method_pattern_start.match(line):
#                     in_method_def = True
#                     method_lines.append(line)
#                     continue
#             if in_method_def:
#                 method_lines.append(line)
#                 if line.count(')') >= line.count('('):
#                     method_started = True
#                     brace_count = line.count('{') - line.count('}')
#                     if brace_count == 0:
#                         method_started = False
#                         method_lines = []
#                     in_method_def = False
#                     continue
#             if method_started:
#                 method_lines.append(line)
#                 brace_count += line.count('{') - line.count('}')
#                 if brace_count == 0:
#                     break
#         else:
#             if in_method_def:
#                 method_lines.append(line)
#                 if line.count(')') >= line.count('('):
#                     method_started = True
#                     brace_count = line.count('{') - line.count('}')
#                     if brace_count == 0:
#                         method_started = False
#                         method_lines = []
#                     in_method_def = False
#                     continue
#             if method_started:
#                 method_lines.append(line)
#                 brace_count += line.count('{') - line.count('}')
#                 if brace_count == 0:
#                     break
    
#     # 提取方法头和方法体
#     method_header_lines = []
#     method_body_lines = []
#     brace_count = 0
#     in_header = True
#     for line in method_lines:
#         if in_header:
#             method_header_lines.append(line)
#             brace_count += line.count('{') - line.count('}')
#             if brace_count > 0:
#                 in_header = False
#         else:
#             method_body_lines.append(line)
    
#     # 合并方法头成一个字符串
#     method_header = ''.join(method_header_lines)
    
#     # 提取函数名
#     func_name_match = re.search(r'(\w+)\s*\(', method_header)
    
#     # 组合新的方法代码块
#     new_method_code = method_header + '\n' + '\n'.join(method_body_lines)
#     if func_name_match:
#         func_name = func_name_match.group(1)
#         # 替换函数名
#         new_method_code = new_method_code.replace(func_name, 'f_filled')

#     return new_method_code


def extract_first_java_method(code):
    lines = code.splitlines()
    method_lines = []
    brace_count = 0
    in_method = False

    method_pattern = re.compile(
        r'^\s*((public|private|protected|static|abstract|final|synchronized|transient|volatile|native|strictfp)\s+)*'
        r'[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\('
    )

    for line in lines:
        stripped_line = line.strip()

        if not in_method:
            if method_pattern.match(stripped_line):
                in_method = True  # Start of a method
                method_lines.append(line)
                brace_count += line.count('{') - line.count('}')
        else:
            method_lines.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:  # End of the method
                break

    if not method_lines:
        return "No method found"

    # Combine the extracted method lines
    method_code = '\n'.join(method_lines)

    # Extract the method name and replace it with "f_filled"
    func_name_match = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', method_code)
    if func_name_match:
        func_name = func_name_match.group(1)
        method_code = method_code.replace(func_name, 'f_filled', 1)

    return method_code


def modify_generated_content(code):
    try:
        code = code.replace('`', '').replace('java\n', '').strip()
        code = extract_first_java_method(code)
    except Exception as e:
        traceback.print_exc()
        print(code)
    return code
   



def extract_import_and_class(code):
    # 初始化一个空字符串用于存储结果
    result = ""
    # 将输入字符串按行分割
    lines = code.splitlines()
    
    # 遍历每一行
    for line in lines:
        # 检查行是否以 '}' 开头，不忽略前导空白
        if line.startswith('}'):
            # 如果是，则将这一行添加到结果中并停止循环
            result += line + '\n'
            break
        # 否则，将当前行添加到结果中，并加上换行符
        result += line + '\n'
    
    # 使用正则表达式来匹配 'class' 后面的类名（包括可能的前导和尾随空白）
    class_pattern = re.compile(r'(class\s+)(\w+)')
    
    # 替换所有匹配到的类名为 'Main'
    modified_string, num_subs = class_pattern.subn(r'\1Main', result.rstrip('\n'))
    # 返回结果时去掉最后多余的换行符
    return modified_string
