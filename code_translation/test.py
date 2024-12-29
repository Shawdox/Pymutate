import re

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


code = "public static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x = x ^ m;\n    return x;\n}\n\nPython\ndef addOne ( x ) :\n    m = 1\n    while ( x & m ) :\n        x = x ^ m\n        m <<= 1\n    x = x ^ m\n    return x\n\nJava\npublic static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x = x ^ m;\n    return x;\n}\n\nPython\ndef addOne ( x ) :\n    m = 1\n    while ( x & m ) :\n        x = x ^ m\n        m <<= 1\n    x = x ^ m\n    return x\n\nJava\npublic static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x = x ^ m;\n    return x;\n}\n\nPython\ndef addOne ( x ) :\n    m = 1\n    while ( x & m ) :\n        x = x ^ m\n        m <<= 1\n    x = x ^ m\n    return x\n\nJava\npublic static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x = x ^ m;\n    return x;\n}\n\nPython\ndef addOne ( x ) :\n    m = 1\n    while ( x & m ) :\n        x = x ^ m\n        m <<= 1\n    x = x ^ m\n    return x\n\nJava\npublic static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x = x ^ m;\n    return x;\n}\n\nPython\ndef addOne ( x ) :\n    m = 1\n    while ( x & m ) :\n        x = x ^ m\n        m <<= 1\n    x = x ^ m\n    return x\n\nJava\npublic static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x = x ^ m;\n    return x;\n}\n\nPython\ndef addOne ( x ) :\n    m = 1\n    while ( x & m ) :\n        x = x ^ m\n        m <<= 1\n    x = x ^ m\n    return x\n\nJava\npublic static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x = x ^ m;\n    return x;\n}\n\nPython\ndef addOne ( x ) :\n    m = 1\n    while ( x & m ) :\n        x = x ^ m\n        m <<= 1\n    x = x ^ m\n    return x\n\nJava\npublic static int addOne(int x) {\n    int m = 1;\n    while (x & m) {\n        x = x ^ m;\n        m <<= 1;\n    }\n    x ="

first_method = extract_first_java_method(code)
print(first_method)
