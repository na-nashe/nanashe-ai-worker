from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    productName: str
    categories: List[str]
    pricingModels: List[str] = []

class AlternativeItem(BaseModel):
    name: str
    country: str
    description: str
    pricingModel: Optional[str] = None
    url: Optional[str] = None

class AIGeneratedData(BaseModel):
    official_title: Optional[str] = Field(default=None, description="Офіційна повна назва шуканого продукту")
    detected_category: Optional[str] = Field(default=None, description="Загальна категорія для продукту та альтернатив")
    detected_country: Optional[str] = None
    aliases: List[str] = []
    alternatives: List[AlternativeItem] = []


class AlternativesResponse(BaseModel):
    message: str
<<<<<<< HEAD
    productName: Optional[str] = None
    alternatives: List[AlternativeItem] = []



=======
    official_title: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    aliases: List[str] = []
    alternatives: List[AlternativeItem] = []

>>>>>>> 40e2e05 (refactor: add KafkaAlternativesEvent model to align with Java contract)
class KafkaAlternativeResponseDto(BaseModel):
    name: str
    country: str
    description: Optional[str] = None
<<<<<<< HEAD
    pricingModel: Optional[str] = None
=======
>>>>>>> 40e2e05 (refactor: add KafkaAlternativesEvent model to align with Java contract)
    url: Optional[str] = None

class KafkaAlternativesEvent(BaseModel):
    aliases: List[str]
    productName: str
    productCategory: str
    productCountry: str
    alternatives: List[KafkaAlternativeResponseDto]