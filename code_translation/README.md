# Code Lingua

>https://codetlingua.github.io/leaderboard.html

| Translation    | Dataset                                             | Num  |
| -------------- | --------------------------------------------------- | ---- |
| Python -> C    | CodeNet(200), Avatar(250)                           | 450  |
| Python -> C++  | CodeNet(200), Avatar(250)                           | 450  |
| Python -> Go   | CodeNet(200), Avatar(250)                           | 450  |
| Python -> Java | CodeNet(200), Avatar(250), EvalPlus(164), Click(15) | 629  |

- `code` = `code`
- `id` = `id`



## Humaneval-x

>https://huggingface.co/datasets/THUDM/humaneval-x

- `task_id`: indicates the target language and ID of the problem. Language is one of ["Python", "Java", "JavaScript", "CPP", "Go"].
- `prompt`: the function declaration and docstring, used for code generation.
- `declaration`: only the function declaration, used for code translation.
- `canonical_solution`: human-crafted example solutions.
- `test`: hidden test samples, used for evaluation.
- `example_test`: public test samples (appeared in prompt), used for evaluation.

| Translation   | Dataset            | Num  |
| ------------- | ------------------ | ---- |
| Python -> xxx | HumanEval-x/python | 163  |

Code translation: 

- `code` = `declaration` + `canonical_solution`
- `id` = `task_id`



## TransCoder

>https://huggingface.co/datasets/ziwenyd/transcoder-geeksforgeeks
>
>Cleaned version: https://github.com/yz1019117968/FSE-24-UniTrans/tree/main

| Translation    | Dataset            | Num  |
| -------------- | ------------------ | ---- |
| Python -> Java | Cleaned transcoder | 568  |

- `code` = `python`
- `id` = `id`
