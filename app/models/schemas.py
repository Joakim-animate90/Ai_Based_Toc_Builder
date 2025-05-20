from pydantic import BaseModel, Field, field_validator, ConfigDict, AnyHttpUrl
from typing import Optional, Union, Dict, List, Any


class TOCRequest(BaseModel):
    """Request model for TOC extraction using file upload."""

    output_file: Optional[str] = Field(
        None,
        description="Optional path to save the extracted TOC (e.g., 'toc/output.json')",
    )
    max_pages: Optional[int] = Field(
        5, description="Maximum number of pages to process (1-20 recommended)"
    )

    @field_validator("max_pages")
    @classmethod
    def validate_max_pages(cls, v):
        if v is not None and v <= 0:
            raise ValueError("max_pages must be greater than 0")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"output_file": "toc/my_document_toc.json", "max_pages": 10}
        }
    )


class TOCEntry(BaseModel):
    """Model for a single TOC entry."""

    case_number: Optional[str] = Field(None, description="Case number")
    case_id: Optional[str] = Field(None, description="Case ID")
    plaintiff: Optional[str] = Field(None, description="Plaintiff name")
    defendant: Optional[str] = Field(None, description="Defendant name")
    page_number: Optional[str] = Field(None, description="Page number")
    raw_text: str = Field(
        ..., description="Full original text as it appears in the document"
    )


class TOCResponse(BaseModel):
    """Response model for table of contents extraction.

    This model is used by all TOC extraction endpoints to return the structured
    results of the AI analysis.
    """

    success: bool = Field(..., description="Whether the extraction was successful")
    toc_content: Union[str, Dict[str, Any], List[Dict[str, Any]]] = Field(
        ...,
        description="Extracted table of contents in structured format. May contain hierarchical structure, section headers, and detailed entries.",
    )
    output_file: Optional[str] = Field(
        None,
        description="Path where the TOC was saved, if output_file was specified in the request. If None, the TOC was not saved to disk.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "toc_content": {
                    "toc_entries": [
                        {
                            "case_number": "123/456",
                            "case_id": "123",
                            "plaintiff": "John Doe",
                            "defendant": "Company XYZ",
                            "page_number": "45",
                            "raw_text": "Juicio nº 123 a instancia de John Doe contra Company XYZ .................. Página 45",
                        }
                    ],
                    "section_headers": [
                        "Juzgado de lo Social Número 3 de Santa Cruz de Tenerife"
                    ],
                    "raw_content": "Juicio nº 123 a instancia de John Doe contra Company XYZ .................. Página 45",
                },
                "output_file": "toc/legal_document.json",
            }
        }
    )


class TOCUrlRequest(BaseModel):
    """Request model for TOC extraction from a PDF URL.

    This model is used by the extract-from-url endpoint to process PDFs from remote URLs.
    """

    pdf_url: AnyHttpUrl = Field(
        ...,
        description="URL of the PDF to process - must be publicly accessible and point directly to a PDF file",
    )
    output_file: Optional[str] = Field(
        None,
        description="Optional path to save the extracted TOC (e.g., 'toc/result.json')",
    )
    max_pages: Optional[int] = Field(
        5, description="Maximum number of pages to process (1-20 recommended)"
    )

    @field_validator("max_pages")
    @classmethod
    def validate_max_pages(cls, v):
        if v is not None and v <= 0:
            raise ValueError("max_pages must be greater than 0")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pdf_url": "https://arxiv.org/pdf/2303.08774.pdf",
                "output_file": "toc/research_paper.json",
                "max_pages": 5,
            }
        }
    )


class TOCBrowserRequest(BaseModel):
    """Request model for TOC extraction from browser uploads."""

    filename: str = Field(..., description="Original filename of the uploaded PDF")
    output_file: Optional[str] = Field(
        None, description="Path to save the extracted TOC"
    )
    max_pages: Optional[int] = Field(
        5, description="Maximum number of pages to process"
    )

    @field_validator("max_pages")
    @classmethod
    def validate_max_pages(cls, v):
        if v is not None and v <= 0:
            raise ValueError("max_pages must be greater than 0")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.pdf",
                "output_file": "toc/browser_upload.json",
                "max_pages": 10,
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response model.

    This model is returned by the health check endpoint to verify API availability.
    """

    status: str = Field(
        "ok",
        description="Status of the API - 'ok' indicates the service is healthy and running",
    )
    api_version: str = Field("1.0", description="Current version of the API")

    model_config = ConfigDict(
        json_schema_extra={"example": {"status": "ok", "api_version": "1.0"}}
    )
