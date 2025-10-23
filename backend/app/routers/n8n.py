from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.n8n_service import N8NService
from ..services.ai_chat import AIChatService
from ..services.ivr_service import IVRService
from ..auth.jwt import get_current_user
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
n8n_service = N8NService()

@router.post("/webhooks/crm-data")
async def handle_crm_webhook(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle CRM data requests from n8n workflows"""
    try:
        operation = data.get("operation")
        crm_system = data.get("crm_system", "generic")

        logger.info(f"CRM webhook request: {operation} for {crm_system}")

        # Route to appropriate handler
        if operation == "get_order_status":
            order_id = data.get("order_id")
            if not order_id:
                raise HTTPException(status_code=400, detail="Order ID required")

            # For now, return mock data - in production this would call actual CRM
            result = {
                "status": "success",
                "order_id": order_id,
                "order_status": "shipped",
                "tracking_number": f"TN{order_id}",
                "estimated_delivery": "2024-01-15"
            }

        elif operation == "get_customer_info":
            customer_id = data.get("customer_id")
            if not customer_id:
                raise HTTPException(status_code=400, detail="Customer ID required")

            result = {
                "status": "success",
                "customer_id": customer_id,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "loyalty_points": 150
            }

        elif operation == "get_product_info":
            product_id = data.get("product_id")
            if not product_id:
                raise HTTPException(status_code=400, detail="Product ID required")

            result = {
                "status": "success",
                "product_id": product_id,
                "name": "Sample Product",
                "price": 99.99,
                "stock_quantity": 50,
                "category": "Electronics"
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {operation}")

        return result

    except Exception as e:
        logger.error(f"CRM webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/audit-log")
async def handle_audit_log_webhook(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Handle audit logging requests from n8n workflows"""
    try:
        event_type = data.get("event_type")
        logger.info(f"Audit log webhook: {event_type}")

        # In a production system, you might want to:
        # 1. Validate the event data
        # 2. Store in additional databases
        # 3. Send to external logging services
        # 4. Trigger compliance workflows

        # For now, just acknowledge receipt
        result = {
            "status": "logged",
            "event_type": event_type,
            "timestamp": data.get("timestamp"),
            "log_id": f"log_{hash(str(data))}"
        }

        # Log to application logger as well
        logger.info(f"AUDIT: {event_type} - {data}")

        return result

    except Exception as e:
        logger.error(f"Audit log webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/notifications")
async def handle_notification_webhook(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Handle notification requests from n8n workflows"""
    try:
        notification_type = data.get("type")
        logger.info(f"Notification webhook: {notification_type}")

        # Here you could integrate with:
        # - Email services (SendGrid, Mailgun)
        # - SMS services (Twilio, AWS SNS)
        # - Push notifications
        # - Internal alerting systems

        result = {
            "status": "sent",
            "notification_type": notification_type,
            "timestamp": data.get("timestamp"),
            "notification_id": f"notif_{hash(str(data))}"
        }

        logger.info(f"NOTIFICATION: {notification_type} - {data}")

        return result

    except Exception as e:
        logger.error(f"Notification webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crm/{operation}")
async def crm_operation(
    operation: str,
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute CRM operation via n8n workflow"""
    try:
        async with N8NService() as n8n:
            if operation == "order-status":
                order_id = data.get("order_id")
                crm_system = data.get("crm_system", "generic")

                result = await n8n.get_order_status(order_id, crm_system)
                return result

            elif operation == "customer-info":
                customer_id = data.get("customer_id")
                crm_system = data.get("crm_system", "generic")

                result = await n8n.get_customer_info(customer_id, crm_system)
                return result

            elif operation == "product-info":
                product_id = data.get("product_id")
                crm_system = data.get("crm_system", "generic")

                result = await n8n.get_product_info(product_id, crm_system)
                return result

            elif operation == "search-products":
                query = data.get("query")
                crm_system = data.get("crm_system", "generic")

                result = await n8n.search_products(query, crm_system)
                return result

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported CRM operation: {operation}")

    except Exception as e:
        logger.error(f"CRM operation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit/log")
async def log_audit_event(
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Log audit event via n8n workflow"""
    try:
        # Add user context
        data["user_id"] = current_user.get("id")
        data["organization_id"] = current_user.get("organization_id")

        async with N8NService() as n8n:
            result = await n8n.send_to_audit_workflow(data)
            return result

    except Exception as e:
        logger.error(f"Audit logging error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/send")
async def send_notification(
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send notification via n8n workflow"""
    try:
        async with N8NService() as n8n:
            result = await n8n.send_notification(data)
            return result

    except Exception as e:
        logger.error(f"Notification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/status")
async def get_workflows_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get status of n8n workflows"""
    try:
        async with N8NService() as n8n:
            status = await n8n.get_workflow_status()
            return status

    except Exception as e:
        logger.error(f"Workflow status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrations/test")
async def test_n8n_integration(
    data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Test n8n integration connectivity"""
    try:
        async with N8NService() as n8n:
            # Test health check
            health = await n8n.health_check()

            # Test CRM workflow
            crm_test = await n8n.send_to_crm_workflow({
                "operation": "test",
                "test_data": "integration_test"
            })

            # Test audit workflow
            audit_test = await n8n.send_to_audit_workflow({
                "event_type": "integration_test",
                "test": True
            })

            return {
                "health_check": health,
                "crm_workflow": crm_test,
                "audit_workflow": audit_test,
                "timestamp": "2024-01-01T00:00:00Z"
            }

    except Exception as e:
        logger.error(f"Integration test error: {str(e)}")
        return {
            "health_check": False,
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

# Background task handlers for async logging
async def log_chat_message_async(conversation_id: int, user_id: Optional[int],
                               organization_id: int, message: str, sender_type: str,
                               confidence_score: Optional[float] = None):
    """Background task to log chat messages"""
    try:
        async with N8NService() as n8n:
            await n8n.log_chat_message(
                conversation_id, user_id, organization_id,
                message, sender_type, confidence_score
            )
    except Exception as e:
        logger.error(f"Async chat logging error: {str(e)}")

async def log_ivr_call_async(call_sid: str, from_number: str, to_number: str,
                           organization_id: int, status: str, duration: Optional[float] = None,
                           ai_interactions: int = 0):
    """Background task to log IVR calls"""
    try:
        async with N8NService() as n8n:
            await n8n.log_ivr_call(
                call_sid, from_number, to_number, organization_id,
                status, duration, ai_interactions
            )
    except Exception as e:
        logger.error(f"Async IVR logging error: {str(e)}")

async def log_escalation_async(conversation_id: int, user_id: Optional[int],
                             organization_id: int, reason: str, escalated_to: str):
    """Background task to log escalations"""
    try:
        async with N8NService() as n8n:
            await n8n.log_escalation(conversation_id, user_id, organization_id, reason, escalated_to)

            # Also send notification
            await n8n.send_escalation_alert(conversation_id, {"user_id": user_id}, reason)

    except Exception as e:
        logger.error(f"Async escalation logging error: {str(e)}")

# Utility functions for other services to use
async def log_chat_event_background(conversation_id: int, user_id: Optional[int],
                                  organization_id: int, message: str, sender_type: str,
                                  confidence_score: Optional[float] = None):
    """Utility function for other services to log chat events"""
    asyncio.create_task(log_chat_message_async(
        conversation_id, user_id, organization_id, message, sender_type, confidence_score
    ))

async def log_ivr_event_background(call_sid: str, from_number: str, to_number: str,
                                 organization_id: int, status: str, duration: Optional[float] = None,
                                 ai_interactions: int = 0):
    """Utility function for other services to log IVR events"""
    asyncio.create_task(log_ivr_call_async(
        call_sid, from_number, to_number, organization_id, status, duration, ai_interactions
    ))

async def log_escalation_event_background(conversation_id: int, user_id: Optional[int],
                                        organization_id: int, reason: str, escalated_to: str):
    """Utility function for other services to log escalation events"""
    asyncio.create_task(log_escalation_async(
        conversation_id, user_id, organization_id, reason, escalated_to
    ))
