import json
import datetime

from pathlib import Path
from typing import Union

from cat.mad_hatter.mad_hatter import MadHatter
from cat.utils import get_static_path, get_static_url

from .settings import GlobalSettings, UserSettings


def generate_file_name(ext)-> str:
    return f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{ext}"


def get_speech_file_path(user_id: Union[str, None] = None) -> Path:
    files_path = Path(get_static_path()) / "openai_voice_engine"
    return files_path / (user_id if user_id else "")


def get_speech_file_url(user_id: str) -> str:
    return get_static_url() + f"openai_voice_engine/{user_id}/"   


def create_html_message(audio_source: str) -> str:
    audio_element = f"""
<audio controls>
    <source src="{audio_source}" type="audio/mpeg">
</audio>"""
    return audio_element 


def load_user_settings(user_id: int) -> UserSettings:
    this_plugin = MadHatter().get_plugin()

    user_settings_path = Path(this_plugin.path) / "users_settings"

    if not user_settings_path.exists():
        user_settings_path.mkdir()

    try:
        with open(user_settings_path / f"{user_id}.json") as f:
            user_settings = json.load(f)
        user_settings = UserSettings(**user_settings)
    except Exception:
        global_settings = GlobalSettings(**this_plugin.load_settings())
        user_settings = UserSettings(
            voice=global_settings.voice, 
            speed=global_settings.speed
        )

    return user_settings


def save_user_settings(user_id: int, settings: UserSettings):
    this_plugin = MadHatter().get_plugin()
    user_settings_path = Path(this_plugin.path) / "users_settings"

    if not user_settings_path.exists():
        user_settings_path.mkdir()

    with open(user_settings_path / f"{user_id}.json", "w") as f:
        json.dump(settings.model_dump(mode='json'), f)