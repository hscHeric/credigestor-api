import app.main as mainmod


def test_root_endpoint(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "CrediGestor API"
    assert "environment" in body
    assert "docs" in body


def test_health_connected(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("healthy", "degraded")
    assert "database" in body


def test_health_disconnected_branch(monkeypatch, client):
    class DummyEngine:
        def connect(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(mainmod, "engine", DummyEngine())

    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "degraded"
    assert body["database"].startswith("disconnected:")


def test_lifespan_exception_branch(monkeypatch):
    """
    Cobre o except do lifespan (Base.metadata.create_all levantando erro).
    """
    import app.main as m

    class DummyMeta:
        def create_all(self, bind):
            raise RuntimeError("create_all failed")

    class DummyBase:
        metadata = DummyMeta()

    monkeypatch.setattr(m, "Base", DummyBase)

    import asyncio

    async def run():
        cm = m.lifespan(m.app)
        await cm.__aenter__()
        await cm.__aexit__(None, None, None)

    asyncio.run(run())
