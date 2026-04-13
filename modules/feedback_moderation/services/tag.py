from app.core.base import BaseService
from slugify import slugify

class TagService(BaseService):
    from ..models.tag import Tag

    def create(self, values: dict):
        """Genera automáticamente el slug si no se proporciona."""
        if values.get("name") and not values.get("slug"):
            values["slug"] = slugify(values["name"])
        return super().create(values)

    def list_all(self):
        """Retorna todos los tags."""
        return super().search({})

    def delete(self, tag_id):
        """Elimina un tag por su ID."""
        return super().delete(tag_id)