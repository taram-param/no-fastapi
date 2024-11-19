import os

from locust import HttpUser, task, between


BEARER_TOKEN = os.getenv("LOCUST_BEARER_TOKEN")


class FastAPIUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    @task
    def get_root(self):
        self.client.get("/api/v1/users/", headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
