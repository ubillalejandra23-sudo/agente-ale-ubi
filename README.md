# agente-ale-ubi · Auditoría CMF/SII — agente A2A autónomo

Taller *Implementa y entrega tu agente* (Agentic AI · Curso 2). Este repositorio contiene **solo el agente de Alejandra Ubilla**
(agente-Aleubi). **No es el coordinador**: el coordinador del equipo lee su ficha y le pasa las preguntas de su especialidad.

| | |
|---|---|
| **Integrante** | Alejandra Ubilla |
| **Qué hace** | Estado tributario SII por RUT · cruce SII + CMF (¿cumple la empresa?) · auditoría de fondos (concentración NCG 365, TER, rentabilidad neta) · checklists de auditoría por tipo de empresa o fondo · apuntes de criterio |
| **Qué NO hace** | Asesoría tributaria personal, legal o de inversión · ejecutar acciones correctivas o informar a organismos · temas ajenos a la auditoría (los rechaza con amabilidad). Solo **recomienda** el siguiente paso |
| **Datos** | **Simulados** (9 herramientas deterministas: el agente no inventa cifras, las toma de ellas) |
| **Servicio** | FastAPI + SDK oficial `a2a-sdk` |

## Endpoints

| Endpoint | Acceso | Descripción |
|---|---|---|
| `GET /salud` | público | Estado del servicio y `url_publica` |
| `GET /.well-known/agent-card.json` | público | Ficha A2A: qué hace, qué no, habilidades, URL y esquema de seguridad |
| `POST /a2a` | **clave** | A2A `message/send` (JSON-RPC). El `contextId` es la memoria de la conversación |
| `POST /chat` | **clave** | Consulta directa: `{"mensaje": "...", "conversation_id": "opcional"}` |
| `GET /docs` | público | Swagger (botón **Authorize** para ingresar la clave) |

**Seguridad.** La clave viaja en `X-API-Key` (o `Authorization: Bearer`) y se valida en el servidor en tiempo constante.
Sin clave → `401`. Si `API_KEYS` no está configurada → `503` (falla cerrado). La clave de ejemplo de `.env.example` es pública y se
rechaza. Ningún secreto está en el repositorio: viven en `.env` (ignorado por git) o en las variables de la nube.

**Errores claros.** `401` clave ausente/inválida · `422` entrada inválida · `429` demasiadas consultas · `502` falla del proveedor del
modelo (nunca se presenta como éxito) · `503` acceso no configurado.

**Memoria.** Cada `contextId` (A2A) o `conversation_id` (`/chat`) tiene su propia conversación; no se mezclan. Vive en el servidor
(checkpointer en memoria): **un reinicio la borra** (ver *Límites conocidos*).

## Preparación (lo que necesita quien lo pruebe)
1. **Python 3.11+** (probado con 3.12) e internet.
2. **Clave de Anthropic** (`ANTHROPIC_API_KEY`) con crédito: https://console.anthropic.com
3. Una **clave de acceso propia** para `API_KEYS`: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

No hay cuentas de correo/mensajería ni acciones con efectos externos.

## Instalación y arranque local
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env        # edite ANTHROPIC_API_KEY y API_KEYS
uvicorn app.main:app --port 8000
```
(macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`, `cp .env.example .env`.) `Ctrl+C` detiene el servicio.

## Probar el agente por separado
Use `SU_CLAVE` = lo que puso en `API_KEYS`. En PowerShell use `curl.exe`.
```bash
# 1. Salud y ficha (públicas)
curl http://127.0.0.1:8000/salud
curl http://127.0.0.1:8000/.well-known/agent-card.json

# 2. Mensaje A2A con clave (message/send)
curl -X POST http://127.0.0.1:8000/a2a -H "X-API-Key: SU_CLAVE" -H "Content-Type: application/json" -d '{
  "jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{
  "role":"user","messageId":"m1","contextId":"6f1c2a3e-0b7d-4c1e-9a55-2b8f0c1d7e90",
  "parts":[{"kind":"text","text":"¿Qué sanciones vigentes tiene en la CMF el RUT 77.987.654-3?"}]}}}'

# 3. Sin clave -> 401
curl -i -X POST http://127.0.0.1:8000/a2a -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{}}'

# 4. Consulta directa
curl -X POST http://127.0.0.1:8000/chat -H "X-API-Key: SU_CLAVE" -H "Content-Type: application/json" \
     -d '{"mensaje":"¿Cumple con la normativa la empresa 77.987.654-3?"}'
```
También en Swagger: http://127.0.0.1:8000/docs → **Authorize** → `POST /chat` → *Try it out*.

