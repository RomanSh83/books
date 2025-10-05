import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from books.application.config import get_settings
from books.presentation.routers import main_router

from fastapi.responses import HTMLResponse
from pathlib import Path

def run_app():
    app = FastAPI()

    app.mount(get_settings().MEDIA_URL, StaticFiles(directory=get_settings().MEDIA_ROOT), name="media")
    app.include_router(main_router)

    uvicorn.run(app, host="0.0.0.0", port=8000, loop=get_settings().ASYNCIO_LOOP)
