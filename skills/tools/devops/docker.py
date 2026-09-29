# Docker DevOps YeteneÄŸi

from skills.base import registry


@registry.register(
    name="optimize_dockerfile",
    description="Dockerfile'Ä± optimize eder (multi-stage build, layer caching)."
)
def optimize_dockerfile(dockerfile_content: str) -> str:
    optimized = dockerfile_content
    if "FROM scratch" not in optimized and "\nCOPY" in optimized:
        optimized += "\n# Ã–NERÄ°: Multi-stage build kullanmayÄ± deÄŸerlendir."
    return optimized


@registry.register(
    name="parse_container_logs",
    description="Container loglarÄ±ndan hata ve uyarÄ±larÄ± Ã§Ä±karÄ±r."
)
def parse_container_logs(logs: str) -> dict:
    errors = [line for line in logs.split("\n") if "ERROR" in line]
    return {"total_errors": len(errors), "errors": errors[:5]}
