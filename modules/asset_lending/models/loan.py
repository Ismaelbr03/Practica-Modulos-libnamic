from sqlalchemy import String, Text, ForeignKey, Uuid, DateTime, Integer
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.core.fields import field

class AssetLoan(Base):
    # Nombre de la tabla que registra el historial y estado de los préstamos
    __tablename__ = "asset_lending_loan"
    # Definición como entidad final para persistencia en base de datos
    __abstract__ = False
    # Identificador del modelo para el sistema de permisos y rutas de API
    __model__ = "loan"
    # Ruta al servicio que gestiona la lógica (ej: validar que el activo no esté ya prestado)
    __service__ = "modules.asset_lending.services.lending.AssetLoanService"

    # Configuración de búsqueda y visualización en listas desplegables (UI)
    __selector_config__ = {
        "label_field": "id",           # Usa el ID como referencia principal en el selector
        "search_fields": ["status"],   # Permite filtrar préstamos por su estado (open, closed, etc.)
        "columns": [                   # Columnas que se muestran al buscar un préstamo
            {"field": "id", "label": "ID"},
            {"field": "status", "label": "Estado"},
        ],
    }

    # ID del activo: Relación obligatoria con la tabla de recursos (Asset)
    asset_id = field(
        Integer,
        ForeignKey("asset_lending_asset.id"),
        required=True, # No puede existir un préstamo sin un objeto asociado
        public=True,
        editable=True, # Permite seleccionar el activo al crear el préstamo
        info={"label": {"es": "Recurso", "en": "Asset"}},
    )

    # ID del prestatario: Vincula el préstamo con un usuario del sistema (core_user)
    borrower_user_id = field(
        Uuid,
        ForeignKey("core_user.id"),
        required=True, # Es obligatorio saber a quién se le entrega el recurso
        public=True,
        editable=True,
        info={"label": {"es": "Usuario prestatario", "en": "Borrower"}},
    )

    # Estado del préstamo: Controla el ciclo de vida (por defecto 'open' al entregarse)
    status = field(
        String(20),
        required=True,
        public=True,
        editable=True,
        default="open",
        info={"label": {"es": "Estado del préstamo", "en": "Loan Status"}},
    )

    # Fecha de entrega: Registra el momento exacto de la salida del activo
    # DateTime(timezone=True) asegura que la hora sea consistente globalmente
    checkout_at = field(
        DateTime(timezone=True),
        required=True,
        public=True,
        editable=True,
        info={"label": {"es": "Fecha de entrega", "en": "Checkout Date"}},
    )

    # Fecha límite: Indica cuándo se espera que el usuario devuelva el activo
    due_at = field(
        DateTime(timezone=True),
        required=False, # Opcional, por si el préstamo es por tiempo indefinido
        public=True,
        editable=True,
        info={"label": {"es": "Fecha límite de devolución", "en": "Due Date"}},
    )

    # Fecha de devolución real: Se llena automáticamente cuando el activo regresa
    returned_at = field(
        DateTime(timezone=True),
        required=False,
        public=True,
        editable=False, # No es editable manualmente para evitar manipulaciones de fechas
        info={"label": {"es": "Fecha de devolución", "en": "Returned At"}},
    )

    # Notas de entrega: Para registrar el estado inicial (ej: "Se entrega con cargador")
    checkout_note = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Observaciones de entrega", "en": "Checkout Notes"}},
    )

    # Notas de devolución: Para registrar incidencias finales (ej: "Devuelto con rayón")
    return_note = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Observaciones de devolución", "en": "Return Notes"}},
    )