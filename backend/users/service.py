from .repository import UserRepository
from .models import User, RegisterRequest, LoginRequest
from typing import Optional
from datetime import datetime
import bcrypt
from fastapi import HTTPException


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def login_or_register_user(self, payload: dict) -> User:

        existing = await self.repository.get_user_by_google_id(payload["google_id"])

        if existing:
            # update avatar/name if changed
            return await self.repository.update_user(payload["google_id"], payload)

        # create new user - ensure bag is initialized
        if "bag" not in payload:
            payload["bag"] = []
        if "favourites" not in payload:
            payload["favourites"] = []
        return await self.repository.create_user(payload)

    async def add_to_favourites(self, user_id: str, product_id: str):
        return await self.repository.add_favourite(user_id, product_id)

    async def remove_from_favourites(self, user_id: str, product_id: str):
        return await self.repository.remove_favourite(user_id, product_id)

    async def add_to_bag(self, user_id: str, product_id: str):
        return await self.repository.add_to_bag(user_id, product_id)

    async def remove_from_bag(self, user_id: str, product_id: str):
        return await self.repository.remove_from_bag(user_id, product_id)

    async def sync_bag(self, user_id: str, bag: list):
        """Sync entire bag contents"""
        return await self.repository.sync_bag(user_id, bag)

    async def get_user(self, user_id: str) -> Optional[User]:
        return await self.repository.get_user_by_id(user_id)

    async def register_user(self, request: RegisterRequest) -> User:
        print("inside register user")
        # Check if user already exists
        existing = await self.repository.get_user_by_email(request.email)
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user data
        user_data = {
            "name": request.name,
            "email": request.email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "favourites": [],
            "bag": []
        }
        
        # Create user
        print("create user called with data - ", user_data)
        user = await self.repository.create_user(user_data)
        return user

    async def login_user(self, request: LoginRequest) -> User:
        # Find user by email
        print("login service called")
        user = await self.repository.get_user_by_email(request.email)
        print(user)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check password
        if not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not bcrypt.checkpw(request.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        print("returning user")
        return user
