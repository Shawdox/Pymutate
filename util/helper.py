import time
import sys
import json

from datasets import load_dataset
from openai import OpenAI
from fireworks.client import Fireworks


def load_dataset_with_retry(dataset_name, max_attempts=20, delay=1):
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt}: Trying to load the dataset...")
            ds = load_dataset(dataset_name)
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
                old_id = int(str(data['old_id']).split("_")[-1])
                mutate_codes[old_id] = data['code']
    return mutate_codes


def get_output_file_path(model_name, mutate_method, temperature, current_time):
    if "#" in model_name:
        simplified_model_name = model_name.split('/')[3].split('#')[0]
    else:
        simplified_model_name = model_name.split('/')[-1]

    return f"./result/{simplified_model_name}_{mutate_method}_t{temperature}_{current_time}.jsonl"
    


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


def generate_content(client, model_name, prompt, temperature, max_attempts=20):
    for _ in range(max_attempts):
        try:
            if "gpt" in model_name \
                or "llama-v3" in model_name \
                or model_name == "deepseek-chat":
                result = client.chat.completions.create(
                    messages=[{'role': 'user', 'content': prompt}],
                    model=model_name,
                    temperature=temperature,
                    max_tokens=500
                )
                return result.choices[0].message.content
            else:
                result = client.completion.create(
                    prompt=prompt,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=100
                )
                return result.choices[0].text
        except Exception as e:
            print(e)
            time.sleep(1)
    return None