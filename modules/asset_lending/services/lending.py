import datetime as dt
from fastapi import HTTPException

from app.core.base import BaseService
from app.core.services import exposed_action
from app.core.serializer import serialize


# --- SERVICIO: UBICACIONES ---
class AssetLocationService(BaseService):
    # Importación local para evitar ciclos y vincular el modelo al servicio
    from ..models import AssetLocation


# --- SERVICIO: RECURSOS (ASSETS) ---
class AssetService(BaseService):
    from ..models import Asset

    # Acción expuesta: Cambia el estado a mantenimiento
    # 'write' indica el permiso requerido; 'groups' define quién puede ejecutarlo
    @exposed_action("write", groups=["asset_lending_group_manager", "asset_lending_group_tech", "core_group_superadmin"])
    def mark_maintenance(self, id: int, note: str | None = None) -> dict:
        # Obtener el registro de la base de datos por su ID
        asset = self.repo.session.get(self.Asset, int(id))
        if asset is None:
            raise HTTPException(404, "Asset not found") # Error 404 si el ID no existe
        
        # Actualización del estado del recurso
        asset.status = "maintenance"

        # Lógica para concatenar notas de mantenimiento sin borrar las anteriores
        if note:
            base = (asset.notes or "").strip()
            # Añade un separador visual y la nueva nota al final del texto existente
            asset.notes = f"{base}\n\n[Mantenimiento] {note}".strip()
            
        # Persistencia: Guardar cambios y refrescar el objeto para devolver los datos actualizados
        self.repo.session.add(asset)
        self.repo.session.commit()
        self.repo.session.refresh(asset)
        return serialize(asset) # Convierte el objeto SQL en un diccionario para la API


    # Acción expuesta: Finaliza el mantenimiento y libera el recurso
    @exposed_action("write", groups=["asset_lending_group_manager", "asset_lending_group_tech", "core_group_superadmin"])
    def release_maintenance(self, id: int) -> dict:
        asset = self.repo.session.get(self.Asset, int(id))
        if asset is None:
            raise HTTPException(404, "Asset not found")
            
        # El activo vuelve a estar apto para ser prestado
        asset.status = "available"
        self.repo.session.add(asset)
        self.repo.session.commit()
        self.repo.session.refresh(asset)
        return serialize(asset)


# --- SERVICIO: PRÉSTAMOS (LOANS) ---
class AssetLoanService(BaseService):
    from ..models import AssetLoan
    from ..models import Asset

    # Acción crítica: Cierra un préstamo y libera el activo automáticamente
    @exposed_action("write", groups=["asset_lending_group_manager", "core_group_superadmin"])
    def return_asset(self, id: int, note: str | None = None) -> dict:
        # 1. Recuperar el préstamo
        loan = self.repo.session.get(self.AssetLoan, int(id))
        if loan is None:
            raise HTTPException(404, "Loan not found")
        
        # Validación de seguridad: Solo se puede devolver algo que está 'abierto'
        if loan.status != "open":
            raise HTTPException(400, "Este préstamo ya no está abierto.")

        # 2. Actualizar los datos del Préstamo
        loan.status = "returned"
        # Registra la fecha y hora exacta del servidor en formato UTC
        loan.returned_at = dt.datetime.now(dt.timezone.utc)
        if note:
            loan.return_note = note

        # 3. Sincronización: Localizar el activo físico vinculado al préstamo
        asset = self.repo.session.get(self.Asset, loan.asset_id)
        if asset:
            # Importante: Aquí es donde el activo vuelve a ser 'available' automáticamente
            asset.status = "available"
            self.repo.session.add(asset)

        # 4. Confirmar todas las operaciones en una sola transacción
        self.repo.session.add(loan)
        self.repo.session.commit()
        self.repo.session.refresh(loan)
        return serialize(loan)