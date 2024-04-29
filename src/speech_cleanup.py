import asyncio
import os
import shutil
import time

from cat.mad_hatter.decorators import hook, plugin
from cat.log import log

from .utils import (
    get_speech_file_path,
)

openai_voice_engine_cleanup_task = None

async def cleanup_expired_files():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _cleanup_expired_files)


def _cleanup_expired_files():
    for root, _, files in os.walk(get_speech_file_path()):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_is_expired(file_path):
                os.remove(file_path)
            log.debug(f"Speech File deleted: {file_path}")


async def cleanup_empty_directories():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _cleanup_empty_directories)


def _cleanup_empty_directories():
    for root, dirs, _ in os.walk(get_speech_file_path()):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if is_empty_directory(dir_path):
                shutil.rmtree(dir_path)
                log.debug(f"Empty directory deleted: {dir_path} ")


def is_empty_directory(dir_path: str) -> bool:
    return not any(True for _ in os.scandir(dir_path))


def file_is_expired(file_path: str) -> bool:
    min_lifetime = 5*60
    creation_time = os.path.getctime(file_path)
    elapsed_time = time.time() - creation_time
    return elapsed_time > min_lifetime


async def cleanup_temporary_files():
    while True:
        await asyncio.sleep(10*60)
        log.debug("OpenAi Voice Engine: strat cleanup")
        await cleanup_expired_files()
        await cleanup_empty_directories()


def schedule_cleanup():
    global openai_voice_engine_cleanup_task
    if openai_voice_engine_cleanup_task is None or openai_voice_engine_cleanup_task.done():
        openai_voice_engine_cleanup_task = asyncio.ensure_future(cleanup_temporary_files())

def cancel_cleanup():
    global openai_voice_engine_cleanup_task
    if openai_voice_engine_cleanup_task and not openai_voice_engine_cleanup_task.done():
        openai_voice_engine_cleanup_task = None


@hook
def after_cat_bootstrap(cat):
    # Start Cleanup corutine
    log.debug("OpenAi Voice Engine: Start speach files cleanup task")
    schedule_cleanup()


@plugin
def activated(plugin):
    log.debug("OpenAi Voice Engine: Start speach files cleanup task")
    schedule_cleanup()


@plugin
def deactivated(plugin):
    log.debug("OpenAi Voice Engine: Stopping speach files cleanup task")
    openai_voice_engine_cleanup_task.cancel()

