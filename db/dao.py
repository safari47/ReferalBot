from .base import connection
from .models import User, Chanel
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

@connection()
async def set_user(
    session, user_id: int, first_name: str, last_name: str, username: str, refer_id: int
):
    try:
        # Поиск пользователя по telegram_id
        user = await session.scalar(select(User).filter_by(telegram_id=user_id))

        if not user:
            new_user = User(
                telegram_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                refer_id=refer_id,
            )
            session.add(new_user)

            # Проверка refer_id и обновление счетчика если refer_id указан
            if refer_id is not None:
                referrer = await session.scalar(
                    select(User).filter_by(telegram_id=refer_id)
                )
                if referrer:
                    referrer.refer_count += 1

            await session.commit()
            return False
        else:
            return True
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        await session.rollback()

@connection()
async def get_user(session, user_id: int):
    try:
        user = await session.scalar(select(User).filter_by(telegram_id=user_id))
        return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        return None

@connection()
async def add_chanel(session, title: str, url: str):
    try:
        new_chanel = Chanel(title=title, url=url)
        session.add(new_chanel)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении канала: {e}")
        await session.rollback()

@connection()
async def delete_chanel(session, url: str):
    try:
        chanel = await session.scalar(select(Chanel).filter_by(url=url))
        if chanel:
            await session.delete(chanel)
            await session.commit()
            return True
        else:
            return False
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении канала: {e}")
        await session.rollback()

@connection()
async def get_chanels(session):
    try:
        result = []
        chanels = await session.execute(select(Chanel))
        chanel_list = chanels.scalars().all()
        for chanel in chanel_list:
            title, url = map(str, (chanel.title, chanel.url))
            result.append({"title": title, "url": url})  # Добавляем каналы в список

        return result
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении канала: {e}")
        await session.rollback()

@connection()
async def get_all_users(session):
    try:
        result = []
        users = await session.execute(select(User))
        user_list = users.scalars().all()
        for user in user_list:
            telegram_id, first_name, last_name, username, refer_id = map(str, (user.telegram_id, user.first_name, user.last_name, user.username, user.refer_id))
            result.append({"telegram_id": telegram_id, "first_name": first_name, "last_name": last_name, "username": username, "refer_id": refer_id})

        return result
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении канала: {e}")
        await session.rollback()
