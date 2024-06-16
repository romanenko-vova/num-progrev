import asyncio
import logging
import os

import dotenv
from creating_bd import creating_db
from payments import yookassa_confirmation
from handlers import (
    GET_DATE,
    READY_ARKANES,
    GET_MINUSES,
    GET_MONEY_CODE,
    PREPARE_BUY_MESSAGE,
    BUY,
    ADMIN_START,
    CONFIRMATION_PAYMENT,
    start,
    get_date,
    send_arkanes,
    minuses,
    get_money_code,
    pre_buy_message,
    admin_choice,
    confirmation_payment,
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

    application = ApplicationBuilder().token("7227890712:AAHu_PD1uaY5Kkh-oK-sgJIwQhs0QbPRkGk").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_DATE: [
                MessageHandler(filters.Regex(date_regex), get_date),
            ],
            READY_ARKANES: [CallbackQueryHandler(send_arkanes)],
            GET_MINUSES: [CallbackQueryHandler(minuses)],
            GET_MONEY_CODE: [
                CallbackQueryHandler(get_money_code),
            ],
            PREPARE_BUY_MESSAGE: [CallbackQueryHandler(pre_buy_message)],
            BUY: [CallbackQueryHandler(confirmation_payment)],
            ADMIN_START: [
                MessageHandler(filters.TEXT, admin_choice),
            ],
            CONFIRMATION_PAYMENT: [CallbackQueryHandler(yookassa_confirmation)],
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
