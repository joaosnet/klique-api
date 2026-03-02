import asyncio
import sys

import httpx


async def test_generation():
    sys.path.append('/app')
    from gemini_webapi import GeminiClient

    from app.config import SECURE_1PSID, SECURE_1PSIDTS

    gemini_client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS)
    await gemini_client.init(timeout=30)
    print('Client initialized. Generating image...')

    response = await gemini_client.generate_content(
        'Generate a picture of a house'
    )
    images = getattr(response, 'images', None)

    if images:
        img = images[0]
        url = img.url
        print('Image url:', url)

        # Pass cookies from GeminiClient
        cookies = getattr(gemini_client, 'cookies', {})
        if not cookies:
            print('No cookies found on gemini_client.cookies')
            cookies = {
                '__Secure-1PSID': SECURE_1PSID,
                '__Secure-1PSIDTS': SECURE_1PSIDTS,
            }
        else:
            print('Found cookies dict:', type(cookies))

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            async with httpx.AsyncClient(
                follow_redirects=True, headers=headers, cookies=cookies
            ) as client:
                res = await client.get(url)
                print('Cookie Download status:', res.status_code)
                print('Downloaded bytes len:', len(res.content))
        except Exception as e:
            print('Cookie download failed:', e)


if __name__ == '__main__':
    asyncio.run(test_generation())
