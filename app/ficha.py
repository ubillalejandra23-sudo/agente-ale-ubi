"""Ficha visual pública del agente (GET /). Se genera con los mismos datos que la Agent Card A2A.

Es solo presentación: la ficha que leen los coordinadores sigue siendo /.well-known/agent-card.json.
No muestra claves ni datos sensibles.
"""
from html import escape as e

from app import config
from app.agentes.registro import AGENTES

HACE = [
    ("Estado tributario SII", "Por RUT: actividad, declaraciones de renta/IVA al día y observaciones vigentes."),
    ("Cumplimiento cruzado CMF + SII", "Cruza ambas fuentes y alerta atrasos, sanciones y normativa aplicable (NCG 461)."),
    ("Auditoría de fondos", "Concentración por emisor vs. límite NCG 365 (20%), TER y rentabilidad neta estimada."),
    ("Checklists de auditoría", "Por tipo de empresa (SA, SpA, Ltda) o de fondo (accionario, deuda, inmobiliario)."),
]
NO_HACE = [
    "Ejecutar acciones correctivas ni informar a la CMF o al SII",
    "Dar asesoría tributaria personal, legal o de inversión",
    "Responder temas ajenos a la auditoría (los rechaza con amabilidad)",
    "Inventar cifras: todo dato sale de una herramienta, y si falta uno lo pregunta",
]
HERRAMIENTAS = ["consultar_sii", "consultar_cmf", "verificar_cumplimiento_contable", "consultar_fondo",
                "revisar_cumplimiento_normativo", "calcular_ratios_fondo", "generar_checklist_auditoria",
                "generar_checklist_cumplimiento_empresa", "consultar_mis_apuntes"]

CSS = """
:root{--bg:#fdf6f9;--card:#fff;--tx:#2a1620;--mut:#7a5c69;--rosa:#be3a6e;--rosa2:#e0709a;--suave:#fbe3ec;--ok:#1f8a5b;
--okbg:#e3f5ec;--no:#b4412f;--nobg:#fdeae6;--bd:#f0d3de;--code:#3b2430}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#1b1015;--card:#26171e;--tx:#f6e9ef;--mut:#c4a3b3;
--rosa:#ef7fa8;--rosa2:#be3a6e;--suave:#3a2230;--ok:#6fd3a4;--okbg:#17302a;--no:#ff9c8a;--nobg:#3a201c;--bd:#40262f;--code:#f1d9e4}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.55 system-ui,Segoe UI,Roboto,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:0 16px 48px}
header{background:linear-gradient(135deg,var(--rosa),var(--rosa2));color:#fff;padding:36px 0 56px}
header .wrap{display:flex;gap:20px;align-items:center;flex-wrap:wrap}
.logo{width:72px;height:72px;border-radius:20px;background:rgba(255,255,255,.18);display:grid;place-items:center;font-weight:800;
font-size:22px;letter-spacing:1px;border:2px solid rgba(255,255,255,.5)}
h1{margin:0;font-size:clamp(24px,5vw,34px);line-height:1.15}header p{margin:6px 0 0;opacity:.95;max-width:60ch}
.pills{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.pill{background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.4);border-radius:999px;padding:3px 12px;font-size:13px}
main{margin-top:-32px}
section{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:20px 22px;margin:16px 0;
box-shadow:0 2px 10px rgba(190,58,110,.07)}
h2{margin:0 0 12px;font-size:19px;color:var(--rosa)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.item{background:var(--suave);border-radius:12px;padding:12px 14px}.item b{display:block;margin-bottom:2px}
.item span{color:var(--mut);font-size:14.5px}
.dos{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.ok,.no{border-radius:14px;padding:16px 18px}.ok{background:var(--okbg)}.no{background:var(--nobg)}
.ok h2{color:var(--ok)}.no h2{color:var(--no)}ul{margin:0;padding-left:20px}li{margin:6px 0}
.ejemplo{font-style:italic;color:var(--mut);font-size:14px;margin-top:4px}
code,pre{font-family:ui-monospace,Consolas,monospace;font-size:13.5px}
code{background:var(--suave);color:var(--code);padding:1px 6px;border-radius:6px}
pre{background:var(--suave);color:var(--code);padding:14px;border-radius:12px;overflow-x:auto;margin:8px 0}
table{width:100%;border-collapse:collapse;font-size:14.5px}td,th{text-align:left;padding:8px 10px;border-bottom:1px solid var(--bd)}
th{color:var(--mut);font-weight:600}.pub{color:var(--ok);font-weight:600}.priv{color:var(--rosa);font-weight:600}
.tools{display:flex;flex-wrap:wrap;gap:6px}
.aviso{font-size:13.5px;color:var(--mut);text-align:center;margin-top:24px}
a{color:var(--rosa)}
"""


