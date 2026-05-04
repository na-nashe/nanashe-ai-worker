import logging
import asyncio
from fastapi import APIRouter
from tenacity import retry, wait_random_exponential, stop_after_attempt

from ai_client import client, AI_MODEL
from prompts import generate_system_prompt
from models import SearchRequest, AlternativesResponse, AIGeneratedData

# Import the Kafka publishing function from your new service
from kafka_service import publish_alternatives_to_kafka

from constants import (
    MSG_UNKNOWN_PRODUCT,
    MSG_HOSTILE_NO_ALTS,
    MSG_HOSTILE_WITH_ALTS,
    MSG_SAFE_WITH_ALTS,  # For safe brands WITH alternatives
    MSG_SAFE_NO_ALTS,    # For safe brands WITHOUT alternatives
    MSG_SERVICE_UNAVAILABLE,
    HOSTILE_COUNTRIES
)

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter()

@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
async def call_openai(prompt: str, product_name: str) -> str:
    # Calls OpenAI API to analyze the product and generate alternatives
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
    # Processes the search request and coordinates AI generation with Kafka publishing
    prompt = generate_system_prompt(request)

    try:
        # 1. Get raw data from AI provider
        raw_data = await call_openai(prompt, request.productName)
        
        # 2. Validate and parse the generated data
        ai_data = AIGeneratedData.model_validate_json(raw_data)
        
        # 3. Fire-and-forget task to publish data to Kafka asynchronously
        asyncio.create_task(publish_alternatives_to_kafka(ai_data))
        
        # 4. Logic to determine the safety status of the product
        if ai_data.detected_country is None:
            final_message = MSG_UNKNOWN_PRODUCT
        else:
            country_upper = ai_data.detected_country.upper()
            is_hostile = any(word in country_upper for word in HOSTILE_COUNTRIES)
            
            if is_hostile:
                final_message = MSG_HOSTILE_WITH_ALTS if ai_data.alternatives else MSG_HOSTILE_NO_ALTS
            else:
                # Determine response for safe brands based on alternatives availability
                final_message = MSG_SAFE_WITH_ALTS if ai_data.alternatives else MSG_SAFE_NO_ALTS
                
        return AlternativesResponse(
            message=final_message,
            aliases=ai_data.aliases,
            alternatives=ai_data.alternatives
        )
        
    except Exception as e:
        logger.error(f"Critical AI Error: {e}")
        return AlternativesResponse(message=MSG_SERVICE_UNAVAILABLE, alternatives=[])

@router.post("/generate", response_model=AlternativesResponse)
async def generate_alternative_endpoint(request: SearchRequest):
    # Endpoint for alternative brand generation
    return await get_ai_response(request)