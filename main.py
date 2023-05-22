import asyncio
import os
import uuid

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types, Router, F

TOKEN = '5884510329:AAFckFdz49eKVwP1QK7YAlpuBBGO6EvQnYY'  # Потрібно вказати свій токен бота

# Створення об'єкту бота та диспетчера
router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(router)

# Створення з'єднання з базою даних
engine = create_engine(conn_str)
Session = sessionmaker(bind=engine)
session = Session()

# Клас для збереження посилань
Base = declarative_base()


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    original_link = Column(String)
    short_link = Column(String)
class FormStates(StatesGroup):
    WAITING_FOR_LINK = State()

# Клас для керування станами


# Обробник команди /start
@router.message(Command("start"))

async def start(message: types.Message, state: FSMContext):
    await state.set_state(FormStates.WAITING_FOR_LINK)
    await message.reply("Відправте посилання, яке потрібно скоротити.")


# Обробник отримання посилання
@router.message(FormStates.WAITING_FOR_LINK, F.text)
async def process_link(message: types.Message, state: FSMContext):
    original_link = message.text
    if original_link.startswith('http'):
        if session.query(Link).filter_by(user_id=message.from_user.id, original_link=original_link).all():
            await message.reply(f"Ви вже додавали такий лінк!")
            return
        short_link = str(uuid.uuid4())[:6]
        link = Link(original_link=original_link, short_link=short_link, user_id = message.from_user.id)
        session.add(link)
        session.commit()
        await state.clear()
        await message.reply(f"Посилання було скорочено. Його ID: {link.id}")
    await message.reply(f"Невірний формат посилання. Посилання повинно починатися з http:// або https://")


# Обробник команди /get_my_links
@router.message(Command('get_my_links'))
async def get_my_links(message: types.Message):
    user_id = message.from_user.id
    user_links = session.query(Link).filter_by(user_id=user_id).all()
    if user_links:
        response = "Ваші скорочені посилання:\n"
        for link in user_links:
            response += f"ID: {link.id}, Посилання: {link.original_link}\n"
    else:
        response = "Ви ще не додали жодного посилання."
    await message.reply(response)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
