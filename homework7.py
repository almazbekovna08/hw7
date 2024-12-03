import aiosmtplib, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from email.message import EmailMessage
from config1 import SMTP_USER, SMTP_PASSWORD, token
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio



inline_button = [
     [InlineKeyboardButton(text="Сообщение", callback_data="message")],
     [InlineKeyboardButton(text="Аудио", callback_data="audio")],
     [InlineKeyboardButton(text="Изображение", callback_data="picture")],
     [InlineKeyboardButton(text="Видео", callback_data="video")]
]

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=inline_button)



SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = SMTP_USER
SMTP_PASSWORD = SMTP_PASSWORD

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=token)
dp = Dispatcher()

async def send_email(to_emain, message_body):
    message = EmailMessage()
    message.set_content(message_body)
    message['Subject'] = 'Сообщение от бота'
    message['From'] = SMTP_USER
    message['To'] = to_emain

    try:
        logging.info(f'Отправка email на {to_emain}')
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD
        )
        logging.info("Успешно отправлена")
    except Exception as e:
        logging.info("Ошибка", e)

user_email = None

@dp.message(CommandStart())
async def start(message:types.Message):
    await message.answer("Привет, этот бот может отправить любое сообщение на введенный email📫. \nВведите email, на который хотите отправить то или иное сообщение✨.")

@dp.message(lambda message: "@gmail.com" in message.text)
async def email(message:types.Message):
    global user_email 
    user_email = message.text
    await message.answer(f"Я отправлю сообщение на адрес {user_email}. Можете использовать команду /variants, чтобы рассмотреть виды сообщение🙌🙌")

@dp.message(Command('variants'))
async def keyboard(message:types.Message):
    await message.answer("Выберите что именно вы хотите отправить:", reply_markup=inline_keyboard)


@dp.callback_query(F.data == 'message')
async def cmd_message(callback: types.CallbackQuery):
    await callback.answer("Вы выбрали отправить сообщение")
    await callback.message.answer('Введите сообщение, которое хотите отправить📫.')
@dp.message()
async def get_message(message: types.Message):
    email_message = message.text 
    global user_email
    if user_email:
        await send_email(user_email, email_message) 
        await message.answer("Сообщение успешно отправлено!🙌")
    else:
        await message.answer("Ошибка: email не указан❌.")

@dp.callback_query(F.data == 'audio')
async def cmd_audio(callback: types.CallbackQuery):
    await callback.answer("Вы выбрали отправить аудиофайл")
    await callback.message.answer('Введите аудиофайл, который хотите отправить(можно ссылкой)📫.')

@dp.message()
async def get_audio(message: types.Message):
    email_message = message.audio 
    global user_email
    if user_email:
        await send_email(user_email, email_message)
        await message.answer("Аудиофайл успешно отправлен!🙌")
    else:
        await message.answer("Ошибка: email не указан❌.")

@dp.callback_query(F.data == 'picture')
async def cmd_picture(callback: types.CallbackQuery):
    await callback.answer("Вы выбрали отправить изображение")
    await callback.message.answer('Введите изображение, которое хотите отправить(можно ссылкой)📫.')

@dp.message()
async def get_picture(message: types.Message):
    email_message = message.photo
    global user_email
    if user_email:
        await send_email(user_email, email_message)
        await message.answer("Изображение успешно отправлено!🙌")
    else:
        await message.answer("Ошибка: email не указан❌.")

@dp.callback_query(F.data == 'video')
async def cmd_video(callback: types.CallbackQuery):
    await callback.answer("Вы выбрали отправить видео")
    await callback.message.answer('Введите видео, которое хотите отправить(можно ссылкой)📫.')

@dp.message()
async def get_video(message: types.Message):
    email_message = message.video
    global user_email
    if user_email:
        await send_email(user_email, email_message) 
        await message.answer("Видео успешно отправлено!🙌")
    else:
        await message.answer("Ошибка: email не указан❌.")

@dp.message(lambda message: '@' not in message.text)
async def error(message:types.Message):
    await message.answer("Пожалуйста введите правильный адрес почты")

async def main():
        await dp.start_polling(bot)

if __name__=='__main__':
    try:
         asyncio.run(main())
    except KeyboardInterrupt:
        print('Выход')


