import hashlib
from typing import Optional

from app.services.proxy_client import proxy_client
from app.utils.logger import get_logger


class DialogManager:
    def __init__(self):
        # {user_id: название_шага}
        self.states: dict[str, str] = {}
        # {hash вопроса: ответ}
        self.cache: dict[str, str] = {}
        # Системный промпт — задаёт тон и правила бота
        self.system_prompt = (
            "Ты — дружелюбный менеджер сервиса по ремонту бытовой техники в Краснодаре. "
            "Твоя задача — помочь клиенту: принять заявку, назвать цену, договориться о выезде мастера. "
            "Отвечай коротко, тепло, по-человечески. "
            "Если клиент говорит 'отказ', 'не надо', 'передумал' — подтверди и вежливо попрощайся."
        )
        # История диалогов {user_id: [{"role": ..., "content": ...}]}
        self.histories: dict[str, list[dict]] = {}

    def _hash_message(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _is_escalation(self, text: str) -> bool:
        keywords = ["отказ", "не надо", "передумал", "оператор", "человека"]
        return any(kw in text.lower() for kw in keywords)

    def get_reply_from_cache(self, message: str) -> Optional[str]:
        h = self._hash_message(message)
        return self.cache.get(h)

    def set_cache(self, message: str, reply: str):
        h = self._hash_message(message)
        self.cache[h] = reply

    async def process_message(self, user_id: str, message: str, log) -> tuple[str, bool]:
        # Проверка кэша
        cached = self.get_reply_from_cache(message)
        if cached:
            log.info("Ответ найден в кэше")
            return cached, False

        # Проверка эскалации
        if self._is_escalation(message):
            log.info("Обнаружен отказ — эскалация оператору")
            reply = "Я передал ваш запрос живому оператору. Он свяжется с вами в ближайшее время. Спасибо за обращение!"
            self.set_cache(message, reply)
            return reply, True

        # Формируем историю
        if user_id not in self.histories:
            self.histories[user_id] = [{"role": "system", "content": self.system_prompt}]

        self.histories[user_id].append({"role": "user", "content": message})
        messages = self.histories[user_id]

        # Обновляем состояние
        self.states[user_id] = "processing"

        try:
            data = await proxy_client.chat_completion(messages=messages, log=log)
            reply = data["choices"][0]["message"]["content"].strip()
            self.histories[user_id].append({"role": "assistant", "content": reply})
            self.set_cache(message, reply)
            self.states[user_id] = "done"
            return reply, False
        except Exception as e:
            log.error("Ошибка GigaChat: {}", str(e))
            self.states[user_id] = "error"
            reply = "Произошла ошибка при обработке запроса. Ваш запрос передан оператору."
            return reply, True


dialog_manager = DialogManager()
