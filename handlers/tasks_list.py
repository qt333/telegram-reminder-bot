from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from message import MESSAGES as MSG
from aiogram.filters import CommandStart,Command,StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from database import DataBase, DatetimeTask_DB
from utils import TaskReminder

import re
from time import time
from random import choice

router = Router()

db = DataBase('db.db')
db_dt = DatetimeTask_DB('db.db')

@router.message(Command('list'))
async def show_list(message: Message):
    username = message.from_user.username
    user_id = message.from_user.id

    await db.create_db()
    await db.add_user(user_id, username)

    await db.create_userTaskTable(user_id)
    await db_dt.create_userTaskTable(user_id)

    task_list_answer = 'Here is your tasks list 🗒:\n\n\t\t\t\t\tName\t\t\t     Time\n\n'
    task_list_empty = 'You currently have no tasks 😐\nWrite /task or /taskdate to create one'
    
    tasks_list = await db.get_all_tasks(user_id)
    tasksDate_list = await db_dt.get_all_tasks(user_id)
    # print(tasks_list, tasksDate_list)

    if tasks_list or tasksDate_list:
        datetask_start_num = len(tasks_list) + 1
        datetask_end_num = datetask_start_num + len(tasksDate_list)
        for i,task in enumerate(tasks_list):
            task_list_answer += f'''{i+1}. "{task['taskName']}" - {task['taskPeriod']}\n'''
        for i,task in list(zip(range(datetask_start_num,datetask_end_num),tasksDate_list)):
            task_list_answer += f'''{i}. "{task['taskName']}" - {task['taskDatetimeFriendly']}\n'''
        tasks_exists = True
    else:
        task_list_answer = task_list_empty
        tasks_exists = False

    await message.answer(task_list_answer)

    return tasks_exists

