from fastapi import HTTPException, Request, status
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class CashifyApiException(HTTPException):
    def __init__(self, error: tuple, diagno_code: tuple):
        self.error_code = error[0]
        self.message = error[1]
        self.diagno_code = diagno_code[0]
        self.status_code = status.HTTP_409_CONFLICT


async def cashify_exception_handler(request: Request, exc: CashifyApiException) -> JSONResponse:
    from app.config.logger import CashifyLogger
    CashifyLogger.error('Exception for request ID ' + request.scope['r_id'])
    headers = getattr(exc, "headers", None)
    if headers:
        return JSONResponse(
            {"message": exc.message, "code": exc.error_code, "dc": exc.diagno_code},
            status_code=exc.status_code, headers=headers
        )
    else:
        return JSONResponse(
            {"message": exc.message, "code": exc.error_code, "dc": exc.diagno_code},
            status_code=exc.status_code
        )


async def cashify_pydantic_exception_handler(request: Request, exc: RequestValidationError):
    from app.config.logger import CashifyLogger
    CashifyLogger.error('Exception for request ID ' + request.scope['r_id'])
    error = exc.errors()[0]
    return JSONResponse(
        {"message": error['msg'] + ' ' + str(error['loc'][1])},
        status_code=status.HTTP_409_CONFLICT
    )
