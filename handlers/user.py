from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from loguru import logger
from keyboards.keyboards import (
    main_kb,
    chanels_kb,
)
from aiogram.utils.deep_linking import create_start_link
from config.config import bot
from db.dao import set_user, get_chanels, get_user
from utils.utils import payload, is_user_subscribed


router = Router()


# Функция для реагирования на команду /start
@router.message(CommandStart())
async def start(message: Message, command: CommandObject):
    invite_id = payload(command.args)
    user = await set_user(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        refer_id=invite_id,
    )
    if user:
        await message.answer(
            f"Привет! Я готов к работе. 🔗",
            reply_markup=main_kb(user_id=message.from_user.id),
        )
    else:
        kb = await get_chanels()
        await message.answer(
            "Для использования бота нужно подписаться", reply_markup=chanels_kb(kb)
        )


@router.callback_query(F.data == "check_subscription")
async def check_subs_func(call: CallbackQuery):
    await call.answer("Проверка подписки...")
    # Проверка подписки пользователя на каналы
    kb = await get_chanels()
    for chanel in kb:
        title = chanel.get("title")
        url = chanel.get("url")
        user_id = call.from_user.id
        is_subscribed = await is_user_subscribed(url, user_id)
        if is_subscribed is False:
            await call.message.answer(
                f"❌ вы не подписались на канал 👉 {title}", reply_markup=chanels_kb(kb)
            )
            return False
    await call.message.answer(
        "Спасибо за подписки на все каналы! Теперь можете воспользоваться функционалом бота",
        reply_markup=main_kb(call.from_user.id),
    )


@router.message(F.user_shared)
async def shared_user(message: Message):
    user_id = message.user_shared.user_id
    request_id = message.user_shared.request_id
    request_text = {
        1: "<b>👨‍🦰 Unique Telegram User ID:</b>",
        2: "<b>🤖 Unique Telegram BOT ID:</b>",
    }
    await message.answer(f"{request_text[request_id]} <code><b>{user_id}</b></code>")


@router.message(F.chat_shared)
async def shared_chat(message: Message):
    chat_id = message.chat_shared.chat_id
    request_id = message.chat_shared.request_id
    request_text = {
        3: "<b>👥 Unique Telegram Group ID:</b>",
        4: "<b>📢 Unique Telegram Channel ID:</b>",
    }
    await message.answer(f"{request_text[request_id]} <code><b>{chat_id}</b></code>")


@router.message(F.text == "🆔 MY INFO")
async def info(message: Message):
    message_id = message.message_id
    firstname = message.from_user.first_name or ""
    lastname = message.from_user.last_name or ""
    user_id = message.from_user.id
    premium = message.from_user.is_premium
    username = message.from_user.username
    refer_count = await get_user(user_id=user_id)
    referal_link = await create_start_link(bot, user_id, encode=True)
    await message.answer(
        f"<b>📌 Information about your profile 📌</b>\n\n"
        f"<b>├ 🖥 Username:</b> @{username}\n"
        f"<b>├ 🧍‍♂️ Name:</b> {firstname} {lastname}\n"
        f"<b>├ 🆔 ID:</b> {user_id}\n"
        f"<b>├ 🔓 Premium:</b> {"Active" if premium else "No Active"}\n"
        f"<b>└ 👥 Total referal:</b> {refer_count.refer_count}\n\n"
        f"<b> 🔗 Referal Link:</b> <code>{referal_link}</code>"
    )
    await message.delete()
