from locust import HttpUser, task, between

class RateGuardUser(HttpUser):
    wait_time = between(0.1, 0.5)  # wait 0.1-0.5s between requests
    def on_start(self):
        self.user_id = f"user_{self.environment.runner.user_count}"
    @task(1)
    def test_token_bucket(self):
        self.client.post("/check", json={
            "key": self.user_id,
            "algorithm": "token_bucket",
            "capacity": 100,
            "refill_rate": 10
        })
    
    @task(1)
    def test_sliding_window(self):
        self.client.post("/check", json={
            "key": self.user_id,
            "algorithm": "sliding_window",
            "max_requests": 100,
            "window_size": 60
        })

    @task(1)
    def test_fixed_window(self):
        self.client.post("/check", json={
            "key": self.user_id,
            "algorithm": "fixed_window",
            "max_requests": 100,
            "window_size": 60
        })