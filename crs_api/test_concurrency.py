import asyncio
import aiohttp
import time

async def send_request(session, i):
    payload = {
        "conversation_history": [
            {"role": "user", "content": f"Recommend a movie {i}"}
        ]
    }
    start = time.time()
    async with session.post("http://localhost:8000/api/v1/recommend", json=payload) as resp:
        await resp.json()
        elapsed = time.time() - start
        print(f"Request {i} completed in {elapsed:.2f}s")
    return elapsed

async def test_concurrent():
    async with aiohttp.ClientSession() as session:
        # Send 5 requests simultaneously
        tasks = [send_request(session, i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        print(f"\nAll 5 requests completed! Avg time: {sum(results)/len(results):.2f}s")

asyncio.run(test_concurrent())