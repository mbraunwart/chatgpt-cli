import argparse
import textwrap
import chatgpt_api
from datetime import datetime
from db_models import HistoryTopic, Message, UserSession
from typing import List, Dict, Any, Optional
from termcolor import colored
from tabulate import tabulate


def response_box(text: str, max_column: int = 80) -> None:
    paragraphs = text.split("\n")
    wrapped_paragraphs = [
        textwrap.wrap(paragraph, width=max_column) for paragraph in paragraphs
    ]

    lines = []
    for wrapped_paragraph in wrapped_paragraphs:
        lines.extend(wrapped_paragraph)
        lines.append("")  # Add an empty line for spacing between paragraphs

    max_line_length = max(len(line) for line in lines)

    horizontal = colored("+" + "-" * (max_line_length + 2) + "+", "cyan")
    vertical = colored("|", "cyan")

    print(horizontal)
    for line in lines:
        print(f"{vertical} {line.ljust(max_line_length)} {vertical}")
    print(horizontal)


class Command:
    def __init__(self, command_name: str, help_text: str, examples: str = "") -> None:
        self.command_name = command_name
        self.help_text = help_text
        self.examples = examples
        self.parser: Optional[argparse.ArgumentParser] = None

    def set_parser(self, subparsers: Any) -> None:
        self.parser = subparsers.add_parser(
            self.command_name, help=self.help_text, epilog=self.examples
        )

    def run(self, cli: Any) -> None:
        cli.parser.print_help()


class HelpCommand(Command):
    def __init__(self) -> None:
        super().__init__("help", "Show help information")

    def run(self, cli: Any) -> None:
        cli.parser.print_help()


class ModelsCommand(Command):
    def __init__(self) -> None:
        super().__init__(
            "models",
            "List available models. Retrieves a list of all available GPT models, including their IDs, creation dates, root model names, and ownership information",
            "python main.py models",
        )

    def run(self, cli: Any) -> None:
        models = chatgpt_api.get_chat_gpt_model_list()
        if models is not None:
            print(
                tabulate(
                    [
                        [model.id, model.created, model.root, model.owned_by]
                        for model in models
                    ],
                    headers=["ID", "Created", "Root", "Owned By"],
                    tablefmt="grid",
                )
            )
        else:
            print("No models found")


class TopicsCommand(Command):
    def __init__(self) -> None:
        super().__init__(
            "topics",
            "Manage your Chat GPT conversation topics. List topics, rename topics, view prompt history from a topic."
            'python main.py topics, python main.py topics --update-name "new name", python main.py topics --list, python main.py topics "net topic name"',
        )

    def set_parser(self, subparsers: Any) -> None:
        super().set_parser(subparsers)
        assert self.parser is not None
        self.parser.add_argument(
            "-n",
            "--name",
            type=str,
            nargs="?",
            help='Create a new topic, defaults to "New Topic"',
        )
        self.parser.add_argument(
            "-m",
            "--model",
            type=str,
            nargs="?",
            default="gpt-3.5-turbo",
            help='Set the model for use with your topic. defaults to "gpt-3.5-turbo"',
        )
        self.parser.add_argument(
            "--set-current-topic",
            type=int,
            help="Set the current topic id to be used with completions.",
        )
        self.parser.add_argument(
            "-l", "--list", action="store_true", help="List all topics."
        )
        self.parser.add_argument(
            "--update-name", type=str, help="Update the name of a topic"
        )
        self.parser.add_argument(
            "-id", "--topic-id", type=int, help="The ID of the topic to update or view"
        )
        self.parser.add_argument(
            "--history", action="store_true", help="View the prompt history of a topic"
        )

    def run(self, cli: Any) -> None:
        if cli.args.list:
            self.list_topics(cli)
        elif cli.args.set_current_topic is not None:
            cli.current_topic_id = cli.args.set_current_topic
            topic = cli.db.get_by_id(cli.db_session, HistoryTopic, cli.current_topic_id)
            print(f"Set {topic.name}")
        elif cli.args.name is not None and cli.args.model is not None:
            topic = cli.db.add(
                cli.db_session, HistoryTopic(name=cli.args.name, model=cli.args.model)
            )
            cli.user_session.topic_id = topic.id
            cli.db.update(cli.db_session, cli.user_session)
        else:
            if self.parser is not None:
                self.parser.print_help()

    def list_topics(self, cli: Any) -> None:
        topics = cli.db.get_all(cli.db_session, HistoryTopic)
        print(
            tabulate(
                [[topic.id, topic.name, topic.model] for topic in topics],
                headers=["ID", "Topic Name", "Model"],
            )
        )


class CompletionCommand(Command):
    def __init__(self) -> None:
        super().__init__(
            "completion",
            "Generate a completion. Requires the model name (e.g., 'text-davinci-002') and a prompt (e.g., 'Translate the following English text to French: '{'Hello, World!'}''). Optionally, you can set the maximum number of tokens to generate using the '--max-tokens' flag.",
            "python main.py completion text-davinci-002 'Translate the following English text to French: Hello, World!'",
        )

    def set_parser(self, subparsers: Any) -> None:
        super().set_parser(subparsers)
        assert self.parser is not None
        self.parser.add_argument(
            "topic-id",
            type=int,
            nargs="?",
            default=None,
            help="The topic-id to continue working with.",
        )
        self.parser.add_argument(
            "prompt", nargs="?", help="The prompt for the completion"
        )
        self.parser.add_argument(
            "--set-topic-name",
            type=str,
            default="latest",
            help="Set the topic name for the current conversation. (default: latest, pulls the most recent conversation)",
        )
        self.parser.add_argument(
            "--max-tokens",
            type=int,
            default=500,
            help="The maximum number of tokens to generate (default: 5)",
        )

    def run(self, cli: Any) -> None:
        topic_id = (
            cli.args.topic_id if cli.args.topic_id is not None else cli.current_topic_id
        )
        if topic_id is None:
            print(
                "No topic is selected.\nPlease specify a topic ID or create a new topic."
            )
            if self.parser is not None:
                self.parser.print_help()
        else:
            topic = cli.db.get_by_id(cli.db_session, HistoryTopic, topic_id)
            if topic is None:
                print(f"No topic found with ID {topic_id}")
                if self.parser is not None:
                    self.parser.print_help()
                return

        if not cli.args.prompt:
            cli.args.prompt = input("Please enter a prompt: ")

        prompt_message = chatgpt_api.Message(
            role=chatgpt_api.Role.ASSISTANT, content=cli.args.prompt
        )
        messages = [
            {"role": message.role.name.lower(), "content": message.content}
            for message in [prompt_message]
        ]

        self.process_completion(cli.args.model, messages, cli.args.max_tokens)
        cli.user_session.last_active = datetime.now()
        cli.db.update(cli.db_session, cli.user_session)

    def process_completion(
        self, model: str, messages: List[Dict[str, str]], max_tokens: int
    ) -> None:
        completion = chatgpt_api.invoke_chat_gpt_completion(model, messages, max_tokens)
        if "choices" in completion:
            response_box(
                f"Prompt: {messages[0]['content']}\nResponse:\n"
                + completion["choices"][0]["message"]["content"]
            )
        else:
            print(f"Received partial data: {completion}")
