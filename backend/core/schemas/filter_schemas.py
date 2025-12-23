"""
Pydantic schemas for filter metadata responses
"""
from pydantic import BaseModel
from typing import List, Optional


class FilterOption(BaseModel):
    label: str
    value: str
    count: Optional[int] = None


class FilterGroup(BaseModel):
    title: str
    options: List[FilterOption]
    multiSelect: bool = True


class SortOption(BaseModel):
    label: str
    value: str


class FilterMetadataResponse(BaseModel):
    categories: List[FilterGroup]
    sortOptions: List[SortOption]

