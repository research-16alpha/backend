from .repository import ProductRepository

class ProductService:

    @staticmethod
    def get_top_deals(limit: int):
        return ProductRepository.get_top_deals(limit)

    @staticmethod
    def get_products(limit: int, skip: int):
        return ProductRepository.get_products(limit, skip)

    @staticmethod
    def get_product_by_id(product_id: str):
        return ProductRepository.get_product_by_id(product_id)

    @staticmethod
    def get_products_by_category(category: str, limit: int, skip: int):
        return ProductRepository.get_products_by_category(category, limit, skip)

    @staticmethod
    def get_products_by_gender(gender: str, limit: int, skip: int):
        return ProductRepository.get_products_by_gender(gender, limit, skip)