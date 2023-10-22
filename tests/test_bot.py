import pytest

from bot_template.core.app_config import TemplateTelegramBotConfig
from bot_template.core import TemplateTelegramBot


@pytest.fixture(scope="function")
def setup_environment(monkeypatch):
    monkeypatch.setenv(
        "TELEGRAM_BOT_TOKEN", "1234567890:aaabbbcccdd-aaabbbcccdddeee_abcdefg"
    )


def test_bot(setup_environment):
    config = TemplateTelegramBotConfig()
    bot = TemplateTelegramBot(config)
