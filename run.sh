#!/bin/bash

# 定义不同的 mutate 参数
# mutates=("VarNorm" "VarRand3" "ConstantUnfoldding" "For2While" "IfAddShortCircuiting")
mutates=( "For2While" "IfAddShortCircuiting")

# 遍历每个 mutate 参数
for mutate in "${mutates[@]}"; do
    echo "Running scripts with mutate: $mutate"
    
    # 运行第一个脚本
    /opt/homebrew/bin/python3.11 code_translation/execution/transcoder.py --model starcoder2-3b --temp 0.2 --curtime 20250122_112012 --mutate "$mutate"
    
    # 运行第二个脚本
    /opt/homebrew/bin/python3.11 code_translation/metrics/evaluation.py --passatk 1 --model starcoder2-3b --temp 0.2 --curtime 20250122_112012 --dataset transcoder --mutate "$mutate"
    
    echo "Finished running scripts with mutate: $mutate"
    echo "---------------------------------------------"
done

echo "All scripts executed with all mutate parameters."