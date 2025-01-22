# import json
# from tqdm import tqdm
# from datasets import load_dataset
# import os
# import sys
# from io import StringIO
# import contextlib
# from wrapt_timeout_decorator import *

# @timeout(20)
# def exec_with_timeout(code, a):
#     exec(code, a)

# current_working_directory = os.getcwd()
# if current_working_directory not in sys.path:
#     sys.path.insert(0, current_working_directory)
    
# from util import mutate, timeout

# # Predefined set of reserved keywords and names
# reserved_keywords = {
#     'Ellipsis', 'FloatingPointError', '__doc__', 'type', 'int', '__spec__', 'super', 'PendingDeprecationWarning',
#     'RuntimeWarning', 'FutureWarning', 'bool', '__name__', 'aiter', 'BaseExceptionGroup', 'UserWarning',
#     'print', 'str', 'FileExistsError', 'ZeroDivisionError', 'OverflowError', 'classmethod', '__package__',
#     'issubclass', 'slice', 'hasattr', 'property', 'ascii', 'copyright', 'next', 'bin', 'KeyError',
#     'ImportWarning', 'list', 'open', 'oct', 'bytes', '__loader__', 'BlockingIOError', 'ValueError',
#     '__build_class__', 'dict', 'RecursionError', 'eval', 'exit', 'NotImplementedError', 'set',
#     'getattr', 'zip', 'credits', 'staticmethod', 'ExceptionGroup', 'BytesWarning', 'ConnectionError',
#     'anext', 'SystemExit', 'ReferenceError', 'NotImplemented', 'filter', 'StopAsyncIteration',
#     'reversed', 'Exception', 'LookupError', 'ord', 'True', 'delattr', 'MemoryError', 'IsADirectoryError',
#     'EncodingWarning', 'compile', 'ArithmeticError', 'TabError', 'SyntaxWarning', 'frozenset', 'globals',
#     'PermissionError', 'FileNotFoundError', 'None', 'exec', 'SyntaxError', 'callable', 'BufferError',
#     '__debug__', 'pow', 'sum', 'BaseException', 'license', 'help', 'range', 'min', 'sorted',
#     'UnicodeDecodeError', 'chr', 'SystemError', 'complex', 'ConnectionAbortedError', 'hash',
#     'repr', 'NameError', 'map', 'vars', 'RuntimeError', 'KeyboardInterrupt', 'AssertionError',
#     'float', 'memoryview', 'round', 'id', 'ProcessLookupError', 'ChildProcessError', 'NotADirectoryError',
#     'ConnectionRefusedError', 'IOError', 'dir', 'object', 'False', 'locals', 'quit', 'StopIteration',
#     'any', 'InterruptedError', 'IndentationError', 'UnicodeWarning', 'TypeError', 'format', 'OSError',
#     'iter', 'BrokenPipeError', 'AttributeError', 'UnicodeEncodeError', 'abs', '__import__', 'all',
#     'EnvironmentError', 'ModuleNotFoundError', 'Warning', 'GeneratorExit', 'TimeoutError', 'isinstance',
#     'UnicodeTranslateError', 'setattr', 'tuple', 'bytearray', 'divmod', 'UnicodeError',
#     'ConnectionResetError', 'max', 'DeprecationWarning', 'ResourceWarning', 'ImportError',
#     'UnboundLocalError', 'breakpoint', 'IndexError', 'EOFError', 'len', 'hex', 'input', 'enumerate', 'extend', 
#     'math', 'operator', 'copy', 'heapq', 'os', 'numpy', 'string', 'random', 'time', 'networkx', 'functools', 
#     'bisect', 'queue', 'sys', 'scipy.misc', 'datetime', 'collections', 're', 'itertools'
# }

# # Load dataset
# ds = {}

# # 从jsonl中读取源程序
# with open('code_translation/mutated_datasets/MultiMutated/CodeLingua/two/codenet_IfAddShortCircuiting_ConstantUnfoldding_134.jsonl', 'r', encoding='utf-8') as file:
#     for line in file:
#         json_object = json.loads(line)
#         id_value = json_object['old_id']
#         python_code = json_object['code']    
#         ds[id_value] = python_code


