import logging

from fastapi import FastAPI

from src.infrastructure.persistence.database import (
    create_engine,
    create_session_factory,
)
from src.presentation.api.dependencies import setup
from src.presentation.api.routes.internal import router as internal_router
from src.presentation.api.routes.public import router as public_router
from src.presentation.middleware import TraceIdMiddleware
from src.settings import Settings
from src.tracing import TraceIdFilter


def _configure_logging() -> None:
    root = logging.getLogger()
    if any(isinstance(f, TraceIdFilter) for h in root.handlers for f in h.filters):
        return
    handler = logging.StreamHandler()
    handler.addFilter(TraceIdFilter())
    fmt = "%(asctime)s %(levelname)s [%(trace_id)s] %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def create_app() -> FastAPI:
    _configure_logging()
    settings = Settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    app = FastAPI(title="Auth Service")
    app.add_middleware(TraceIdMiddleware)
    setup(settings, session_factory)
    app.include_router(public_router)
    app.include_router(internal_router)
    return app
