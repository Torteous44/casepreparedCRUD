from typing import Any, List
from datetime import datetime, timedelta

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
    user_subscriptions = [sub for sub in subscriptions if sub.user_id == current_user.id]
    
    # Enhance subscriptions with next payment date
    for sub in user_subscriptions:
        if sub.stripe_subscription_id and sub.status == "active":
            try:
                # Try to get subscription details from Stripe
                stripe_sub = stripe_service.retrieve_subscription(sub.stripe_subscription_id)
                
                # Get the next billing date
                if stripe_sub and "current_period_end" in stripe_sub:
                    # Convert UNIX timestamp to datetime
                    next_payment_timestamp = stripe_sub["current_period_end"]
                    sub.next_payment_date = datetime.fromtimestamp(next_payment_timestamp)
                else:
                    # Fallback: estimate based on creation date if unavailable
                    # This assumes monthly billing - adjust as needed
                    sub.next_payment_date = sub.created_at + timedelta(days=30)
            except Exception as e:
                # If Stripe API call fails, use an estimate
                sub.next_payment_date = sub.created_at + timedelta(days=30)
        else:
            # For non-active subscriptions, don't set a next payment date
            sub.next_payment_date = None
    
    return user_subscriptions

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
    data: dict = Body(...),
) -> Any:
    """
    Create a Stripe subscription for the user
    """
    # Extract price_id from the request body
    price_id = data.get("price_id")
    payment_method_id = data.get("payment_method_id")  # Get payment method if provided
    
    if not price_id:
        raise HTTPException(
            status_code=422,
            detail="price_id is required"
        )
        
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
            try:
                customer = stripe_service.create_customer(
                    email=current_user.email,
                    name=current_user.full_name,
                )
                customer_id = customer["id"]
            except Exception as customer_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error creating Stripe customer: {str(customer_error)}"
                )
        
        # If payment method ID is provided, attach it to the customer
        if payment_method_id:
            try:
                stripe_service.attach_payment_method(customer_id, payment_method_id)
                
                # Set as default payment method
                stripe_service.set_default_payment_method(customer_id, payment_method_id)
            except Exception as payment_method_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error attaching payment method: {str(payment_method_error)}"
                )
        
        # Create the subscription in Stripe
        try:
            subscription = stripe_service.create_subscription(
                customer_id=customer_id,
                price_id=price_id,
            )
        except Exception as subscription_error:
            raise HTTPException(
                status_code=400,
                detail=f"Error creating Stripe subscription: {str(subscription_error)}"
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
            
            # Get client secret from payment intent if available
            client_secret = None
            latest_invoice = subscription.get("latest_invoice", {})
            if isinstance(latest_invoice, dict) and latest_invoice.get("payment_intent"):
                payment_intent = latest_invoice["payment_intent"]
                if isinstance(payment_intent, dict):
                    client_secret = payment_intent.get("client_secret")
                elif isinstance(payment_intent, str):
                    # If it's just the ID, we need to fetch the payment intent
                    try:
                        payment_intent_obj = stripe_service.retrieve_payment_intent(payment_intent)
                        client_secret = payment_intent_obj.get("client_secret")
                    except Exception:
                        # Continue without client secret if it fails
                        pass
                        
            return {
                "subscription_id": updated_sub.id,
                "stripe_subscription_id": subscription["id"],
                "status": subscription["status"],
                "client_secret": client_secret,
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
            
            # Get client secret from payment intent if available
            client_secret = None
            latest_invoice = subscription.get("latest_invoice", {})
            if isinstance(latest_invoice, dict) and latest_invoice.get("payment_intent"):
                payment_intent = latest_invoice["payment_intent"]
                if isinstance(payment_intent, dict):
                    client_secret = payment_intent.get("client_secret")
                elif isinstance(payment_intent, str):
                    # If it's just the ID, we need to fetch the payment intent
                    try:
                        payment_intent_obj = stripe_service.retrieve_payment_intent(payment_intent)
                        client_secret = payment_intent_obj.get("client_secret")
                    except Exception:
                        # Continue without client secret if it fails
                        pass
                        
            return {
                "subscription_id": new_sub.id,
                "stripe_subscription_id": subscription["id"],
                "status": subscription["status"],
                "client_secret": client_secret,
            }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating subscription: {str(e)}",
        )

@router.post("/create-setup-intent")
async def create_setup_intent(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a SetupIntent for collecting payment method
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
            try:
                customer = stripe_service.create_customer(
                    email=current_user.email,
                    name=current_user.full_name,
                )
                customer_id = customer["id"]
            except Exception as customer_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error creating Stripe customer: {str(customer_error)}"
                )
                
        # Create a SetupIntent
        setup_intent = stripe_service.create_setup_intent(customer_id)
        
        # If we created a new customer, store it with the user
        if not existing_sub:
            sub_create = SubscriptionCreate(
                user_id=current_user.id,
                stripe_customer_id=customer_id,
                plan="pending",
                status="incomplete",
            )
            subscription_service.create_subscription(
                db=db, subscription_in=sub_create
            )
        elif not existing_sub.stripe_customer_id:
            sub_update = SubscriptionUpdate(stripe_customer_id=customer_id)
            subscription_service.update_subscription(
                db=db, db_subscription=existing_sub, subscription_in=sub_update
            )
            
        return {
            "client_secret": setup_intent.client_secret,
            "customer_id": customer_id,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating SetupIntent: {str(e)}",
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

@router.post("/cancel")
async def cancel_subscription(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Cancel the user's Stripe subscription
    """
    subscription = subscription_service.get_subscription_by_user_id(
        db=db, user_id=current_user.id
    )
    
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=404,
            detail="Active subscription not found"
        )
        
    try:
        # Cancel subscription in Stripe
        stripe_service.cancel_subscription(subscription.stripe_subscription_id)
        
        # Update subscription status in our database
        sub_update = SubscriptionUpdate(status="cancelled")
        updated_sub = subscription_service.update_subscription(
            db=db, db_subscription=subscription, subscription_in=sub_update
        )
        
        return {
            "status": "success",
            "subscription_id": updated_sub.id,
            "status": updated_sub.status
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error cancelling subscription: {str(e)}"
        )

@router.post("/create-checkout-session")
async def create_checkout_session(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: dict = Body(...),
) -> Any:
    """
    Create a Stripe Checkout session for subscription purchase
    """
    # Extract price_id from the request body
    price_id = data.get("price_id")
    success_url = data.get("success_url")
    cancel_url = data.get("cancel_url")
    
    if not price_id:
        raise HTTPException(
            status_code=422,
            detail="price_id is required"
        )
        
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
            try:
                customer = stripe_service.create_customer(
                    email=current_user.email,
                    name=current_user.full_name,
                )
                customer_id = customer["id"]
                
                # If we created a new customer, store the relationship
                if not existing_sub:
                    sub_create = SubscriptionCreate(
                        user_id=current_user.id,
                        stripe_customer_id=customer_id,
                        plan="pending",
                        status="incomplete",
                    )
                    subscription_service.create_subscription(
                        db=db, subscription_in=sub_create
                    )
            except Exception as customer_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error creating Stripe customer: {str(customer_error)}"
                )
        
        # Create the checkout session
        checkout_args = {
            "price_id": price_id,
            "customer_id": customer_id,
        }
        
        # Add optional parameters if provided
        if success_url:
            checkout_args["success_url"] = success_url
        if cancel_url:
            checkout_args["cancel_url"] = cancel_url
            
        checkout_session = stripe_service.create_checkout_session(**checkout_args)
        
        return {
            "session_id": checkout_session.id,
            "checkout_url": checkout_session.url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating checkout session: {str(e)}"
        )

@router.get("/verify-session")
async def verify_session(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_id: str,
) -> Any:
    """
    Verify a Stripe Checkout session status and update subscription if needed
    """
    try:
        # Retrieve the session from Stripe
        session = stripe_service.retrieve_checkout_session(session_id)
        
        # If the payment was successful
        if session.get("status") == "complete":
            # Check if the session has subscription and customer data
            subscription_id = session.get("subscription")
            customer_id = session.get("customer")
            
            # Extract string IDs from objects if needed
            if subscription_id and hasattr(subscription_id, "id"):
                subscription_id = subscription_id.id
            
            if customer_id and hasattr(customer_id, "id"):
                customer_id = customer_id.id
            
            if subscription_id and customer_id:
                # Find the subscription in our database
                db_subscription = subscription_service.get_subscription_by_user_id(
                    db, current_user.id
                )
                
                if db_subscription:
                    # Update the subscription with the Stripe data if needed
                    update_needed = False
                    update_data = {}
                    
                    # Update Stripe subscription ID if not set or different
                    if not db_subscription.stripe_subscription_id or db_subscription.stripe_subscription_id != subscription_id:
                        update_data["stripe_subscription_id"] = subscription_id
                        update_needed = True
                    
                    # Update customer ID if not set or different
                    if not db_subscription.stripe_customer_id or db_subscription.stripe_customer_id != customer_id:
                        update_data["stripe_customer_id"] = customer_id
                        update_needed = True
                    
                    # Update status to active if not already
                    if db_subscription.status != "active":
                        update_data["status"] = "active"
                        update_needed = True
                        
                    # Update the subscription in database if needed
                    if update_needed:
                        sub_update = SubscriptionUpdate(**update_data)
                        subscription_service.update_subscription(
                            db=db, db_subscription=db_subscription, subscription_in=sub_update
                        )
                        # Refresh the subscription data
                        db_subscription = subscription_service.get_subscription_by_id(
                            db, db_subscription.id
                        )
                    
                    # Return the updated subscription details
                    return {
                        "session_id": session_id,
                        "status": session.get("status"),
                        "subscription_id": db_subscription.id,
                        "subscription_status": db_subscription.status,
                        "is_active": db_subscription.status == "active",
                        "plan": db_subscription.plan
                    }
                else:
                    # This should rarely happen - customer paid but we have no record
                    # Create a new subscription record
                    try:
                        # Get Stripe subscription data to find the price/plan
                        stripe_sub = stripe_service.retrieve_subscription(subscription_id)
                        plan = None
                        if stripe_sub and stripe_sub.get("items") and stripe_sub["items"].get("data") and len(stripe_sub["items"]["data"]) > 0:
                            plan = stripe_sub["items"]["data"][0].get("price", {}).get("id")
                        
                        # Create the subscription in our database
                        sub_create = SubscriptionCreate(
                            user_id=current_user.id,
                            stripe_customer_id=customer_id,
                            stripe_subscription_id=subscription_id,
                            plan=plan or "price_unknown",
                            status="active",
                        )
                        new_sub = subscription_service.create_subscription(
                            db=db, subscription_in=sub_create
                        )
                        
                        return {
                            "session_id": session_id,
                            "status": session.get("status"),
                            "subscription_id": new_sub.id,
                            "subscription_status": new_sub.status,
                            "is_active": new_sub.status == "active",
                            "plan": new_sub.plan
                        }
                    except Exception as e:
                        # If we can't create the subscription, at least inform the user it was successful
                        return {
                            "session_id": session_id,
                            "status": session.get("status"),
                            "error": f"Payment successful but error syncing subscription: {str(e)}",
                            "is_active": False,
                        }
        
        # If the session isn't complete
        return {
            "session_id": session_id,
            "status": session.get("status", "unknown"),
            "is_active": False,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error verifying session: {str(e)}"
        ) 