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
    SHIMMER = "Shimmer"


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
    response_type: ResponseType = Field(
        title="Response type",
        description="""How you want to receive the speech file:
         - HTML: The message content will be the audio embedded in an html element (For the admin).
         - TTS key: The url to file will be added in the websocket response under response["tts"] (For other clients).""",
        default=ResponseType.HTML
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
    actions: bool = Field(
        title="Actions (Plugin reload required)",
        description="Enable chat interactions to be able to change voices, know current voice or available ones.",
        default=True
    )


@plugin
def settings_model():
    return VoiceEngineSettings
