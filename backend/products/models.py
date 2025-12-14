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
    
    price_original: Optional[str]       
    price_final: Optional[str]
    sale_price: Optional[str]           
    original_price: Optional[str]       # duplicate of price_original

    discount: Optional[int]             # 49
    disc_pct: Optional[str]             # "-50%"

    available_sizes: Optional[List[str]]  # ["S", "M", "L", "XL", "XXL", "3XL"]

    wishlist_state: Optional[bool]      # convert "false" → False automatically

    added_at: Optional[datetime]

    class Config:
        populate_by_name = True
