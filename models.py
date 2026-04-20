from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    product_name: str = Field(..., alias="productName")
    categories: List[str]

    class Config:
        populate_by_name = True

class AlternativeItem(BaseModel):
    name: str
    country: str
    description: str
    url: Optional[str] = None
    aliases: Optional[List[str]] = []


class AIGeneratedData(BaseModel):
    detected_category: Optional[str] = None
    detected_country: Optional[str] = None
    alternatives: List[AlternativeItem] = []


class AlternativesResponse(BaseModel):
    message: str
    alternatives: List[AlternativeItem] = []