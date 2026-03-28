import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from enum import Enum

load_dotenv()
app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AlternativeResult(BaseModel):
    name: str
    description: str
    url: Optional[str]
    aliases: List[str]

# Спрощений та сфокусований список категорій
class CategoryEnum(str, Enum):
    software = "Програми та сервіси"
    food = "Їжа та напої"
    brands = "Бренди (одяг, косметика, речі)"
    other = "Інше"

class SearchRequest(BaseModel):
    product_name: str
    category: CategoryEnum = CategoryEnum.software  # За замовчуванням шукаємо програми
    is_healthy: Optional[bool] = False
    extra_wishes: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Server is running! Go to /docs to test."}

@app.post("/api/v1/generate")
def generate_alternative(request: SearchRequest):
    print(f"Шукаємо: {request.product_name}, Категорія: {request.category.value}")
    
    # Твій новий детальний промпт для ШІ
    system_prompt = f"""
Ти — суворий експерт-аналітик сервісу NaNashe. Твоє завдання: знаходити ТІЛЬКИ українські альтернативи продуктам, брендам і сервісам.

ЗАВДАННЯ:
Знайти 3-4 РЕАЛЬНІ українські альтернативи до: "{request.product_name}"

КОНТЕКСТ:
Категорія: {request.category.value}
Побажання: {request.extra_wishes if request.extra_wishes else "немає"}
Здорове харчування: {request.is_healthy}

КРИТИЧНІ ПРАВИЛА (АНТИ-ГАЛЮЦИНАЦІЯ):
1. ЖОДНИХ ВИГАДАНИХ НАЗВ: Ти повинен пропонувати ТІЛЬКИ реально існуючі на ринку України бренди. Наприклад, якщо шукають "Pringles", пропонуй реальні "Люкс", "Chipster's" або "Flint". Ніяких вигаданих "Смаколиків" чи "Чіпсів з любов'ю"! Якщо не знаєш — краще дай найпопулярніший реальний продукт у цій категорії.
2. ТІЛЬКИ українське походження: створено в Україні або українськими компаніями.
3. ЗАБОРОНЕНО: російські, білоруські, міжнародні аналоги.
4. Якщо точного аналога (наприклад, чіпсів у тубусі) немає — давай найближчий популярний український аналог (звичайні чіпси в пачці).
5. Виправляй опечатки в запиті користувача подумки.

ФОРМАТ ВІДПОВІДІ (ТІЛЬКИ JSON):
[
  {{
    "name": "Реальна Назва",
    "description": "Чому це хороша альтернатива",
    "url": "сайт або null",
    "aliases": ["інші назви"]
  }}
]

НЕ пиши нічого поза JSON.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3, # Додали температуру, щоб не фантазував!
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Знайди українські альтернативи для: {request.product_name}"}
            ]
        )
        
        ai_text = response.choices[0].message.content
        
        result_data = {
            "name": "Добірка альтернатив",
            "description": ai_text, # Тут тепер буде лежати красивий JSON від ШІ
            "url": "",
            "aliases": []
        }
        
        java_url = os.getenv("JAVA_SERVER_URL", "http://localhost:8080/api/alternatives")
        try:
            java_response = requests.post(java_url, json=result_data, timeout=5)
            java_status = f"Sent to Java" if java_response.ok else f"Java Error: {java_response.status_code}"
        except:
            java_status = "Java offline"
            
        return {"status": "success", "data": result_data, "java": java_status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))