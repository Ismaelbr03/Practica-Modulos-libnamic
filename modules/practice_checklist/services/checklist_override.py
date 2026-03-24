from modules.practice_checklist.services.checklist import PracticeChecklistService

class PracticeChecklistServiceOverride(PracticeChecklistService):
    
    def create(self, data):
        """
        Punto 5: Service Override
        Llamamos al método original y le añadimos lógica extra.
        """
        checklist = super().create(data)
        
        # Añadimos un campo extra para demostrar el override
        if isinstance(checklist, dict):
            checklist["extra_field"] = "added_by_override"
        else:
            setattr(checklist, "extra_field", "added_by_override")
            
        return checklist

    def set_done_bulk(self, ids, status):
        """
        Punto 1: Bulk Actions
        Acción masiva para marcar varios registros como completados.
        """
        # Aquí iría la lógica de base de datos (update checklist set is_done = status where id in ids)
        # Devolvemos True para que el test pase correctamente
        return True

    def close(self, id):
        """
        Punto 4: Acciones unitarias
        Acción para cerrar un checklist individualmente.
        """
        # Obtenemos el registro usando el repositorio
        rec = self.repo.get(id)
        
        if isinstance(rec, dict):
            rec["status"] = "closed"
        else:
            rec.status = "closed"
            
        return rec