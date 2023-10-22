from pydantic import BaseModel
from datetime import datetime


class SaveTelegramMessageRequest(BaseModel):
    content: str
    date: datetime
