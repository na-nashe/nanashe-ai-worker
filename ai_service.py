import os
import json
from fastapi import APIRouter, HTTPException

from models import SearchRequest, AlternativesResponse
from prompts import generate_system_prompt
from ai_client import client, AI_MODEL

router = APIRouter()

@router.post("/api/v1/generate", response_model=AlternativesResponse)
def generate_alternative(request: SearchRequest):
    
    formatted_prompt = generate_system_prompt(request)

    try:
        # Використовуємо стандартний метод create з JSON-режимом
        response = client.chat.completions.create(
            model=AI_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": f"Знайди альтернативи для: {request.product_name}"}
            ],
            response_format={"type": "json_object"}
        )
        
        # Отримуємо текст і перетворюємо його на об'єкт
        ai_content = response.choices[0].message.content
        data = json.loads(ai_content)
        
        # Валідуємо через Pydantic і повертаємо результат
        return AlternativesResponse(**data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))