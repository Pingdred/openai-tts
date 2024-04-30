from enum import Enum

from pydantic import BaseModel, Field, SecretStr

from cat.mad_hatter.decorators import plugin


class VoiceQuality(Enum):
    STANDARD = "tts-1"
    HD = "tts-1-hd"


class Voice(Enum):
    ALLOY = "Alloy"
    FABLE = "Fable"
    ECHO = "Echo"
    ONYX = "Onyx"
    NOVA = "Nova"


class SupportedAudioFormat(Enum):
    MP3 =  "mp3"
    OPUS = "opus"
    AAC = "aac"
    FLAC = "flac"
    WAV = "wav"
    PCM = "pcm"


class ResponceType(Enum):
    HTML = "HTML content"
    KEY = "TTS key"


class VoiceEngineSettings(BaseModel):
    openai_api_key: SecretStr = Field(
        title="OpenAi API Key"
    )
    responce_type: ResponceType = Field(
        title="Responce type",
        description="""How you want to recive the speech file:
         - HTML: The message content will be the audio embedded in an html element (For the admin).
         - TTS key: The url to file will be added in the websocket wesponce under responce["tts"] (For other clients).""",
        default=ResponceType.HTML
    )
    quality: VoiceQuality = Field(
        title="Quality", 
        default=VoiceQuality.STANDARD
    )
    voice: Voice = Field(
        title="Voice", 
        default=Voice.ALLOY
    )
    output_format: SupportedAudioFormat = Field(
        title="Speech format",
        default=SupportedAudioFormat.MP3
    )
    autoplay: bool = Field(
        title="Autoplay (Only HTML content)",
        description="The Speech will be auto played in the admin",
        default=True
    )
    send_text: bool = Field(
        title="Send text (Only HTML content)", 
        description="Send the text message along the Speech",
        default=False
    )


@plugin
def settings_model():
    return VoiceEngineSettings
