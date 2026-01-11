import time
from app.utils.rate_limit import SimpleRateLimiter

def test_rate_limit_hits_block_and_reset(monkeypatch):
    # Mock do tempo
    now = {"t": 1000.0}
    monkeypatch.setattr(time, "time", lambda: now["t"])

    # Instancia com os parâmetros corretos
    limiter = SimpleRateLimiter(max_attempts=2, window_seconds=5)

    assert limiter.allow("user_1") is True
    assert limiter.allow("user_1") is True
    assert limiter.allow("user_1") is False

    # Avança o tempo além da janela (5s) para cobrir o reset (popleft)
    now["t"] += 6.0
    
    assert limiter.allow("user_1") is True

def test_rate_limit_different_keys(monkeypatch):
    now = {"t": 1000.0}
    monkeypatch.setattr(time, "time", lambda: now["t"])

    limiter = SimpleRateLimiter(max_attempts=1, window_seconds=5)

    assert limiter.allow("user_1") is True
    assert limiter.allow("user_1") is False
    # Outro usuário não é afetado
    assert limiter.allow("user_2") is True