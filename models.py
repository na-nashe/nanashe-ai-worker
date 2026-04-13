from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    product_name: str
    is_healthy: Optional[bool] = False

class AlternativeItem(BaseModel):
    name: str
    country: str
    description: Optional[str] = "Опис відсутній"
    url: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)

class AlternativesResponse(BaseModel):
    detected_category: Optional[str] = Field(default=None)
    detected_country: Optional[str] = Field(default=None)
    alternatives: List[AlternativeItem] = Field(default_factory=list)
    message: Optional[str] = Field(default=None)