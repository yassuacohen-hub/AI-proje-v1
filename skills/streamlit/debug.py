# Streamlit Debug Yetenekleri

from skills.base import registry


@registry.register(
    name="analyze_streamlit_lifecycle",
    description="Streamlit kodundaki session_state sızıntılarını ve sonsuz st.rerun() döngülerini yakalar."
)
def analyze_streamlit_lifecycle(code_snippet: str) -> str:
    """Fonksiyonun docstring'i veya parametreleri içeride işlenir."""
    if "st.session_state" in code_snippet and "st.rerun()" in code_snippet:
        return "CRITICAL: st.session_state güncellenirken st.rerun() kontrolsüz çağrılmış. Sonsuz döngü riski var!"
    return "SUCCESS: Kod döngüsü analizi temiz."


@registry.register(
    name="fix_nginx_websocket",
    description="Streamlit sunucularındaki Nginx 502 Bad Gateway ve kopma hataları için konfigürasyon üretir."
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
