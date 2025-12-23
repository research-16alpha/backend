from typing import Optional, Dict


def title_case(text: Optional[str]) -> Optional[str]:
    """
    Capitalize first letter of each word.
    Handles spaces and hyphen-separated words.
    """
    if not text:
        return text

    return " ".join(
        "-".join(
            part.capitalize() for part in word.split("-")
        )
        for word in text.split()
    )


def all_caps(text: Optional[str]) -> Optional[str]:
    """
    Convert text to ALL CAPS.
    """
    if not text:
        return text
    return text.upper()


def has_valid_dual_price(product: Dict) -> bool:
    """
    Return True only if product has two DIFFERENT prices.
    """
    original = product.get("original_price")
    final = product.get("sale_price")

    if not original or not final:
        return False

    return str(original) != str(final)


def transform_product(product: Dict) -> Optional[Dict]:
    """
    Transform a single product for frontend consumption.
    Returns None if product should be excluded.
    """

    # ❌ Filter out products without valid dual pricing
    if not has_valid_dual_price(product):
        return None

    # PRICES - Handle both number and string formats
    original_price = product.get("original_price")
    sale_price = product.get("sale_price")
    
    # Convert to float if they're strings
    if original_price and isinstance(original_price, str):
        try:
            original_price = float(str(original_price).replace('$', '').replace(',', '').strip())
        except (ValueError, TypeError):
            original_price = None
    
    if sale_price and isinstance(sale_price, str):
        try:
            sale_price = float(str(sale_price).replace('$', '').replace(',', '').strip())
        except (ValueError, TypeError):
            sale_price = None
    
    # Calculate discount_value if not present
    discount_value = product.get("discount_value")
    if discount_value is None and original_price and sale_price:
        try:
            original_float = float(original_price) if not isinstance(original_price, float) else original_price
            sale_float = float(sale_price) if not isinstance(sale_price, float) else sale_price
            discount_value = original_float - sale_float
        except (ValueError, TypeError):
            discount_value = None

    return {
        "id": product.get("id"),

        # LINKS / MEDIA
        "product_link": product.get("product_link"),
        "product_image": product.get("product_image"),

        # TEXT FIELDS
        "brand_name": all_caps(product.get("brand_name")),
        "product_category": all_caps(product.get("product_category")),
        "product_sub_category": title_case(product.get("product_sub_category")),
        "product_gender": title_case(product.get("product_gender")),
        "product_name": title_case(product.get("product_name")),
        "product_description": title_case(product.get("product_description")),

        # PRICES
        "currency": product.get("currency"),
        "original_price": original_price,
        "sale_price": sale_price,
        "discount": product.get("discount"),
        "disc_pct": product.get("disc_pct"),
        "discount_value": discount_value,

        # ATTRIBUTES
        "product_color": product.get("product_color", []),
        "product_material": product.get("product_material"),
        "product_occasion": product.get("product_occasion"),
        "available_sizes": product.get("available_sizes", []),
        "wishlist_state": bool(product.get("wishlist_state", False)),

        # META
        "search_tags": product.get("search_tags"),
        "scraped_at": product.get("scraped_at"),
    }
