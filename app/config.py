"""
Конфигурация приложения
Все переменные окружения загружаются отсюда с использованием Pydantic
ВАЖНО: никогда не хардкодь ключи в коде!
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Главные настройки приложения
    Все значения подгружаются из переменных окружения
    """
    
    # ========== ENVIRONMENT ==========
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # ========== API ==========
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "http://localhost:8000/webhook")
    
    # ========== TELEGRAM ==========
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID", "0"))
    
    # ========== AI & LLM ==========
    # Все модели через OpenRouter с одним ключом
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Модели для различных агентов
    ORCHESTRATOR_MODEL: str = "deepseek/deepseek-r1"
    SALES_MODEL: str = "deepseek/deepseek-v3"
    SEARCH_MODEL: str = "google/gemini-2.0-flash-exp"
    ORDER_MODEL: str = "meta-llama/llama-3.3-70b"
    TRACKING_MODEL: str = "google/gemini-flash-1.5"
    ANALYTICS_MODEL: str = "deepseek/deepseek-r1"
    LANGUAGE_MODEL: str = "qwen/qwen-2.5-72b"
    
    # ========== DATABASE ==========
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # ========== CACHE ==========
    UPSTASH_REDIS_URL: str = os.getenv("UPSTASH_REDIS_URL", "")
    
    # ========== SEARCH ==========
    BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")
    
    # ========== MONITORING ==========
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "autoparts-agents")
    
    class Config:
        """Конфиг Pydantic"""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Кэшированный вызов настроек
    Загружается один раз при первом обращении
    
    Returns:
        Settings: объект конфигурации
    """
    return Settings()


# Глобальный объект настроек
settings = get_settings()
