import app.database as dbmod


def test_get_db_closes_session(monkeypatch):
    closed = {"value": False}

    class DummySession:
        def close(self):
            closed["value"] = True

    def fake_sessionlocal():
        return DummySession()

    monkeypatch.setattr(dbmod, "SessionLocal", fake_sessionlocal)

    gen = dbmod.get_db()
    sess = next(gen)
    assert isinstance(sess, DummySession)

    gen.close()

    assert closed["value"] is True
