import re
import sys
from threading import Thread, Event
import requests
from time import ctime, sleep, time
import sqlite3
from dotenv import load_dotenv
import os
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

load_dotenv()


TG_ChatID = os.getenv('CHAT_ID')
TG_BOT_TOKEN = os.getenv('TOKEN')


def tg_sendMsg(
    msg: str | list = "no message",
    TOKEN=TG_BOT_TOKEN,
    chat_id=TG_ChatID,
    ps = "",
    *,
    sep_msg: bool = False,
) -> str:

    """send message via telegram api(url)\n
    url = (
        f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"
    )"""
    # TOKEN = TOKEN
    # chat_id = chat_id
    _ps = ps
    isStr = type(msg) is str
    if isStr:
        msg = msg + _ps
    elif sep_msg and type(msg) == list:
        for m in msg:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={m + _ps}"
            requests.get(url).json()
        return True
    elif not sep_msg and type(msg) != str:
        msg = " \n".join([m for m in msg]) + _ps
    url = (
        f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"
    )
    requests.get(url).json()


db = sqlite3.connect('db.db', check_same_thread=False)


class TaskReminder():
    def __init__(self, taskName: str, taskMsg: str, taksPeriod: int, taskEndTimestamp: int , username, lang: str = 'en', chat_id: int = 123456) -> None:
        self.taskName = '_'.join(re.sub(r'[^a-zA-Z0-9а-яА-Я\s]', '', taskName).split()).lower()
        self.friendly_name = self.taskName.replace('_',' ').capitalize()
        self.taskMsg = taskMsg

        self.username = username
        self.user_id = chat_id
        self.taskName = taskName
        # self.thr_string = f'{self.taskName}_thread = Thread(target=self._thread_func, args=(self.taskName,self.msg,self.time,self.event,), name=self.taskName, daemon=True)\n{self.taskName}_thread.start()'
        self.thr_string = f'Thread(target=self._thread_func, args=(self.user_id,self.taskName,), name=self.taskName, daemon=True).start()'
        if lang == None:
            self.lang = 'en'
        else:
            self.lang = lang

        # self.time_parse(time_msg)
        # XXX
        self.taskPeriod = taksPeriod
        self.taskEndTimestamp = taskEndTimestamp
        self.chat_id = chat_id

        self.event = Event()

    # Hide for now this block, cuz i need to provide taskPeriod and taskEndTimestamp
    # def time_parse(self, time_msg):
    #     if time_msg:
    #         time_value_parsed = int(re.sub('[a-zA-Zа-яА-Я]', '', time_msg).split()[0])
    #         time_unit_parsed = re.sub('[0-9]', '', time_msg).lower()
    #         if any(i in time_unit_parsed for i in ['minute', 'minutes','min', 'm', 'мин','минут','минута','м','минуток']):
    #             self.taskPeriod = time_value_parsed * 60
    #         elif any(i in time_unit_parsed for i in ['hour', 'h','hours','час','часов','ч','часик']):
    #             self.taskPeriod = time_value_parsed * 60 * 60
    #         elif any(i in time_unit_parsed for i in ['day', 'days','d','день','денек','д','дней']):
    #             self.taskPeriod = time_value_parsed * 60 * 60 * 24
    #         else:
    #             self.taskPeriod = 15
    #             if self.lang == 'en':
    #                 print('Set default period 1h.')
    #             elif self.lang == 'ru':
    #                 print('Установлен базовый период 60 минут.')
    
    def _thread_func(self, user_id, taskName: str) -> Thread:
        c = 0
        while True:
            timeNow = int(time())
            if self.event.is_set():
                print(f'About to stop {self.taskName.capitalize()}...')
                break
            # New method to stop thread... XXX
            cursor = db.execute(f'''select * from "{user_id}" where taskName="{taskName}"''')
            task = cursor.fetchone()
            if not task:
                # print(f'About to stop {self.taskName.capitalize()}...')
                logger.info(f'^^^^^^^^^^^^^TaskThread {self.taskName.__repr__()} has been finished.')
                break
            c += 1
            if c > self.taskPeriod/10 or (timeNow > self.taskEndTimestamp and ((timeNow - self.taskEndTimestamp) < 20)):
            # if c >= self.taskPeriod/10:
                print(self.taskMsg)
                tg_sendMsg(self.taskMsg, chat_id=self.chat_id)
                c = 0
                self.taskEndTimestamp += self.taskPeriod
                db.execute(f'UPDATE "{user_id}" SET taskEndTimestamp={self.taskEndTimestamp} WHERE taskName="{self.taskName}"')
                db.commit()
            sleep(10)

    def launch_task(self):
        try:
            exec(self.thr_string)
        except Exception as e:
            print(e)
        if self.lang == 'en':
            # print(f'Task {self.friendly_name.__repr__()} is launch.')
            logger.info(f'^^^^^^^^^^^^^TaskThread {self.friendly_name.__repr__()} has been launched.')
        elif self.lang == 'ru':
            print(f'Задание {self.friendly_name.__repr__()} было запущено.')
        


    def stop_task(self):
        if self.lang == 'en':
            print(f'Task {self.friendly_name.__repr__()} has been stopped.')
        elif self.lang == 'ru':
            print(f'Задание {self.friendly_name.__repr__()} остановлено.')
        self.event.set()




scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Kiev'})

from datetime import datetime

class DateTask():
    """
    taskName: str, message: str, datetime_str: str, telegram_id: int
    \nThe job will be executed on November 6th, 2009 at 16:30:05
    \nsched.add_job(my_job, 'date', run_date=datetime(2009, 11, 6, 16, 30, 5), args=['text'])
    \ndatetime_str = '2024 3 26 16 48 55'
    """
    
    def __init__(self, username: str, taskName: str, message: str, datetime_str: str, user_id: int) -> None:
        self.username = username
        self.taskName = taskName
        self.message = message
        self.user_id = user_id
        self.datetime_str = datetime_str
        self._datetime_parse()
        self.timeNow = datetime.now()
    
    def _job(self):
        tg_sendMsg(msg=self.message, chat_id=self.user_id)
        db.execute(f'''delete from "{self.user_id}_date" where taskName="{self.taskName}"''')
        db.commit()
        logger.info(f"^^^^^^^^^^^^^TaskDate '{self.taskName}' has been finished.")

    def task_start(self):
        # timeNow = datetime.now()
        if self.datetime < self.timeNow:
            db.execute(f'''delete from "{self.user_id}_date" where taskName="{self.taskName}"''')
            db.commit()
            return
        # print(f"Taskdate '{self.taskName}' is launch.")
        logger.info(f"^^^^^^^^^^^^^TaskDate '{self.taskName}' has been launched.")
        scheduler.add_job(self._job, trigger='date', run_date=self.datetime)
        scheduler.start()
        #TODO try to make possible delete job after delete task/ for now the job still working after remove from taks_list
    def _datetime_parse(self):
        self.datetime_list = [int(i) for i in self.datetime_str.split(' ')]
        self.datetime = datetime(*self.datetime_list)
        return self.datetime

    @staticmethod
    def time_valid(datetime_str: str) -> bool: 
        """
        datetime_str = '2024 3 26 16 48 55'
        """
        from datetime import datetime
        timeNow = datetime.now()
        datetime_list = [int(i) for i in datetime_str.split(' ')]
        datetime = datetime(*datetime_list)
        if datetime > timeNow:
            return True
        else:
            return False
    
    @staticmethod
    def datetime_userFriendly(datetime_str: str) -> str: 
        """
        datetime_str = '2024 3 26 16 48 55'
        """
        datetime_list = [int(i) for i in datetime_str.split(' ')]
        output = datetime(*datetime_list).strftime("%Y-%m-%d %H:%M:%S")
        return output
        # output = f'{datetime_list[0]}-{datetime_list[0]}-{datetime_list[0]} {datetime_list[0]}:{datetime_list[0]}:{datetime_list[0]}'




from ast import literal_eval
import aiosqlite


