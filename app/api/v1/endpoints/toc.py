from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, UploadFile, File
from typing import Optional
from app.models.schemas import TOCRequest, TOCResponse, HealthResponse
from app.services.toc_service import TOCService

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
