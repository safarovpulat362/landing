import httpx
from app.core.config import config
from app.utils.retry import async_retry


class ProxyClient:
    def __init__(self):
        self.base_url = config.proxy_base_url.rstrip("/")
        self.path = config.proxy_path
        self.api_key = config.proxy_api_key
        self.model = config.model_name
        self._client: httpx.AsyncClient | None = None
        # Мок-ответы для демонстрации, если API недоступен
        self.mock_responses = {
            "стиральн": "Здравствуйте! Починим вашу стиральную машину в Краснодаре. "
                        "Называем цену до выезда, диагностика бесплатно. "
                        "Платите только когда всё заработает. Какой адрес?",
            "холодильн": "Починим холодильник в Краснодаре. Бесплатно проверим, "
                         "скажем цену до выезда. Оплата — после результата. Оставляйте заявку!",
            "плит": "Ремонт плит в Краснодаре. Диагностика 0 руб, цена известна до выезда. "
                    "Звоните — поможем!",
            "посудом": "Чиним посудомоечные машины в Краснодаре. "
                       "Бесплатная диагностика, оплата по факту. Оставьте заявку!",
        }

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=15.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_mock_reply(self, messages: list[dict]) -> dict:
        user_text = ""
        for m in messages:
            if m["role"] == "user":
                user_text = m["content"].lower()
        for keyword, reply in self.mock_responses.items():
            if keyword in user_text:
                return {
                    "choices": [{"message": {"content": reply, "role": "assistant"}}]
                }
        return {
            "choices": [{"message": {
                "content": "Здравствуйте! Чиним любую бытовую технику в Краснодаре. "
                           "Бесплатная диагностика, оплата после результата. Что у вас сломалось?",
                "role": "assistant",
            }}]
        }

    @async_retry(max_retries=2, base_delay=1.0)
    async def chat_completion(self, messages: list[dict], log=None) -> dict:
        try:
            client = await self.get_client()
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 512,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = await client.post(self.path, json=payload, headers=headers)
            response.raise_for_status()
            if log:
                log.info("Ответ от ProxyAPI получен")
            return response.json()
        except Exception as e:
            if log:
                log.warning("ProxyAPI недоступен ({}). Используется мок-ответ.", str(e))
            return self._get_mock_reply(messages)


proxy_client = ProxyClient()
