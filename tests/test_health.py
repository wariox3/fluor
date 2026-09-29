from sqlalchemy.exc import OperationalError


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_db_caida(client, monkeypatch):
    class EngineCaido:
        def connect(self):
            raise OperationalError("SELECT 1", {}, Exception("sin conexión"))

    monkeypatch.setattr("app.main.master_engine", EngineCaido())
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["database"] == "unreachable"
