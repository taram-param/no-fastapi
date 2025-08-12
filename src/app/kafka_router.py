from faststream.kafka import fastapi
from faststream.kafka.broker.broker import KafkaBroker

from app.config import settings

router = fastapi.KafkaRouter(settings.KAFKA_BOOTSTRAP_SERVERS)


def get_broker() -> KafkaBroker:
    return router.broker
