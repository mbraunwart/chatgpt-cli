from colorama import init
from chatgpt_cli import ChatGPTCLI

init(autoreset=True)

if __name__ == "__main__":
    cli = ChatGPTCLI()
    cli.run()
