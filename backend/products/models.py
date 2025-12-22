from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Product(BaseModel):
    id: Optional[str] = Field(alias="_id")
    
    product_link: Optional[str]
    product_image: Optional[str]
    
    brand_name: Optional[str]
    product_name: Optional[str]         
    product_description: Optional[str]
    
    product_category: Optional[str]     
    product_sub_category: Optional[str] 
    product_gender: Optional[str]       
    
    color: Optional[List[str]]
    material: Optional[str]
    occasion: Optional[str]
    
    original_price: Optional[str]
    sale_price: Optional[str]
    discount: Optional[int]

    available_sizes: Optional[List[str]]  # ["S", "M", "L", "XL", "XXL", "3XL"]

    scraped_at: Optional[datetime]

    class Config:
        populate_by_name = True
