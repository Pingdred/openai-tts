from enum import Enum

from pydantic import BaseModel, Field, SecretStr

from cat.mad_hatter.decorators import plugin


class VoiceQuality(Enum):
    """OpenAI TTS supported qualities."""
    STANDARD = "tts-1"
    HD = "tts-1-hd"


class Voice(Enum):
    """OpenAI TTS supported voices."""
    ALLOY = "Alloy"
    ASH = "Ash"
    CORAL = "Coral"
    ECHO = "Echo"
    FABLE = "Fable"
    ONYX = "Onyx"
    NOVA = "Nova"
    SAGE = "Sage"
    SHIMMER = "Shimmer"


class SupportedAudioFormat(Enum):
    """OpenAI TTS supported audio formats."""
    MP3 =  "mp3"
    OPUS = "opus"
    AAC = "aac"
    FLAC = "flac"
    WAV = "wav"
    PCM = "pcm"


class ResponseType(Enum):
    """OpenAI TTS supported response types."""
    HTML = "HTML content"
    KEY = "TTS key"


class VoiceEngineSettings(BaseModel):
    openai_api_key: SecretStr = Field(
        title="OpenAI API Key"
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
    )
    actions: bool = Field(
        title="Actions (Plugin reload required)",
        description="Enable chat interactions to be able to change voices, know current voice or available ones.",
        default=True
    )


@plugin
def settings_model():
    return VoiceEngineSettings
