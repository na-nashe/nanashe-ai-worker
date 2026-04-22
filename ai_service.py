import json
from fastapi import APIRouter
from tenacity import retry, wait_random_exponential, stop_after_attempt
from ai_client import client, AI_MODEL
from prompts import generate_system_prompt
from models import SearchRequest, AlternativesResponse, AIGeneratedData


from constants import (
    MSG_UNKNOWN_PRODUCT,
    MSG_HOSTILE_NO_ALTS,
    MSG_HOSTILE_WITH_ALTS,
    MSG_SAFE_BRAND,
    MSG_SERVICE_UNAVAILABLE,
    HOSTILE_COUNTRIES
)

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
        raw_data = await call_openai(prompt, request.productName)
        data = json.loads(raw_data)
        
        
        ai_data = AIGeneratedData.model_validate(data)
        
       
        if ai_data.detected_country is None:
            final_message = MSG_UNKNOWN_PRODUCT
        else:
            country_upper = ai_data.detected_country.upper()
            is_hostile = any(word in country_upper for word in HOSTILE_COUNTRIES)
            
            if is_hostile:
                final_message = MSG_HOSTILE_WITH_ALTS if ai_data.alternatives else MSG_HOSTILE_NO_ALTS
            else:
                final_message = MSG_SAFE_BRAND
                
       
        return AlternativesResponse(
            message=final_message,
            alternatives=ai_data.alternatives
        )
        
    except Exception as e:
        print(f"Critical AI Error: {e}")
        return AlternativesResponse(message=MSG_SERVICE_UNAVAILABLE, alternatives=[])
@router.post("/generate", response_model=AlternativesResponse)
async def generate_alternative_endpoint(request: SearchRequest):
    return await get_ai_response(request)