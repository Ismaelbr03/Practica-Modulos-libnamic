from __future__ import annotations

from sqlalchemy import String, Text, Integer, Boolean, DateTime, Uuid, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.core.fields import field


class Event(Base):
    __tablename__ = "community_event"
    __abstract__ = False

    # Identificación del modelo dentro del framework
    __model__ = "event"
    __service__ = "modules.community_events.services.event.EventService"

    # Configuración del selector (búsqueda y visualización en UI)
    __selector_config__ = {
        "label_field": "title",
        "search_fields": ["title", "slug"],
        "columns": [
            {"field": "id", "label": "ID"},
            {"field": "title", "label": "Título"},
            {"field": "status", "label": "Estado"},
        ],
    }

    # Información básica del evento
    title = field(
        String(180),
        required=True,
        public=True,
        info={"label": {"es": "Título del Evento", "en": "Event Title"}},
    )

    description = field(
        Text,
        required=False,
        public=True,
        info={"label": {"es": "Descripción", "en": "Description"}},
    )

    summary = field(
        String(300),
        required=False,
        public=True,
        info={"label": {"es": "Resumen", "en": "Summary"}},
    )

    slug = field(
        String(180),
        required=True,
        unique=True,
        public=True,
        info={"label": {"es": "Slug (URL)", "en": "Slug"}},
        # Identificador único para URLs amigables y acceso público
    )

    # Estado y visibilidad
    status = field(
        String(20),
        default="draft",
        required=True,
        public=True,
        editable=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"value": "draft", "label": {"es": "Borrador", "en": "Draft"}},
                {"value": "published", "label": {"es": "Publicado", "en": "Published"}},
                {"value": "closed", "label": {"es": "Cerrado", "en": "Closed"}},
                {"value": "cancelled", "label": {"es": "Cancelado", "en": "Cancelled"}},
            ],
        },
        # Controla el ciclo de vida del evento (borrador → publicado → cerrado/cancelado)
    )

    # Fechas y localización
    start_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        info={"label": {"es": "Fecha de inicio", "en": "Start Date"}},
    )

    end_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        info={"label": {"es": "Fecha de fin", "en": "End Date"}},
        # Se recomienda validar que end_at >= start_at a nivel de servicio
    )

    location = field(
        String(300),
        required=False,
        public=True,
        info={"label": {"es": "Ubicación", "en": "Location"}},
    )

    is_public = field(
        Boolean,
        default=False,
        public=True,
        info={"label": {"es": "Es Público", "en": "Is Public"}},
        # Determina si el evento es visible para usuarios no internos
    )

    # Capacidad y organización
    capacity_total = field(
        Integer,
        required=True,
        default=0,
        public=True,
        info={"label": {"es": "Aforo Total", "en": "Total Capacity"}},
        # Número máximo de asistentes permitidos
    )

    organizer_user_id = field(
        Uuid,
        ForeignKey("core_user.id", ondelete="SET NULL"),
        required=False,
        public=True,
        info={"label": {"es": "Organizador", "en": "Organizer"}},
        # Usuario responsable del evento (relación débil, puede ser null)
    )

    # Relaciones
    sessions = relationship(
        "EventSession",
        back_populates="event",
        cascade="all, delete-orphan",
        # Sesiones o agenda asociada al evento
    )

    registrations = relationship(
        "Registration",
        back_populates="event",
        cascade="all, delete-orphan",
        # Inscripciones de usuarios al evento
    )