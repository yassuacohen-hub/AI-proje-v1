# -*- coding: utf-8 -*-
"""Health check & monitoring API.

Sistem saglik kontrolu, metrik toplama ve alerting icin endpoint.

Kullanim:
    # API endpoint olarak
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(health_router)
    
    # Cron job olarak (her 5 dakika)
    # */5 * * * * python health_check.py
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(ROOT / "logs" / "health_check.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health check sonucu."""
    status: str
    timestamp: str
    checks: Dict[str, bool]
    metrics: Dict[str, Any]
    alerts: List[str]


def check_database() -> tuple[bool, str]:
    """PostgreSQL baglantisini kontrol et."""
    try:
        from sqlalchemy import text
        from company_master.db.connection import get_engine
        
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True, "OK"
    except Exception as e:
        return False, str(e)


def check_data_quality() -> tuple[bool, str]:
    """Kalite skoru ortalamasini kontrol et."""
    try:
        from sqlalchemy import text
        from company_master.db.connection import get_engine
        
        engine = get_engine()
        with engine.connect() as conn:
            avg = conn.execute(text("""
                SELECT AVG(data_quality_score) as avg_score
                FROM companies WHERE is_ankara = TRUE
            """)).fetchone()[0]
            
            if avg and avg >= 50:
                return True, f"Avg: {avg:.1f}"
            else:
                return False, f"Dusuk kalite: {avg:.1f}"
    except Exception as e:
        return False, str(e)


def check_data_freshness() -> tuple[bool, str]:
    """Veri tazeligini kontrol et (son 7 gun icinde scrape?)."""
    try:
        from sqlalchemy import text
        from company_master.db.connection import get_engine
        
        engine = get_engine()
        with engine.connect() as conn:
            last_scrape = conn.execute(text("""
                SELECT MAX(ingested_at) FROM companies
            """)).fetchone()[0]
            
            if not last_scrape:
                return False, "Hiç veri yok"
            
            days_old = (datetime.now() - last_scrape.replace(tzinfo=None)).days
            if days_old <= 7:
                return True, f"{days_old} gun önce"
            else:
                return False, f"Eski veri: {days_old} gün"
    except Exception as e:
        return False, str(e)


def check_api_endpoints() -> tuple[bool, str]:
    """API endpoint'lerinin calistigini kontrol et."""
    try:
        import requests
        api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
        
        resp = requests.get(f"{api_base}/health", timeout=5)
        if resp.status_code == 200:
            return True, "OK"
        else:
            return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)


def check_disk_space() -> tuple[bool, str]:
    """Disk alanini kontrol et."""
    try:
        import shutil
        path = ROOT
        usage = shutil.disk_usage(path)
        free_gb = usage.free / (1024**3)
        if free_gb > 5:
            return True, f"{free_gb:.1f} GB bos"
        else:
            return False, f"Dusuk alan: {free_gb:.1f} GB"
    except Exception as e:
        return False, str(e)


def run_health_check() -> HealthStatus:
    """Tum saglik kontrollerini calistir."""
    checks = {}
    metrics = {}
    alerts = []
    
    # DB kontrol
    ok, msg = check_database()
    checks["database"] = ok
    metrics["db_message"] = msg
    
    # Kalite kontrol
    ok, msg = check_data_quality()
    checks["data_quality"] = ok
    metrics["quality_message"] = msg
    
    # Tazelik kontrol
    ok, msg = check_data_freshness()
    checks["data_freshness"] = ok
    metrics["freshness_message"] = msg
    
    # API kontrol
    ok, msg = check_api_endpoints()
    checks["api_endpoints"] = ok
    metrics["api_message"] = msg
    
    # Disk kontrol
    ok, msg = check_disk_space()
    checks["disk_space"] = ok
    metrics["disk_message"] = msg
    
    # Alert'ler
    if not checks["database"]:
        alerts.append("CRITICAL: Database baglantisi basarisiz!")
    if not checks["data_quality"]:
        alerts.append("WARNING: Kalite skoru dusuk!")
    if not checks["data_freshness"]:
        alerts.append("WARNING: Veri eski!")
    if not checks["api_endpoints"]:
        alerts.append("WARNING: API endpoint'leri yonettirmiyor!")
    if not checks["disk_space"]:
        alerts.append("CRITICAL: Disk alani dusuk!")
    
    # Overall status
    critical_failed = sum(1 for c in checks.values() if not c)
    if critical_failed == 0:
        status = "healthy"
    elif critical_failed <= 2:
        status = "degraded"
    else:
        status = "unhealthy"
    
    return HealthStatus(
        status=status,
        timestamp=datetime.now().isoformat(),
        checks=checks,
        metrics=metrics,
        alerts=alerts,
    )


def send_alert(alert: str):
    """Alert gonder (Telegram/email)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if token and chat_id:
        try:
            import requests
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={
                "chat_id": chat_id,
                "text": f"🚨 Huginn Alert:\n{alert}",
                "parse_mode": "Markdown",
            }, timeout=10)
        except Exception as e:
            logger.error(f"Alert gonderilemedi: {e}")


def main():
    """CLI modu."""
    result = run_health_check()
    
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    
    # Kritik alert'leri gonder
    if result.alerts:
        for alert in result.alerts:
            if alert.startswith("CRITICAL"):
                send_alert(alert)
    
    # Exit code
    if result.status == "unhealthy":
        sys.exit(2)
    elif result.status == "degraded":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
