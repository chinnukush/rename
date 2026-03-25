import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


# ================== FIX THUMB ================== #
async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb:
            parser = createParser(thumb)
            metadata = extractMetadata(parser)

            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")

            with Image.open(thumb) as img:
                img = img.convert("RGB")
                img = img.resize((width, height))
                img.save(thumb, "JPEG")

            parser.close()

    except Exception as e:
        print(e)
        thumb = None

    return width, height, thumb


# ================== SCREENSHOT ================== #
async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"

    command = [
        "ffmpeg",
        "-ss", str(ttl),
        "-i", video_file,
        "-vframes", "1",
        out_put_file_name
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    await process.communicate()

    if os.path.exists(out_put_file_name):
        return out_put_file_name

    return None


# ================== METADATA ================== #
async def add_metadata(input_path, output_path, metadata, ms, enable_metadata=True):
    try:
        if enable_metadata:
            await ms.edit("<i>⚡ Adding Your Metadata...</i>")

            command = [
                'ffmpeg', '-y',
                '-i', input_path,

                # keep all streams
                '-map', '0',

                # no re-encode (fast)
                '-c', 'copy',

                # remove old metadata first
                '-map_metadata', '-1',

                # ✅ add only clean metadata
                '-metadata', f'title={metadata}',

                # optional clean flags
                '-movflags', 'use_metadata_tags',

                output_path
            ]

        else:
            await ms.edit("<i>⚡ Removing Metadata...</i>")

            command = [
                'ffmpeg', '-y',
                '-i', input_path,

                '-map', '0',
                '-c', 'copy',

                # ❌ remove everything
                '-map_metadata', '-1',
                '-map_chapters', '-1',

                output_path
            ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        print(stderr.decode())  # debug logs

        if os.path.exists(output_path):
            await ms.edit("<i>✅ Process Completed Successfully</i>")
            return output_path
        else:
            await ms.edit("<i>❌ Failed To Process File</i>")
            return None

    except Exception as e:
        print(f"Error: {e}")
        await ms.edit("<i>❌ Error While Processing File</i>")
        return None
