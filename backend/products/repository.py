from .models import Product
from core.database import products_collection
from bson import ObjectId
from products.models import Product
from typing import Dict, List, Optional, Any
from core.constants.filter_constants import PRICE_RANGES


class ProductRepository:

    @staticmethod
    def get_top_deals(limit: int, skip: int = 0):
        # DUMMY IMPLEMENTATION
        # CHANGE THIS LATER

        # Get the total count without pulling data into Python
        total_count = products_collection.count_documents({})
        
        # Fetch only the slice needed
        items = list(products_collection.find({}).skip(skip).limit(limit))
        
        validated_items = []
        for item in items:
            # 1. Manual transform of the ID
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
            
            # 2. Ensure all fields have defaults if missing
            # Set defaults for fields that might be missing
            if "product_description" not in item:
                item["product_description"] = None
            if "available_sizes" not in item:
                item["available_sizes"] = None
            if "product_color" not in item:
                item["product_color"] = None
            
            # 3. Validation: This is where Pydantic checks the data
            # If the data doesn't match ProductSchema, it raises a ValidationError
            try:
                validated_product = Product(**item)
                # 4. Convert back to dict or keep as object
                validated_items.append(validated_product.model_dump())
            except Exception as e:
                # Skip invalid products instead of crashing
                print(f"Error validating product: {e}")
                continue
            
        return len(validated_items), validated_items

    @staticmethod
    def get_products(limit: int, skip: int):
        # DUMMY IMPLEMENTATION
        # CHANGE THIS LATER
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

    @staticmethod
    def get_best_deals(limit: int):
        """Get products with largest discount difference (original_price - sale_price), sorted by discount_value descending."""
        pipeline = [
            # Match products that have both original_price and sale_price as numbers
            {
                "$match": {
                    "original_price": {"$exists": True, "$ne": None, "$type": "number", "$gt": 0},
                    "sale_price": {"$exists": True, "$ne": None, "$type": "number", "$gt": 0}
                }
            },
            # Calculate discount difference (original_price - sale_price)
            {
                "$addFields": {
                    "discount_value": {
                        "$subtract": ["$original_price", "$sale_price"]
                    }
                }
            },
            # Only include products with positive discount (sale_price < original_price)
            {
                "$match": {
                    "discount_value": {"$gt": 0}
                }
            },
            # Sort by discount_value descending (highest difference first)
            {
                "$sort": {"discount_value": -1}
            },
            # Limit results
            {
                "$limit": limit
            },
            # Project fields and convert _id to id
            {
                "$project": {
                    "_id": 0,
                    "id": {"$toString": "$_id"},
                    "discount_value": 1,
                    "original_price": 1,
                    "sale_price": 1,
                    "product_name": 1,
                    "product_image": 1,
                    "brand_name": 1,
                    "product_category": 1,
                    "product_sub_category": 1,
                    "product_gender": 1,
                    "product_description": 1,
                    "product_color": 1,
                    "product_material": 1,
                    "product_occasion": 1,
                    "currency": 1,
                    "discount": 1,
                    "search_tags": 1,
                    "available_sizes": 1,
                    "product_link": 1,
                    "scraped_at": 1
                }
            }
        ]
        
        items = list(products_collection.aggregate(pipeline))
        total = len(items)
        
        return total, items

 


    @staticmethod
    def get_latest_products(limit: int, skip: int):
        """Get newest products sorted by scraped_at (or _id fallback) descending."""
        products = (
            products_collection.find({})
            .sort([("scraped_at", -1), ("_id", -1)])
            .skip(skip)
            .limit(limit)
        )
        items = list(products)
        total = products_collection.count_documents({})

        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]

        return total, items

    @staticmethod
    def get_filter_metadata():
        """Get filter metadata (categories, brands, occasions) with counts from database."""
        # Get unique categories with counts
        category_pipeline = [
            {"$match": {"product_category": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$product_category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        categories = list(products_collection.aggregate(category_pipeline))
        
        # Get unique brands with counts
        brand_pipeline = [
            {"$match": {"brand_name": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$brand_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        brands = list(products_collection.aggregate(brand_pipeline))
        
        # Get unique occasions with counts
        occasion_pipeline = [
            {"$match": {"product_occasion": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$product_occasion", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        occasions = list(products_collection.aggregate(occasion_pipeline))
        
        return {
            "categories": categories,
            "brands": brands,
            "occasions": occasions
        }

    @staticmethod
    def get_filtered_products(
        limit: int,
        skip: int,
        category: Optional[List[str]] = None,
        brand: Optional[List[str]] = None,
        occasion: Optional[List[str]] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        gender: Optional[str] = None
    ):
        """Get products with filters applied. Sorting is handled on the frontend."""
        from bson.regex import Regex
        
        query = {}
        
        # Category filter - convert from frontend format (lowercase-dashes) back to match database
        if category and len(category) > 0:
            # Frontend sends values like "electronics" or "electronics-clothing"
            # Database has values like "Electronics" or "Electronics & Clothing"
            # Use regex to match case-insensitively, converting dashes to spaces/ampersands
            category_patterns = []
            for cat in category:
                # Convert dash-separated back to space/ampersand pattern
                pattern = cat.replace("-", "[-\\s&]+")
                category_patterns.append(pattern)
            category_regex_list = [Regex(pattern, "i") for pattern in category_patterns]
            query["product_category"] = {"$in": category_regex_list}
        
        # Brand filter - similar conversion
        if brand and len(brand) > 0:
            brand_patterns = []
            for b in brand:
                # Convert dash-separated back to space/ampersand pattern
                pattern = b.replace("-", "[-\\s&]+")
                brand_patterns.append(pattern)
            brand_regex_list = [Regex(pattern, "i") for pattern in brand_patterns]
            query["brand_name"] = {"$in": brand_regex_list}
        
        # Occasion filter
        if occasion and len(occasion) > 0:
            occasion_patterns = []
            for occ in occasion:
                # Convert dash-separated back to space/ampersand pattern
                pattern = occ.replace("-", "[-\\s&]+")
                occasion_patterns.append(pattern)
            occasion_regex_list = [Regex(pattern, "i") for pattern in occasion_patterns]
            query["product_occasion"] = {"$in": occasion_regex_list}
        
        # Gender filter
        if gender:
            query["product_gender"] = Regex(gender, "i")
        
        # Price filter
        price_query = {}
        if price_min is not None:
            price_query["$gte"] = price_min
        if price_max is not None:
            price_query["$lte"] = price_max
        if price_query:
            # Check both original_price and sale_price
            query["$or"] = [
                {"original_price": price_query},
                {"sale_price": price_query}
            ]
        
        # Get total count
        total = products_collection.count_documents(query)
        
        # Get filtered items (no sorting - handled on frontend)
        items = list(
            products_collection.find(query)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        
        return total, items