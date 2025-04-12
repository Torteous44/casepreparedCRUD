from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, subscriptions, interview_templates, interviews

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(interview_templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"]) 