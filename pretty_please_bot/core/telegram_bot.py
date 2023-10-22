from aiogram import types
from bot_base.core.telegram_bot import TelegramBot

from pretty_please_bot.core.app_config import PrettyPleaseAppConfig
from pretty_please_bot.data_model.dm_pydantic import \
    SaveTelegramMessageRequest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pretty_please_bot.core import PrettyPleaseApp


class PrettyPleaseTelegramBot(TelegramBot):
    _config_class = PrettyPleaseAppConfig
    recognized_hashtags = {"#ignore": {"ignore": True}}  #

    def __init__(self, config: _config_class, app: "PrettyPleaseApp" = None):
        super().__init__(config, app=app)

    async def chat_message_handler(self, message: types.Message):
        message_text = await super().chat_message_handler(message)

        # save message to the database
        if self.app:
            request = SaveTelegramMessageRequest(
                content=message_text,
                timestamp=message.date,
            )
            self.app.save_message(request)
