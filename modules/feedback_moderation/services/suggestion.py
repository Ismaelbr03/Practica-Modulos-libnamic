import datetime as dt
from fastapi import HTTPException
from app.core.base import BaseService
from app.core.services import exposed_action
from app.core.serializer import serialize


class SuggestionService(BaseService):
    from ..models.suggestion import Suggestion
    from ..models.comment import Comment

    # -------------------------
    # Métodos internos auxiliares
    # -------------------------

    def _get_suggestion(self, id: int):
        """Obtiene una sugerencia o lanza 404 si no existe."""
        record = self.repo.session.get(self.Suggestion, int(id))
        if not record:
            raise HTTPException(404, "Sugerencia no encontrada")
        return record

    def _save(self, record):
        """Guarda cambios en base de datos y devuelve el registro serializado."""
        self.repo.session.add(record)
        self.repo.session.commit()
        self.repo.session.refresh(record)
        return serialize(record)

    # -------------------------
    # Acciones de moderación
    # -------------------------

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def publish(self, id: int, note: str | None = None, pin: bool = False) -> dict:
        """
        Publica una sugerencia.

        - Cambia estado a 'published'
        - La hace visible públicamente
        - Registra fecha de publicación
        - Guarda nota de moderación opcional
        """
        record = self._get_suggestion(id)

        if record.status == "published":
            raise HTTPException(400, "Esta sugerencia ya está publicada.")

        record.status = "published"
        record.is_public = True
        record.published_at = dt.datetime.now(dt.timezone.utc)

        if note:
            record.moderation_note = note

        # 'pin' se deja preparado por si existe campo is_pinned
        return self._save(record)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reject(self, id: int, note: str) -> dict:
        """
        Rechaza una sugerencia.

        - Cambia estado a 'rejected'
        - La oculta del público
        - Guarda nota obligatoria con el motivo
        """
        record = self._get_suggestion(id)

        record.status = "rejected"
        record.is_public = False
        record.moderation_note = note

        return self._save(record)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def merge(self, id: int, target_id: int, note: str | None = None) -> dict:
        """
        Fusiona una sugerencia con otra (duplicado).

        - Mueve los comentarios a la sugerencia destino
        - Cambia estado a 'merged'
        - La oculta del público
        - Guarda nota indicando la fusión
        """
        record = self._get_suggestion(id)
        target_record = self._get_suggestion(target_id)

        if id == target_id:
            raise HTTPException(400, "No puedes fusionar una sugerencia consigo misma")

        # Mover comentarios a la sugerencia destino
        comments = (
            self.repo.session.query(self.Comment)
            .filter(self.Comment.suggestion_id == id)
            .all()
        )
        for c in comments:
            c.suggestion_id = target_id

        record.status = "merged"
        record.is_public = False
        record.moderation_note = note if note else f"Fusionado con la sugerencia #{target_id}"

        return self._save(record)

    @exposed_action("write", groups=["feedback_group_moderator", "core_group_superadmin"])
    def reopen(self, id: int) -> dict:
        """
        Reabre una sugerencia.

        - Vuelve a estado 'pending'
        - La oculta del público
        - Limpia datos de publicación/moderación
        """
        record = self._get_suggestion(id)

        record.status = "pending"
        record.is_public = False
        record.published_at = None
        record.moderation_note = None

        return self._save(record)