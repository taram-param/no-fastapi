class SpiderwebDispatcher:
    def __init__(self):
        self.events = {
            "hello": self._hello,
            "create": self._create,
        }

    async def __call__(self, event_type: str, msg: dict):
        await self.events[event_type](msg)

    async def _hello(self, msg: dict):
        print("hello")
        print(msg)

    async def _create(self, msg: dict):
        pass
