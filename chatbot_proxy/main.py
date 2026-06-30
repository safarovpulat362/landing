from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.webhook import router as webhook_router
from app.services.proxy_client import proxy_client
from app.utils.logger import get_logger

log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Сервер запущен. Ожидание запросов...")
    yield
    await proxy_client.close()
    log.info("HTTP-клиент закрыт. Сервер остановлен.")


app = FastAPI(
    title="Чат-бот для отдела продаж (GigaChat + ProxyAPI)",
    description="MVP чат-бота для отдела продаж с интеграцией GigaChat через ProxyAPI",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(webhook_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
