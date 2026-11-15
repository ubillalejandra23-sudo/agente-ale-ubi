"""Tema rosado para Swagger UI (/docs): banner, colores de métodos, botones y modo oscuro automático."""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' "
           "rx='8' fill='%23be3a6e'/%3E%3Ctext x='16' y='21' font-size='13' font-weight='700' text-anchor='middle' fill='white' "
           "font-family='Arial'%3EA2A%3C/text%3E%3C/svg%3E")

BANNER = """<header class="ale-banner"><div class="ale-in">
  <div class="ale-logo" aria-hidden="true">A2A</div>
  <div><h1>agente-ale-ubi · API</h1><p>Auditoría CMF/SII · agente A2A de Alejandra Ubilla — documentación interactiva</p></div>
  <nav><a class="ale-btn" href="/">Ficha del agente</a>
  <a href="/.well-known/agent-card.json" target="_blank" rel="noopener">Ficha A2A (JSON)</a>
  <a href="/salud" target="_blank" rel="noopener">Estado</a></nav>
</div></header>"""

CSS = """
:root{--rosa:#be3a6e;--rosa2:#e0709a;--suave:#fbe3ec;--bg:#fdf6f9;--tx:#2a1620;--mut:#7a5c69;--bd:#f0d3de;--card:#fff}
@media (prefers-color-scheme:dark){:root{--rosa:#ef7fa8;--rosa2:#be3a6e;--suave:#3a2230;--bg:#1b1015;--tx:#f6e9ef;--mut:#c4a3b3;
--bd:#40262f;--card:#26171e}
.swagger-ui,.swagger-ui .info .title,.swagger-ui .info p,.swagger-ui .info li,.swagger-ui .info table,.swagger-ui td,.swagger-ui th,
.swagger-ui .opblock-description-wrapper p,.swagger-ui .opblock .opblock-section-header h4,.swagger-ui .response-col_status,
.swagger-ui .response-col_description,.swagger-ui label,.swagger-ui .parameter__name,.swagger-ui .parameter__type,
.swagger-ui .tab li,.swagger-ui table thead tr th,.swagger-ui .responses-inner h4,.swagger-ui .responses-inner h5,
.swagger-ui .opblock-summary-description,.swagger-ui .opblock-tag,.swagger-ui .markdown p,.swagger-ui .markdown li,
.swagger-ui .markdown code{color:var(--tx)!important}
.swagger-ui .opblock .opblock-section-header,.swagger-ui .scheme-container,.swagger-ui section.models{background:var(--card)!important}
.swagger-ui input,.swagger-ui textarea,.swagger-ui select{background:#33202a!important;color:var(--tx)!important}}
body{margin:0;background:var(--bg)}
.ale-banner{background:linear-gradient(135deg,var(--rosa),var(--rosa2));color:#fff;padding:22px 16px}
.ale-in{max-width:1200px;margin:0 auto;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.ale-logo{width:54px;height:54px;border-radius:15px;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.55);
display:grid;place-items:center;font:800 17px system-ui,Segoe UI,sans-serif;letter-spacing:1px}
.ale-banner h1{margin:0;font-size:24px;color:#fff;font-family:system-ui,Segoe UI,sans-serif}
.ale-banner p{margin:2px 0 0;opacity:.95;font-size:14px;font-family:system-ui,Segoe UI,sans-serif}
.ale-banner nav{margin-left:auto;display:flex;gap:10px;flex-wrap:wrap}
.ale-banner nav a{color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.55);border-radius:999px;padding:5px 14px;
font:13px system-ui,Segoe UI,sans-serif}
.ale-banner nav a:hover{background:rgba(255,255,255,.2)}.ale-banner nav a.ale-btn{background:#fff;color:var(--rosa);font-weight:600}
.swagger-ui .wrapper{max-width:1200px}
.swagger-ui .info .title{color:var(--rosa)}.swagger-ui .info a,.swagger-ui a.nostyle{color:var(--rosa)}
.swagger-ui .info .title small.version-stamp{background:var(--rosa)}
.swagger-ui .scheme-container{box-shadow:none;border-bottom:1px solid var(--bd);background:var(--card)}
.swagger-ui .opblock-tag{border-bottom:1px solid var(--bd);color:var(--rosa)}
.swagger-ui .opblock.opblock-post{background:rgba(190,58,110,.07);border-color:var(--rosa)}
.swagger-ui .opblock.opblock-post .opblock-summary{border-color:var(--rosa)}
.swagger-ui .opblock.opblock-post .opblock-summary-method,.swagger-ui .opblock.opblock-post .tab-header .tab-item.active h4 span::after{background:var(--rosa)}
.swagger-ui .opblock.opblock-get{background:rgba(224,112,154,.07);border-color:var(--rosa2)}
.swagger-ui .opblock.opblock-get .opblock-summary{border-color:var(--rosa2)}
.swagger-ui .opblock.opblock-get .opblock-summary-method{background:var(--rosa2)}
.swagger-ui .btn.authorize{color:var(--rosa);border-color:var(--rosa);background:transparent}
.swagger-ui .btn.authorize svg{fill:var(--rosa)}
.swagger-ui .btn.execute{background:var(--rosa);border-color:var(--rosa);color:#fff}
.swagger-ui .btn.try-out__btn{border-color:var(--rosa);color:var(--rosa)}
.swagger-ui .btn.cancel{border-color:#b4412f;color:#b4412f}
.swagger-ui .responses-inner h4,.swagger-ui .opblock .opblock-section-header h4{color:var(--rosa)}
.swagger-ui .tab li.active,.swagger-ui .tab li button.tablinks.active{color:var(--rosa)}
.swagger-ui select{border-color:var(--rosa)}
.swagger-ui .markdown code,.swagger-ui .renderedMarkdown code{background:var(--suave);color:var(--rosa);border-radius:6px}
.swagger-ui section.models{border-color:var(--bd)}
"""
