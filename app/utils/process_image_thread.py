import base64
import os
import fitz  # type: ignore # PyMuPDF
from concurrent.futures import ThreadPoolExecutor
from app.utils.decorators import timing_decorator


class PDFToBase64Thread:
    """Thread-based class for converting PDF pages to base64-encoded images."""

    def __init__(self, num_threads=None):
        """Initialize with optional thread count."""
        # If thread_count is 0 or None, use CPU count - 1 with minimum of 1
        if num_threads is None:
            self.num_threads = max(1, os.cpu_count() - 1)
        else:
            # Ensure at least 1 thread
            self.num_threads = max(1, num_threads)

    def _process_page(self, pdf_document, page_num, pages_to_process):
        """Process a single PDF page to a base64-encoded image."""
        try:
            page = pdf_document.load_page(page_num)

            # Render page to image at higher resolution for better OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            # Convert pixmap to bytes (PNG format)
            img_bytes = pix.tobytes("png")

            # Convert bytes to base64
            base64_image = base64.b64encode(img_bytes).decode("utf-8")

            print(f"Processed page {page_num + 1}/{pages_to_process}")
            return page_num, base64_image
        except Exception as e:
            print(f"Error processing page {page_num}: {str(e)}")
            return page_num, None

    @timing_decorator
    def convert_pdf_to_base64_images(self, pdf_path, max_pages=20):
        """Convert first several pages of a PDF to base64-encoded images using threads.
        Limits to max_pages to focus on likely TOC pages and avoid memory issues.
        """
        pdf_document = fitz.open(pdf_path)
        results = [None] * min(max_pages, pdf_document.page_count)
        pages_to_process = len(results)

        print(
            f"Converting {pages_to_process} pages to images using {self.num_threads} threads..."
        )

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Submit all tasks to the executor
            future_to_page = {
                executor.submit(
                    self._process_page, pdf_document, page_num, pages_to_process
                ): page_num
                for page_num in range(pages_to_process)
            }

            # Process results as they complete
            for future in future_to_page:
                try:
                    page_num, base64_image = future.result()
                    if base64_image:
                        results[page_num] = base64_image
                except Exception as e:
                    print(f"Exception occurred: {str(e)}")

        # Filter out any None values in case of errors
        results = [img for img in results if img is not None]

        pdf_document.close()
        return results


# Example usage:
# thread_converter = PDFToBase64Thread(num_threads=4)  # Optionally specify thread count
# base64_images = thread_converter.convert_pdf_to_base64_images("path/to/your/pdf.pdf", max_pages=20)
