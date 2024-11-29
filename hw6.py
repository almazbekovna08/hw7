from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import sqlite3
from config import token
import asyncio

bot = Bot(token=token)

ADMIN_ID = [6120470758]


connection = sqlite3.connect("mailing.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL UNIQUE,
chat_id INTEGER NOT NULL UNIQUE,
full_name TEXT,
status_admin BOOLEAN DEFAULT FALSE
)
""")

class Register(StatesGroup):
    full_name = State()


class Mailing(StatesGroup):
    text = State()

class AddAdmin(StatesGroup):
    is_admin_user_id = State()

router = Router()

def register_user(user_id, chat_id, full_name, status_admin=False):
    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, chat_id, full_name, status_admin) VALUES (?, ?, ?, ?)
    """, (user_id, chat_id, full_name, status_admin))
    connection.commit()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        await message.answer("Вы уже зарегистрированы. \nЕсли вы админ используйте команды /mailing или /add_admin или /users")
    else:
        await message.answer("Добро пожаловать! Пожалуйста, введите ваше полное имя (фамилию и имя!):")
        await state.set_state(Register.full_name)

@router.message(Register.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    full_name = message.text
    user_id = message.from_user.id
    chat_id = message.chat.id
    status_admin = user_id in ADMIN_ID

    register_user(user_id, chat_id, full_name, status_admin)
    await message.answer(f"Спасибо, {full_name}! Вы успешно зарегистрированы.\nЕсли вы админ используйте команды /mailing или /add_admin или /users")
    await state.clear()
    
@router.message(Command('mailing'))
async def command_mailing(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        for i in ADMIN_ID:
            await bot.send_message(i, 'Введите сообщение для рассылки')
            await state.set_state(Mailing.text)
    else:
        await message.reply("Эта команда доступна только администраторам.")
        


@router.message(Mailing.text)
async def mailing(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    text = data['text']
    cursor.execute("SELECT chat_id FROM users")
    users = cursor.fetchall()
    for i in users:
        chat_id = i[0]  
        await bot.send_message(chat_id, f'Рассылка: {text}')
        await message.answer("Рассылка окончена. \nЕсли вы админ используйте команды /add_admin или /users")
        await Mailing.text.finish()



@router.message(Command("users"))
async def users_command(message: types.Message):
    if message.from_user.id in ADMIN_ID:
            cursor.execute("SELECT full_name, user_id, status_admin FROM users")
            users = cursor.fetchall()
            await message.reply(f"Список пользователей:\n{users}. \nЕсли вы админ используйте команды /mailing или /add_admin")
    else:
            await message.reply("Эта команда доступна только администраторам.")

@router.message(Command("add_admin"))
async def add_admin_command(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        await message.reply("Введите ID пользователя, которого хотите сделать администратором:")
        await AddAdmin.is_admin_user_id.state.set_state() # не сработало, выдало ошибку AttributeError: 'str' object has no attribute 'set_state'
    else:
        await message.reply("Эта команда доступна только администраторам.")


@router.message(AddAdmin.is_admin_user_id) 
async def process_add_admin(message: types.Message, state: FSMContext):
        user_id = int(message.text)
        cursor.execute("UPDATE users SET status_admin = TRUE WHERE user_id = ?", (user_id,))
        connection.commit()

        if cursor.rowcount == 0: 
            await message.reply("Пользователь с указанным ID не найден в базе данных.")
        else:
            await message.reply(f"Пользователь с ID {user_id} успешно назначен администратором.")
    

@router.message()
async def echo(message: types.Message):
    await message.answer('Я вас не понял')

async def main():
        dp = Dispatcher()
        dp.include_router(router)
        await dp.start_polling(bot)

if __name__=='__main__':
    try:
         asyncio.run(main())
    except KeyboardInterrupt:
        print('Выход')