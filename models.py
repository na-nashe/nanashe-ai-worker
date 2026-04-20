from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    productName: str  
    categories: List[str]

class AlternativeItem(BaseModel):
    name: str
    country: str
    description: str
    url: Optional[str] = None
   

class AIGeneratedData(BaseModel):
    detected_category: Optional[str] = None
    detected_country: Optional[str] = None
    alternatives: List[AlternativeItem] = []

class AlternativesResponse(BaseModel):
    message: str
    alternatives: List[AlternativeItem] = []