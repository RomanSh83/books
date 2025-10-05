from asyncio import Protocol

from books.domain.entities.file_entities import DomainFile


class StorageServiceProtocol(Protocol):
    @staticmethod
    def get_file_from_base64_uri(data: str) -> DomainFile:
        raise NotImplementedError

    @staticmethod
    def get_filename_from_url(url: str) -> str:
        raise NotImplementedError

    async def save_file(self, file: DomainFile) -> str:
        raise NotImplementedError

    async def remove_file(self, filename: str) -> None:
        raise NotImplementedError
