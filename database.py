import asyncio
import aiosqlite
from sqlite3 import OperationalError,IntegrityError
from utils import Connect
from ast import literal_eval


class DataBase:
    """Async DB IMPLEMENTATION"""
    def __init__(self, db_file) -> None:
        self.db_file = db_file
    
    async def create_db(self):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users
                    ([user_id] integer PRIMARY KEY, [username] TEXT)
                    ''')

    async def execute(self, query):
        """select query
        """
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
                async with conn.execute(query) as cursor:
                    result = await cursor.fetchall()
                    return result

    async def add_user(self, user_id, username):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            try:
                await conn.execute(f'''
                                    INSERT INTO users (user_id, username)
                                    SELECT {user_id}, "{username}"
                                    WHERE NOT EXISTS (
                                        SELECT 1 FROM users WHERE user_id = {user_id} OR username = "{username}"
                                    )''')
            except Exception as e:
                print(e)


    async def create_userTaskTable(self, user_id: str):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS '{user_id}'
                    ([taskName] TEXT PRIMARY KEY,
                    [taskExecThread] TEXT,
                    [taskExecStopThread] TEXT,
                    [taskMsg] TEXT,
                    [taskPeriod] TEXT,
                    [taskPeriodParsed] integer,
                    [taskEndTimestamp] integer)
                    ''')


    async def get_users_ids(self) -> list[str]:
        ll = []
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            async with conn.execute(f'''select user_id from users''') as cursor:
                async for row in cursor:
                    ll.append(row[0])
                return ll
                # rows = await cursor.fetchall()
                # print(rows)
                # return rows

    async def get_user_id(self, user_id):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            async with conn.execute(f'''select * from users where user_id="{user_id}"''') as cursor:
                row = await cursor.fetchone()
                print(row)

    async def user_exists(self, user_id):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            async with conn.execute(f'''select * from users where user_id="{user_id}"''') as cursor:
                result = await cursor.fetchmany(2)
                # print(row)
            if not bool(len(result)):
                return False
            else: return True

    async def taskName_exists(self, user_id, taskName):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            try:
                async with conn.execute(f'''select * from "{user_id}" where taskName="{taskName}"''') as cursor:
                    result = await cursor.fetchone()
                    if result:
                        return True
                    else: return False
            except OperationalError:
                print('No such table')
                return False
    

    async def get_all_tasks(self, user_id) -> list[dict]:
        '''
        Return all tasks list contains dict for each task.\n\n
        {'taskName': 'ASDASD',\n
         'taskExecThread': "task_1711291649h = TaskReminder(data['taskName'],data['taskMsg'],data['taskPeriodParsed'],data['taskEndTimestamp'],chat_id=752683417)\ntask_1711291649h.launch_task()",\n
         'taskExecStopThread': 'task_1711291649h.stop_task()',\n
         'taskMsg': 'aaaaaaaaaaaaa',\n
         'taskPeriod': '1m',\n
         'taskPeriodParsed': 60,\n
         'taskEndTimestamp': 1711291709}'''
        tasks_list = []
        task_dict = {}

        def check_type(value, value_type):
                    # to check if value is of certain type
                    try:
                        val = str(value)
                        return isinstance(literal_eval(val), value_type)
                    except SyntaxError:
                        return False
                    except ValueError:
                        return False

        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            try:
                async with conn.execute(f'''select * from "{user_id}"''') as cursor:
                    async for task in cursor:
                        # task_list.append(task)
                        fieldnames = [f[0] for f in cursor.description]
                        # values = await cursor.fetchone()
                        values = list(task)
                        for v in range(len(values)):
                            if not (isinstance(values[v], int) or isinstance(values[v], float)):
                                isList = check_type(values[v], list)
                                isTuple = check_type(values[v], tuple)
                                isDict = check_type(values[v], dict)
                                if isList or isTuple or isDict:
                                    values[v] = literal_eval(values[v])
                        for i in range(len(fieldnames)):
                            task_dict[fieldnames[i]] = values[i]
                        # [print(task_dict)]
                        tasks_list.append(task_dict)
                        task_dict = {}
                # print(tasks_list)
                return tasks_list
            except OperationalError:
                print('No such table')
                return 0

    async def add_task(self,user_id,taskName,taskExecThread,taskExecStopThread,taskMsg,taskPeriod,taskPeriodParsed,taskEndTimestamp):
        """
        ([taskName] TEXT PRIMARY KEY,\n
                    [taskExecThread] TEXT,\n
                    [taskExecStopThread] TEXT,\n
                    [taskMsg] TEXT,\n
                    [taskPeriod] TEXT,\n
                    [taskPeriodParsed] integer,\n
                    [taskEndTimestamp] integer)"""
        
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            try:
                await conn.execute(f'''insert into "{user_id}" values("{taskName}","{taskExecThread}","{taskExecStopThread}","{taskMsg}","{taskPeriod}",{taskPeriodParsed},{taskEndTimestamp})''')
            except IntegrityError:
                print('task already exists! Change taskName!')
        

    # Delete All Records
    async def delete_all_tasks(self, user_id):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute(f'''delete from "{user_id}"''')
    
    async def delete_task(self, user_id, taskName):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute(f'''delete from "{user_id}" where taskName="{taskName}"''')

    async def update_task(self, user_id, taskName, taskNameNew, taskMsg, taskPeriod):
        #TODO implenent feature
        list_to_update = list([taskNameNew, taskMsg, taskPeriod])
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute(f'''update "{user_id}" set taskName=?,taskMsg=?,taskPeriod=? where taskName="{taskName}"''',
            tuple(list_to_update))

