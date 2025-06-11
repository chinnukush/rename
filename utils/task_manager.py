# codes add by @Harikushal

async def handle_request(file):
    return await process_file(file)

tasks = [handle_request(f) for f in files]
results = await asyncio.gather(*tasks)
