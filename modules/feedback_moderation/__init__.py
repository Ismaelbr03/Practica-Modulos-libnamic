from . import models
from . import services

from .services.tag_api import router as tag_router

def setup_module(app):
    """Licium llama a esta función para cargar routers del módulo"""
    app.include_router(tag_router)