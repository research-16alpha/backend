from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List

from .repository import UserRepository
from .service import UserService
from .models import User, RegisterRequest, LoginRequest


# Create a singleton async client
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

_async_client = None
_async_db = None

def get_async_db():
    global _async_client, _async_db
    if _async_db is None:
        _async_client = AsyncIOMotorClient(settings.MONGODB_URI)
        _async_db = _async_client[settings.DATABASE_NAME]
    return _async_db

def get_user_service():
    async_db = get_async_db()
    repo = UserRepository(async_db)
    return UserService(repo)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/oauth-login", response_model=User)
async def oauth_login(payload: Dict, service: UserService = Depends(get_user_service)):
    """
    Called after Google OAuth login.
    payload example:
    {
      "name": "...",
      "email": "...",
      "avatar": "...",
      "google_id": "...",
      "created_at": "2025-12-10T08:18:43.189Z"
    }
    """
    user = await service.login_or_register_user(payload)
    return user


@router.post("/{user_id}/favourites/{product_id}")
async def add_favourite(user_id: str, product_id: str, service: UserService = Depends(get_user_service)):
    await service.add_to_favourites(user_id, product_id)
    return {"status": "added"}


@router.delete("/{user_id}/favourites/{product_id}")
async def remove_favourite(user_id: str, product_id: str, service: UserService = Depends(get_user_service)):
    await service.remove_from_favourites(user_id, product_id)
    return {"status": "removed"}


@router.post("/{user_id}/bag/{product_id}")
async def add_to_bag(user_id: str, product_id: str, service: UserService = Depends(get_user_service)):
    await service.add_to_bag(user_id, product_id)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "added", "bag": user.bag}


@router.delete("/{user_id}/bag/{product_id}")
async def remove_from_bag(user_id: str, product_id: str, service: UserService = Depends(get_user_service)):
    await service.remove_from_bag(user_id, product_id)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "removed", "bag": user.bag}


@router.put("/{user_id}/bag")
async def sync_bag(user_id: str, bag: List[str], service: UserService = Depends(get_user_service)):
    """
    Sync entire bag contents for a user.
    """
    await service.sync_bag(user_id, bag)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "synced", "bag": user.bag}


@router.post("/register", response_model=User)
async def register(request: RegisterRequest, service: UserService = Depends(get_user_service)):
    """
    Register a new user with email and password.
    """
    print("register users called with data - ", request)
    return await service.register_user(request)


@router.post("/login", response_model=User)
async def login(request: LoginRequest, service: UserService = Depends(get_user_service)):
    """
    Login with email and password.
    """
    print("login requested with payload - ",request)
    return await service.login_user(request)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
