from sqlalchemy import Boolean, String
from app.core.base import Base
from app.core.fields import field

class AssetLocation(Base):
    # Nombre de la tabla física en la base de datos para almacenar ubicaciones
    __tablename__ = "asset_lending_location"
    # Entidad final: se creará una tabla real en el motor SQL
    __abstract__ = False
    # Identificador del modelo para el motor de permisos y rutas internas
    __model__ = "location"
    # Referencia al servicio que contiene la lógica de negocio para las ubicaciones
    __service__ = "modules.asset_lending.services.lending.AssetLocationService"

    # Configuración de búsqueda y visualización en los selectores de la interfaz web
    __selector_config__ = {
        "label_field": "name",           # El nombre de la ubicación será el texto visible en los desplegables
        "search_fields": ["name", "code"], # Campos habilitados para la búsqueda rápida
        "columns": [                     # Estructura de la tabla de selección avanzada
            {"field": "id", "label": "ID"},
            {"field": "name", "label": "Nombre"},
            {"field": "code", "label": "Código"},
        ],
    }

    # ----------------------------------------------------------------
    # ESTADO DE LA UBICACIÓN
    # ----------------------------------------------------------------
    # Define si la ubicación está operativa (True) o deshabilitada (False)
    is_active = field(
        Boolean,
        required=True,   # Obligatorio definir el estado
        public=True,     # Visible en la API
        editable=True,   # Permite activar/desactivar desde el formulario
        default=True,    # Por defecto, una nueva ubicación se crea como activa
        info={"label": {"es": "Activo", "en": "Active"}},
    )

    # ----------------------------------------------------------------
    # NOMBRE DE LA UBICACIÓN
    # ----------------------------------------------------------------
    # Texto descriptivo (ej: "Almacén Central", "Oficina 402")
    name = field(
        String(180),
        required=True,   # No se puede crear una ubicación sin nombre
        public=True,
        editable=True,
        info={"label": {"es": "Ubicación", "en": "Location"}},
    )

    # ----------------------------------------------------------------
    # CÓDIGO ÚNICO DE LA UBICACIÓN
    # ----------------------------------------------------------------
    # Identificador interno o código de inventario (ej: "ALM-01")
    code = field(
        String(50),
        required=True,
        public=True,
        editable=True,
        unique=True,     # Garantiza que no existan dos ubicaciones con el mismo código
        info={"label": {"es": "Código de ubicación", "en": "Location Code"}},
    )