import re
import random
import string
import keyword


def replace_variables_with_random(code, varlen, full_builtins, seed):
    random.seed(42+ seed)

    # 匹配变量名的正则表达式，不包括字符串中的内容
    var_pattern = r'\b([a-zA-Z_]\w*)\b'
    
    # 字典来存储变量和新名称的映射
    var_map = {}
    # Python内建函数和方法集合，避免替换它们
    builtins = full_builtins  # 包含所有内建函数
    # 包含常见的内建数据类型方法：字符串、列表、字典等
    object_methods = {
        'str': dir(str),
        'list': dir(list),
        'dict': dir(dict),
        'tuple': dir(tuple),
        'set': dir(set),
        'int': dir(int),
        'float': dir(float),
        'bool': dir(bool)
    }
    
    # 汇总所有不应该替换的内建方法
    excluded_methods = builtins.copy()  # 包含所有内建函数
    for methods in object_methods.values():
        excluded_methods.update(methods)  # 加入所有内建类型的方法

    # 集合来存储已使用的变量名，避免重复
    used_names = set()

    # 生成唯一的随机字符串
    def generate_unique_random_string(length):
        while True:
            random_name = ''.join(random.choices(string.ascii_letters, k=length))
            # 确保生成的名字唯一且不在排除列表中
            if random_name not in used_names and random_name not in excluded_methods:
                used_names.add(random_name)
                return random_name

    # 函数：替换变量名
    def repl(match):
        var_name = match.group(1)
        
        # 检查是否已经替换过该变量名
        if var_name not in var_map:
            # 跳过关键字、内建函数和方法
            if not keyword.iskeyword(var_name) and var_name not in excluded_methods:
                # 如果变量名是 `key` 且后面紧接着 `=`（没有空格），则不替换
                start_pos = match.end()  # 变量名结束位置
                if var_name == 'key' and start_pos < len(code) and \
                    code[start_pos] == '=' and (start_pos + 1 >= len(code) or code[start_pos + 1] != ' '):
                    # 如果是 `key` 且紧接着 `=`（没有空格），则不替换
                    return var_name
                # 否则，替换变量名
                var_map[var_name] = generate_unique_random_string(varlen)
        return var_map.get(var_name, var_name)
    
    # 通过正则表达式，避免替换字符串中的内容
    # 匹配所有的字符串内容
    strings_pattern = r'(\".*?\"|\'.*?\')'
    
    # 分离字符串和代码
    segments = re.split(strings_pattern, code)
    
    # 替换代码片段中的变量
    for i in range(len(segments)):
        if not (segments[i].startswith('"') or segments[i].startswith("'")):
            segments[i] = re.sub(var_pattern, repl, segments[i])
    
    # 重新组合代码
    replaced_code = ''.join(segments)
    return replaced_code





def replace_variables_with_norm(code, full_builtins):
    # 匹配变量名的正则表达式，不包括字符串中的内容
    var_pattern = r'\b([a-zA-Z_]\w*)\b'
    
    # 字典来存储变量和新名称的映射
    var_map = {}
    var_counter = 1  # 起始编号

    # Python内建函数和方法集合，避免替换它们
    builtins = full_builtins  # 包含所有内建函数
    # 包含常见的内建数据类型方法：字符串、列表、字典等
    object_methods = {
        'str': dir(str),
        'list': dir(list),
        'dict': dir(dict),
        'tuple': dir(tuple),
        'set': dir(set),
        'int': dir(int),
        'float': dir(float),
        'bool': dir(bool)
    }
    
    # 汇总所有不应该替换的内建方法
    excluded_methods = builtins.copy()  # 包含所有内建函数
    for methods in object_methods.values():
        excluded_methods.update(methods)  # 加入所有内建类型的方法

    # 函数：替换变量名
    def repl(match):
        nonlocal var_counter
        var_name = match.group(1)

        # 检查是否已经替换过该变量名
        if var_name not in var_map:
            # 不修改函数名
            if var_name == 'f':
                return var_name
            # 跳过关键字、内建函数和方法
            if not keyword.iskeyword(var_name) and var_name not in excluded_methods:
                # 如果变量名是 `key` 且后面紧接着 `=`（没有空格），则不替换
                start_pos = match.end()  # 变量名结束位置
                if var_name == 'key' and start_pos < len(code) and \
                    code[start_pos] == '=' and (start_pos + 1 >= len(code) or code[start_pos + 1] != ' '):
                    # 如果是 `key` 且紧接着 `=`（没有空格），则不替换
                    return var_name
                # 否则，使用 var1, var2, var3... 来替换变量名
                var_map[var_name] = f"var{var_counter}"
                var_counter += 1
        return var_map.get(var_name, var_name)
    
    # 通过正则表达式，避免替换字符串中的内容
    # 匹配所有的字符串内容
    strings_pattern = r'(\".*?\"|\'.*?\')'
    
    # 分离字符串和代码
    segments = re.split(strings_pattern, code)

    
    # 替换代码片段中的变量
    for i in range(len(segments)):
        if not (segments[i].startswith('"') or segments[i].startswith("'")):
            segments[i] = re.sub(var_pattern, repl, segments[i])
    
    # 重新组合代码
    replaced_code = ''.join(segments)
    return replaced_code
