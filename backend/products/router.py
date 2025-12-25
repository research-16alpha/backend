from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from .service import ProductService
from typing import List, Optional
import time

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/top-deals")
def get_top_deals(limit: int = 4, skip: int = 0):
    total, items= ProductService.get_top_deals(limit, skip)
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total
    }

@router.get("/best-deals")
def get_best_deals(limit: int = 20):
    """Get products with largest discount in dollar terms, sorted by discount_value descending."""
    total, items = ProductService.get_best_deals(limit)
    return {
        "products": items,
        "total": total,
        "limit": limit,
    }

@router.get("/latest")
def get_latest_products(limit: int = 100, skip: int = 0):
    total, items = ProductService.get_latest_products(limit, skip)
    # print("Latest products fetched:", items)
    # print("Returning latest products with limit:", limit, "and skip:", skip)
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total
    }

@router.get("/")
def list_products(limit: int = 100, skip: int = 0):
    total, items = ProductService.get_products(limit, skip)
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total
    }

@router.get("/custom-sort")
def get_products_with_custom_sort(limit: int = 100, skip: int = 0):
    """Get products sorted by custom brand order and scraped_at."""
    # print("api hit")
    total, items = ProductService.get_products_with_custom_sort(limit, skip)
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total
    }

@router.get("/category/{category}")
def get_products_by_category(category: str, limit: int = 100, skip: int = 0):
    """Get products filtered by category name matching product_name or product_description."""
    total, items = ProductService.get_products_by_category(category, limit, skip)
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total,
        "category": category
    }

@router.get("/gender/{gender}")
def get_products_by_gender(gender: str, limit: int = 100, skip: int = 0):
    """Get products filtered by gender."""

    total, items = ProductService.get_products_by_gender(gender, limit, skip)
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total,
        "gender": gender
    }

@router.get("/filter/metadata")
def get_filter_metadata():
    """Get filter metadata (categories, brands, occasions) with counts."""
    return ProductService.get_filter_metadata()

@router.get("/filter/products")
def get_filtered_products(
    limit: int = Query(100, ge=1, le=200),
    skip: int = Query(0, ge=0),
    category: Optional[List[str]] = Query(None),
    brand: Optional[List[str]] = Query(None),
    occasion: Optional[List[str]] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    gender: Optional[str] = Query(None)
):
    """Get products with filters applied. Sorting is handled on the frontend."""
    total, items = ProductService.get_filtered_products(
        limit=limit,
        skip=skip,
        category=category,
        brand=brand,
        occasion=occasion,
        price_min=price_min,
        price_max=price_max,
        gender=gender
    )
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total
    }

@router.get("/search")
def search_products(
    q: str = Query(..., description="Search query string"),
    limit: int = Query(20, ge=1, le=200),
    skip: int = Query(0, ge=0),
    category: Optional[List[str]] = Query(None),
    brand: Optional[List[str]] = Query(None),
    occasion: Optional[List[str]] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    gender: Optional[str] = Query(None)
):
    """
    Search products using MongoDB Atlas Search with fuzzy matching.
    Searches across all product fields and supports filters.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    total, items = ProductService.search_products(
        query=q.strip(),
        limit=limit,
        skip=skip,
        category=category,
        brand=brand,
        occasion=occasion,
        price_min=price_min,
        price_max=price_max,
        gender=gender
    )
    return {
        "products": items,
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": (skip + limit) < total,
        "query": q
    }

@router.get("/search/suggestions")
def get_search_suggestions(
    q: str = Query(..., description="Partial search query for autocomplete"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get search suggestions/autocomplete based on partial query.
    Returns suggested search terms for autocomplete functionality.
    """
    if not q or not q.strip():
        return {"suggestions": []}
    
    suggestions = ProductService.get_search_suggestions(q.strip(), limit)
    return {
        "suggestions": suggestions,
        "query": q
    }

class ProductLinksRequest(BaseModel):
    product_links: List[str]

@router.post("/by-links")
def get_products_by_links(request: ProductLinksRequest):
    """Get products by product_link values, returning them in the exact order provided."""
    if not request.product_links:
        return {"products": []}
    
    items = ProductService.get_products_by_links(request.product_links)
    return {
        "products": items,
        "total": len(items)
    }

@router.get("/{product_id}")
def get_product(product_id: str):
    product = ProductService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product