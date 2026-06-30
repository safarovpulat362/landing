from pydantic import BaseModel
from typing import Optional


class WebhookResponse(BaseModel):
    user_id: str
    reply: str
    request_id: str
    status: str  # "ok" или "escalated"
    operator_message: Optional[str] = None
