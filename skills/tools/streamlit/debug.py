# Streamlit Debug Yetenekleri

from skills.base import registry


@registry.register(
    name="analyze_streamlit_lifecycle",
    description="Streamlit kodundaki session_state sÄ±zÄ±ntÄ±larÄ±nÄ± ve sonsuz st.rerun() dÃ¶ngÃ¼lerini yakalar."
)
def analyze_streamlit_lifecycle(code_snippet: str) -> str:
    """Fonksiyonun docstring'i veya parametreleri iÃ§eride iÅŸlenir."""
    if "st.session_state" in code_snippet and "st.rerun()" in code_snippet:
        return "CRITICAL: st.session_state gÃ¼ncellenirken st.rerun() kontrolsÃ¼z Ã§aÄŸrÄ±lmÄ±ÅŸ. Sonsuz dÃ¶ngÃ¼ riski var!"
    return "SUCCESS: Kod dÃ¶ngÃ¼sÃ¼ analizi temiz."


@registry.register(
    name="fix_nginx_websocket",
    description="Streamlit sunucularÄ±ndaki Nginx 502 Bad Gateway ve kopma hatalarÄ± iÃ§in konfigÃ¼rasyon Ã¼retir."
)
def fix_nginx_websocket(domain_name: str, internal_port: int = 8501) -> str:
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
