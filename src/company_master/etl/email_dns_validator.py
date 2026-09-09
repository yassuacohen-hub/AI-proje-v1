#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E-posta domain DNS MX doÄŸrulama ve teslim edilebilirlik kontrolÃ¼."""
from __future__ import annotations

import json
import logging
import re
import socket
import smtplib
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import dns.resolver
import dns.exception
from sqlalchemy import text
from company_master.db.connection import get_engine

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "email_dns_validator.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("email_dns_validator")

# E-posta format kontrolÃ¼
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# YaygÄ±n catch-all domainler (sadece format kontrolÃ¼ yap)
COMMON_CATCHALL = {
    "gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "yandex.com",
    "mynet.com", "hotmail.co.uk", "live.com", "msn.com", "icloud.com",
}

# DNS resolver ayarlarÄ±
DNS_TIMEOUT = 5.0
DNS_LIFETIME = 10.0


def extract_domain(email: str) -> str | None:
    """E-posta adresinden domain Ã§Ä±kar."""
    if not email or "@" not in email:
        return None
    return email.split("@", 1)[1].lower().strip()


def check_mx_record(domain: str) -> list[str] | None:
    """Domain iÃ§in MX kaydÄ± kontrol et."""
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = DNS_TIMEOUT
        resolver.lifetime = DNS_LIFETIME
        resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']  # Google + Cloudflare
        
        answers = resolver.resolve(domain, 'MX')
        mx_records = []
        for rdata in answers:
            mx_host = str(rdata.exchange).rstrip(".")
            mx_records.append(mx_host)
        
        if mx_records:
            log.debug("MX records for %s: %s", domain, mx_records)
            return mx_records
        return None
    except dns.resolver.NXDOMAIN:
        log.debug("Domain does not exist: %s", domain)
        return None
    except dns.resolver.NoAnswer:
        log.debug("No MX record for: %s", domain)
        return None
    except dns.exception.DNSException as e:
        log.debug("DNS error for %s: %s", domain, e)
        return None


def check_smtp_deliverable(email: str, mx_host: str) -> bool:
    """SMTP RCPT TO ile teslim edilebilirlik kontrolÃ¼."""
    try:
        # SMTP baÄŸlantÄ±sÄ±
        with smtplib.SMTP(mx_host, 25, timeout=10) as server:
            server.ehlo(socket.getfqdn())
            
            # MAIL FROM
            code, _ = server.mail("<>")
            if code != 250:
                return False
            
            # RCPT TO
            code, _ = server.rcpt(email)
            server.quit()
            
            return code == 250
    except Exception as e:
        log.debug("SMTP check failed for %s via %s: %s", email, mx_host, e)
        return False


def calculate_email_score(email: str | None, check_smtp: bool = False) -> dict[str, Any]:
    """E-posta geÃ§erlilik skoru hesapla (0-3)."""
    result = {
        "email": email,
        "score": 0,
        "format_valid": False,
        "has_mx": False,
        "mx_host": None,
        "smtp_deliverable": False,
        "checked_at": datetime.now().isoformat(),
    }
    
    if not email:
        return result
    
    # Format kontrolÃ¼
    if not EMAIL_REGEX.match(email):
        return result
    
    result["format_valid"] = True
    result["score"] = 1  # Format geÃ§erli
    
    domain = extract_domain(email)
    if not domain:
        return result
    
    # YaygÄ±n catch-all domainler iÃ§in sadece format skoru
    if domain in COMMON_CATCHALL:
        log.debug("Common catch-all domain: %s", domain)
        return result
    
    # MX kaydÄ± kontrolÃ¼
    mx_records = check_mx_record(domain)
    if mx_records:
        result["has_mx"] = True
        result["mx_host"] = mx_records[0]
        result["score"] = 2  # MX var
        
        # SMTP kontrolÃ¼ (opsiyonel)
        if check_smtp:
            for mx in mx_records[:2]:  # Ä°lk 2 MX dene
                if check_smtp_deliverable(email, mx):
                    result["smtp_deliverable"] = True
                    result["score"] = 3  # Teslim edilebilir
                    break
    else:
        # A kaydÄ± kontrol et (fallback)
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = DNS_TIMEOUT
            resolver.lifetime = DNS_LIFETIME
            resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']  # Google + Cloudflare
            resolver.resolve(domain, 'A')
            result["score"] = 1  # Sadece A kaydÄ± var
        except dns.exception.DNSException:
            pass
    
    return result


def run_email_validation(limit: int | None = None, offset: int = 0, check_smtp: bool = False) -> dict[str, int]:
    """TÃ¼m e-postalarÄ± doÄŸrula."""
    engine = get_engine()
    stats = {"processed": 0, "format_valid": 0, "has_mx": 0, "smtp_deliverable": 0, "errors": 0}
    
    with engine.begin() as conn:
        query = """
            SELECT company_id, primary_email 
            FROM companies 
            WHERE primary_email IS NOT NULL AND primary_email != ''
            ORDER BY company_id
            LIMIT :lim OFFSET :off
        """
        rows = conn.execute(text(query), {"lim": limit or 10000, "off": offset}).mappings().all()
        
        if not rows:
            log.info("DoÄŸrulanacak e-posta yok")
            return stats
        
        log.info("Toplam %d e-posta doÄŸrulanacak (limit=%s, offset=%d, smtp=%s)", 
                len(rows), limit, offset, check_smtp)
        
        for i, row in enumerate(rows):
            company_id = row["company_id"]
            email = row["primary_email"]
            
            try:
                result = calculate_email_score(email, check_smtp)
                
                # Skoru kaydet
                conn.execute(text("""
                    UPDATE companies SET
                        email_validity_score = :score,
                        email_validation_data = CAST(:data AS jsonb),
                        email_validated_at = :checked
                    WHERE company_id = :cid
                """), {
                    "score": result["score"],
                    "data": json.dumps(result, ensure_ascii=False),
                    "checked": result["checked_at"],
                    "cid": company_id,
                })
                
                if result["format_valid"]:
                    stats["format_valid"] += 1
                if result["has_mx"]:
                    stats["has_mx"] += 1
                if result["smtp_deliverable"]:
                    stats["smtp_deliverable"] += 1
                stats["processed"] += 1
                
                if (i + 1) % 100 == 0:
                    log.info("Ä°lerleme: %d/%d - Format: %d, MX: %d, SMTP: %d", 
                            i + 1, len(rows), stats["format_valid"], stats["has_mx"], stats["smtp_deliverable"])
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                stats["errors"] += 1
                log.error("Error validating %s: %s", email, e)
    
    return stats


if __name__ == "__main__":
    import sys
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Email DNS MX validator")
    parser.add_argument("--limit", type=int, default=100, help="Max emails to validate")
    parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    parser.add_argument("--smtp", action="store_true", help="Enable SMTP deliverability check")
    args = parser.parse_args()
    
    log.info("Starting email DNS validation (limit=%s, offset=%d, smtp=%s)", args.limit, args.offset, args.smtp)
    stats = run_email_validation(limit=args.limit, offset=args.offset, check_smtp=args.smtp)
    log.info("Done: %s", json.dumps(stats, ensure_ascii=False))
    print(json.dumps(stats, ensure_ascii=False, indent=2))



