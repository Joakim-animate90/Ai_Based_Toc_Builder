from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Form,
    Body,
)
from typing import Optional
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.models.schemas import (
    TOCRequest,
    TOCResponse,
    HealthResponse,
    TOCUrlRequest,
    TOCBrowserRequest,
)
from app.services.toc_service import TOCService
import json

router = APIRouter(
    prefix="",
    tags=["toc"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


def get_toc_service():
    """Dependency to get TOC service instance.

    Returns:
        TOCService: Instance of the TOC service for handling PDF processing
    """
    return TOCService()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="API Health Check",
    description="Check if the API is operational and responsive.",
)
def health_check():
    """Health check endpoint that returns API status information.

    Returns:
        HealthResponse: Object containing status='ok' if the API is healthy
    """
    return HealthResponse()


@router.post(
    "/extract",
    response_model=TOCResponse,
    tags=["toc"],
    summary="Extract TOC from Uploaded PDF",
    description="Upload a PDF file and extract its table of contents using AI analysis.",
)
async def extract_toc(
    file: UploadFile = File(..., description="PDF file to upload and analyze"),
    request: TOCRequest = Depends(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    toc_service: TOCService = Depends(get_toc_service),
):
    """
    Extract table of contents from an uploaded PDF document using thread-optimized processing.

    The endpoint uses AI to analyze PDF content and identify the table of contents structure.
    Performance is optimized using thread-based parallel processing of PDF pages.

    Parameters:
        - **file**: Uploaded PDF file (must be a valid PDF document)
        - **output_file**: Optional path to save the extracted TOC (file saving is optional)
        - **max_pages**: Maximum number of pages to process (default: 10)

    Returns:
        A TOCResponse object containing:
        - success: Boolean indicating if extraction was successful
        - toc_content: Extracted table of contents data (structured as JSON)
        - output_file: Path where the TOC was saved (if output_file was specified)

    Raises:
        400: If the uploaded file is not a valid PDF
        500: For server-side processing errors (including OpenAI API issues)
    """
    # Validate PDF file upload
    if not file or not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file: Please upload a PDF document"
        )

    try:
        # Extract TOC from uploaded file
        pdf_content = await file.read()

        # Process the uploaded PDF content
        toc_content, output_file = toc_service.extract_toc_from_upload(
            pdf_content, file.filename, request.output_file, request.max_pages
        )

        return TOCResponse(
            success=True, toc_content=toc_content, output_file=output_file
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/extract-from-url",
    response_model=TOCResponse,
    tags=["toc"],
    summary="Extract TOC from PDF URL",
    description="Provide a URL to a PDF file and extract its table of contents.",
)
async def extract_toc_from_url(
    request: TOCUrlRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    toc_service: TOCService = Depends(get_toc_service),
):
    """
    Extract table of contents from a PDF accessed via URL.

    This endpoint downloads the PDF from the provided URL and processes it using
    the same AI analysis engine used for direct uploads.

    Parameters:
        - **pdf_url**: URL of the PDF document to process (must be publicly accessible)
        - **output_file**: Optional path to save the extracted TOC
        - **max_pages**: Maximum number of pages to process (default: 5)

    Returns:
        A TOCResponse object containing:
        - success: Boolean indicating if extraction was successful
        - toc_content: Extracted table of contents data (structured as JSON)
        - output_file: Path where the TOC was saved (if output_file was specified)

    Raises:
        422: If the URL is invalid or improperly formatted
        500: For server-side processing errors (including download failures)
    """

    try:
        # Extract TOC from the URL
        toc_content, output_file = toc_service.extract_toc_from_url(
            pdf_url=str(request.pdf_url),
            output_file=request.output_file,
            max_pages=request.max_pages,
        )

        return TOCResponse(
            success=True, toc_content=toc_content, output_file=output_file
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/extract-from-browser",
    response_model=TOCResponse,
    tags=["toc"],
    summary="Extract TOC from Browser Upload",
    description="Upload a PDF file directly from a browser form and extract its table of contents. Optimized for multipart/form-data uploads.",
)
async def extract_toc_from_browser(
    file: UploadFile = File(..., description="PDF file to analyze (binary data)"),
    filename: str = Form(
        ..., description="Original name of the PDF file (must end with .pdf)"
    ),
    output_file: Optional[str] = Form(
        None, description="Optional path to save the TOC result"
    ),
    max_pages: Optional[int] = Form(
        5, description="Maximum number of pages to process"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    toc_service: TOCService = Depends(get_toc_service),
):
    """
    Extract table of contents from a PDF uploaded directly from a browser.
    
    This endpoint is specifically designed for browser-based uploads using multipart/form-data.
    It accepts binary PDF data and handles the form submission format commonly used by web forms.
    The endpoint is ideal for integration with frontend applications and supports curl commands.
    
    Example curl command:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/toc/extract-from-browser" \
      -H "accept: application/json" \
      -F "file=@your_file.pdf" \
      -F "filename=your_file.pdf" \
      -F "max_pages=10"
    ```
    
    Parameters:
        - **file**: Binary PDF file data uploaded as multipart/form-data
        - **filename**: Original filename of the PDF (must end with .pdf)
        - **output_file**: Optional path to save the extracted TOC
        - **max_pages**: Maximum number of pages to process (default: 5)
        
    Returns:
        A TOCResponse object containing:
        - success: Boolean indicating if extraction was successful
        - toc_content: Extracted table of contents data (structured as JSON)
        - output_file: Path where the TOC was saved (if output_file was specified)
    
    Raises:
        400: If the uploaded file is not a valid PDF
        500: For server-side processing errors
    """
    # Validate PDF file upload
    if not file or not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file: Please upload a PDF document"
        )

    try:
        # Extract TOC from uploaded file
        pdf_content = await file.read()

        # Create browser request object
        request = TOCBrowserRequest(
            filename=filename, output_file=output_file, max_pages=max_pages
        )

        # Process the uploaded PDF content
        toc_content, output_file = toc_service.extract_toc_from_upload(
            pdf_content, filename, request.output_file, request.max_pages
        )

        # Simply return the content as-is without trying to parse it
        # Just ensure it's in a format acceptable for the TOCResponse model
        if not isinstance(toc_content, (str, dict, list)):
            # Convert to string if not already a string, dict or list
            toc_content = str(toc_content)

        return TOCResponse(
            success=True, toc_content=toc_content, output_file=output_file
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
