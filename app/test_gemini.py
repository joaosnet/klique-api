import asyncio
import sys

import httpx


async def test_generation():
    sys.path.append('/app')
    from gemini_webapi import GeminiClient  # noqa: PLC0415

    from app.config import SECURE_1PSID, SECURE_1PSIDTS  # noqa: PLC0415

    gemini_client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS)
    await gemini_client.init(timeout=30)
    print('Client initialized. Generating image...')

    response = await gemini_client.generate_content(
        'Generate a picture of a dog'
    )
    images = getattr(response, 'images', None)

    if images:
        img = images[0]
        url = img.url
        print('Image url:', url)

        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            print('Download status:', res.status_code)
            print('Downloaded bytes len:', len(res.content))


if __name__ == '__main__':
    asyncio.run(test_generation())
