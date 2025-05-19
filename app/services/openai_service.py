import json
from openai import OpenAI
from app.utils.decorators import timing_decorator
from app.core.config import settings


class OpenAIService:
    """Service for OpenAI API operations."""

    def __init__(self):
        """Initialize OpenAI client."""
        self._client = None

    @property
    def client(self):
        """Lazy-loaded OpenAI client."""
        if self._client is None:
            self._client = self._setup_client()
        return self._client

    def _setup_client(self):
        """Set up the OpenAI client."""
        api_key = settings.OPENAI_API_KEY

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set in environment variables or .env file"
            )

        return OpenAI(api_key=api_key)

    @timing_decorator
    def extract_toc_from_images(self, base64_images):
        """
        Extract Table of Contents from PDF images using OpenAI's Vision API.
        Processes all pages at once in a single API call.

        Args:
            base64_images: List of base64-encoded images

        Returns:
            dict: Extracted table of contents as a structured JSON object
        """
        if not base64_images:
            empty_response = {
                "toc_entries": [],
                "section_headers": [],
                "raw_content": "No content to process",
            }
            return json.dumps(empty_response)

        print(f"Processing {len(base64_images)} pages in a single batch...")

        # Prepare content for the multi-page request
        content = [
            {
                "type": "text",
                "text": f"Extract the complete Table of Contents information from these {len(base64_images)} PDF pages. "
                "The pages are provided in order. "
                "Format your response as a valid JSON with the following structure:\n\n"
                "```json\n"
                "{\n"
                '  "toc_entries": [\n'
                "    {\n"
                '      "case_number": "string",\n'
                '      "case_id": "string",\n'
                '      "plaintiff": "string",\n'
                '      "defendant": "string",\n'
                '      "page_number": "string",\n'
                '      "raw_text": "Full original text as it appears in the document"\n'
                "    }\n"
                "  ],\n"
                '  "section_headers": ["Juzgado de lo Social Número X de Santa Cruz de Tenerife", "Other sections"]\n'
                "}\n"
                "```\n\n"
                "Requirements:\n"
                "1. Extract ONLY what is actually visible in the images\n"
                "2. Maintain exact case numbers, party names, and page numbers\n"
                "3. Format ALL your output as a single, parseable JSON object\n"
                "4. Combine information from all pages into one comprehensive TOC\n"
                "5. If there is no TOC information in any of the pages, return empty arrays",
            }
        ]

        # Add all images to the content array
        for i, base64_image in enumerate(base64_images):
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "high",
                    },
                }
            )

        # Send request to OpenAI with all pages
        print(f"Sending all {len(base64_images)} pages to OpenAI in one request...")
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized JSON data extractor tasked with parsing legal document "
                        "Tables of Contents into structured data. Your output MUST be a valid, parseable JSON object "
                        "following exactly the schema requested. Extract EXACTLY what is visible in the images without "
                        "fabrication or inference. Combine information from all provided pages into a complete TOC.",
                    },
                    {"role": "user", "content": content},
                ],
                response_format={"type": "json_object"},
                max_tokens=20000,
            )

            # Just return the raw response without any parsing
            raw_response = response.choices[0].message.content
            print("Returning raw OpenAI response")
            return raw_response

        except Exception as e:
            print(f"Error processing pages: {str(e)}")
            # Return a JSON string for error cases to keep the API response consistent
            error_response = {
                "toc_entries": [],
                "section_headers": [],
                "error": True,
                "error_message": str(e),
            }
            return json.dumps(error_response)
