"""
Подключение к Supabase (PostgreSQL + Realtime)
Работает с базой данных для хранения клиентов, заказов, доставки и запчастей
ВАЖНО: никогда не хардкодь ключи! Используются переменные окружения
"""

import logging
from typing import Optional, Dict, Any

from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseDB:
    """
    Singleton для работы с Supabase
    Гарантирует единственное подключение к БД на всё приложение
    """
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Получить клиент Supabase
        Создаёт подключение при первом обращении, потом переиспользует
        
        Returns:
            Client: подключение к Supabase
            
        Raises:
            Exception: если не получилось подключиться
        """
        if cls._instance is None:
            try:
                if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                    raise ValueError("SUPABASE_URL и SUPABASE_ANON_KEY не установлены")
                
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_ANON_KEY
                )
                logger.info("✅ Supabase клиент инициализирован успешно")
            except Exception as e:
                logger.error(f"❌ Ошибка подключения к Supabase: {e}")
                raise
        
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """
        Сбросить подключение (для тестирования)
        """
        cls._instance = None
        logger.info("🔄 Supabase подключение сброшено")


def get_db() -> Client:
    """
    FastAPI dependency для получения клиента БД
    Используется в маршрутах как параметр функции
    
    Returns:
        Client: подключение к Supabase
        
    Example:
        @router.get("/clients")
        async def get_clients(db: Client = Depends(get_db)):
            response = db.table("clients").select("*").execute()
            return response.data
    """
    return SupabaseDB.get_client()


async def init_db() -> None:
    """
    Инициализировать БД при запуске приложения
    Проверяет соединение и логирует информацию о БД
    
    Raises:
        Exception: если БД недоступна
    """
    try:
        db = SupabaseDB.get_client()
        
        # Проверка соединения простым запросом к таблице clients
        result = db.table("clients").select("count", count="exact").execute()
        client_count = result.count if hasattr(result, 'count') else 0
        
        logger.info(f"✅ БД готова. Клиентов в системе: {client_count}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise


# ========== SQL ДЛЯ ИНИЦИАЛИЗАЦИИ ТАБЛИЦ ==========
# Выполнить один раз в Supabase SQL editor
DB_INIT_SQL = """
-- ========== ТАБЛИЦА КЛИЕНТОВ ==========
CREATE TABLE IF NOT EXISTS clients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  telegram_id BIGINT UNIQUE,
  name VARCHAR(100),
  phone VARCHAR(20),
  city VARCHAR(50),
  language VARCHAR(10) DEFAULT 'ru',
  total_orders INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ========== ТАБЛИЦА ЗАКАЗОВ ==========
CREATE TABLE IF NOT EXISTS orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_number SERIAL UNIQUE,
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  car_brand VARCHAR(50),
  car_model VARCHAR(50),
  car_year INT,
  part_name VARCHAR(200),
  part_article VARCHAR(100),
  price_uae_usd DECIMAL(10,2),
  price_client DECIMAL(10,2),
  prepayment DECIMAL(10,2),
  remainder DECIMAL(10,2),
  status VARCHAR(20) DEFAULT 'new',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ========== ТАБЛИЦА ДОСТАВКИ ==========
CREATE TABLE IF NOT EXISTS deliveries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  method VARCHAR(10) CHECK (method IN ('air', 'cargo')),
  weight_kg DECIMAL(8,2),
  cost_usd DECIMAL(8,2),
  days_min INT,
  days_max INT,
  status VARCHAR(20) DEFAULT 'pending',
  tracking_number VARCHAR(100),
  estimated_date DATE,
  actual_date DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ========== ТАБЛИЦА КАТАЛОГА ЗАПЧАСТЕЙ ==========
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  article VARCHAR(100) UNIQUE,
  name VARCHAR(200),
  car_brand VARCHAR(50),
  price_uae DECIMAL(10,2),
  price_retail DECIMAL(10,2),
  weight_kg DECIMAL(8,2),
  in_stock BOOLEAN DEFAULT false,
  image_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ========== ИНДЕКСЫ ДЛЯ ОПТИМИЗАЦИИ ==========
CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders(client_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_deliveries_order_id ON deliveries(order_id);
CREATE INDEX IF NOT EXISTS idx_products_article ON products(article);
CREATE INDEX IF NOT EXISTS idx_clients_telegram_id ON clients(telegram_id);
"""


# ========== HELPER ФУНКЦИИ ДЛЯ CRUD ОПЕРАЦИЙ ==========
async def create_client(
    db: Client,
    telegram_id: int,
    name: str,
    phone: str,
    city: str,
    language: str = "ru"
) -> Dict[str, Any]:
    """
    Создать нового клиента в БД
    
    Args:
        db: Supabase клиент
        telegram_id: ID клиента в Telegram
        name: Имя клиента
        phone: Телефон клиента
        city: Город доставки
        language: Язык клиента (ru/tg)
        
    Returns:
        Созданный клиент (словарь)
        
    Raises:
        Exception: если не получилось создать
    """
    try:
        response = db.table("clients").insert({
            "telegram_id": telegram_id,
            "name": name,
            "phone": phone,
            "city": city,
            "language": language
        }).execute()
        
        logger.info(f"✅ Клиент создан: {telegram_id}")
        return response.data[0] if response.data else {}
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания клиента: {e}")
        raise


async def get_client_by_telegram_id(db: Client, telegram_id: int) -> Optional[Dict[str, Any]]:
    """
    Получить клиента по Telegram ID
    
    Args:
        db: Supabase клиент
        telegram_id: ID в Telegram
        
    Returns:
        Клиент или None если не найден
    """
    try:
        response = db.table("clients").select("*").eq("telegram_id", telegram_id).execute()
        return response.data[0] if response.data else None
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения клиента: {e}")
        raise


async def create_order(
    db: Client,
    client_id: str,
    car_brand: str,
    car_model: str,
    car_year: int,
    part_name: str,
    part_article: str,
    price_uae_usd: float,
    price_client: float,
    prepayment: float,
    remainder: float
) -> Dict[str, Any]:
    """
    Создать новый заказ
    
    Args:
        db: Supabase клиент
        client_id: UUID клиента
        car_brand: Марка авто
        car_model: Модель авто
        car_year: Год выпуска
        part_name: Название запчасти
        part_article: Артикул
        price_uae_usd: Цена в ОАЭ
        price_client: Цена для клиента
        prepayment: Размер предоплаты
        remainder: Остаток
        
    Returns:
        Созданный заказ
    """
    try:
        response = db.table("orders").insert({
            "client_id": client_id,
            "car_brand": car_brand,
            "car_model": car_model,
            "car_year": car_year,
            "part_name": part_name,
            "part_article": part_article,
            "price_uae_usd": price_uae_usd,
            "price_client": price_client,
            "prepayment": prepayment,
            "remainder": remainder,
            "status": "new"
        }).execute()
        
        logger.info(f"✅ Заказ создан: {response.data[0]['order_number']}")
        return response.data[0] if response.data else {}
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания заказа: {e}")
        raise


async def get_order_by_id(db: Client, order_id: str) -> Optional[Dict[str, Any]]:
    """
    Получить заказ по ID
    
    Args:
        db: Supabase клиент
        order_id: UUID заказа
        
    Returns:
        Заказ или None
    """
    try:
        response = db.table("orders").select("*").eq("id", order_id).execute()
        return response.data[0] if response.data else None
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения заказа: {e}")
        raise


async def update_order_status(
    db: Client,
    order_id: str,
    status: str
) -> Dict[str, Any]:
    """
    Обновить статус заказа
    
    Args:
        db: Supabase клиент
        order_id: UUID заказа
        status: Новый статус
        
    Returns:
        Обновленный заказ
    """
    try:
        response = db.table("orders").update({
            "status": status,
            "updated_at": "now()"
        }).eq("id", order_id).execute()
        
        logger.info(f"✅ Статус заказа обновлен: {order_id} -> {status}")
        return response.data[0] if response.data else {}
        
    except Exception as e:
        logger.error(f"❌ Ошибка обновления статуса: {e}")
        raise
