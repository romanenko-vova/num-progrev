import asyncio
import logging
import os

import dotenv
from creating_bd import creating_db
from payments import yookassa_confirmation
from handlers import (
    GET_DATE,
    READY_TRIANGLE,
    READY_ARKANES,
    GET_MINUSES,
    GET_MONEY_CODE,
    PREPARE_BUY_MESSAGE,
    CREATE_PAYMENT,
    CHEK_PAYMENT,
    ADMIN_START,
    CONFIRMATION_PAYMENT,
    GET_MAILING_MESSAGE,
    YOU_SURE,
    start,
    get_date,
    send_triangle,
    send_arkanes,
    minuses,
    get_money_code,
    pre_buy_message,
    admin_choice,
    buy_callback,
    get_mailing_message,
    get_confirmation_mailing_message,
    create_payment,
    send_warning
)
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)


dotenv.load_dotenv()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main():
    date_regex = r"^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[012])\.(1|2)\d{3}$|^(0?[1-9]|[12][0-9])\.(0?[1-9]|1[012])\.(1|2)\d{3}$"

    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_DATE: [
                MessageHandler(filters.Regex(date_regex), get_date),
                MessageHandler(filters.TEXT, send_warning)
            ],
            READY_TRIANGLE: [CallbackQueryHandler(send_triangle)],
            READY_ARKANES: [CallbackQueryHandler(send_arkanes)],
            GET_MINUSES: [CallbackQueryHandler(minuses)],
            GET_MONEY_CODE: [
                CallbackQueryHandler(get_money_code),
            ],
            PREPARE_BUY_MESSAGE: [CallbackQueryHandler(pre_buy_message)],
            CREATE_PAYMENT: [CallbackQueryHandler(create_payment)],
            CONFIRMATION_PAYMENT: [CallbackQueryHandler(yookassa_confirmation)],
            ADMIN_START: [
                MessageHandler(filters.TEXT, admin_choice),
            ],
            GET_MAILING_MESSAGE:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_mailing_message)],
            YOU_SURE: [CallbackQueryHandler(get_confirmation_mailing_message)],
        },
        fallbacks=[],
        # per_message=True,
    )
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(creating_db())
    main()
