from bot_base.core import AppConfig, DatabaseConfig, TelegramBotConfig


class PrettyPleaseDatabaseConfig(DatabaseConfig):
    pass


class PrettyPleaseTelegramBotConfig(TelegramBotConfig):
    pass


class PrettyPleaseAppConfig(AppConfig):
    database: PrettyPleaseDatabaseConfig = PrettyPleaseDatabaseConfig()
    telegram_bot: PrettyPleaseTelegramBotConfig = PrettyPleaseTelegramBotConfig()
