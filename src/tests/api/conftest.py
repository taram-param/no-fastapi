from unittest.mock import AsyncMock

import pytest


@pytest.fixture
async def mocked_kafka_message(mocker) -> AsyncMock:
    return mocker.patch("services.kafka_service.KafkaService.send_message")
