from .repository import ProductRepository
from .transformers import transform_product
from typing import List, Optional
import random
from core.constants.filter_constants import SORT_OPTIONS, PRICE_RANGES, FILTER_GROUP_TITLES
from core.schemas.filter_schemas import FilterGroup, FilterOption, SortOption, FilterMetadataResponse


class ProductService:

    @staticmethod
    def get_top_deals(limit: int, skip: int = 0):
        total, items = ProductRepository.get_top_deals(limit, skip)
        transformed = [p for p in map(transform_product, items)if p]
        return total, transformed

    @staticmethod
    def get_products(limit: int, skip: int):
        total, items = ProductRepository.get_products(limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed

    @staticmethod
    def get_product_by_id(product_id: str):
        product = ProductRepository.get_product_by_id(product_id)
        return transform_product(product) if product else None

    @staticmethod
    def get_latest_products(limit: int, skip: int):
        # print("Getting latest products with limit:", limit, "and skip:", skip)
        total, items = ProductRepository.get_latest_products(limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        # print(transformed, total)
        return total, transformed

    @staticmethod
    def get_products_by_gender(gender: str, limit: int, skip: int):
        """
        Get products filtered by gender.
        Calls get_products from repository and filters by gender in the service layer.
        Only matches exact gender (no unisex or unknown).
        """
        import re
        
        # Fetch a larger batch to account for filtering
        # Fetch 5x the requested limit to ensure we have enough after filtering
        fetch_limit = max(limit * 5, 100)
        fetch_skip = 0
        
        # Accumulate filtered items across multiple fetches if needed
        all_filtered_items = []
        total_fetched = 0
        
        # Filter by gender - only match exact gender (case-insensitive)
        gender_pattern = re.compile(f"^{re.escape(gender)}$", re.IGNORECASE)
        
        # Keep fetching until we have enough filtered items
        while len(all_filtered_items) < skip + limit:
            _, items = ProductRepository.get_products(fetch_limit, fetch_skip)
            
            if not items:
                break  # No more items available
            
            # Filter by gender
            filtered_batch = [
                item for item in items
                if item.get("product_gender") and gender_pattern.match(str(item.get("product_gender", "")))
            ]
            
            all_filtered_items.extend(filtered_batch)
            total_fetched += len(items)
            
            # If we got fewer items than requested, we've likely reached the end
            if len(items) < fetch_limit:
                break
            
            fetch_skip += fetch_limit
        
        # Apply pagination to filtered results
        paginated_items = all_filtered_items[skip:skip + limit]
        
        # Estimate total count
        # If we have enough items, estimate based on ratio, otherwise use actual count
        if len(all_filtered_items) >= skip + limit:
            # Estimate: assume similar ratio across all products
            estimated_total = len(all_filtered_items) * 2  # Conservative estimate
        else:
            estimated_total = len(all_filtered_items)
        
        transformed = [p for p in map(transform_product, paginated_items) if p]
        return estimated_total, transformed

    @staticmethod
    def get_filter_metadata():
        """Get filter metadata including categories, brands, occasions with counts."""
        metadata = ProductRepository.get_filter_metadata()
        
        # Build category filter group
        category_options = [
            FilterOption(
                label=cat["_id"],
                value=cat["_id"].lower().replace(" ", "-").replace("&", "-"),
                count=cat["count"]
            )
            for cat in metadata["categories"]
        ]
        
        # Build brand filter group
        brand_options = [
            FilterOption(
                label=brand["_id"],
                value=brand["_id"].lower().replace(" ", "-").replace("&", "-"),
                count=brand["count"]
            )
            for brand in metadata["brands"]
        ]
        
        # Build occasion filter group
        occasion_options = [
            FilterOption(
                label=occasion["_id"],
                value=occasion["_id"].lower().replace(" ", "-").replace("&", "-"),
                count=occasion["count"]
            )
            for occasion in metadata["occasions"]
        ]
        
        # Build price filter group (from constants)
        price_options = [
            FilterOption(
                label=price["label"],
                value=price["value"],
                count=None
            )
            for price in PRICE_RANGES
        ]
        
        # Build filter groups
        filter_groups = [
            FilterGroup(
                title=FILTER_GROUP_TITLES["CATEGORY"],
                options=category_options,
                multiSelect=True
            ),
            FilterGroup(
                title=FILTER_GROUP_TITLES["BRAND"],
                options=brand_options,
                multiSelect=True
            ),
            FilterGroup(
                title=FILTER_GROUP_TITLES["OCCASION"],
                options=occasion_options,
                multiSelect=True
            ),
            FilterGroup(
                title=FILTER_GROUP_TITLES["PRICE"],
                options=price_options,
                multiSelect=False
            )
        ]
        
        # Build sort options
        sort_options = [SortOption(**opt) for opt in SORT_OPTIONS]
        
        response = FilterMetadataResponse(
            categories=filter_groups,
            sortOptions=sort_options
        )
        # Return as dict for FastAPI serialization
        return response.model_dump()

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
        """Get filtered products. Sorting is handled on the frontend."""
        total, items = ProductRepository.get_filtered_products(
            limit=limit,
            skip=skip,
            category=category,
            brand=brand,
            occasion=occasion,
            price_min=price_min,
            price_max=price_max,
            gender=gender
        )
        # Shuffle the items list to randomize order
        items_list = list(items)  # Convert to list if it's not already
        random.shuffle(items_list)
        
        transformed = [p for p in map(transform_product, items_list) if p]
        return total, transformed

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
        """Search products using MongoDB Atlas Search."""
        total, items = ProductRepository.search_products(
            query=query,
            limit=limit,
            skip=skip,
            category=category,
            brand=brand,
            occasion=occasion,
            price_min=price_min,
            price_max=price_max,
            gender=gender
        )
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed

    @staticmethod
    def get_search_suggestions(query: str, limit: int = 10):
        """Get search suggestions/autocomplete."""
        return ProductRepository.get_search_suggestions(query, limit)

    @staticmethod
    def get_products_by_links(product_links: List[str]):
        """Get products by product_link values, preserving order."""
        items = ProductRepository.get_products_by_links(product_links)
        transformed = [p for p in map(transform_product, items) if p]
        return transformed

    @staticmethod
    def get_curated_products(brand_keyword_pairs: List):
        """
        Get curated products based on brand_name and keyword pairs.
        For each tuple (brand_name, keyword), finds products that match both criteria.
        Returns the union of all products from all tuples.
        """
        # Convert Pydantic models to dictionaries if needed
        pairs_as_dicts = []
        for pair in brand_keyword_pairs:
            if hasattr(pair, 'model_dump'):
                # Pydantic model - convert to dict
                pairs_as_dicts.append(pair.model_dump())
            elif hasattr(pair, 'dict'):
                # Pydantic model (older version) - convert to dict
                pairs_as_dicts.append(pair.dict())
            elif isinstance(pair, dict):
                # Already a dictionary
                pairs_as_dicts.append(pair)
            else:
                # Try to access as attributes
                pairs_as_dicts.append({
                    "brand_name": getattr(pair, 'brand_name', ''),
                    "keyword": getattr(pair, 'keyword', '')
                })
        
        items = ProductRepository.get_curated_products(pairs_as_dicts)
        transformed = [p for p in map(transform_product, items) if p]
        return transformed