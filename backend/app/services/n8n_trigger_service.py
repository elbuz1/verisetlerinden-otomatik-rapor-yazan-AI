"""
n8n Trigger Service
===================
Backend'den n8n'e webhook göndererek workflow'u başlatan servis.
Kullanıcı analiz talep ettiğinde bu servis n8n'deki Webhook node'unu tetikler.
n8n daha sonra sırayla backend endpoint'lerini çağırarak pipeline'ı yönetir.
"""

import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()


class N8NTriggerService:
    """n8n workflow'unu dışarıdan tetikleyen servis."""

    def __init__(self):
        self.webhook_base_url = settings.N8N_WEBHOOK_URL
        self.is_available = False

    async def check_n8n_connection(self) -> bool:
        """n8n'in çalışıp çalışmadığını kontrol et."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.N8N_API_URL.replace('/api/v1', '')}")
                self.is_available = response.status_code == 200
                return self.is_available
        except Exception:
            self.is_available = False
            return False

    async def trigger_analysis_workflow(
        self,
        dataset_id: int,
        user_id: int,
        format: str = "pdf"
    ) -> dict:
        """
        n8n'deki 'Veri Analiz Workflow' webhook'unu tetikler.

        n8n'de oluşturulan webhook URL'i:
        http://localhost:5678/webhook/data-analysis
        """
        webhook_url = f"{self.webhook_base_url}/data-analysis"

        payload = {
            "dataset_id": dataset_id,
            "user_id": user_id,
            "format": format,
            "callback_url": "http://localhost:8000/api/n8n"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(webhook_url, json=payload)

                if response.status_code == 200:
                    return {
                        "status": "triggered",
                        "n8n_response": response.json(),
                        "message": "n8n workflow basariyla tetiklendi"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"n8n webhook hatasi: {response.status_code}",
                        "fallback": True
                    }
        except httpx.ConnectError:
            return {
                "status": "unavailable",
                "message": "n8n servisi calismIyor. Dahili workflow kullanilacak.",
                "fallback": True
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"n8n tetikleme hatasi: {str(e)}",
                "fallback": True
            }

    async def get_n8n_status(self) -> dict:
        """n8n servisinin durumunu döndür."""
        is_connected = await self.check_n8n_connection()
        return {
            "n8n_available": is_connected,
            "webhook_url": self.webhook_base_url,
            "status": "connected" if is_connected else "disconnected",
            "message": (
                "n8n bagli ve calisIyor" if is_connected
                else "n8n calismIyor - dahili workflow aktif"
            )
        }


n8n_trigger_service = N8NTriggerService()
