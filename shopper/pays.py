import stripe
import time
from django.conf import settings

# Set Stripe API key - these should be moved to settings.py in production
stripe.api_key = "sk_test_51R42iE4UO6oA7xziEVlMICY6mVRKozfumvIbVp49oH9VDR81PvQBaV3Yi1e0qgadEG9fAu4YHoFg5MDHOVwtgSCq0074teygS8"
STRIPE_PUBLIC_KEY = "pk_test_51R42iE4UO6oA7xziArvJcg8wUXhX9MYz0Ty1rNjavu3lPtdmYr6Q7fvV8pJcNwiaSJk1Qd0gFe0kmzWHMTADZ0sb008wTC165b"


def get_payment_intent(amount, order_id, return_url):
    """
    Create a Stripe payment intent

    Args:
        amount: Payment amount in GBP
        order_id: Order ID
        return_url: Return URL after payment

    Returns:
        dict: Dictionary containing client secret and public key
    """
    # Stripe uses the smallest currency unit (pence for GBP), convert pounds to pence
    amount_in_pence = int(float(amount) * 100)

    try:
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_in_pence,
            currency="gbp",  # British Pounds
            metadata={"order_id": order_id},
            description=f"Order #{order_id}"
        )

        # Return information needed by the client
        return {
            "client_secret": intent.client_secret,
            "public_key": STRIPE_PUBLIC_KEY,
            "payment_id": intent.id,
            "return_url": return_url,
            "amount": amount,
            "currency": "GBP"
        }
    except Exception as e:
        print(f"Stripe payment error: {str(e)}")
        return None