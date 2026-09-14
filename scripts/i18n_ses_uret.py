# -*- coding: utf-8 -*-
"""MRK-02c — Marka sesi kaynağını `i18n/ses.json` şemasına dönüştüren üretici.

Girdi:  `../projemdeki dil klasörüne yerleştir ve kod içinde kullan.json`
        Yapı: {"tr": {anahtar: metin}, "en": {anahtar: metin}} — 105 anahtar.

Çıktı:  `src/company_master/i18n/ses.json`
        Yapı: {anahtar: {"tr": ..., "en": ..., "katman": ..., "ton": ..., "ikon": ...}}

Neden script?
    105 kaydı elle yazmak hem token israfı hem hata kaynağıdır. Metinler
    kaynaktan otomatik akar; yalnızca **ton/ikon/katman kararları** burada
    kod olarak durur ve denetlenebilir.

Kullanım:
    python scripts/i18n_ses_uret.py            # üret
    python scripts/i18n_ses_uret.py --kontrol  # yalnız rapor, dosya yazma
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

KOK = Path(__file__).resolve().parents[1]
KAYNAK = KOK.parent / "projemdeki dil klasörüne yerleştir ve kod içinde kullan.json"
HEDEF = KOK / "src" / "company_master" / "i18n" / "ses.json"

# --------------------------------------------------------------------------
# 1) Kaynak metin düzeltmeleri (kaynakta tespit edilen dil hataları)
# --------------------------------------------------------------------------
#: Kaynak JSON'da TR metne sızmış İngilizce sözcükler / yazım hataları.
METIN_DUZELTME: dict[tuple[str, str], str] = {
    ("tr", "odin_runes_aligned"): "Sistem parametreleri hizalandı. Operasyon sorunsuz.",
}

# --------------------------------------------------------------------------
# 2) Ton kararları
# --------------------------------------------------------------------------
#: Desenle doğru sonuç vermeyen anahtarlar burada açıkça belirtilir.
#: Örn. "brute_force_block" bir saldırının **engellendiğini** anlatır → success.
TON_ISTISNA: dict[str, str] = {
    # Güvenlik: tehdit bertaraf edildi → başarı
    "muninn_brute_force_block": "success",
    "muninn_threat_neutralized": "success",
    "muninn_data_leak_shield": "success",
    "muninn_access_denied": "danger",
    "muninn_root_warn": "warning",
    "muninn_session_timeout": "warning",
    "muninn_mfa_required": "warning",
    "muninn_data_purge": "warning",
    "muninn_lock_changes": "warning",
    "muninn_password_policy": "info",
    "muninn_key_rotation": "info",
    "muninn_query_history": "neutral",
    "muninn_immutable_log": "neutral",
    "muninn_recovery_point": "neutral",
    "muninn_admin_session": "neutral",
    "muninn_storage_status": "neutral",
    "muninn_role_assigned": "success",
    "muninn_gdpr_export": "info",
    # Canlı izleme: dikkat çeken olaylar
    "huginn_anomaly_spotted": "warning",
    "huginn_speed_alert": "warning",
    "huginn_user_surge": "warning",
    "huginn_error_intercept": "warning",
    "huginn_live_feed_pause": "warning",
    "huginn_queue_status": "neutral",
    "huginn_session_count": "neutral",
    "huginn_bot_detection": "warning",
    "huginn_incident_resolved": "success",
    "huginn_performance_peak": "success",
    "huginn_latency_low": "success",
    # Çekirdek
    "odin_uncompromised_safety": "success",
    "odin_total_control": "success",
    "odin_valhalla_tier": "info",
    "odin_end_of_day_sync": "neutral",
    "odin_command_center": "neutral",
    "odin_throne_welcome": "info",
}

#: Sıralı desen listesi — ilk eşleşen ton kazanır.
TON_DESENLERI: tuple[tuple[str, str], ...] = (
    (r"_(denied|error|breach|leak|threat|intercept)$", "danger"),
    (r"_(warn|alert|required|timeout|pause|surge|spotted)$", "warning"),
    (
        r"_(success|complete|completed|ok|granted|ready|applied|verified|valid"
        r"|resolved|secured|safe|clear|neutralized|shield|optimized|aligned"
        r"|restore|peak|harmony|milestone|low)$",
        "success",
    ),
    (r"_(status|count|history|log|point|session|mode|tier|trail)$", "neutral"),
)

#: Bazı anahtarlar için ton varsayılanının üstüne özel ikon.
IKON_OZEL: dict[str, str] = {
    "huginn_pulse_check": "monitor_heart",
    "huginn_active_users": "group",
    "huginn_realtime_sync": "sync",
    "huginn_anomaly_spotted": "radar",
    "huginn_live_traffic": "traffic",
    "huginn_watchtower_ready": "visibility",
    "huginn_realtime_chart": "monitoring",
    "huginn_api_health": "api",
    "huginn_server_pulse": "dns",
    "huginn_queue_status": "queue",
    "huginn_latency_low": "speed",
    "muninn_vault_safe": "lock",
    "muninn_memory_locked": "lock",
    "muninn_backup_success": "backup",
    "muninn_encryption_active": "enhanced_encryption",
    "muninn_archive_complete": "inventory_2",
    "muninn_audit_trail_ready": "fact_check",
    "muninn_key_rotation": "key",
    "muninn_mfa_required": "phonelink_lock",
    "muninn_gdpr_export": "download",
    "muninn_immutable_log": "history_edu",
    "odin_throne_welcome": "chair",
    "odin_eyes_on_you": "visibility",
    "odin_command_center": "dashboard",
    "odin_bifrost_active": "hub",
    "odin_ai_co_pilot": "smart_toy",
    "odin_global_teleport": "public",
    "odin_shield_wall": "shield",
    "odin_runes_aligned": "tune",
    "odin_nexus_online": "lan",
    "odin_epic_milestone": "emoji_events",
}

ONEKLER: tuple[str, ...] = ("huginn_", "muninn_", "odin_")


def ton_belirle(anahtar: str) -> str:
    """Anahtar adından tonu türetir (istisna > desen > varsayılan)."""
    if anahtar in TON_ISTISNA:
        return TON_ISTISNA[anahtar]
    for desen, ton in TON_DESENLERI:
        if re.search(desen, anahtar):
            return ton
    return "info"


def kaynak_oku(yol: Path) -> dict[str, dict[str, str]]:
    """Kaynak JSON'u okur ve `tr`/`en` bloklarını doğrular."""
    if not yol.exists():
        raise SystemExit(f"Kaynak bulunamadi: {yol}")
    veri = json.loads(yol.read_text(encoding="utf-8"))
    for dil in ("tr", "en"):
        if dil not in veri:
            raise SystemExit(f"Kaynakta '{dil}' blogu yok.")
    tr_anahtar = set(veri["tr"])
    en_anahtar = set(veri["en"])
    if tr_anahtar != en_anahtar:
        eksik = tr_anahtar ^ en_anahtar
        raise SystemExit(f"tr/en anahtar kumeleri esit degil: {sorted(eksik)}")
    return veri


