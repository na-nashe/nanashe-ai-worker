from pydantic import BaseModel, Field
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
    official_title: Optional[str] = Field(default=None, description="Офіційна повна назва шуканого продукту")
    detected_category: Optional[str] = Field(default=None, description="Загальна категорія для продукту та альтернатив")
    detected_country: Optional[str] = None
    aliases: List[str] = []
    alternatives: List[AlternativeItem] = []

class AlternativesResponse(BaseModel):
    message: str
    official_title: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    aliases: List[str] = []
    alternatives: List[AlternativeItem] = []

class KafkaAlternativeResponseDto(BaseModel):
    name: str
    country: str
    description: Optional[str] = None
    url: Optional[str] = None

class KafkaAlternativesEvent(BaseModel):
    aliases: List[str]
    productName: str
    productCategory: str
    productCountry: str
    alternatives: List[KafkaAlternativeResponseDto]