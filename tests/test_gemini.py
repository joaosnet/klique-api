import asyncio
import os
import sys

import pytest


async def test_generation():
    sys.path.append('/app')
    from gemini_webapi import GeminiClient  # noqa: PLC0415

    from app.config import SECURE_1PSID, SECURE_1PSIDTS  # noqa: PLC0415

    if not SECURE_1PSID:
        pytest.skip('SECURE_1PSID não configurado para teste de integração')

    print('Init client')

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
            'Generate an original image of a cute cat. '
            'Do not send web images.'
        )
        print('Response received')
        print(type(response))
        images = getattr(response, 'images', None)
        print('Images:', type(images), len(images) if images else 0)
        if images:
            print('Image 0 type:', type(images[0]))
            output_dir = os.path.join('generated_media', 'test_outputs')
            os.makedirs(output_dir, exist_ok=True)
            save_kwargs = {
                'path': output_dir,
                'filename': 'gemini-test-cat.png',
            }
            if hasattr(images[0], 'cookies'):
                save_kwargs['full_size'] = True
            saved_path = await images[0].save(**save_kwargs)
            print('Saved path:', saved_path)
    except Exception as e:
        print('Error:', e)
        raise
    finally:
        await gemini_client.close()


if __name__ == '__main__':
    asyncio.run(test_generation())
