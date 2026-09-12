#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9R-05 — 9Router Optimizasyon & İzleme Aracı.

Kullanım:
  python scripts/9router_optimizer.py                 # sağlık taraması + rapor
  python scripts/9router_optimizer.py --probe         # + combo probu (ağ/$$$)
  python scripts/9router_optimizer.py --watch 3600    # periyodik (saatlik)
  python scripts/9router_optimizer.py --backup        # DB yedekleme
  python scripts/9router_optimizer.py --json          # sadece JSON
  python scripts/9router_optimizer.py --db <yol>      # 9router DB yolu override
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# .env otomatik yükleme
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Proje kökünü sys.path'e ekle
def _find_root() -> Path:
    here = Path(__file__).resolve().parent
    for p in [here, here.parent]:
        if (p / "src" / "company_master").exists():
            return p
    return here.parent

ROOT = _find_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Sabitler
DB_DEFAULT = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
SQL_TABLO = "providerConnections"
SECRET_TERMS = ("key", "token", "secret", "pass", "auth", "apikey")
OUTPUT_DIR = ROOT / "data" / "router"
YEDEK_DIR = OUTPUT_DIR / "yedekler"
KARAR_GECMISI = OUTPUT_DIR / "karar_gecmisi.jsonl"
SON_UYARILAR = OUTPUT_DIR / "son_uyarilar.json"

# ---------------------------------------------------------------- Secret maskeleme
def _maskele(v: Any) -> str:
    s = str(v)
    if len(s) <= 8:
        return "****"
    return s[:4] + "..." + s[-4:]

def _is_secret(k: str) -> bool:
    kl = k.lower()
    return any(t in kl for t in SECRET_TERMS)

