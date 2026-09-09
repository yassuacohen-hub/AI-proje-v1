"""Sistem sağlık kontrol betiği.

Veritabanı bağlantısı, API endpoint ve sistem kaynaklarını kontrol eder.
Çıktı JSON formatında, exit code: 0=OK, 1=degraded, 2=critical.

Gereksinimler:
    - sqlalchemy>=2.0
    - requests
    - psutil (opsiyonel; yoksa stdlib ile sistem kaynakları kontrol edilir)

Ortam değişkenleri:
    - DATABASE_URL: PostgreSQL bağlantı dizgesi
    - HEALTHCHECK_API_URL: Kontrol edilecek API endpoint (opsiyonel)
    - HEALTHCHECK_OUTPUT: JSON çıktı dosyası yolu (opsiyonel)

Kullanım:
    python scripts/healthcheck.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import psutil  # type: ignore
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore

try:
    from sqlalchemy import create_engine, text  # type: ignore
except ImportError:
    create_engine = None  # type: ignore
    text = None  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "healthcheck.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_database_url(env: dict[str, str]) -> str | None:
    return os.environ.get("DATABASE_URL") or env.get("DATABASE_URL")


def check_database(database_url: str) -> dict:
    if create_engine is None:
        return {"status": "skipped", "reason": "sqlalchemy yüklü değil"}

    result: dict = {"status": "unknown", "latency_ms": None}
    start = time.perf_counter()
    try:
        engine = create_engine(database_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        result["status"] = "ok"
        result["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
    except Exception as exc:
        result["status"] = "critical"
        result["error"] = str(exc)
        logger.error("Veritabanı kontrolü başarısız: %s", exc)
    return result


def check_api(url: str | None) -> dict:
    if not url or requests is None:
        return {"status": "skipped", "reason": "URL veya requests yüklü değil"}

    result: dict = {"status": "unknown", "latency_ms": None, "url": url}
    start = time.perf_counter()
    try:
        resp = requests.get(url, timeout=10)
        result["status"] = "ok" if resp.status_code < 400 else "degraded"
        result["http_status"] = resp.status_code
        result["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
    except Exception as exc:
        result["status"] = "critical"
        result["error"] = str(exc)
        logger.error("API kontrolü başarısız: %s", exc)
    return result


def check_system() -> dict:
    result: dict = {"status": "ok"}

    if HAS_PSUTIL:
        result["cpu_percent"] = psutil.cpu_percent(interval=1)
        result["memory_percent"] = psutil.virtual_memory().percent
        result["disk_percent"] = psutil.disk_usage("/").percent
    else:
        cpu = os.cpu_count() or 1
        load1, load5, load15 = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
        result["cpu_load_1m"] = round(load1 / cpu, 2)
        result["cpu_load_5m"] = round(load5 / cpu, 2)
        result["cpu_load_15m"] = round(load15 / cpu, 2)
        result["note"] = "psutil bulunamadı; stdlib ile sınırlı veri"

    if result.get("memory_percent", 0) > 90 or result.get("disk_percent", 0) > 90:
        result["status"] = "degraded"

    return result


def main() -> int:
    LOG_DIR.mkdir(exist_ok=True)
    env = load_env()

    database_url = get_database_url(env)
    api_url = os.environ.get("HEALTHCHECK_API_URL") or env.get("HEALTHCHECK_API_URL")
    output_path = os.environ.get("HEALTHCHECK_OUTPUT") or env.get("HEALTHCHECK_OUTPUT")

    report: dict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": check_database(database_url) if database_url else {"status": "skipped", "reason": "DATABASE_URL yok"},
        "api": check_api(api_url),
        "system": check_system(),
    }

    degraded = any(
        v.get("status") == "degraded"
        for v in report.values()
        if isinstance(v, dict)
    )
    critical = any(
        v.get("status") == "critical"
        for v in report.values()
        if isinstance(v, dict)
    )

    if critical:
        report["overall_status"] = "critical"
        exit_code = 2
    elif degraded:
        report["overall_status"] = "degraded"
        exit_code = 1
    else:
        report["overall_status"] = "ok"
        exit_code = 0

    json_output = json.dumps(report, ensure_ascii=False, indent=2)

    if output_path:
        try:
            Path(output_path).write_text(json_output, encoding="utf-8")
            logger.info("Sağlık raporu yazıldı: %s", output_path)
        except OSError as exc:
            logger.error("Çıktı dosyası yazılamadı: %s", exc)

    logger.info("Sağlık kontrolü tamamlandı: %s", report["overall_status"])
    print(json_output)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
