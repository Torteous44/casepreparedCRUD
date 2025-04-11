from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.subscription import Subscription, SubscriptionCreate, SubscriptionUpdate
from app.services import subscription as subscription_service
from app.services import stripe as stripe_service

router = APIRouter()

@router.get("/", response_model=List[Subscription])
def read_subscriptions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve subscriptions for the current user
    """
    subscriptions = subscription_service.get_subscriptions(db=db, skip=skip, limit=limit)
    # Filter to only show subscriptions that belong to the current user
    return [sub for sub in subscriptions if sub.user_id == current_user.id]

@router.post("/", response_model=Subscription)
def create_subscription(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    subscription_in: SubscriptionCreate,
) -> Any:
    """
    Create new subscription
    """
    # Check if user already has a subscription
    existing_sub = subscription_service.get_subscription_by_user_id(
        db=db, user_id=current_user.id
    )
    if existing_sub:
        raise HTTPException(
            status_code=400,
            detail="User already has a subscription",
        )
    
    subscription = subscription_service.create_subscription(
        db=db, subscription_in=subscription_in
    )
    return subscription

@router.post("/create-stripe-subscription")
async def create_stripe_subscription(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    price_id: str = Body(...),
) -> Any:
    """
    Create a Stripe subscription for the user
    """
    # Check if user already has a subscription
    existing_sub = subscription_service.get_subscription_by_user_id(
        db=db, user_id=current_user.id
    )
    
    try:
        # Create or get existing Stripe customer
        customer_id = None
        if existing_sub and existing_sub.stripe_customer_id:
            customer_id = existing_sub.stripe_customer_id
        else:
            # Create a new customer in Stripe
            customer = stripe_service.create_customer(
                email=current_user.email,
                name=current_user.full_name,
            )
            customer_id = customer["id"]
        
        # Create the subscription in Stripe
        subscription = stripe_service.create_subscription(
            customer_id=customer_id,
            price_id=price_id,
        )
        
        # Create or update subscription in our database
        if existing_sub:
            sub_update = SubscriptionUpdate(
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription["id"],
                plan=price_id,  # Using price_id as plan identifier
                status=subscription["status"],
            )
            updated_sub = subscription_service.update_subscription(
                db=db, db_subscription=existing_sub, subscription_in=sub_update
            )
            return {
                "subscription_id": updated_sub.id,
                "stripe_subscription_id": subscription["id"],
                "status": subscription["status"],
                "client_secret": subscription.get("latest_invoice", {}).get("payment_intent", {}).get("client_secret"),
            }
        else:
            sub_create = SubscriptionCreate(
                user_id=current_user.id,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription["id"],
                plan=price_id,
                status=subscription["status"],
            )
            new_sub = subscription_service.create_subscription(
                db=db, subscription_in=sub_create
            )
            return {
                "subscription_id": new_sub.id,
                "stripe_subscription_id": subscription["id"],
                "status": subscription["status"],
                "client_secret": subscription.get("latest_invoice", {}).get("payment_intent", {}).get("client_secret"),
            }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating subscription: {str(e)}",
        )

@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> Any:
    """
    Handle Stripe webhook events
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header")
    
    result = stripe_service.handle_webhook_event(payload, sig_header, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Webhook error"))
    
    return {"status": "success", "event_type": result.get("event_type")} 