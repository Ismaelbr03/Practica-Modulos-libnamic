import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

# Importamos únicamente el servicio que queremos probar
from modules.community_events.services.registration import RegistrationService


@pytest.fixture
def mock_service():
    """
    Fixture que crea una instancia del servicio con un repositorio simulado.
    Esto nos permite aislar la lógica del servicio sin depender de la base de datos.
    """
    # Creamos un mock del repositorio
    repo_mock = MagicMock()
    
    # Simulamos el atributo session que normalmente proporciona acceso a la DB
    repo_mock.session = MagicMock()
    
    # Devolvemos el servicio inicializado con el repositorio falso
    return RegistrationService(repo_mock)


def test_registration_closed_event_raises_error(mock_service):
    """
    Este test valida que el sistema NO permita crear una inscripción
    si el evento no está publicado (por ejemplo, en estado 'draft').
    """

    # ======================
    # ARRANGE (Preparación)
    # ======================

    # Creamos un evento simulado
    event = MagicMock()
    
    # Definimos sus atributos mínimos necesarios
    event.id = 1
    event.status = "draft"  # Estado no permitido para inscripciones
    event.capacity_total = 2

    # Configuramos el mock para que cuando el servicio busque el evento,
    # reciba nuestro objeto simulado en lugar de consultar la base de datos
    mock_service.repo.session.get.return_value = event

    # ======================
    # ACT + ASSERT
    # ======================

    # Intentamos crear la inscripción esperando que falle
    with pytest.raises(HTTPException) as error:
        mock_service.create({
            "event_id": 1,
            "attendee_name": "Ismael Ismael",
            "attendee_email": "ismael@test.com"
        })

    # ======================
    # ASSERT (Validaciones)
    # ======================

    # Verificamos que el código de error HTTP sea 400 (Bad Request)
    assert error.value.status_code == 400

    # Comprobamos que el mensaje de error menciona el estado
    assert "estado" in error.value.detail.lower()

    # Comprobamos que el estado específico ('draft') aparece en el mensaje
    assert "draft" in error.value.detail.lower()


def test_registration_waitlist_logic(mock_service):
    """
    Este test comprueba que cuando un evento ya está lleno,
    las nuevas inscripciones se asignan automáticamente a 'waitlist'.
    """

    # ======================
    # ARRANGE (Preparación)
    # ======================

    # Creamos un evento simulado ya publicado
    event = MagicMock()
    event.id = 1
    event.status = "published"  # Estado válido
    event.capacity_total = 1    # Capacidad máxima muy baja (1 persona)

    # Simulamos que ya existe una inscripción confirmada,
    # lo que implica que el evento ya está lleno
    mock_service.repo.session.scalars().all.return_value = [MagicMock()]

    # Configuramos el mock para devolver el evento al consultarlo
    mock_service.repo.session.get.return_value = event

    # Datos de la nueva inscripción
    payload = {
        "event_id": 1,
        "attendee_name": "Esteban",
        "attendee_email": "Esteban@test.com"
    }

    # ======================
    # ACT (Ejecución)
    # ======================

    # Ejecutamos la lógica del servicio
    # NOTA: usamos try/except porque probablemente falle al intentar
    # persistir en la base de datos (que no existe en este test)
    try:
        mock_service.create(payload)
    except:
        # Ignoramos cualquier excepción ya que solo nos interesa
        # validar la lógica previa (asignación de estado)
        pass

    # ======================
    # ASSERT (Validación)
    # ======================

    # Verificamos que el servicio haya modificado el payload
    # asignando el estado 'waitlist' automáticamente
    assert payload.get("status") == "waitlist"