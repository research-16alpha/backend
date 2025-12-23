from .repository import ProductRepository
from .transformers import transform_product
from typing import List, Optional
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
    def get_products_with_custom_sort(limit: int, skip: int = 0):
        """Get products sorted by custom brand order and scraped_at."""
        total, items = ProductRepository.get_products_with_custom_sort(limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed

    @staticmethod
    def get_product_by_id(product_id: str):
        product = ProductRepository.get_product_by_id(product_id)
        return transform_product(product) if product else None

    @staticmethod
    def get_products_by_category(category: str, limit: int, skip: int):
        total, items = ProductRepository.get_products_by_category(category, limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed

    @staticmethod
    def get_products_by_gender(gender: str, limit: int, skip: int):
        total, items = ProductRepository.get_products_by_gender(gender, limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed

    @staticmethod
    def get_best_deals(limit: int):
        total, items = ProductRepository.get_best_deals(limit)
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed

    @staticmethod
    def get_latest_products(limit: int, skip: int):
        # print("Getting latest products with limit:", limit, "and skip:", skip)
        total, items = ProductRepository.get_latest_products(limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        # print(transformed, total)
        return total, transformed

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
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed