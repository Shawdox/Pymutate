import argparse
import json
import os
import sys
import traceback
import re
from tqdm import tqdm

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from util.helper import get_output_file_path, create_client, generate_content,\
                        load_mutate_codes

def main():
    parser = argparse.ArgumentParser(description="A simple argument parser.")
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--temp", type=float, help="Temperature")
    parser.add_argument("--nsample", type=int, default=10, help="N sample in Pass@k")
    parser.add_argument("--mutate", type=str, help="Mutate method")
    parser.add_argument("--curtime", type=str, help="Current time")
    parser.add_argument("--sourlang", type=str, default="Python", help="Source language")
    parser.add_argument("--tarlang", type=str, default="Java", help="Target language")

    args = parser.parse_args()

    model_name = args.model
    temperature = args.temp
    nsample = args.nsample
    mutate_method = args.mutate
    current_time = args.curtime
    source_lang = args.sourlang
    target_lang = args.tarlang
    prompt = "You are a code translation expert. Translate the {0} code below to {2}\n\n{0}\n{1}\n\n{2}\n"

    output_file = get_output_file_path(model_name, mutate_method, temperature, current_time)

    ds = {}

    # 从jsonl中读取源程序
    with open('TransCoder/testable_samples.jsonl', 'r', encoding='utf-8') as file:
        for line in file:
            json_object = json.loads(line)
            id_value = json_object['id']
            python_code = json_object['python']    
            ds[id_value] = python_code

    mutate_codes = load_mutate_codes(f"mutation_jsonl/{mutate_method}.jsonl")


    try:
        with open(output_file, 'w') as file:
            for old_id, mutate_code in tqdm(mutate_codes.items()):
                code = ds[old_id]
                new_code = mutate_code

                for code_type, test_code in [("original", code), ("modified", new_code)]:
                    
                    for _ in range(nsample):
                        client = create_client(model_name)
                        generated_content = generate_content(client, model_name, \
                                        prompt.format(source_lang, test_code, target_lang), temperature)
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