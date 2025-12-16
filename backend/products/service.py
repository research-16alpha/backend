from .repository import ProductRepository
from .transformers import transform_product


class ProductService:

    @staticmethod
    def get_top_deals(limit: int):
        items = ProductRepository.get_top_deals(limit)
        return [p for p in map(transform_product, items) if p]

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
    def get_products_by_category(category: str, limit: int, skip: int):
        total, items = ProductRepository.get_products_by_category(category, limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed

    @staticmethod
    def get_products_by_gender(gender: str, limit: int, skip: int):
        total, items = ProductRepository.get_products_by_gender(gender, limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        return total, transformed
