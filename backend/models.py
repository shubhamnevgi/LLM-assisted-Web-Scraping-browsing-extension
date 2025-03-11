from pydantic import BaseModel
from typing import List
from typing import Literal

class ScrapeRequest(BaseModel):
    urls: List[str]
    parse_description: str
    output_format: Literal["csv", "json", "excel", "xml"]  # Validate output format

class ScrapeResponse(BaseModel):
    status: str
    data: str  # Processed data in the requested format
    message: str