# Docker DevOps Yeteneği

from skills.base import registry


@registry.register(
    name="optimize_dockerfile",
    description="Dockerfile'ı optimize eder (multi-stage build, layer caching)."
)
def optimize_dockerfile(dockerfile_content: str) -> str:
    optimized = dockerfile_content
    if "FROM scratch" not in optimized and "\nCOPY" in optimized:
        optimized += "\n# ÖNERİ: Multi-stage build kullanmayı değerlendir."
    return optimized


@registry.register(
    name="parse_container_logs",
    description="Container loglarından hata ve uyarıları çıkarır."
)
def parse_container_logs(logs: str) -> dict:
    errors = [line for line in logs.split("\n") if "ERROR" in line]
    return {"total_errors": len(errors), "errors": errors[:5]}
