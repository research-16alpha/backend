from pydantic import BaseModel, Field
from typing import Optional, List


class Product(BaseModel):
    id: Optional[str] = Field(default=None)
    
    product_link: Optional[str] = None
    product_image: Optional[str] = None
    
    brand_name: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    
    product_category: Optional[str] = None
    product_sub_category: Optional[str] = None
    product_gender: Optional[str] = None
    
    product_color: Optional[List[str]] = None
    product_material: Optional[str] = None
    product_occasion: Optional[str] = None
    
    currency: Optional[str] = None
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    discount: Optional[int] = None
    search_tags: Optional[str] = None
    available_sizes: Optional[List[str]] = None

    scraped_at: Optional[str] = None

    class Config:
        populate_by_name = True
