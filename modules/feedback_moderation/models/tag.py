from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.core.fields import field

# Tabla intermedia para la relación Many2Many entre Suggestion y Tag.
# Esta tabla no tiene modelo propio, solo sirve para relacionar
# sugerencias con etiquetas. Si se elimina una sugerencia o una etiqueta,
# las relaciones también se eliminan automáticamente (CASCADE).
suggestion_tag_rel = Table(
    "feedback_moderation_suggestion_tag_rel",
    Base.metadata,
    Column(
        "suggestion_id",
        Integer,
        ForeignKey("feedback_moderation_suggestion.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("feedback_moderation_tag.id", ondelete="CASCADE"),
        primary_key=True
    ),
)


class Tag(Base):
    """
    Modelo de etiquetas para clasificar sugerencias.

    Las etiquetas permiten organizar y categorizar las sugerencias
    (por ejemplo: UI, Bug, Mejora, Feature, etc.).
    Se relacionan con Suggestion mediante una relación Many2Many.
    """

    __tablename__ = "feedback_moderation_tag"
    __abstract__ = False
    __model__ = "tag"

    # Servicio asociado al modelo Tag.
    # Aquí se pueden implementar acciones como crear slug automáticamente, etc.
    __service__ = "modules.feedback_moderation.services.tag.TagService"

    # Configuración del selector para la UI.
    # Define cómo se muestran las etiquetas en los campos Many2many.
    __selector_config__ = {
        "label_field": "name",
        "search_fields": ["name", "slug"],
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "name", "label": "Nombre"},
            {"field": "slug", "label": "Slug"},
            {"field": "color", "label": "Color"},
        ],
    }

    # Nombre de la etiqueta (lo que ve el usuario).
    name = field(
        String(100),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Nombre", "en": "Name"}},
    )

    # Slug de la etiqueta (identificador técnico, usado en URLs o filtros).
    # Normalmente se genera automáticamente a partir del nombre.
    slug = field(
        String(100),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Slug", "en": "Slug"}},
    )

    # Color de la etiqueta en formato hexadecimal.
    # Se usa en la UI para mostrar etiquetas con color.
    color = field(
        String(20),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Color (Hex)", "en": "Color (Hex)"}},
    )

    # Relación inversa Many2Many con Suggestion.
    # Permite acceder a todas las sugerencias que tienen esta etiqueta.
    # back_populates conecta esta relación con Suggestion.tags.
    suggestions = relationship(
        "Suggestion",
        secondary=suggestion_tag_rel,
        back_populates="tags",
        info={"public": True, "recursive": False, "editable": True},
    )