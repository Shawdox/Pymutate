### Code Reasoning

Mutate python code on CRUXEval.

- `Mutate.py`: Mutate the python samples in CRUXEval.



### Code Translation

Targeting at 3 datasets: `Code Lingua`, `HumanEval X` and `TransCoder`.

https://codetlingua.github.io/leaderboard.html

https://huggingface.co/datasets/THUDM/humaneval-x

https://huggingface.co/datasets/ziwenyd/transcoder-geeksforgeeks 



### Scripts

- `colored_table.py`: Script for coloring the table for further anlysis.



### Util

- `helper.py`: Auxiliary functions for generation and execution.
- `mutate.py`: Auxiliary functions for variable mutation.
- `mutators.py`: Mutators for modifying the Python code.
- `timeout.py`: Functions for timeout control.
- `util.py`: Generic functions.


### How to Run
```
pip install vllm
vllm serve <model_name> --dtype auto --api-key token-abc123 --gpu-memory-utilization 0.9 --max-model-len 4096
python code_reasoning/reasoning.py --model <model_name>
python code_translation/codelingua.py --model <model_name> --dataset [avatar|codenet]
python code_translation/transcoder.py --model <model_name>
```
