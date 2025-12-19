from .repository import ProductRepository
from .transformers import transform_product


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
        print("Getting latest products with limit:", limit, "and skip:", skip)
        total, items = ProductRepository.get_latest_products(limit, skip)
        transformed = [p for p in map(transform_product, items) if p]
        # print(transformed, total)
        return total, transformed