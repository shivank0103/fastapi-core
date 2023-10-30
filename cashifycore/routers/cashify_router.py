from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.config import settings

core_router = APIRouter(
    tags=["core"]
)


@core_router.get('/health')
def health(request: Request):
    return JSONResponse({
        'status': 'up',
        'service': settings.app_name,
        'version': settings.app_version
    })


@core_router.get('/v1/health')
def health(request: Request):
    return JSONResponse({
        'status': 'up',
        'service': settings.app_name,
        'version': settings.app_version
    })