def _maskele_rek(obj: Any) -> Any:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return {
            k: (_maskele(v) if _is_secret(k) else _maskele_rek(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_maskele_rek(i) for i in obj]
    return obj

# ---------------------------------------------------------------- DB okuma
def _db_baglan(db_path: Path, read_only: bool = True) -> sqlite3.Connection:
    if read_only:
        uri = f"file:{db_path.as_posix()}?mode=ro"
        return sqlite3.connect(uri, uri=True)
    return sqlite3.connect(db_path)

def _db_providerlar(con: sqlite3.Connection) -> list[dict[str, Any]]:
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT provider, authType, name, priority, isActive, data, updatedAt "
        f"FROM {SQL_TABLO} ORDER BY provider"
    ).fetchall()
    
    kayitlar = []
    for r in rows:
        provider = r["provider"]
        data_raw = r["data"]
        data = None
        if data_raw:
            try:
                data = json.loads(data_raw)
            except Exception:
                data = {"HAM": str(data_raw)[:400]}
        
        d = data if isinstance(data, dict) else {}
        ozet = {
            "testStatus": d.get("testStatus"),
            "lastError": d.get("lastError"),
            "errorCode": d.get("errorCode"),
            "backoffLevel": d.get("backoffLevel"),
            "rateLimitedUntil": d.get("rateLimitedUntil"),
        }
        # modelLock'ları say
        kilit_sayisi = 0
        for k in d.keys():
            kl = str(k).lower()
            if kl.startswith("modellock") or kl.startswith("model_lock"):
                kilit_sayisi += 1
        psd = d.get("providerSpecificData")
        if isinstance(psd, dict):
            for k in psd.keys():
                kl = str(k).lower()
                if kl.startswith("modellock") or kl.startswith("model_lock"):
                    kilit_sayisi += 1
        
        kayitlar.append({
            "provider": provider,
            "authType": r["authType"],
            "name": r["name"],
            "priority": r["priority"],
            "isActive": r["isActive"],
            "updatedAt": r["updatedAt"],
            "durum": {**ozet, "modelLockSayisi": kilit_sayisi},
            "data_maskeli": _maskele_rek(data),
        })
    return kayitlar

def _db_request_details(con: sqlite3.Connection, limit: int = 100) -> list[dict[str, Any]]:
    """requestDetails tablosundan son N kayıt (latency, tokens, status)."""
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT timestamp, provider, model, status, data "
        "FROM requestDetails ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    
    kayitlar = []
    for r in rows:
        data_raw = r["data"] or "{}"
        try:
            data = json.loads(data_raw)
        except Exception:
            data = {}
        
        latency = data.get("latency", {})
        tokens = data.get("tokens", {})
        
        kayitlar.append({
            "timestamp": r["timestamp"],
            "provider": r["provider"],
            "model": r["model"],
            "status": r["status"],
            "latency_ttft_ms": latency.get("ttft", 0),
            "latency_total_ms": latency.get("total", 0),
            "prompt_tokens": tokens.get("prompt_tokens", 0),
            "completion_tokens": tokens.get("completion_tokens", 0),
        })
    return kayitlar

def _db_usage_history(con: sqlite3.Connection, limit: int = 500) -> list[dict[str, Any]]:
    """usageHistory tablosundan son N kayıt (provider, model, endpoint, cost, status)."""
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT timestamp, provider, model, endpoint, status, cost, promptTokens, completionTokens "
        "FROM usageHistory ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    return [dict(r) for r in rows]

def _db_settings(con: sqlite3.Connection) -> dict[str, Any]:
    """settings tablosundan ayarlar (comboStrategy, stickyLimit, enableObservability)."""
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
    if not row:
        return {}
    data_raw = row["data"] or "{}"
    try:
        return json.loads(data_raw)
    except Exception:
        return {}

# ---------------------------------------------------------------- Adım A: Sağlık taraması
def saglik_taramasi(db_path: Path) -> dict[str, Any]:
    """DB'den providerConnections oku, durum analizi yap."""
    con = _db_baglan(db_path, read_only=True)
    try:
        providerlar = _db_providerlar(con)
        
        aktif = [p for p in providerlar if p["isActive"] == 1]
        inaktif = [p for p in providerlar if p["isActive"] == 0]
        
        sorunlu = []
        for p in providerlar:
            d = p["durum"]
            sorunlar = []
            backoff = d.get("backoffLevel") or 0
            locks = d.get("modelLockSayisi") or 0
            if backoff >= 5:
                sorunlar.append(f"backoff={backoff}")
            if locks > 10:
                sorunlar.append(f"locks={locks}")
            if d.get("errorCode"):
                sorunlar.append(f"error={d['errorCode']}")
            if d.get("testStatus") == "error":
                sorunlar.append("testStatus=error")
            
            if sorunlar:
                sorunlu.append({
                    "provider": p["provider"],
                    "name": p["name"],
                    "sorunlar": sorunlar,
                    "durum": d,
                })
        
        return {
            "toplam": len(providerlar),
            "aktif": len(aktif),
            "inaktif": len(inaktif),
            "sorunlu_sayisi": len(sorunlu),
            "sorunlu": sorunlu,
            "providerlar": providerlar,
        }
    finally:
        con.close()

# ---------------------------------------------------------------- Adım B1: DB yedekleme
def db_yedekle(db_path: Path, keep: int = 7) -> dict[str, Any]:
    """SQLite backup API ile WAL-safe yedek al, eski yedekleri temizle."""
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    yedek_path = YEDEK_DIR / f"9router_{ts}.sqlite"
    
    src = _db_baglan(db_path, read_only=True)
    try:
        dst = sqlite3.connect(yedek_path)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    
    yedekler = sorted(YEDEK_DIR.glob("9router_*.sqlite"), reverse=True)
    silinen = []
    for eski in yedekler[keep:]:
        try:
            eski.unlink()
            silinen.append(eski.name)
        except Exception as e:
            silinen.append(f"{eski.name}: {e}")
    
    return {
        "yedek_alindi": str(yedek_path),
        "boyut_mb": round(yedek_path.stat().st_size / 1024 / 1024, 2),
        "silinen_yedekler": silinen,
    }

# ---------------------------------------------------------------- Adım B2: Combo RR istatistiği (disk tabanlı)
def combo_rr_istatistik(db_path: Path, limit: int = 500) -> dict[str, Any]:
    """requestDetails + usageHistory'den combo provider dağılımı çıkar.
    
    Provider-bazlı latency ve maliyet istatistikleri de hesaplanır
    (skorla() fonksiyonunda provider-bazlı skorlama için).
    """
    con = _db_baglan(db_path, read_only=True)
    try:
        rd = _db_request_details(con, limit=100)
        
        provider_sayac: dict[str, int] = {}
        status_sayac: dict[str, int] = {"success": 0, "error": 0}
        latency_toplam = 0
        latency_sayac = 0
        
        # Provider-bazlı latency toplama
        prov_latency: dict[str, list[float]] = {}
        # Provider-bazlı status toplama
        prov_status: dict[str, dict[str, int]] = {}
        
        for r in rd:
            prov = r["provider"]
            provider_sayac[prov] = provider_sayac.get(prov, 0) + 1
            status_sayac[r["status"]] = status_sayac.get(r["status"], 0) + 1
            if r["latency_total_ms"] > 0:
                latency_toplam += r["latency_total_ms"]
                latency_sayac += 1
                prov_latency.setdefault(prov, []).append(r["latency_total_ms"])
            
            # Provider-bazlı status
            ps = prov_status.setdefault(prov, {"success": 0, "error": 0})
            ps[r["status"]] = ps.get(r["status"], 0) + 1
        
        ortalama_latency_ms = round(latency_toplam / latency_sayac, 1) if latency_sayac > 0 else 0
        
        # Provider-bazlı ortalama latency
        prov_latency_ort: dict[str, float] = {}
        for prov, degerler in prov_latency.items():
            prov_latency_ort[prov] = round(sum(degerler) / len(degerler), 1) if degerler else 0
        
        uh = _db_usage_history(con, limit=limit)
        
        endpoint_sayac: dict[str, int] = {}
        maliyet_toplam = 0.0
        # Provider-bazlı maliyet
        prov_maliyet: dict[str, float] = {}
        prov_cagri: dict[str, int] = {}
        for r in uh:
            ep = r["endpoint"]
            endpoint_sayac[ep] = endpoint_sayac.get(ep, 0) + 1
            cost = r.get("cost", 0.0) or 0.0
            maliyet_toplam += cost
            prov = r["provider"]
            prov_maliyet[prov] = prov_maliyet.get(prov, 0.0) + cost
            prov_cagri[prov] = prov_cagri.get(prov, 0) + 1
        
        # Provider-bazlı ortalama maliyet
        prov_maliyet_ort: dict[str, float] = {}
        for prov, toplam in prov_maliyet.items():
            cagri = prov_cagri.get(prov, 1)
            prov_maliyet_ort[prov] = round(toplam / cagri, 6) if cagri > 0 else 0
        
        settings = _db_settings(con)
        
        return {
            "requestDetails": {
                "kayit_sayisi": len(rd),
                "provider_dagilimi": provider_sayac,
                "status_dagilimi": status_sayac,
                "ortalama_latency_ms": ortalama_latency_ms,
                "provider_latency_ort": prov_latency_ort,
                "provider_status": prov_status,
            },
            "usageHistory": {
                "kayit_sayisi": len(uh),
                "endpoint_dagilimi": endpoint_sayac,
                "toplam_maliyet_usd": round(maliyet_toplam, 4),
                "provider_maliyet_toplam": {k: round(v, 4) for k, v in prov_maliyet.items()},
                "provider_maliyet_ort": prov_maliyet_ort,
                "provider_cagri_sayisi": prov_cagri,
            },
            "settings": {
                "comboStrategy": settings.get("comboStrategy"),
                "comboStickyRoundRobinLimit": settings.get("comboStickyRoundRobinLimit"),
                "enableObservability": settings.get("enableObservability"),
            },
        }
    finally:
        con.close()

# ---------------------------------------------------------------- Adım C: Skorlama
def skorla(saglik: dict, combo_ist: dict) -> list[dict[str, Any]]:
    """Her provider için skor hesapla: %50 sağlık / %25 hız / %25 maliyet.
    
    Hız ve maliyet skorları provider-bazlıdır (requestDetails/usageHistory'den
    per-provider ortalama latency ve maliyet kullanılır). Verisi olmayan
    provider'lar için genel ortalama kullanılır.
    """
    rd = combo_ist["requestDetails"]
    uh = combo_ist["usageHistory"]
    genel_latency = rd.get("ortalama_latency_ms", 0)
    prov_latency_ort = rd.get("provider_latency_ort", {})
    prov_maliyet_ort = uh.get("provider_maliyet_ort", {})
    
    # Maliyet skoru için referans: tüm provider'ların ortalama maliyeti
    maliyetler = list(prov_maliyet_ort.values())
    referans_maliyet = sum(maliyetler) / len(maliyetler) if maliyetler else 0.0
    
    skorlar = []

    for p in saglik["providerlar"]:
        saglik_skor = 100
        d = p["durum"]
        backoff = d.get("backoffLevel") or 0
        locks = d.get("modelLockSayisi") or 0
        if backoff >= 5:
            saglik_skor -= 30
        if locks > 10:
            saglik_skor -= 20
        if d.get("errorCode"):
            saglik_skor -= 40
        if d.get("testStatus") == "error":
            saglik_skor -= 40
        if p["isActive"] == 0:
            saglik_skor = 0
        
        # Provider-bazlı hız skoru (veri yoksa nötr 75 — ölçülmemişi 100 gösterme)
        hiz_skor = 75
        prov_latency = prov_latency_ort.get(p["provider"])
        if prov_latency is not None:
            if prov_latency > 10000:
                hiz_skor = 25
            elif prov_latency > 5000:
                hiz_skor = 50
            elif prov_latency > 2000:
                hiz_skor = 75
            else:
                hiz_skor = 100
        elif genel_latency > 0:
            # Verisi yoksa genel ortalamaya göre
            if genel_latency > 10000:
                hiz_skor = 25
            elif genel_latency > 5000:
                hiz_skor = 50
            elif genel_latency > 2000:
                hiz_skor = 75
        
        # Provider-bazlı maliyet skoru (0 = ideal, referansın 3x'i = 0; veri yoksa nötr 75)
        maliyet_skor = 75
        prov_maliyet = prov_maliyet_ort.get(p["provider"])
        if prov_maliyet is not None and referans_maliyet > 0:
            oran = prov_maliyet / referans_maliyet
            if oran >= 3.0:
                maliyet_skor = 0
            elif oran >= 2.0:
                maliyet_skor = 25
            elif oran >= 1.5:
                maliyet_skor = 50
            elif oran >= 1.0:
                maliyet_skor = 75
            else:
                maliyet_skor = 100
        elif prov_maliyet is not None:
            # Maliyet verisi var ama referans yok (tek provider) — 0 maliyet ideal
            maliyet_skor = 100 if prov_maliyet == 0 else 75
        
        toplam_skor = (
            saglik_skor * 0.50 +
            hiz_skor * 0.25 +
            maliyet_skor * 0.25
        )
        
        skorlar.append({
            "provider": p["provider"],
            "name": p["name"],
            "saglik": saglik_skor,
            "hiz": hiz_skor,
            "maliyet": maliyet_skor,
            "toplam": round(toplam_skor, 1),
            "latency_ms": prov_latency_ort.get(p["provider"]),
            "maliyet_ort_usd": prov_maliyet_ort.get(p["provider"]),
        })
    
    skorlar.sort(key=lambda x: x["toplam"], reverse=True)
    return skorlar

# ---------------------------------------------------------------- Adım D: Anomali tespiti
def anomali_tespit(saglik: dict, combo_ist: dict) -> list[dict[str, Any]]:
    """Anomali imzalarını tespit et: backoff >=5, locks >10, error rate yüksek."""
    anomaliler = []
    
    for p in saglik["providerlar"]:
        d = p["durum"]
        nedenler = []

        backoff = d.get("backoffLevel") or 0
        locks = d.get("modelLockSayisi") or 0
        if backoff >= 5:
            nedenler.append(f"backoffLevel={backoff} (eşik: 5)")
        if locks > 10:
            nedenler.append(f"modelLockSayisi={locks} (eşik: 10)")
        if d.get("errorCode"):
            nedenler.append(f"errorCode={d['errorCode']}")
        if d.get("testStatus") == "error":
            nedenler.append("testStatus=error")
        
        if nedenler:
            anomaliler.append({
                "provider": p["provider"],
                "name": p["name"],
                "nedenler": nedenler,
                "oncelik": "YUKSEK" if len(nedenler) >= 2 else "ORTA",
            })
    
    return anomaliler

# ---------------------------------------------------------------- Adım E: Çıktılar
def konsol_cikti(saglik: dict, skorlar: list, anomaliler: list, combo_ist: dict) -> None:
    """Renkli konsol çıktısı (3 bölüm: Sağlık / Skor & Öneri / Uyarılar)."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    SIFIR = "\033[0m"
    
    print(f"\n{MAVI}{'='*70}{SIFIR}")
    print(f"{MAVI}9R-05 — 9Router Optimizasyon Raporu{SIFIR}")
    print(f"{MAVI}{'='*70}{SIFIR}\n")
    
    print(f"{YESIL}BÖLÜM 1: SAĞLIK TARAMASI{SIFIR}")
    print(f"  Toplam provider: {saglik['toplam']}")
    print(f"  Aktif: {saglik['aktif']}")
    print(f"  İnaktif: {saglik['inaktif']}")
    print(f"  Sorunlu: {saglik['sorunlu_sayisi']}")
    
    if saglik["sorunlu"]:
        print(f"\n  {KIRMIZI}Sorunlu providerlar:{SIFIR}")
        for s in saglik["sorunlu"][:5]:
            print(f"    - {s['provider']} ({s['name']}): {', '.join(s['sorunlar'])}")
    
    print(f"\n{YESIL}BÖLÜM 2: SKOR & ÖNERİ{SIFIR}")
    print(f"  Combo RR istatistik: {combo_ist['settings']}")
    print(f"  RequestDetails: {combo_ist['requestDetails']['kayit_sayisi']} kayıt")
    print(f"  Ortalama latency: {combo_ist['requestDetails']['ortalama_latency_ms']}ms")
    print(f"  Toplam maliyet (son 500): ${combo_ist['usageHistory']['toplam_maliyet_usd']}")
    
    print(f"\n  {MAVI}En iyi 5 provider (skora göre):{SIFIR}")
    for s in skorlar[:5]:
        latency = f"{s['latency_ms']:.0f}ms" if s.get("latency_ms") else "-"
        maliyet = f"${s['maliyet_ort_usd']:.4f}" if s.get("maliyet_ort_usd") is not None else "-"
        print(f"    {s['provider']:<20} skor={s['toplam']:.1f} (sağlık={s['saglik']}, hız={s['hiz']}, maliyet={s['maliyet']}, lat={latency}, $={maliyet})")
    
    # Provider-bazlı latency/maliyet detayı
    prov_latency = combo_ist["requestDetails"].get("provider_latency_ort", {})
    prov_maliyet = combo_ist["usageHistory"].get("provider_maliyet_ort", {})
    if prov_latency or prov_maliyet:
        print(f"\n  {MAVI}Provider-bazlı ölçümler:{SIFIR}")
        for prov in sorted(set(list(prov_latency.keys()) + list(prov_maliyet.keys()))):
            lat = f"{prov_latency[prov]:.0f}ms" if prov in prov_latency else "-"
            maliyet = f"${prov_maliyet[prov]:.4f}" if prov in prov_maliyet else "-"
            print(f"    {prov:<20} lat={lat:<10} maliyet/çağrı={maliyet}")
    
    print(f"\n{YESIL}BÖLÜM 3: UYARILAR{SIFIR}")
    if anomaliler:
        for a in anomaliler[:5]:
            oncelik_renk = KIRMIZI if a["oncelik"] == "YUKSEK" else SARI
            print(f"  {oncelik_renk}[{a['oncelik']}]{SIFIR} {a['provider']} ({a['name']}): {', '.join(a['nedenler'])}")
    else:
        print(f"  {YESIL}Anomali tespit edilmedi.{SIFIR}")
    
    print(f"\n{MAVI}{'='*70}{SIFIR}\n")

def json_cikti(saglik: dict, skorlar: list, anomaliler: list, combo_ist: dict) -> dict:
    """JSON çıktısı (makine okunabilir)."""
    return {
        "timestamp": datetime.now().isoformat(),
        "saglik": saglik,
        "skorlar": skorlar,
        "anomaliler": anomaliler,
        "combo_istatistik": combo_ist,
    }

def markdown_rapor(saglik: dict, skorlar: list, anomaliler: list, combo_ist: dict) -> str:
    """Markdown rapor (data/router/optimizer_<tarih>.md)."""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    lines = [
        f"# 9R-05 Optimizasyon Raporu — {ts}\n",
        "## 1. Sağlık Taraması\n",
        f"- Toplam provider: {saglik['toplam']}",
        f"- Aktif: {saglik['aktif']}",
        f"- İnaktif: {saglik['inaktif']}",
        f"- Sorunlu: {saglik['sorunlu_sayisi']}\n",
    ]
    
    if saglik["sorunlu"]:
        lines.append("### Sorunlu Providerlar\n")
        for s in saglik["sorunlu"]:
            lines.append(f"- **{s['provider']}** ({s['name']}): {', '.join(s['sorunlar'])}")
        lines.append("")
    
    lines.extend([
        "## 2. Skor & Öneri\n",
        f"- Combo RR: {combo_ist['settings']}",
        f"- RequestDetails: {combo_ist['requestDetails']['kayit_sayisi']} kayıt",
        f"- Ortalama latency: {combo_ist['requestDetails']['ortalama_latency_ms']}ms",
        f"- Toplam maliyet: ${combo_ist['usageHistory']['toplam_maliyet_usd']}\n",
        "### En İyi 5 Provider\n",
    ])
    for s in skorlar[:5]:
        latency = f"{s['latency_ms']:.0f}ms" if s.get("latency_ms") else "-"
        maliyet = f"${s['maliyet_ort_usd']:.4f}" if s.get("maliyet_ort_usd") is not None else "-"
        lines.append(f"- {s['provider']}: skor={s['toplam']:.1f} (sağlık={s['saglik']}, hız={s['hiz']}, maliyet={s['maliyet']}, lat={latency}, $={maliyet})")
    lines.append("")
    
    # Provider-bazlı ölçümler tablosu
    prov_latency = combo_ist["requestDetails"].get("provider_latency_ort", {})
    prov_maliyet = combo_ist["usageHistory"].get("provider_maliyet_ort", {})
    if prov_latency or prov_maliyet:
        lines.extend([
            "### Provider-bazlı Ölçümler\n",
            "| Provider | Ort. Latency (ms) | Ort. Maliyet/Çağrı ($) |",
            "|----------|-------------------|------------------------|",
        ])
        for prov in sorted(set(list(prov_latency.keys()) + list(prov_maliyet.keys()))):
            lat = f"{prov_latency[prov]:.0f}" if prov in prov_latency else "-"
            maliyet = f"{prov_maliyet[prov]:.4f}" if prov in prov_maliyet else "-"
            lines.append(f"| {prov} | {lat} | {maliyet} |")
        lines.append("")
    
    if anomaliler:
        lines.extend([
            "## 3. Uyarılar\n",
        ])
        for a in anomaliler:
            lines.append(f"- **[{a['oncelik']}]** {a['provider']}: {', '.join(a['nedenler'])}")
        lines.append("")
    
    return "\n".join(lines)

# ---------------------------------------------------------------- Telegram bildirimi
def telegram_bildir(anomaliler: list) -> None:
    """Anomali listesini Telegram'a gönder (sentinel ile tekrar engelleme)."""
    if not anomaliler:
        return
    
    sentinel: dict[str, str] = {}
    if SON_UYARILAR.exists():
        try:
            sentinel = json.loads(SON_UYARILAR.read_text(encoding="utf-8"))
        except Exception:
            sentinel = {}
    
    simdi = datetime.now()
    yeni_anomaliler = []
    for a in anomaliler:
        key = f"{a['provider']}:{','.join(sorted(a['nedenler']))}"
        son_bildirim = sentinel.get(key)
        if son_bildirim:
            try:
                son_dt = datetime.fromisoformat(son_bildirim)
                if (simdi - son_dt).total_seconds() < 3600:
                    continue
            except Exception:
                pass
        yeni_anomaliler.append(a)
        sentinel[key] = simdi.isoformat()
    
    if not yeni_anomaliler:
        return
    
    mesaj = "🚨 9Router Anomali Uyarısı\n\n"
    for a in yeni_anomaliler[:5]:
        mesaj += f"[{a['oncelik']}] {a['provider']}: {', '.join(a['nedenler'])}\n"
    
    try:
        from src.company_master.utils.telegram_bot import send_telegram_message
        send_telegram_message(mesaj)
    except Exception as e:
        print(f"[WARN] Telegram gönderilemedi: {e}", file=sys.stderr)
    
    SON_UYARILAR.parent.mkdir(parents=True, exist_ok=True)
    SON_UYARILAR.write_text(json.dumps(sentinel, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------- Ana akış
def main() -> int:
    parser = argparse.ArgumentParser(description="9R-05 — 9Router Optimizasyon & İzleme Aracı")
    parser.add_argument("--db", type=Path, default=DB_DEFAULT, help="9router DB yolu")
    parser.add_argument("--probe", action="store_true", help="Combo probu yap (ağ/$$$ gerekli)")
    parser.add_argument("--limit-probes", type=int, default=5, help="Bir turda max prob sayısı")
    parser.add_argument("--backup", action="store_true", help="DB yedekleme yap")
    parser.add_argument("--backup-keep", type=int, default=7, help="Kaç yedek saklansın")
    parser.add_argument("--watch", type=int, metavar="SN", help="Periyodik mod (saniye)")
    parser.add_argument("--json", action="store_true", help="Sadece JSON çıktısı")
    parser.add_argument("--no-telegram", action="store_true", help="Telegram bildirimini devre dışı bırak")
    
    args = parser.parse_args()
    
    if not args.db.exists():
        print(f"[HATA] 9router DB bulunamadı: {args.db}", file=sys.stderr)
        return 2
    
    def tur() -> None:
        saglik = saglik_taramasi(args.db)
        
        if args.backup:
            yedek = db_yedekle(args.db, keep=args.backup_keep)
            print(f"[BİLGİ] DB yedek alındı: {yedek['yedek_alindi']} ({yedek['boyut_mb']}MB)")
        
        combo_ist = combo_rr_istatistik(args.db)
        
        skorlar = skorla(saglik, combo_ist)
        
        anomaliler = anomali_tespit(saglik, combo_ist)
        
        if args.json:
            print(json.dumps(json_cikti(saglik, skorlar, anomaliler, combo_ist), ensure_ascii=False, indent=2))
        else:
            konsol_cikti(saglik, skorlar, anomaliler, combo_ist)
            
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M")
            rapor_path = OUTPUT_DIR / f"optimizer_{ts}.md"
            rapor_path.write_text(markdown_rapor(saglik, skorlar, anomaliler, combo_ist), encoding="utf-8")
            print(f"[BİLGİ] Markdown rapor: {rapor_path}")
            
            json_path = OUTPUT_DIR / "optimizer_latest.json"
            json_path.write_text(json.dumps(json_cikti(saglik, skorlar, anomaliler, combo_ist), ensure_ascii=False, indent=2), encoding="utf-8")
        
        if not args.no_telegram:
            telegram_bildir(anomaliler)
    
    if args.watch:
        print(f"[BİLGİ] Periyodik mod: her {args.watch} saniyede bir tur")
        try:
            while True:
                tur()
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\n[BİLGİ] Ctrl+C ile kapatıldı.")
    else:
        tur()
    
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
