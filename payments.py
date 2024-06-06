
from yookassa import Configuration, Payment
import dotenv
import os
dotenv.load_dotenv()

Configuration.account_id = os.getenv("ACCOUNT_ID")
Configuration.secret_key = os.getenv("SECRET_KEY")

payment = Payment.create({
    "amount": {
        "value": "100.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://www.example.com/return_url"
    },
    "capture": True,
    "description": "Заказ №37",
    "metadata": {
      "order_id": "37"
    }
})

payment_id = payment.id
payment_info = Payment.find_one(payment_id)

if payment_info.status == 'succeeded':
    print("Оплата прошла успешно")
elif payment_info.status == 'pending':
    print("Оплата в процессе")
else:
    print("Оплата не прошла")
