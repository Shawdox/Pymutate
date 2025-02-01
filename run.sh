#!/bin/bash

# 定义不同的 mutate 参数
# mutates=("VarNorm" "VarRand3" "ConstantUnfoldding" "For2While" "IfAddShortCircuiting")
mutates=( "FCVR3" "ICVN" "IFC" )

# 遍历每个 mutate 参数
for mutate in "${mutates[@]}"; do
    echo "Running scripts with mutate: $mutate"
    
    # 运行第一个脚本
    /opt/homebrew/bin/python3.11 code_translation/execution/transcoder.py --model Qwen/Qwen2.5-Coder-7B-Instruct --temp 0.2 --curtime 20250131_122458 --mutate "$mutate" 
    
    # 运行第二个脚本
    /opt/homebrew/bin/python3.11 code_translation/metrics/evaluation.py --passatk 1 --model Qwen/Qwen2.5-Coder-7B-Instruct --temp 0.2 --curtime 20250131_122458 --dataset transcoder --mutate "$mutate"
    
    echo "Finished running scripts with mutate: $mutate"
    echo "---------------------------------------------"
done

echo "All scripts executed with all mutate parameters."