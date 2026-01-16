import asyncio
import aiohttp

URL = "http://localhost:8000/"
REQUESTS = 50
CONCURRENCY = 20

async def fetch(session):
    try:
        async with session.get(URL):
            pass  # 🔇 silent on success
    except Exception as e:
        print(f"[ERROR] {e}")  # 🔔 only errors

async def main():
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch(session) for _ in range(REQUESTS)]
        await asyncio.gather(*tasks)

asyncio.run(main())
