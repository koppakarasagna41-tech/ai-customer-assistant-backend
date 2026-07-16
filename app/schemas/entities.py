from pydantic import BaseModel, Field
from typing import List

class Entity(BaseModel):
    name: str = Field(..., description="The value of the extracted entity")
    type: str = Field(..., description="The category of the entity, e.g., PRODUCT, SYSTEM, CODE, PERSON, DATE, EMAIL")
    confidence: float = Field(..., description="Confidence score for this extraction")

class ExtractedEntities(BaseModel):
    entities: List[Entity] = Field(default_factory=list, description="List of extracted entities")
