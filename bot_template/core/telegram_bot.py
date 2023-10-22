from aiogram import types
from bot_base.core.telegram_bot import TelegramBot

from bot_template.core.app_config import TemplateAppConfig
from bot_template.data_model.dm_pydantic import \
    SaveTelegramMessageRequest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot_template.core import TemplateApp


class TemplateTelegramBot(TelegramBot):
    _config_class = TemplateAppConfig
    recognized_hashtags = {"#ignore": {"ignore": True}}  #

    def __init__(self, config: _config_class, app: "TemplateApp" = None):
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
