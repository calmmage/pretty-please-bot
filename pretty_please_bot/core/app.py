from bot_base.core import App
from pretty_please_bot.core.app_config import (
    PrettyPleaseAppConfig,
    PrettyPleaseDatabaseConfig,
    PrettyPleaseTelegramBotConfig,
)
from pretty_please_bot.core.telegram_bot import PrettyPleaseTelegramBot
from pretty_please_bot.data_model.dm_mongo import TelegramMessageMongo
from pretty_please_bot.data_model.dm_pydantic import SaveTelegramMessageRequest


class PrettyPleaseApp(App):
    _app_config_class = PrettyPleaseAppConfig
    _telegram_bot_class = PrettyPleaseTelegramBot
    _database_config_class = PrettyPleaseDatabaseConfig
    _telegram_bot_config_class = PrettyPleaseTelegramBotConfig

    def save_telegram_message(self, message: SaveTelegramMessageRequest):
        self._connect_db()
        item = TelegramMessageMongo(content=message.content, date=message.date)
        item.save()
