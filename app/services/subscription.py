from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

def get_subscription_by_id(db: Session, subscription_id: UUID) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()

def get_subscription_by_user_id(db: Session, user_id: UUID) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.user_id == user_id).first()

def get_subscription_by_stripe_id(db: Session, stripe_subscription_id: str) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_subscription_id).first()

def get_subscriptions(db: Session, skip: int = 0, limit: int = 100) -> List[Subscription]:
    return db.query(Subscription).offset(skip).limit(limit).all()

def has_active_subscription(db: Session, user_id: Union[UUID, str]) -> bool:
    """
    Check if a user has an active subscription
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        True if the user has an active subscription, False otherwise
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status.in_(["active", "trial"])
    ).first()
    
    return subscription is not None

def create_subscription(db: Session, subscription_in: SubscriptionCreate) -> Subscription:
    db_subscription = Subscription(
        user_id=subscription_in.user_id,
        stripe_customer_id=subscription_in.stripe_customer_id,
        stripe_subscription_id=subscription_in.stripe_subscription_id,
        plan=subscription_in.plan,
        status=subscription_in.status,
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def update_subscription(
    db: Session, db_subscription: Subscription, subscription_in: SubscriptionUpdate
) -> Subscription:
    update_data = subscription_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subscription, field, value)
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def delete_subscription(db: Session, subscription_id: UUID) -> bool:
    subscription = get_subscription_by_id(db, subscription_id)
    if subscription:
        db.delete(subscription)
        db.commit()
        return True
    return False 