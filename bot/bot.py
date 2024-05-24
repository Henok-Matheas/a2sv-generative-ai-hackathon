from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message
)
from aiogram.fsm.context import FSMContext
from config import initial_config as config
from utils.logger import logging
from chatbot.chat import ask

# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

welcome_message = """
🚀 Welcome to the <b>2024 A2SV AI for Africa Hackathon Helper Bot!</b>

We're thrilled to have you here! 🌍✨

<b>What can you do?</b>

<b>🔍 Explore A2SV:</b>
Learn more about A2SV, its mission, and find important links. Discover how we're empowering African tech talent and fostering innovation.

<b>🔍 Explore the 2024 AI for Africa Hackathon:</b>
Learn more about the hackathon, its goals, and how you can participate. Find important links and resources to help you get started.
"""

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    print("here")
    await message.answer(welcome_message)

@dp.message()
async def chat_handler(message: Message) -> None:
    """
    This handler will handle all non start messages
    """
    chat_id, query = message.chat.id, message.text

    if not query:
        await message.reply("I can only process text messages! 📝")
        return
    sticker = await message.answer_sticker(sticker=config.LOADING_STICKER)
    response = await message.reply("Give me some moments please ⏳...")
    
    try:
        output = ask(chat_id, query)
        await response.edit_text(output)

    except:
        await response.edit_text("couldn't process question, try again later!")

    await sticker.delete()
