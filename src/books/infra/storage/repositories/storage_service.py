import base64
import uuid

import aiofiles  # type: ignore
import aiofiles.os  # type: ignore
import aiofiles.ospath  # type: ignore

from books.application.config import get_settings
from books.domain.entities.file_entities import DomainFile
from books.domain.exceptions.core_exceptions import Base64DecodeError
from books.domain.protocols.auth.storage_protocols import StorageServiceProtocol


class StorageService(StorageServiceProtocol):
    def __init__(self):
        self._media_root = get_settings().MEDIA_ROOT
        self._media_url = get_settings().MEDIA_URL

    @staticmethod
    def get_file_from_base64_uri(data: str) -> DomainFile:
        header, base64_data = data.split(sep=";base64,", maxsplit=1)

        try:
            decoded_data = base64.b64decode(base64_data, validate=True)
        except Base64DecodeError:
            raise Base64DecodeError

        return DomainFile(filename=f"{str(uuid.uuid4())}.{header.split('/')[-1]}", data=decoded_data)

    @staticmethod
    def get_filename_from_url(url: str) -> str:
        return url.split("/")[-1]

    async def save_file(self, file: DomainFile) -> str:
        async with aiofiles.open(f"{self._media_root}/{file.filename}", mode="wb") as output_file:
            await output_file.write(file.data)
        file_url = f"{self._media_url}/{file.filename}"
        return file_url

    async def remove_file(self, filename: str) -> None:
        if await aiofiles.ospath.exists(self._media_root / filename):
            await aiofiles.os.remove(self._media_root / filename)
