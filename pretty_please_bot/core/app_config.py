from bot_base.core import AppConfig, DatabaseConfig, TelegramBotConfig


class PrettyPleaseDatabaseConfig(DatabaseConfig):
    pass


class PrettyPleaseTelegramBotConfig(TelegramBotConfig):
    pass


class PrettyPleaseAppConfig(AppConfig):
    _database_config_class = PrettyPleaseDatabaseConfig
    _telegram_bot_config_class = PrettyPleaseTelegramBotConfig
