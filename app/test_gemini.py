import asyncio
import os
import sys


async def test_generation():
    sys.path.append('/app')
    from gemini_webapi import GeminiClient  # noqa: PLC0415

    from app.config import SECURE_1PSID, SECURE_1PSIDTS  # noqa: PLC0415

    gemini_client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS)
    await gemini_client.init(
        timeout=30,
        auto_close=True,
        close_delay=15,
        auto_refresh=True,
    )
    print('Client initialized. Generating image...')

    try:
        response = await gemini_client.generate_content(
            'Generate an original image of a dog. Do not send web images.'
        )
        images = getattr(response, 'images', None)

        if images:
            img = images[0]
            output_dir = os.path.join('generated_media', 'test_outputs')
            os.makedirs(output_dir, exist_ok=True)
            save_kwargs = {
                'path': output_dir,
                'filename': 'app-test-dog.png',
            }
            if hasattr(img, 'cookies'):
                save_kwargs['full_size'] = True
            saved_path = await img.save(**save_kwargs)
            print('Saved image:', saved_path)
    finally:
        await gemini_client.close()


if __name__ == '__main__':
    asyncio.run(test_generation())
