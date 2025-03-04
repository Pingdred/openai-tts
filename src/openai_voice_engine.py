import sys
import json

from pathlib import Path
from typing import List

from openai import OpenAI

from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts.chat import SystemMessagePromptTemplate

from cat.log import log
from cat.mad_hatter.decorators import hook
from cat.looking_glass.stray_cat import StrayCat
from cat.convo.messages import CatMessage, UserMessage
from cat.utils import langchain_log_output, langchain_log_prompt

from .settings import GlobalSettings, WhenToSpeak, ResponceType
from .utils import (
    generate_file_name,
    get_speech_file_path,
    get_speech_file_url,
    load_user_settings,
    create_html_message,
)


# SECTION: Determine if speech is needed


def asked_to_speak(message: UserMessage, cat: StrayCat) -> bool:
    """
        Chain to determine if the user explicitly asked to respond with speech, audio, voice or asked to read.
    """

    prompt_text = """Your objective is to determine if the user explicitly asked to respond with speech, audio, voice or asked to read.
Respond with the following format, setting the value to true if the user explicitly asked to respond with speech false otherwise:
{{
    "speech_requested": true
}}
"""

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(template=prompt_text),
            *[m.langchainfy() for m in cat.working_memory.history[-3:]], # Add last 3 messagess
        ]
    )

    chain = (prompt 
        | RunnableLambda(lambda x: langchain_log_prompt(x, "Ask to speak prompt"))
        | cat._llm 
        | RunnableLambda(lambda x: langchain_log_output(x, "Ask to speak output"))
        # Sometimes some LLMs write True or False instead of true or false
        | RunnableLambda(lambda x: setattr(x, "content", x.content.lower()) or x)
        | JsonOutputParser()
    )

    try:
        output = chain.invoke({"user_message": message.text})
    except json.JSONDecodeError:
        log.error("Unparsable output, setting speech_requested to False")
        return False
    except Exception as e:
        log.error(f"Error while processing output, setting speech_requested to False: {e}")
        return False
        
    return output["speech_requested"]


def speech_needed(message: CatMessage, cat: StrayCat) -> bool:
    settings = GlobalSettings(**(cat.mad_hatter.get_plugin().load_settings()))

    match settings.when_to_speak:
        case WhenToSpeak.ALWAYS:
            return True
        case WhenToSpeak.LONG_TEXT:
            return len(message.text) >= settings.message_length
        case WhenToSpeak.SHORT_TEXT:
            return len(message.text) <= settings.message_length
        case WhenToSpeak.WHEN_ASKED:
            user_message = cat.working_memory.user_message_json
            return asked_to_speak(user_message, cat)
        case _:
            return False


@hook(priority=-sys.maxsize)
def agent_prompt_prefix(prefix: str, cat: StrayCat) -> str:
    """
        Modify the agent prompt prefix to inform the LLM that speech capability is enabled.
    """
    prefix += "\n\n# Speech Capability: \n - You have the ability to speak.\n"
    return prefix


# SECTION: Process final massege


def generate_audio_file(text: str, user_id: str, settings: GlobalSettings) -> Path:
    # Generate speech file name
    file_name = generate_file_name(settings.output_format.value)
    # Get path to speech file
    speech_files_path = get_speech_file_path(user_id)

    # Create directory to store speech files 
    speech_files_path.mkdir(parents=True, exist_ok=True)

    # Create OpenAi Client
    client = OpenAI(api_key=settings.openai_api_key.get_secret_value())

    # Load user settings
    user_settings = load_user_settings(user_id)

    # Max supported length is 4096 characters, 
    # mostly there is no need to split the text

    # Create Speech
    response = client.audio.speech.create(
        response_format=settings.output_format.value,
        model=settings.quality.model_name,
        voice=user_settings.voice.value.lower(),
        speed=user_settings.speed.speed_value,
        input=text
    )
    response.write_to_file(speech_files_path / file_name)

    return file_name


def split_at_code_blocks(text: str) -> list[str]:
    """
        Split the text at code blocks and return a list of text blocks.
    """
    blocks = []
    # Split the text at code blocks
    for idx, block in enumerate(text.split("```")):
        if idx % 2 == 0:
            blocks.append({
                "block": block,
                "type": "text"
            })
        else:
            blocks.append({
                "block": f"```{block}```",
                "type": "code"
            })
            
    return blocks


def create_audio_message(cat: StrayCat, text: str, original_message: CatMessage, settings: GlobalSettings) -> str:
    # Generate speech
    speech_path = generate_audio_file(text, cat.user_id, settings)
    # Create speech file url
    speech_url = get_speech_file_url(user_id=cat.user_id) + speech_path

    new_message = original_message.model_copy()
    if settings.show_caption:
        new_message.text = text

    if settings.responce_type == ResponceType.HTML:
        html_message = original_message.model_copy()
        html_message.text = create_html_message(
            audio_source=speech_url
        )
        # Send the HTML audio element in a separate message
        # withouth saving it in the chat history
        cat.send_chat_message(html_message)
        
        return new_message

    new_message.audio = speech_url
    return new_message


def process_block(cat: StrayCat, block: dict, original_message: CatMessage, settings: GlobalSettings) -> CatMessage:
    if block["type"] == "text":
       return create_audio_message(
            cat=cat,
            text=block["block"],
            original_message=original_message,
            settings=settings
        )
        
    code_message = original_message.model_copy(update={"text": block["block"]})
    return code_message


@hook(priority=-sys.maxsize)
def before_cat_sends_message(message: CatMessage, cat: StrayCat):
    # If the speech is not needed, skip the process
    if not speech_needed(message, cat):
        return message

    # Load settings
    settings = GlobalSettings(**(cat.mad_hatter.get_plugin().load_settings()))

    # Split the message at code blocks
    # to process them separately
    blocks = split_at_code_blocks(message.text)
    last_block = blocks.pop()
    
    # Process each block sending the code blocks as messages
    # and the text blocks as audio messages
    for block in blocks:
        new_message = process_block(cat, block, message, settings)
        cat.send_chat_message(new_message, save=True)
           
    # Process the last block and return the message
    # to let finish the Chehsire Cat response pipeline
    if last_block["type"] == "code":
        message.text = last_block["block"]
        return message
    
    return create_audio_message(
        cat=cat,
        text=last_block["block"],
        original_message=message,
        settings=settings
    )