class DatetimeTask_DB(DataBase):
    def __init__(self, db_file) -> None:
        super().__init__(db_file)

    async def create_userTaskTable(self, user_id: str):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS '{user_id}_date'
                    ([taskName] TEXT PRIMARY KEY,
                    [taskMsg] TEXT,
                    [taskDatetime] TEXT,
                    [taskDatetimeFriendly] TEXT,
                    [taskScheduleJob] TEXT)
                    ''')

    async def add_task(self, user_id, taskName, taskMsg, taskDatetime, taskDatetimeFriendly, taskScheduleJob):
        """
            ([taskName] TEXT PRIMARY KEY,
            [taskMsg] TEXT,
            [taskDatetime] TEXT,
            [taskDatetimeFriendly] TEXT,
            [taskScheduleJob] TEXT)
        """
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            try:
                await conn.execute(f'''insert into '{user_id}_date' values("{taskName}","{taskMsg}","{taskDatetime}","{taskDatetimeFriendly}","{taskScheduleJob}")''')
            except IntegrityError:
                print('task already exists! Change taskName!')
    
    async def taskName_exists(self, user_id, taskName):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            try:
                async with conn.execute(f'''select * from '{user_id}_date' where taskName="{taskName}"''') as cursor:
                    result = await cursor.fetchone()
                    if result:
                        return True
                    else: return False
            except OperationalError:
                print('No such table')
                return False
    
    async def get_all_tasks(self, user_id) -> list[dict]:
        '''
        Return all tasks list contains dict for each task.\n\n
        ([taskName] TEXT PRIMARY KEY,
        \n[taskMsg] TEXT,
        \n[taskDatetime] TEXT,
        \n[taskScheduleJob] TEXT)'''
        tasks_list = []
        task_dict = {}

        def check_type(value, value_type):
                    # to check if value is of certain type
                    try:
                        val = str(value)
                        return isinstance(literal_eval(val), value_type)
                    except SyntaxError:
                        return False
                    except ValueError:
                        return False

        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            try:
                async with conn.execute(f'''select * from "{user_id}_date"''') as cursor:
                    async for task in cursor:
                        # task_list.append(task)
                        fieldnames = [f[0] for f in cursor.description]
                        # values = await cursor.fetchone()
                        values = list(task)
                        for v in range(len(values)):
                            if not (isinstance(values[v], int) or isinstance(values[v], float)):
                                isList = check_type(values[v], list)
                                isTuple = check_type(values[v], tuple)
                                isDict = check_type(values[v], dict)
                                if isList or isTuple or isDict:
                                    values[v] = literal_eval(values[v])
                        for i in range(len(fieldnames)):
                            task_dict[fieldnames[i]] = values[i]
                        # [print(task_dict)]
                        tasks_list.append(task_dict)
                        task_dict = {}
                # print(tasks_list)
                return tasks_list
            except OperationalError:
                print('No such table')
                return 0

    async def delete_task(self, user_id, taskName):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute(f'''delete from '{user_id}_date' where taskName="{taskName}"''')

    # Delete All Records
    async def delete_all_tasks(self, user_id):
        async with aiosqlite.connect(f"file:{self.db_file}?cache=shared",uri=True,isolation_level=None) as conn:
            await conn.execute(f'''delete from "{user_id}_date"''')

# async def main():
#     db = DataBase('db.db')
#     await db.create_db()
#     # await db.add_user(454355,'325pitix')
#     # await db.add_user(45435345,'34pitix')
#     # await db.add_user(45435523425,'234pitix')
#     # await db.add_user(45435524,'1pitix')
#     # await db.create_userTaskTable('dima34')
#     await db.add_task('325pitix', 'cofee46','thread','stoptread','time to drink cofe', '5 min',35, 17586768)
#     await db.add_task('34pitix', 'cofee4','thread','stoptread','time to drink cofe', '5 min',35, 17586768)
#     await db.add_task('234pitix', 'cofeed465','thread','stoptread','time to drink cofe', '5 min',35, 17586768)
#     await db.add_task('1pitix', 'cofee1465','thread','stoptread','time to drink cofe', '5 min',35, 17586768)

#     # usernames = await db.get_user_ids()
#     # print(usernames)
#     # for username in usernames:
#     #     await db.create_userTaskTable(username)

#     # await db.delete_all_tasks('dima34')
#     # if await db.taskName_exists('dimad','cofed'):
#     #     print(True)

# if __name__ == "__main__":
#     asyncio.run(main())