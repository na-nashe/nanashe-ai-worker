from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

class SearchRequest(BaseModel):
    product_name: str
    available_categories: List[str] = Field(default_factory=list)
    is_healthy: Optional[bool] = False
    extra_wishes: Optional[str] = None

class AlternativeItem(BaseModel):
    name: str
    country: str
    description: Optional[str] = "Опис відсутній"
    url: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)

class AlternativesResponse(BaseModel):
    # Додаємо default=None та default_factory=list, щоб поля не були обов'язковими при створенні об'єкта
    detected_category: Optional[str] = Field(default=None)
    detected_country: Optional[str] = Field(default=None)
    alternatives: Annotated[
        List[AlternativeItem], 
        Field(default_factory=list, max_length=4)
    ]
    message: Optional[str] = Field(default=None)