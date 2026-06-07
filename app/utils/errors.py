"""
Кастомные исключения для приложения
Позволяет обработчикам ошибок правильно реагировать на разные типы ошибок
"""

from typing import Any, Dict, Optional
from fastapi import status


class AutoPartsException(Exception):
    """
    Базовое исключение для приложения AutoParts
    Все остальные исключения наследуются от этого
    """
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ClientNotFound(AutoPartsException):
    """Клиент не найден в БД"""
    
    def __init__(self, client_id: str):
        super().__init__(
            message=f"Клиент {client_id} не найден",
            code="CLIENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class OrderNotFound(AutoPartsException):
    """Заказ не найден в БД"""
    
    def __init__(self, order_id: str):
        super().__init__(
            message=f"Заказ {order_id} не найден",
            code="ORDER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InvalidOrder(AutoPartsException):
    """Невалидный заказ (неправильные данные)"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="INVALID_ORDER",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class DeliveryCalculationError(AutoPartsException):
    """Ошибка при расчёте доставки"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="DELIVERY_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class AIServiceError(AutoPartsException):
    """Ошибка AI сервиса (модели, агенты)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AI_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {}
        )


class DatabaseError(AutoPartsException):
    """Ошибка БД (Supabase)"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ProductNotFound(AutoPartsException):
    """Запчасть не найдена"""
    
    def __init__(self, article: str):
        super().__init__(
            message=f"Запчасть с артикулом {article} не найдена",
            code="PRODUCT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedError(AutoPartsException):
    """Ошибка авторизации"""
    
    def __init__(self, message: str = "Необходима авторизация"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class PermissionDeniedError(AutoPartsException):
    """Нет прав доступа"""
    
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN
        )
