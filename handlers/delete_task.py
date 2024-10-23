from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart,Command,StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import DataBase, DatetimeTask_DB
from utils import TaskReminder

import re
from time import time
from random import choice

from handlers.tasks_list import show_list

router = Router()

db = DataBase('db.db')
db_dt = DatetimeTask_DB('db.db')

class DeleteTask(StatesGroup):
    enter_taskNumber = State()


@router.message(StateFilter(None), Command('delete'))
async def delete_task(message: Message, state: FSMContext):
    # Устанавливаем пользователю состояние "выбирает название"
    username = message.from_user.username
    user_id = message.from_user.id

    tasks_list = await show_list(message)
    if tasks_list:
        await message.answer(text=f"Write task number which your wanna delete:")
    else:
        # del data # UnboundLocalError: cannot access local variable 'data' where it is not associated with a value
        await state.clear()
        return False
    
    await state.set_state(DeleteTask.enter_taskNumber)
    # await NewTask.enter_taskName.set()

@router.message(DeleteTask.enter_taskNumber)
async def delete_task1(message: Message, state: FSMContext):
    # username = message.from_user.username
    user_id = message.from_user.id

    tasks_list = await db.get_all_tasks(user_id)
    tasksDate_list = await db_dt.get_all_tasks(user_id)
    # print(tasks_list, tasksDate_list)
    tasks_all = tasks_list + tasksDate_list
    # print('ALL:',tasks_all)

    taskN = int(message.text)
    if re.findall('^[0-9]*$', message.text) and taskN <= len(tasks_all):
        await state.update_data(taskN=taskN)
        data = await state.get_data()
        await state.clear()
        # print(data)

        taskName = tasks_all[data['taskN']-1]['taskName']

        #print(taskExecStopThread)
        # exec(taskExecStopThread) # Notworking NameError: name 'task_1711291649h' is not defined, need to make queue or somethig...
        if tasks_list and taskN <= len(tasks_list):
            await db.delete_task(user_id,taskName)
        elif tasksDate_list:
            await db_dt.delete_task(user_id,taskName)
        await message.answer(f"Task '{taskName}' was successfully deleted ☑️")

        # del data # UnboundLocalError: cannot access local variable 'data' where it is not associated with a value
    else:
        await message.answer(f"Task number is incorrect!")

@router.message(StateFilter(None), Command('delete_all'))
async def delete_task(message: Message, state: FSMContext):
    # username = message.from_user.username
    user_id = message.from_user.id

    tasks = await db.get_all_tasks(user_id)
    tasksdate = await db_dt.get_all_tasks(user_id)
    if tasks or tasksdate:   
        if tasks:
            await db.delete_all_tasks(user_id)
        if tasksdate:
            await db_dt.delete_all_tasks(user_id)
        await message.answer('All tasks were successfully deleted ☑️')
    else:
        task_list_empty = 'You currently have no tasks 😐\nWrite /task or /taskdate to create one'
        await message.answer(task_list_empty)

    
    
