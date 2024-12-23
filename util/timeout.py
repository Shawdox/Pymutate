from wrapt_timeout_decorator import *

@timeout(20)
def exec_with_timeout(code):
    exec(code, globals())