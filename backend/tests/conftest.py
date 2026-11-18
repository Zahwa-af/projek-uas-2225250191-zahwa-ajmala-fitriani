import pytest


@pytest.fixture(autouse=True)
def tanpa_deepseek_sungguhan(monkeypatch):
    """Tes TIDAK PERNAH memanggil API DeepSeek sungguhan, walaupun .env berisi API key."""
    monkeypatch.setenv("SEGIPINTAR_ASISTEN", "mati")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
