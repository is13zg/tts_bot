import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram import F
import asyncio
from text_processing import extract_text_from_file, extract_text_from_url, split_text
from salitspeech import synthesize_speech
from googleTTS import g_synthesize_speech
from config import TELEGRAM_BOT_TOKEN, Salut_speech_keys
import random
import functools

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

const_key_num = random.randint(0, len(Salut_speech_keys) - 1)


def error_handler(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as err:
            # Поиск объекта message среди аргументов.
            message = kwargs.get('message')
            if not message and args:
                message = args[0]
            if message:
                await message.answer(f"Произошла ошибка: {err}")
            else:
                # Если объект message не найден, можно залогировать ошибку
                print(f"Произошла ошибка: {err}")

    return wrapper


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Отправьте мне текст, ссылку или файл для озвучки.")


@dp.message(F.text | F.photo | F.video | F.animation | F.document)
@error_handler
async def handle_text(message: types.Message):
    global const_key_num
    if message.content_type in [types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.ANIMATION]:
        text = message.caption
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        local_path = os.path.join("downloads", message.document.file_name)
        os.makedirs("downloads", exist_ok=True)
        await bot.download(file_path, destination=local_path)
        text = extract_text_from_file(local_path)

    else:
        text = message.text

    if text.startswith("http"):
        text = extract_text_from_url(text)

    if len(text) < 150 and "==" not in text:
        await message.answer(text="too short..")
        return

    const_key_num = (const_key_num + 1) % len(Salut_speech_keys)
    text_parts = split_text(text)
    for text_part in text_parts:

        try:
            audio_file = synthesize_speech(text_part, key_number=const_key_num)
        except Exception as e:
            await message.answer(text=f"salut speech error: {e}...")
            audio_file = g_synthesize_speech(text_part)

        await message.answer_voice(voice=FSInputFile(audio_file))
        await asyncio.sleep(3)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
