"""
AutoParts Backend - главная точка входа FastAPI приложения
Платформа для онлайн продажи автозапчастей из ОАЭ в Таджикистан

Структура:
- Маршруты для заказов, продуктов, клиентов, доставки
- Интеграция с Supabase БД
- AI агенты через OpenRouter
- Telegram вебхук для уведомлений
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.utils.logger import app_logger
from app.routers import orders, products, clients, delivery, agents

# ========== ЛОГИРОВАНИЕ ==========
logger = app_logger


# ========== LIFECYCLE СОБЫТИЯ ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Событие запуска и остановки приложения
    На старте: инициализируем БД, проверяем соединение
    На остановке: закрываем подключения
    """
    # STARTUP
    logger.info("🚀 Запуск AutoParts Backend...")
    try:
        await init_db()
        logger.info("✅ База данных инициализирована успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Остановка AutoParts Backend...")


# ========== ИНИЦИАЛИЗАЦИЯ FASTAPI ==========
app = FastAPI(
    title="AutoParts Backend API",
    description="REST API для платформы продажи автозапчастей из ОАЭ в Таджикистан",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ========== MIDDLEWARE ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Ограничить в production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== ОБРАБОТЧИК ОШИБОК ==========
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Глобальный обработчик ошибок
    Логирует ошибку и возвращает JSON ответ
    """
    logger.error(f"❌ Необработанная ошибка: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "Внутренняя ошибка сервера"
        }
    )


# ========== КОРНЕВЫЕ МАРШРУТЫ ==========
@app.get("/", tags=["Health"])
async def root():
    """Проверка живого сервера"""
    return {
        "status": "ok",
        "service": "AutoParts Backend API",
        "version": "0.1.0",
        "environment": settings.ENV
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Проверка здоровья сервера
    Используется для мониторинга и load balancer
    """
    return {
        "status": "healthy",
        "service": "autoparts-backend",
        "debug": settings.DEBUG
    }


# ========== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ==========
app.include_router(
    orders.router,
    prefix="/api/orders",
    tags=["Orders"]
)

app.include_router(
    products.router,
    prefix="/api/products",
    tags=["Products"]
)

app.include_router(
    clients.router,
    prefix="/api/clients",
    tags=["Clients"]
)

app.include_router(
    delivery.router,
    prefix="/api/delivery",
    tags=["Delivery"]
)

app.include_router(
    agents.router,
    prefix="/api/agents",
    tags=["Agents"]
)


# ========== TELEGRAM WEBHOOK ==========
@app.post("/webhook/telegram", tags=["Webhook"])
async def telegram_webhook(update: dict):
    """
    Вебхук для получения обновлений от Telegram бота
    Получает сообщения от пользователей и уведомления о платежах
    
    Args:
        update: Telegram Update object
    
    Returns:
        Статус обработки
    """
    logger.info(f"📨 Telegram webhook: {update}")
    # TODO: Обработка вебхука в отдельном сервисе
    return {"ok": True}


# ========== 404 ОБРАБОТЧИК ==========
@app.get("/{full_path:path}", tags=["NotFound"])
async def catch_all(full_path: str):
    """Обработчик несуществующих маршрутов"""
    logger.warning(f"⚠️ 404: {full_path}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": f"Маршрут /{full_path} не найден",
            "docs": "/api/docs"
        }
    )


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    import uvicorn
    
    logger.info("🔧 Запуск Uvicorn сервера...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
