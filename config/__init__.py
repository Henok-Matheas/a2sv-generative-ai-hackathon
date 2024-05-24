import os
from dotenv import load_dotenv, dotenv_values
from pydantic import ConfigDict
from pydantic import BaseModel
import logging


if not dotenv_values():
    logging.error("No .env file found!")
    raise Exception("No .env file found!")

load_dotenv(override=True)

class Config(BaseModel):
    CONFIG_TYPE: str = ""
    CORS_ORGINS: list[str] = ["*"]

    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    BOT_NAME: str = os.environ.get("BOT_NAME", "A2SV Community Helper Bot")
    SERVICE_BASE_URL: str = os.environ.get(
        "SERVICE_BASE_URL",
        "https://a2sv-community-telegram-bot-lylswf275a-uc.a.run.app",
    )
    WEBHOOK_PATH: str = f"{SERVICE_BASE_URL}/bot/{BOT_TOKEN}"

    # LLM API KEYS
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    CACHE_SIZE: int = 1024
    CACHE_TIME: int = 1800

    # Loading Sticker Id
    LOADING_STICKER: str = "CAACAgIAAxkBAANJZbzSkvelL5pyrfiyC3r5MiqIqhoAAiMAAygPahQnUSXnjCCkBjQE"



class ProductionConfig(Config):
    CONFIG_TYPE: str = "production"
    pass


class DevConfig(Config):
    CONFIG_TYPE: str = "dev"
    BOT_TOKEN: str = os.environ.get("TESTING_BOT_TOKEN", "")
    SERVICE_BASE_URL: str = os.environ.get("SERVICE_BASE_URL", "")
    WEBHOOK_PATH: str = f"{SERVICE_BASE_URL}/bot/{BOT_TOKEN}"
    pass


class TestConfig(Config):
    CONFIG_TYPE: str = "test"


def get_settings(config_type: str = os.environ.get("CONFIG", "dev")) -> Config:
    if config_type == "dev":
        return DevConfig()
    if config_type == "test":
        return TestConfig()
    return ProductionConfig()


initial_config = get_settings()
tests_config = get_settings("test")
print("enviroment is: ", initial_config.CONFIG_TYPE)