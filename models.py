from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    product_name: str = Field(..., alias="productName")
    categories: List[str] 
    
    
    available_alternatives: List[str] = Field(default_factory=list, alias="availableAlternatives")
    
    is_healthy: Optional[bool] = False

    class Config:
        populate_by_name = True

class AlternativeItem(BaseModel):
    name: str
    country: str
    description: str
    url: Optional[str] = None
    aliases: Optional[List[str]] = []

class AlternativesResponse(BaseModel):
    detected_category: Optional[str] = None
    detected_country: Optional[str] = None
    alternatives: List[AlternativeItem] = []
    message: str = ""

    class Config:
        populate_by_name = True