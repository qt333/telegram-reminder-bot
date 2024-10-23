
help_msg = '📖 List of available commands:\
    \n\n/menu - Menu \
    \n/task - Create task \
    \n/taskdate - Create datetime task \
    \n/list - Show list of all current tasks \
    \n/help - Help \
    \n/taskhelp - Instruction \
    \n/update - Update certain task parameter (in process) \
    \n/delete - Delete task \
    \n/delete_all - Delete all tasks'

newTask_help_msg = '🗒 Well, to create <b>Period-Task</b> you need to pass 3 steps 👇:\n\n\
1. Write new task name. Example: Drink coffee ☕️\n\n\
2. Write message that you wanna reiceve from task:\nExample: Hey👋 buddy! Its time to drink some coffee ☕️...\n\n\
3. Write desire period of time of this task.\nExample: 5m or 1h or 3d\
\n\nTo create <b>Datetime-Task</b> same 1st-2nd steps, 3rd step specify exact datetime:\
\nFormat: 2024 11 6 16 30 5 - the task will be executed\non November 6th, 2024 at 16:30:05\
\n\nFor this all done 👍, you about to reiceve message after timer countdown'

newTask = ['Enter new task name 🖋:','Enter task message 📩:','Enter task period 🕔:\n\n(Example: 5m or 1h or 3d)']
newDateTask = [
    'Enter new task name 🖋:',
    '<b>Enter task message</b>📩:',
    'Enter <b>task datetime</b> 🕔:\n\nFormat: 2024 11 6 16 30 5\nThe task will be executed on November 6th, 2024 at 16:30:05'
    ]

updateTask = 'update current task'

supportMsg = 'If you wanna support project (which is not needed but appreciated 🤝) - available options below:\
    \n\nToncoin (TON):\n<code>UQDyUVl29oSatC-oQeTYKb7gz6EljcmmUvzr2J0unEsP1o0c</code>\n\n\
USDT (TRC-20):\n<code>TBp7oJSbHMb8hfY8ZjV31Lz4wkG5kwhuM7</code>\n\n\
BinancePay (ID):\n<code>168079608</code>\n\nThanks! 🙂'

MESSAGES = {
    # 'hello':hello_msg,
    'help':help_msg,
    'newTask':newTask,
    'newTaskHelp':newTask_help_msg,
    'updateTask': updateTask,
    'support': supportMsg,
    'newDateTask':newDateTask
    }