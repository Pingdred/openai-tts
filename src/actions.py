import random
from pydantic import BaseModel, Field

from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators import tool
from cat.experimental.form import form, CatForm
from .settings import Voice

if MadHatter().get_plugin().load_settings().get("actions", True):

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
            "What's your current voice?",
            "What voice are you using?",
            "Which voices can you use?"
        ]
    )
    def current_voice(input, cat):
        """Lets you know what voice you are using."""
        # Load current settings
        settings = cat.mad_hatter.get_plugin().load_settings()

        return f"The current voice is {settings['voice']}."

    @tool(examples=[
            "Which voices can you use?"
        ]
    )
    def available_voice(input, cat):
        """Lets you know what voices are available to you."""
        return "The available voices are : " + ", ".join([v.value for v in Voice])