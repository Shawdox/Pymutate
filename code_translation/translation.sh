TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
TEMP="0.2"
MODEL="gpt-4o"
DATASET="codenet"


MUTATE="ConstantUnfoldding"
/opt/homebrew/bin/python3.11 code_translation/generation/codelingua.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate ${MUTATE}
/opt/homebrew/bin/python3.11 code_translation/execution/codelingua.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate ${MUTATE}
/opt/homebrew/bin/python3.11 code_translation/metrics/evaluation.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate ${MUTATE}

MUTATE="StringUnfoldding"
/opt/homebrew/bin/python3.11 code_translation/generation/codelingua.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate ${MUTATE}
/opt/homebrew/bin/python3.11 code_translation/execution/codelingua.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --mutate ${MUTATE}
/opt/homebrew/bin/python3.11 code_translation/metrics/evaluation.py --dataset ${DATASET} --model ${MODEL} --temp ${TEMP}  --curtime $TIMESTAMP --passatk 1 --mutate ${MUTATE}
