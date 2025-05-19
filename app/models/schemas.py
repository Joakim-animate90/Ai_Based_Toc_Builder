from pydantic import BaseModel, Field, field_validator, ConfigDict, AnyHttpUrl
from typing import Optional, Union, Dict, List, Any


class TOCRequest(BaseModel):
    """Request model for TOC extraction."""

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
        json_schema_extra={"example": {"output_file": None, "max_pages": 10}}
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
    """Response model for TOC extraction."""

    success: bool = Field(..., description="Whether the extraction was successful")
    toc_content: Union[str, Dict[str, Any]] = Field(
        ...,
        description="Extracted table of contents (either as string or structured JSON)",
    )
    output_file: Optional[str] = Field(
        None,
        description="No longer used - always None as the service no longer saves files",
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
                "output_file": None,
            }
        }
    )


class TOCUrlRequest(BaseModel):
    """Request model for TOC extraction from URL."""

    pdf_url: AnyHttpUrl = Field(..., description="URL of the PDF to process")
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
                "pdf_url": "https://example.com/sample.pdf",
                "output_file": None,
                "max_pages": 10,
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
                "output_file": None,
                "max_pages": 10,
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = "ok"
    api_version: str = "1.0"
