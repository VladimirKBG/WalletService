from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Optional, Type

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeMeta

from app.config import settings
from base import DBConnectionManager

DATABASE_URL = settings.DATABASE_URL
ECHO = settings.SQL_ECHO

# --- Engine и SessionMaker ---
_engine: AsyncEngine = get_engine()

AsyncSessionMaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_engine() -> AsyncEngine:
    """Возвращает AsyncEngine (для скриптов/инициализации)."""
    return _engine


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency / контекстный менеджер для получения асинхронной сессии.

    Пример в FastAPI:
        async def endpoint(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionMaker() as session:
        yield session


@asynccontextmanager
async def transactional_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер, который открывает сессию и транзакцию:
    async with transactional_session() as session:
        # session - AsyncSession, внутри транзакции
    """
    async with AsyncSessionMaker() as session:
        async with session.begin():
            yield session


# --- Утилиты для конкурентной работы (SELECT ... FOR UPDATE) ---
async def lock_row_by_id(
    session: AsyncSession,
    model: Type[DeclarativeMeta],
    id_value: Any,
) -> Optional[Any]:
    """
    Заблокировать строку по первичному ключу (SELECT ... FOR UPDATE)
    и вернуть объект или None.

    Требует, чтобы у модели была колонка `id` (обычный кейс). Если PK другая
    колонка, используйте select(...) с нужным условием.
    """
    pk_col = getattr(model, "id", None)
    if pk_col is None:
        raise AttributeError(
            "Модель не имеет атрибута 'id'. Используйте select с явным условием."
        )
    stmt = select(model).where(pk_col == id_value).with_for_update()
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# --- Retry helper для сериализационных конфликтов ---
async def run_with_retry(
    func: Callable[..., Any],
    *args: Any,
    attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 1.0,
    **kwargs: Any,
) -> Any:
    """
    Простая функция-обёртка, повторяющая `func` при конфликтах транзакции
    (например, serialization failure). `func` должен быть coroutine-функцией.

    Логика: ловим DBAPIError и по тексу ошибки определяем возможность ретрая.
    Это обобщённый подход: при необходимости подстроить под конкретный драйвер
    (asyncpg) можно проверять type(e.orig) и конкретные коды ошибок.
    """
    last_exc: Optional[BaseException] = None
    for attempt in range(1, attempts + 1):
        try:
            return await func(*args, **kwargs)
        except DBAPIError as exc:
            last_exc = exc
            msg = str(exc.__context__ or exc.orig or exc)
            # грубая эвристика: ключевые слова, указывающие на сериализационные конфликты
            if any(keyword in msg.lower() for keyword in ("could not serialize", "serialization", "deadlock", "deadlock detected")):
                if attempt >= attempts:
                    raise
                # экспоненциальная пауза с джиттером
                delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                jitter = delay * 0.1 * (0.5 - (os.urandom(1)[0] / 255))
                await asyncio.sleep(max(0.0, delay + jitter))
                continue
            raise
    # если цикл завершился без return, пробросим последнее исключение
    if last_exc:
        raise last_exc
    raise RuntimeError("run_with_retry: неизвестная ошибка.")



