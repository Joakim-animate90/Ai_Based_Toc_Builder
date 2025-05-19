import os
import json
from app.utils.decorators import timing_decorator
from app.utils.process_image_thread import PDFToBase64Thread
from app.core.config import settings


class PDFService:
    """Service for PDF processing operations."""

    def __init__(self, thread_count=None):
        """Initialize PDF service with optional thread count."""
        self.thread_count = thread_count or settings.DEFAULT_THREAD_COUNT
        self.pdf_converter = PDFToBase64Thread(num_threads=self.thread_count)

    @timing_decorator
    def convert_pdf_to_images(self, pdf_path, max_pages=None):
        """
        Convert PDF pages to base64-encoded images using thread-based processing.
        """
        max_pages = max_pages or settings.PDF_MAX_PAGES
        return self.pdf_converter.convert_pdf_to_base64_images(pdf_path, max_pages)

    @timing_decorator
    def save_toc_to_file(self, toc_content, output_path=None):
        """
        Save extracted table of contents to a file.
        Handles both string content and dictionary (JSON) content.
        """
        if output_path is None:
            output_dir = settings.PDF_OUTPUT_DIR
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "table_of_contents.txt")
        else:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Handle both dictionary and string content
        if isinstance(toc_content, dict):
            # If it's a dictionary, get the raw_content if available
            if "raw_content" in toc_content:
                raw_text = toc_content["raw_content"]
                # Format TOC with monospace font for better display
                formatted_toc = "```\n" + raw_text + "\n```"

                # Also save the structured JSON data to a separate file
                json_path = os.path.splitext(output_path)[0] + ".json"
                with open(json_path, "w") as json_file:
                    json.dump(toc_content, json_file, indent=2)
                print(f"Structured JSON data saved to {json_path}")
            else:
                # If no raw_content, just save the JSON as text
                formatted_toc = json.dumps(toc_content, indent=2)
        else:
            # Original behavior for string content
            formatted_toc = "```\n" + str(toc_content) + "\n```"

        # Save to file
        with open(output_path, "w") as file:
            file.write(formatted_toc)

        print(f"Table of Contents saved to {output_path}")
        return output_path
