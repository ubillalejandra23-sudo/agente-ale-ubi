"""mi-agente (Alejandra · auditoría CMF/SII): un agente A2A autónomo sobre FastAPI. Swagger en `/docs`.

  GET  /salud                          estado del servicio (público)
  GET  /.well-known/agent-card.json    ficha A2A (pública)
  POST /a2a                            A2A message/send (protegido con X-API-Key)
  POST /chat                           consulta directa (protegido con X-API-Key)
"""
import logging
import uuid
from contextlib import asynccontextmanager

from a2a.server.routes import fastapi_routes
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app import config
from app.a2a_server import es_ruta_rpc, rutas_a2a
from app.agentes.registro import construir_agentes, responder
from app.security import clave_valida, exigir_clave, extraer_clave

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("api")


class ChatIn(BaseModel):
    mensaje: str = Field(
        ..., min_length=1, max_length=4000,
        description="Consulta en lenguaje natural (máx. 4000 caracteres). Incluya el dato que necesita el agente "
                    "(RUT de la empresa 12.345.678-9, nombre del fondo, etc.). Si falta, el agente lo pedirá.",
        examples=["¿Cumple con la normativa la empresa 77.987.654-3?"])
    conversation_id: str | None = Field(
        None, max_length=100, pattern=r"^[A-Za-z0-9_\-:.]+$",
        description="Identificador de la conversación. Reutilícelo para que el agente recuerde el contexto. "
                    "Si se omite, se crea una conversación nueva y se devuelve su id.",
        examples=["auditoria-andina-001"])


class ChatOut(BaseModel):
    respuesta: str = Field(..., description="Respuesta del agente.")
    conversation_id: str = Field(..., description="Id de la conversación; envíelo de vuelta para continuarla.")
    agente: str = Field(..., description="Agente que respondió.")


class SaludOut(BaseModel):
    status: str = Field(..., examples=["ok"])
    agente: str = Field(..., examples=["mi-agente"])
    acceso_configurado: bool = Field(..., description="False si el servidor no tiene API_KEYS (rechazará todo con 503).")
    url_publica: str = Field(..., description="Dirección que publica la ficha del agente (URL_PUBLICA).")


class ErrorOut(BaseModel):
    detail: str


DESCRIPCION = """
## mi-agente · Auditoría de cumplimiento normativo y tributario (CMF y SII)

Agente de IA **autónomo** que se publica como servicio **A2A**: un coordinador (u otro agente) lee su ficha y le pasa
las preguntas de su especialidad.

| Qué hace | Qué NO hace |
|---|---|
| Estado tributario SII por RUT, cruce SII + CMF, auditoría de fondos (NCG 365, TER), checklists de auditoría | Asesoría tributaria personal, legal o de inversión; ejecutar acciones o informar a organismos; temas ajenos a la auditoría (los rechaza con amabilidad) |

Los datos de SII/CMF/fondos son **simulados**. El agente solo recomienda el siguiente paso.

### Acceso
* **Públicos:** `GET /salud` y `GET /.well-known/agent-card.json`.
* **Con clave** (`X-API-Key: <clave>` o `Authorization: Bearer <clave>`): `POST /a2a` y `POST /chat`.
  Sin clave → `401`; servidor sin claves configuradas → `503` (falla cerrado).

### Códigos de error
`401` clave ausente/inválida · `422` entrada inválida · `429` demasiadas consultas · `502` falla del proveedor · `503` acceso no configurado.
"""

TAGS = [
    {"name": "Estado", "description": "Salud del servicio. Público, sin datos sensibles."},
    {"name": "Agente", "description": "Consulta directa al agente. **Requiere clave.** Memoria por `conversation_id`."},
    {"name": "A2A: Agent Card", "description": "Ficha pública del agente (habilidades, límites, URL y seguridad)."},
    {"name": "A2A: JSON-RPC", "description": "Endpoint A2A (`message/send`). **Requiere clave** (`X-API-Key`)."},
]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    construir_agentes()   # memoria de conversación en el proceso (checkpointer en memoria)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="mi-agente · Auditoría CMF/SII",
    version="3.0.0",
    summary="Agente A2A autónomo de auditoría, con ficha pública, /salud y acceso por clave",
    description=DESCRIPCION, openapi_tags=TAGS, contact={"name": "Alejandra Ubilla"},
)
construir_agentes()
cards, rpc = rutas_a2a()


@app.middleware("http")
async def proteger_a2a(request: Request, call_next):
    """El endpoint JSON-RPC A2A exige la misma clave que /chat (la ficha y /salud quedan públicas)."""
    if es_ruta_rpc(request.url.path):
        if not config.API_KEYS:
            return JSONResponse({"detail": "Acceso deshabilitado: API_KEYS no configuradas."}, status_code=503)
        if not clave_valida(extraer_clave(request)):
            log.warning("A2A rechazado: clave ausente o inválida")
            return JSONResponse({"detail": "Clave de acceso ausente o inválida."}, status_code=401,
                                headers={"WWW-Authenticate": "Bearer"})
        log.info("A2A recibido rid=%s", request.headers.get("x-request-id", "-"))
    return await call_next(request)


@app.get("/salud", tags=["Estado"], response_model=SaludOut, summary="Estado del servicio",
         description="Indica si el servicio está en línea y si tiene claves configuradas. No requiere clave y no "
                     "expone datos sensibles.")
async def salud():
    return {"status": "ok", "agente": config.AGENT_ID, "acceso_configurado": bool(config.API_KEYS),
            "url_publica": config.URL_PUBLICA}


@app.post("/chat", response_model=ChatOut, tags=["Agente"], dependencies=[Depends(exigir_clave)],
          summary="Consultar al agente",
          description="Envía una consulta al agente, que decide qué herramientas usar y responde en español. Si falta un "
                      "dato lo pregunta en vez de inventarlo; si el tema no es de su área lo rechaza con amabilidad. "
                      "Reenvíe el `conversation_id` recibido para continuar la conversación.",
          responses={401: {"model": ErrorOut, "description": "Clave ausente o inválida."},
                     422: {"description": "Entrada inválida (mensaje vacío o muy largo, id con caracteres no permitidos)."},
                     429: {"model": ErrorOut, "description": "Límite de consultas por minuto excedido."},
                     502: {"model": ErrorOut, "description": "Falló el proveedor del modelo; la consulta NO se realizó."},
                     503: {"model": ErrorOut, "description": "El servidor no tiene API_KEYS configuradas."}})
async def chat(body: ChatIn):
    cid = body.conversation_id or uuid.uuid4().hex
    log.info("chat conversation=%s chars=%d", cid, len(body.mensaje))
    try:
        return ChatOut(respuesta=await responder(config.AGENT_ID, body.mensaje, cid), conversation_id=cid,
                       agente=config.AGENT_ID)
    except Exception as e:  # falla del proveedor del modelo / límite del agente: nunca como éxito
        log.exception("fallo del agente")
        raise HTTPException(502, f"El agente no pudo responder ({type(e).__name__}). Intente de nuevo.") from e


fastapi_routes.add_a2a_routes_to_fastapi(app, agent_card_routes=cards, jsonrpc_routes=rpc)
