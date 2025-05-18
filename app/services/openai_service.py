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
            raise ValueError("OPENAI_API_KEY is not set in environment variables or .env file")
        
        return OpenAI(api_key=api_key)
    
    @timing_decorator
    def extract_toc_from_images(self, base64_images):
        """
        Extract Table of Contents from PDF images using OpenAI's Vision API.
        
        Args:
            base64_images: List of base64-encoded images
            
        Returns:
            str: Extracted table of contents
        """
        # Create content array for the API request 
        content = [
            {
                "type": "text",
                "text": "Extract the Table of Contents from this PDF document. The TOC follows this specific format:\n\n"
                        "[Case Number] Juicio nº [Case ID] a instancia de [Plaintiff] contra [Defendant] "
                        ".................. Página [Page Number]\n\n"
                        "Requirements:\n"
                        "1. Extract ONLY what is actually visible in the image\n"
                        "2. Maintain exact case numbers, party names, and page numbers\n"
                        "3. Preserve section headers like 'Juzgado de lo Social Número X de Santa Cruz de Tenerife'\n"
                        "4. Keep dotted leader lines (..........) connecting entries to page numbers\n\n"
                        "Format using monospace to preserve the original layout. Include ONLY real content from the images."
            }
        ]
        
        # Add each page image to the request
        for i, base64_image in enumerate(base64_images):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                    "detail": "high"
                }
            })
        
        # Send request to OpenAI
        print("Sending PDF pages to OpenAI for TOC extraction...")
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized legal document analyzer tasked with extracting ONLY the actual "
                               "Table of Contents from legal and judicial documents. Extract EXACTLY what is visible "
                               "in the images without fabrication or inference. If you see a Table of Contents with "
                               "case numbers, lawsuit details, and page numbers, extract it PRECISELY as it appears."
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=20000
        )
        
        # Extract TOC from response
        toc = response.choices[0].message.content
        return toc
