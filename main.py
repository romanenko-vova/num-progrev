import asyncio
import logging
import os
import datetime
import dotenv
from creating_bd import creating_db
from payments import yookassa_confirmation
from handlers import (
    GET_DATE,
    READY_TRIANGLE,
    READY_ARKANES,
    GET_MINUSES,
    GET_MONEY_CODE,
    PREPREPARE_BUY_MESSAGE,
    PREREADY_BUY_MESSAGE,
    PREPARE_BUY_MESSAGE,
    GET_PHONE_NUMBER,
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
    preprepare_buy_message,
    preready_buy_message,
    pre_buy_message,
    admin_choice,
    get_mailing_message,
    get_confirmation_mailing_message,
    get_phone_number,
    create_payment,
    send_warning,
    send_progrev_message,
    send_warning_phone,
    load_conversation,
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

    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.ALL, load_conversation),
            CallbackQueryHandler(load_conversation)
        ],
        states={
            GET_DATE: [
                MessageHandler(filters.Regex(date_regex), get_date),
                MessageHandler(filters.TEXT, send_warning),
            ],
            READY_TRIANGLE: [
                CallbackQueryHandler(send_triangle, pattern="^ready_triangle$")
            ],
            READY_ARKANES: [
                CallbackQueryHandler(send_arkanes, pattern="^ready_arkanes$")
            ],
            GET_MINUSES: [
                CallbackQueryHandler(
                    minuses, pattern="^(0min|1min|2min|3min|4min|5min|6min)$"
                )
            ],
            GET_MONEY_CODE: [
                CallbackQueryHandler(get_money_code, pattern="^ready$"),
            ],
            PREPREPARE_BUY_MESSAGE: [
                CallbackQueryHandler(preprepare_buy_message, pattern="^ready_to_buy$")
            ],
            PREREADY_BUY_MESSAGE: [
                CallbackQueryHandler(
                    preready_buy_message, pattern="^prepre_buy_message$"
                )
            ],
            PREPARE_BUY_MESSAGE: [
                CallbackQueryHandler(pre_buy_message, pattern="^ready_to_pay$"),
            ],
            GET_PHONE_NUMBER: [
                CallbackQueryHandler(get_phone_number, pattern="^get_phone_number$")
            ],
            CREATE_PAYMENT: [
                MessageHandler(filters.CONTACT, create_payment),
                MessageHandler(filters.Regex("^7\d{10}$"), create_payment),
                MessageHandler(
                    filters.TEXT & (~filters.Regex("^7\d{10}$")) & (~filters.CONTACT),
                    send_warning_phone,
                ),
                CallbackQueryHandler(get_phone_number, pattern="^get_phone_number$"),
            ],
            CONFIRMATION_PAYMENT: [
                CallbackQueryHandler(
                    yookassa_confirmation, pattern="^confirmation_payment$"
                ),
                CallbackQueryHandler(get_phone_number, pattern="^get_phone_number$"),
            ],
            ADMIN_START: [
                MessageHandler(filters.TEXT, admin_choice),
            ],
            GET_MAILING_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_mailing_message)
            ],
            YOU_SURE: [
                CallbackQueryHandler(
                    get_confirmation_mailing_message, pattern="^(i_sure|not_sure)$"
                )
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        # per_message=True,
    )
    application.job_queue.run_daily(send_progrev_message, time=datetime.time(hour=12))
    # application.job_queue.run_once(send_progrev_message, datetime.timedelta(minutes=5))
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(creating_db())
    main()
