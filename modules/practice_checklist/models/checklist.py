# Para anotaciones modernas
from __future__ import annotations

# Importaciones comunes de tipo de SQLAlchemy
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UUID

# Importaciones para relaciones 1-N o N-M
from sqlalchemy.orm import backref, relationship

# Clase personalizada del proyecto
from app.core.base import Base

# Funcion personalizada para definir datos adicionales
from app.core.fields import field

# Modelo que representa una checklist
class PracticeChecklist(Base):
    # Nombre de la tabla en la BD
    __tablename__ = "practice_checklist"
    # Modelo no abstracto (que si se crea en la BD)
    __abstract__ = False
    # Nombre interno en el systema
    __model__ = "checklist"
    # Ruta del servicio que maneja la logica del programa
    __service__ = "modules.practice_checklist.services.checklist.PracticeChecklistService"

    __selector_config__ = {
        # Campo que se usa como etiqueta principal
        "label_field": "name",
        # Campo de los que se puede buscar
        "search_fields": ["name", "status", "description"],
        # Columnas que tiene
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "name", "label": "Checklist"},
            {"field": "status", "label": "Estado"},
            {"field": "is_public", "label": "Público"},
        ],
    }

    # Aqui se definen los campos que usamos
    name = field(
        String(180),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Checklist", "en": "Checklist"}},
    )

    description = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Descripción", "en": "Description"}},
    )

    status = field(
        String(20),
        required=True,
        public=True,
        editable=True,
        default="draft",
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Draft", "value": "draft"},
                {"label": "Open", "value": "open"},
                {"label": "Closed", "value": "closed"},
            ],
        },
    )

    is_public = field(
        Boolean,
        required=True,
        public=True,
        editable=True,
        default=False,
        info={"label": {"es": "Público", "en": "Public"}},
    )

    owner_id = field(
        UUID,
        ForeignKey("core_user.id"),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Responsable", "en": "Owner"}},
    )

    # Relacion entre owner y user
    owner = relationship(
        "User",
        foreign_keys=lambda: [PracticeChecklist.owner_id],
        info={"public": True, "recursive": False, "editable": True},
    )

    closed_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False,
        info={"label": {"es": "Cerrado en", "en": "Closed at"}},
    )

# Representa un item dentro de la checklist
class PracticeChecklistItem(Base):
    __tablename__ = "practice_checklist_item"
    __abstract__ = False
    __model__ = "checklist_item"
    __service__ = "modules.practice_checklist.services.checklist.PracticeChecklistItemService"

    __selector_config__ = {
        "label_field": "title",
        "search_fields": ["title", "note"],
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "checklist", "label": "Checklist"},
            {"field": "title", "label": "Ítem"},
            {"field": "is_done", "label": "Hecho"},
        ],
    }

    checklist_id = field(
        Integer,
        ForeignKey("practice_checklist.id", ondelete="CASCADE"),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Checklist", "en": "Checklist"}},
    )

    checklist = relationship(
        "modules.practice_checklist.models.checklist.PracticeChecklist",
        foreign_keys=lambda: [PracticeChecklistItem.checklist_id],
        backref=backref("items", cascade="all, delete-orphan"), # crea automaticamente un checklist items
        info={"public": True, "recursive": False, "editable": True},
    )

    title = field(
        String(180),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Ítem", "en": "Item"}},
    )

    note = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Nota", "en": "Note"}},
    )

    assigned_user_id = field(
        UUID,
        ForeignKey("core_user.id"),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Asignado a", "en": "Assigned to"}},
    )

    assigned_user = relationship(
        "User",
        foreign_keys=lambda: [PracticeChecklistItem.assigned_user_id],
        info={"public": True, "recursive": False, "editable": True},
    )

    is_done = field(
        Boolean,
        required=True,
        public=True,
        editable=True,
        default=False,
        info={"label": {"es": "Hecho", "en": "Done"}},
    )

    done_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False,
        info={"label": {"es": "Hecho en", "en": "Done at"}},
    )

# El modelo de configuracion de los setting
class PracticeChecklistSettings(Base):
    __tablename__ = "practice_checklist_settings"
    __abstract__ = False
    __model__ = "checklist_settings"

    auto_close_when_all_done = field(
        Boolean,
        required=True,
        public=True,
        editable=True,
        default=False,
        info={"label": {"es": "Cierre automático", "en": "Auto close"}},
    )