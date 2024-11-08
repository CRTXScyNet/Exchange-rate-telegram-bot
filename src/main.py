import asyncio
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from src.functions import get_rate



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    first = True
    while True:
        message = get_rate()
        if message is not None and len(message) != 0:
            await update.message.reply_text(message)
        elif first:
            await update.message.reply_text('Changes not found')

        first = False

        await asyncio.sleep(5)


app = ApplicationBuilder().token(os.getenv('EXCHANGE_RATE_TELEGRAM_BOT')).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
