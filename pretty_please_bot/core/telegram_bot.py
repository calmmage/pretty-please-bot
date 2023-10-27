import datetime
from textwrap import dedent
# from pretty_please_bot.data_model.dm_pydantic import SaveTelegramMessageRequest
from typing import TYPE_CHECKING

from aiogram import types

from bot_base.core import mark_command
from bot_base.core.telegram_bot import TelegramBot
from pretty_please_bot.core.app_config import PrettyPleaseTelegramBotConfig

if TYPE_CHECKING:
    from pretty_please_bot.core import PrettyPleaseApp


class PrettyPleaseTelegramBot(TelegramBot):
    _config_class = PrettyPleaseTelegramBotConfig
    recognized_hashtags = {"#ignore": {"ignore": True}}  #
    app: "PrettyPleaseApp"

    def __init__(self, config: _config_class, app: "PrettyPleaseApp" = None):
        super().__init__(config, app=app)
        self._last_refresh_time = datetime.datetime.now()

        # check destination chat id is not None
        if self.config.destination_chat_id is None:
            raise ValueError("Destination chat id is not set!")

    async def run(self) -> None:
        for user in self.config.allowed_users:
            self.app.register_user(user)
        await super().run()

    async def chat_message_handler(self, message: types.Message):
        # todo: ignore messages that are not in personal chat
        if message.chat.type != "private":
            return
        await self.pretty_please(message)
        # message_text = await super().chat_message_handler(message)

        # # save message to the database
        # if self.app:
        #     request = SaveTelegramMessageRequest(
        #         content=message_text,
        #         timestamp=message.date,
        #     )
        #     self.app.save_telegram_message(request)

    REPLY_TEXT_TEMPLATE = dedent(
        """Congratulations! Your request has been sent!
    Remaining token quota: {tokens_left}
    Token quota refreshes: {tokens_refresh_time}
    """
    )

    DECLINE_TEXT_TEMPLATE = dedent(
        """No tokens left, sorry :(
    Next refresh available in: {tokens_refresh_time}
    """
    )

    @mark_command(commands=["prettyPlease", "pp"], description="Pretty please")
    async def pretty_please(self, message: types.Message):
        # take message text
        message_text = await self._extract_message_text(message)
        destination_chat_id = self.config.destination_chat_id

        if message_text.startswith("/"):
            message_text = message_text.strip()
            # check if there's more text after the command
            if " " in message_text:
                message_text = message_text.split(" ", 1)[1].strip()
            else:
                reply_text = (
                    "Please specify your request after the command. "
                    "\nYou can use /pp for short."
                )
                await self.send_safe(
                    reply_text, message.chat.id, reply_to_message_id=message.message_id
                )
                return

        # allowed = self.tokens[message.from_user.username] > 0
        allowed = self.app.has_tokens(message.from_user.username)
        time_since_refresh = datetime.datetime.now() - self._last_refresh_time
        refresh_period = datetime.timedelta(days=self.config.refresh_period)
        time_until_refresh = refresh_period - time_since_refresh
        if allowed:
            # send it to the chat
            request_text = f"@{message.from_user.username} asks: \n{message_text}"
            await self.send_safe(request_text, destination_chat_id)
            self.app.spend_token(message.from_user.username)
            # self.tokens[message.from_user.username] -= 1
            reply_text = self.REPLY_TEXT_TEMPLATE.format(
                tokens_left=self.app.get_token_count(message.from_user.username),
                tokens_refresh_time=time_until_refresh,
            )
            await self.send_safe(
                reply_text, message.chat.id, reply_to_message_id=message.message_id
            )
        else:
            # todo: notify when token quota refreshes
            reply_text = self.DECLINE_TEXT_TEMPLATE.format(
                tokens_refresh_time=time_until_refresh,
            )
            await self.send_safe(
                reply_text, message.chat.id, reply_to_message_id=message.message_id
            )
        self.app.register_event(
            event_content=message_text, allowed=allowed, user=message.from_user.username
        )

    @mark_command(commands=["refresh"], description="Refresh token quota")
    async def refresh(self, message: types.Message, force=False):
        # todo: check if last refresh was less than 6 days ago
        time_since_refresh = datetime.datetime.now() - self._last_refresh_time
        refresh_period = datetime.timedelta(days=self.config.refresh_period)
        time_until_refresh = refresh_period - time_since_refresh
        if force or (time_until_refresh < datetime.timedelta(days=0)):
            # allow
            self._last_refresh_time = datetime.datetime.now()
            await self.app.refresh_tokens()
            await self.send_safe(
                text="Refreshed!",
                chat_id=message.chat.id,
                reply_to_message_id=message.message_id,
            )
        else:
            # decline
            reply_text = (
                f"Refresh blocked! Next refresh available in:" f" {time_until_refresh}"
            )
            await message.answer(reply_text)

    @mark_command("forceRefresh", description="Force refresh token quota")
    async def force_refresh(self, message: types.Message):
        username = message.from_user.username
        announcement_text = f"@{username} force refreshed the token quota! Cheater!"
        await self.send_safe(
            text=announcement_text, chat_id=self.config.destination_chat_id
        )
        await self.refresh(message, force=True)

    @mark_command(
        "listEvents",
        description="List latest events. Pass count=n for a custom number of events",
    )
    async def list_events(self, message: types.Message):
        """
        List latest events
        Pass count=n for a custom number of events
        Example: "/listevents count=5"
        :param message:
        :return:
        """
        message_text = await self._extract_message_text(message)
        kwargs = self._parse_attributes(message_text)
        events = await self.app.get_events(**kwargs)
        reply_text = "\n".join([str(event) for event in events])
        await self.send_safe(chat_id=message.chat.id, text=reply_text)

    async def bootstrap(self):
        await super().bootstrap()
