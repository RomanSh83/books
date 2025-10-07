from pydantic import BaseModel


class RatingReturnSchema(BaseModel):
    rating: float
