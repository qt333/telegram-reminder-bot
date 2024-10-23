import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils import TaskReminder, DateTask
from database import DataBase, DatetimeTask_DB

from apscheduler.schedulers import SchedulerAlreadyRunningError


db = DataBase('db.db')
db_dt = DatetimeTask_DB('db.db')

async def restart_tasks():

    for user_id in await db.get_users_ids():
        # print(username)
        # Restart Periodic tasks
        try:
            for data in await db.get_all_tasks(user_id):
                # if data['taskExecThread']:
                exec(data['taskExecThread'])
                # elif data['taskScheduleJob']:
                #     exec(data['taskScheduleJob'])
                # print(data)
        except TypeError:
            pass
        
        # Restart Datetime tasks
        try:
            for data in await db_dt.get_all_tasks(user_id):
                # if data['taskExecThread']:
                exec(data['taskScheduleJob'])
                # elif data['taskScheduleJob']:
                #     exec(data['taskScheduleJob'])
                # print(data)
        except TypeError:
            pass
        except SchedulerAlreadyRunningError:
            pass

# if __name__ == "__main__":
#     asyncio.run(restart_tasks())
