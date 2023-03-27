from colorama import init
from chatgpt_cli import ChatGPTCLI

init(autoreset=True)

if __name__ == "__main__":
    cli = ChatGPTCLI()
    cli.run()

# # Create the parser for the "usage" command
# usage_parser = subparsers.add_parser("usage", help="Retrieve API usage. Returns information about the total tokens used, prompt tokens, completion tokens, and user. Example command: 'python main.py usage'")

# # Create the parser for the "status" command
# status_parser = subparsers.add_parser("status", help="Get fine-tuning status for a model. Requires the model name (e.g., 'text-davinci-002'). Returns the fine-tuning status, progress, and other related information. Example command: 'python main.py status text-davinci-002'")
# status_parser.add_argument("model", help="The model to get the status for (e.g., 'text-davinci-002')")

# # Create the parser for the "files" command
# files_parser = subparsers.add_parser("files", help="List uploaded files. Returns a list of uploaded files, including their IDs, object types, creation dates, filenames, and purposes. Example command: 'python main.py files'")

# # Parse the arguments and call the corresponding function
# args = parser.parse_args()

# elif args.command == "usage":
#     usage = get_chat_gpt_usage()
#     print(json.dumps(usage, indent=2))

# elif args.command == "status":
#     status = get_chat_gpt_fine_tune_status(args.model)
#     print(json.dumps(status, indent=2))

# elif args.command == "files":
#     files = get_chat_gpt_list_files()
#     print(json.dumps(files, indent=2, default=str))

# else:
#     parser.print_help()