class RateLimiter:
    def __init__(self):
        self.requests = {}

    def check(self, key: str, client_ip: str):
        # Simple in-memory rate limit (demo)
        if client_ip in self.requests:
            self.requests[client_ip] += 1
        else:
            self.requests[client_ip] = 1

        if self.requests[client_ip] > 100:
            raise Exception("Rate limit exceeded")

limiter = RateLimiter()
