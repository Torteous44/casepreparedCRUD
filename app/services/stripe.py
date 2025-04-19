import stripe
from typing import Optional, Dict, Any
from uuid import UUID
import os

from app.core.config import settings
from app.services import subscription as subscription_service
from sqlalchemy.orm import Session

# Debug prints to see what's happening
print(f"Environment variable: {os.environ.get('STRIPE_API_KEY', 'Not set')}")
print(f"Settings key: {settings.STRIPE_API_KEY[:5] if settings.STRIPE_API_KEY else 'None'}")

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_API_KEY
print(f"Final Stripe key: {stripe.api_key if stripe.api_key else 'None'}...")

def create_customer(email: str, name: str) -> Dict[str, Any]:
    """
    Create a Stripe customer
    """
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
        )
        return customer
    except stripe.error.StripeError as e:
        raise e

def create_subscription(
    customer_id: str, 
    price_id: str,
) -> Dict[str, Any]:
    """
    Create a Stripe subscription
    """
    try:
        # Try to retrieve the price first to validate it exists
        try:
            print(f"Attempting to retrieve price: {price_id}")
            price = stripe.Price.retrieve(price_id)
            print(f"Price found: {price.id}")
        except Exception as price_error:
            print(f"Error retrieving price: {str(price_error)}")
            raise price_error
            
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {"price": price_id},
            ],
            expand=["latest_invoice"],
        )
        
        # If you need payment intent, fetch it separately
        if subscription.get("latest_invoice") and subscription["latest_invoice"].get("payment_intent"):
            payment_intent_id = subscription["latest_invoice"]["payment_intent"]
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            # Add the payment intent to the subscription object
            subscription["latest_invoice"]["payment_intent"] = payment_intent
            
        return subscription
    except stripe.error.StripeError as e:
        raise e

def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
    """
    Cancel a Stripe subscription
    """
    try:
        subscription = stripe.Subscription.delete(subscription_id)
        return subscription
    except stripe.error.StripeError as e:
        raise e

def handle_webhook_event(payload: Dict[str, Any], sig_header: str, db: Session) -> Dict[str, Any]:
    """
    Handle Stripe webhook events
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        event_type = event["type"]
        event_data = event["data"]["object"]
        
        # Handle subscription events
        if event_type.startswith("customer.subscription"):
            stripe_subscription_id = event_data["id"]
            db_subscription = subscription_service.get_subscription_by_stripe_id(
                db, stripe_subscription_id
            )
            
            if db_subscription:
                # Handle various subscription events
                if event_type == "customer.subscription.created":
                    db_subscription.status = "active"
                elif event_type == "customer.subscription.updated":
                    db_subscription.status = event_data["status"]
                elif event_type == "customer.subscription.deleted":
                    db_subscription.status = "cancelled"
                
                db.add(db_subscription)
                db.commit()
                db.refresh(db_subscription)
        
        # Handle checkout session completed events
        elif event_type == "checkout.session.completed":
            # Get details from the checkout session
            session = event_data
            
            # If this is for a subscription
            if session.get("mode") == "subscription" and session.get("customer") and session.get("subscription"):
                customer_id = session.get("customer")
                subscription_id = session.get("subscription")
                
                # Try to find user with this customer ID
                db_subscription = subscription_service.get_subscription_by_stripe_customer_id(
                    db, customer_id
                )
                
                if db_subscription:
                    # Update subscription with the new subscription ID
                    db_subscription.stripe_subscription_id = subscription_id
                    db_subscription.status = "active"
                    
                    # Try to get subscription details to update plan info
                    try:
                        subscription = retrieve_subscription(subscription_id)
                        if subscription and subscription.get("items") and subscription["items"].get("data") and len(subscription["items"]["data"]) > 0:
                            price_id = subscription["items"]["data"][0].get("price", {}).get("id")
                            if price_id:
                                db_subscription.plan = price_id
                    except Exception:
                        # Continue even if we can't get the price ID
                        pass
                    
                    db.add(db_subscription)
                    db.commit()
                    db.refresh(db_subscription)
        
        return {"success": True, "event_type": event_type}
    
    except (stripe.error.SignatureVerificationError, ValueError) as e:
        return {"success": False, "error": str(e)}

def create_setup_intent(customer_id: str) -> Dict[str, Any]:
    """
    Create a SetupIntent for collecting a payment method
    """
    try:
        setup_intent = stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=["card"],
        )
        return setup_intent
    except stripe.error.StripeError as e:
        raise e

def attach_payment_method(customer_id: str, payment_method_id: str) -> Dict[str, Any]:
    """
    Attach a payment method to a customer
    """
    try:
        payment_method = stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id,
        )
        return payment_method
    except stripe.error.StripeError as e:
        raise e

def set_default_payment_method(customer_id: str, payment_method_id: str) -> Dict[str, Any]:
    """
    Set a payment method as the default for a customer
    """
    try:
        customer = stripe.Customer.modify(
            customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id,
            },
        )
        return customer
    except stripe.error.StripeError as e:
        raise e

def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
    """
    Retrieve a payment intent by ID
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent
    except stripe.error.StripeError as e:
        raise e

def retrieve_subscription(subscription_id: str) -> Dict[str, Any]:
    """
    Retrieve a Stripe subscription by ID
    
    Args:
        subscription_id: Stripe subscription ID
        
    Returns:
        Dictionary containing subscription details
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription
    except stripe.error.StripeError as e:
        raise e

def create_checkout_session(
    price_id: str,
    customer_id: Optional[str] = None,
    success_url: str = f"{settings.FRONTEND_BASE_URL}/checkout/success",
    cancel_url: str = f"{settings.FRONTEND_BASE_URL}/checkout/cancel",
) -> Dict[str, Any]:
    """
    Create a Stripe Checkout session for subscription
    
    Args:
        price_id: Stripe Price ID for the subscription plan
        customer_id: Optional existing Stripe customer ID
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect after cancelled payment
        
    Returns:
        Dictionary containing checkout session details with URL
    """
    try:
        checkout_params = {
            "payment_method_types": ["card"],
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        
        # Add customer if provided
        if customer_id:
            checkout_params["customer"] = customer_id
            
        print(f"Stripe API key: {stripe.api_key[:8]}... (live mode: {not stripe.api_key.startswith('sk_test_')})")
        print(f"Creating checkout session with params: {checkout_params}")
        
        # Validate price exists in Stripe
        try:
            price = stripe.Price.retrieve(price_id)
            print(f"Price found: {price.id}, product: {price.product}")
        except Exception as price_error:
            print(f"Price validation error: {str(price_error)}")
            raise price_error
            
        checkout_session = stripe.checkout.Session.create(**checkout_params)
        return checkout_session
    except stripe.error.StripeError as e:
        print(f"Stripe error: {type(e)}, {str(e)}")
        print(f"Error details: {e.json_body if hasattr(e, 'json_body') else 'No JSON body'}")
        raise e

def retrieve_checkout_session(session_id: str) -> Dict[str, Any]:
    """
    Retrieve a Stripe Checkout session by ID
    
    Args:
        session_id: Stripe Checkout session ID
        
    Returns:
        Dictionary containing checkout session details
    """
    try:
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=["subscription", "customer"]
        )
        return session
    except stripe.error.StripeError as e:
        raise e 