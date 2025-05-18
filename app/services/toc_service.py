import os
import tempfile
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
    def extract_toc(self, pdf_path, output_file=None, max_pages=None):
        """
        Extract Table of Contents from a PDF file using OpenAI's Vision API.
        
        Args:
            pdf_path: Path to the PDF file
            output_file: Optional output file path
            max_pages: Maximum number of pages to process
            
        Returns:
            tuple: (toc_content, output_file_path)
        """
        # Convert PDF pages to base64-encoded images
        base64_images = self.pdf_service.convert_pdf_to_images(pdf_path, max_pages=max_pages)
        
        # Extract TOC using OpenAI
        toc_content = self.openai_service.extract_toc_from_images(base64_images)
        
        # Save TOC to file if requested
        if output_file:
            saved_path = self.pdf_service.save_toc_to_file(toc_content, output_file)
        else:
            saved_path = self.pdf_service.save_toc_to_file(toc_content)
        
        return toc_content, saved_path
        
    @timing_decorator
    def extract_toc_from_upload(self, pdf_content, filename, output_file=None, max_pages=None):
        """
        Extract Table of Contents from uploaded PDF content using OpenAI's Vision API.
        
        Args:
            pdf_content: Binary content of the uploaded PDF file
            filename: Original filename of the uploaded PDF
            output_file: Optional output file path
            max_pages: Maximum number of pages to process
            
        Returns:
            tuple: (toc_content, output_file_path)
        """
        # Create a temporary file to store the uploaded PDF content
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(pdf_content)
        
        try:
            # Process the PDF file
            base64_images = self.pdf_service.convert_pdf_to_images(temp_path, max_pages=max_pages)
            
            # Extract TOC using OpenAI
            toc_content = self.openai_service.extract_toc_from_images(base64_images)
            
            # Generate output filename based on the original filename if not provided
            if not output_file:
                base_name = os.path.splitext(os.path.basename(filename))[0]
                output_file = f"toc_{base_name}.txt"
            
            # Save TOC to file
            saved_path = self.pdf_service.save_toc_to_file(toc_content, output_file)
            
            return toc_content, saved_path
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
