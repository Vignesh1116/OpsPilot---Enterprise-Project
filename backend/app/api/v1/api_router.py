from fastapi import APIRouter
from app.api.v1.endpoints import auth, system, users

api_router = APIRouter()

# Core system / health routes
api_router.include_router(system.router, prefix="/system", tags=["System & Health"])

# Authentication & RBAC routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & RBAC"])
