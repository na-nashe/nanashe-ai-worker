import json
from fastapi import APIRouter
from ai_client import client, AI_MODEL
from prompts import generate_system_prompt
from models import SearchRequest, AlternativesResponse

router = APIRouter()

def get_ai_response(request: SearchRequest) -> AlternativesResponse:
    prompt = generate_system_prompt(request)

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Analyze: {request.product_name}"}
            ],
            temperature=0.0, # Тільки 0.0 для максимальної точності!
            response_format={"type": "json_object"}
        )

        raw_data = response.choices[0].message.content
        data = json.loads(raw_data)
        response_obj = AlternativesResponse.model_validate(data)
        
        # --- ПЕРЕВІРКА ПОВІДОМЛЕНЬ ---
        if response_obj.detected_country is None:
            response_obj.message = "На жаль, ми не змогли розпізнати цей запит 🕵️‍♀️"
        else:
            country_upper = response_obj.detected_country.upper()
            # Додаємо Нурі в перевірку, про всяк випадок
            is_hostile = any(word in country_upper for word in ["RUSSIA", "RU", "BELARUS", "BY", "РОСІЯ"]) or "НУРІ" in request.product_name.upper()
            
            if is_hostile:
                response_obj.message = "Цей продукт має вороже походження. Ми підібрали для вас чудові аналоги 🇺🇦"
            else:
                response_obj.message = "Цей бренд є безпечним. Проте, ось кілька українських альтернатив 💛💙"
                
        return response_obj
        
    except Exception as e:
        return AlternativesResponse(message=f"Технічна помилка: {str(e)}")

@router.post("/generate", response_model=AlternativesResponse)
async def generate_alternative_endpoint(request: SearchRequest):
    return get_ai_response(request)