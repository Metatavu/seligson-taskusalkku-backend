import os
import sys
import asyncio
import logging

from aiokafka import AIOKafkaConsumer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from sync_handler.handler import SyncHandler

async def consume():
    """Waits for Kafka messages"""
    consumer = AIOKafkaConsumer(
        'FundSecurities', 'RATErah',
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        group_id=os.getenv('KAFKA_GROUP', 'sync-group'))

    await consumer.start()
    logger.info("Started synchronizing.")

    try:
        logger.info("Waiting for messages...")
        sync_handler = SyncHandler()
        async for msg in consumer:
            await sync_handler.handle_message(msg)
    finally:
        logger.info("Stopping the consumer")
        await consumer.stop()
        logger.info("Consumer stopped")

asyncio.run(consume())
