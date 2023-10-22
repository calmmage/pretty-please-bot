from dotenv import load_dotenv

from bot_base.core import AppConfig, DatabaseConfig, TelegramBotConfig

load_dotenv()


class PrettyPleaseDatabaseConfig(DatabaseConfig):
    pass


class PrettyPleaseTelegramBotConfig(TelegramBotConfig):
    # id of the chat where the bot will be sending requests
    destination_chat_id: str
    refresh_period: int = 6  # 6 days

    # model_config = {
    #     "env_prefix": "TELEGRAM_BOT_",
    # }


class PrettyPleaseAppConfig(AppConfig):
    database: PrettyPleaseDatabaseConfig = PrettyPleaseDatabaseConfig()
    telegram_bot: PrettyPleaseTelegramBotConfig = PrettyPleaseTelegramBotConfig()
