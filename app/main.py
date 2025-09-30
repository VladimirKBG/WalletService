import logging

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import g

from config import settings
from app.api.v1.routes import router


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
        log.info("Shutting down application '%s'...", title)
        engine = await get_async_engine()
        await engine.dispose()
        log.info("Engine disposed.")

    @app.get("/", tags=["health"])
    async def root() -> dict[str, str]:
        return {"status": "ok", "app": title}

    return app



