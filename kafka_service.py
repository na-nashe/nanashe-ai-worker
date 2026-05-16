import os
import json
import logging
from aiokafka import AIOKafkaProducer
from models import AIGeneratedData, KafkaAlternativesEvent, KafkaAlternativeResponseDto
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
KAFKA_TOPIC = "alternatives"

_producer = None

async def get_producer():
    global _producer
    if _producer is None:
        try:
            _producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await _producer.start()
            logger.info("AIOKafka Producer successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize AIOKafka Producer: {e}")
            _producer = None
    return _producer

async def publish_alternatives_to_kafka(ai_data: AIGeneratedData):
    producer = await get_producer()
    
    if not producer:
        logger.warning("Kafka producer is not available. Skipping publish.")
        return
        
    if not ai_data.alternatives:
        logger.info("No alternatives to publish.")
        return
        

    kafka_event = KafkaAlternativesEvent(
        aliases=ai_data.aliases or [],
        productName=ai_data.official_title,
        productCategory=ai_data.detected_category,
        productCountry=ai_data.detected_country,
        alternatives=[
            KafkaAlternativeResponseDto(
                name=alt.name,
                country=alt.country,
                description=alt.description,
                pricingModel=alt.pricingModel,
                url=alt.url
            ) for alt in ai_data.alternatives
        ]
    )


    payload = kafka_event.dict()

    try:
        await producer.send(KAFKA_TOPIC, value=payload)
        logger.info(f"Successfully sent alternatives to Kafka for: {ai_data.official_title}")
    except Exception as e:
        logger.error(f"Failed to publish message to Kafka: {e}")