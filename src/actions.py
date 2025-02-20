import random
from pydantic import BaseModel, Field

from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators import tool
from cat.experimental.form import form, CatForm
from .settings import Voice

from .settings import Voice, VoiceSpeed
from .utils import load_user_settings, save_user_settings


def is_action_enabled() -> bool:
    plugin_path = Path(__file__).parent.parent

    with open(plugin_path / "settings.json") as f:
        settings = json.load(f)

    return settings["actions"]


def pick_random_voice() -> Voice:
    setting = MadHatter().get_plugin().load_settings()
    current_voice = setting["voice"]
    voices = [voice for voice in Voice if voice != current_voice]
    
    return random.choice(voices)

    def pick_random_voice() -> Voice:
        setting = MadHatter().get_plugin().load_settings()
        current_voice = setting["voice"]
        
        voices = [voice for voice in Voice if voice != current_voice]
        
        return random.choice(voices)


    class ChangeVoiceModel(BaseModel):
        voice: Voice = Field(
            description=f"The voice to set, should be be one of {[e.value for e in Voice]}.", 
            default_factory=pick_random_voice
        )

class ChangeVoiceModel(BaseModel):
    voice: Voice = Field(
        description=f"The voice to set, should be be one of {[e.value for e in Voice]}.", 
        default_factory=pick_random_voice
    )


# Only define the actions if they are enabled in the settings
if is_action_enabled():

    @form
    class ChangeVoice(CatForm):
        model_class = ChangeVoiceModel
        description = "Use this action to change your voice."
        
        start_examples =  [
            "I do not like your voice",
            "Change your voice",
            "Use the voice Echo",
            "Speak to me in the voice of Nova"
        ]

        def submit(self, form_data) -> str:

            # Load current settings
            settings = self.cat.mad_hatter.get_plugin().load_settings()
            # Update voice
            settings["voice"] = form_data["voice"]
            # Save new settings
            self.cat.mad_hatter.get_plugin().save_settings(settings)
        
            return {
                "output": f"Voice changed to {form_data['voice']}."
            }
        
    @tool(examples=[
    @tool(
        examples=[
            "What's your current voice?",
            "What voice are you using?",
            "Which voices can you use?"
        ]
    )
    def current_voice(_, cat: StrayCat):
        """User this action to know what voice you are currently using. """
        # Load current settings
        settings = cat.mad_hatter.get_plugin().load_settings()

        return f"The current voice is {settings['voice']}."

    @tool(
        examples=[
            "Which voices can you use?"
        ]
    )
    def available_voice(_, cat: StrayCat):
            """Lets you know what voices are available to you."""
            return "The available voices are : " + ", ".join([v.value for v in Voice])
