import asyncio
import logging
import sys
from os import getenv
import json

from dotenv import load_dotenv

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Bot, Dispatcher, Router, types,F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command,StateFilter

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils import TaskReminder

from handlers import create_task
from handlers import tasks_list
from handlers import delete_task
from handlers import create_datetask

from database import DataBase
from message import MESSAGES as MSG

from on_strartup.restart_tasks import restart_tasks
# Bot token can be obtained via https://t.me/BotFather

load_dotenv()

TOKEN = getenv('TOKEN')

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

db = DataBase('db.db')

@dp.message(CommandStart())
async def start(message: types.Message):
    # метод row позволяет явным образом сформировать ряд
    # из одной или нескольких кнопок. Например, первый ряд
    # будет состоять из двух кнопок...
    name = message.from_user.full_name
    username = message.from_user.username
    user_id = message.from_user.id
    await db.create_userTaskTable(user_id)
    await db.add_user(user_id, username)

    kb = [
        [
            types.KeyboardButton(text="/menu"),
            types.KeyboardButton(text="/help")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True)
    hello_msg = f'''Hi, <b>{name}</b>! I'm a Reminder Bot ✋🙂.\n\nWrite down /help to see list of available commands.'''
    await message.answer(f"{hello_msg}\n\nSelect command:", reply_markup=keyboard)

@dp.message(Command("menu"))
async def menu_handler(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # метод row позволяет явным образом сформировать ряд
    # из одной или нескольких кнопок. Например, первый ряд
    # будет состоять из двух кнопок...
    builder.row(
        types.KeyboardButton(text="/task"),
        types.KeyboardButton(text="/taskdate"),
        types.KeyboardButton(text="/taskhelp")
    )
    # ... второй из одной ...
    builder.row(types.KeyboardButton(
        text="/list",
        )
    )
    # ... а третий снова из двух
    builder.row(
        types.KeyboardButton(
            text="/delete",
            
        ),
        types.KeyboardButton(
            text="/delete_all",
            
        )
    )

    builder.row(
        types.KeyboardButton(text="/help"),
        types.KeyboardButton(text="/donate")
    )
    # WebApp-ов пока нет, сорри :(

    await message.answer(
        "Select action:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    # builder = ReplyKeyboardBuilder()
    # # метод row позволяет явным образом сформировать ряд
    # # из одной или нескольких кнопок. Например, первый ряд
    # # будет состоять из двух кнопок...
    # builder.row(
    #     types.KeyboardButton(text="Запросить геолокацию"),
    #     types.KeyboardButton(text="Запросить контакт")
    # )

    # await message.answer(
    #     "Выберите действие:",
    #     reply_markup=builder.as_markup(resize_keyboard=True),
    # )
    await message.answer(MSG['help'])


@dp.message(Command("taskhelp"))
async def create_task_help(message: types.Message):
    await message.answer(MSG['newTaskHelp'])


@dp.message(Command("donate"))
async def create_task_help(message: types.Message):
    await message.answer(MSG['support'])

# @dp.callback_query(F.data == "random_value")
# async def compute(callback: types.CallbackQuery):
#     await callback.message.answer('str(randint(1, 10))')
#     await callback.answer()


#inline buttons in chat
# @dp.message(Command("random"))
# async def cmd_random(message: types.Message):
#     builder = InlineKeyboardBuilder()
#     builder.row(types.InlineKeyboardButton(
#         text="Нажми меня",
#         callback_data='random_value')
#     )
#     builder.row(types.InlineKeyboardButton(
#         text="Нажми меня",
#         callback_data='random_value')
#     )
#     builder.row(types.InlineKeyboardButton(
#         text="Нажми меня",
#         callback_data='random_value')
#     )

    
#     await message.answer(
#         "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
#         reply_markup=builder.as_markup()
#     )


# task_list = []
#create task 1st attempt sipmle with thread
# @dp.message()
# async def echo_handler(message: types.Message) -> None:
#     """
#     Handler will forward receive a message back to the sender

#     By default, message handler will handle all message types (like a text, photo, sticker etc.)
#     """
#     global task_list
#     try:
#         if message.text == 'create task':
#             await message.answer("Write down new task info with 2 white spaces separate: \n\n \
#                 Task:'task name'  'message'  'period' \n\n \
# Example: 'Task: Drink coffee  Hey buddy, its time to drink some coffee  5 min")
#         if message.text.lower().startswith('task'):
#             print(message.text[5:].split('  '))
#             msg_list = message.text[5:].split('  ')
#             task_name = msg_list[0]
#             task_msg = msg_list[1]
#             task_period = msg_list[2]
#             task_list.append({'taskName':task_name,
#             'taskPeriod':task_period})
#             newTask = TaskReminder(task_name,task_msg,task_period, 'en')
#             newTask.launch_task()
#         if message.text == 'list':
#             for task in task_list:
#                 list_msg = ''.join(f"{task['taskName']} {task['taskPeriod']}\n")
#             await message.answer(list_msg)
#         # Send a copy of the received message
#         # await message.send_copy(chat_id=message.chat.id)
#         # print(message.text)
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    
    await db.create_db()
    await restart_tasks()

    dp.include_router(create_task.router)
    dp.include_router(create_datetask.router)
    dp.include_router(tasks_list.router)
    dp.include_router(delete_task.router)
    # And the run events dispatching
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
