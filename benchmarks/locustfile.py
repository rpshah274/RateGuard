from locust import HttpUser, task, between

class RateGuardUser(HttpUser):
    wait_time = between(0.1, 0.5)  # wait 0.1-0.5s between requests

    @task(1)
    def test_token_bucket(self):
        self.client.post("/check", json={
            "key": "locust_token_user",
            "algorithm": "token_bucket",
            "capacity": 3,
            "refill_rate": 1
        })
    
    @task(1)
    def test_sliding_window(self):
        self.client.post("/check", json={
            "key": "locust_sliding_user",
            "algorithm": "sliding_window",
            "max_requests": 100,
            "window_size": 60
        })

    @task(1)
    def test_fixed_window(self):
        self.client.post("/check", json={
            "key": "locust_fixed_user",
            "algorithm": "fixed_window",
            "max_requests": 100,
            "window_size": 60
        })