def donustur(veri: dict[str, dict[str, str]]) -> dict[str, dict[str, Any]]:
    """Düz metin sözlüğünü katman/ton/ikon şemasına çevirir."""
    cikti: dict[str, dict[str, Any]] = {}
    for anahtar in sorted(veri["tr"]):
        if not anahtar.startswith(ONEKLER):
            raise SystemExit(f"Onek kurali ihlali: {anahtar}")
        tr = METIN_DUZELTME.get(("tr", anahtar), veri["tr"][anahtar])
        en = METIN_DUZELTME.get(("en", anahtar), veri["en"][anahtar])
        kayit: dict[str, Any] = {
            "tr": tr,
            "en": en,
            # Kaynaktaki 105 metnin tamamı anlatısal/mitolojiktir; hiçbiri
            # müşterinin karar verdiği bir rakamı veya hata kodunu taşımaz.
            "katman": "cerceve",
            "ton": ton_belirle(anahtar),
        }
        ikon = IKON_OZEL.get(anahtar)
        if ikon:
            kayit["ikon"] = ikon
        cikti[anahtar] = kayit
    return cikti


def _ton_dagilimi(kayitlar: dict[str, dict[str, Any]]) -> dict[str, int]:
    dagilim: dict[str, int] = {}
    for kayit in kayitlar.values():
        dagilim[kayit["ton"]] = dagilim.get(kayit["ton"], 0) + 1
    return dict(sorted(dagilim.items()))


def main() -> int:
    ayristirici = argparse.ArgumentParser(description="Marka sesi ses.json ureticisi")
    ayristirici.add_argument("--kaynak", default=str(KAYNAK), help="Kaynak JSON yolu")
    ayristirici.add_argument("--hedef", default=str(HEDEF), help="Cikti ses.json yolu")
    ayristirici.add_argument(
        "--kontrol", action="store_true", help="Dosya yazma, yalniz rapor ver"
    )
    args = ayristirici.parse_args()

    veri = kaynak_oku(Path(args.kaynak))
    kayitlar = donustur(veri)

    print(f"Kaynak anahtar sayisi : {len(kayitlar)}")
    for onek in ONEKLER:
        adet = sum(1 for a in kayitlar if a.startswith(onek))
        print(f"  {onek:<9}: {adet}")
    print(f"Ton dagilimi          : {_ton_dagilimi(kayitlar)}")
    print(f"Ozel ikonlu kayit     : {sum(1 for k in kayitlar.values() if 'ikon' in k)}")

    if args.kontrol:
        print("[kontrol] Dosya yazilmadi.")
        return 0

    hedef = Path(args.hedef)
    hedef.parent.mkdir(parents=True, exist_ok=True)
    metin = json.dumps(kayitlar, ensure_ascii=False, indent=2) + "\n"
    hedef.write_text(metin, encoding="utf-8")
    print(f"Yazildi: {hedef}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
