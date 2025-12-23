"""
Hardcoded filter lists and constants for product filtering
"""

# Sort options
SORT_OPTIONS = [
    {"label": "Featured", "value": "featured"},
    {"label": "Price: Low to High", "value": "price-asc"},
    {"label": "Price: High to Low", "value": "price-desc"},
    {"label": "Discount: High to Low", "value": "discount-desc"},
    {"label": "Newest", "value": "newest"},
    {"label": "Name: A to Z", "value": "name-asc"},
    {"label": "Name: Z to A", "value": "name-desc"}
]

# Price range options
PRICE_RANGES = [
    {"label": "Under $500", "value": "under-500", "min": None, "max": 500},
    {"label": "$500 - $1000", "value": "500-1000", "min": 500, "max": 1000},
    {"label": "$1000 - $5000", "value": "1000-5000", "min": 1000, "max": 5000},
    {"label": "$5000 - $10000", "value": "5000-10000", "min": 5000, "max": 10000},
    {"label": "Over $10000", "value": "over-10000", "min": 10000, "max": None}
]

# Filter group titles
FILTER_GROUP_TITLES = {
    "CATEGORY": "CATEGORY",
    "BRAND": "BRAND",
    "OCCASION": "OCCASION",
    "PRICE": "PRICE"
}

