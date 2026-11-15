"""Servidor A2A (SDK oficial a2a-sdk) montado dentro de FastAPI.

  GET  /.well-known/agent-card.json   Ficha del agente (pública: qué hace, qué no y cómo autenticarse)
  POST /a2a                           JSON-RPC (message/send, ...) -> protegido con la clave
"""
import logging

from a2a.helpers.proto_helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (AgentCapabilities, AgentCard, AgentInterface, AgentProvider, AgentSkill, APIKeySecurityScheme,
                       SecurityRequirement, SecurityScheme)

from app import config
from app.agentes.registro import AGENTES, AgenteDef, responder

log = logging.getLogger("a2a")
RPC_PATH = "/a2a"
CARD_PATH = "/.well-known/agent-card.json"


class AgenteExecutor(AgentExecutor):
    def __init__(self, agente_id: str):
        self.agente_id = agente_id

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        pregunta = context.get_user_input().strip()
        cid = context.context_id or context.task_id or "a2a-sin-contexto"
        if not pregunta:
            await event_queue.enqueue_event(new_text_message(
                "No recibí texto en el mensaje. Envía una consulta.", context_id=cid))
            return
        log.info("A2A ejecuta agente=%s context=%s chars=%d", self.agente_id, cid, len(pregunta))
        try:
            texto = await responder(self.agente_id, pregunta, cid)
        except Exception as e:  # falla del proveedor: el SDK la convierte en error JSON-RPC, no en éxito
            log.exception("fallo del agente %s", self.agente_id)
            raise RuntimeError(f"El agente no pudo responder ({type(e).__name__}).") from e
        await event_queue.enqueue_event(new_text_message(texto, context_id=cid))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Este agente responde de forma inmediata; no hay tareas que cancelar.")


def construir_card(a: AgenteDef, rpc_path: str) -> AgentCard:
    return AgentCard(
        name=a.id,
        description=a.descripcion + " Acceso: enviar la clave en la cabecera X-API-Key. Envíe texto en español; use un "
                                    "contextId fijo por conversación para que recuerde el contexto.",
        version="2.0.0",
        documentation_url=f"{config.URL_PUBLICA}/docs",
        provider=AgentProvider(organization=f"{a.autor} · Taller Agentic AI", url=config.URL_PUBLICA),
        supported_interfaces=[AgentInterface(url=f"{config.URL_PUBLICA}{rpc_path}", protocol_binding="JSONRPC",
                                             protocol_version="1.0")],
        capabilities=AgentCapabilities(streaming=False, push_notifications=False),
        default_input_modes=["text/plain"], default_output_modes=["text/plain"],
        skills=[AgentSkill(id=i, name=n, description=d, tags=t, examples=e) for i, n, d, t, e in a.skills],
        security_schemes={"apiKey": SecurityScheme(api_key_security_scheme=APIKeySecurityScheme(
            location="header", name="X-API-Key",
            description="Clave de acceso configurada en el servidor (API_KEYS). Se solicita al administrador del servicio."))},
        security_requirements=[SecurityRequirement(schemes={"apiKey": {}})],
    )


def rutas_a2a() -> tuple[list, list]:
    """Devuelve (rutas de la Agent Card, rutas JSON-RPC) del agente: /.well-known/agent-card.json y /a2a."""
    a = AGENTES[config.AGENT_ID]
    card = construir_card(a, RPC_PATH)
    handler = DefaultRequestHandler(agent_executor=AgenteExecutor(a.id), task_store=InMemoryTaskStore(), agent_card=card)
    return (create_agent_card_routes(card, card_url=CARD_PATH),
            create_jsonrpc_routes(handler, rpc_url=RPC_PATH, enable_v0_3_compat=True))


def es_ruta_rpc(path: str) -> bool:
    return path.rstrip("/") == RPC_PATH
