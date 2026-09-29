# Nginx DevOps YeteneÄŸi

from skills.base import registry


@registry.register(
    name="analyze_nginx_websocket",
    description="Nginx WebSocket zaman aÅŸÄ±mÄ± ve 502 Bad Gateway hatalarÄ±nÄ± analiz eder."
)
def analyze_nginx_websocket(error_log: str) -> str:
    if "Connection timed out" in error_log:
        return "WebSocket zaman aÅŸÄ±mÄ± tespit edildi: proxy buffer boyutunu artÄ±r veya keepalive timeout ayarlarÄ±nÄ± kontrol et."
    return "WebSocket hatasÄ± analiz edilemedi, logu kontrol edin."


@registry.register(
    name="fix_nginx_proxy",
    description="Nginx proxy yapÄ±landÄ±rmasÄ±nÄ± kontrol eder ve Ã¶neriler verir."
)
def fix_nginx_proxy(config: str) -> str:
    issues = []
    if "proxy_buffer_size" not in config:
        issues.append("proxy_buffer_size ayarÄ± eksik.")
    return f"Proxy KontrolÃ¼: {len(issues)} Ã¶neri var." if issues else "Proxy yapÄ±landÄ±rmasÄ± sorunlu deÄŸil."


@registry.register(
    name="generate_nginx_config",
    description="Verilen domain ve port bilgisiyle Nginx yapÄ±landÄ±rma dosyasÄ± Ã¼retir."
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
