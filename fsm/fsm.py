from aiogram.fsm.state import State, StatesGroup


class SubChanel(StatesGroup):
    title = State()
    url = State()


class DeleteChanel(StatesGroup):
    url = State()


class BroadcastMessage(StatesGroup):
    message = State()
    button = State()
    url = State()
