from .models import Product
from core.database import products_collection
from bson import ObjectId

class ProductRepository:

    @staticmethod
    def get_top_deals(limit: int, skip: int = 0):
        items = list(products_collection.find({}).skip(skip).limit(limit))
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        return len(items), items[:limit]

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

    @staticmethod
    def get_best_deals(limit: int):
        """Get products with largest discount in dollar terms, sorted by discount_value descending."""
        items = list(products_collection.find({}))
        
        # Calculate discount_value for each product and filter out invalid ones
        products_with_discount = []
        for item in items:
            original = item.get("original_price") or item.get("price_original")
            final = item.get("sale_price") or item.get("price_final")
            
            if original and final:
                try:
                    original_float = float(str(original).replace('$', '').replace(',', '').strip())
                    final_float = float(str(final).replace('$', '').replace(',', '').strip())
                    discount_value = original_float - final_float
                    
                    if discount_value > 0:  # Only include products with actual discount
                        item["discount_value"] = discount_value
                        products_with_discount.append(item)
                except (ValueError, TypeError):
                    # Skip products with invalid price formats
                    continue
        
        # Sort by discount_value descending
        products_with_discount.sort(key=lambda x: x.get("discount_value", 0), reverse=True)
        
        # Convert _id to id string and limit results
        result = []
        for item in products_with_discount[:limit]:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
            result.append(item)
        
        return  len(result),result

    # @staticmethod
    # def get_best_deals(limit: int):
        # pipeline = [
        #                 {
        #                     "$addFields": {
        #                         "original_price_num": {
        #                             "$toDouble": {
        #                                 "$replaceAll": {
        #                                     "input": {
        #                                         "$replaceAll": {
        #                                            "input": {
        #                                                 "$ifNull": ["$original_price", "$price_original"]
        #                                             },
        #                                             "find": ",",
        #                                             "replacement": ""
        #                                         }
        #                                     },
        #                                     "find": {"$literal": "$"},
        #                                     "replacement": ""
        #                                 }
        #                             }
        #                         },
        #                         "sale_price_num": {
        #                             "$toDouble": {
        #                                 "$replaceAll": {
        #                                     "input": {
        #                                         "$replaceAll": {
        #                                             "input": {
        #                                                 "$ifNull": ["$sale_price", "$price_final"]
        #                                             },
        #                                             "find": ",",
        #                                             "replacement": ""
        #                                         }
        #                                     },
        #                                     "find": {"$literal": "$"},
        #                                     "replacement": ""
        #                                 }
        #                             }
        #                         }
        #                     }
        #                 },
        #                 {
        #                     "$addFields": {
        #                         "discount_value": {
        #                             "$subtract": ["$original_price_num", "$sale_price_num"]
        #                         }
        #                     }
        #                 },
        #                 {
        #                     "$match": {
        #                         "discount_value": {"$gt": 0}
        #                     }
        #                 },
        #                 {
        #                     "$sort": {"discount_value": -1}
        #                 },
        #                 {
        #                     "$limit": limit
        #                 },
        #                 {
        #                     "$project": {
        #                         "_id": 0,
        #                         "id": {"$toString": "$_id"},
        #                         "discount_value": 1,
        #                         "original_price": 1,
        #                         "sale_price": 1,
        #                         "product_name": 1,
        #                         "product_image": 1,
        #                         "brand_name": 1,
        #                         "product_category": 1,
        #                         "product_sub_category": 1,
        #                         "product_gender": 1,
        #                         "product_description": 1
        #                     }
        #                 }
        #             ]
        pipeline = [
            {
                "$addFields": {
                    "original_price_num": {
                        "$convert": {
                            "input": {
                                "$regexReplace": {
                                    "input": {
                                        "$ifNull": ["$original_price", "$price_original"]
                                    },
                                    "regex": "[^0-9.]",
                                    "replacement": ""
                                }
                            },
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    },
                    "sale_price_num": {
                        "$convert": {
                            "input": {
                                "$regexReplace": {
                                    "input": {
                                        "$ifNull": ["$sale_price", "$price_final"]
                                    },
                                    "regex": "[^0-9.]",
                                    "replacement": ""
                                }
                            },
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "discount_value": {
                        "$subtract": ["$original_price_num", "$sale_price_num"]
                    }
                }
            },
            {
                "$match": {
                    "discount_value": {"$gt": 0}
                }
            },
            {
                "$sort": {"discount_value": -1}
            },
            {
                "$limit": limit
            },
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
                    "product_gender": 1
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