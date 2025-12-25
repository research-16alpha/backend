from .models import Product
from core.database import products_collection
from bson import ObjectId
from products.models import Product
from typing import Dict, List, Optional, Any
from core.constants.filter_constants import PRICE_RANGES


class ProductRepository:
    # Common filter for product_image: must exist, be a string, not empty, and start with "http"
    IMAGE_FILTER = {
        "product_image": {
            "$exists": True,
            "$type": "string",
            "$ne": "",
            "$regex": "^http"
        }
    }

    @staticmethod
    def get_top_deals(limit: int, skip: int = 0):
        # DUMMY IMPLEMENTATION
        # CHANGE THIS LATER

        # Get the total count without pulling data into Python
        total_count = products_collection.count_documents(ProductRepository.IMAGE_FILTER)
        
        # Fetch only the slice needed
        items = list(products_collection.find(ProductRepository.IMAGE_FILTER).skip(skip).limit(limit))
        
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
        total = products_collection.count_documents(ProductRepository.IMAGE_FILTER)
        items = list(products_collection.find(ProductRepository.IMAGE_FILTER).skip(skip).limit(limit))
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        return total, items

    @staticmethod
    def get_product_by_id(product_id: str):
        query = {"_id": ObjectId(product_id)}
        query.update(ProductRepository.IMAGE_FILTER)
        item = products_collection.find_one(query)
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
        # Add image filter
        query.update(ProductRepository.IMAGE_FILTER)
        
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
        """Get products filtered by gender. Includes unisex and unknown genders for both men and women queries."""
        from bson.regex import Regex

        # Normalize gender input to lowercase for comparison
        gender_lower = gender.lower()
        
        # Build gender query - include unisex and unknown for both men and women
        gender_patterns = []
        
        # Add the requested gender
        gender_patterns.append(Regex(gender, "i"))
        
        # For men or women queries, also include unisex and unknown
        if gender_lower in ['men', 'women', 'male', 'female']:
            gender_patterns.append(Regex("unisex", "i"))
            gender_patterns.append(Regex("unknown", "i"))
        
        # Use $in with list of regex patterns for multiple matches
        query = {"product_gender": {"$in": gender_patterns}}
        
        # Add image filter
        query.update(ProductRepository.IMAGE_FILTER)
        
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
        """
        Get products with largest discount difference, 
        optionally filtered by a list of brand names.
        """
        brand_names = [
            "Brioni", "Brunello Cucinelli", "Zegna", "Bottega Veneta", 
            "Canali", "Polo Ralph Lauren", "John Lobb", "Johnstons Of Elgin", "Kiton", 
            "LOEWE", "N.Peal", "Prada", "Saint Laurent", "Ralph Lauren Purple Label", 
            "Salvatore Ferragamo", "Santoni", "Zimmermann", "FARM Rio", "Chrome Hearts", 
            "Alexander McQueen", "Dolce & Gabbana", "Dolce&Gabbana", 
            "Christian Louboutin", "Maje", "Sandro Paris", "Missoni", "Johanna Ortiz", 
            "Gabriela Hearst", "Cartier", "Marina Rinaldi", "Christopher Esber", 
            "Oscar de la Renta", "Derek Rose", "Falke", "Etro", "ETRO", "Balenciaga", 
            "Bally", "JACQUEMUS", "Jacquemus", "Giorgio Armani", "Canada Goose", 
            "AMI Paris", "Yves Salomon", "Corneliani", "MACKAGE", "AG Jeans", 
            "Fear of God", "Orlebar Brown", "EVISU", "BAPE", "A BATHING APE®", 
            "AAPE BY *A BATHING APE®", "Lanvin" , "Versace", 
            "TOD's", "Tod's", "AllSaints", "ALLSAINTS", "Balmain", "Burberry", 
            "Chloé", "Common Projects", "Fleur du Mal", "Fendi", "FERRAGAMO", 
            "Ferragamo", "Gucci", "Hanro", "Helmut Lang", "Herno", "Heron Preston", 
            "Hogan", "Isabel Marant", "Isabel Marant Etoile", "ISSEY MIYAKE", 
            "Issey Miyake", "J.Lindeberg", "Jimmy Choo", "Kenzo", "Ksubi", "lululemon", 
            "Mackage", "Lladró", "Maison Margiela", "Marc Jacobs", "Palm Angels", 
            "Palm Angels Kids", "Paige", "PAIGE", "Moschino", "Off-White", 
            "Off-White Kids" , "RHUDE", "Rhude", "Roberto Cavalli", "Theory", 
            "Stüssy", "Stone Island", "Vilebrequin"
        ]
        # 1. Start the match stage with your price validation and image filter
        match_filter = {
            "original_price": {"$exists": True, "$ne": None, "$type": "number", "$gt": 0},
            "sale_price": {"$exists": True, "$ne": None, "$type": "number", "$gt": 0},
            "product_image": {
                "$exists": True, 
                "$type": "string", 
                "$ne": "",
                "$regex": "^http"  # Filter out products without images (null, empty, or not starting with http)
            }
        }

        # 2. Add the brand filter if brand_names list is provided
        if brand_names and len(brand_names) > 0:
            match_filter["brand_name"] = {"$in": brand_names}

        pipeline = [
            # Match products that meet price criteria AND belong to the selected brands
            { "$match": match_filter },
            
            # Calculate discount difference (original_price - sale_price)
            {
                "$addFields": {
                    "discount_value": {
                        "$subtract": ["$original_price", "$sale_price"]
                    }
                }
            },
            # Only include products with positive discount
            { "$match": { "discount_value": {"$gt": 0} } },
            
            # Sort by discount_value descending (highest difference first)
            { "$sort": {"discount_value": -1} },
            
            # Limit results
            { "$limit": limit },
            
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
        return len(items), items


    @staticmethod
    def get_latest_products(limit: int, skip: int):
        """Get newest products sorted by scraped_at (or _id fallback) descending."""
        products = (
            products_collection.find(ProductRepository.IMAGE_FILTER)
            .sort([("scraped_at", -1), ("_id", -1)])
            .skip(skip)
            .limit(limit)
        )
        items = list(products)
        total = products_collection.count_documents(ProductRepository.IMAGE_FILTER)

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
        
        # Gender filter - include unisex and unknown for all gender queries
        if gender:
            gender_patterns = [Regex(gender, "i")]
            # Always include unisex and unknown genders
            gender_patterns.append(Regex("unisex", "i"))
            gender_patterns.append(Regex("unknown", "i"))
            query["product_gender"] = {"$in": gender_patterns}
        
        # Price filter - filter by sale_price only (the price customers actually pay)
        if price_min is not None or price_max is not None:
            price_query = {}
            if price_min is not None:
                price_query["$gte"] = price_min
            if price_max is not None:
                price_query["$lte"] = price_max
            # Filter only by sale_price
            query["sale_price"] = price_query
        
        # Add image filter
        query.update(ProductRepository.IMAGE_FILTER)
        
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


    @staticmethod
    def get_products_with_custom_sort(limit: int, skip: int = 0):
        """Get products sorted by custom brand order and scraped_at."""

        print("custom sort api called")
        # Your hardcoded brand order
        brand_order = ['Brioni', 'Brunello Cucinelli', 'Zegna', 'TOM FORD', 'Bottega Veneta', 'Canali', 'Polo Ralph Lauren', 'John Lobb', 'Johnstons Of Elgin', 'Kiton', 'LOEWE', 'N.Peal', 'Prada', 'Saint Laurent', 'Ralph Lauren Purple Label', 'Salvatore Ferragamo', 'Santoni', 'Zimmermann', 'FARM Rio', 'Chrome Hearts', 'Alexander McQueen', 'Valentino', 'Dolce & Gabbana', 'Dolce&Gabbana', 'Christian Louboutin', 'Maje', 'Sandro Paris', 'Missoni', 'Johanna Ortiz', 'Gabriela Hearst', 'Cartier', 'Marina Rinaldi', 'Christopher Esber', 'Oscar de la Renta', 'Derek Rose', 'Falke', 'Etro', 'ETRO', 'Balenciaga', 'Bally', 'JACQUEMUS', 'Jacquemus', 'Giorgio Armani', 'Canada Goose', 'AMI Paris', 'Yves Salomon', 'Corneliani', 'MACKAGE', 'AG Jeans', 'Fear of God', 'Orlebar Brown', 'EVISU', 'BAPE', 'A BATHING APE®', 'AAPE BY *A BATHING APE®', 'Lanvin', 'Valentino Garavani', 'Versace', "TOD's", "Tod's", 'AllSaints', 'ALLSAINTS', 'Balmain', 'Burberry', 'Chloé', 'Common Projects', 'Fleur du Mal', 'Fendi', 'FERRAGAMO', 'Ferragamo', 'Gucci', 'Hanro', 'Helmut Lang', 'Herno', 'Heron Preston', 'Hogan', 'Isabel Marant', 'Isabel Marant Etoile', 'ISSEY MIYAKE', 'Issey Miyake', 'J.Lindeberg', 'Jimmy Choo', 'Kenzo', 'Ksubi', 'lululemon', 'Mackage', 'Lladró', 'Maison Margiela', 'Marc Jacobs', 'Palm Angels', 'Palm Angels Kids', 'Paige', 'PAIGE', 'Moschino', 'Off-White', 'Off-White Kids', 'Rick Owens', 'Rick Owens DRKSHDW', 'Rick Owens Lilies', 'Rick Owens X Champion', 'RHUDE', 'Rhude', 'Roberto Cavalli', 'Theory', 'Stüssy', 'Stone Island', 'Vilebrequin', "Church's", 'Comme des Garçons', 'Comme Des Garçons', 'Acne Studios', 'Acqua di Parma', 'A-COLD-WALL*', 'Alexander Wang', 'alexanderwang.t', 'alice + olivia', 'Alice+Olivia', 'adidas Yeezy', 'Balmain Kids', 'BAPE BLACK *A BATHING APE®', 'BAPY BY *A BATHING APE®', 'Barbour', 'Barbour International', 'Birkenstock', 'BIRKENSTOCK 1774', 'DOMREBEL', 'VETEMENTS', 'Armani', 'Ea7 Emporio Armani', 'Ed Hardy', 'Fear Of God', 'FEAR OF GOD ESSENTIALS', 'Fear of God ESSENTIALS', 'Fear of God Athletics', 'FEAR OF GOD ESSENTIALS KIDS', 'Fendi Kids', 'FRAME', 'Giuseppe Zanotti', 'Givenchy', 'Gianvito Rossi', 'La Perla', 'Eileen Fisher', 'Elie Tahari', 'Eleventy', 'Emporio Armani', 'Dita Eyewear', 'TOM FORD Eyewear', 'Cartier Eyewear', 'Dolce & Gabbana Eyewear', 'Prada Eyewear', 'Gucci Eyewear', 'Alexander McQueen Eyewear', 'Balenciaga Eyewear', 'Chloé Eyewear', 'Balmain Eyewear', 'Palm Angels Eyewear', 'Burberry Eyewear', 'Givenchy Eyewear', 'Jimmy Choo Eyewear', 'Off-White Eyewear', 'Versace Eyewear', 'Hermès\xa0Pre-Owned', 'CHANEL Pre-Owned', 'Bottega Veneta Pre-Owned', 'Christian Dior Pre-Owned', 'Balenciaga Pre-Owned', 'Celine Pre-Owned', 'Fendi Pre-Owned', 'Goyard Pre-Owned', 'Gucci Pre-Owned', 'Loewe Pre-Owned', 'Louis Vuitton Pre-Owned', 'Prada Pre-Owned', 'Versace Pre-Owned', 'MEMO PARIS', 'Bond No. 9', 'Bobbi Brown', 'Estée Lauder', 'Jo Malone London', 'La Prairie', 'Kerastase', "Kiehl's", 'Lancôme', 'Prada Beauty']
        
        # Match filter for products with valid dual pricing and sale_price > 1000
        match_filter = {
            "original_price": {"$exists": True, "$ne": None, "$type": "number", "$gt": 0},
            "sale_price": {"$exists": True, "$ne": None, "$type": "number", "$gt": 1000},
            "$expr": {"$ne": ["$original_price", "$sale_price"]}
        }
        # Add image filter
        match_filter.update(ProductRepository.IMAGE_FILTER)
        
        # Get total count of products with valid dual pricing
        total = products_collection.count_documents(match_filter)
        
        pipeline = [
            # Match only products with valid dual pricing (both prices exist and are different)
            {
                "$match": match_filter
            },
            {
                "$addFields": {
                    "brand_index": {
                        "$indexOfArray": [brand_order, "$brand_name"]
                    }
                }
            },
            {
                # If a brand isn't in your list, indexOfArray returns -1.
                # We move those to the end by giving them a high priority.
                # Otherwise, assign priority based on groups of 10:
                # - First 10 brands (indices 0-9): priority 0
                # - Next 10 brands (indices 10-19): priority 1
                # - Next 10 brands (indices 20-29): priority 2
                # - And so on...
                "$addFields": {
                    "brand_priority": {
                        "$cond": { 
                            "if": { "$eq": ["$brand_index", -1] }, 
                            "then": 999, 
                            "else": {
                                "$floor": {
                                    "$divide": ["$brand_index", 3]
                                }
                            }
                        }
                    }
                }
            },
            { "$sort": { "brand_priority": 1, "scraped_at": -1 } },
            { "$skip": skip },
            { "$limit": limit },
            # Project all fields needed for transform_product
            {
                "$project": {
                    "_id": 1,
                    "product_link": 1,
                    "product_image": 1,
                    "brand_name": 1,
                    "product_name": 1,
                    "product_description": 1,
                    "product_category": 1,
                    "product_sub_category": 1,
                    "product_gender": 1,
                    "product_color": 1,
                    "product_material": 1,
                    "product_occasion": 1,
                    "currency": 1,
                    "original_price": 1,
                    "sale_price": 1,
                    "discount": 1,
                    "search_tags": 1,
                    "available_sizes": 1,
                    "scraped_at": 1
                }
            }
        ]
        
        items = list(products_collection.aggregate(pipeline))
        
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        
        return total, items

    @staticmethod
    def search_products(
        query: str,
        limit: int = 20,
        skip: int = 0,
        category: Optional[List[str]] = None,
        brand: Optional[List[str]] = None,
        occasion: Optional[List[str]] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        gender: Optional[str] = None
    ):
        """
        Search products using MongoDB Atlas Search with fuzzy matching.
        Searches across all text fields using wildcard path.
        """
        from bson.regex import Regex
        
        # Build the aggregation pipeline
        pipeline = []
        
        # Step 1: $search stage - MongoDB Atlas Search
        search_stage = {
            "$search": {
                "index": "default",  # The name of your search index
                "text": {
                    "query": query,
                    "path": {"wildcard": "*"},  # Searches all fields
                    "fuzzy": {}  # Allows for typos
                }
            }
        }
        pipeline.append(search_stage)
        
        # Step 2: Add filters if provided (using $match after search)
        match_filters = {}
        
        # Add image filter first
        match_filters.update(ProductRepository.IMAGE_FILTER)
        
        # Category filter
        if category and len(category) > 0:
            category_patterns = []
            for cat in category:
                pattern = cat.replace("-", "[-\\s&]+")
                category_patterns.append(pattern)
            category_regex_list = [Regex(pattern, "i") for pattern in category_patterns]
            match_filters["product_category"] = {"$in": category_regex_list}
        
        # Brand filter
        if brand and len(brand) > 0:
            brand_patterns = []
            for b in brand:
                pattern = b.replace("-", "[-\\s&]+")
                brand_patterns.append(pattern)
            brand_regex_list = [Regex(pattern, "i") for pattern in brand_patterns]
            match_filters["brand_name"] = {"$in": brand_regex_list}
        
        # Occasion filter
        if occasion and len(occasion) > 0:
            occasion_patterns = []
            for occ in occasion:
                pattern = occ.replace("-", "[-\\s&]+")
                occasion_patterns.append(pattern)
            occasion_regex_list = [Regex(pattern, "i") for pattern in occasion_patterns]
            match_filters["product_occasion"] = {"$in": occasion_regex_list}
        
        # Gender filter
        if gender:
            match_filters["product_gender"] = Regex(gender, "i")
        
        # Price filter - filter by sale_price only
        if price_min is not None or price_max is not None:
            price_query = {}
            if price_min is not None:
                price_query["$gte"] = price_min
            if price_max is not None:
                price_query["$lte"] = price_max
            match_filters["sale_price"] = price_query
        
        # Add $match stage if we have filters
        if match_filters:
            pipeline.append({"$match": match_filters})
        
        # Step 3: Add score for relevance ranking
        pipeline.append({
            "$addFields": {
                "searchScore": {"$meta": "searchScore"}
            }
        })
        
        # Step 4: Sort by search score (most relevant first)
        pipeline.append({
            "$sort": {"searchScore": -1}
        })
        
        # Step 5: Skip and limit for pagination
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": limit})
        
        # Step 6: Project fields and convert _id to id
        pipeline.append({
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "product_link": 1,
                "product_image": 1,
                "brand_name": 1,
                "product_name": 1,
                "product_description": 1,
                "product_category": 1,
                "product_sub_category": 1,
                "product_gender": 1,
                "product_color": 1,
                "product_material": 1,
                "product_occasion": 1,
                "currency": 1,
                "original_price": 1,
                "sale_price": 1,
                "discount": 1,
                "search_tags": 1,
                "available_sizes": 1,
                "scraped_at": 1,
                "searchScore": 1
            }
        })
        
        # Execute the aggregation pipeline
        try:
            # Get total count first using $facet to get both count and results
            count_pipeline = pipeline[:-3]  # Remove skip, limit, and project stages
            count_pipeline.append({"$count": "total"})
            
            # Execute count pipeline
            count_result = list(products_collection.aggregate(count_pipeline))
            total = count_result[0]["total"] if count_result else 0
            
            # Execute main pipeline to get results
            items = list(products_collection.aggregate(pipeline))
            
            return total, items
        except Exception as e:
            # If search index doesn't exist or search fails, fall back to text search
            print(f"Search index error: {e}. Falling back to text search.")
            # Fallback to regex-based search
            return ProductRepository._fallback_text_search(
                query, limit, skip, category, brand, occasion, price_min, price_max, gender
            )
    
    @staticmethod
    def _fallback_text_search(
        query: str,
        limit: int,
        skip: int,
        category: Optional[List[str]] = None,
        brand: Optional[List[str]] = None,
        occasion: Optional[List[str]] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        gender: Optional[str] = None
    ):
        """Fallback text search using regex if Atlas Search is not available."""
        from bson.regex import Regex
        
        # Build query with text search
        search_query = {
            "$or": [
                {"product_name": Regex(query, "i")},
                {"product_description": Regex(query, "i")},
                {"brand_name": Regex(query, "i")},
                {"product_category": Regex(query, "i")},
                {"search_tags": Regex(query, "i")}
            ]
        }
        # Add image filter
        search_query.update(ProductRepository.IMAGE_FILTER)
        
        # Add other filters
        if category and len(category) > 0:
            category_patterns = []
            for cat in category:
                pattern = cat.replace("-", "[-\\s&]+")
                category_patterns.append(pattern)
            category_regex_list = [Regex(pattern, "i") for pattern in category_patterns]
            search_query["product_category"] = {"$in": category_regex_list}
        
        if brand and len(brand) > 0:
            brand_patterns = []
            for b in brand:
                pattern = b.replace("-", "[-\\s&]+")
                brand_patterns.append(pattern)
            brand_regex_list = [Regex(pattern, "i") for pattern in brand_patterns]
            search_query["brand_name"] = {"$in": brand_regex_list}
        
        if occasion and len(occasion) > 0:
            occasion_patterns = []
            for occ in occasion:
                pattern = occ.replace("-", "[-\\s&]+")
                occasion_patterns.append(pattern)
            occasion_regex_list = [Regex(pattern, "i") for pattern in occasion_patterns]
            search_query["product_occasion"] = {"$in": occasion_regex_list}
        
        if gender:
            search_query["product_gender"] = Regex(gender, "i")
        
        if price_min is not None or price_max is not None:
            price_query = {}
            if price_min is not None:
                price_query["$gte"] = price_min
            if price_max is not None:
                price_query["$lte"] = price_max
            search_query["sale_price"] = price_query
        
        total = products_collection.count_documents(search_query)
        items = list(products_collection.find(search_query).skip(skip).limit(limit))
        
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        
        return total, items
    
    @staticmethod
    def get_search_suggestions(query: str, limit: int = 10):
        """
        Get search suggestions/autocomplete using MongoDB Atlas Search.
        Returns suggested search terms based on partial query.
        Note: Autocomplete requires specific field paths, not wildcards.
        """
        # Use text search instead of autocomplete since we want to search across multiple fields
        # Autocomplete requires specific field paths and is typically used for single fields
        pipeline = [
            {
                "$search": {
                    "index": "default",
                    "text": {
                        "query": query,
                        "path": ["product_name", "brand_name", "product_category", "search_tags"],
                        "fuzzy": {
                            "maxEdits": 1
                        }
                    }
                }
            },
            # Filter by image after search
            {
                "$match": ProductRepository.IMAGE_FILTER
            },
            {
                "$limit": limit * 3  # Get more results to extract unique suggestions
            },
            {
                "$project": {
                    "_id": 0,
                    "product_name": 1,
                    "brand_name": 1,
                    "product_category": 1,
                    "score": {"$meta": "searchScore"}
                }
            }
        ]
        
        try:
            results = list(products_collection.aggregate(pipeline))
            
            # Extract unique suggestions from results
            suggestions = set()
            for result in results:
                if result.get("product_name"):
                    # Add product name if it contains the query
                    if query.lower() in result["product_name"].lower():
                        suggestions.add(result["product_name"])
                if result.get("brand_name"):
                    # Add brand name if it contains the query
                    if query.lower() in result["brand_name"].lower():
                        suggestions.add(result["brand_name"])
                if result.get("product_category"):
                    # Add category if it contains the query
                    if query.lower() in result["product_category"].lower():
                        suggestions.add(result["product_category"])
            
            # Return as list, limited to requested limit, sorted by relevance
            return list(suggestions)[:limit]
        except Exception as e:
            # Fallback: return empty suggestions if search index not available
            print(f"Search suggestions error: {e}")
            return []
    
    @staticmethod
    def get_products_by_links(product_links: List[str]):
        """
        Get products by product_link values, returning them in the exact order
        of the provided links list.
        """
        if not product_links:
            return []
        
        # Query products with matching product_links
        query = {"product_link": {"$in": product_links}}
        query.update(ProductRepository.IMAGE_FILTER)
        
        items = list(products_collection.find(query))
        
        # Convert _id to id string
        for item in items:
            if "_id" in item:
                item["id"] = str(item["_id"])
                del item["_id"]
        
        # Create a mapping of product_link -> product for quick lookup
        products_map = {item.get("product_link"): item for item in items if item.get("product_link")}
        
        # Return products in the exact order of the input product_links
        ordered_products = []
        for link in product_links:
            if link in products_map:
                ordered_products.append(products_map[link])
        
        return ordered_products