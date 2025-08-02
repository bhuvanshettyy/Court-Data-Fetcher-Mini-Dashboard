import os
import logging
import requests
import hashlib
from urllib.parse import urlparse, unquote
from datetime import datetime
import PyPDF2
from io import BytesIO

logger = logging.getLogger(__name__)

class PDFHandler:
    """PDF download and processing utility"""
    
    def __init__(self):
        self.downloads_dir = os.path.join('static', 'downloads')
        self.ensure_downloads_dir()
    
    def ensure_downloads_dir(self):
        """Ensure downloads directory exists"""
        try:
            os.makedirs(self.downloads_dir, exist_ok=True)
            logger.info(f"Downloads directory ready: {self.downloads_dir}")
        except Exception as e:
            logger.error(f"Error creating downloads directory: {str(e)}")
    
    def download_pdf(self, pdf_url):
        """Download PDF from URL and save to local storage"""
        try:
            # Clean and validate URL
            pdf_url = unquote(pdf_url)
            if not pdf_url.startswith(('http://', 'https://')):
                logger.error(f"Invalid PDF URL: {pdf_url}")
                return None
            
            # Generate filename from URL
            filename = self._generate_filename(pdf_url)
            filepath = os.path.join(self.downloads_dir, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                logger.info(f"PDF already exists: {filepath}")
                return filepath
            
            # Download PDF
            logger.info(f"Downloading PDF from: {pdf_url}")
            response = requests.get(pdf_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Verify it's actually a PDF
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower():
                logger.warning(f"URL does not appear to be a PDF: {content_type}")
            
            # Save PDF
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"PDF downloaded successfully: {filepath}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading PDF: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {str(e)}")
            return None
    
    def _generate_filename(self, pdf_url):
        """Generate a unique filename for the PDF"""
        try:
            # Parse URL to get original filename
            parsed_url = urlparse(pdf_url)
            original_filename = os.path.basename(parsed_url.path)
            
            # If no filename in URL, generate one
            if not original_filename or '.' not in original_filename:
                # Create hash from URL
                url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:8]
                original_filename = f"court_document_{url_hash}.pdf"
            
            # Ensure .pdf extension
            if not original_filename.lower().endswith('.pdf'):
                original_filename += '.pdf'
            
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{timestamp}{ext}"
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating filename: {str(e)}")
            # Fallback filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"court_document_{timestamp}.pdf"
    
    def extract_text(self, pdf_path):
        """Extract text from PDF file"""
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return None
            
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def get_pdf_info(self, pdf_path):
        """Get basic information about PDF file"""
        try:
            if not os.path.exists(pdf_path):
                return None
            
            info = {
                'filename': os.path.basename(pdf_path),
                'size': os.path.getsize(pdf_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(pdf_path))
            }
            
            # Try to get PDF metadata
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    info['pages'] = len(pdf_reader.pages)
                    
                    # Get document info if available
                    if pdf_reader.metadata:
                        info['title'] = pdf_reader.metadata.get('/Title', 'Unknown')
                        info['author'] = pdf_reader.metadata.get('/Author', 'Unknown')
                        info['subject'] = pdf_reader.metadata.get('/Subject', 'Unknown')
                        info['creator'] = pdf_reader.metadata.get('/Creator', 'Unknown')
            except Exception as e:
                logger.warning(f"Could not read PDF metadata: {str(e)}")
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info: {str(e)}")
            return None
    
    def cleanup_old_files(self, max_age_days=30):
        """Clean up old PDF files"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            cleaned_count = 0
            
            for filename in os.listdir(self.downloads_dir):
                filepath = os.path.join(self.downloads_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        cleaned_count += 1
                        logger.info(f"Cleaned up old file: {filename}")
            
            logger.info(f"Cleanup completed: {cleaned_count} files removed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def get_downloads_list(self):
        """Get list of downloaded PDFs"""
        try:
            files = []
            for filename in os.listdir(self.downloads_dir):
                filepath = os.path.join(self.downloads_dir, filename)
                if os.path.isfile(filepath) and filename.lower().endswith('.pdf'):
                    info = self.get_pdf_info(filepath)
                    if info:
                        files.append(info)
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"Error getting downloads list: {str(e)}")
            return [] 