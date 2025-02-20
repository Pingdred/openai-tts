import json
import random
from pathlib import Path

from pydantic import BaseModel, Field

from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators import tool
from cat.looking_glass.stray_cat import StrayCat
from cat.experimental.form import form, CatForm

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


def get_next_speed(current_speed: VoiceSpeed, increase: True) -> VoiceSpeed | None:
    speeds_list = [v for v in VoiceSpeed]
    current_speed_index = speeds_list.index(current_speed)

    if increase and current_speed_index == len(speeds_list) - 1:
        return None
    
    if not increase and current_speed_index == 0:
        return None
    
    step = 1 if increase else -1

    return speeds_list[current_speed_index + step]


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
            settings = load_user_settings(self.cat.user_id)
            # Update voice
            settings.voice = form_data["voice"]
            # Save new settings
            save_user_settings(self.cat.user_id, settings)
        
            return {
                "output": f"Voice changed to {form_data['voice']}."
            }
        

    @tool(
        examples=[
            "You are speaking too slow",
            "Can you speak faster?",
        ]
    )  
    def speak_faster(_, cat: StrayCat):
        """Use this action to make your voice speak faster. Use only if the user has explicitly asked to change the voice speed."""
        user_settings = load_user_settings(cat.user_id)

        if (new_speed := get_next_speed(user_settings.speed, increase=True)) is None:
            return "You are already speaking as fast as you can."
        
        user_settings.speed = new_speed
        save_user_settings(cat.user_id, user_settings)

        if new_speed == VoiceSpeed.FAST:
            return "You are speaking as fast as you can now."

        return "You are now speaking faster."

    
    @tool(
        examples=[
            "You are speaking too fast", 
            "Can you speak slower?"
       ]
    )
    def speak_slower(_, cat: StrayCat):
        """Use this action to make the voice speak slower. Use only if the user have explicitly asked to change the voice speed."""
        settings = load_user_settings(cat.user_id)

        if (new_speed := get_next_speed(settings.speed, increase=False)) is None:
            return "You are already speaking as slow as you can."
        
        settings.speed = new_speed
        save_user_settings(cat.user_id, settings)       
        
        if new_speed == VoiceSpeed.SLOW:
            return "You are speaking as slow as you can now."
        
        return "You are now speaking slower now."


    @tool
    def current_voice_speed(_, cat: StrayCat):
        """Use this action to know what speed you are currently using. """
        # Load current settings
        settings = load_user_settings(cat.user_id)

        return f"The current voice speed is: {settings.speed}."


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
        settings = load_user_settings(cat.user_id)

        return f"The current voice is {settings.voice}."


    @tool(
        examples=[
            "Which voices can you use?"
        ]
    )
    def available_voice(_, cat: StrayCat):
            """Lets you know what voices are available to you."""
            return "The available voices are : " + ", ".join([v.value for v in Voice])
