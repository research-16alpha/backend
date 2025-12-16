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
    original = (
        product.get("original_price")
        or product.get("price_original")
    )
    final = (
        product.get("sale_price")
        or product.get("price_final")
    )

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
        "original_price": product.get("original_price") or product.get("price_original"),
        "sale_price": product.get("sale_price") or product.get("price_final"),
        "discount": product.get("discount"),
        "disc_pct": product.get("disc_pct"),

        # ATTRIBUTES
        "available_sizes": product.get("available_sizes", []),
        "wishlist_state": bool(product.get("wishlist_state", False)),

        # META
        "added_at": product.get("added_at"),
    }
