from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from .models import User


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        data = await self.collection.find_one({"google_id": google_id})
        if data:
            data["_id"] = str(data["_id"])
            return User(**data)
        return None

    async def create_user(self, user_data: dict) -> User:
        result = await self.collection.insert_one(user_data)
        created = await self.collection.find_one({"_id": result.inserted_id})

        # Convert ObjectId → str
        created["_id"] = str(created["_id"])

        return User(**created)



    async def update_user(self, google_id: str, updates: dict) -> Optional[User]:
        await self.collection.update_one({"google_id": google_id}, {"$set": updates})
        data = await self.collection.find_one({"google_id": google_id})
        if data:
            data["_id"] = str(data["_id"])
            return User(**data)
        return None

    async def add_favourite(self, user_id: str, product_id: str):
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"favourites": product_id}}
            )
        except Exception:
            # Fall back to string id if ObjectId conversion fails
            await self.collection.update_one(
                {"_id": user_id},
                {"$addToSet": {"favourites": product_id}}
            )

    async def remove_favourite(self, user_id: str, product_id: str):
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"favourites": product_id}}
            )
        except Exception:
            await self.collection.update_one(
                {"_id": user_id},
                {"$pull": {"favourites": product_id}}
            )

    async def add_to_bag(self, user_id: str, product_id: str):
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"bag": product_id}}
            )
        except Exception:
            await self.collection.update_one(
                {"_id": user_id},
                {"$addToSet": {"bag": product_id}}
            )

    async def remove_from_bag(self, user_id: str, product_id: str):
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"bag": product_id}}
            )
        except Exception:
            await self.collection.update_one(
                {"_id": user_id},
                {"$pull": {"bag": product_id}}
            )

    async def sync_bag(self, user_id: str, bag: list):
        """Update entire bag contents"""
        from bson import ObjectId
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"bag": bag}}
            )
        except Exception:
            # If ObjectId conversion fails, try as string
            await self.collection.update_one(
                {"_id": user_id},
                {"$set": {"bag": bag}}
            )

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        print("get user called by id: ", user_id)
        from bson import ObjectId
        try:
            data = await self.collection.find_one({"_id": ObjectId(user_id)})
            if data:
                data["_id"] = str(data["_id"])
                return User(**data)
            return None
        except Exception:
            # If ObjectId conversion fails, try as string
            data = await self.collection.find_one({"_id": user_id})
            if data:
                data["_id"] = str(data["_id"])
                return User(**data)
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        data = await self.collection.find_one({"email": email})
        if data:
            data["_id"] = str(data["_id"])
            return User(**data)
        return None
