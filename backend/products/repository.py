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
    def _normalize_sizes(sizes) -> Optional[List[str]]:
        """
        Normalize available_sizes from various formats to a list of strings.
        Handles: None, empty string, list, comma-separated string.
        """
        if sizes is None:
            return None
        if isinstance(sizes, list):
            # Already a list, return as is (filter out empty strings)
            return [str(s).strip() for s in sizes if str(s).strip()]
        if isinstance(sizes, str):
            # Comma-separated string, split and clean
            if not sizes.strip():
                return None
            # Filter out "See all sizes" and other non-size values
            cleaned = [s.strip() for s in sizes.split(',') if s.strip() and s.strip().lower() != 'see all sizes']
            return cleaned if cleaned else None
        # For any other type, try to convert
        try:
            return [str(sizes).strip()] if str(sizes).strip() else None
        except:
            return None
    
    @staticmethod
    def _normalize_colors(colors) -> Optional[List[str]]:
        """
        Normalize product_color from various formats to a list of strings.
        Handles: None, empty string, list, comma-separated string.
        """
        if colors is None:
            return None
        if isinstance(colors, list):
            # Already a list, return as is (filter out empty strings)
            return [str(c).strip() for c in colors if str(c).strip()]
        if isinstance(colors, str):
            # Comma-separated string, split and clean
            if not colors.strip():
                return None
            return [c.strip() for c in colors.split(',') if c.strip()]
        # For any other type, try to convert
        try:
            return [str(colors).strip()] if str(colors).strip() else None
        except:
            return None

    @staticmethod
    def get_top_deals(limit: int, skip: int = 0):
        """
        Get top deals filtered by specific luxury brands.
        Includes common brand name variations for better matching.
        """
        # Define the list of luxury brands to filter by, including variations
        brand_names = [
            # Brunello Cucinelli
            "Brunello Cucinelli",
            
            # Brioni
            "Brioni",
            
            # Loro Piana
            "Loro Piana",
            
            # Berluti
            "Berluti",
            
            # Zegna / Ermenegildo Zegna
            "Zegna",
            "Ermenegildo Zegna",
            "ERMENEGILDO ZEGNA",
            
            # Tom Ford / TOM FORD
            "Tom Ford",
            "TOM FORD",
            
            # Kiton
            "Kiton",
            "KITON",
            
            # Ralph Lauren Purple Label
            "Ralph Lauren Purple Label",
            "RALPH LAUREN PURPLE LABEL",
            
            # Polo Ralph Lauren
            "Polo Ralph Lauren",
            "POLO RALPH LAUREN",
            
            # Salvatore Ferragamo / Ferragamo
            "Salvatore Ferragamo",
            "Ferragamo",
            "FERRAGAMO",
            
            # Canali
            "Canali",
            "CANALI",
            
            # Stefano Ricci
            "Stefano Ricci",
            "STEFANO RICCI",
            
            # Bottega Veneta
            "Bottega Veneta",
            "BOTTEGA VENETA",
            
            # Hermes / Hermès
            "Hermes",
            "Hermès",
            "HERMÈS",
            
            # Chanel
            "Chanel",
            "CHANEL",
            
            # Zimmerman / Zimmermann
            "Zimmerman",
            "Zimmermann",
            "ZIMMERMANN",
            
            # Christopher Esber
            "Christopher Esber",
            "CHRISTOPHER ESBER",
            
            # Ellie Saab / Elie Saab
            "Ellie Saab",
            "Elie Saab",
            "ELIE SAAB",
            
            # Valentino / Valentino Garavani
            "Valentino",
            "Valentino Garavani",
            "VALENTINO",
            
            # Dolce & Gabbana / Dolce&Gabbana
            "Dolce & Gabbana",
            "Dolce&Gabbana",
            "DOLCE & GABBANA",
            "DOLCE&GABBANA",
            
            # Etro / ETRO
            "Etro",
            "ETRO",
            
            # Oscar de la Renta
            "Oscar de la Renta",
            "OSCAR DE LA RENTA",
            
            # Carolina Herrera
            "Carolina Herrera",
            "CAROLINA HERRERA",
            
            # Gucci
            "Gucci",
            "GUCCI",
            
            # Louis Vuitton
            "Louis Vuitton",
            "LOUIS VUITTON"
        ]
        
        # Build query with brand filter and image filter
        query = {
            "brand_name": {"$in": brand_names}
        }
        query.update(ProductRepository.IMAGE_FILTER)
        
        # Get the total count
        total_count = products_collection.count_documents(query)
        
        # Use aggregation pipeline to calculate discount and sort by it
        # Discount = original_price - sale_price (largest discount first)
        pipeline = [
            {"$match": query},
            {
                "$addFields": {
                    "discount_amount": {
                        "$subtract": [
                            {"$ifNull": ["$original_price", 0]},
                            {"$ifNull": ["$sale_price", 0]}
                        ]
                    }
                }
            },
            {
                "$match": {
                    "discount_amount": {"$gt": 0}  # Only include products with positive discount
                }
            },
            {"$sort": {"discount_amount": -1}},  # Sort by discount descending
            {"$skip": skip},
            {"$limit": limit},
            {
                "$project": {
                    "discount_amount": 0  # Remove the computed field from final output
                }
            }
        ]
        
        # Fetch products sorted by discount
        items = list(products_collection.aggregate(pipeline))
        
        validated_items = []
        for item in items:
            # 1. Manual transform of the ID
            if "_id" in item:
                item["id"] = str(item.pop("_id"))
            
            # 2. Normalize fields that might be in different formats
            # Normalize available_sizes (convert string to list if needed)
            if "available_sizes" in item:
                item["available_sizes"] = ProductRepository._normalize_sizes(item["available_sizes"])
            else:
                item["available_sizes"] = None
            
            # Normalize product_color (convert string to list if needed)
            if "product_color" in item:
                item["product_color"] = ProductRepository._normalize_colors(item["product_color"])
            else:
                item["product_color"] = None
            
            # Set defaults for other optional fields
            if "product_description" not in item:
                item["product_description"] = None
            
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
            
        return total_count, validated_items

    @staticmethod
    def get_products(limit: int, skip: int):
        """
        Get products sorted by price (low to high) with randomization.
        Products are grouped into price buckets and randomized within each bucket
        to maintain price ordering while adding variety.
        Excludes products containing certain keywords in product_name or product_description.
        """
        import random
        from bson.regex import Regex
        
        # Keywords to filter out from product names and descriptions
        # Products containing any of these keywords will be excluded
        excluded_keywords = [
            "diamond",
            "ring",
            "gold",
            "coin",
            "furniture",
            "streamdale",
        ]
        
        # Generate a random seed for consistent randomization per request
        random_seed = random.randint(0, 1000000)
        
        # Build match filter - only products with valid sale_price and images
        match_filter = {
            "sale_price": {
                "$exists": True,
                "$ne": None,
                "$type": "number",
                "$gt": 0
            }
        }
        match_filter.update(ProductRepository.IMAGE_FILTER)
        
        # Add filter to exclude products with certain keywords in product_name or product_description
        # Use $nor to exclude products where product_name OR product_description contains any excluded keyword
        keyword_filters = []
        for keyword in excluded_keywords:
            keyword_regex = Regex(keyword, "i")  # Case-insensitive
            keyword_filters.append({
                "$or": [
                    {"product_name": keyword_regex},
                    {"product_description": keyword_regex}
                ]
            })
        
        if keyword_filters:
            match_filter["$nor"] = keyword_filters
        
        # Get total count
        total = products_collection.count_documents(match_filter)
        
        # Build aggregation pipeline
        # Price bucket size: group products into $200 buckets for randomization
        # This allows products within similar price ranges to be randomized
        pipeline = [
            # Match products with valid sale_price and images
            {"$match": match_filter},
            {
                # Add price bucket and random value for sorting
                "$addFields": {
                    # Group products into price buckets (e.g., 0-199, 200-399, etc.)
                    # Using $200 buckets to maintain price ordering while allowing randomization
                    "price_bucket": {
                        "$floor": {
                            "$divide": ["$sale_price", 1000]
                        }
                    },
                    # Generate a random value based on ObjectId + seed
                    # This creates randomization within price buckets that varies per request
                    # Use sale_price combined with ObjectId string length for variation
                    # This avoids hex parsing and uses only basic numeric operations
                    "random_value": {
                        "$mod": [
                            {
                                "$add": [
                                    {
                                        "$mod": [
                                            {
                                                "$add": [
                                                    {"$multiply": ["$sale_price", 0.01]},  # Use price for variation
                                                    {"$strLenCP": {"$toString": "$_id"}}  # ObjectId string length
                                                ]
                                            },
                                            10000
                                        ]
                                    },
                                    {"$literal": random_seed}  # Random seed for per-request variation
                                ]
                            },
                            10000  # Random value 0-9999 for mixing within bucket
                        ]
                    }
                }
            },
            {
                # Create sort priority: price_bucket * 10000 + random_value
                # This ensures price ordering (low to high) with randomization within buckets
                "$addFields": {
                    "sort_priority": {
                        "$add": [
                            {"$multiply": ["$price_bucket", 10000]},  # Price bucket (main sort)
                            "$random_value"  # Random mixing within bucket (0-9999)
                        ]
                    }
                }
            },
            # Sort by priority (price buckets ascending with randomization)
            {"$sort": {"sort_priority": -1}},
            # Pagination
            {"$skip": skip},
            {"$limit": limit},
            # Project all fields needed
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
        
        # Execute aggregation
        items = list(products_collection.aggregate(pipeline))
        
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
    def get_products_by_gender_with_brand_sort(gender: str, limit: int, skip: int):
        """Get products filtered by gender, sorted by brand order with randomization within each brand group."""
        from bson.regex import Regex
        import random
        print("new api hit")

        # Brand order list for sorting
        brand_order = ['Brioni', 'Brunello Cucinelli', 'Zegna', 'TOM FORD', 'Bottega Veneta', 'Canali', 'Polo Ralph Lauren', 'John Lobb', 'Johnstons Of Elgin', 'Kiton', 'LOEWE', 'N.Peal', 'Prada', 'Saint Laurent', 'Ralph Lauren Purple Label', 'Salvatore Ferragamo', 'Santoni', 'Zimmermann', 'FARM Rio', 'Chrome Hearts', 'Alexander McQueen', 'Valentino', 'Dolce & Gabbana', 'Dolce&Gabbana', 'Christian Louboutin', 'Maje', 'Sandro Paris', 'Missoni', 'Johanna Ortiz', 'Gabriela Hearst', 'Cartier', 'Marina Rinaldi', 'Christopher Esber', 'Oscar de la Renta', 'Derek Rose', 'Falke', 'Etro', 'ETRO', 'Balenciaga', 'Bally', 'JACQUEMUS', 'Jacquemus', 'Giorgio Armani', 'Canada Goose', 'AMI Paris', 'Yves Salomon', 'Corneliani', 'MACKAGE', 'AG Jeans', 'Fear of God', 'Orlebar Brown', 'EVISU', 'BAPE', 'A BATHING APE®', 'AAPE BY *A BATHING APE®', 'Lanvin', 'Valentino Garavani', 'Versace', "TOD's", "Tod's", 'AllSaints', 'ALLSAINTS', 'Balmain', 'Burberry', 'Chloé', 'Common Projects', 'Fleur du Mal', 'Fendi', 'FERRAGAMO', 'Ferragamo', 'Gucci', 'Hanro', 'Helmut Lang', 'Herno', 'Heron Preston', 'Hogan', 'Isabel Marant', 'Isabel Marant Etoile', 'ISSEY MIYAKE', 'Issey Miyake', 'J.Lindeberg', 'Jimmy Choo', 'Kenzo', 'Ksubi', 'lululemon', 'Mackage', 'Lladró', 'Maison Margiela', 'Marc Jacobs', 'Palm Angels', 'Palm Angels Kids', 'Paige', 'PAIGE', 'Moschino', 'Off-White', 'Off-White Kids', 'Rick Owens', 'Rick Owens DRKSHDW', 'Rick Owens Lilies', 'Rick Owens X Champion', 'RHUDE', 'Rhude', 'Roberto Cavalli', 'Theory', 'Stüssy', 'Stone Island', 'Vilebrequin', "Church's", 'Comme des Garçons', 'Comme Des Garçons', 'Acne Studios', 'Acqua di Parma', 'A-COLD-WALL*', 'Alexander Wang', 'alexanderwang.t', 'alice + olivia', 'Alice+Olivia', 'adidas Yeezy', 'Balmain Kids', 'BAPE BLACK *A BATHING APE®', 'BAPY BY *A BATHING APE®', 'Barbour', 'Barbour International', 'Birkenstock', 'BIRKENSTOCK 1774', 'DOMREBEL', 'VETEMENTS', 'Armani', 'Ea7 Emporio Armani', 'Ed Hardy', 'Fear Of God', 'FEAR OF GOD ESSENTIALS', 'Fear of God ESSENTIALS', 'Fear of God Athletics', 'FEAR OF GOD ESSENTIALS KIDS', 'Fendi Kids', 'FRAME', 'Giuseppe Zanotti', 'Givenchy', 'Gianvito Rossi', 'La Perla', 'Eileen Fisher', 'Elie Tahari', 'Eleventy', 'Emporio Armani', 'Dita Eyewear', 'TOM FORD Eyewear', 'Cartier Eyewear', 'Dolce & Gabbana Eyewear', 'Prada Eyewear', 'Gucci Eyewear', 'Alexander McQueen Eyewear', 'Balenciaga Eyewear', 'Chloé Eyewear', 'Balmain Eyewear', 'Palm Angels Eyewear', 'Burberry Eyewear', 'Givenchy Eyewear', 'Jimmy Choo Eyewear', 'Off-White Eyewear', 'Versace Eyewear', 'Hermès\xa0Pre-Owned', 'CHANEL Pre-Owned', 'Bottega Veneta Pre-Owned', 'Christian Dior Pre-Owned', 'Balenciaga Pre-Owned', 'Celine Pre-Owned', 'Fendi Pre-Owned', 'Goyard Pre-Owned', 'Gucci Pre-Owned', 'Loewe Pre-Owned', 'Louis Vuitton Pre-Owned', 'Prada Pre-Owned', 'Versace Pre-Owned', 'MEMO PARIS', 'Bond No. 9', 'Bobbi Brown', 'Estée Lauder', 'Jo Malone London', 'La Prairie', 'Kerastase', "Kiehl's", 'Lancôme', 'Prada Beauty']
        
        # Build gender query - only match the exact gender (no unisex or unknown)
        gender_patterns = []
        
        # Add the requested gender only
        gender_patterns.append(Regex(gender, "i"))
        
        # Build match filter - only exact gender match
        match_filter = {"product_gender": {"$in": gender_patterns}}
        match_filter.update(ProductRepository.IMAGE_FILTER)
        
        # Get total count
        total = products_collection.count_documents(match_filter)
        
        # Generate a random seed for consistent randomization per request
        # This ensures products within the same brand are randomly mixed
        random_seed = random.randint(0, 1000000)
        
        # Build aggregation pipeline
        pipeline = [
            # Match products by gender and image filter
            {"$match": match_filter},
            {
                # Add brand index (position in brand_order list)
                "$addFields": {
                    "brand_index": {
                        "$indexOfArray": [brand_order, "$brand_name"]
                    },
                    # Add a random value for mixing within brand groups
                    # Using ObjectId hash + random seed for deterministic randomization
                    "random_value": {
                        "$mod": [
                            {
                                "$add": [
                                    {"$toInt": {"$substr": [{"$toString": "$_id"}, 0, 8]}},
                                    random_seed
                                ]
                            },
                            10000  # Random value 0-9999 for mixing
                        ]
                    }
                }
            },
            {
                # Create sort priority: brand_index * 10000 + random_value
                # This ensures brands are ordered, but products within each brand are mixed
                "$addFields": {
                    "sort_priority": {
                        "$cond": {
                            "if": {"$eq": ["$brand_index", -1]},
                            "then": 999999999,  # Brands not in list go to end
                            "else": {
                                "$add": [
                                    {"$multiply": ["$brand_index", 10000]},  # Brand priority (main sort)
                                    "$random_value"  # Random mixing within brand (0-9999)
                                ]
                            }
                        }
                    }
                }
            },
            # Sort by priority (brand order with randomization)
            {"$sort": {"sort_priority": 1}},
            # Pagination
            {"$skip": skip},
            {"$limit": limit},
            # Project fields needed for transform_product
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
    def get_latest_products(limit: int, skip: int):
        """Get newest products sorted by scraped_at (or _id fallback) descending, filtered by luxury brands."""
        # Define the list of luxury brands to filter by
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
            "AAPE BY *A BATHING APE®", "Lanvin", "Versace", 
            "TOD's", "Tod's", "AllSaints", "ALLSAINTS", "Balmain", "Burberry", 
            "Chloé", "Common Projects", "Fleur du Mal", "Fendi", "FERRAGAMO", 
            "Ferragamo", "Gucci", "Hanro", "Helmut Lang", "Herno", "Heron Preston", 
            "Hogan", "Isabel Marant", "Isabel Marant Etoile", "ISSEY MIYAKE", 
            "Issey Miyake", "J.Lindeberg", "Jimmy Choo", "Kenzo", "Ksubi", "lululemon", 
            "Mackage", "Lladró", "Maison Margiela", "Marc Jacobs", "Palm Angels", 
            "Palm Angels Kids", "Paige", "PAIGE", "Moschino", "Off-White", 
            "Off-White Kids", "RHUDE", "Rhude", "Roberto Cavalli", "Theory", 
            "Stüssy", "Stone Island", "Vilebrequin"
        ]
        
        # Build query with brand filter and image filter
        query = {
            "brand_name": {"$in": brand_names}
        }
        query.update(ProductRepository.IMAGE_FILTER)
        
        products = (
            products_collection.find(query)
            .sort([("scraped_at", -1), ("_id", -1)])
            .skip(skip)
            .limit(limit)
        )
        items = list(products)
        total = products_collection.count_documents(query)

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
        
        # Get price range counts
        price_counts = {}
        for price_range in PRICE_RANGES:
            price_query = {}
            # Add image filter
            price_query.update(ProductRepository.IMAGE_FILTER)
            
            # Build sale_price filter based on range
            sale_price_filter = {
                "$exists": True,
                "$type": "number"
            }
            
            if price_range["min"] is not None and price_range["max"] is not None:
                sale_price_filter["$gte"] = price_range["min"]
                sale_price_filter["$lte"] = price_range["max"]
            elif price_range["min"] is not None:
                sale_price_filter["$gte"] = price_range["min"]
            elif price_range["max"] is not None:
                sale_price_filter["$lte"] = price_range["max"]
            else:
                # Both are None, skip this range
                continue
            
            price_query["sale_price"] = sale_price_filter
            
            count = products_collection.count_documents(price_query)
            price_counts[price_range["value"]] = count
        
        return {
            "categories": categories,
            "brands": brands,
            "occasions": occasions,
            "price_counts": price_counts
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
        gender: Optional[str] = None,
        sort_by: Optional[str] = None
    ):
        """Get products with filters applied. Sorting is handled on the backend."""
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
        
        # Gender filter - only match exact gender (no unisex or unknown)
        if gender:
            gender_patterns = [Regex(gender, "i")]
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
        
        # Build sort criteria based on sort_by parameter
        sort_criteria = []
        if sort_by:
            if sort_by == 'price-asc':
                sort_criteria = [("sale_price", 1), ("original_price", 1)]
            elif sort_by == 'price-desc':
                sort_criteria = [("sale_price", -1), ("original_price", -1)]
            elif sort_by == 'discount-desc':
                # Sort by discount percentage - use aggregation pipeline to calculate discount percentage
                # For discount sorting, we need to calculate (original_price - sale_price) / original_price * 100
                # Since MongoDB doesn't support computed fields in simple sort, we'll use aggregation
                pipeline = [
                    {"$match": query},
                    {"$addFields": {
                        "discount_percent": {
                            "$cond": {
                                "if": {"$and": [
                                    {"$gt": ["$original_price", 0]},
                                    {"$gt": ["$sale_price", 0]},
                                    {"$gt": ["$original_price", "$sale_price"]}
                                ]},
                                "then": {
                                    "$multiply": [
                                        {"$divide": [
                                            {"$subtract": ["$original_price", "$sale_price"]},
                                            "$original_price"
                                        ]},
                                        100
                                    ]
                                },
                                "else": 0
                            }
                        }
                    }},
                    {"$sort": {"discount_percent": -1}},
                    {"$skip": skip},
                    {"$limit": limit}
                ]
                items = list(products_collection.aggregate(pipeline))
                # Convert _id to id string
                for item in items:
                    if "_id" in item:
                        item["id"] = str(item["_id"])
                        del item["_id"]
                return total, items
            elif sort_by == 'name-asc':
                sort_criteria = [("product_name", 1)]
            elif sort_by == 'name-desc':
                sort_criteria = [("product_name", -1)]
            elif sort_by == 'newest':
                sort_criteria = [("scraped_at", -1)]
            # 'featured' or None: no sorting, return in database order
        
        # Get filtered items with optional sorting
        find_query = products_collection.find(query)
        if sort_criteria:
            find_query = find_query.sort(sort_criteria)
        items = list(find_query.skip(skip).limit(limit))
        
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

    @staticmethod
    def get_curated_products(brand_keyword_pairs: List[dict]):
        """
        Get curated products based on brand_name and keyword pairs.
        For each tuple (brand_name, keyword), finds products that:
        - Have the specified brand_name
        - Have the keyword in product_name OR product_description
        Returns the union of all products from all tuples (no duplicates).
        """
        from bson.regex import Regex
        
        if not brand_keyword_pairs:
            return []
        
        # Use a set to track unique product IDs to avoid duplicates
        seen_product_ids = set()
        all_products = []
        
        # Process each brand_keyword pair
        for pair in brand_keyword_pairs:
            brand_name = pair.get("brand_name", "").strip()
            keyword = pair.get("keyword", "").strip()
            
            if not brand_name or not keyword:
                continue
            
            # Build query: brand_name matches AND (keyword in product_name OR product_description)
            keyword_regex = Regex(keyword, "i")  # Case-insensitive
            brand_regex = Regex(f"^{brand_name}$", "i")  # Case-insensitive exact match
            
            query = {
                "brand_name": brand_regex,  # Case-insensitive exact match for brand_name
                "$or": [
                    {"product_name": keyword_regex},
                    {"product_description": keyword_regex}
                ]
            }
            query.update(ProductRepository.IMAGE_FILTER)
            
            # Find products matching this tuple
            items = list(products_collection.find(query))
            
            # Add products to result set, avoiding duplicates
            for item in items:
                if "_id" in item:
                    product_id = str(item["_id"])
                    if product_id not in seen_product_ids:
                        seen_product_ids.add(product_id)
                        item["id"] = product_id
                        del item["_id"]
                        all_products.append(item)
        
        # Randomly shuffle the products before returning
        import random
        random.shuffle(all_products)
        
        return all_products