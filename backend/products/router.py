from fastapi import APIRouter, HTTPException
from .service import ProductService
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
    print("Returning latest products with limit:", limit, "and skip:", skip)
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

@router.get("/{product_id}")
def get_product(product_id: str):
    product = ProductService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product
