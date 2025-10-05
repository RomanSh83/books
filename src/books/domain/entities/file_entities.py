from dataclasses import dataclass


@dataclass(frozen=True)
class DomainFile:
    filename: str
    data: bytes
