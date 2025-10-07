from dataclasses import dataclass


@dataclass(frozen=True)
class DomainRating:
    points: int
