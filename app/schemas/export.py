from pydantic import BaseModel, Field
from typing import Optional

class ExportOptions(BaseModel):
    format: str = Field("csv", description="The export file format: pdf, csv, excel, or json")
    compress: bool = Field(False, description="Whether to zip compression the exported report")

class ExportResponse(BaseModel):
    id: str = Field(..., description="The unique export transaction ID")
    download_url: str = Field(..., description="The URL link to download the exported file")
    format: str = Field(..., description="Export format (pdf, csv, excel, or json)")
    size_bytes: int = Field(..., description="Size of the exported report in bytes")
    status: str = Field("COMPLETED", description="Status of the export (COMPLETED, PROCESSING, FAILED)")