# # List to store processed data
# processed_entries = []

# # Define output filename prefix
# output_prefix = "VarNorm"

# # Process test set
# for id in tqdm(ds, desc="Processing test set"):
#     original_code = ds[id]
#     # modified_code = mutate.replace_variables_with_random(original_code, 3, reserved_keywords, hash(id))
#     modified_code = mutate.replace_variables_with_norm(original_code, reserved_keywords)

#     processed_entry = {
#         "old_id": id,
#         "code": modified_code,
#     }
#     processed_entries.append(processed_entry)

# # Save processed data to a JSONL file
# output_file = f"{output_prefix}.jsonl"
# with open(output_file, "w", encoding="utf-8") as file:
#     for entry in processed_entries:
#         json.dump(entry, file, ensure_ascii=False)
#         file.write("\n")

# print(f"Processed data saved to {output_file}")

# # Input and output paths for cleaned data
# input_file_path = output_file
# cleaned_file_path = f"{output_prefix}_cleaned.jsonl"

# # Initialize counters and error tracking
# error_count = 0
# failed_ids = set()



# # Validate code entries
# def validate_code():
#     ds = load_dataset("iidai/codenet")['train'].filter(lambda x: x['language'] == 'Python')


#     global error_count
#     with open(input_file_path, "r", encoding="utf-8") as file:
#         for line_number, line in enumerate(file, start=1):
#             try:
#                 # Parse JSON entry
#                 entry = json.loads(line.strip())
#                 code = entry.get("code", "")
#                 old_id = entry.get("old_id", f"unknown_id_{line_number}")
#                 # exec(code)
#                 test_io = ds.filter(lambda x: x['id'] == old_id)[0]['test_IO'] 
#                 input_value = test_io[0]['input']
#                 output_value = test_io[0]['output']

#                 # Execute the code to validate
#                 input_stream = StringIO(input_value)
#                 original_stdin = sys.stdin
#                 sys.stdin = input_stream
#                 output_stream = StringIO()

#                 # print(old_id)
#                 # print(code)
#                 # 自定义全局命名空间
#                 custom_globals = {
#                     '__builtins__': __builtins__,
#                     'sys': sys
#                 }

#                 # 重定义 sys.exit 和 exit
#                 custom_globals['sys'].exit = lambda *args: None
#                 custom_globals['exit'] = lambda *args: None

#                 with contextlib.redirect_stdout(output_stream):
#                     exec_with_timeout(code, custom_globals)

#                 # Retrieve the captured output
#                 sys.stdin = original_stdin
#                 captured_output = output_stream.getvalue()
#                 assert captured_output.strip() == output_value.strip()
    
#             except Exception as error:
#                 # Log failure
#                 error_count += 1
#                 failed_ids.add(old_id)
#                 print(f"Error in code execution for ID {old_id}: {error}")

# # Run validation
# validate_code()

# # Log results
# print("Execution failed for the following IDs:")
# for failed_id in failed_ids:
#     print(failed_id)
# print(f"Total failed executions: {error_count}")

# # Write cleaned data, excluding failed entries
# with open(input_file_path, "r", encoding="utf-8") as infile, open(cleaned_file_path, "w", encoding="utf-8") as outfile:
#     for line in infile:
#         entry = json.loads(line.strip())
#         if entry.get("old_id") not in failed_ids:
#             json.dump(entry, outfile, ensure_ascii=False)
#             outfile.write("\n")

# print(f"Cleaned data saved to {cleaned_file_path}")


# # import json
# # import ast

# # def extract_imports(code_str):
# #     imports = []
# #     try:
# #         tree = ast.parse(code_str)
# #     except SyntaxError:
# #         return imports
# #     for node in ast.walk(tree):
# #         if isinstance(node, ast.Import):
# #             for alias in node.names:
# #                 imports.append(alias.name)
# #         elif isinstance(node, ast.ImportFrom):
# #             if node.module:
# #                 imports.append(node.module)
# #     return imports

# # all_imports = []

