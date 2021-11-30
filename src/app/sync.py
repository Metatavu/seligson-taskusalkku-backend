import os
import sys
import asyncio
from aiokafka import AIOKafkaConsumer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def consume():
    """Waits for Kafka messages"""
    consumer = AIOKafkaConsumer(
        'FundSecurities',
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        group_id=os.getenv('KAFKA_GROUP', 'sync-group'))

    await consumer.start()
    print("Started synchronizing.")

    try:
        print("Waiting for messages...")
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        print("Stopping the consumer")
        await consumer.stop()
        print("Consumer stopped")

asyncio.run(consume())
