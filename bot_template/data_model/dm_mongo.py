from mongoengine import Document, StringField, DateTimeField


class TelegramMessageMongo(Document):
    content = StringField(required=True)
    date = DateTimeField(required=True)

    meta = {'collection': 'telegram_messages'}


if __name__ == '__main__':
    # test mongo connection
    from bot_base.data_model.mongo_utils import connect_to_db

    connect_to_db()
