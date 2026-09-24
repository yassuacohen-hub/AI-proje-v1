#!/usr/bin/env python
"""
Credential Rotation Script — 90 gün rotasyon

Kullanım:
  python scripts/rotate_secrets.py --dry-run
  python scripts/rotate_secrets.py --apply

Cron kurulumu (her pazar gece 2:00):
  0 2 * * 0 cd /app && python scripts/rotate_secrets.py --apply
"""

import argparse
import datetime
import json
import logging
import os
import secrets
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Rotation threshold: 90 days
ROTATION_DAYS = 90
SECRETS_TRACKER_FILE = Path(__file__).parent.parent / ".secrets_rotation.json"


def load_rotation_tracker():
    """Load last rotation timestamps."""
    if SECRETS_TRACKER_FILE.exists():
        try:
            with open(SECRETS_TRACKER_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Corrupted rotation tracker, starting fresh")
            return {}
    return {}


def save_rotation_tracker(tracker):
    """Save rotation timestamps."""
    with open(SECRETS_TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2, default=str)
    logger.info(f"Saved rotation tracker: {SECRETS_TRACKER_FILE}")


def needs_rotation(last_rotation_date):
    """Check if secret needs rotation (>90 days old)."""
    if not last_rotation_date:
        return True
    last_date = datetime.datetime.fromisoformat(last_rotation_date)
    days_old = (datetime.datetime.now() - last_date).days
    return days_old > ROTATION_DAYS


def rotate_session_secret():
    """Generate new SESSION_SECRET."""
    return secrets.token_urlsafe(32)


def rotate_jwt_secret():
    """Generate new JWT_SECRET."""
    return secrets.token_urlsafe(32)


def rotate_api_key(key_name):
    """Placeholder for API key rotation (real: re-provision from provider)."""
    # In prod: call Groq/NineRouter API to revoke old key and get new
    # Here: we log that it needs manual rotation
    logger.warning(f"API key {key_name} needs manual re-provisioning from provider")
    return None  # Require manual action


def get_env_path():
    """Get .env file path."""
    return Path(__file__).parent.parent / ".env"


def update_env_file(env_file, key, new_value):
    """Update or add key=value in .env file."""
    lines = []
    found = False
    
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={new_value}\n")
                    found = True
                else:
                    lines.append(line)
    
    if not found:
        lines.append(f"{key}={new_value}\n")
    
    with open(env_file, "w") as f:
        f.writelines(lines)


def apply_rotations(dry_run=True):
    """Apply secret rotations."""
    tracker = load_rotation_tracker()
    env_file = get_env_path()
    
    rotations = {
        "SESSION_SECRET": rotate_session_secret,
        "JWT_SECRET": rotate_jwt_secret,
    }
    
    applied = {}
    
    for secret_name, rotation_func in rotations.items():
        last_rotation = tracker.get(secret_name, {}).get("last_rotated")
        
        if needs_rotation(last_rotation):
            logger.info(f"Rotating {secret_name}...")
            new_value = rotation_func()
            
            if new_value:
                applied[secret_name] = new_value
                
                if not dry_run:
                    update_env_file(env_file, secret_name, new_value)
                    tracker[secret_name] = {
                        "last_rotated": datetime.datetime.now().isoformat(),
                        "rotated_by": "rotate_secrets.py",
                    }
                    logger.info(f"✅ {secret_name} rotated and saved to {env_file}")
                else:
                    logger.info(f"[DRY RUN] Would rotate {secret_name}")
            else:
                logger.warning(f"⚠️  {secret_name} needs manual rotation (API provider)")
        else:
            logger.info(f"⏭️  {secret_name} does not need rotation yet")
    
    if applied and not dry_run:
        save_rotation_tracker(tracker)
        logger.info(f"✅ Rotation complete. {len(applied)} secret(s) rotated.")
    
    return applied


def main():
    parser = argparse.ArgumentParser(description="Rotate application secrets")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply rotations (default: dry-run)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be rotated (default)",
    )
    
    args = parser.parse_args()
    
    if args.apply:
        logger.info("🔄 Applying secret rotations...")
        apply_rotations(dry_run=False)
    else:
        logger.info("🔍 Dry-run mode: showing what would be rotated...")
        apply_rotations(dry_run=True)


if __name__ == "__main__":
    main()
