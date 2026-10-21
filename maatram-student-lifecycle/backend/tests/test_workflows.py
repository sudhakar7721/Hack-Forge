import os
os.environ["DATABASE_URL"] = "sqlite:///./test_maatram.db"
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def setup_cycle():
    cycles = client.get("/api/cycles").json()
    if cycles: return cycles[0]["id"]
    return client.post("/api/cycles", json={"name":"Demo Cycle 2026","year":2026,"active":True}).json()["id"]

def test_admission_select_and_linked_student():
    cycle = setup_cycle()
    a = client.post("/api/applications", json={"cycle_id":cycle,"applicant_name":"Demo Applicant","email":"demo@example.test","status":"submitted"}).json()
    assert a["status"] == "submitted"
    res = client.post("/api/applications/bulk-review", json={"application_ids":[a["id"]],"action":"select"})
    assert res.status_code == 200
    selected = res.json()["applications"][0]
    assert selected["student_id"] is not None
    assert client.get("/api/students").status_code == 200

def test_duplicate_event_is_idempotent():
    students = client.get("/api/students").json()
    if not students:
        test_admission_select_and_linked_student()
        students = client.get("/api/students").json()
    sid = students[0]["id"]
    body = {"event_id":"test-event-unique-001","student_id":sid,"event_type":"TestEvent","occurred_at":"2026-01-01T10:00:00","payload":{"status":"ok"}}
    first = client.post("/api/events", json=body)
    second = client.post("/api/events", json=body)
    assert first.status_code == 200 and second.status_code == 200
    assert second.json()["duplicate"] is True

def test_upload_rejects_oversized_file():
    response = client.post("/api/uploads/presign", json={"owner_type":"application","owner_id":1,"filename":"big.pdf","content_type":"application/pdf","size_bytes":999999999})
    assert response.status_code == 413
