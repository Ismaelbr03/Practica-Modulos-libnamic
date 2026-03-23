from sqlalchemy import String, Text, ForeignKey, Uuid, Integer
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.core.fields import field

class Asset(Base):
    # Nombre de la tabla física que se creará en la base de datos SQL
    __tablename__ = "asset_lending_asset"
    # Al ser False, el sistema confirma que esta clase no es solo un molde, sino una entidad final
    __abstract__ = False
    # Identificador único del modelo para el motor de permisos (ACL) y rutas internas
    __model__ = "asset"
    # Ruta al archivo de Service que contiene la lógica de negocio (CRUD, validaciones personalizadas)
    __service__ = "modules.asset_lending.services.lending.AssetService"

    # Configura cómo se comportará este modelo en los desplegables de la interfaz web
    __selector_config__ = {
        "label_field": "name",           # El campo que se verá por defecto en los selects
        "search_fields": ["name", "asset_code", "status"], # Campos habilitados para búsqueda rápida
        "columns": [                     # Columnas que aparecerán en la tabla de búsqueda avanzada
            {"field": "id", "label": "ID"},
            {"field": "name", "label": "Recurso"},
            {"field": "asset_code", "label": "Código"},
        ],
    }

    # ID de la ubicación: Almacena el número entero que conecta con la tabla 'asset_lending_location'
    location_id = field(
        Integer,
        ForeignKey("asset_lending_location.id"),
        required=False, # Permite que un activo no tenga ubicación asignada inicialmente
        public=True,    # Expone el campo a través de la API
        editable=True,  # Permite que el usuario cambie la ubicación desde el formulario
        info={"label": {"es": "Ubicación", "en": "Location"}}, # Traducciones para la etiqueta del campo
    )

    # Relación de objeto: Permite acceder a los datos de la ubicación (ej. asset.location.name)
    location = relationship(
        "modules.asset_lending.models.location.AssetLocation",
        foreign_keys=lambda: [Asset.location_id], # Resuelve la clave foránea de forma perezosa para evitar errores de importación
        info={"public": True, "recursive": False, "editable": True},
    )

    # Vínculo con el usuario: Usa Uuid porque es el estándar del núcleo (core_user) para IDs globales
    responsible_user_id = field(
        Uuid,
        ForeignKey("core_user.id"),
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Usuario responsable", "en": "Responsible User"}},
    )

    # Nombre del recurso: String con límite de 180 caracteres para optimizar almacenamiento
    name = field(
        String(180),
        required=True, # Campo obligatorio: no se puede crear un activo sin nombre
        public=True,
        editable=True,
        info={"label": {"es": "Nombre del recurso", "en": "Asset Name"}},
    )

    # Código del activo: String indexado y único para evitar duplicados en el inventario
    asset_code = field(
        String(50),
        required=True,
        public=True,
        editable=True,
        unique=True, # Bloquea a nivel de base de datos la creación de dos activos con el mismo código
        info={"label": {"es": "Código del activo", "en": "Asset Code"}},
    )

    # Notas: Tipo Text para permitir descripciones largas sin límite estricto de caracteres
    notes = field(
        Text,
        required=False,
        public=True,
        editable=True,
        info={"label": {"es": "Observaciones", "en": "Notes"}},
    )

    # Estado: Controla el flujo de vida del activo (available, loaned, broken, etc.)
    status = field(
        String(20),
        required=True,
        public=True,
        editable=True,
        default="available", # Valor que toma automáticamente si no se especifica uno al crear
        info={"label": {"es": "Estado del activo", "en": "Asset Status"}},
    )