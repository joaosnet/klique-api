import asyncio
import sys


async def test_generation():
    sys.path.append('/app')
    from gemini_webapi import GeminiClient  # noqa: PLC0415

    from app.config import SECURE_1PSID, SECURE_1PSIDTS  # noqa: PLC0415

    print('Init client')

    gemini_client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS)
    await gemini_client.init(timeout=30)
    print('Client initialized. Generating image...')

    try:
        response = await gemini_client.generate_custom_images('A cute cat')
        print('Response received')
        print(type(response))
        images = getattr(response, 'images', None)
        print('Images:', type(images), len(images) if images else 0)
        if images:
            print('Image 0 type:', type(images[0]))
            if isinstance(images[0], dict):
                print('Image 0 keys:', images[0].keys())
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    asyncio.run(test_generation())
