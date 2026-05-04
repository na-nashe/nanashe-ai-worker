import json
import logging
import asyncio
from fastapi import APIRouter
from tenacity import retry, wait_random_exponential, stop_after_attempt
from aiokafka import AIOKafkaProducer 

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


logger = logging.getLogger(__name__)

router = APIRouter()


_producer = None

async def get_kafka_producer():
    """Лінива ініціалізація асинхронного продюсера."""
    global _producer
    if _producer is None:
        try:
           
            _producer = AIOKafkaProducer(
                bootstrap_servers='kafka:29092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await _producer.start()
            logger.info("AIOKafka Producer successfully initialized and started.")
        except Exception as e:
            logger.error(f"Failed to initialize AIOKafka Producer: {e}")
            _producer = None
    return _producer

async def publish_alternatives_to_kafka(ai_data: AIGeneratedData):
    """Асинхронно відправляє знайдені альтернативи в Kafka."""
    producer = await get_kafka_producer()
    
    if not producer:
        logger.warning("Kafka producer is not available. Skipping publish.")
        return

 
    if not ai_data.alternatives:
        logger.info("No alternatives to publish.")
        return

   
    payload = {
        "aliases": ai_data.aliases or [],
        "alternatives": [
            {
                "name": alt.name,
                "category": alt.category,
                "country": alt.country,
                "description": alt.description,
                "url": alt.url
            } for alt in ai_data.alternatives
        ]
    }

    try:
       
        await producer.send('alternatives', value=payload)
        logger.info("Successfully sent alternatives to Kafka asynchronously via aiokafka.")
    except Exception as e:
        logger.error(f"Error publishing to Kafka: {e}")
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
        
        
        asyncio.create_task(publish_alternatives_to_kafka(ai_data))
     
        
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
            aliases=ai_data.aliases,
            alternatives=ai_data.alternatives
        )
        
    except Exception as e:
        print(f"Critical AI Error: {e}")
        return AlternativesResponse(message=MSG_SERVICE_UNAVAILABLE, alternatives=[])

@router.post("/generate", response_model=AlternativesResponse)
async def generate_alternative_endpoint(request: SearchRequest):
    return await get_ai_response(request)