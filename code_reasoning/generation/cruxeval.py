import argparse
import json
import os
import sys
import traceback
from tqdm import tqdm

current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)

from util.helper import generate_content, get_output_file_path, \
    load_dataset_with_retry, load_mutate_codes, create_client

def main():
    prompt = """Based on the given Python code, which may contain errors, complete the assert statement with the output when executing the code on the given test case. Do NOT output any extra information, even if the function is incorrect or incomplete. Output "# done" after the assertion.
    """ 

    parser = argparse.ArgumentParser(description="A simple argument parser.")
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--temp", type=float, help="Temperature")
    parser.add_argument("--nsample", type=int, default=10, help="N sample in Pass@k")
    parser.add_argument("--mutate", type=str, help="Mutate method")
    parser.add_argument("--curtime", type=str, help="Current time")
    args = parser.parse_args()

    model_name = args.model
    temperature = args.temp
    nsample = args.nsample
    mutate_method = args.mutate
    current_time = args.curtime

    output_file = get_output_file_path(model_name, mutate_method, temperature, current_time)

    ds = load_dataset_with_retry("cruxeval-org/cruxeval")
    if mutate_method.count('_') < 2:
        mutate_codes = load_mutate_codes(f"code_reasoning/new_data/SingleMutated/{mutate_method}.jsonl")
    else:
        mutate_codes = load_mutate_codes(f"code_reasoning/new_data/MultiMutated/{mutate_method}.jsonl")

    try:
        with open(output_file, 'w') as file:
            for old_id, mutate_code in tqdm(mutate_codes.items()):
                code = ds['test']['code'][old_id] + f"\nassert f({ds['test']['input'][old_id]}) =="
                if "VarNorm" in mutate_method or "VarRand" in mutate_method:
                    new_code = mutate_code
                else:
                    new_code = mutate_code + f"\nassert f({ds['test']['input'][old_id]}) =="

                for code_type, test_code in [("original", code), ("modified", new_code)]:
                    
                    for _ in range(nsample):
                        client = create_client(model_name)
                        generated_content = generate_content(client, model_name, prompt+test_code, temperature)
                        raw_generated_content = generated_content

                        json.dump({
                            "id": old_id,
                            "code_type": code_type,
                            "code": test_code,
                            "generated_content": generated_content,
                            "execution_success": False,
                            "raw_generated_content": raw_generated_content
                        }, file)
                        file.write('\n')

    except Exception as e:
        traceback.print_exc()
        error_message = traceback.format_exc()
        with open(output_file, 'a') as file:
            file.write(error_message)
        error_output_file = "./result/[ERROR]" + output_file.split("/")[2]
        os.rename(output_file, error_output_file)


if __name__ == "__main__":
    main()