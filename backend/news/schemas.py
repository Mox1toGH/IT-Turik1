from datetime import datetime

from ninja import Schema
from pydantic import JsonValue

class NewsArticleRequest(Schema):
    title: str
    content: dict[str, JsonValue]
    send_notification: bool = False


class NewsArticleResponse(Schema):
    id: int
    title: str
    content: dict[str, JsonValue]
    created_by: int | None
    created_by_name: str
    created_at: datetime
    updated_at: datetime


class NewsListResponse(Schema):
    items: list[NewsArticleResponse]
    count: int
