import argparse
from commands import HelpCommand, TopicsCommand, ModelsCommand, CompletionCommand
from typing import Optional, cast
from db import Database
from db_models import UserSession


class ChatGPTCLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="ChatGPT CLI is a powerful command-line tool for interacting with OpenAI's ChatGPT API.",
            epilog="Example usage: \npython main.py models\npython main.py completion gpt-3.5-turbo 'Translate the following English text to French: Hello, World!'",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.subparsers = self.parser.add_subparsers(dest="command")

        db = Database()
        db.init_db()
        self.db_session = db.SessionLocal()
        self.db = db

        self.current_topic_id: Optional[int] = None
        self.user_session = self.load_active_user_session()

        self.commands = [
            HelpCommand(),
            TopicsCommand(),
            ModelsCommand(),
            CompletionCommand(),
        ]
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

    def load_active_user_session(self) -> UserSession:
        user_session = self.db.get_active_user_session()
        if user_session:
            if user_session.topic is not None:
                self.current_topic_id = cast(int, user_session.topic_id)
                print(f"Current topic is {user_session.topic.name}")
            # else:
            #     print("No topic associated with this session, please create a new topic.\npython main.py topic --name \"new topic name\" --model \"gpt-3.5-turbo\"")
            return user_session
        else:
            return self.db.create_user_session()
