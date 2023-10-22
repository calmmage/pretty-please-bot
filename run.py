# run the app
from bot_base.data_model.mongo_utils import connect_to_db
from bot_base.utils.logging_utils import setup_logger
from pretty_please_bot.core.app import PrettyPleaseApp

if __name__ == '__main__':
    # connect to db
    connect_to_db()

    # setup logger
    setup_logger()

    app = PrettyPleaseApp()
    app.run()
