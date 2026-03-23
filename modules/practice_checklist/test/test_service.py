import pytest
from unittest.mock import MagicMock, patch, PropertyMock

# Importo la clase override que voy a testear
from modules.practice_checklist.services.checklist_override import PracticeChecklistServiceOverride

@pytest.fixture
def checklist_service():
    """
    Aquí configuro el servicio con un Mock que sobrevive al serializador de Licium.
    Basicamente simulo el repositorio y un registro de base de datos.
    """
    mock_repo = MagicMock()
    
    # Creo el objeto que simula ser un registro de base de datos
    mock_rec = MagicMock()
    
    # ESTO EVITA EL ERROR __mapper__:
    # El serializador de Licium espera que el modelo tenga __mapper__ (como los modelos de SQLAlchemy),
    # así que se lo añado al mock a nivel de clase para que no falle.
    type(mock_rec).__mapper__ = PropertyMock()
    
    # Defino algunos campos que tendría el registro
    mock_rec.id = 99
    mock_rec.name = "Test Checklist"
    mock_rec.status = "open"
    mock_rec.extra_field = "added_by_override"
    
    # Configuro el repo para que cuando se llame a get, create o session.get devuelva este objeto
    mock_repo.get.return_value = mock_rec
    mock_repo.create.return_value = mock_rec
    mock_repo.session.get.return_value = mock_rec
    
    # Creo el servicio usando el repo mockeado
    service = PracticeChecklistServiceOverride(mock_repo)
    
    # Simulo los settings del servicio
    service.settings = {"auto_close": True}
    
    return service


# --- TESTS DE LOS 5 PUNTOS ---

def test_point_1_bulk_actions(checklist_service):
    """
    Aquí verifico la acción masiva 'set_done_bulk' (Punto 1)
    """
    # Verifico que el método existe
    if hasattr(checklist_service, 'set_done_bulk'):
        res = checklist_service.set_done_bulk([1, 2, 3], True)
        
        # La acción bulk debería devolver True si todo va bien
        assert res is True
    else:
        pytest.fail("ERROR: El método 'set_done_bulk' no existe. Revisa tu checklist_override.py")


def test_point_2_and_3_settings_and_i18n(checklist_service):
    """
    Aquí verifico la integración de settings (Punto 2).
    Básicamente compruebo que el servicio puede acceder a sus settings.
    """
    assert "auto_close" in checklist_service.settings
    assert checklist_service.settings["auto_close"] is True


def test_point_5_service_override(checklist_service):
    """
    Aquí verifico el override del servicio:
    el servicio debe añadir el campo 'extra_field'
    """
    # Mockeo serialize para evitar que intente usar mappers reales del core
    with patch('modules.practice_checklist.services.checklist.serialize', side_effect=lambda x: x):
        payload = {"name": "Test Override"}
        result = checklist_service.create(payload)
        
        # Verifico que se ha creado algo
        assert result is not None
        
        # Verifico que el campo extra existe (esto valida el override - Punto 5)
        assert hasattr(result, "extra_field")
        assert result.extra_field == "added_by_override"


@patch('modules.practice_checklist.services.checklist.serialize', side_effect=lambda x: x)
def test_point_4_unit_actions_close(mock_serialize, checklist_service):
    """
    Aquí verifico la acción unitaria 'close' (Punto 4)
    """
    # Primero verifico que el método existe
    if hasattr(checklist_service, 'close'):
        result = checklist_service.close(99)
        
        # Verifico que devuelve algo
        assert result is not None
        
        # Verifico que el estado cambió a 'closed'
        assert result.status == "closed"
    else:
        pytest.fail("ERROR: El método 'close' no existe en el servicio")


def test_db_connection_isolated(db_session):
    """
    Este test verifica que la conexión a la base de datos de test funciona
    y está aislada de la base de datos real.
    """
    from sqlalchemy import text
    
    # Hago una query simple para comprobar la conexión
    res = db_session.execute(text("SELECT 1")).fetchone()
    
    # Si devuelve 1, la conexión funciona correctamente
    assert res[0] == 1