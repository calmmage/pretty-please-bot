import datetime
from aiogram import types
from textwrap import dedent
# from pretty_please_bot.data_model.dm_pydantic import SaveTelegramMessageRequest
from typing import TYPE_CHECKING

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
        # todo: make persistent over sessions - store in database
        # todo: move over to the app class
        self.tokens = {user: 1 for user in self.config.allowed_users}
        self._last_refresh_time = datetime.datetime.now()

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
                reply_text = ("Please specify your request after the command. "
                              "\nYou can use /pp for short.")
                await message.answer(reply_text)
                return

        allowed = self.tokens[message.from_user.username] > 0
        time_since_refresh = datetime.datetime.now() - self._last_refresh_time
        refresh_period = datetime.timedelta(days=self.config.refresh_period)
        time_until_refresh = refresh_period - time_since_refresh
        if allowed:
            # send it to the chat
            request_text = f"@{message.from_user.username} asks: \n{message_text}"
            await self.send_safe(destination_chat_id, request_text)

            self.tokens[message.from_user.username] -= 1
            reply_text = self.REPLY_TEXT_TEMPLATE.format(
                tokens_left=self.tokens[message.from_user.username],
                tokens_refresh_time=time_until_refresh,
            )
            await message.answer(reply_text)
        else:
            # todo: notify when token quota refreshes
            reply_text = self.DECLINE_TEXT_TEMPLATE.format(
                tokens_refresh_time=time_until_refresh,
            )
            await message.answer(reply_text)
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
            for user in self.config.allowed_users:
                self.tokens[user] = 1
            await message.answer("Refreshed!")
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
        await self.send_safe(self.config.destination_chat_id, announcement_text)
        await self.refresh(message, force=True)

    async def bootstrap(self):
        await super().bootstrap()
