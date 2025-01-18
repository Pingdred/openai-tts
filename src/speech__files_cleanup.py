import asyncio
import os
import shutil
import time

from cat.mad_hatter.decorators import hook, plugin
from cat.log import log

from .utils import get_speech_file_path

cleanup_task = None

def file_is_expired(file_path: str) -> bool:
    min_lifetime = 5*60  # Minimum lifetime in seconds (5 minutes)
    creation_time = os.path.getctime(file_path)
    elapsed_time = time.time() - creation_time
    return elapsed_time > min_lifetime


def is_empty_directory(dir_path: str) -> bool:
    return not any(True for _ in os.scandir(dir_path))


def cleanup_expired_files():
    for root, _, files in os.walk(get_speech_file_path()):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # Check if the file is expired and should be deleted
            if file_is_expired(file_path):
                os.remove(file_path)
                log.debug(f"OpenAI TTS: Speech File deleted {file_path}")


def cleanup_directories(only_empty: bool = True):
    for root, dirs, _ in os.walk(get_speech_file_path()):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if is_empty_directory(dir_path) or not only_empty:
                shutil.rmtree(dir_path)
                log.debug(f"OpenAI TTS: Directory deleted {dir_path} ")


async def cleanup_temporary_files():
    loop = asyncio.get_running_loop()
    # Cleanup every 10 minutes
    while True:     
        log.debug("OpenAI TTS: cleanup started")

        # Cleanup expired files and empty directories in a separate thread
        await loop.run_in_executor(None, cleanup_expired_files)
        await loop.run_in_executor(None, cleanup_directories)
        await asyncio.sleep(10*60)  

        log.debug("OpenAI TTS: cleanup completed")


def schedule_cleanup():
    global cleanup_task
    if cleanup_task is None or cleanup_task.done():
        cleanup_task = asyncio.create_task(cleanup_temporary_files())


def cancel_cleanup():
    global cleanup_task
    if cleanup_task and not cleanup_task.done():
        cleanup_task.cancel()
        cleanup_task = None


@hook
def after_cat_bootstrap(cat):
    log.debug("OpenAI TTS: Start speech files cleanup task")
    schedule_cleanup()


@plugin
def activated(plugin):
    log.debug("OpenAI TTS: Start speech files cleanup task")
    schedule_cleanup()


@plugin
def deactivated(plugin):
    cleanup_directories(only_empty=False)
    log.debug("OpenAI TTS: Stopping speech files cleanup task")
    cancel_cleanup()

