"""Pruebas de la ficha, el acceso, la validación y la herramienta (no llaman al modelo)."""
import importlib
import uuid

from fastapi.testclient import TestClient

from app import config, security
from app.agentes.alejandra import herramientas
from app.main import app

client = TestClient(app)
OK = {"X-API-Key": "clave-de-prueba"}


def jsonrpc(texto, ctx=None):
    return {"jsonrpc": "2.0", "id": "1", "method": "message/send", "params": {"message": {
        "role": "user", "messageId": uuid.uuid4().hex, "contextId": ctx or str(uuid.uuid4()),
        "parts": [{"kind": "text", "text": texto}]}}}


# ── público ──
def test_salud_publica():
    j = client.get("/salud").json()
    assert j["status"] == "ok" and j["agente"] == "agente-ale-ubi" and j["acceso_configurado"] is True
    assert j["url_publica"] == config.URL_PUBLICA


def test_swagger_y_rutas():
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    for p in ("/salud", "/chat", "/a2a", "/.well-known/agent-card.json"):
        assert p in paths


# ── ficha ──
def test_ficha_publica_dice_que_hace_y_que_no_y_declara_seguridad():
    card = client.get("/.well-known/agent-card.json").json()
    assert card["name"] == "agente-ale-ubi" and card["skills"] and "apiKey" in card["securitySchemes"]
    assert "ALCANCE" in card["description"] and "no ejecuta" in card["description"]
    assert card["supportedInterfaces"][0]["url"] == f"{config.URL_PUBLICA}/a2a"


def test_la_ficha_publica_la_url_publica_configurada(monkeypatch):
    monkeypatch.setenv("URL_PUBLICA", "https://agente-ale-ubi.example.com/")
    try:
        assert importlib.reload(config).URL_PUBLICA == "https://agente-ale-ubi.example.com"
    finally:
        monkeypatch.undo()
        importlib.reload(config)


# ── acceso ──
def test_chat_rechaza_sin_clave_o_con_clave_falsa():
    assert client.post("/chat", json={"mensaje": "hola"}).status_code == 401
    assert client.post("/chat", json={"mensaje": "hola"}, headers={"X-API-Key": "mala"}).status_code == 401


def test_a2a_sin_clave_rechazado():
    assert client.post("/a2a", json=jsonrpc("hola")).status_code == 401
    assert client.post("/a2a", json=jsonrpc("hola"), headers={"X-API-Key": "mala"}).status_code == 401


def test_falla_cerrado_sin_claves_en_servidor(monkeypatch):
    monkeypatch.setattr(config, "API_KEYS", [])
    assert client.post("/chat", json={"mensaje": "hola"}, headers=OK).status_code == 503
    assert client.post("/a2a", json=jsonrpc("hola"), headers=OK).status_code == 503


def test_limite_de_consultas_por_minuto(monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT_PER_MIN", 2)
    security._ventanas.clear()
    codigos = [client.post("/chat", json={"mensaje": ""}, headers=OK).status_code for _ in range(3)]
    assert codigos == [422, 422, 429]  # las dos primeras pasan el acceso (fallan en validación); la tercera se limita
    security._ventanas.clear()


# ── validación ──
def test_entradas_invalidas():
    security._ventanas.clear()
    assert client.post("/chat", json={"mensaje": ""}, headers=OK).status_code == 422
    assert client.post("/chat", json={"mensaje": "x" * 5000}, headers=OK).status_code == 422
    assert client.post("/chat", json={"mensaje": "hola", "conversation_id": "a b/../"}, headers=OK).status_code == 422


# ── herramientas con datos (no respuestas inventadas) ──
def test_el_agente_tiene_herramientas_con_datos():
    assert len(herramientas.HERRAMIENTAS) >= 1


def test_la_clave_de_ejemplo_publica_no_se_acepta(monkeypatch):
    """Quien copie .env.example y olvide cambiar API_KEYS no debe dejar la API abierta con una clave pública."""
    monkeypatch.setenv("API_KEYS", "clave-ficticia-cambiar-por-una-larga-y-aleatoria")
    try:
        c = importlib.reload(config)
        assert c.API_KEYS == []                                  # -> el servidor responde 503 (falla cerrado)
        monkeypatch.setenv("API_KEYS", "clave-ficticia-cambiar-por-una-larga-y-aleatoria, mi-clave-real-larga")
        assert importlib.reload(config).API_KEYS == ["mi-clave-real-larga"]
    finally:
        monkeypatch.undo()
        importlib.reload(config)


def test_ficha_visual_publica_sin_secretos():
    r = client.get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    assert "Qué NO hace" in r.text and "consultar_cmf" in r.text and "/.well-known/agent-card.json" in r.text
    assert "clave-de-prueba" not in r.text and "sk-ant" not in r.text
