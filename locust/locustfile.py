import os
from uuid import uuid4

from locust import HttpUser, between, task

BEARER_TOKEN = os.getenv("LOCUST_BEARER_TOKEN")


class FastAPIUser(HttpUser):
    wait_time = between(1, 5)

    @task(10)
    def get_users(self):
        self.client.get("/api/v1/users/", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})

    @task(2)
    def create_note(self):
        unique_str = uuid4()
        self.client.post(
            "/api/v1/diary/notes/",
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
            json={
                "diary_id": 6,
                "title": f"title {unique_str}",
                "content": f"content {unique_str}",
            },
        )
