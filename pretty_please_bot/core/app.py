import datetime
import json

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
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

    meta = {"collection": "app_events"}

    def __str__(self):  # date, user, allowed, event_content
        return (
            f"{self.date}, {self.user}, Allowed: {self.allowed}, "
            f"Text:\n{self.event_content}"
        )

    def __repr__(self):
        return (
            f"AppEvent({self.event_content=} {self.allowed=} {self.user=} {self.date=})"
        )


class PrettyPleaseApp(App):
    _app_config_class = PrettyPleaseAppConfig
    _telegram_bot_class = PrettyPleaseTelegramBot
    _database_config_class = PrettyPleaseDatabaseConfig
    _telegram_bot_config_class = PrettyPleaseTelegramBotConfig
    bot: PrettyPleaseTelegramBot

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # todo: make persistent over sessions - store in database
        self.app_events = []
        # self.events_path = self.data_dir / "events.json"

        # load events from disk
        # if self.events_path.exists():
        #     with open(self.events_path, "r") as f:
        #         self.app_events = json.load(f)

        # load events from database
        # todo: sort by date?
        for event in AppEvent.objects:
            self.app_events.append(event)

        # sync events on disk and in database
        # with open(self.events_path, "w") as f:

        # tokens file
        self.tokens_path = self.data_dir / "tokens.json"
        self.tokens = {}
        if self.tokens_path.exists():
            with open(self.tokens_path, "r") as f:
                self.tokens.update(json.load(f))

        self._schedule_jobs()

    # def register_event(self, event):
    def register_event(self, event_content: str, allowed: bool, user: str):
        event = AppEvent(
            event_content=event_content,
            allowed=allowed,
            date=datetime.datetime.now(),
            user=user,
        )
        self.app_events.append(event)
        # save events to disk
        # with open(self.events_path, "w") as f:
        #     json.dump(self.app_events, f)
        # save to database
        event.save()

    def save_telegram_message(self, message: SaveTelegramMessageRequest):
        self._connect_db()
        item = TelegramMessageMongo(content=message.content, date=message.date)
        item.save()

    async def get_events(self, count=10):
        return self.app_events[-count:]

    def get_token_count(self, user):
        return self.tokens[user]

    def has_tokens(self, user):
        return self.tokens[user] > 0

    def spend_token(self, user):
        if self.has_tokens(user):
            self.tokens[user] -= 1
            self._save_tokens()
        else:
            raise ValueError("No tokens left")

    async def refresh_tokens(self):
        for key in self.tokens:
            self.tokens[key] = 1  # todo: make it configurable per group
        self._save_tokens()

    def register_user(self, user):
        if user not in self.tokens:
            self.logger.info(f"Registering user {user}")
            self.tokens[user] = 1  # todo: make it configurable per group
            # save tokens to disk
            self._save_tokens()
        else:
            self.logger.info(f"User {user} already registered")

    def _save_tokens(self):
        with open(self.tokens_path, "w") as f:
            json.dump(self.tokens, f)

    # new: rework into complete app function
    # 1) request - make a wish. reply - request accepted or declined
    # 2) register user (add user to group)
    # 3) create a new group
    # 4) list groups for user

    # --------------------------------
    # Schedule tasks
    # --------------------------------
    @staticmethod
    def _get_next_day_of_week(day_of_week):
        today = datetime.datetime.now()
        days_ahead = day_of_week - today.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + datetime.timedelta(days=days_ahead, hours=23 - today.hour)

    def _schedule_jobs(self):
        # every Monday at 23:59
        next_monday = self._get_next_day_of_week(0)
        refresh_trigger = IntervalTrigger(weeks=1, start_date=next_monday)
        self._scheduler.add_job(
            self._task_1_refresh_tokens,
            trigger=refresh_trigger,
            id="refresh_tokens",
            name="Refresh tokens",
        )

        # every Sunday at 23:59
        next_sunday = self._get_next_day_of_week(6)
        notify_trigger = IntervalTrigger(weeks=1, start_date=next_sunday)
        self._scheduler.add_job(
            self._task_2_notify_users,
            trigger=notify_trigger,
            id="notify_users",
            name="Notify users",
        )

    async def _task_1_refresh_tokens(self):
        """
        Refresh tokens and notify users
        :return:
        """
        await self.refresh_tokens()
        message = "Tokens refreshed. Make your wishes!"
        await self.bot.send_safe(message, self.bot.config.destination_chat_id)

    async def _task_2_notify_users(self):
        """
        Notify users about upcoming token refresh
        :return:
        """
        self.logger.info("Notifying users")
        message = "Tokens will be refreshed in 1 day"
        await self.bot.send_safe(message, self.bot.config.destination_chat_id)
