from openai import OpenAI

from cat.mad_hatter.decorators import hook

from .utils import (
    generate_file_name,
    get_speech_file_path,
    get_speech_file_url,
    create_html_message,
)
from .settings import VoiceEngineSettings, ResponceType


# Text-to-speech function
def generate_audio_file(text: str, user_id: str, settings: VoiceEngineSettings):
    # Generate speech file name
    file_name = generate_file_name(settings.output_format.value)
    # Get path to speech file
    speech_files_path = get_speech_file_path(user_id)

    # Create directory to store speech files 
    speech_files_path.mkdir(parents=True, exist_ok=True)

    # Create OpenAi Client
    client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
    # Chreate Speech
    response = client.audio.speech.create(
        model=settings.quality.value.lower(), voice=settings.voice.value.lower(), input=text
    )
    response.write_to_file(speech_files_path / file_name)

    return file_name


@hook
def before_cat_sends_message(message, cat):
    # Load settings
    settings = VoiceEngineSettings(**(cat.mad_hatter.get_plugin().load_settings()))
    # generate speech
    speech_path = generate_audio_file(message["content"], cat.user_id, settings)
    # Create speech urls
    speech_url = get_speech_file_url(user_id=cat.user_id) + speech_path

    if settings.responce_type == ResponceType.HTML:
        # Embedd audio in html and update content text
        html_message = create_html_message(
            audio_source=speech_url, autoplay=settings.autoplay
        )

        cat.send_chat_message(html_message)

    elif settings.responce_type == ResponceType.KEY:
        # Add speech url to websocket responce under tts key
        message["tts"] = speech_url
   
    return message
