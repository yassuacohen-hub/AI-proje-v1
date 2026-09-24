#!/usr/bin/env python3
"""
Config Test — Eksik/hatalı key tespiti ve redaction kontrolü.

Kullanım:
  python scripts/config_test.py --env dev|prod
  python scripts/config_test.py --check-redaction
"""

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Zorunlu key'ler (ortamdan bağımsız)
REQUIRED_KEYS = [
    "GROQ_API_KEY",
    "NINEROUTER_API_KEY",
    "DATABASE_URL",
    "SESSION_SECRET",
    "JWT_SECRET",
]

# Prod-specific zorunlu key'ler
PROD_REQUIRED_KEYS = [
    "ADMIN_PASSWORD",
    "AWS_SECRETS_MANAGER_REGION",
    "AWS_SECRETS_MANAGER_PREFIX",
]

# Hassas key'ler (loglarda redact edilmeli)
SENSITIVE_KEYS = [
    "GROQ_API_KEY",
    "NINEROUTER_API_KEY",
    "DATABASE_URL",
    "ADMIN_PASSWORD",
    "SESSION_SECRET",
    "JWT_SECRET",
    "AWS_SECRETS_MANAGER_PREFIX",  # path bilgisini gizle
]


def load_env(env: str) -> dict:
    """Ortama göre .env dosyası yükle."""
    if env == "dev":
        env_path = ROOT / ".env.vault"
    elif env == "prod":
        env_path = ROOT / ".env"
    else:
        raise ValueError(f"Bilinmeyen env: {env}")

    if not env_path.exists():
        return {}

    data = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def check_missing_keys(env: str, data: dict) -> list:
    """Eksik key'leri kontrol et."""
    required = REQUIRED_KEYS.copy()
    if env == "prod":
        required.extend(PROD_REQUIRED_KEYS)

    missing = []
    for key in required:
        if key not in data or not data[key] or data[key].startswith("***"):
            missing.append(key)
    return missing


def check_placeholder_keys(data: dict) -> list:
    """Placeholder değerleri tespit et (dummy değerler)."""
    placeholders = []
    dummy_patterns = [
        r"^sk-dummy-",
        r"^sk-local-test-",
        r"^\*\*\*",
        r"^local-",
        r"^postgresql://postgres:postgres@",
    ]
    for key, value in data.items():
        if any(re.match(p, value) for p in dummy_patterns):
            placeholders.append(key)
    return placeholders


def check_invalid_keys(data: dict) -> list:
    """Geçersiz/eksik değer içeren key'leri tespit et."""
    invalid = []
    for key in REQUIRED_KEYS:
        if key in data:
            value = data[key]
            # Boş veya placeholder değer kontrolü
            if not value or value.startswith("***"):
                invalid.append(f"{key}=<empty or placeholder>")
            # API key uzunluğu kontrolü (genelde 20+ char)
            elif key.endswith("_KEY") and len(value) < 20:
                invalid.append(f"{key}=<too short ({len(value)} chars)>")
    return invalid


def check_redaction(log_text: str) -> list:
    """Log metninde hassas değerlerin redact edilip edilmediğini kontrol et."""
    issues = []
    for key in SENSITIVE_KEYS:
        # Basit pattern: key=value formatında loglanıyorsa
        pattern = rf"{key}=[^\s]+"
        matches = re.findall(pattern, log_text, re.IGNORECASE)
        for m in matches:
            if "REDACTED" not in m and "***" not in m:
                issues.append(f"{key} redact edilmemis: {m[:50]}...")
    return issues


def validate_url_format(key: str, value: str) -> bool:
    """URL formatı doğrula."""
    # Boş değerler opsiyonel key'ler için geçerli
    if not value:
        return True
    if key == "DATABASE_URL":
        return value.startswith("postgresql://") or value.startswith("postgres://")
    if key in ("NINEROUTER_URL", "REDIS_URL", "SENTRY_DSN", "VAULT_ADDR"):
        return value.startswith("http://") or value.startswith("https://") or value.startswith("redis://")
    return True


def main():
    parser = argparse.ArgumentParser(description="Config test scripti")
    parser.add_argument("--env", choices=["dev", "prod"], default="dev", help="Test edilecek ortam")
    parser.add_argument("--check-redaction", action="store_true", help="Log redaction kontrolü")
    parser.add_argument("--log-file", type=str, help="Kontrol edilecek log dosyası")
    args = parser.parse_args()

    print(f"[config_test] env={args.env}")

    # Config yükle
    data = load_env(args.env)
    if not data:
        print(f"[HATA] Config dosyasi bulunamadi: {args.env}")
        sys.exit(1)

    print(f"  Yuklenen key sayisi: {len(data)}")

    # Eksik key kontrolü
    missing = check_missing_keys(args.env, data)
    if missing:
        print(f"[HATA] Eksik key'ler: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("[OK] Tum zorunlu key'ler mevcut")

    # Placeholder kontrolü
    placeholders = check_placeholder_keys(data)
    if placeholders:
        print(f"[UYARI] Placeholder/dummy key'ler: {', '.join(placeholders)}")
        if args.env == "prod":
            print("[HATA] Prod ortaminda placeholder kabul edilemez")
            sys.exit(1)
    else:
        print("[OK] Placeholder key yok")

    # URL format kontrolü
    url_errors = []
    for key, value in data.items():
        if not validate_url_format(key, value):
            url_errors.append(key)
    if url_errors:
        print(f"[HATA] Gecersiz URL format: {', '.join(url_errors)}")
        sys.exit(1)
    else:
        print("[OK] URL formatlari gecerli")

    # Redaction kontrolü
    if args.check_redaction:
        if not args.log_file:
            print("[HATA] --check-redaction icin --log-file gerekli")
            sys.exit(1)
        log_path = Path(args.log_file)
        if not log_path.exists():
            print(f"[HATA] Log dosyasi bulunamadi: {log_path}")
            sys.exit(1)
        log_text = log_path.read_text(encoding="utf-8", errors="ignore")
        issues = check_redaction(log_text)
        if issues:
            print(f"[HATA] Redaction eksiklikleri:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("[OK] Tum hassas key'ler loglarda redact edilmis")

    print("\n[TUM KONTROLLER BASARILI]")
    sys.exit(0)


if __name__ == "__main__":
    main()
