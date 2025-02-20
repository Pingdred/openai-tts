from enum import Enum

from pydantic import BaseModel, Field, SecretStr

from cat.mad_hatter.decorators import plugin


class VoiceQuality(Enum):
    """OpenAI TTS supported qualities."""
    STANDARD = "Standard"
    HD = "HD"

    @property
    def model_name(self) -> str:
        models = {
            "Standard": "tts-1",
            "HD": "tts-1-hd"
        }
        return models[self.value]


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


class WhenToSpeak(Enum):
    ALWAYS = "Always"
    #UNLESS_ASKED_NOT_TO = "Unless asked not to"
    WHEN_ASKED = "When asked"
    LONG_TEXT = "Long messages"
    SHORT_TEXT = "Short messages"
    

class VoiceSpeed(Enum):
    """OpenAI TTS supported speeds."""
    SLOW = "Slow"
    NORMAL = "Normal"
    FAST = "Fast"

    @property
    def speed_value(self) -> float:
        speed_values = {
            "Slow": 0.75,
            "Normal": 1.0,
            "Fast": 1.25,
        }
        return speed_values[self.value]


class ResponceType(Enum):
    HTML = "HTML content"
    AUDIO_KEY = "WS audio key"
    BOTH = "Both"

        
class GlobalSettings(BaseModel):
    openai_api_key: SecretStr = Field(
        title="OpenAI API Key"
    )
    responce_type: ResponceType = Field(
        title="Responce type",
        description="How you want to recive the speech file, as ws key, html content or both.",
        default=ResponceType.BOTH
    )
    when_to_speak: WhenToSpeak = Field(
        title="When to speak",
        description="Determines speech generation trigger: always, on request, or based on message length.",
        default=WhenToSpeak.ALWAYS
    )
    voice: Voice = Field(
        title="Voice", 
        default=Voice.ALLOY
    )
    quality: VoiceQuality = Field(
        title="Quality", 
        default=VoiceQuality.STANDARD
    )
    speed: VoiceSpeed = Field(
        title="Speed",
        default=VoiceSpeed.NORMAL
    )
    output_format: SupportedAudioFormat = Field(
        title="Speech format",
        default=SupportedAudioFormat.MP3
    )
    message_length: int = Field(
        title="Message length",
        description="Minimum character count to trigger speech for long or short messages.",
        default=300
    )
    optimize_text: bool = Field(
        title="Optimize text",
        description="Guide the LLM to generate text more suitable for speech.",
        default=True
    )    
    actions: bool = Field(
        title="Actions (Plugin reload required)",
        description="Enable chat interactions to be able to change voices, know current voice or available ones.",
        default=True
    )


class UserSettings(BaseModel):
    voice: Voice = Field(
        title="Voice", 
        default=Voice.ALLOY
    )
    speed: VoiceSpeed = Field(
        title="Speed",
        default=VoiceSpeed.NORMAL
    )
    

@plugin
def settings_model():
    return GlobalSettings
