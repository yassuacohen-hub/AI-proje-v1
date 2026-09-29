# DevOps Yetenekleri Paketi
#
# ALTYAPI-SKILL-YAPISI-01 Faz A: burasÄ± sinif (NginxSkill) bekliyordu ama
# moduller duz fonksiyon tanimliyor -> ImportError. Duzeltme: fonksiyonlar
# disa aktarildi; desen skills/common/__init__.py ile ayni.

from skills.tools.devops.docker import optimize_dockerfile, parse_container_logs
from skills.tools.devops.monitor import analyze_oom_killer, check_resource_usage
from skills.tools.devops.nginx import (
    analyze_nginx_websocket,
    fix_nginx_proxy,
    generate_nginx_config,
)

__all__ = [
    "optimize_dockerfile",
    "parse_container_logs",
    "analyze_oom_killer",
    "check_resource_usage",
    "analyze_nginx_websocket",
    "fix_nginx_proxy",
    "generate_nginx_config",
]