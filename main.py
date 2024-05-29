import asyncio
from fastapi import FastAPI
from bot.commands import BOT_COMMANDS
from utils.logger import logging
from aiogram.types import Update
from config import initial_config as config
from fastapi.middleware.cors import CORSMiddleware
from bot.bot import (bot, dp)
from contextlib import asynccontextmanager
from pydantic import BaseModel
from chatbot.chat import ask

class Request(BaseModel):
    ip_address: str
    query: str


async def startup_event():
    """
    Check if webhook is set. If not or outdated- set it. Also set bot commands.
    """
    logging.info("Starting up the bot...")
    webhook_info = await bot.get_webhook_info()

    logging.info(f"Webhook info: {webhook_info} and config webhook info: {config.WEBHOOK_PATH}")

    await bot.set_my_commands(commands=BOT_COMMANDS)

    if webhook_info.url != config.WEBHOOK_PATH:
        response = await bot.set_webhook(url=config.WEBHOOK_PATH)
        logging.info(f"Updated webhook url: {config.WEBHOOK_PATH} is successfully set. Response: {response}")


async def shutdown_event():
    """
    Close the bot session
    """
    logging.info("Shutting down the bot...")
    await bot.session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    await shutdown_event()

# Initialize FastAPI app
app = FastAPI(title="A2SV Community Helper Telegram Bot", version="0.1.0", lifespan=lifespan)

# add cors policy
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "Hello adventurer!"}


@app.post(f"/bot/{config.BOT_TOKEN}")
async def bot_webhook(update: dict):
    """
    Upon receiving a webhook request, parse the request body into an Update.
    """
    logging.debug(update)
    res = Update.model_validate(update, context={"bot": bot})
    await dp.feed_update(bot=bot, update=res)

@app.post(f"/api/v1/chats")
async def chat_api(request: Request):
    """
    Chat API endpoint

    :param text: The text to be sent to the bot
    """

    response = ask(chat_id= request.ip_address, query= request.query)
    logging.debug(request)
    return {"message": response}

    
async def run_local():
    """
    Run the bot locally
    """
    logging.info("Starting bot locally...")
    await bot.delete_webhook()

    # And the run events dispatching
    await dp.start_polling(bot, polling_timeout=2)
    logging.info("Starting Polling...")

if __name__ == "__main__":
    if config.CONFIG_TYPE == "dev":
        print("wee")
        asyncio.run(run_local())
