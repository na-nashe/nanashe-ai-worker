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
                {"role": "user", "content": f"Analyze {request.product_name} and return JSON."}
            ],
            response_format={"type": "json_object"}
        )

        raw_data = response.choices[0].message.content
        data = json.loads(raw_data)
        
        # Використовуємо .model_validate для безпечного створення об'єкта
        return AlternativesResponse.model_validate(data)
        
    except Exception as e:
        print(f"QA Alert: {e}")
        return AlternativesResponse(message=f"Технічна помилка: {str(e)}")

@router.post("/generate", response_model=AlternativesResponse)
async def generate_alternative_endpoint(request: SearchRequest):
    return get_ai_response(request)

def generate_alternative(request: SearchRequest) -> AlternativesResponse:
    return get_ai_response(request)