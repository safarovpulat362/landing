from pydantic import BaseModel


class WebhookRequest(BaseModel):
    user_id: str
    message: str
