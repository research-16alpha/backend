from .models import Product
from core.database import products_collection
from bson import ObjectId

class ProductRepository:

    @staticmethod
    def get_top_deals(limit: int):
        items = list(products_collection.find({}))
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        return items[:limit]

    @staticmethod
    def get_products(limit: int, skip: int):
        total = products_collection.count_documents({})
        items = list(products_collection.find({}).skip(skip).limit(limit))
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        return total, items

    @staticmethod
    def get_product_by_id(product_id: str):
        item = products_collection.find_one({"_id": ObjectId(product_id)})
        if item and "_id" in item:
            item["id"] = str(item["_id"])
            del item["_id"]
        return item

    @staticmethod
    def get_products_by_category(category: str, limit: int, skip: int):
        """Get products filtered by category name matching product_name or product_description."""
        from bson.regex import Regex
        
        # Case-insensitive regex search for category in product_name or product_description
        category_regex = Regex(category, "i")
        query = {
            "$or": [
                {"product_name": category_regex},
                {"product_description": category_regex}
            ]
        }
        
        total = products_collection.count_documents(query)
        items = list(products_collection.find(query).skip(skip).limit(limit))
        
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        
        return total, items

    @staticmethod
    def get_products_by_gender(gender: str, limit: int, skip: int):
        """Get products filtered by gender."""
        from bson.regex import Regex
        
        # Case-insensitive regex search for gender
        gender_regex = Regex(gender, "i")
        query = {"product_gender": gender_regex}
        
        total = products_collection.count_documents(query)
        items = list(products_collection.find(query).skip(skip).limit(limit))
        
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        
        return total, items