import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.catalog.routes import router as catalog_router
from app.core.config import get_settings
from app.core.errors import ApiError
from app.core.i18n import language_from_request, message
from app.orders.routes import router as orders_router

logger = logging.getLogger("herbstore")


class BodySizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        maximum = get_settings().max_body_bytes
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > maximum:
            language = language_from_request(request)
            return JSONResponse(
                {
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": message("PAYLOAD_TOO_LARGE", language),
                    }
                },
                status_code=413,
                headers={"Content-Language": language},
            )
        if content_length is None and request.method in {"POST", "PUT", "PATCH"}:
            body = await request.body()
            if len(body) > maximum:
                language = language_from_request(request)
                return JSONResponse(
                    {
                        "error": {
                            "code": "PAYLOAD_TOO_LARGE",
                            "message": message("PAYLOAD_TOO_LARGE", language),
                        }
                    },
                    status_code=413,
                    headers={"Content-Language": language},
                )
        return await call_next(request)


def create_app() -> FastAPI:
    app = FastAPI(
        title="HerbStore API",
        description=(
            "Persistent API for the HerbStore mobile app. / "
            "API persistente para la aplicación móvil HerbStore."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(BodySizeMiddleware)
    app.include_router(catalog_router)
    app.include_router(orders_router)

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
        language = language_from_request(request)
        body = {
            **(error.extra or {}),
            "error": {"code": error.code, "message": message(error.code, language)},
        }
        if error.fields is not None:
            body["fields"] = error.fields
        return JSONResponse(
            body, status_code=error.status_code, headers={"Content-Language": language}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, _error: RequestValidationError
    ) -> JSONResponse:
        language = language_from_request(request)
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": message("VALIDATION_ERROR", language),
                }
            },
            status_code=400,
            headers={"Content-Language": language},
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, _error) -> JSONResponse:
        language = language_from_request(request)
        return JSONResponse(
            {"error": {"code": "NOT_FOUND", "message": message("NOT_FOUND", language)}},
            status_code=404,
            headers={"Content-Language": language},
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
        logger.exception("Unexpected API error", exc_info=error)
        language = language_from_request(request)
        return JSONResponse(
            {"error": {"code": "INTERNAL_ERROR", "message": message("INTERNAL_ERROR", language)}},
            status_code=500,
            headers={"Content-Language": language},
        )

    return app


app = create_app()
