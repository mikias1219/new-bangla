import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from ..models import TrainingDocument, Organization, AIAgent
import logging
from .document_processor import DocumentProcessor

load_dotenv()
logger = logging.getLogger(__name__)

class VectorStore:
    """Service for managing vector embeddings and similarity search"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.document_processor = DocumentProcessor()
        self.embedding_model = "text-embedding-3-small"  # OpenAI's embedding model

    def create_embeddings_for_document(self, document: TrainingDocument, db: Session) -> bool:
        """Create vector embeddings for a processed document"""
        try:
            if not document.extracted_text:
                logger.error(f"No extracted text for document {document.id}")
                return False

            # Chunk the text for better retrieval
            chunks = self.document_processor.chunk_text(document.extracted_text)

            # Create embeddings for each chunk
            embeddings = []
            for chunk in chunks:
                embedding = self._create_embedding(chunk)
                if embedding:
                    embeddings.append({
                        'text': chunk,
                        'embedding': embedding,
                        'chunk_index': len(embeddings)
                    })

            if embeddings:
                # Save embeddings to file (for now - could use Pinecone, Weaviate, etc.)
                self._save_embeddings(document, embeddings)
                logger.info(f"Created {len(embeddings)} embeddings for document {document.id}")
                return True
            else:
                logger.error(f"No embeddings created for document {document.id}")
                return False

        except Exception as e:
            logger.error(f"Error creating embeddings for document {document.id}: {str(e)}")
            return False

    def _create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding for a text chunk using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return None

    def _save_embeddings(self, document: TrainingDocument, embeddings: List[Dict]):
        """Save embeddings to a JSON file for the organization"""
        org_dir = f"embeddings/organizations/{document.organization_id}"
        os.makedirs(org_dir, exist_ok=True)

        embedding_file = f"{org_dir}/document_{document.id}_embeddings.json"

        # Convert numpy arrays to lists for JSON serialization
        serializable_embeddings = []
        for emb in embeddings:
            serializable_embeddings.append({
                'text': emb['text'],
                'embedding': emb['embedding'],  # Already a list from OpenAI
                'chunk_index': emb['chunk_index']
            })

        with open(embedding_file, 'w', encoding='utf-8') as f:
            json.dump({
                'document_id': document.id,
                'filename': document.filename,
                'embeddings': serializable_embeddings,
                'created_at': str(document.processed_at)
            }, f, ensure_ascii=False, indent=2)

    def search_similar_content(self, query: str, organization_id: int, limit: int = 5) -> List[Dict]:
        """Search for similar content using vector similarity"""
        try:
            # Create embedding for the query
            query_embedding = self._create_embedding(query)
            if not query_embedding:
                return []

            # Load all embeddings for the organization
            org_dir = f"embeddings/organizations/{organization_id}"
            if not os.path.exists(org_dir):
                return []

            all_similar_chunks = []

            # Search through all document embeddings
            for filename in os.listdir(org_dir):
                if filename.endswith('_embeddings.json'):
                    file_path = os.path.join(org_dir, filename)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)

                    # Calculate similarity for each chunk
                    for chunk_data in doc_data['embeddings']:
                        chunk_embedding = chunk_data['embedding']
                        similarity = self._cosine_similarity(query_embedding, chunk_embedding)

                        all_similar_chunks.append({
                            'text': chunk_data['text'],
                            'similarity': similarity,
                            'document_id': doc_data['document_id'],
                            'filename': doc_data['filename'],
                            'chunk_index': chunk_data['chunk_index']
                        })

            # Sort by similarity and return top results
            all_similar_chunks.sort(key=lambda x: x['similarity'], reverse=True)
            return all_similar_chunks[:limit]

        except Exception as e:
            logger.error(f"Error searching similar content: {str(e)}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)

        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0

        return dot_product / (norm_vec1 * norm_vec2)

    def get_organization_context(self, organization_id: int, max_chunks: int = 10) -> str:
        """Get combined context from all trained documents for an organization"""
        org_dir = f"embeddings/organizations/{organization_id}"
        if not os.path.exists(org_dir):
            return ""

        context_parts = []

        try:
            for filename in os.listdir(org_dir):
                if filename.endswith('_embeddings.json'):
                    file_path = os.path.join(org_dir, filename)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)

                    # Take first few chunks from each document for context
                    chunks_taken = 0
                    for chunk_data in doc_data['embeddings']:
                        if chunks_taken >= max_chunks // max(1, len(os.listdir(org_dir))):
                            break
                        context_parts.append(chunk_data['text'])
                        chunks_taken += 1

        except Exception as e:
            logger.error(f"Error getting organization context: {str(e)}")

        return "\n\n".join(context_parts)
