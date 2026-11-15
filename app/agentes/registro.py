"""Registro de agentes locales. Cada agente es un agente ReAct de LangChain con su prompt y sus herramientas.

El agente usa el modelo (Claude) y un checkpointer en memoria: el `thread_id` es el contextId A2A,
así cada conversación conserva su memoria por agente.
"""
from dataclasses import dataclass, field

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from app import config
from app.costos import AVISO_TRUNCADO, VentanaMensajes, registrar_uso_turno, truncado
from app.agentes.alejandra import herramientas as h_ale, prompts as p_ale

@dataclass
class AgenteDef:
    id: str                      # graph id / nombre en la Agent Card
    nombre: str                  # nombre de la persona que representa
    especialidad: str            # una línea para el selector y el enrutador
    descripcion: str             # descripción larga (Agent Card)
    skills: list[tuple]          # (id, nombre, descripción, tags, ejemplos)
    ejemplos: list[str]
    herramientas: list
    system_prompt: str
    autor: str = ""
    grafo: object = field(default=None, repr=False)


AGENTES_DEF: list[AgenteDef] = [
    AgenteDef(
        id=config.AGENT_ID, nombre="Alejandra Ubilla", autor="Alejandra Ubilla",
        especialidad="auditoría de cumplimiento normativo y tributario (CMF y SII)",
        descripcion=(
            "agente-ale-ubi · la auditora de la red: revisa si una empresa o un fondo de inversión cumple la normativa "
            "chilena, cruzando SII y CMF, y te dice qué mirar primero. Rigurosa, directa y paciente; explica con ejemplos "
            "concretos y cita la fuente o norma exacta de cada dato (NCG 461, NCG 365).\n"
            "DERÍVAME: ¿cumple la empresa X (RUT)? · estado tributario o sanciones de un RUT · concentración, TER y "
            "rentabilidad neta de un fondo · checklist de auditoría para una SA, SpA o Ltda, o para un fondo "
            "accionario, de deuda o inmobiliario.\n"
            "NO ME DERIVES: asesoría tributaria personal, legal o de inversión, ni nada ajeno a la auditoría "
            "(lo rechazo con amabilidad y te lo digo).\n"
            "ALCANCE: solo recomienda; no ejecuta acciones correctivas, no informa a organismos ni presenta "
            "declaraciones. Nunca inventa cifras: todo dato sale de una herramienta, y si falta uno (RUT, nombre del "
            "fondo, tipo de empresa o de fondo) lo pregunta antes de concluir. Conserva cifras, unidades y fechas tal cual. "
            "DATOS SIMULADOS para demostración."),
        skills=[
            ("estado-tributario-sii", "Estado tributario SII",
             "Consulta por RUT el estado de actividad, si las declaraciones de renta/IVA están al día, la fecha de la "
             "última declaración y las observaciones vigentes; señala atrasos. Datos simulados.",
             ["sii", "tributario", "rut"], ["¿Qué observaciones tiene en el SII el RUT 77.987.654-3?"]),
            ("cumplimiento-cruzado-cmf-sii", "Cumplimiento cruzado CMF + SII",
             "Cruza SII y CMF para determinar si una empresa cumple (declaraciones al día, sin sanciones ni observaciones) "
             "y devuelve alertas y normativa aplicable (p. ej. NCG 461). Solo recomienda el siguiente paso.",
             ["cmf", "sii", "cumplimiento"],
             ["¿Cumple con la normativa la empresa 77.987.654-3?", "¿Tiene sanciones vigentes en la CMF el RUT 78.555.111-2?"]),
            ("auditoria-fondos", "Auditoría de fondos de inversión",
             "Revisa un fondo: concentración por emisor vs. límite NCG 365 (20%), TER y rentabilidad neta estimada "
             "(rentabilidad 12m - TER), y genera el checklist según tipo (accionario, deuda, inmobiliario).",
             ["fondos", "ncg-365", "ratios"],
             ["Revisa el cumplimiento normativo del fondo FM Inmobiliario", "Calcula los ratios de FM Deuda Privada"]),
            ("checklist-empresa", "Checklist de auditoría de empresa",
             "Genera el checklist de cumplimiento administrativo y contable según el tipo de empresa: sa, spa o ltda.",
             ["checklist", "auditoria"], ["Dame el checklist de auditoría para una SpA"]),
        ],
        ejemplos=["¿Cumple con la normativa la empresa 77.987.654-3?", "Revisa la concentración del fondo FM Inmobiliario"],
        herramientas=h_ale.HERRAMIENTAS, system_prompt=p_ale.SYSTEM_PROMPT,
    ),
]

AGENTES: dict[str, AgenteDef] = {a.id: a for a in AGENTES_DEF}


def construir_agentes(checkpointer=None) -> None:
    """Crea el grafo ReAct de cada agente (no hace llamadas de red). Sin checkpointer usa memoria."""
    checkpointer = checkpointer or InMemorySaver()
    modelo = ChatAnthropic(model=config.MODELO, max_retries=2, timeout=60, max_tokens=config.MAX_TOKENS)
    # Ahorro de tokens: ventana de historial + caché del prompt de sistema (ver app/costos.py).
    middleware = [VentanaMensajes(config.HISTORIAL_MAX_MENSAJES)]
    if config.PROMPT_CACHE:
        middleware.append(AnthropicPromptCachingMiddleware(ttl="5m", unsupported_model_behavior="ignore"))
    for a in AGENTES_DEF:
        a.grafo = create_agent(model=modelo, tools=a.herramientas, system_prompt=a.system_prompt,
                               checkpointer=checkpointer, name=a.id, middleware=middleware)


def texto(msg) -> str:
    """El contenido puede venir como lista de partes; se aplana a texto."""
    c = msg.content
    return c if isinstance(c, str) else " ".join(p.get("text", "") for p in c if isinstance(p, dict))


async def responder(agente_id: str, mensaje: str, thread_id: str) -> str:
    a = AGENTES[agente_id]
    cfg = {"configurable": {"thread_id": thread_id}, "recursion_limit": 12}  # tope de ciclo
    r = await a.grafo.ainvoke({"messages": [{"role": "user", "content": mensaje}]}, cfg)
    registrar_uso_turno(agente_id, thread_id, r["messages"])
    final = r["messages"][-1]
    return texto(final) + (AVISO_TRUNCADO if truncado(final) else "")      # nunca presentar una respuesta cortada como completa
