from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.core.fields import field

# Importación de la tabla intermedia para la relación Many2many
# y del modelo Tag para poder establecer la relación bidireccional.
from .tag import suggestion_tag_rel, Tag


class Suggestion(Base):
    """
    Modelo de sugerencias enviadas por usuarios.

    Este modelo representa el flujo principal del módulo de feedback.
    Las sugerencias son creadas por usuarios públicos y pasan por un
    proceso de moderación donde pueden ser publicadas, rechazadas o fusionadas.
    """

    __tablename__ = "feedback_moderation_suggestion"
    __abstract__ = False
    __model__ = "suggestion"

    # Servicio de dominio asociado al modelo.
    # Aquí se implementa la lógica de negocio: publicar, rechazar,
    # fusionar sugerencias, reabrir, etc.
    __service__ = "modules.feedback_moderation.services.suggestion.SuggestionService"

    # Configuración del selector para la interfaz de usuario.
    # Define cómo se muestran y buscan las sugerencias en campos relacionales.
    __selector_config__ = {
        "label_field": "title",
        "search_fields": ["title", "author_email", "status"],
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "title", "label": "Título"},
            {"field": "status", "label": "Estado"},
            {"field": "author_email", "label": "Email Autor"},
            {"field": "is_public", "label": "Público"},
        ],
    }

    # Título de la sugerencia.
    # Campo obligatorio y visible públicamente.
    title = field(
        String(180),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Título", "en": "Title"}},
    )

    # Descripción o contenido de la sugerencia.
    # Aquí el usuario explica la propuesta o problema.
    content = field(
        Text,
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Contenido", "en": "Content"}},
    )

    # Estado dentro del flujo de moderación.
    # Estados posibles:
    # - pending: pendiente de revisión
    # - published: aprobada y visible públicamente
    # - rejected: rechazada por el moderador
    # - merged: fusionada con otra sugerencia existente
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
                {"label": "Fusionado", "value": "merged"},
            ],
        },
    )

    # Nombre del autor de la sugerencia (usuario público).
    # No es obligatorio porque puede ser anónimo.
    author_name = field(
        String(100),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Nombre del autor", "en": "Author Name"}},
    )

    # Email del autor de la sugerencia.
    # Se usa para contacto o identificación básica.
    author_email = field(
        String(150),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Email del autor", "en": "Author Email"}},
    )

    # Indica si la sugerencia es visible en la parte pública del sistema.
    # Solo las sugerencias publicadas y con is_public=True serán visibles
    # según las reglas ACL.
    is_public = field(
        Boolean,
        required=True,
        public=True,
        editable=True,
        default=False,
        info={"label": {"es": "Público", "en": "Public"}},
    )

    # Nota interna del moderador.
    # Se utiliza para explicar el motivo de rechazo, fusión o publicación.
    moderation_note = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Nota de moderación", "en": "Moderation Note"}},
    )

    # Fecha de publicación de la sugerencia.
    # Se rellena automáticamente cuando la sugerencia pasa a estado "published".
    published_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False,
        info={"label": {"es": "Publicado en", "en": "Published at"}},
    )

    # Usuario moderador que revisó la sugerencia.
    # Relación con la tabla de usuarios del sistema.
    reviewed_by_id = field(
        Uuid,
        ForeignKey("core_user.id"),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Revisado por", "en": "Reviewed by"}},
    )

    # --- Relaciones ORM ---

    # Relación Many2one con el usuario que revisó la sugerencia.
    # Permite saber qué moderador realizó la acción de moderación.
    reviewed_by = relationship(
        "User",
        foreign_keys=lambda: [Suggestion.reviewed_by_id],
        info={"public": True, "recursive": False, "editable": True},
    )

    # Relación Many2many con etiquetas (tags).
    # Permite clasificar las sugerencias por categorías o temas.
    # Se usa una tabla intermedia (suggestion_tag_rel).
    tags = relationship(
        "Tag",
        secondary=suggestion_tag_rel,
        back_populates="suggestions",
        info={
            "public": True,
            "recursive": False,
            "editable": True,
            "label": {"es": "Etiquetas", "en": "Tags"}
        }
    )