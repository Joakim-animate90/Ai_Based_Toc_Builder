from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class TOCRequest(BaseModel):
    """Request model for TOC extraction."""
    output_file: Optional[str] = Field(None, description="Path to save the extracted TOC")
    max_pages: Optional[int] = Field(10, description="Maximum number of pages to process")
    
    @field_validator('max_pages')
    @classmethod
    def validate_max_pages(cls, v):
        if v is not None and v <= 0:
            raise ValueError('max_pages must be greater than 0')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "output_file": "toc/my_table_of_contents.txt",
                "max_pages": 10
            }
        }
    )

class TOCResponse(BaseModel):
    """Response model for TOC extraction."""
    success: bool = Field(..., description="Whether the extraction was successful")
    toc_content: str = Field(..., description="Extracted table of contents")
    output_file: str = Field(..., description="Path to the saved TOC file")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "toc_content": "Juicio nº 123 a instancia de Plaintiff contra Defendant .................. Página 45",
                "output_file": "toc/table_of_contents.txt"
            }
        }
    )

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "ok"
    api_version: str = "1.0"
