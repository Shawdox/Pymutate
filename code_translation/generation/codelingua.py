import argparse
import json
import os
import sys
import traceback
from tqdm import tqdm

current_working_directory = os.getcwd()
if current_working_directory not in sys.path:
    sys.path.insert(0, current_working_directory)

from util.helper import generate_content, get_output_file_path_for_translation, \
    load_dataset_with_retry, load_mutate_codes_for_translation, create_client

def main():
    parser = argparse.ArgumentParser(description="A simple argument parser.")
    parser.add_argument("--dataset", type=str, help="Dataset")
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--temp", type=float, help="Temperature")
    parser.add_argument("--nsample", type=int, default=10, help="N sample in Pass@k")
    parser.add_argument("--mutate", type=str, help="Mutate method")
    parser.add_argument("--curtime", type=str, help="Current time")
    parser.add_argument("--sourlang", type=str, default="Python", help="Source language")
    parser.add_argument("--tarlang", type=str, default="Java", help="Target language")

    args = parser.parse_args()

    dataset_name = args.dataset
    model_name = args.model
    temperature = args.temp
    nsample = args.nsample
    mutate_method = args.mutate
    current_time = args.curtime
    source_lang = args.sourlang
    target_lang = args.tarlang
    prompt = "You are a code translation expert. Translate the {0} code below to {2}\n\n{0}\n{1}\n\n{2}\n"

    output_file = get_output_file_path_for_translation(dataset_name, model_name, mutate_method, temperature, current_time)

    if dataset_name == "codenet":
        ds = load_dataset_with_retry("iidai/codenet")
    elif dataset_name == "avatar":
        ds = load_dataset_with_retry("iidai/avatar")
    else:
        print("Check dataset name.")
        sys.exit(1)

    try:
        mutate_codes = load_mutate_codes_for_translation(f"code_translation/mutated_datasets/SingleMutated/CodeLingua/{dataset_name}_{mutate_method}.jsonl")
    except:
        mutate_codes = load_mutate_codes_for_translation(f"code_translation/mutated_datasets/MultiMutated/CodeLingua/{dataset_name}_{mutate_method}.jsonl")

    ds = ds['train'].filter(lambda x: x['language'] == 'Python')

    try:
        with open(output_file, 'w') as file:
            for old_id, mutate_code in tqdm(mutate_codes.items()):
                code = ds.filter(lambda x: x['id'] == old_id)[0]['code']
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
        error_output_file = "code_translation/result/[ERROR]" + output_file.split("/")[2]
        os.rename(output_file, error_output_file)


if __name__ == "__main__":
    main()