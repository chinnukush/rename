# codes add by @Harikushal
import asyncio

async def handle_request(file):
    return await process_file(file)

async def run_tasks(files):
    tasks = [handle_request(f) for f in files]
    return await asyncio.gather(*tasks)
