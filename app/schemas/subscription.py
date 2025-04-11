from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# Shared properties
class SubscriptionBase(BaseModel):
    plan: str
    status: str

# Properties to receive via API on creation
class SubscriptionCreate(SubscriptionBase):
    user_id: UUID
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

# Properties to receive via API on update
class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    status: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

# Properties shared by models stored in DB
class SubscriptionInDBBase(SubscriptionBase):
    id: UUID
    user_id: UUID
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Subscription(SubscriptionInDBBase):
    pass

# Properties stored in DB
class SubscriptionInDB(SubscriptionInDBBase):
    pass 