from pyrogram import Client
from pytgcalls import PyTgCalls
from os import remove as rm
from os import listdir
from sira import is_empty, get, task_done
import config


client = Client(config.SESSION_NAME, config.API_ID, config.API_HASH)
pytgcalls = PyTgCalls(client, 1512, False)
playing = []
paused = []


def get_file(chat_id: str, num: int):
    return f"{str(chat_id).replace('-', '')}_{num}.raw"


@pytgcalls.on_event_update()
def _(update: dict) -> None:
    if update["result"] == "JOINED_VOICE_CHAT":
        if update["chat_id"] not in playing:
            playing.append(update["chat_id"])


@pytgcalls.on_stream_end()
def on_stream_end(chat_id: int) -> None:
    task_done(chat_id)

    if chat_id in playing:
        playing.remove(chat_id)

    if is_empty(chat_id):
        deled = 0
        pytgcalls.leave_group_call(chat_id)
        try:
            rm(f"raw_files/{str(chat_id).replace('-', '')}_1.raw")
        except:
            pass
        for x in range(80):
            if get_file(chat_id, deled) in listdir("raw_files"):
                rm(f"raw_files/{get_file(chat_id, deled)}")
                deled += 1
    else:
        pytgcalls.change_stream(chat_id, get(chat_id)["file_path"])


def run():
    pytgcalls.run()
