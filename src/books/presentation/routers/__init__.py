from fastapi import APIRouter

from books.presentation.routers.auth_router import auth_router
from books.presentation.routers.authors_router import authors_router
from books.presentation.routers.books_router import books_router

main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(authors_router)
main_router.include_router(books_router)