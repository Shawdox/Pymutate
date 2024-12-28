TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
TEMP="0.2"
MODEL="deepseek-chat"

# /opt/homebrew/bin/python3.11 code_reasoning/generation/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Add_IndependentVar
# /opt/homebrew/bin/python3.11 code_reasoning/execution/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Add_IndependentVar
# /opt/homebrew/bin/python3.11 code_reasoning/metrics/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate IfAddShortCircuiting_For2While_Add_IndependentVar

# /opt/homebrew/bin/python3.11 code_reasoning/generation/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Assign2Ternary
# /opt/homebrew/bin/python3.11 code_reasoning/execution/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Assign2Ternary
# /opt/homebrew/bin/python3.11 code_reasoning/metrics/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1  --mutate IfAddShortCircuiting_For2While_Assign2Ternary

/opt/homebrew/bin/python3.11 code_reasoning/generation/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate For2While
/opt/homebrew/bin/python3.11 code_reasoning/execution/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate For2While
/opt/homebrew/bin/python3.11 code_reasoning/metrics/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate For2While