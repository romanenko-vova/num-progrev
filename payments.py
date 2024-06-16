
import uuid

from yookassa import Configuration, Payment

Configuration.account_id = "349918"
Configuration.secret_key = "test_wwHRVzc1JTXUJhM5Wh9lV65VCFtc4iG2ryM0bKJ6SUw"
async def yookassa_payment():
    payment_process = Payment.create({
        "amount": {
            "value": "2000.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.e-fliterc.com/product/nx10-10-channel-dsmx-transmitter-only/SPMR10100.html"
        },
        "capture": True,
        "description": "Заказ №1"
    }, uuid.uuid4())

    payment_id = payment_process.id
    global payment
    payment = Payment.find_one(payment_id)
    if payment.confirmation and payment.confirmation.type == "redirect":
        return payment.confirmation.confirmation_url

async def yookassa_confirmation():
    print(f"Статус платежа: {payment.status}")
