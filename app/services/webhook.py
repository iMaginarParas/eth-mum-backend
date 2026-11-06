import hmac
import hashlib
import httpx
import logging
from typing import Dict, Any
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self):
        self.secret = settings.WEBHOOK_SECRET

    def generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        expected_signature = self.generate_signature(payload)
        return hmac.compare_digest(expected_signature, signature)

    async def send_webhook(
        self,
        webhook_url: str,
        event_type: str,
        data: Dict[str, Any],
        max_retries: int = 3
    ) -> bool:
        """Send webhook with retry logic"""
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        import json
        payload_str = json.dumps(payload, default=str)
        signature = self.generate_signature(payload_str)

        headers = {
            "Content-Type": "application/json",
            "X-PayLink-Signature": signature,
            "X-PayLink-Event": event_type
        }

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        webhook_url,
                        content=payload_str,
                        headers=headers
                    )

                    if response.status_code == 200:
                        logger.info(f"Webhook sent successfully: {event_type}")
                        return True
                    else:
                        logger.warning(
                            f"Webhook failed with status {response.status_code}: "
                            f"{event_type} (attempt {attempt + 1}/{max_retries})"
                        )
            except Exception as e:
                logger.error(
                    f"Webhook error: {e} (attempt {attempt + 1}/{max_retries})"
                )

            if attempt < max_retries - 1:
                # Exponential backoff
                import asyncio
                await asyncio.sleep(2 ** attempt)

        logger.error(f"Webhook failed after {max_retries} attempts: {event_type}")
        return False


webhook_service = WebhookService()
