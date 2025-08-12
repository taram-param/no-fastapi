from pydantic import BaseModel

from app.kafka_router import router


@router.after_startup
async def test(app):
    await router.broker.publish("Hello!", "test")


class Incoming(BaseModel):
    msg: str


def call() -> bool:
    return True


@router.subscriber("test")
@router.publisher("response")
async def hello(msg: Incoming):
    print("Incoming value: %s, depends value: %s" % (msg, "ho"))
    return {"response": "Hello, Kafka!"}

