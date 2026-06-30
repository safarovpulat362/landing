import uuid
from fastapi import APIRouter
from app.models.request import WebhookRequest
from app.models.response import WebhookResponse
from app.services.dialog_manager import dialog_manager
from app.utils.logger import setup_logger, get_logger

router = APIRouter()
setup_logger()


@router.post("/webhook", response_model=WebhookResponse)
async def webhook(payload: WebhookRequest):
    request_id = str(uuid.uuid4())
    log = get_logger(request_id)

    log.info("Входящий запрос | user_id={} | message={}", payload.user_id, payload.message)

    reply, escalated = await dialog_manager.process_message(
        user_id=payload.user_id,
        message=payload.message,
        log=log,
    )

    status = "escalated" if escalated else "ok"
    operator_msg = (
        "Запрос передан оператору. Ожидайте звонка."
        if escalated else None
    )

    log.info("Ответ | status={} | reply={}", status, reply)

    return WebhookResponse(
        user_id=payload.user_id,
        reply=reply,
        request_id=request_id,
        status=status,
        operator_message=operator_msg,
    )
