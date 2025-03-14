import os
import logging
import asyncio
from typing import Optional, List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 
          'https://www.googleapis.com/auth/drive.readonly']

# Cache for document content to minimize API calls
_document_cache = {}

async def fetch_knowledge(query: str) -> Optional[str]:
    """
    Fetch relevant knowledge from Google Docs based on the query.
    
    Args:
        query: The user's question
    
    Returns:
        A string containing relevant information or None if no relevant info is found
    """
    try:
        # Get the document IDs from environment variables
        doc_ids_str = os.getenv("GOOGLE_DOC_IDS")
        if not doc_ids_str:
            logger.warning("GOOGLE_DOC_IDS not found in environment variables.")
            return None
            
        doc_ids = [doc_id.strip() for doc_id in doc_ids_str.split(',')]
        
        # Prepare the documents (fetch them from Google Docs)
        docs_content = await asyncio.gather(*[
            _get_document_content(doc_id) for doc_id in doc_ids
        ])
        
        # For now, implement a simple keyword-based search
        # In a more advanced implementation, you could use embeddings or a better search algorithm
        relevant_content = _simple_search(query, docs_content)
        
        return relevant_content
    except Exception as e:
        logger.error(f"Error fetching knowledge: {e}")
        return None

async def _get_document_content(doc_id: str) -> str:
    """
    Get content from a Google Doc by its ID.
    Uses caching to minimize API calls.
    
    Args:
        doc_id: The Google Doc ID
    
    Returns:
        The document content as a string
    """
    # Check if document is in cache
    if doc_id in _document_cache:
        return _document_cache[doc_id]
        
    try:
        # Run the API call in a thread to avoid blocking
        content = await asyncio.to_thread(_fetch_gdoc_content, doc_id)
        
        # Cache the result
        _document_cache[doc_id] = content
        
        return content
    except Exception as e:
        logger.error(f"Error retrieving document {doc_id}: {e}")
        return ""

def _fetch_gdoc_content(doc_id: str) -> str:
    """
    Synchronous function to fetch Google Doc content.
    
    Args:
        doc_id: The Google Doc ID
    
    Returns:
        The document content as a string
    """
    try:
        # Get credentials from the credentials file
        creds_path = os.getenv("GOOGLE_API_CREDENTIALS")
        if not creds_path:
            logger.error("GOOGLE_API_CREDENTIALS not found in environment variables.")
            return ""
            
        credentials = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES)
            
        # Build the Docs API client without proxies to avoid compatibility issues
        docs_service = build('docs', 'v1', credentials=credentials, cache_discovery=False)
        
        # Get the document
        document = docs_service.documents().get(documentId=doc_id).execute()
        
        # Extract text content
        content = ""
        if 'body' in document and 'content' in document['body']:
            for element in document['body']['content']:
                if 'paragraph' in element:
                    for paragraph_element in element['paragraph']['elements']:
                        if 'textRun' in paragraph_element:
                            content += paragraph_element['textRun']['content']
                            
        return content
    except HttpError as e:
        logger.error(f"HttpError while retrieving document {doc_id}: {e}")
        return ""
    except Exception as e:
        logger.error(f"Error retrieving document {doc_id}: {e}")
        return ""

def _simple_search(query: str, documents: List[str]) -> Optional[str]:
    """
    Simple keyword-based search to find relevant info in documents.
    
    Args:
        query: The user's question
        documents: List of document content strings
    
    Returns:
        Relevant content if found, None otherwise
    """
    # Convert query to lowercase for case-insensitive matching
    query_terms = query.lower().split()
    
    relevant_paragraphs = []
    
    for doc in documents:
        if not doc:
            continue
            
        # Split document into paragraphs
        paragraphs = [p for p in doc.split('\n\n') if p.strip()]
        
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            
            # Check if any query terms are in the paragraph
            if any(term in paragraph_lower for term in query_terms):
                relevant_paragraphs.append(paragraph.strip())
                
    if relevant_paragraphs:
        # Join the relevant paragraphs, limited to a reasonable length
        result = "\n\n".join(relevant_paragraphs[:5])  # Limit to 5 paragraphs
        
        # If the result is too long, truncate it
        if len(result) > 2000:
            result = result[:1997] + "..."
            
        return result
    
    return None 