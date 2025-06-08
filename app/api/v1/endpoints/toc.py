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

from uuid import uuid4
from app.repository.open_ai_db import OpenAIDB
from app.services.pdf_tasks import process_pdf_task
from fastapi import status as http_status

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
    "/pdf-processing-jobs",
    tags=["toc"],
    summary="Asynchronous PDF Processing (returns ticket)",
    description="Submit a PDF for async processing. Returns a ticket immediately. Use /status/{ticket_id} to poll for status/result.",
)
async def async_process_pdf(
    file: UploadFile = File(
        ..., description="PDF file to upload and process asynchronously"
    ),
    max_pages: Optional[int] = Form(
        5, description="Maximum number of pages to process"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Accepts a PDF file, generates a ticket, stores the request as 'pending', and enqueues the Celery task.
    Returns the ticket id immediately.
    """
    if not file or not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file: Please upload a PDF document"
        )
    try:
        pdf_content = await file.read()
        ticket_id = str(uuid4())
        db = OpenAIDB()
        db.create(
            {
                "id": ticket_id,
                "status": "pending",
                "payload": {
                    "filename": file.filename,
                    "pdf_content": pdf_content.hex(),  # Store as hex string for binary safety
                    "max_pages": max_pages,
                },
                "result": None,
            }
        )
        # Enqueue background task
        background_tasks.add_task(process_pdf_task, ticket_id)
        return {"ticket_id": ticket_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/status/{ticket_id}",
    tags=["toc"],
    summary="Check status/result of async PDF processing",
    description="Poll for the status and result of an async PDF processing request using the ticket id.",
)
def get_async_status(ticket_id: str):
    """
    Returns the status and result for the given ticket id.
    """
    db = OpenAIDB()
    record = db.get(ticket_id)
    if not record:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {
        "ticket_id": record["id"],
        "status": record["status"],
        "result": record["result"],
    }


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

        # If toc_content is a string, try to parse it as JSON for proper structure
        if isinstance(toc_content, str):
            try:
                toc_content = json.loads(toc_content)
            except Exception:
                pass  # If parsing fails, leave as string

        return TOCResponse(
            success=True, toc_content=toc_content, output_file=output_file
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
