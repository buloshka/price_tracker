from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Инициализируем приложение FastAPI с метаданными
app = FastAPI(
    title="Price Tracker API",
    description="Сервис мониторинга цен с уведомлениями в Telegram",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # На проде здесь должен быть конкретный адрес фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "working",
        "message": "Price Tracker API is up and running"
    }

# Сюда мы чуть позже подключим наш роутер авторизации:
# from src.routers.auth import router as auth_router
# app.include_router(auth_router)
