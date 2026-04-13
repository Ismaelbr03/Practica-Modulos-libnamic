# services/tag_api.py
from fastapi import APIRouter, HTTPException
from .tag import TagService
from ..models.tag import Tag  # importar el modelo para pasar al repo

router = APIRouter(prefix="/feedback_moderation", tags=["Feedback Moderation"])

# Crear el servicio con el repo (modelo Tag)
tag_service = TagService(repo=Tag)

@router.post("/tag/create")
def create_tag(payload: dict):
    try:
        tag = tag_service.create(payload)
        return {"status": "ok", "tag": tag}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tag/list")
def list_tags():
    try:
        tags = tag_service.list_all()
        return {"status": "ok", "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tag/{tag_id}")
def delete_tag(tag_id: int):
    try:
        tag_service.delete(tag_id)
        return {"status": "ok", "message": f"Tag {tag_id} eliminado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))