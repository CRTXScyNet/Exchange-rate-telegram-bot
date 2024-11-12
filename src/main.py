import asyncio
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from src.functions import get_rate, get_custom_currency, get_all_currencies

admin_users = [265929445]
users_id = {}    #{'user_id':{'user_name':username,first_update':first_update, 'context':context},...}

CHECK_DELAY = 60
CONTEXT = 'context'
FIRST_UPDATE = 'first update'
USERNAME = 'username'
UPDATE = 'update'
IS_UPDATE_SENDING = 'is sending'
is_update_running = False
def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users_id[user_id] = {}
    users_id[user_id][USERNAME] = update.message.from_user.name
    users_id[user_id][CONTEXT] = context
    users_id[user_id][UPDATE] = update
    users_id[user_id][FIRST_UPDATE] = True
    users_id[user_id][IS_UPDATE_SENDING] = False


async def check_rate_updates():
    while True:
        message = get_rate()

        for user in users_id:
            if not users_id[user][IS_UPDATE_SENDING]:
                continue
            context = users_id[user][CONTEXT]

            if message is not None and len(message) != 0:
                await context.bot.send_message(chat_id=user, text=message)

            print(f'User id: {user}, username: {users_id[user][USERNAME]}')

        print(f'Message length: {len(message)}')
        print(len([i for i in users_id if users_id[i][IS_UPDATE_SENDING]]))
        print()
        await asyncio.sleep(CHECK_DELAY)


async def stop_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in users_id:
        add_user(update, context)

    users_id[user_id][IS_UPDATE_SENDING] = False
    await context.bot.send_message(chat_id=user_id, text='No more notifications about changes for you.')


async def get_noticed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_update_running
    user_id = update.message.from_user.id

    if user_id not in users_id:
        add_user(update, context)

    if not users_id[user_id][IS_UPDATE_SENDING]:
        await context.bot.send_message(chat_id=user_id, text='I will show you changes of currency rates!')
        users_id[user_id][IS_UPDATE_SENDING] = True

    if not is_update_running:
        is_update_running = True
        asyncio.create_task(check_rate_updates())






async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if user_id not in users_id:
        add_user(update, context)

    introduce_message = '''
    Hi, I am Alexanders Exchange Rate Bot.
    Here are some commands to use for you:
    /all - prints all contained currencies
    /updates - will notice you if any currency changed
    /stop - disable notification of any currency changing for you
    Also you can type currency code to get its rate.
    '''
    await context.bot.send_message(chat_id=user_id, text=introduce_message)


async def get_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_all_currencies()
    user_id = update.message.from_user.id

    if user_id not in users_id:
        add_user(update, context)

    await context.bot.send_message(chat_id=user_id, text=message)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = get_custom_currency(update.message.text)
    user_id = update.message.from_user.id

    if user_id not in users_id:
        add_user(update, context)

    if len(message) != 0:
        await context.bot.send_message(chat_id=user_id, text=message)
    else:
        await context.bot.send_message(chat_id=user_id, text="No matching.\nCheck that you wrote currency code correctly")


async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in users_id:
        add_user(update, context)

    if user_id in admin_users:
        await context.bot.send_message(chat_id=user_id, text='\n'.join([str(users_id[i][USERNAME]) for i in users_id]))




app = ApplicationBuilder().token(os.getenv('EXCHANGE_RATE_TELEGRAM_BOT')).build()

introducing_handler = CommandHandler("start",start)
currency_rate_notification = CommandHandler("updates", get_noticed)
stop_rate_notification = CommandHandler("stop", stop_updates)
echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND),echo)
get_all_currencies_handler = CommandHandler('all', get_all)
get_all_users = CommandHandler('users', get_users)

app.add_handler(introducing_handler)
app.add_handler(currency_rate_notification)
app.add_handler(stop_rate_notification)
app.add_handler(echo_handler)
app.add_handler(get_all_currencies_handler)
app.add_handler(get_all_users)
print('started')




app.run_polling()




