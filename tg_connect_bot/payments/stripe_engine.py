import decouple
import stripe

stripe.api_key = decouple.config("STRIPE_API")
STRIPE_PRICE = decouple.config("STRIPE_PRICE")
bot_link = decouple.config("BOT_LINK")


def create_payment_link(tg_id):
    try:
        session = stripe.checkout.Session.create(
            # payment_method_types=["card"],
            subscription_data={
                'trial_period_days': 7,
            },
            line_items=[
                {
                    "price": STRIPE_PRICE,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=f"{bot_link}?start=success_{tg_id}",
            cancel_url=f"{bot_link}?start=cancel",
        )
        return session.url, session.id
    except Exception as e:
        print(f'[stripe_engine]\n {e}')


def check_payment_status(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.status, session.url
    except Exception as e:
        print(f'[stripe_engine]\n {e}')
