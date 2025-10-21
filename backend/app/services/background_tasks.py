import asyncio
import logging
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import TrainingDocument, AIAgent
from .document_processor import DocumentProcessor
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class BackgroundTaskService:
    """Service for handling background tasks like document processing"""

    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()

    async def process_pending_documents(self):
        """Process all pending documents in the background"""
        while True:
            try:
                # Get a database session
                db = SessionLocal()

                # Find pending documents
                pending_docs = db.query(TrainingDocument).filter(
                    TrainingDocument.processing_status == "uploaded"
                ).limit(5).all()  # Process 5 at a time

                if not pending_docs:
                    db.close()
                    await asyncio.sleep(30)  # Wait 30 seconds if no work
                    continue

                logger.info(f"Processing {len(pending_docs)} documents")

                # Process each document
                for doc in pending_docs:
                    try:
                        logger.info(f"Processing document {doc.id}: {doc.filename}")

                        # Step 1: Extract text
                        success = self.document_processor.process_document(doc, db)

                        if success:
                            # Step 2: Create embeddings
                            embedding_success = self.vector_store.create_embeddings_for_document(doc, db)

                            if embedding_success:
                                doc.training_status = "completed"
                                logger.info(f"Successfully processed document {doc.id}")
                            else:
                                doc.training_status = "failed"
                                logger.error(f"Failed to create embeddings for document {doc.id}")
                        else:
                            doc.training_status = "failed"
                            logger.error(f"Failed to process document {doc.id}")

                        db.commit()

                    except Exception as e:
                        logger.error(f"Error processing document {doc.id}: {str(e)}")
                        doc.training_status = "failed"
                        doc.error_message = str(e)
                        db.commit()

                db.close()

            except Exception as e:
                logger.error(f"Error in background document processing: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error

            # Small delay between batches
            await asyncio.sleep(5)

    async def update_ai_agent_training_status(self):
        """Update AI agent training status based on their documents"""
        while True:
            try:
                db = SessionLocal()

                # Get all AI agents
                agents = db.query(AIAgent).all()

                for agent in agents:
                    try:
                        # Get all documents for this agent's organization
                        org_docs = db.query(TrainingDocument).filter(
                            TrainingDocument.organization_id == agent.organization_id
                        ).all()

                        if not org_docs:
                            agent.training_status = "not_trained"
                            continue

                        # Check if all documents are trained
                        trained_docs = [doc for doc in org_docs if doc.training_status == "completed"]
                        failed_docs = [doc for doc in org_docs if doc.training_status == "failed"]

                        if len(trained_docs) == len(org_docs):
                            agent.training_status = "trained"
                            agent.last_trained_at = db.func.now()
                        elif failed_docs:
                            agent.training_status = "failed"
                        else:
                            agent.training_status = "training"

                        # Update trained document IDs
                        if trained_docs:
                            agent.trained_document_ids = ",".join(str(doc.id) for doc in trained_docs)

                    except Exception as e:
                        logger.error(f"Error updating agent {agent.id} training status: {str(e)}")

                db.commit()
                db.close()

            except Exception as e:
                logger.error(f"Error in agent training status update: {str(e)}")

            # Update every 5 minutes
            await asyncio.sleep(300)

    async def cleanup_old_data(self):
        """Clean up old temporary files and data"""
        while True:
            try:
                # This could clean up old log files, temporary uploads, etc.
                logger.info("Running cleanup tasks")

                # For now, just log - can add actual cleanup logic later
                # - Remove old temporary files
                # - Archive old conversation data
                # - Clean up failed processing attempts

            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")

            # Run daily
            await asyncio.sleep(86400)

# Global instance for easy access
background_service = BackgroundTaskService()

# Functions to start background tasks
async def start_background_tasks():
    """Start all background tasks"""
    logger.info("Starting background tasks...")

    # Start document processing
    asyncio.create_task(background_service.process_pending_documents())

    # Start agent status updates
    asyncio.create_task(background_service.update_ai_agent_training_status())

    # Start cleanup tasks
    asyncio.create_task(background_service.cleanup_old_data())

    logger.info("Background tasks started")

def get_background_service() -> BackgroundTaskService:
    """Get the global background service instance"""
    return background_service
