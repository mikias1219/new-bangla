import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class N8NService:
    """Service for integrating with n8n workflows for CRM and audit logging"""

    def __init__(self):
        self.n8n_base_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
        self.n8n_api_key = os.getenv("N8N_API_KEY")

        # Webhook URLs for different workflows
        self.crm_webhook_url = f"{self.n8n_base_url}/webhook/crm-integration"
        self.audit_webhook_url = f"{self.n8n_base_url}/webhook/audit-log"
        self.notification_webhook_url = f"{self.n8n_base_url}/webhook/notifications"

        # HTTP client for async requests
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.n8n_api_key or ""
            }
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def send_to_crm_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data to CRM integration workflow"""
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "bangla_chat_pro",
                **data
            }

            logger.info(f"Sending CRM request to n8n: {data.get('operation', 'unknown')}")

            response = await self.client.post(
                self.crm_webhook_url,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("CRM workflow executed successfully")
                return result
            else:
                logger.error(f"CRM workflow failed: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error": f"CRM workflow failed: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            logger.error(f"Error sending to CRM workflow: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def send_to_audit_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send audit event to logging workflow"""
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "bangla_chat_pro",
                **data
            }

            logger.info(f"Sending audit event to n8n: {data.get('event_type', 'unknown')}")

            response = await self.client.post(
                self.audit_webhook_url,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("Audit logging successful")
                return result
            else:
                logger.error(f"Audit logging failed: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error": f"Audit logging failed: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            logger.error(f"Error sending audit event: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def send_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification through n8n workflow"""
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "bangla_chat_pro",
                **data
            }

            logger.info(f"Sending notification to n8n: {data.get('type', 'unknown')}")

            response = await self.client.post(
                self.notification_webhook_url,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("Notification sent successfully")
                return result
            else:
                logger.error(f"Notification failed: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error": f"Notification failed: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    # Specific CRM operations
    async def get_order_status(self, order_id: str, crm_system: str = "generic", api_config: Dict = None) -> Dict[str, Any]:
        """Get order status from CRM system"""
        return await self.send_to_crm_workflow({
            "operation": "get_order_status",
            "crm_system": crm_system,
            "order_id": order_id,
            "api_config": api_config or {}
        })

    async def get_customer_info(self, customer_id: str, crm_system: str = "generic", api_config: Dict = None) -> Dict[str, Any]:
        """Get customer information from CRM system"""
        return await self.send_to_crm_workflow({
            "operation": "get_customer_info",
            "crm_system": crm_system,
            "customer_id": customer_id,
            "api_config": api_config or {}
        })

    async def get_product_info(self, product_id: str, crm_system: str = "generic", api_config: Dict = None) -> Dict[str, Any]:
        """Get product information from CRM system"""
        return await self.send_to_crm_workflow({
            "operation": "get_product_info",
            "crm_system": crm_system,
            "product_id": product_id,
            "api_config": api_config or {}
        })

    async def search_products(self, query: str, crm_system: str = "generic", api_config: Dict = None) -> Dict[str, Any]:
        """Search for products in CRM system"""
        return await self.send_to_crm_workflow({
            "operation": "search_products",
            "crm_system": crm_system,
            "query": query,
            "api_config": api_config or {}
        })

    # Audit logging methods
    async def log_chat_message(self, conversation_id: int, user_id: Optional[int],
                             organization_id: int, message: str, sender_type: str,
                             confidence_score: Optional[float] = None) -> Dict[str, Any]:
        """Log chat message event"""
        return await self.send_to_audit_workflow({
            "event_type": "chat_message",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "message": message,
            "sender_type": sender_type,
            "confidence_score": confidence_score,
            "severity": "low"
        })

    async def log_ivr_call(self, call_sid: str, from_number: str, to_number: str,
                          organization_id: int, status: str, duration: Optional[float] = None,
                          ai_interactions: int = 0) -> Dict[str, Any]:
        """Log IVR call event"""
        return await self.send_to_audit_workflow({
            "event_type": "ivr_call",
            "call_sid": call_sid,
            "from_number": from_number,
            "to_number": to_number,
            "organization_id": organization_id,
            "status": status,
            "duration": duration,
            "ai_interactions": ai_interactions,
            "severity": "medium" if status == "escalated" else "low"
        })

    async def log_escalation(self, conversation_id: int, user_id: Optional[int],
                           organization_id: int, reason: str, escalated_to: str) -> Dict[str, Any]:
        """Log escalation event"""
        return await self.send_to_audit_workflow({
            "event_type": "escalation",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "reason": reason,
            "escalated_to": escalated_to,
            "severity": "high"
        })

    async def log_admin_action(self, admin_id: int, organization_id: int,
                             action: str, target_type: str, target_id: int,
                             details: Dict[str, Any]) -> Dict[str, Any]:
        """Log admin action event"""
        return await self.send_to_audit_workflow({
            "event_type": "admin_action",
            "admin_id": admin_id,
            "organization_id": organization_id,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "details": details,
            "severity": "medium"
        })

    # Notification methods
    async def send_escalation_alert(self, conversation_id: int, user_info: Dict[str, Any],
                                  reason: str) -> Dict[str, Any]:
        """Send escalation alert"""
        return await self.send_notification({
            "type": "escalation_alert",
            "conversation_id": conversation_id,
            "user_info": user_info,
            "reason": reason,
            "priority": "high"
        })

    async def send_system_alert(self, alert_type: str, message: str,
                              severity: str = "medium") -> Dict[str, Any]:
        """Send system alert"""
        return await self.send_notification({
            "type": "system_alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        })

    async def send_performance_alert(self, metric: str, value: float,
                                   threshold: float) -> Dict[str, Any]:
        """Send performance alert"""
        return await self.send_notification({
            "type": "performance_alert",
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "severity": "medium"
        })

    # Workflow management
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of all n8n workflows"""
        try:
            # This would typically call n8n API to get workflow status
            # For now, return a basic health check
            response = await self.client.get(f"{self.n8n_base_url}/health")
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "workflows": ["crm-integration", "audit-logging", "notification-system"]
            }
        except Exception as e:
            logger.error(f"Error checking workflow status: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    # Batch operations for better performance
    async def batch_log_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Log multiple events in batch"""
        results = []
        for event in events:
            result = await self.send_to_audit_workflow(event)
            results.append(result)

            # Small delay to avoid overwhelming n8n
            await asyncio.sleep(0.1)

        return results

    # Health check
    async def health_check(self) -> bool:
        """Check if n8n service is healthy"""
        try:
            response = await self.client.get(f"{self.n8n_base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
