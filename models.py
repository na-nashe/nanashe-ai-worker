from pydantic import BaseModel, Field
from typing import List, Optional, Literal # Додали Literal

class SearchRequest(BaseModel):
    product_name: str
    # Тепер користувач зможе обрати категорію ТІЛЬКИ з цього списку
    category: Literal["soft", "media", "food", "clothes", "cosmetics", "other"]
    is_healthy: Optional[bool] = False
    extra_wishes: Optional[str] = None

class AlternativeItem(BaseModel):
    name: str
    description: Optional[str] = "Опис відсутній"
    url: Optional[str] = None
    aliases: List[str] = []

class AlternativesResponse(BaseModel):
    alternatives: List[AlternativeItem] = Field(max_length=4)