# Чат-бот для отдела продаж (GigaChat + ProxyAPI)

MVP чат-бота для отдела продаж с интеграцией GigaChat через ProxyAPI.

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка .env

Файл `.env` уже создан. При необходимости отредактируйте ключи:

| Переменная | Описание |
|---|---|
| `PROXY_API_KEY` | API-ключ ProxyAPI |
| `PROXY_BASE_URL` | Базовый URL ProxyAPI |
| `PROXY_PATH` | Путь к GigaChat API |
| `MODEL_NAME` | Имя модели |
| `DATABASE_URL` | URL БД (SQLite, для продакшена — PostgreSQL) |

### 3. Запуск

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу: http://127.0.0.1:8000

### 4. Тестовый запрос

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "message": "Привет! У меня сломалась стиральная машина"}'
```

## Эндпоинты

- `POST /webhook` — основной эндпоинт чат-бота
- `GET /health` — проверка состояния сервера

## Архитектура

```
chatbot_proxy/
├── app/
│   ├── api/webhook.py      # Эндпоинт /webhook
│   ├── core/config.py      # Конфигурация из .env
│   ├── models/             # Pydantic схемы
│   ├── services/
│   │   ├── proxy_client.py  # Клиент ProxyAPI (httpx)
│   │   └── dialog_manager.py # Управление диалогами
│   └── utils/
│       ├── logger.py       # Логирование (loguru)
│       └── retry.py        # Retry с экспоненциальной задержкой
├── data/                   # SQLite БД
├── main.py                 # Точка входа FastAPI
├── .env                    # Переменные окружения
└── requirements.txt        # Зависимости
```

## Функции

- Асинхронный обмен сообщениями через GigaChat (ProxyAPI)
- Retry 3 раза при сетевых ошибках (экспоненциальная задержка)
- Кэш ответов в памяти (MD5-хеш вопроса → ответ)
- Состояния диалогов в памяти {user_id: step}
- Логирование с request_id (uuid)
- Эскалация оператору при ошибке GigaChat или отказе клиента
