from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUser,
    KeyboardButtonRequestChat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from config.config import settings

ADMIN_ID = settings.ADMIN_ID


def main_kb(user_id: int):
    buttons = [
        [
            KeyboardButton(
                text="👨‍🦰 ID USER",
                request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False),
            ),
            KeyboardButton(
                text="🤖 ID BOT",
                request_user=KeyboardButtonRequestUser(request_id=2, user_is_bot=True),
            ),
        ],
        [
            KeyboardButton(
                text="👥 ID GROUP",
                request_chat=KeyboardButtonRequestChat(
                    request_id=3, chat_is_channel=False
                ),
            ),
            KeyboardButton(
                text="📢 ID CHANNEL",
                request_chat=KeyboardButtonRequestChat(
                    request_id=4, chat_is_channel=True
                ),
            ),
        ],
        [KeyboardButton(text="🆔 MY INFO")],
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="⚙️ ADMIN PANEL")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Нажмите необходимую кнопку",
    )

    return keyboard


def admin_kb():
    buttons = [
        [
            KeyboardButton(text="🧍‍♂️ USER INFO"),
            KeyboardButton(text="📩 BROADCAST MESSAGE"),
        ],
        [
            KeyboardButton(text="✅ ADD CHANEL SUB"),
            KeyboardButton(text="❌ DEL CHANEL SUB"),
        ],
        [KeyboardButton(text="⬅️ BACK TO MAIN MENU")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Нажмите необходимую кнопку",
    )
    return keyboard


def chanels_kb(kb: list):
    inline_keyboard = []
    for chanel in kb:
        inline_keyboard.append(
            [InlineKeyboardButton(text=chanel["title"], url=chanel["url"])]
        )
    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Проверить подписку", callback_data="check_subscription"
            )
        ]
    )
    # Создаем клавиатуру для каналов
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def fsm_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ ОТМЕНА")]], resize_keyboard=True
    )

def broadcast_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔜 ПРОПУСТИТЬ")],
            [KeyboardButton(text="❌ ОТМЕНА")]  
        ],
        resize_keyboard=True
    )
