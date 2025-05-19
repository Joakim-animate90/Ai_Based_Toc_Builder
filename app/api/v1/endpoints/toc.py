from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Form,
)
from typing import Optional
from app.models.schemas import (
    TOCRequest,
    TOCResponse,
    HealthResponse,
    TOCUrlRequest,
    TOCBrowserRequest,
)
from app.services.toc_service import TOCService
import json

router = APIRouter()


def get_toc_service():
    """Dependency to get TOC service instance."""
    return TOCService()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """Health check endpoint."""
    return HealthResponse()


@router.post("/extract", response_model=TOCResponse, tags=["toc"])
async def extract_toc(
    file: UploadFile = File(...),
    request: TOCRequest = Depends(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    toc_service: TOCService = Depends(get_toc_service),
):
    """
    Extract table of contents from an uploaded PDF document.

    - **file**: Uploaded PDF file
    - **output_file**: Optional path to save the extracted TOC
    - **max_pages**: Maximum number of pages to process (default: 10)
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


@router.post("/extract-from-url", response_model=TOCResponse, tags=["toc"])
async def extract_toc_from_url(
    request: TOCUrlRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    toc_service: TOCService = Depends(get_toc_service),
):
    """
    Extract table of contents from a PDF accessed via URL.

    - **pdf_url**: URL of the PDF document to process
    - **output_file**: Optional path to save the extracted TOC
    - **max_pages**: Maximum number of pages to process (default: 5)
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


@router.post("/extract-from-browser", response_model=TOCResponse, tags=["toc"])
async def extract_toc_from_browser(
    file: UploadFile = File(...),
    filename: str = Form(...),
    output_file: Optional[str] = Form(None),
    max_pages: Optional[int] = Form(5),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    toc_service: TOCService = Depends(get_toc_service),
):
    """
    Extract table of contents from a PDF uploaded directly from a browser.
    Optimized for web browser uploads with form-data.

    - **file**: Uploaded PDF file
    - **filename**: Original filename of the PDF
    - **output_file**: Optional path to save the extracted TOC
    - **max_pages**: Maximum number of pages to process (default: 5)
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
