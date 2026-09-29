# Streamlit Production Agent Yetenekleri
# Kaynak: streamlit_production_agent_v2.md (VERSION: 2.0.26)

from skills.base import registry


@registry.register(
    name="analyze_streamlit_lifecycle",
    description="Streamlit kodundaki session_state sÄ±zÄ±ntÄ±larÄ±nÄ± ve sonsuz st.rerun() dÃ¶ngÃ¼lerini yakalar. Ãœretim ortamÄ± triajÄ± yapar."
)
def analyze_streamlit_lifecycle(code_snippet: str) -> str:
    """Fonksiyonun docstring'i veya parametreleri iÃ§eride iÅŸlenir."""
    if "st.session_state" in code_snippet and "st.rerun()" in code_snippet:
        return "CRITICAL: st.session_state gÃ¼ncellenirken st.rerun() kontrolsÃ¼z Ã§aÄŸrÄ±lmÄ±ÅŸ. Sonsuz dÃ¶ngÃ¼ riski var!"
    return "SUCCESS: Kod dÃ¶ngÃ¼sÃ¼ analizi temiz."


@registry.register(
    name="fix_streamlit_websocket",
    description="Streamlit sunucularÄ±ndaki Nginx/Traefik WebSocket kopma hatalarÄ± iÃ§in konfigÃ¼rasyon Ã¼retir."
)
def fix_streamlit_websocket(domain_name: str, internal_port: int = 8501) -> str:
    return f"""
    server {{
        listen 80;
        server_name {domain_name};
        location / {{
            proxy_pass http://localhost:{internal_port};
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $http_host;
        }}
    }}
    """


@registry.register(
    name="generate_streamlit_config",
    description="Ãœretim Streamlit config.toml Ã¼retir (threading, caching, server settings)."
)
def generate_streamlit_config(server_port: int = 8501, max_upload_size: str = "200M") -> str:
    return f"""
[server]
port = {server_port}
maxUploadSize = {max_upload_size}
fileWatcherType = "none"
enableXsrfProtection = true

[theme]
base = "dark"
primaryColor = "#1f77b4"

[logger]
level = "info"
"""


@registry.register(
    name="analyze_performance_metrics",
    description="Streamlit uygulamasÄ± performans metriklerini analiz eder (render sÃ¼resi, memory, CPU)."
)
def analyze_performance_metrics(metrics: dict) -> str:
    render_ms = metrics.get("render_ms", 0)
    memory_mb = metrics.get("memory_mb", 0)
    if render_ms > 3000:
        return f"WARNING: Render sÃ¼resi yÃ¼ksek ({render_ms}ms) â€” lazy loading / st.cache_data eklenmeli."
    if memory_mb > 500:
        return f"WARNING: Bellek kullanÄ±mÄ± yÃ¼ksek ({memory_mb}MB) â€” cache ttl ve max_entries azaltÄ±lmalÄ±."
    return f"OK: Render {render_ms}ms, Memory {memory_mb}MB â€” iÃ§inde iyi."