class SQLCommands(object):
    def __init__(self, database_name: str, table_name: str, primary_key: str):
        self._database_name = database_name
        self._table_name = table_name
        self._primary_key = primary_key

    async def delete(self, row_id):
        """
        deletes a certain row from the table.
        :param row_id: The id of the row.
        :type row_id: int
        """
        async with aiosqlite.connect(self._database_name) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    f"DELETE FROM {self._table_name} WHERE {self._primary_key} = ?", (row_id,))
            await db.commit()

    async def execute(self, query):
        """
        Execute SQL query.
        """
        async with aiosqlite.connect(self._database_name) as db:
            async with db.cursor() as cursor:
                cur = await cursor.execute(query)
                res = await cur.fetchall()
            await db.commit()
            return res


class Connect(SQLCommands):
    """
    Instantiate a conversion to and from sqlite3 database and python dictionary.
    """

    def __init__(self, database_name: str, table_name: str, primary_key: str):
        super().__init__(database_name, table_name, primary_key)

    async def to_dict(self, my_id, *column_names: str) -> dict:
        """
        Convert a sqlite3 table into a python dictionary.
        :param my_id: The id of the row.
        :type my_id: int
        :param column_names: The column name.
        :type column_names: str
        :return: The dictionary.
        :rtype: dict
        """
        async with aiosqlite.connect(self._database_name) as db:
            async with db.cursor() as cursor:
                data = {}
                columns = ", ".join(column for column in column_names)

                def check_type(value, value_type):
                    # to check if value is of certain type
                    try:
                        val = str(value)
                        return isinstance(literal_eval(val), value_type)
                    except SyntaxError:
                        return False
                    except ValueError:
                        return False

                if columns == "*":
                    getID = await cursor.execute(
                        f"SELECT {columns} FROM {self._table_name} WHERE {self._primary_key} = ?", (my_id,))
                    fieldnames = [f[0] for f in getID.description]
                    values = await getID.fetchone()
                    values = list(values)
                    for v in range(len(values)):
                        if not (isinstance(values[v], int) or isinstance(values[v], float)):
                            isList = check_type(values[v], list)
                            isTuple = check_type(values[v], tuple)
                            isDict = check_type(values[v], dict)
                            if isList or isTuple or isDict:
                                values[v] = literal_eval(values[v])
                    for i in range(len(fieldnames)):
                        data[fieldnames[i]] = values[i]
                    return data
                else:
                    getID = await cursor.execute(
                        f"SELECT {columns} FROM {self._table_name} WHERE {self._primary_key} = ?", (my_id,))
                    values = await getID.fetchone()
                    values = list(values)
                    for v in range(len(values)):
                        if not (isinstance(values[v], int) or isinstance(values[v], float)):
                            isList = check_type(values[v], list)
                            isTuple = check_type(values[v], tuple)
                            isDict = check_type(values[v], dict)
                            if isList or isTuple or isDict:
                                values[v] = literal_eval(values[v])
                    for i in range(len(column_names)):
                        data[column_names[i]] = values[i]
                    return data

    #  To push data to db

    async def to_sql(self, my_id, dictionary: dict):
        """
        Convert a python dictionary into a sqlite3 table.
        :param my_id: The id of the row.
        :type my_id: int
        :param dictionary: The dictionary object.
        :type dictionary: dict
        :return: The SQLite3 Table.
        :rtype: sqlite
        """
        async with aiosqlite.connect(self._database_name) as db:
            async with db.cursor() as cursor:
                getUser = await cursor. \
                    execute(f"SELECT {self._primary_key} FROM {self._table_name} WHERE {self._primary_key} = ?",
                            (my_id,))
                isUserExists = await getUser.fetchone()
                if isUserExists:
                    for key, val in dictionary.items():
                        if isinstance(val, list) or isinstance(val, dict) or isinstance(val, tuple):
                            dictionary[key] = str(val)
                    await cursor.execute(f"UPDATE {self._table_name} SET " + ', '.join(
                        "{}=?".format(k) for k in dictionary.keys()) + f" WHERE {self._primary_key}=?",
                                         list(dictionary.values()) + [my_id])
                else:
                    await cursor.execute(f"INSERT INTO {self._table_name} ({self._primary_key}) VALUES ( ? )", (my_id,))
                    for key, val in dictionary.items():
                        if isinstance(val, list) or isinstance(val, dict) or isinstance(val, tuple):
                            dictionary[key] = str(val)
                    await cursor.execute(f"UPDATE {self._table_name} SET " + ', '.join(
                        "{}=?".format(k) for k in dictionary.keys()) + f" WHERE {self._primary_key}=?",
                                         list(dictionary.values()) + [my_id])

            await db.commit()

    async def select(self, column_name: str, limit: int = None, order_by: str = None,
                     ascending: bool = True, equal=None, like: str = None, between: tuple = None,
                     distinct: bool = False, offset: int = None) -> list:
        """
        Select a column from the table.

        :param column_name: The column name.
        :type column_name: str
        :param limit:
        :rtype: int
        :param order_by:
        :rtype: str
        :param ascending:
        :rtype: bool
        :param equal:
        :param like:
        :rtype: str
        :param distinct:
        :rtype: bool
        :param between:
        :rtype: tuple
        :param offset:
        :rtype: int
        :return: The list.
        :rtype: list
        """
        async with aiosqlite.connect(self._database_name) as db:
            async with db.cursor() as cursor:

                query = f"SELECT {column_name} FROM {self._table_name}"
                parameters = []
                condition = False
                if distinct is True:
                    query = f"SELECT DISTINCT {column_name} FROM {self._table_name}"
                if equal is not None and condition is False:
                    condition = True
                    query += f" WHERE {column_name} = ?"
                    parameters.append(equal)
                elif equal is not None and condition is True:
                    query += f" AND {column_name} = ?"
                    parameters.append(equal)
                if like is not None and condition is False:
                    condition = True
                    query += f" WHERE {column_name} LIKE ?"
                    parameters.append("%" + like + "%")
                elif like is not None and condition is True:
                    query += f" AND {column_name} LIKE ?"
                    parameters.append("%" + like + "%")
                if between is not None and condition is False:
                    condition = True
                    query += f" WHERE {column_name} BETWEEN ? AND ?"
                    parameters.append(range(between[0], between[1]).start)
                    parameters.append(range(between[0], between[1]).stop)

                elif between is not None and condition is True:
                    query += f" AND {column_name} BETWEEN ? AND ?"
                    parameters.append(range(between[0], between[1]).start)
                    parameters.append(range(between[0], between[1]).stop)
                if order_by is not None:
                    query += f" ORDER BY {order_by}"
                if ascending is False:
                    query += f" DESC"
                else:
                    query += f""
                if limit is not None:
                    query += f" LIMIT ?"
                    parameters.append(limit)
                if offset is not None and limit is not None:
                    query += f" OFFSET ?"
                    parameters.append(offset)
                elif offset is not None and limit is None:
                    raise Exception("You can't use kwarg 'offset' without kwarg 'limit'")
                parameters = str(tuple(parameters))
                parameters = eval(parameters)
                # print(f"query ==> await cursor.execute(\"{query}\", {parameters})")
                # print(parameters)
                getValues = await cursor.execute(query, parameters)
                values = await getValues.fetchall()
                my_list = []

                def check_type(value, value_type):
                    # to check if value is of certain type
                    try:
                        val = str(value)
                        return isinstance(literal_eval(val), value_type)
                    except SyntaxError:
                        return False
                    except ValueError:
                        return False

                for i in values:
                    i = str(i)
                    i = i[1:-2]  # Remove round brackets in i
                    # Check the type of i
                    if i.isnumeric():
                        my_list.append(int(i))
                    elif isinstance(i, float):
                        my_list.append(float(i))
                    elif i == 'None' or i is None:
                        my_list.append(i)
                    elif check_type(i, list) or check_type(i, dict) or check_type(i, tuple):
                        i = eval(i)
                        my_list.append(eval(i))
                    elif i.isascii():
                        i = i[1:-1]
                        my_list.append(i)
                    else:
                        my_list.append(i)

                return my_list