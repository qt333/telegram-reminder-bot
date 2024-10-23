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

from database import DatetimeTask_DB

from utils import DateTask

from apscheduler.schedulers import SchedulerAlreadyRunningError


router = Router()

db = DatetimeTask_DB('db.db')


class NewTaskDate(StatesGroup):
    enter_taskName = State()
    enter_taskMsg = State()
    enter_taskDatetime = State()


@router.message(StateFilter(None), Command('taskdate'))
async def create_task(message: Message, state: FSMContext):
    # Устанавливаем пользователю состояние "выбирает название"
    await message.answer(text=f"Follow instruction below:\n\n <b>{MSG['newDateTask'][0]} </b>")
    data = await state.get_data()
    print(data)
    username = message.from_user.username
    user_id = message.from_user.id

    await db.create_db()
    await db.add_user(user_id, username)
    await db.create_userTaskTable(user_id)

    await state.set_state(NewTaskDate.enter_taskName)
    # await NewTaskDate.enter_taskName.set()

@router.message(NewTaskDate.enter_taskName)
async def create_task1(message: Message, state: FSMContext):
    # username = message.from_user.username
    user_id = message.from_user.id
    if not await db.taskName_exists(user_id,message.text):
        await state.update_data(taskName=message.text)
        await message.answer(f"<b>{MSG['newDateTask'][1]}</b>")
        # Устанавливаем пользователю состояние "выбирает название"
        data = await state.get_data()
        print(data)
        await state.set_state(NewTaskDate.enter_taskMsg)
    else:
        await message.answer(f"Task with name <b>'{message.text}'</b> already exists! Enter different name")

@router.message(NewTaskDate.enter_taskMsg)
async def create_task2(message: Message, state: FSMContext):
    await state.update_data(data={'taskMsg':message.text})
    await message.answer(f"{MSG['newDateTask'][2]}")
    # Устанавливаем пользователю состояние "выбирает название"
    data = await state.get_data()
    print(data)
    await state.set_state(NewTaskDate.enter_taskDatetime)

@router.message(NewTaskDate.enter_taskDatetime)
async def create_task3(message: Message, state: FSMContext):
    pattern = r'^\d{4} \d{1,2} \d{1,2} \d{1,2} \d{1,2} \d{1,2}$'
    if not re.findall(pattern, message.text):
        await message.answer(f"You must enter correct format!")
    else:
        if DateTask.time_valid(message.text):
            dt_friendly = DateTask.datetime_userFriendly(message.text)
            await state.update_data(data={'taskDatetime':message.text})
            data = await state.get_data()
            await state.clear()

            await message.answer(f"The datetask <b>'{data['taskName']}'</b> was created successfully ☑️")
            print(data)

            username = message.from_user.username
            user_id = message.from_user.id

            task_var = f'task_{int(time())}' + str(choice('abcdefghigpqtczxbnmvjkl'))
            taskScheduleJob = f"{task_var} = DateTask(username, data['taskName'], data['taskMsg'], data['taskDatetime'], {user_id})\n{task_var}.task_start()"
            await db.add_task(user_id, data['taskName'], data['taskMsg'], data['taskDatetime'], dt_friendly, taskScheduleJob)
            
            try:
                exec(taskScheduleJob)
            except SchedulerAlreadyRunningError:
                pass
            # await db.get_all_tasks(username)
            # print(tasks)
            del data
        else:
            await message.answer(f"You must enter a future datetime!")
        

    