**Datos de prueba:** RUT `76.123.456-7`, `77.987.654-3` (con multa CMF 2025), `78.555.111-2`; fondos `FM Acciones Chile`,
`FM Deuda Privada`, `FM Inmobiliario` (35% de concentración vs. límite 20%); tipos de empresa `sa`/`spa`/`ltda`.
**Rechazo amable:** pregunte «¿qué tiempo hará mañana?» y el agente responde que está fuera de su área.

**Pruebas automáticas:** `pip install -r requirements-dev.txt && pytest -q` (no llaman al modelo).

## Despliegue en la nube (Heroku)
Archivos incluidos: `Procfile`, `.python-version`, `requirements.txt`. El puerto lo entrega `$PORT`.
```bash
heroku login
heroku create nombre-unico-app
heroku config:set ANTHROPIC_API_KEY=sk-ant-... API_KEYS=<clave-larga> URL_PUBLICA=https://nombre-unico-app.herokuapp.com
git push heroku main
heroku ps:scale web=1          # un solo dyno (la memoria es del proceso)
heroku logs --tail
```
`URL_PUBLICA` debe ser la dirección en la nube: es la que la ficha publica como lugar donde encontrar al agente (`/a2a`).
Compruebe: `https://nombre-unico-app.herokuapp.com/salud` y `.../.well-known/agent-card.json`. Entregue al coordinador y al equipo
docente la URL y la clave **por una vía privada**.

## Cómo lo usa el coordinador
El coordinador registra la URL de la ficha (`<URL_PUBLICA>/.well-known/agent-card.json`) y la clave del agente, lee `skills` y
`description` para decidir cuándo derivarme una pregunta, y envía `message/send` a `<URL_PUBLICA>/a2a` con `X-API-Key`. Las
respuestas del agente conservan cifras, unidades, fechas y supuestos tal como los entregan las herramientas, para que el
coordinador las integre sin cambiarlas y atribuyéndolas a `mi-agente`.

## Límites conocidos
- Datos SII/CMF/fondos **simulados**; el agente solo recomienda.
- La memoria de conversación y las tareas A2A están **en memoria del proceso**: un reinicio (Heroku reinicia los dynos a diario) la borra.
- Un solo proceso/worker: necesario para que esa memoria sea coherente.
- Límite de consultas por minuto y por clave solo en `/chat` (`RATE_LIMIT_PER_MIN`); en `/a2a` no hay límite de tasa.
- A2A: respuesta inmediata (sin streaming ni cancelación de tareas).
- Si el proveedor del modelo falla, el agente responde con un error explícito (no inventa una respuesta).
- El coordinador y el canal de atención (Telegram) **no forman parte de este repositorio**: aquí vive solo el agente.

## Estructura
```
app/
  main.py          FastAPI: /salud, /chat y protección de /a2a
  a2a_server.py    Ficha (Agent Card) y servidor A2A (a2a-sdk)
  security.py      validación de la clave y límite de consultas
  config.py        variables de entorno (URL_PUBLICA, API_KEYS, MODELO…)
  costos.py        ventana de historial, aviso de respuestas cortadas, registro de tokens
  agentes/         registro.py (agente, ficha y checkpointer) · alejandra/ (prompts.py + herramientas.py)
tests/             acceso, ficha, validación y costos
Procfile  .python-version  requirements*.txt  .env.example
```
