from aiogram import Router, F
from aiogram.types import (Message, BufferedInputFile)
from loguru import logger
from keyboards.keyboards import (main_kb,admin_kb,fsm_button,broadcast_button)
from config.config import bot, settings
from db.dao import get_all_users, add_chanel, delete_chanel
from utils.utils import is_channel_valid, broadcast_send
from fsm.fsm import SubChanel, DeleteChanel, BroadcastMessage
from aiogram.fsm.context import FSMContext
import json

router = Router()



@router.message(lambda message: message.text == "🧍‍♂️ USER INFO" and message.from_user.id == settings.ADMIN_ID)
async def user_info(message: Message):
    try:
        # Получаем всех пользователей из базы
        all_users = await get_all_users()
        # Преобразуем пользователей в JSON-строку
        users_json = json.dumps(all_users, indent=4)

        # Создаем файл из строки
        data = BufferedInputFile(
            file=users_json.encode("utf-8"), filename="users_data.json"
        )

        # Отправляем файл
        await message.answer_document(document=data)

    except Exception as e:
        # Работаем с ошибками
        await message.answer(f"Произошла ошибка: {str(e)}")

@router.message(lambda message: message.text == "❌ ОТМЕНА")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено. Возвращаюсь в главное меню.", reply_markup = main_kb(message.from_user.id))

@router.message(lambda message: message.text == "✅ ADD CHANEL SUB" and message.from_user.id == settings.ADMIN_ID)
async def add_chanel_sub(message: Message, state: FSMContext):
    await state.clear()  # Очищаем предыдущее состояние
    await state.set_state(SubChanel.title)
    await message.answer("Введите заголовок канала:", reply_markup=fsm_button())


@router.message(SubChanel.title)
async def add_chanel_sub_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)  # Сохраняем заголовок канала
    await state.set_state(SubChanel.url)  # Переход к следующему шагу
    await message.answer(
        "Введите ссылку на канал (например, @example или https://t.me/example):",
        reply_markup=fsm_button(),
    )

@router.message(SubChanel.url)
async def add_chanel_sub_url(message: Message, state: FSMContext, bot):
    channel_url = message.text.strip()  # Убираем лишние пробелы
    # Проверяем корректность и существование канала
    if not await is_channel_valid(channel_url, bot):
        await message.answer(
            "Указанный канал не найден. Проверьте правильность ссылки и попробуйте снова.",
            reply_markup=fsm_button(),
        )
        return  # Не продолжаем дальше

    # Если канал существует, сохраняем полученные данные
    await state.update_data(url=channel_url)
    fsm_chanel = await state.get_data()
    title = fsm_chanel.get("title")
    url = fsm_chanel.get("url")

    await add_chanel(title=title, url=url)  # Добавляем канал в базу данных

    # Завершаем процесс
    await state.clear()
    await message.answer(
        text=f"Канал успешно добавлен в базу данных:\n\n**Заголовок:** {title}\n**Ссылка:** {url}",
        reply_markup=main_kb(message.from_user.id),
    )

@router.message(lambda message: message.text == "❌ DEL CHANEL SUB" and message.from_user.id == settings.ADMIN_ID)
async def del_chanel_sub(message: Message, state: FSMContext):
    await state.clear()  # Очищаем предыдущее состояние
    await state.set_state(DeleteChanel.url)
    await message.answer("Введите url канала:", reply_markup=fsm_button())


@router.message(DeleteChanel.url)
async def del_chanel_sub_url(message: Message, state: FSMContext, bot):
    channel_url = message.text.strip()  # Убираем лишние пробелы
    if not await delete_chanel(url=channel_url):
        await message.answer(
            "Канал не найден в базе данных. Проверьте правильность ссылки и попробуйте снова.",
            reply_markup=fsm_button(),
        )
        return  # Не продолжаем дальше
    # Если канал существует, удаляем его из базы
    await message.answer(
        text=f"Канал успешно удален из базы данных.",
        reply_markup=main_kb(message.from_user.id),
    )
    # Завершаем процесс
    await state.clear()


# Обработка команды и начало процесса рассылки
@router.message(F.text == "📩 BROADCAST MESSAGE")
async def broadcast_message(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BroadcastMessage.message)
    await message.answer(
    "📢 Пожалуйста, отправьте сообщение для рассылки!\n\n"
    "Можно использовать:\n"
    "- Текст 🖊️\n"
    "- Фото 🖼️\n"
    "- Видео 🎥\n\n"
    "Вы также можете добавить опциональную подпись к вашему содержимому.\n\n"
    "👉 Как только вы будете готовы, просто отправьте файл или сообщение.",
    reply_markup=fsm_button(),
)


@router.message(BroadcastMessage.message)
async def broadcast_message_text(message: Message, state: FSMContext):
    await state.update_data(message=message)
    await state.set_state(BroadcastMessage.button)
    await message.answer(
    "🔘 Хотите добавить кнопку к сообщению?\n\n"
    "Напишите заголовок для кнопки ниже 👇\n\n"
    "➡️ Если кнопка не нужна, просто пропустите этот шаг.",
    reply_markup=broadcast_button(),
)


@router.message(BroadcastMessage.button)
async def broadcast_message_button(message: Message, state: FSMContext):
    await state.update_data(button=message)
    await state.set_state(BroadcastMessage.url)
    await message.answer(
    "🔗 Хотите добавить ссылку к сообщению?\n\n"
    "Введите ссылку для перехода ниже 👇\n\n"
    "➡️ Если ссылка не нужна, просто пропустите этот шаг.",
    reply_markup=broadcast_button(),
)


@router.message(BroadcastMessage.url)
async def broadcast_message_url(message: Message, state: FSMContext):
    # Сохраняем переданный URL в состояние
    await state.update_data(url=message)
    
    # Получаем данные из состояния
    data = await state.get_data()
    content_type = data.get("message").content_type
    broadcast_message = data.get("message")
    button = data.get("button")
    url = data.get("url")
    
    # Получаем всех пользователей из базы
    user_data = await get_all_users()

    # Отправляем сообщение с прогрессом
    progress_message = await message.answer(
        "➖ Инициализация рассылки... ➖\n\n"
        "✅ Успешно доставлено: <b>0</b>\n"
        "❌ Не доставлено: <b>0</b>\n\n"
        "📤 Прогресс: <b>0%</b>"
    )

    # Запускаем процесс рассылки
    good, bad = await broadcast_send(
        users=user_data,
        message=broadcast_message,
        content_type=content_type,
        button=button,
        url=url,
        progress_message=progress_message
    )
    await progress_message.delete()
    # Отправляем финальное сообщение об окончании рассылки
    await message.answer(
        f"➖ РАССЫЛКА ЗАВЕРШЕНА ➖\n\n"
        f"✅ Успешно доставлено: <b>{good}</b> пользователей.\n"
        f"❌ Не удалось доставить: <b>{bad}</b> пользователей.\n\n"
        f"🔄 Выберите дальнейшее действие:",
        reply_markup=admin_kb()
    )
    # Очищаем состояние
    await state.clear()


@router.message(
    lambda message: message.text == "⚙️ ADMIN PANEL"
    and message.from_user.id == settings.ADMIN_ID
)
async def admin_panel(message: Message):
    panel_admin = await message.answer(text="ADMIN PANEL OPEN", reply_markup=admin_kb())
    await message.delete()


@router.message(F.text == "⬅️ BACK TO MAIN MENU")
async def admin_panel_back(message: Message):
    panel_admin_back = await message.answer(
        text="BACK TO MAIN MENU", reply_markup=main_kb(user_id=message.from_user.id)
    )
    await message.delete()
