import stripe
from typing import Optional, Dict, Any
from uuid import UUID

from app.core.config import settings
from app.services import subscription as subscription_service
from sqlalchemy.orm import Session

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_API_KEY

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
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {"price": price_id},
            ],
            expand=["latest_invoice.payment_intent"],
        )
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
        
        return {"success": True, "event_type": event_type}
    
    except (stripe.error.SignatureVerificationError, ValueError) as e:
        return {"success": False, "error": str(e)} 