# # with open('code_translation/Datasets/CodeLingua/codenet/codenet_python.jsonl', 'r') as f:
# #     for line in f:
# #         try:
# #             data = json.loads(line)
# #             code = data.get('code', '')
# #             imports = extract_imports(code)
# #             all_imports.extend(imports)
# #         except json.JSONDecodeError:
# #             # 忽略无法解析的JSON行
# #             pass

# # print(set(all_imports))

# # all_functions = []

# # for lib in all_imports:
# #     functions = [func for func in dir(lib) if not func.startswith('_')]
# #     all_functions.extend(functions)

# # print(all_functions)

import json
from tqdm import tqdm
from datasets import load_dataset
import os
import sys
from io import StringIO
import contextlib



current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)
    
from util import mutate, timeout

# Predefined set of reserved keywords and names
reserved_keywords = {
    'Ellipsis', 'FloatingPointError', '__doc__', 'type', 'int', '__spec__', 'super', 'PendingDeprecationWarning',
    'RuntimeWarning', 'FutureWarning', 'bool', '__name__', 'aiter', 'BaseExceptionGroup', 'UserWarning',
    'print', 'str', 'FileExistsError', 'ZeroDivisionError', 'OverflowError', 'classmethod', '__package__',
    'issubclass', 'slice', 'hasattr', 'property', 'ascii', 'copyright', 'next', 'bin', 'KeyError',
    'ImportWarning', 'list', 'open', 'oct', 'bytes', '__loader__', 'BlockingIOError', 'ValueError',
    '__build_class__', 'dict', 'RecursionError', 'eval', 'exit', 'NotImplementedError', 'set',
    'getattr', 'zip', 'credits', 'staticmethod', 'ExceptionGroup', 'BytesWarning', 'ConnectionError',
    'anext', 'SystemExit', 'ReferenceError', 'NotImplemented', 'filter', 'StopAsyncIteration',
    'reversed', 'Exception', 'LookupError', 'ord', 'True', 'delattr', 'MemoryError', 'IsADirectoryError',
    'EncodingWarning', 'compile', 'ArithmeticError', 'TabError', 'SyntaxWarning', 'frozenset', 'globals',
    'PermissionError', 'FileNotFoundError', 'None', 'exec', 'SyntaxError', 'callable', 'BufferError',
    '__debug__', 'pow', 'sum', 'BaseException', 'license', 'help', 'range', 'min', 'sorted',
    'UnicodeDecodeError', 'chr', 'SystemError', 'complex', 'ConnectionAbortedError', 'hash',
    'repr', 'NameError', 'map', 'vars', 'RuntimeError', 'KeyboardInterrupt', 'AssertionError',
    'float', 'memoryview', 'round', 'id', 'ProcessLookupError', 'ChildProcessError', 'NotADirectoryError',
    'ConnectionRefusedError', 'IOError', 'dir', 'object', 'False', 'locals', 'quit', 'StopIteration',
    'any', 'InterruptedError', 'IndentationError', 'UnicodeWarning', 'TypeError', 'format', 'OSError',
    'iter', 'BrokenPipeError', 'AttributeError', 'UnicodeEncodeError', 'abs', '__import__', 'all',
    'EnvironmentError', 'ModuleNotFoundError', 'Warning', 'GeneratorExit', 'TimeoutError', 'isinstance',
    'UnicodeTranslateError', 'setattr', 'tuple', 'bytearray', 'divmod', 'UnicodeError',
    'ConnectionResetError', 'max', 'DeprecationWarning', 'ResourceWarning', 'ImportError',
    'UnboundLocalError', 'breakpoint', 'IndexError', 'EOFError', 'len', 'hex', 'input', 'enumerate', 'extend', 
    'math', 'operator', 'copy', 'heapq', 'os', 'numpy', 'string', 'random', 'time', 'networkx', 'functools', 
    'bisect', 'queue', 'sys', 'scipy.misc', 'datetime', 'collections', 're', 'itertools'
}

# Load dataset
ds = {}

