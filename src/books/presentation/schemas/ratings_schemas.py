from typing import Annotated

from pydantic import BaseModel, Field

class RatingInSchema(BaseModel):
    points: Annotated[int, Field(ge=1, le=5)]

class RatingReturnSchema(BaseModel):
    rating: float
