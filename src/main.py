import argparse
import json
from termcolor import colored
from colorama import init
from tabulate import tabulate
from chatgpt_api import (
    get_chat_gpt_model_list,
    invoke_chat_gpt_completion,
    get_chat_gpt_usage,
    get_chat_gpt_fine_tune_status,
    get_chat_gpt_list_files,
    Role,
    Message
)

init(autoreset=True)

def response_box(text):
    lines = text.split('\n')
    max_line_length = max(len(line) for line in lines)

    top_bottom_border = colored('+' + '-' * (max_line_length + 2) + '+', 'cyan')
    left_right_border = colored('|', 'cyan')

    print(top_bottom_border)
    for line in lines:
        print(f'{left_right_border} {line.ljust(max_line_length)} {left_right_border}')
    print(top_bottom_border)

# Create the top-level parser
parser = argparse.ArgumentParser(description="ChatGPT CLI")
subparsers = parser.add_subparsers(dest="command")

# Create the parser for the "help" command
help_parser = subparsers.add_parser("help", help="Show help information")

# Create the parser for the "models" command
models_parser = subparsers.add_parser("models", help="List available models. Retrieves a list of all available GPT models, including their IDs, creation dates, root model names, and ownership information. Example command: 'python main.py models'")

# Create the parser for the "completion" command
completion_parser = subparsers.add_parser("completion", help="Generate a completion. Requires the model name (e.g., 'text-davinci-002') and a prompt (e.g., 'Translate the following English text to French: '{'Hello, World!'}''). Optionally, you can set the maximum number of tokens to generate using the '--max_tokens' flag. Example command: 'python main.py completion text-davinci-002 'Translate the following English text to French: Hello, World!''")
completion_parser.add_argument("model", help="The model to use (e.g., 'text-davinci-002')")
completion_parser.add_argument("prompt", nargs="?", help="The prompt for the completion")
completion_parser.add_argument("--max_tokens", type=int, default=5, help="The maximum number of tokens to generate (default: 5)")

# Create the parser for the "usage" command
usage_parser = subparsers.add_parser("usage", help="Retrieve API usage. Returns information about the total tokens used, prompt tokens, completion tokens, and user. Example command: 'python main.py usage'")

# Create the parser for the "status" command
status_parser = subparsers.add_parser("status", help="Get fine-tuning status for a model. Requires the model name (e.g., 'text-davinci-002'). Returns the fine-tuning status, progress, and other related information. Example command: 'python main.py status text-davinci-002'")
status_parser.add_argument("model", help="The model to get the status for (e.g., 'text-davinci-002')")

# Create the parser for the "files" command
files_parser = subparsers.add_parser("files", help="List uploaded files. Returns a list of uploaded files, including their IDs, object types, creation dates, filenames, and purposes. Example command: 'python main.py files'")

# Parse the arguments and call the corresponding function
args = parser.parse_args()

if args.command == "help":
    parser.print_help()

elif args.command == "models":
    models = get_chat_gpt_model_list()
    if models is not None:
        print(
            tabulate(
                [[model.id, model.created, model.root, model.owned_by] for model in models],
                headers=["ID", "Created", "Root", "Owned By"],
                tablefmt="grid",
            )
        )
    else:
        print("No models found")

elif args.command == "completion":
    if not args.prompt:
        args.prompt = input("Please enter a prompt: ")

    prompt_message = Message(role=Role.ASSISTANT, content=args.prompt)
    #system_message = Message(role=Role.SYSTEM, content="You are a helpful assistant.")
    messages = [{"role": message.role.name.lower(), "content": message.content} for message in [prompt_message]]

    completion = json.dumps(invoke_chat_gpt_completion(args.model, messages, args.max_tokens)["choices"][0]["message"]["content"], indent=2)
    response_box(completion)

elif args.command == "usage":
    usage = get_chat_gpt_usage()
    print(json.dumps(usage, indent=2))

elif args.command == "status":
    status = get_chat_gpt_fine_tune_status(args.model)
    print(json.dumps(status, indent=2))

elif args.command == "files":
    files = get_chat_gpt_list_files()
    print(json.dumps(files, indent=2, default=str))

else:
    parser.print_help()