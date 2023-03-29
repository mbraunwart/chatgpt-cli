import argparse
from commands import HelpCommand, ModelsCommand, CompletionCommand


class ChatGPTCLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="ChatGPT CLI is a powerful command-line tool for interacting with OpenAI's ChatGPT API.",
            epilog="Example usage: \npython main.py models\npython main.py completion gpt-3.5-turbo 'Translate the following English text to French: Hello, World!'",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.subparsers = self.parser.add_subparsers(dest="command")

        self.commands = [HelpCommand(), ModelsCommand(), CompletionCommand()]
        #     # "usage": self.usage,
        #     # "status": self.status,
        #     # "files": self.files,py
        for command in self.commands:
            command.set_parser(self.subparsers)

        self.args = self.parser.parse_args()

    def run(self) -> None:
        cli_command = next(
            (
                command
                for command in self.commands
                if command.command_name == self.args.command
            ),
            None,
        )
        if cli_command:
            cli_command.run(self)
        else:
            self.parser.print_help()
