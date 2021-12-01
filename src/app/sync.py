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
        'FundSecurities',
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        group_id=os.getenv('KAFKA_GROUP', 'sync-group'))

    await consumer.start()
    logger.info("Started synchronizing.")

    try:
        logger.info("Waiting for messages...")
        sync = SyncHandler()
        async for msg in consumer:
            if (msg.topic == "FundSecurities"):
                await sync.sync_fund_securities(msg)
            else:
                logger.warning(f"Unknown message from topic {msg.topic}")
    finally:
        logger.info("Stopping the consumer")
        await consumer.stop()
        logger.info("Consumer stopped")

asyncio.run(consume())
