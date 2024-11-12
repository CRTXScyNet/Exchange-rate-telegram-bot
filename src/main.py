import asyncio
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from src.functions import get_rate, get_custom_currency, get_all_currencies
admin_users = [265929445]
users_id = {}
users_names = {}
CHECK_DELAY = 900
async def check_rate_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    while True:
        message = get_rate()

        if user_id not in users_id or users_id[user_id] == False:
            await context.bot.send_message(chat_id=user_id, text=get_all_currencies())
            users_id[user_id] = True
        elif message is not None and len(message) != 0:
            await context.bot.send_message(chat_id=user_id, text=message)
            # await update.message.reply_text(message)

        print(f'User id: {user_id}, username: {users_names[user_id]}')
        print(f'Message length: {len(message)}\n')
        await asyncio.sleep(CHECK_DELAY)


async def get_noticed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in users_id:
        users_id[user_id] = False
        users_names[user_id] = user_id

    asyncio.create_task(check_rate_updates(update, context))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if user_id not in users_id:
        users_id[user_id] = False
        users_names[user_id] = update.message.from_user.name

    introduce_message = '''
    Hi, I am Alexanders Exchange Rate Bot.
    Here are some commands to use for you:
    /all - prints all contained currencies
    /updates - will notice you if any currency changed
    Also you can type currency code to get its rate.
    '''
    await context.bot.send_message(chat_id=user_id, text=introduce_message)



async def get_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_all_currencies()
    user_id = update.message.from_user.id

    if user_id not in users_id:
        users_id[user_id] = False
        users_names[user_id] = update.message.from_user.name

    await context.bot.send_message(chat_id=user_id, text=message)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = get_custom_currency(update.message.text)
    user_id = update.message.from_user.id

    if user_id not in users_id:
        users_id[user_id] = False
        users_names[user_id] = update.message.from_user.name

    if len(message) != 0:
        await context.bot.send_message(chat_id=user_id, text=message)
    else:
        await context.bot.send_message(chat_id=user_id, text="No matching.\nCheck that you wrote currency code correctly")


async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in users_id:
        users_id[user_id] = False
        users_names[user_id] = update.message.from_user.name


    if user_id in admin_users:

        await context.bot.send_message(chat_id=user_id, text='\n'.join([str(i) for i in users_names.values()]))


app = ApplicationBuilder().token(os.getenv('EXCHANGE_RATE_TELEGRAM_BOT')).build()

introducing_handler = CommandHandler("start",start)
currency_rate_notification = CommandHandler("updates", get_noticed)
echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND),echo)
get_all_currencies_handler = CommandHandler('all', get_all)
get_all_users = CommandHandler('users', get_users)

app.add_handler(introducing_handler)
app.add_handler(currency_rate_notification)
app.add_handler(echo_handler)
app.add_handler(get_all_currencies_handler)
app.add_handler(get_all_users)



print('started')
app.run_polling()