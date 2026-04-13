import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

# Importamos el modelo y el servicio que vamos a probar
from ..models.suggestion import Suggestion
from ..services.suggestion import SuggestionService


@pytest.fixture
def mock_service():
    """
    Fixture de pytest que crea una instancia del servicio
    utilizando un repositorio simulado (MagicMock) en lugar
    de una base de datos real.

    Esto permite hacer tests unitarios sin depender de la BD.
    """
    # Creamos un repositorio falso
    mock_repo = MagicMock()
    mock_repo.session = MagicMock()

    # Inyectamos el repositorio falso en el servicio
    service = SuggestionService(mock_repo)

    return service


def test_publish_suggestion_success(mock_service):
    """
    Caso: Publicar una sugerencia en estado 'pending'.

    Verificamos que:
    - Cambia el estado a 'published'
    - Se hace pública
    - Se guarda la nota de moderación
    - Se establece la fecha de publicación
    """
    # Simulamos una sugerencia pendiente
    mock_suggestion = Suggestion(id=1, status="pending", is_public=False)
    mock_service.repo.session.get.return_value = mock_suggestion

    # Ejecutamos la acción
    mock_service.publish(id=1, note="Buena idea")

    # Verificamos cambios
    assert mock_suggestion.status == "published"
    assert mock_suggestion.is_public is True
    assert mock_suggestion.moderation_note == "Buena idea"
    assert mock_suggestion.published_at is not None


def test_publish_already_published_raises_error(mock_service):
    """
    Caso defensivo: Intentar publicar una sugerencia que ya
    está publicada debe lanzar un error HTTP 400.
    """
    mock_suggestion = Suggestion(id=2, status="published", is_public=True)
    mock_service.repo.session.get.return_value = mock_suggestion

    # Esperamos una excepción
    with pytest.raises(HTTPException) as exc_info:
        mock_service.publish(id=2)

    # Validamos el error
    assert exc_info.value.status_code == 400
    assert "ya está publicada" in exc_info.value.detail


def test_reject_suggestion(mock_service):
    """
    Caso: Rechazar una sugerencia pendiente.

    Verificamos que:
    - Cambia el estado a 'rejected'
    - No es pública
    - Guarda la nota de moderación
    """
    mock_suggestion = Suggestion(id=3, status="pending", is_public=False)
    mock_service.repo.session.get.return_value = mock_suggestion

    # Ejecutamos la acción de rechazo
    mock_service.reject(id=3, note="No es viable")

    # Validamos cambios
    assert mock_suggestion.status == "rejected"
    assert mock_suggestion.is_public is False
    assert mock_suggestion.moderation_note == "No es viable"


def test_merge_suggestion_with_itself_raises_error(mock_service):
    """
    Caso defensivo: No se puede fusionar una sugerencia consigo misma.
    Debe lanzar un error HTTP 400.
    """
    mock_suggestion = Suggestion(id=4, status="pending")

    # El mock devuelve la misma sugerencia para cualquier ID
    mock_service.repo.session.get.return_value = mock_suggestion

    with pytest.raises(HTTPException) as exc_info:
        mock_service.merge(id=4, target_id=4)

    assert exc_info.value.status_code == 400
    assert "No puedes fusionar una sugerencia consigo misma" in exc_info.value.detail


def test_reopen_suggestion(mock_service):
    """
    Caso: Reabrir una sugerencia rechazada o publicada.

    Verificamos que:
    - Vuelve a estado 'pending'
    - No es pública
    - Se eliminan la nota de moderación y la fecha de publicación
    """
    mock_suggestion = Suggestion(
        id=5,
        status="rejected",
        is_public=False,
        moderation_note="spam",
        published_at="2024-01-01"
    )
    mock_service.repo.session.get.return_value = mock_suggestion

    # Ejecutamos la acción de reabrir
    mock_service.reopen(id=5)

    # Validamos cambios
    assert mock_suggestion.status == "pending"
    assert mock_suggestion.is_public is False
    assert mock_suggestion.moderation_note is None
    assert mock_suggestion.published_at is None