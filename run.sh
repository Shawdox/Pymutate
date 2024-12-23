TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
TEMP="0.2"
MODEL="gpt-4o-mini"
MUTATE="IASC_F2W_AU"
/opt/homebrew/bin/python3.11 generation/cruxeval.py --model ${MODEL} --temp ${TEMP} --mutate ${MUTATE} --curtime $TIMESTAMP
/opt/homebrew/bin/python3.11 execution/cruxeval.py --model ${MODEL} --temp ${TEMP} --mutate ${MUTATE} --curtime $TIMESTAMP
/opt/homebrew/bin/python3.11 evaluation/evaluation.py --model ${MODEL} --temp ${TEMP} --mutate ${MUTATE} --curtime $TIMESTAMP