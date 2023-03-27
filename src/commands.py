import asyncio
import json
from termcolor import colored
from tabulate import tabulate
from chatgpt_api import (
    get_chat_gpt_model_list,
    invoke_chat_gpt_completion,
    invoke_chat_gpt_completion_async,
    get_chat_gpt_usage,
    get_chat_gpt_fine_tune_status,
    get_chat_gpt_list_files,
    Role,
    Message
)

def response_box(text):
    lines = text.split('\n')
    max_line_length = max(len(line) for line in lines)

    top_bottom_border = colored('+' + '-' * (max_line_length + 2) + '+', 'cyan')
    left_right_border = colored('|', 'cyan')

    print(top_bottom_border)
    for line in lines:
        print(f'{left_right_border} {line.ljust(max_line_length)} {left_right_border}')
    print(top_bottom_border)

class Command:
    def __init__(self, command_name, help_text, examples=None):
        self.command_name = command_name
        self.help_text = help_text
        self.examples = examples
        self.parser = None
        
    def set_parser(self, subparsers):
        self.parser = subparsers.add_parser(
            self.command_name,
            help = self.help_text,
            epilog = self.examples
        )
        
class HelpCommand(Command):
    def __init__(self):
        super().__init__("help", "Show help information")
        
    def run(self, cli):
        cli.parser.print_help()
        
class ModelsCommand(Command):
    def __init__(self):
        super().__init__("models", "List available models. Retrieves a list of all available GPT models, including their IDs, creation dates, root model names, and ownership information. Example command: 'python main.py models'")
        
    def run(self, cli):
        models = get_chat_gpt_model_list()
        if models is not None:
            print(
                tabulate(
                    [[model.id, model.created, model.root, model.owned_by]
                        for model in models],
                    headers=["ID", "Created", "Root", "Owned By"],
                    tablefmt="grid",
                )
            )
        else:
            print("No models found")
            
class CompletionCommand(Command):
    def __init__(self):
        super().__init__(
            "completion", 
            "Generate a completion. Requires the model name (e.g., 'text-davinci-002') and a prompt (e.g., 'Translate the following English text to French: '{'Hello, World!'}''). Optionally, you can set the maximum number of tokens to generate using the '--max_tokens' flag.", 
            "python main.py completion text-davinci-002 'Translate the following English text to French: Hello, World!'"
        )
        
    def set_parser(self, subparsers):
        super().set_parser(subparsers)
        self.parser.add_argument("model", help="The model to use (e.g., 'text-davinci-002')")
        self.parser.add_argument("prompt", nargs="?", help="The prompt for the completion")
        self.parser.add_argument("--max_tokens", type=int, default=5, help="The maximum number of tokens to generate (default: 5)")
        
    async def process_completion(self, model, messages, max_tokens):
        async for completion in invoke_chat_gpt_completion_async(model, messages, max_tokens):
            if "choices" in completion:
                response_box(completion["choices"][0]["message"]["content"])
            else:
                print(f"Received partial data: {completion}")

    def run(self, cli):
        if not cli.args.prompt:
            cli.args.prompt = input("Please enter a prompt: ")

        prompt_message = Message(role=Role.ASSISTANT, content=cli.args.prompt)
        #system_message = Message(role=Role.SYSTEM, content="You are a helpful assistant.")
        messages = [{"role": message.role.name.lower(), "content": message.content} for message in [prompt_message]]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process_completion(cli.args.model, messages, cli.args.max_tokens))