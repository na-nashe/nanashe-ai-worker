from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    product_name: str
    category: str
    is_healthy: Optional[bool] = False
    extra_wishes: Optional[str] = None

class AlternativeItem(BaseModel):
    name: str
    # Тепер ці поля мають значення за замовчуванням, якщо ШІ їх пропустить
    description: Optional[str] = "Опис відсутній"
    url: Optional[str] = None
    aliases: List[str] = []

class AlternativesResponse(BaseModel):
    alternatives: List[AlternativeItem] = Field(max_length=4)