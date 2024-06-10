import asyncio
import logging
import os

import dotenv
from creating_bd import creating_db
from handlers import (
    GET_DATE,
    GET_MINUSES,
    GET_MONEY_CODE,
    start,
    get_date,
    minuses,
    get_money_code,
)
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

def main():
    date_regex = "^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.\d{4}$"
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_DATE: [
                MessageHandler(filters.Regex(date_regex), get_date),
            ],
            GET_MINUSES: [
                MessageHandler(filters.TEXT, minuses),
            ],
            GET_MONEY_CODE: [
                MessageHandler(filters.TEXT, get_money_code),
            ],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(creating_db())
    main()