from __future__ import annotations

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.core.fields import field


class EventSession(Base):
    __tablename__ = "community_event_session"
    __abstract__ = False

    # Identificación del modelo dentro del módulo
    __model__ = "session"
    __service__ = "modules.community_events.services.session.SessionService"

    # Relación con evento principal
    event_id = field(
        Integer,
        ForeignKey("community_event.id", ondelete="CASCADE"),
        required=True,
        public=True,
        info={"label": {"es": "Evento", "en": "Event"}},
        # Vincula la sesión con el evento correspondiente
    )

    # Información básica de la sesión
    title = field(
        String(180),
        required=True,
        public=True,
        info={"label": {"es": "Título de la Sesión", "en": "Session Title"}},
    )

    speaker_name = field(
        String(180),
        required=False,
        public=True,
        info={"label": {"es": "Ponente", "en": "Speaker"}},
        # Nombre del ponente o responsable de la sesión
    )

    start_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        info={"label": {"es": "Inicio", "en": "Start"}},
        # Hora de inicio de la sesión
    )

    end_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        info={"label": {"es": "Fin", "en": "End"}},
        # Hora de finalización de la sesión
    )

    capacity = field(
        Integer,
        required=False,
        public=True,
        info={"label": {"es": "Aforo Sesión", "en": "Session Capacity"}},
        # Número máximo de asistentes permitido en la sesión
    )

    room = field(
        String(120),
        required=False,
        public=True,
        info={"label": {"es": "Sala", "en": "Room"}},
        # Ubicación física o virtual de la sesión
    )

    # Estado de la sesión
    status = field(
        String(50),
        default="active",
        public=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"value": "active", "label": {"es": "Activa", "en": "Active"}},
                {"value": "cancelled", "label": {"es": "Cancelada", "en": "Cancelled"}},
            ],
        },
        # Controla si la sesión está disponible o cancelada
    )

    # Relaciones ORM
    event = relationship(
        "Event",
        back_populates="sessions",
        # Permite acceder al evento desde la sesión
    )

    registrations = relationship(
        "Registration",
        back_populates="session",
        cascade="all, delete-orphan",
        # Inscripciones asociadas a esta sesión
    )