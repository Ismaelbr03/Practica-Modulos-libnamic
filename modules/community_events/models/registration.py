from __future__ import annotations

from sqlalchemy import String, Text, DateTime, ForeignKey, Uuid, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.base import Base
from app.core.fields import field


class Registration(Base):
    __tablename__ = "community_event_registration"
    __abstract__ = False

    # Identificación del modelo dentro del módulo
    __model__ = "registration"
    __service__ = "modules.community_events.services.registration.RegistrationService"

    # Relaciones principales
    event_id = field(
        Integer,
        ForeignKey("community_event.id", ondelete="CASCADE"),
        required=True,
        public=True,
        info={"label": {"es": "Evento", "en": "Event"}},
        # Evento al que pertenece la inscripción (obligatorio)
    )

    session_id = field(
        Integer,
        ForeignKey("community_event_session.id", ondelete="SET NULL"),
        required=False,
        public=True,
        info={"label": {"es": "Sesión (Opcional)", "en": "Session"}},
        # Sesión específica dentro del evento (si aplica)
    )

    attendee_user_id = field(
        Uuid,
        ForeignKey("core_user.id", ondelete="SET NULL"),
        required=False,
        public=True,
        info={"label": {"es": "Usuario", "en": "User"}},
        # Referencia al usuario si está autenticado (relación opcional)
    )

    # Datos del asistente
    attendee_name = field(
        String(180),
        required=True,
        public=True,
        info={"label": {"es": "Nombre Asistente", "en": "Attendee Name"}},
    )

    attendee_email = field(
        String(180),
        required=True,
        public=True,
        info={"label": {"es": "Email", "en": "Email"}},
        # Canal principal de comunicación (confirmaciones, avisos, etc.)
    )

    # Estado de la inscripción
    status = field(
        String(50),
        default="pending",
        public=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"value": "pending", "label": {"es": "Pendiente", "en": "Pending"}},
                {"value": "confirmed", "label": {"es": "Confirmada", "en": "Confirmed"}},
                {"value": "waitlist", "label": {"es": "Lista de Espera", "en": "Waitlist"}},
                {"value": "cancelled", "label": {"es": "Cancelada", "en": "Cancelled"}},
            ],
        },
    )

    notes = field(
        Text,
        required=False,
        public=True,
        info={"label": {"es": "Notas", "en": "Notes"}},
        # Información adicional relevante (dietas, observaciones, incidencias, etc.)
    )

    # Trazabilidad
    registered_at = field(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        public=True,
        info={"label": {"es": "Fecha de Registro", "en": "Registered At"}},
        # Momento en el que se realiza la inscripción
    )

    checkin_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        info={"label": {"es": "Fecha de Check-in", "en": "Check-in Date"}},
        # Se rellena cuando el asistente accede físicamente al evento
    )

    # Relaciones ORM
    event = relationship(
        "Event",
        back_populates="registrations",
        # Acceso al evento asociado desde la inscripción
    )

    session = relationship(
        "EventSession",
        back_populates="registrations",
        # Acceso a la sesión concreta (si existe)
    )