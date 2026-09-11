#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APIFY-03-TOOLS: Apify webhook yönetim CLI'si.

Apify webhook'larını kaydet, listele, sil, test et.
Bu script Apify REST API'sini kullanır (apify_client.py'den türetilmiş).

Kullanım:
  python scripts/manage_apify_webhooks.py --list
  python scripts/manage_apify_webhooks.py --register \\
    --actor-id ziyrak/kariyer-scraper \\
    --event-types ACTOR.RUN.SUCCEEDED,ACTOR.RUN.FAILED \\
    --url https://your-domain.com/api/webhooks/apify
  python scripts/manage_apify_webhooks.py --delete <webhook_id>
  python scripts/manage_apify_webhooks.py --test --payload-file sample.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.intelligence.job_intelligence.sources.apify_client import (  # noqa: E402
    ApifyClient,
    ApifyError,
)

APIFY_WEBHOOKS_URL = "https://api.apify.com/v2/webhooks"

# Apify'nin webhook gönderdiği event tipleri
DEFAULT_EVENT_TYPES = [
    "ACTOR.RUN.SUCCEEDED",
    "ACTOR.RUN.FAILED",
    "ACTOR.RUN.ABORTED",
    "ACTOR.RUN.TIMED_OUT",
]


def _get_client() -> ApifyClient:
    token = os.getenv("APIFY_TOKEN")
    if not token:
        print("HATA: APIFY_TOKEN ortam değişkeni gerekli.", file=sys.stderr)
        sys.exit(1)
    return ApifyClient(token=token)


def list_webhooks(client: ApifyClient) -> list[dict[str, Any]]:
    """Kayıtlı webhook'ları listeler."""
    resp = client.session.get(
        f"{client.api_base}/webhooks",
        params={"token": client.token, "limit": 100},
    )
    if resp.status_code != 200:
        raise ApifyError(
            f"Webhook listesi alınamadı ({resp.status_code}): {resp.text[:300]}"
        )
    data = resp.json().get("data", [])
    if isinstance(data, dict):
        data = [data]
    return data


def register_webhook(
    client: ApifyClient,
    actor_id: str,
    url: str,
    event_types: list[str] | None = None,
    secret_token: str | None = None,
) -> dict[str, Any]:
    """Apify'ye yeni bir webhook kaydi yapar."""
    if not event_types:
        event_types = DEFAULT_EVENT_TYPES

    payload: dict[str, Any] = {
        "actorId": actor_id,
        "url": url,
        "eventTypes": event_types,
        "enabled": True,
    }
    if secret_token:
        payload["secret"] = secret_token

    resp = client.session.post(
        f"{client.api_base}/webhooks",
        params={"token": client.token},
        json=payload,
    )
    if resp.status_code not in (200, 201):
        raise ApifyError(f"Webhook kaydolamadı ({resp.status_code}): {resp.text[:300]}")
    webhook = resp.json().get("data", {})

    print(f"Webhook kaydedildi: id={webhook.get('id')}")
    print(f"  actor: {webhook.get('actorId', actor_id)}")
    print(f"  url: {webhook.get('url', url)}")
    print(f"  events: {webhook.get('eventTypes', event_types)}")
    print(f"  enabled: {webhook.get('enabled', True)}")
    if secret_token:
        print("  secret: [AYARLANDI - APFY_WEBHOOK_SECRET env ile eslestir]")
    print()
    print(f"APFY_WEBHOOK_SECRET={secret_token or os.urandom(16).hex()}")
    if not secret_token:
        print(
            "NOT: --secret belirterek kendi tokenınızı kullanın veya yukarıdaki değeri kopyalayın."
        )

    return webhook


def delete_webhook(client: ApifyClient, webhook_id: str) -> bool:
    """Webhook ID'si ile siler."""
    resp = client.session.delete(
        f"{client.api_base}/webhooks/{webhook_id}",
        params={"token": client.token},
    )
    if resp.status_code not in (200, 204):
        raise ApifyError(f"Webhook silinemedi ({resp.status_code}): {resp.text[:300]}")
    print(f"Webhook silindi: {webhook_id}")
    return True


def test_webhook(
    url: str, payload_file: str, secret: str | None = None
) -> dict[str, Any]:
    """Yerel webhook receiver'a test POST gönderir (network gerektirmez)."""
    import json as _json

    with open(payload_file, "r", encoding="utf-8") as f:
        payload = _json.load(f)

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if secret:
        headers["Authorization"] = f"Bearer {secret}"

    import requests as _requests

    try:
        resp = _requests.post(url, json=payload, headers=headers, timeout=30)
        result = {
            "status_code": resp.status_code,
            "response": resp.text[:500] if resp.text else "",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as e:
        print(f"Webhook test hatası: {e}", file=sys.stderr)
        return {"status_code": 0, "response": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apify webhook yönetim aracı (APIFY-03)"
    )
    parser.add_argument(
        "--list", action="store_true", help="Kayıtlı webhook'ları göster"
    )
    parser.add_argument("--register", action="store_true", help="Yeni webhook kaydet")
    parser.add_argument("--delete", metavar="ID", help="Webhook sil")
    parser.add_argument(
        "--test", action="store_true", help="Webhook receiver'a test gönder"
    )
    parser.add_argument("--actor-id", help="Actor ID (örn: ziyrak/kariyer-scraper)")
    parser.add_argument("--url", help="Webhook hedef URL")
    parser.add_argument(
        "--event-types",
        default=",".join(DEFAULT_EVENT_TYPES),
        help=f"Event tipleri (comma-separated). Default: {','.join(DEFAULT_EVENT_TYPES)}",
    )
    parser.add_argument("--payload-file", help="Test için JSON payload dosyası")
    parser.add_argument("--secret", help="Webhook secret token (register için)")
    args = parser.parse_args()

    if args.list:
        client = _get_client()
        webhooks = list_webhooks(client)
        if not webhooks:
            print("Kayıtlı webhook yok.")
            return 0
        print(f"{'ID':<30} {'Actor':<30} {'Events':<20} {'Enabled'}")
        print("-" * 90)
        for wh in webhooks:
            eid = wh.get("id", "")[:30]
            aid = wh.get("actorId", wh.get("actor_id", ""))[:30]
            evts = ",".join(wh.get("eventTypes", wh.get("event_types", [])))[:20]
            enabled = wh.get("enabled", True)
            print(f"{eid:<30} {aid:<30} {evts:<20} {enabled}")
        return 0

    if args.delete:
        client = _get_client()
        delete_webhook(client, args.delete)
        return 0

    if args.register:
        if not args.actor_id or not args.url:
            parser.error("--register için --actor-id ve --url gerekli")
        client = _get_client()
        register_webhook(
            client,
            actor_id=args.actor_id,
            url=args.url,
            event_types=args.event_types.split(","),
            secret_token=args.secret,
        )
        return 0

    if args.test:
        if not args.url or not args.payload_file:
            parser.error("--test için --url ve --payload-file gerekli")
        test_webhook(args.url, args.payload_file, args.secret)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
