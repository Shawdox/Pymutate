TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
TEMP="0.2"
MODEL="gpt-4o-mini"
DATASET="codenet"
TIMESTAMP=20241223_214227

# /opt/homebrew/bin/python3.11 code_translation/generation/codelingua.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate For2While
# /opt/homebrew/bin/python3.11 code_translation/execution/codelingua.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate For2While
/opt/homebrew/bin/python3.11 code_translation/metrics/evaluation.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate For2While

# /opt/homebrew/bin/python3.11 generation/codelingua.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Assign2Ternary
# /opt/homebrew/bin/python3.11 execution/codelingua.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Assign2Ternary
# /opt/homebrew/bin/python3.11 ../metrics/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1  --mutate IfAddShortCircuiting_For2While_Assign2Ternary

# /opt/homebrew/bin/python3.11 generation/codelingua.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_ConstantUnfoldding
# /opt/homebrew/bin/python3.11 execution/codelingua.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_ConstantUnfoldding
# /opt/homebrew/bin/python3.11 ../metrics/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate IfAddShortCircuiting_For2While_ConstantUnfoldding