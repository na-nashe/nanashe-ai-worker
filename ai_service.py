import json
from fastapi import APIRouter, HTTPException
from tenacity import retry, wait_random_exponential, stop_after_attempt
from ai_client import client, AI_MODEL
from prompts import generate_system_prompt
from models import SearchRequest, AlternativesResponse

router = APIRouter()


@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
async def call_openai(prompt: str, product_name: str) -> str:
    
    response = await client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Analyze: {product_name}"}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

async def get_ai_response(request: SearchRequest) -> AlternativesResponse:
    prompt = generate_system_prompt(request)

    try:
        raw_data = await call_openai(prompt, request.product_name)
        data = json.loads(raw_data)
        response_obj = AlternativesResponse.model_validate(data)
        
      
        if response_obj.detected_country is None:
            response_obj.message = "На жаль, ми не змогли розпізнати цей запит. Перевірте написання "
        else:
            country_upper = response_obj.detected_country.upper()
            is_hostile = any(word in country_upper for word in ["RUSSIA", "RU", "BELARUS", "BY", "РОСІЯ", "РФ"])
            
            if is_hostile:
                if not response_obj.alternatives:
                    response_obj.message = "Цей продукт ворожий, але ми поки не знайшли для нього ідеальних аналогів "
                else:
                    response_obj.message = "Цей продукт має вороже походження. Ми підібрали для вас чудові аналоги 🇺🇦"
            else:
                response_obj.message = "Цей бренд є безпечним. Проте, ось кілька українських альтернатив "
                
        return response_obj
        
    except Exception as e:
        print(f"Critical AI Error: {e}")
        
        return AlternativesResponse(message="Сервіс тимчасово перевантажений. Спробуйте через хвилинку ")


@router.post("/generate", response_model=AlternativesResponse)
async def generate_alternative_endpoint(request: SearchRequest):
    return await get_ai_response(request)