from pathlib import Path
from typing import Union
import datetime

from cat.utils import get_static_path, get_static_url

FILES_PATH = Path(get_static_path()) / "openai_voice_engine"


def generate_file_name(ext)-> str:
    return f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{ext}"


def get_speech_file_path(user_id: Union[str, None] = None) -> Path:
    return FILES_PATH / (user_id if user_id else "")


def get_speech_file_url(user_id: str) -> str:
    return get_static_url() + f"openai_voice_engine/{user_id}/"    
