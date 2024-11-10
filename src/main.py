import asyncio
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from src.functions import get_rate, get_custom_currency

users = {}
RESPONSE_TIMEOUT = 900
async def check_rate_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    while True:
        message = get_rate()
        if message is not None and len(message) != 0:
            await context.bot.send_message(chat_id=user_id, text=message)
            # await update.message.reply_text(message)
        elif user_id in users and users[user_id] == False:
            await context.bot.send_message(chat_id=user_id, text='Changes not found')
            users[user_id] = True
            # await update.message.reply_text('Changes not found')

        print(f'Message length: {len(message)}\n')
        await asyncio.sleep(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in users:
        asyncio.create_task(check_rate_updates(update, context))
        users[user_id] = False


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = get_custom_currency(update.message.text)
    user_id = update.message.from_user.id

    if len(message) != 0:
        await context.bot.send_message(chat_id=user_id, text=message)
    else:
        await context.bot.send_message(chat_id=user_id, text="No matching.\nCheck that you write currency correct")


app = ApplicationBuilder().token(os.getenv('EXCHANGE_RATE_TELEGRAM_BOT')).build()

currency_rate_notification = CommandHandler("start", start)
echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND),echo)

app.add_handler(currency_rate_notification)
app.add_handler(echo_handler)


app.run_polling()
