# Permite usar anotaciones modernas
from __future__ import annotations

# Alias para manejar fechas y horas
import datetime as dt

# Excepcion HTTP estandar de FastAPI
from fastapi import HTTPException

# Clase base de servicios del proyecto
from app.core.base import BaseService

# Funcion para obtener el usuario actual
from app.core.context import get_current_user_id

# Funcion para convertir un modelo SQLAlchemy a serializable
from app.core.serializer import serialize

# Decorador personalizado para exponer metodos como acciones accesibles por API
from app.core.services import exposed_action

# Importamos las listas para poder coger mas de 1 columana
from typing import List

# Importacion de los modelos
from ..models import PracticeChecklist, PracticeChecklistItem


# Maneja la logica del programa
class PracticeChecklistService(BaseService):
    # Import interno del modelo asociado a este servicio
    from ..models import PracticeChecklist

    def create(self, obj):  # type: ignore[override]
        """
        Sobrescribe el método create del BaseService
        para agregar valores automáticos al crear un checklist.
        """

        # Si no es un diccionario, usa el comportamiento normal
        if not isinstance(obj, dict):
            return super().create(obj)

        # Creamos una copia del payload
        payload = dict(obj)

        # Si no se envia owner_id, asigna automaticamente el usuario actual del contexto
        if not payload.get("owner_id"):
            payload["owner_id"] = get_current_user_id()

        # Si no se envia status, lo pone en "open"
        if not payload.get("status"):
            payload["status"] = "open"

        # Llama al create original del BaseService
        return super().create(payload)


    # Cierra elk checklist
    @exposed_action(
        "write",
        groups=["practice_checklist_group_manager", "core_group_superadmin"]
    )
    def close(self, id: int, close_note: str | None = None, make_public: bool = False) -> dict:
        """
        Cierra un checklist:
        - Cambia status a 'closed'
        - Marca fecha de cierre
        - Opcionalmente lo hace público
        - Puede agregar una nota de cierre
        """

        # Busca el checklist en base de datos
        rec = self.repo.session.get(PracticeChecklist, int(id))

        # Si no existe, devuelve error 404
        if rec is None:
            raise HTTPException(404, "Checklist not found")

        # Cambia el estado a cerrado
        rec.status = "closed"

        # Pone si es publico o no
        rec.is_public = bool(make_public)

        # Guarda la fecha actual
        rec.closed_at = dt.datetime.now(dt.timezone.utc)

        # Si envia nota de cierre
        if close_note:
            # Toma descripcion prevista
            base = (rec.description or "").strip()

            # Agrega la nota al final
            rec.description = f"{base}\n\n[Cierre] {close_note}".strip()

        # Marca el objeto como modificado
        self.repo.session.add(rec)

        # Guarda cambios en la base de datos
        self.repo.session.commit()

        # Refresca el objeto desde la BD
        self.repo.session.refresh(rec)

        # Devuelve el objeto serializado
        return serialize(rec)


    # Reabre un checklist cerrado
    @exposed_action(
        "write",
        groups=["practice_checklist_group_manager", "core_group_superadmin"]
    )
    def reopen(self, id: int) -> dict:
        """
        Reabre un checklist:
        - Cambia status a 'open'
        - Borra la fecha de cierre
        """

        # Busca el checklist
        rec = self.repo.session.get(PracticeChecklist, int(id))

        # Si no existe da error 404
        if rec is None:
            raise HTTPException(404, "Checklist not found")

        # Cambia el estado
        rec.status = "open"

        # Borra fecha de cierre
        rec.closed_at = None

        # Guarda cambios
        self.repo.session.add(rec)
        self.repo.session.commit()
        self.repo.session.refresh(rec)

        # Devuelve version serializada
        return serialize(rec)


# Maneja logica del programa de los items del checklist
class PracticeChecklistItemService(BaseService):
    from ..models import PracticeChecklistItem

    # Marca un item como hecho o no hecho
    @exposed_action(
        "write",
        groups=["practice_checklist_group_manager", "core_group_superadmin"]
    )
    def set_done(
        self,
        id: int | None = None,
        ids: List[int] | None = None,
        done: bool = True,
        note: str | None = None
    ) -> dict:
        """
        Permite marcar uno o varios items.
        Soporta tanto acciones individuales (row_action) como masivas (bulk_action).
        """

        # Determinar si es accion individual o masiva
        if ids:
            id_list = ids  # Mas de uno
        elif id is not None:
            id_list = [id]  # Solo uno
        else:
            raise HTTPException(400, "No id or ids provided")  # Ningun error

        # Buscar todos los items
        items = (
            self.repo.session.query(PracticeChecklistItem)
            .filter(PracticeChecklistItem.id.in_(id_list))
            .all()
        )

        # Aplicar cambios a cada item
        for item in items:
            # Marca como hecho o no
            if done:
                item.is_done = True
                item.done_at = dt.datetime.now(dt.timezone.utc)
            else:
                item.is_done = False
                item.done_at = None

            # Añadir nota si la hay
            if note:
                if item.note:
                    item.note = item.note + "\n\n[Estado] " + note
                else:
                    item.note = "[Estado] " + note

            # Guardar cambios
            self.repo.session.add(item)

        # Confirmar todos los cambios en la base de datos
        self.repo.session.commit()

        # Cierre automatico usando settings.yml
        if self.get_setting("practice_checklist.auto_close_when_all_done"):

            # Obtener checklist afectados, sin duplicados
            checklist_ids = list({item.checklist_id for item in items})

            for checklist_id in checklist_ids:
                checklist = self.repo.session.get(PracticeChecklist, checklist_id)
                if checklist:
                    # Refrescar los items para que la sesion tenga datos actualizados
                    self.repo.session.refresh(checklist)
                    # Verificar si todos los items estan hechos
                    all_done = all(ci.is_done for ci in checklist.items)
                    if all_done and checklist.status != "closed":
                        checklist.status = "closed"
                        checklist.closed_at = dt.datetime.now(dt.timezone.utc)
                        self.repo.session.add(checklist)

            self.repo.session.commit()

        # Devolver los items actualizados
        return [serialize(item) for item in items]