# Nginx DevOps Yeteneği

from skills.base import registry


@registry.register(
    name="analyze_nginx_websocket",
    description="Nginx WebSocket zaman aşımı ve 502 Bad Gateway hatalarını analiz eder."
)
def analyze_nginx_websocket(error_log: str) -> str:
    if "Connection timed out" in error_log:
        return "WebSocket zaman aşımı tespit edildi: proxy buffer boyutunu artır veya keepalive timeout ayarlarını kontrol et."
    return "WebSocket hatası analiz edilemedi, logu kontrol edin."


@registry.register(
    name="fix_nginx_proxy",
    description="Nginx proxy yapılandırmasını kontrol eder ve öneriler verir."
)
def fix_nginx_proxy(config: str) -> str:
    issues = []
    if "proxy_buffer_size" not in config:
        issues.append("proxy_buffer_size ayarı eksik.")
    return f"Proxy Kontrolü: {len(issues)} öneri var." if issues else "Proxy yapılandırması sorunlu değil."


@registry.register(
    name="generate_nginx_config",
    description="Verilen domain ve port bilgisiyle Nginx yapılandırma dosyası üretir."
)
def generate_nginx_config(domain_name: str, internal_port: int = 8501) -> str:
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
