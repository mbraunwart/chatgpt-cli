import os
import json
import requests
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any

headers = {
    "Authorization": f"Bearer {os.environ.get('ChatGPTToken')}",
    "Content-Type": "application/json",
}

BASE_URL = "https://api.openai.com/v1"


class Role(Enum):
    SYSTEM = auto()
    USER = auto()
    ASSISTANT = auto()


@dataclass
class Message:
    role: Role
    content: str


@dataclass
class Model:
    id: str
    created: datetime
    root: str
    owned_by: str


def get_chat_gpt_model_list() -> List[Model]:
    url = f"{BASE_URL}/models"
    response = requests.get(url, headers=headers)
    models = response.json()["data"]

    filtered_models = [
        Model(
            id=model["id"],
            created=datetime.fromtimestamp(model["created"]),
            root=model["root"],
            owned_by=model["owned_by"],
        )
        for model in models
        if model["object"] == "model"
    ]

    return filtered_models


def invoke_chat_gpt_completion(
    model: str, messages: List[Dict[str, str]], max_tokens: int = 50
) -> Any:
    url = f"{BASE_URL}/chat/completions"
    data = {"model": model, "messages": messages, "max_tokens": max_tokens}
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=300)
    completion = response.json()

    return completion


def get_chat_gpt_usage() -> Dict[str, str]:
    url = f"{BASE_URL}/usage"
    response = requests.get(url, headers=headers, timeout=30)
    usage_data = response.json()

    usage = {
        "total_tokens": usage_data["total_tokens"],
        "prompt_tokens": usage_data["prompt_tokens"],
        "completion_tokens": usage_data["completion_tokens"],
        "user": usage_data["user"],
    }

    return usage


def get_chat_gpt_fine_tune_status(model: str) -> Dict[str, str]:
    url = f"{BASE_URL}/models/{model}"
    response = requests.get(url, headers=headers, timeout=30)
    status_data = response.json()

    status = {
        "id": status_data["id"],
        "object": status_data["object"],
        "status": status_data["status"],
        "progress": status_data["progress"],
    }

    return status


def get_chat_gpt_list_files() -> List[Dict[str, Any]]:
    url = f"{BASE_URL}/files"
    response = requests.get(url, headers=headers, timeout=30)
    files_data = response.json()["data"]

    files = [
        {
            "id": file["id"],
            "object": file["object"],
            "created": datetime.fromtimestamp(file["created"]),
            "filename": file["filename"],
            "purpose": file["purpose"],
        }
        for file in files_data
    ]

    return files
