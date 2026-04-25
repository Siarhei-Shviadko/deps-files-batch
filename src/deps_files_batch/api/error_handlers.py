import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.requests import Request

from deps_files_batch.api.serializers.error import ErrorSerializer
from deps_files_batch.domain.exceptions import *

logger = logging.getLogger(__name__)


def json_files_batch_error_handler(error: BatchException, status_code: int):
    error_message = ErrorSerializer(code=error.code, message=str(error)).dict()
    return JSONResponse(status_code=status_code, content=error_message)


def register_error_handler(app: FastAPI) -> None:
    @app.exception_handler(BatchException)
    def handle_files_batch_exception(req: Request, error: BatchException):  # noqa: WPS430
        mapper = [
            (NotFoundError, HTTPStatus.NOT_FOUND),
            (BatchException, HTTPStatus.BAD_REQUEST),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_files_batch_error_handler(error, status_code)

    @app.exception_handler(ValidationError)
    def bad_request(req: Request, exc: ValidationError):  # noqa: WPS430
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorSerializer(code="bad_request", message=str(exc)).dict(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(req: Request, error: Exception):  # noqa: WPS430
        logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=ErrorSerializer(code="unhandled_error", message=str(error)).dict(),
        )
