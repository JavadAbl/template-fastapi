"""App factory — creates the FastAPI application instance.

Responsibilities:
  - Define the lifespan (startup / shutdown)
  - Register routers
  - Add global middleware
  - Include the root health-check
"""

from contextlib import asynccontextmanager
import logging
import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status

from app.contracts.config import get_settings
from app.contracts.database import close_db, init_db
from app.users.routers.user_router import router as users_router

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    yield
    # Shutdown logic
    await close_db()


# @app.on_event("startup")
# async def startup():
#     await init_db()

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    docs_url=f"{settings.api_v1_prefix}/docs",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"

)


# ─── Middleware ──────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routers ────────────────────────────────────────────────────

app.include_router(users_router, prefix=settings.api_v1_prefix)


# ─── Health check ──────────────────────────────────────────────

@app.get("/health", tags=["health"])
def health_check() -> str:
    return "ok"


# Handle Pydantic validation errors consistently
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = {"detail": exc.errors()}

    if settings.debug:
        response["traceback"] = traceback.format_exception(
            type(exc), exc, exc.__traceback__
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response = {"detail": exc.detail}

    if settings.debug:
        response["traceback"] = traceback.format_exception(
            type(exc), exc, exc.__traceback__)

    return JSONResponse(
        status_code=exc.status_code,
        content=response,
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", request.url, True)
    response = {"detail": str(exc)}

    if settings.debug:  # or settings.environment == "development"
        response["traceback"] = traceback.format_exception(
            type(exc), exc, exc.__traceback__)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response,
    )
