from bot_base.core import AppConfig, DatabaseConfig, TelegramBotConfig


class TemplateDatabaseConfig(DatabaseConfig):
    pass


class TemplateTelegramBotConfig(TelegramBotConfig):
    pass


class TemplateAppConfig(AppConfig):
    _database_config_class = TemplateDatabaseConfig
    _telegram_bot_config_class = TemplateTelegramBotConfig
