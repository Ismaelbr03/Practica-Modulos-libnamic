import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService
from app.core.services import exposed_action
from app.core.serializer import serialize     


class CommentService(BaseService):
    # Import del modelo para poder acceder a él desde el servicio
    from ..models.comment import Comment

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def publish_comment(self, id: int, note: str | None = None) -> dict:
        """
        Acción de moderación: publicar comentario.

        Esta acción cambia el estado del comentario a 'published',
        lo marca como público y registra la fecha de publicación.
        Solo puede ser ejecutada por usuarios con rol moderador o superadmin.
        """
        # Buscar el comentario en base de datos
        record = self.repo.session.get(self.Comment, int(id))
        if not record:
            raise HTTPException(404, "Comentario no encontrado")
        
        # Actualización de campos al publicar
        record.status = "published"
        record.is_public = True
        record.published_at = dt.datetime.now(dt.timezone.utc)
        
        # El parámetro 'note' se mantiene aunque el modelo no tenga
        # moderation_note en comentarios, ya que el frontend genera
        # automáticamente un formulario cuando detecta este parámetro.
        
        # Guardar cambios en base de datos
        self.repo.session.add(record)
        self.repo.session.commit()
        self.repo.session.refresh(record)

        # Devolver el registro serializado para la API
        return serialize(record)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reject_comment(self, id: int, note: str) -> dict:
        """
        Acción de moderación: rechazar comentario.

        Cambia el estado a 'rejected' y lo marca como no público,
        evitando que aparezca en la parte pública del sistema.
        """
        # Obtener comentario
        record = self.repo.session.get(self.Comment, int(id))
        if not record:
            raise HTTPException(404, "Comentario no encontrado")
        
        # Actualizar estado a rechazado
        record.status = "rejected"
        record.is_public = False
        
        # Guardar cambios
        self.repo.session.add(record)
        self.repo.session.commit()
        self.repo.session.refresh(record)

        # Retornar comentario actualizado
        return serialize(record)