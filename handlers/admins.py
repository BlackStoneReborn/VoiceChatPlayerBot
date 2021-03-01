from pyrogram import Client, filters
from pyrogram.types import Message
import tgcalls
import sira
from cache.admins import set
from os import remove as rm
from os import listdir
from helpers.wrappers import errors, admins_only


def get_file(chat_id: str, num: int):
    return f"{str(chat_id).replace('-', '')}_{num}.raw"


@Client.on_message(
    filters.command(["pause", "pause@VoiceChatPlayerBot"])
    & filters.group
    & ~filters.edited
)
@errors
@admins_only
async def pause(client: Client, message: Message):
    if message.chat.id in tgcalls.playing and message.chat.id not in tgcalls.paused:
        tgcalls.pytgcalls.pause_stream(message.chat.id)
        tgcalls.paused.append(message.chat.id)
        await message.reply_text("Paused! ⏸ Use /resume to resume.")
    elif message.chat.id in tgcalls.paused:
        await message.reply_text("Already paused! Use /resume to resume.")
    elif message.chat.id not in tgcalls.playing:
        await message.reply_text("There's nothing playing to pause!")


@Client.on_message(
    filters.command(["resume", "resume@VoiceChatPlayerBot"])
    & filters.group
    & ~filters.edited
)
@errors
@admins_only
async def resume(client: Client, message: Message):
    if message.chat.id in tgcalls.paused:
        tgcalls.pytgcalls.resume_stream(message.chat.id)
        tgcalls.paused.remove(message.chat.id)
        await message.reply_text("Resumed! ▶")
    else:
        await message.reply_text("There's nothing paused to resume!")


@Client.on_message(
    filters.command(["leave", "leave@VoiceChatPlayerBot"])
    & filters.group
    & ~filters.edited
)
@errors
@admins_only
async def stop(client: Client, message: Message):
    if message.chat.id in tgcalls.playing:
        tgcalls.playing.remove(message.chat.id)
        await message.reply_text("Left! ↩️")

    try:
        sira.clear(message.chat.id)
    except:
        pass

    tgcalls.pytgcalls.leave_group_call(message.chat.id)


@Client.on_message(
    filters.command(["skip", "next", "skip@VoiceChatPlayerBot"])
    & filters.group
    & ~filters.edited
)
@errors
@admins_only
async def skip(client: Client, message: Message):
    sira.task_done(message.chat.id)

    if message.chat.id not in tgcalls.playing:
        await message.reply_text("There's nothing playing to skip!")
        return

    if sira.is_empty(message.chat.id):
        deled = 0
        tgcalls.pytgcalls.leave_group_call(message.chat.id)
        tgcalls.playing.remove(message.chat.id)
        try:
            rm(f"raw_files/{str(message.chat.id).replace('-', '')}_1.raw")
        except:
            pass
        for x in range(80):
            if get_file(message.chat.id, deled) in listdir("raw_files"):
                rm(f"raw_files/{get_file(message.chat.id, deled)}")
                deled += 1
        await message.reply_text("Skipped ⏭, nothing is playing now.")
    else:
        if sira.get(message.chat.id)["file_path"]:
            tgcalls.pytgcalls.change_stream(
                message.chat.id, sira.get(message.chat.id)["file_path"]
            )
            await message.reply_text("Skipped to the next song ⏭")
        else:
            deled = 0
            tgcalls.pytgcalls.leave_group_call(message.chat.id)
            tgcalls.playing.remove(message.chat.id)
            try:
                rm(f"raw_files/{str(message.chat.id).replace('-', '')}_1.raw")
            except:
                pass
            for x in range(80):
                if get_file(message.chat.id, deled) in listdir("raw_files"):
                    rm(f"raw_files/{get_file(message.chat.id, deled)}")
                    deled += 1
            await message.reply_text("Skipped ⏭, nothing is playing now.")


@Client.on_message(filters.command("admincache"))
@errors
@admins_only
async def admincache(client, message: Message):
    set(
        message.chat.id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("Admin-cache refreshed ❇️")
