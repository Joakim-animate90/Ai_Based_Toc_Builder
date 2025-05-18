import os
from app.utils.decorators import timing_decorator
from app.services.pdf_service import PDFService
from app.services.openai_service import OpenAIService

class TOCService:
    """Service for Table of Contents extraction operations."""
    
    def __init__(self, thread_count=None):
        """Initialize the TOC extraction service."""
        self.pdf_service = PDFService(thread_count=thread_count)
        self.openai_service = OpenAIService()
    
    @timing_decorator
    def extract_toc(self, pdf_path, output_file=None):
        """
        Extract Table of Contents from a PDF file using OpenAI's Vision API.
        
        Args:
            pdf_path: Path to the PDF file
            output_file: Optional output file path
            
        Returns:
            tuple: (toc_content, output_file_path)
        """
        # Convert PDF pages to base64-encoded images
        base64_images = self.pdf_service.convert_pdf_to_images(pdf_path)
        
        # Extract TOC using OpenAI
        toc_content = self.openai_service.extract_toc_from_images(base64_images)
        
        # Save TOC to file if requested
        if output_file:
            saved_path = self.pdf_service.save_toc_to_file(toc_content, output_file)
        else:
            saved_path = self.pdf_service.save_toc_to_file(toc_content)
        
        return toc_content, saved_path
