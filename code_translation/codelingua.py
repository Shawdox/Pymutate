import subprocess
from datetime import datetime

def run_command(command):
    """Runs a shell command and waits for its completion."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error: Command failed with return code {result.returncode}")

def main(model, dataset):
    # Constants
    TEMP = "0.2"
    DATASET = dataset

    # Get current timestamp
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Mutations
    mutations = ["FCVR3", "ICVN", "IFC"]
    # mutations = ["ConstantUnfoldding", "VarNorm", "VarRand3", "IfAddShortCircuiting", "For2While"]
    # mutations = ["VarNorm", "VarRand3"]

    # Commands template
    command_templates = [
        "/opt/homebrew/bin/python3.11 code_translation/generation/codelingua.py --dataset {dataset} --model {model} --temp {temp} --curtime {curtime} --mutate {mutate}",
        "/opt/homebrew/bin/python3.11 code_translation/execution/codelingua.py --dataset {dataset} --model {model} --temp {temp} --curtime {curtime} --mutate {mutate}",
        "/opt/homebrew/bin/python3.11 code_translation/metrics/evaluation.py --dataset {dataset} --model {model} --temp {temp} --curtime {curtime} --passatk 1 --mutate {mutate}"
    ]

    # Execute commands for each mutation
    for mutate in mutations:
        for command_template in command_templates:
            command = command_template.format(dataset=DATASET, model=model, temp=TEMP, curtime=TIMESTAMP, mutate=mutate)
            print(f"Running command: {command}")
            run_command(command)

    print("All commands executed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run codelingua pipeline.")
    parser.add_argument("--model", required=True, help="The model to use (e.g., gpt-4o).")
    parser.add_argument("--dataset", required=True, help="avatar/codenet")
    args = parser.parse_args()

    main(args.model, args.dataset)
