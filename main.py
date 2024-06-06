import asyncio
import logging
import os

import dotenv
from creating_bd import creating_db
from handlers import GET_DATE, GET_MINUSES, start, get_date, minuses
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


dotenv.load_dotenv()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    date_regex = "^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.\d{4}$"
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    asyncio.run(creating_db())

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_DATE: [
                MessageHandler(filters.Regex(date_regex), get_date),
            ],
            GET_MINUSES: [
                MessageHandler(filters.TEXT, minuses),
            ],
        },
        fallbacks=[],
    )

    application.run_polling()
