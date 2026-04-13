from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.core.fields import field


class Comment(Base):
    """
    Modelo de comentarios asociados a sugerencias.

    Este modelo permite a usuarios públicos añadir comentarios sobre sugerencias.
    Todos los comentarios pasan por un flujo de moderación antes de ser visibles
    públicamente.
    """

    __tablename__ = "feedback_moderation_comment"
    __abstract__ = False
    __model__ = "comment"

    # Servicio de dominio asociado al modelo.
    # Aquí se implementan las acciones de moderación como publicar o rechazar.
    __service__ = "modules.feedback_moderation.services.comment.CommentService"

    # Configuración del selector utilizada por la UI para mostrar registros
    # en campos relacionales Many2one. Define cómo se buscan y muestran.
    __selector_config__ = {
        "label_field": "id",
        "search_fields": ["content", "author_email", "status"],
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "suggestion_id", "label": "Sugerencia ID"},
            {"field": "status", "label": "Estado"},
            {"field": "author_email", "label": "Email Autor"},
            {"field": "is_public", "label": "Público"},
        ],
    }

    # Clave foránea a la sugerencia.
    # Relación obligatoria: un comentario siempre pertenece a una sugerencia.
    # ondelete="CASCADE" asegura que si se elimina la sugerencia,
    # también se eliminan automáticamente sus comentarios.
    suggestion_id = field(
        Integer,
        ForeignKey("feedback_moderation_suggestion.id", ondelete="CASCADE"),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Sugerencia", "en": "Suggestion"}},
    )

    # Texto del comentario enviado por el usuario.
    # Este contenido será moderado antes de su publicación.
    content = field(
        Text,
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Contenido", "en": "Content"}},
    )

    # Estado del comentario dentro del flujo de moderación.
    # Estados posibles:
    # - pending: pendiente de revisión
    # - published: aprobado y visible
    # - rejected: rechazado por el moderador
    # Por defecto, todo comentario nuevo se crea como "pending".
    status = field(
        String(20),
        required=True,
        public=True,
        editable=True,
        default="pending",
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Pendiente", "value": "pending"},
                {"label": "Publicado", "value": "published"},
                {"label": "Rechazado", "value": "rejected"},
            ],
        },
    )

    # Email del autor del comentario.
    # Se utiliza para identificar al autor en entornos públicos sin autenticación.
    author_email = field(
        String(150),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Email del autor", "en": "Author Email"}},
    )

    # Indica si el comentario puede mostrarse en la parte pública del sistema.
    # Un comentario puede estar publicado pero no ser público si el moderador decide ocultarlo.
    is_public = field(
        Boolean,
        required=True,
        public=True,
        editable=True,
        default=False,
        info={"label": {"es": "Público", "en": "Public"}},
    )

    # Fecha y hora en la que el comentario fue publicado.
    # Este campo se rellena automáticamente cuando el moderador aprueba el comentario.
    published_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False,
        info={"label": {"es": "Publicado en", "en": "Published at"}},
    )

    # Relación ORM con el modelo Suggestion.
    # Permite acceder a la sugerencia desde el comentario.
    # recursive=False evita cargas recursivas infinitas en serialización pública.
    suggestion = relationship(
        "Suggestion",
        foreign_keys=lambda: [Comment.suggestion_id],
        info={"public": True, "recursive": False, "editable": True},
    )