# 从jsonl中读取源程序
with open('code_translation/mutated_datasets/MultiMutated/TransCoder/two/IfAddShortCircuiting_ConstantUnfoldding_396.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        json_object = json.loads(line)
        id_value = json_object['old_id']
        python_code = json_object['code']    
        ds[id_value] = python_code


# List to store processed data
processed_entries = []

# Define output filename prefix
output_prefix = "VarNorm"

# Process test set
for id in tqdm(ds, desc="Processing test set"):
    original_code = ds[id]
    modified_code = mutate.replace_variables_with_random(original_code, 3, reserved_keywords, hash(id))
    # modified_code = mutate.replace_variables_with_norm(original_code, reserved_keywords)

    processed_entry = {
        "old_id": id,
        "code": modified_code,
    }
    processed_entries.append(processed_entry)

# Save processed data to a JSONL file
output_file = f"{output_prefix}.jsonl"
with open(output_file, "w", encoding="utf-8") as file:
    for entry in processed_entries:
        json.dump(entry, file, ensure_ascii=False)
        file.write("\n")

print(f"Processed data saved to {output_file}")

# Input and output paths for cleaned data
input_file_path = output_file
cleaned_file_path = f"{output_prefix}_cleaned.jsonl"

# Initialize counters and error tracking
error_count = 0
failed_ids = set()

# Validate code entries
def validate_code():
    global error_count
    with open(input_file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Parse JSON entry
                entry = json.loads(line.strip())
                code = entry.get("code", "")
                old_id = entry.get("old_id", f"unknown_id_{line_number}")
                exec(code)
                # input_value = entry.get("input", "")
                # output_value = entry.get("output", "")

                # # Execute the code to validate
                # input_stream = StringIO(input_value)
                # original_stdin = sys.stdin
                # sys.stdin = input_stream
                # output_stream = StringIO()

                # print(old_id)
                # print(code)
                # # 自定义全局命名空间
                # custom_globals = {
                #     '__builtins__': __builtins__,
                #     'sys': sys
                # }

                # # 重定义 sys.exit 和 exit
                # custom_globals['sys'].exit = lambda *args: None
                # custom_globals['exit'] = lambda *args: None

                # with contextlib.redirect_stdout(output_stream):
                #     exec(code, custom_globals)

                # Retrieve the captured output
                # sys.stdin = original_stdin
                # captured_output = output_stream.getvalue()
                # assert captured_output.strip() == output_value.strip()
    
            except Exception as error:
                # Log failure
                error_count += 1
                failed_ids.add(old_id)
                print(f"Error in code execution for ID {old_id}: {error}")

# Run validation
validate_code()

# Log results
print("Execution failed for the following IDs:")
for failed_id in failed_ids:
    print(failed_id)
print(f"Total failed executions: {error_count}")

# Write cleaned data, excluding failed entries
with open(input_file_path, "r", encoding="utf-8") as infile, open(cleaned_file_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        entry = json.loads(line.strip())
        if entry.get("old_id") not in failed_ids:
            json.dump(entry, outfile, ensure_ascii=False)
            outfile.write("\n")

print(f"Cleaned data saved to {cleaned_file_path}")


# import json
# import ast

# def extract_imports(code_str):
#     imports = []
#     try:
#         tree = ast.parse(code_str)
#     except SyntaxError:
#         return imports
#     for node in ast.walk(tree):
#         if isinstance(node, ast.Import):
#             for alias in node.names:
#                 imports.append(alias.name)
#         elif isinstance(node, ast.ImportFrom):
#             if node.module:
#                 imports.append(node.module)
#     return imports

# all_imports = []

# with open('code_translation/Datasets/CodeLingua/codenet/codenet_python.jsonl', 'r') as f:
#     for line in f:
#         try:
#             data = json.loads(line)
#             code = data.get('code', '')
#             imports = extract_imports(code)
#             all_imports.extend(imports)
#         except json.JSONDecodeError:
#             # 忽略无法解析的JSON行
#             pass

# print(set(all_imports))

# all_functions = []

# for lib in all_imports:
#     functions = [func for func in dir(lib) if not func.startswith('_')]
#     all_functions.extend(functions)

# print(all_functions)