import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram import F
import asyncio
from text_processing import extract_text_from_file, extract_text_from_url, split_text
from salitspeech import synthesize_speech
from config import TELEGRAM_BOT_TOKEN, Salut_speech_keys
import random

bot = Bot(token=TELEGRAM_BOT_TOKEN)

dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Отправьте мне текст, ссылку или файл для озвучки.")


@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text.startswith("http"):
        text = extract_text_from_url(message.text)
    else:
        text = message.text

    if len(text) < 150 and "==" not in text:
        await message.answer(text="Слишком коротко")

    key_num = random.randint(0, len(Salut_speech_keys) - 1)
    text_parts = split_text(text)
    for text_part in text_parts:
        audio_file = synthesize_speech(text_part, key_number=key_num)
        await message.answer_voice(voice=FSInputFile(audio_file))


@dp.message(F.document)
async def handle_document(message: types.Message, bot: Bot):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    local_path = os.path.join("downloads", message.document.file_name)
    os.makedirs("downloads", exist_ok=True)
    await bot.download(file_path, destination=local_path)
    text = extract_text_from_file(local_path)
    audio_file = synthesize_speech(text)
    await message.answer_voice(voice=FSInputFile(audio_file))
    os.remove(local_path)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
