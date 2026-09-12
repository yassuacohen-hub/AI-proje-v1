from locust import HttpUser, task, between
import os
import json
import hmac
import hashlib
from datetime import datetime, timezone

class WebhookUser(HttpUser):
    wait_time = between(1, 3)
    host = os.getenv("TARGET_HOST", "http://localhost:8000")
    secret_token = os.getenv("WEBHOOK_SECRET", "test-secret")

    def _generate_signature(self, payload: bytes) -> str:
        """Generate HMAC-SHA256 signature."""
        return hmac.new(self.secret_token.encode(), payload, hashlib.sha256).hexdigest()

    @task
    def post_webhook_success(self):
        payload = {
            "eventType": "ACTOR.RUN.SUCCEEDED",
            "actorRunId": f"run-{self.__class__.__name__}-{self.id}",
            "actorId": "ziyrak/kariyer-scraper",
            "resource": {
                "id": f"run-{self.__class__.__name__}-{self.id}",
                "actorId": "ziyrak/kariyer-scraper",
                "defaultDatasetId": f"ds-{self.__class__.__name__}-{self.id}",
                "status": "SUCCEEDED",
            },
        }
        payload_bytes = json.dumps(payload).encode()
        signature = self._generate_signature(payload_bytes)
        headers = {
            "Content-Type": "application/json",
            "X-Signature": f"sha256={signature}",
            "X-Secret": self.secret_token,
        }
        self.client.post("/api/webhooks/apify", data=payload_bytes, headers=headers, name="webhook_success")

    @task
    def post_webhook_failure(self):
        payload = {
            "eventType": "ACTOR.RUN.SUCCEEDED",
            "actorRunId": f"run-fail-{self.__class__.__name__}-{self.id}",
            "actorId": "ziyrak/kariyer-scraper",
            "resource": {
                "id": f"run-fail-{self.__class__.__name__}-{self.id}",
                "actorId": "ziyrak/kariyer-scraper",
                "defaultDatasetId": f"ds-fail-{self.__class__.__name__}-{self.id}",
                "status": "SUCCEEDED",
            },
        }
        payload_bytes = json.dumps(payload).encode()
        # Wrong signature
        signature = self._generate_signature(b"wrong")
        headers = {
            "Content-Type": "application/json",
            "X-Signature": f"sha256={signature}",
            "X-Secret": self.secret_token,
        }
        self.client.post("/api/webhooks/apify", data=payload_bytes, headers=headers, name="webhook_failure")

class MCPUser(HttpUser):
    wait_time = between(2, 5)
    host = os.getenv("MCP_HOST", "http://localhost:8000")

    @task
    def get_source_policy(self):
        self.client.get("/mcp/get_source_policy", name="mcp_get_source_policy")

    @task
    def get_collection_run_status(self):
        self.client.get("/mcp/get_collection_run_status", name="mcp_get_collection_run_status")

    @task
    def submit_evidence_batch(self):
        payload = {
            "company_id": "test-company",
            "evidence": [{"key": "test", "value": "value"}],
        }
        self.client.post("/mcp/submit_evidence_batch", json=payload, name="mcp_submit_evidence")

    @task
    def report_collection_failure(self):
        payload = {
            "company_id": "test-company",
            "reason": "test failure",
        }
        self.client.post("/mcp/report_collection_failure", json=payload, name="mcp_report_failure")
