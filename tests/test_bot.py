import pytest

from pretty_please_bot.core.app_config import PrettyPleaseTelegramBotConfig
from pretty_please_bot.core import PrettyPleaseTelegramBot


@pytest.fixture(scope="function")
def setup_environment(monkeypatch):
    monkeypatch.setenv(
        "TELEGRAM_BOT_TOKEN", "1234567890:aaabbbcccdd-aaabbbcccdddeee_abcdefg"
    )


def test_bot(setup_environment):
    config = PrettyPleaseTelegramBotConfig()
    bot = PrettyPleaseTelegramBot(config)
