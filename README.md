# OpenAI ChatGPT API Python Client

- [OpenAI ChatGPT API Python Client](#openai-chatgpt-api-python-client)
  - [Overview](#overview)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command Line Interface (CLI)](#command-line-interface-cli)
    - [Python Library](#python-library)
  - [Examples](#examples)
    - [CLI Examples](#cli-examples)

## Overview

This Python client provides a simple way to interact with OpenAI's ChatGPT API. With this client, you can list available models, check usage, and generate completions based on user input.

## Requirements

    Python 3.11+

## Installation

`pip install -r requirements.txt`

## Usage

### Command Line Interface (CLI)

You can use the CLI tool to interact with the OpenAI ChatGPT API. The following commands are available:

- `models`: List available models.
- `completion`: Generate a completion based on the given prompt.
- `usage`: Retrieve API usage.
- `status`: Get fine-tuning status for a model.
- `files`: List uploaded files.

### Python Library

You can also use this client as a Python library. Import the necessary functions from chatgpt_api.py and use them in your Python code.

## Examples

### CLI Examples

1. Listing models

`python main.py models`

2. Generating a completion

`python main.py completion "gpt-3.5-turbo" "Is this thing on?"`

3. Retrieving API usage

`python main.py usage`

4. Getting fine-tuning status for a model

`python main.py status "gpt-3.5-turbo"`

5. Listing uploaded files

`python main.py files`
