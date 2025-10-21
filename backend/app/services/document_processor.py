import os
import fitz  # PyMuPDF for PDF processing
from docx import Document
import csv
import io
from typing import Dict, List, Optional
import openai
from dotenv import load_dotenv
import re
from sqlalchemy.orm import Session
from ..models import TrainingDocument, Organization
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing and extracting text from various document types"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def process_document(self, document: TrainingDocument, db: Session) -> bool:
        """Process a document and extract text content"""
        try:
            document.processing_status = "processing"
            db.commit()

            file_path = document.file_path
            content_type = document.content_type

            # Extract text based on file type
            if content_type == "pdf":
                extracted_text = self._extract_pdf_text(file_path)
            elif content_type in ["docx", "doc"]:
                extracted_text = self._extract_docx_text(file_path)
            elif content_type == "txt":
                extracted_text = self._extract_txt_text(file_path)
            elif content_type == "csv":
                extracted_text = self._extract_csv_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {content_type}")

            if extracted_text:
                # Clean and process the text
                cleaned_text = self._clean_text(extracted_text)

                # Update document record
                document.extracted_text = cleaned_text
                document.word_count = len(cleaned_text.split())
                document.page_count = self._estimate_page_count(cleaned_text)
                document.processing_status = "completed"
                document.processed_at = db.func.now()

                db.commit()
                logger.info(f"Successfully processed document {document.id}")
                return True
            else:
                document.processing_status = "failed"
                document.error_message = "No text could be extracted from the document"
                db.commit()
                return False

        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            document.processing_status = "failed"
            document.error_message = str(e)
            db.commit()
            return False

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _extract_csv_text(self, file_path: str) -> str:
        """Extract text from CSV file"""
        text = ""
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                text += " | ".join(row) + "\n"
        return text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)

        # Remove very short lines (likely headers/footers)
        lines = text.split('\n')
        filtered_lines = [line for line in lines if len(line.strip()) > 10]
        text = '\n'.join(filtered_lines)

        return text.strip()

    def _estimate_page_count(self, text: str) -> int:
        """Estimate page count based on word count (rough approximation)"""
        words_per_page = 300  # Average words per page
        word_count = len(text.split())
        return max(1, round(word_count / words_per_page))

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for embedding"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = words[i:i + chunk_size]
            if chunk:  # Only add non-empty chunks
                chunks.append(' '.join(chunk))

        return chunks
