import asyncio
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.config import settings
from services.dispatchers.kafka.spiderweb_dispatcher import SpiderwebDispatcher


class KafkaService:
    _producer = None
    _consumers = {}

    def __init__(self):
        self.actions = {
            "spiderweb": SpiderwebDispatcher(),
        }

    async def get_producer(self):
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                enable_idempotence=True,
            )
            await self._producer.start()
        return self._producer

    async def close_producer(self):
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def send_message(self, topic: str, msg: dict):
        try:
            producer = await self.get_producer()
            await producer.send_and_wait(topic, self._serialize(msg))
        except Exception as err:
            print(f"Kafka send_message error: {err}")

    async def start_consumer(self, topic: str):
        if topic not in self._consumers:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=self._deserialize,
                group_id="control_service",
            )
            await consumer.start()
            self._consumers[topic] = consumer

            asyncio.create_task(self.consume(topic))

    async def consume(self, topic: str):
        consumer = self._consumers.get(topic)
        if not consumer:
            raise ValueError(f"No consumer for topic: {topic}")

        try:
            async for msg in consumer:
                await self._handle_message(msg)
        except Exception as err:
            print(f"Kafka consume error on topic {topic}: {err}")

    async def close_all_consumers(self):
        for topic, consumer in self._consumers.items():
            await consumer.stop()
        self._consumers.clear()

    async def _handle_message(self, msg):
        try:
            action = self.actions.get(msg.topic)
            if action:
                await action(msg.value["event_type"], msg.value)
            else:
                print(f"No handler for topic: {msg.topic}")
        except Exception as err:
            print(f"Message handling error: {err}")

    def _serialize(self, value):
        return json.dumps(value).encode()

    def _deserialize(self, value):
        return json.loads(value.decode())


kafka_service = KafkaService()
