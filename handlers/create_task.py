import re
from time import time
from random import choice

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

from database import DataBase

from utils import TaskReminder, DateTask


router = Router()

db = DataBase('db.db')


async def time_parse(time_msg):
    if time_msg:
        try:
            time_value_parsed = int(re.sub('[a-zA-Zа-яА-Я]', '', time_msg).split()[0])
        except:
            time_value_parsed = 0
            pass 
        time_unit_parsed = re.sub('[0-9]', '', time_msg).lower()
        if any(i in time_unit_parsed for i in ['minute', 'minutes','min', 'm', 'мин','минут','минута','м','минуток']):
            taskPeriodParsed = time_value_parsed * 60
        elif any(i in time_unit_parsed for i in ['hour', 'h','hours','час','часов','ч','часик']):
            taskPeriodParsed = time_value_parsed * 60 * 60
        elif any(i in time_unit_parsed for i in ['day', 'days','d','день','денек','д','дней']):
            taskPeriodParsed = time_value_parsed * 60 * 60 * 24
        else:
            taskPeriodParsed = 15
        taskEndTimestamp = int(time()) + taskPeriodParsed
        return taskPeriodParsed,taskEndTimestamp


class NewTask(StatesGroup):
    enter_taskName = State()
    enter_taskMsg = State()
    enter_taskPeriod = State()
# новый импорт!

@router.message(StateFilter(None), Command('task'))
async def create_task(message: Message, state: FSMContext):
    # Устанавливаем пользователю состояние "выбирает название"
    await message.answer(text=f"Follow instruction below:\n\n <b>{MSG['newTask'][0]} </b>")
    data = await state.get_data()
    print(data)
    username = message.from_user.username
    user_id = message.from_user.id

    await db.create_db()
    await db.add_user(user_id, username)
    await db.create_userTaskTable(user_id)

    await state.set_state(NewTask.enter_taskName)
    # await NewTask.enter_taskName.set()

@router.message(NewTask.enter_taskName)
async def create_task1(message: Message, state: FSMContext):
    # username = message.from_user.username
    user_id = message.from_user.id
    if not await db.taskName_exists(user_id,message.text):
        await state.update_data(taskName=message.text)
        await message.answer(f"<b>{MSG['newTask'][1]}</b>")
        # Устанавливаем пользователю состояние "выбирает название"
        data = await state.get_data()
        print(data)
        await state.set_state(NewTask.enter_taskMsg)
    else:
        await message.answer(f"Task with name <b>'{message.text}'</b> already exists! Enter different name")

@router.message(NewTask.enter_taskMsg)
async def create_task2(message: Message, state: FSMContext):
    await state.update_data(data={'taskMsg':message.text})
    await message.answer(f"<b>{MSG['newTask'][2]}</b>")
    # Устанавливаем пользователю состояние "выбирает название"
    data = await state.get_data()
    print(data)
    await state.set_state(NewTask.enter_taskPeriod)

@router.message(NewTask.enter_taskPeriod)
async def create_task3(message: Message, state: FSMContext):
    await state.update_data(data={'taskPeriod':message.text})
    # Устанавливаем пользователю состояние "выбирает название"
    data = await state.get_data()
    await message.answer(f"The task <b>'{data['taskName']}'</b> was created successfully ☑️")
    print(data)
    #add new task to DB:
    username = message.from_user.username
    user_id = message.from_user.id
    taskPeriodParsed,taskEndTimestamp = await time_parse(data['taskPeriod'])
    data.update({'taskPeriodParsed':taskPeriodParsed})
    data.update({'taskEndTimestamp':taskEndTimestamp})
    task_var = f'task_{int(time())}' + str(choice('abcdefghigpqtczxbnmvjkl'))
    taskExecThread = f"{task_var} = TaskReminder(data['taskName'],data['taskMsg'],data['taskPeriodParsed'],data['taskEndTimestamp'],username,chat_id={user_id})\n{task_var}.launch_task()"
    taskExecStopThread = f'{task_var}.stop_task()'

    
    await db.add_task(user_id, data['taskName'],taskExecThread,taskExecStopThread,data['taskMsg'],data['taskPeriod'],taskPeriodParsed,taskEndTimestamp)
    exec(taskExecThread)
    # await db.get_all_tasks(username)
    # print(tasks)
    del data
    await state.clear()

    


