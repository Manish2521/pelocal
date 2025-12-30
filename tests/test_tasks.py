from app import app

def test_get_tasks():
    client = app.test_client()
    res = client.get("/api/tasks")
    assert res.status_code == 200

def test_create_task():
    client = app.test_client()
    res = client.post("/api/tasks", json={"title": "Test Task"})
    assert res.status_code == 201
