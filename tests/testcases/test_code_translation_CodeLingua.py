import pytest
import sys,os
sys.path.append("../../")
from code_translation_mutate.Mutate import execute_code, evaluate_code, mutate_dataset_once
from util.util import *
from util.mutators import *

class TestAvatar:
    code_list = [
    {
        "code": "n = int(input())\nprint((n * 2 + 1) // 3)\n",
        "test_IO": [
            {
                "input": "6\n",
                "output": "4\n"
            },
            {
                "input": "100000000\n",
                "output": "66666667\n"
            },
            {
                "input": "2\n",
                "output": "1\n"
            }
        ]
    },
    {
        "code": "def sum(k):\n    ret = 0\n    pw = 10\n    len = 1\n    while 1 == 1:\n        cur = min(pw - 1, k)\n        prev = pw // 10\n        ret += (cur - prev + 1) * len\n        if (pw - 1 >= k):\n            break\n        len += 1\n        pw *= 10\n    return ret\n\n\nw, m, k = map(int, input().split())\nlo = 0\nhi = int(1e18)\nwhile hi - lo > 1:\n    md = (lo + hi) // 2\n    c = sum(m + md - 1) - sum(m - 1)\n    if c * k <= w:\n        lo = md\n    else:\n        hi = md\nprint(lo)\n",
        "test_IO": [
            {
                "input": "462 183 8\n",
                "output": "19\n"
            },
            {
                "input": "121212121 3434343434 56\n",
                "output": "216450\n"
            },
            {
                "input": "3 1 4\n",
                "output": "0\n"
            }
        ]
    }]
    
    def test_code_avatar_execute(self):
        for test in self.code_list:
            code = test["code"]
            for testcase in test["test_IO"]:
                input = testcase["input"]
                output = testcase["output"]
                res = execute_code(code, input)
    
    def test_code_avatar_evaluate(self):
        for test in self.code_list:
            code = test["code"]
            for testcase in test["test_IO"]:
                input = testcase["input"]
                output = testcase["output"]
                res = evaluate_code(code, input, output)
                assert res == True
                
            
