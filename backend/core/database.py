from pymongo import MongoClient
from .config import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]

products_collection = db["products"]
messages_collection = db["messages"]
users_collection = db["users"]

# Test connection
try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB")
except:
    print("❌ Failed to connect MongoDB")
