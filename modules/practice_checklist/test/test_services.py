import pytest
from modules.practice_checklist.services.checklist import (
    PracticeChecklistService,
    PracticeChecklistItemService,
)

# Test crear checklist
def test_create_checklist(db_session):
    service = PracticeChecklistService(db_session)

    checklist = service.create({
        "name": "Checklist test"
    })

    assert checklist["status"] == "open"
    assert checklist["name"] == "Checklist test"

# Test cerrar checklist
def test_close_checklist(db_session):
    service = PracticeChecklistService(db_session)

    checklist = service.create({"name": "Checklist test"})
    result = service.close(checklist["id"])

    assert result["status"] == "closed"
    assert result["closed_at"] is not None

# Test reabrir checklist
def test_reopen_checklist(db_session):
    service = PracticeChecklistService(db_session)

    checklist = service.create({"name": "Checklist test"})
    service.close(checklist["id"])

    reopened = service.reopen(checklist["id"])

    assert reopened["status"] == "open"
    assert reopened["closed_at"] is None

# Test marcar un item como hecho
def test_set_done_item(db_session):
    checklist_service = PracticeChecklistService(db_session)
    item_service = PracticeChecklistItemService(db_session)

    checklist = checklist_service.create({"name": "Checklist test"})

    item = item_service.create({
        "title": "Tarea de prueba",
        "checklist_id": checklist["id"]
    })

    result = item_service.set_done(id=item["id"], done=True)

    assert len(result) == 1
    assert result[0]["is_done"] is True

# Test marcar varios items como hechos (bulk action)
def test_set_done_bulk_items(db_session):
    checklist_service = PracticeChecklistService(db_session)
    item_service = PracticeChecklistItemService(db_session)

    checklist = checklist_service.create({"name": "Checklist test"})

    item1 = item_service.create({"title": "Item 1", "checklist_id": checklist["id"]})
    item2 = item_service.create({"title": "Item 2", "checklist_id": checklist["id"]})

    result = item_service.set_done(ids=[item1["id"], item2["id"]], done=True)

    assert len(result) == 2
    assert all(r["is_done"] for r in result)