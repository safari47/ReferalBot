from .database import engine, async_session_maker, Base
from functools import wraps
from sqlalchemy import text


# Декоратор для работы с базой данных
def connection(isolation_level=None):
    def decorator(method):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            async with async_session_maker() as session:
                try:
                    # Устанавливаем уровень изоляции, если передан
                    if isolation_level:
                        await session.execute(
                            text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
                        )

                    # Выполняем декорированный метод
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()  # Откатываем сессию при ошибке
                    raise e  # Поднимаем исключение дальше
                finally:
                    await session.close()  # Закрываем сессию

        return wrapper

    return decorator

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

