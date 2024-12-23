TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
TEMP="0.2"
MODEL="gpt-4o-mini"

/opt/homebrew/bin/python3.11 code_reasoning/generation/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Add_IndependentVar
/opt/homebrew/bin/python3.11 code_reasoning/execution/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Add_IndependentVar
/opt/homebrew/bin/python3.11 evaluation/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate IfAddShortCircuiting_For2While_Add_IndependentVar

/opt/homebrew/bin/python3.11 code_reasoning/generation/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Assign2Ternary
/opt/homebrew/bin/python3.11 code_reasoning/execution/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_Assign2Ternary
/opt/homebrew/bin/python3.11 evaluation/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1  --mutate IfAddShortCircuiting_For2While_Assign2Ternary

/opt/homebrew/bin/python3.11 code_reasoning/generation/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_ConstantUnfoldding
/opt/homebrew/bin/python3.11 code_reasoning/execution/cruxeval.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate IfAddShortCircuiting_For2While_ConstantUnfoldding
/opt/homebrew/bin/python3.11 evaluation/evaluation.py --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate IfAddShortCircuiting_For2While_ConstantUnfoldding