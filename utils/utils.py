from aiogram.utils.deep_linking import decode_payload
from config.config import bot
from aiogram.enums import ChatMemberStatus,ContentType
import asyncio
from keyboards.keyboards import main_kb
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from loguru import logger

def payload(object):
    if object:
        return decode_payload(object)
    else:
        return None

async def is_user_subscribed(channel_url: str, telegram_id: int) -> bool:
    try:
        # Получаем username канала из URL
        channel_username = channel_url.split('/')[-1]

        # Получаем информацию о пользователе в канале
        member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=telegram_id)

        # Проверяем статус пользователя
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            return True
        else:
            return False
    except Exception as e:
        # Если возникла ошибка (например, пользователь не найден или бот не имеет доступа к каналу)
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False

async def is_channel_valid(url: str, bot) -> bool:
    try:
        if url.startswith("https://t.me/"):
            url = "@" + url.split("/")[-1]
        url = url.rstrip('/')
        chat = await bot.get_chat(url)
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке канала: {e}")  # Логирование ошибки
        return False
   

async def broadcast_send(users: list, message: dict, content_type: str, button: dict, url: dict, progress_message):
    good_send = 0
    bad_send = 0
    keyboard = None

    # Проверка на наличие кнопки
    if not (button.text == '🔜 ПРОПУСТИТЬ' or url.text == '🔜 ПРОПУСТИТЬ'):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=button.text, url=url.text)]]
        )

    # Обработка пользователей
    total_users = len(users)
    for index, user in enumerate(users, start=1):
        try:
            chat_id = user.get('telegram_id')

            # Отправка текста
            if content_type == ContentType.TEXT:
                await bot.send_message(chat_id=chat_id, text=message.text, reply_markup=keyboard)
            
            # Отправка фото
            elif content_type == ContentType.PHOTO:
                await bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=message.caption, reply_markup=keyboard)
            
            # Отправка документа
            elif content_type == ContentType.DOCUMENT:
                await bot.send_document(chat_id=chat_id, document=message.document.file_id, caption=message.caption, reply_markup=keyboard)
            
            # Отправка видео
            elif content_type == ContentType.VIDEO:
                await bot.send_video(chat_id=chat_id, video=message.video.file_id, caption=message.caption, reply_markup=keyboard)

            # Отправка аудио
            elif content_type == ContentType.AUDIO:
                await bot.send_audio(chat_id=chat_id, audio=message.audio.file_id, caption=message.caption, reply_markup=keyboard)
            
            # Отправка голосового сообщения
            elif content_type == ContentType.VOICE:
                await bot.send_voice(chat_id=chat_id, voice=message.voice.file_id, caption=message.caption, reply_markup=keyboard)

            # Успешная отправка
            good_send += 1
        except Exception as e:
            logger.info(f"Ошибка отправки пользователю {chat_id}: {e}")
            bad_send += 1
        finally:
            # Расчёт прогресса
            progress = int((index / total_users) * 100)
            await progress_message.edit_text(
                f"➖ **Рассылка в процессе...** ➖\n\n"
                f"✅ **Успешно доставлено:** <b>{good_send}</b>\n"
                f"❌ **Не доставлено:** <b>{bad_send}</b>\n\n"
                f"📤 **Прогресс:** <b>{progress}%</b>"
            )
            await asyncio.sleep(1)  # Задержка между отправками

    # Возвращаем количество успешно/неуспешно отправленных сообщений
    return good_send, bad_send