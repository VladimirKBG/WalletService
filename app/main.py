import logging

from fastapi import FastAPI

from app.config import settings
from app.api.v1.routes import router
from app.db.base import DBConnectionManager


log = logging.getLogger("uvicorn.error")


def create_app() -> FastAPI:
    title = settings.APP_NAME
    version = settings.APP_VERSION
    enable_docs = settings.ENABLE_OPENAPI_DOCS

    app = FastAPI(title=title, version=version, docs_url="/docs" if enable_docs else None)
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup() -> None:
        log.info("Starting application.")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        log.info("Shutting down application.")
        await DBConnectionManager.dispose_engine()
        log.info("Engine disposed.")

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"status": "ok", "app": title}

    return app


app = create_app()

