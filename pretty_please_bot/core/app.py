import datetime
from mongoengine import Document, DateTimeField, StringField, BooleanField

from bot_base.core import App
from pretty_please_bot.core.app_config import (
    PrettyPleaseAppConfig,
    PrettyPleaseDatabaseConfig,
    PrettyPleaseTelegramBotConfig,
)
from pretty_please_bot.core.telegram_bot import PrettyPleaseTelegramBot
from pretty_please_bot.data_model.dm_mongo import TelegramMessageMongo
from pretty_please_bot.data_model.dm_pydantic import SaveTelegramMessageRequest


class AppEvent(Document):
    event_content = StringField(required=True)
    allowed = BooleanField(required=True)
    user = StringField(required=True)
    date = DateTimeField(required=True)

    meta = {'collection': 'app_events'}


class PrettyPleaseApp(App):
    _app_config_class = PrettyPleaseAppConfig
    _telegram_bot_class = PrettyPleaseTelegramBot
    _database_config_class = PrettyPleaseDatabaseConfig
    _telegram_bot_config_class = PrettyPleaseTelegramBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # todo: make persistent over sessions - store in database
        self.app_events = []

    # def register_event(self, event):
    def register_event(self, event_content: str, allowed: bool, user: str):
        event = AppEvent(event_content=event_content, allowed=allowed,
                         date=datetime.datetime.now())
        self.app_events.append(event)

    def save_telegram_message(self, message: SaveTelegramMessageRequest):
        self._connect_db()
        item = TelegramMessageMongo(content=message.content, date=message.date)
        item.save()
