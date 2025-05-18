from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.models.schemas import TOCRequest, TOCResponse, HealthResponse
from app.services.toc_service import TOCService
import os

router = APIRouter()

def get_toc_service():
    """Dependency to get TOC service instance."""
    return TOCService()

@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """Health check endpoint."""
    return HealthResponse()

@router.post("/extract", response_model=TOCResponse, tags=["toc"])
def extract_toc(
    request: TOCRequest,
    background_tasks: BackgroundTasks,
    toc_service: TOCService = Depends(get_toc_service)
):
    """
    Extract table of contents from a PDF document.
    
    - **pdf_path**: Path to the PDF file
    - **output_file**: Optional path to save the extracted TOC
    - **max_pages**: Maximum number of pages to process (default: 20)
    """
    # Validate PDF path
    if not os.path.exists(request.pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF file not found at {request.pdf_path}")
    
    try:
        # Extract TOC
        toc_content, output_file = toc_service.extract_toc(
            request.pdf_path, 
            request.output_file
        )
        
        return TOCResponse(
            success=True,
            toc_content=toc_content,
            output_file=output_file
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
