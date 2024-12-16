import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime
from tqdm import tqdm

from datasets import load_dataset
from openai import OpenAI
from fireworks.client import Fireworks

from util import timeout


def load_dataset_with_retry(max_attempts=20, delay=1):
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt}: Trying to load the dataset...")
            ds = load_dataset("cruxeval-org/cruxeval")
            print("Dataset loaded successfully!")
            return ds
        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt < max_attempts - 1:
                print("Retrying...")
                time.sleep(delay)
            else:
                print("Max retries reached. Exiting the program.")
                sys.exit(1)


def load_mutate_codes(mutation_filename):
    mutate_codes = {}
    with open(mutation_filename, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            if 'code' in data and 'old_id' in data:
                old_id = int(data['old_id'].split("_")[-1])
                mutate_codes[old_id] = data['code']
    return mutate_codes


def generate_output_file(model_name, mutate_method, temperature, passat, current_time):
    if "#" in model_name:
        simplified_model_name = model_name.split('/')[3].split('#')[0]
    else:
        simplified_model_name = model_name.split('/')[-1]

    if mutate_method in [
        "AugAssign2Assign", "AddIndVar", "Assign2Ternary", "AssignUnfolding",
        "ConstantUnfolding", "For2While", "IfReverse", "VarNorm", "VarRand1",
        "VarRand3", "VarRand5"
    ]:
        return f"./result/{simplified_model_name}_{mutate_method}_t{temperature}_pass@{passat}_{current_time}.jsonl"
    else:
        print("Method not found.")
        sys.exit(1)


def create_client(model_name):
    if "gpt" in model_name:
        return OpenAI(
            base_url="https://api.openai.com/v1",
            api_key="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"
        )
    elif model_name == "deepseek-chat":
        return OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key="sk-6cb72a4ef04a4b149fc3e2189b8c3ca4",
        )
    else:
        return Fireworks(api_key="fw_3ZfzgdBmufwmNxAGZyye6E8B")


def generate_content(client, model_name, prompt, test_code, temperature, max_attempts=20):
    for _ in range(max_attempts):
        try:
            if "gpt" in model_name \
                or "llama-v3" in model_name \
                or "starcoder" in model_name \
                or model_name == "deepseek-chat":
                result = client.chat.completions.create(
                    messages=[{'role': 'user', 'content': prompt + test_code}],
                    model=model_name,
                    temperature=temperature,
                    max_tokens=500
                )
                return result.choices[0].message.content
            else:
                result = client.completion.create(
                    prompt=prompt + test_code,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=500
                )
                return result.choices[0].text
        except Exception as e:
            print(e)
            time.sleep(1)
    return None


def main():
    prompt = """Based on the given Python code, which may contain errors, complete the assert statement with the output when executing the code on the given test case. Do NOT output any extra information, even if the function is incorrect or incomplete. Output "# done" after the assertion.
    """

    parser = argparse.ArgumentParser(description="A simple argument parser.")
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--temp", type=float, help="Temperature")
    parser.add_argument("--passat", type=int, help="Pass@")
    parser.add_argument("--mutate", type=str, help="Mutate method")
    args = parser.parse_args()

    model_name = args.model
    temperature = args.temp
    passat = args.passat
    mutate_method = args.mutate

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = generate_output_file(model_name, mutate_method, temperature, passat, current_time)

    ds = load_dataset_with_retry()
    mutate_codes = load_mutate_codes(f"./mutation_jsonl/{mutate_method}.jsonl")

    original_count = 0
    new_count = 0
    

    try:
        with open(output_file, 'w') as file:
            for old_id, mutate_code in tqdm(mutate_codes.items()):
                code = ds['test']['code'][old_id] + f"\nassert f({ds['test']['input'][old_id]}) =="
                if "VarNorm" in mutate_method or "VarRand" in mutate_method:
                    new_code = mutate_code
                else:
                    new_code = mutate_code + f"\nassert f({ds['test']['input'][old_id]}) =="

                original_success = False
                new_success = False

                for code_type, test_code in [("original", code), ("modified", new_code)]:
                    success_flag = False
                    
                    for _ in range(passat):
                        client = create_client(model_name)
                        generated_content = generate_content(client, model_name, prompt, test_code, temperature)

                        raw_generated_content = generated_content

                        if generated_content:

                            generated_content = generated_content.replace('`', '').replace('python', '').strip()
                            if "==" in generated_content:
                                generated_content = generated_content.split("==")[-1].strip()
                            generated_content = generated_content.split("\n", 1)[0].split("# done", 1)[0]

                            exec_code = test_code + generated_content

                            try:
                                timeout.exec_with_timeout(exec_code)
                                success_flag = True
                            except Exception as e:
                                pass

                            json.dump({
                                "id": old_id,
                                "code_type": code_type,
                                "code": test_code,
                                "generated_content": generated_content,
                                "execution_success": success_flag,
                                "raw_generated_content": raw_generated_content
                            }, file)
                            file.write('\n')

                            if success_flag:
                                break

                    if success_flag:
                        if code_type == "original":
                            original_count += 1
                            original_success = True
                        else:
                            new_count += 1
                            new_success = True
                
                file.write(f"i:{old_id}  Original Success:{original_success}  New Success:{new_success}\n")
                file.write(f"i:{old_id}  Original Count:{original_count}  New Count:{new_count}\n\n")

        print("Original Count:", original_count)
        print("New Count:", new_count)

        with open(output_file, 'a') as file:
            file.write(f"Original Count: {original_count}\n")
            file.write(f"New Count: {new_count}\n")
            file.write(f"model: {model_name}\n")
            file.write(f"mutate method: {mutate_method}\n")
            file.write(f"temperature: {temperature}\n")
            file.write(f"passat: {passat}\n")

    except Exception as e:
        traceback.print_exc()
        error_message = traceback.format_exc()
        with open(output_file, 'a') as file:
            file.write(error_message)
        error_output_file = "./result/[ERROR]" + output_file.split("/")[2]
        os.rename(output_file, error_output_file)


if __name__ == "__main__":
    main()