def pagina() -> str:
    a = AGENTES[config.AGENT_ID]
    u = e(config.URL_PUBLICA)
    ejemplos = "".join(f'<div class="ejemplo">“{e(x)}”</div>' for x in a.ejemplos[:2])
    hace = "".join(f'<div class="item"><b>{e(t)}</b><span>{e(d)}</span></div>' for t, d in HACE)
    no_hace = "".join(f"<li>{e(x)}</li>" for x in NO_HACE)
    skills = "".join(
        f'<div class="item"><b>{e(n)}</b><span>{e(d)}</span><div class="ejemplo">“{e(ej[0])}”</div></div>'
        for _i, n, d, _t, ej in a.skills)
    tools = "".join(f"<code>{e(t)}</code>" for t in HERRAMIENTAS)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(config.AGENT_ID)} · Ficha del agente</title>
<style>{CSS}</style></head><body>
<header><div class="wrap"><div class="logo" aria-hidden="true">A2A</div><div>
<h1>{e(config.AGENT_ID)} · Auditoría CMF/SII</h1>
<p>Agente de {e(a.especialidad)}. Rigurosa, directa y paciente: cita la fuente o norma de cada dato.</p>
<div class="pills"><span class="pill">Alejandra Ubilla</span><span class="pill">Protocolo A2A</span>
<span class="pill">Datos simulados</span><span class="pill">Acceso con clave</span></div></div></div></header>
<div class="wrap"><main>
<section><h2>Qué sabe hacer</h2><div class="grid">{hace}</div>
<div style="margin-top:12px">{ejemplos}</div></section>
<section class="dos"><div class="ok"><h2>✔ Qué hace</h2><ul>
<li>Consulta datos con herramientas y cita su fuente</li><li>Distingue hallazgos de recomendaciones</li>
<li>Pide el dato que falta (RUT, fondo, tipo) antes de concluir</li><li>Recuerda la conversación por <code>contextId</code></li></ul></div>
<div class="no"><h2>✖ Qué NO hace</h2><ul>{no_hace}</ul></div></section>
<section><h2>Habilidades publicadas en la ficha A2A</h2><div class="grid">{skills}</div></section>
<section><h2>Cómo consultarme</h2>
<table><tr><th>Endpoint</th><th>Acceso</th><th>Para qué</th></tr>
<tr><td><code>GET /salud</code></td><td class="pub">público</td><td>Estado del servicio</td></tr>
<tr><td><code>GET /.well-known/agent-card.json</code></td><td class="pub">público</td><td>Ficha A2A (la que lee el coordinador)</td></tr>
<tr><td><code>POST /a2a</code></td><td class="priv">con clave</td><td>A2A <code>message/send</code></td></tr>
<tr><td><code>POST /chat</code></td><td class="priv">con clave</td><td>Consulta directa</td></tr>
<tr><td><a href="/docs">/docs</a></td><td class="pub">público</td><td>Swagger interactivo</td></tr></table>
<pre>curl -X POST {u}/a2a -H "X-API-Key: &lt;SU_CLAVE&gt;" -H "Content-Type: application/json" \\
  -d '{{"jsonrpc":"2.0","id":"1","method":"message/send","params":{{"message":{{"role":"user",
  "messageId":"m1","contextId":"mi-conversacion","parts":[{{"kind":"text","text":"¿Cumple la empresa 77.987.654-3?"}}]}}}}}}'</pre>
<p style="font-size:14px;color:var(--mut)">La clave la entrega la administradora del servicio por un canal privado.</p></section>
<section><h2>Herramientas con datos</h2><div class="tools">{tools}</div>
<p style="font-size:14px;color:var(--mut);margin-bottom:0">Datos de prueba: RUT <code>76.123.456-7</code>,
<code>77.987.654-3</code>, <code>78.555.111-2</code> · fondos <code>FM Acciones Chile</code>, <code>FM Deuda Privada</code>,
<code>FM Inmobiliario</code>.</p></section>
<p class="aviso">Dirección pública: <a href="{u}">{u}</a> · Ficha máquina: <a href="/.well-known/agent-card.json">agent-card.json</a><br>
La memoria de las conversaciones vive en el servidor y se borra al reiniciarlo.</p>
</main></div></body></html>"""
