from os import path, remove
import asyncio
from sira import qusize


class FFmpegReturnCodeError(Exception):
    pass


async def convert(file_path: str, cid: int) -> str:
    sizey = await qusize(f"-{cid}")
    sizey += 1
    out = f"{cid}_{sizey}.raw"

    proc = await asyncio.create_subprocess_shell(
        f"ffmpeg -y -i {file_path} -f s16le -ac 1 -ar 48000 -acodec pcm_s16le raw_files/{out}",
        asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    remove(file_path)

    if proc.returncode != 0:
        raise FFmpegReturnCodeError("FFmpeg did not return 0")

    return f"raw_files/{out}"
