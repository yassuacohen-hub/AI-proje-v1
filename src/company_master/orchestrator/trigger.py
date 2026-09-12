# -*- coding: utf-8 -*-
"""ORCH-08: Görev tetikleme postası + teslim/onay kuyruğu.

Sorun: görev panoya yazılıyor ama ajan bunu ancak panoyu elle açarsa
görüyordu. Bu modül her ajana bir "posta kutusu" ekler: atama anında
tetik düşer, ajan tek komutla postasını okur.

Doğrulama zorunluluğu: ajan işi bitirince görev doğrudan `done` OLMaz.
Teslim önce `review` durumuna düşer ve kontrolör onayı (`onayla`) ya da
red (`reddet`) bekler. Onaysız `done` geçersizdir; reddedilen iş ajanın
düzeltmesi için `aktif`'e geri döner.

Dosyalar:
    data/orchestrator/triggers/{ajan}.jsonl  -> ajan postası (tetikler)
    data/orchestrator/onay_kuyrugu.json      -> teslim edilmiş, onay bekleyenler
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.company_master.orchestrator import task_board as tb


class TriggerError(Exception):
    """Tetikleme/onay kuyruğu işlemi reddedildi."""


def _data_dir(data_dir: Path | None) -> Path:
    return Path(data_dir) if data_dir else tb.STATE_DIR


def _simdi() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---- Posta kutusu (tetikler) ----

def _tetik_yolu(ajan: str, data_dir: Path | None = None) -> Path:
    return _data_dir(data_dir) / "triggers" / f"{ajan}.jsonl"


def _tetikleri_oku(ajan: str, data_dir: Path | None = None) -> list[dict[str, Any]]:
    yol = _tetik_yolu(ajan, data_dir)
    if not yol.exists():
        return []
    kayitlar: list[dict[str, Any]] = []
    for satir in yol.read_text(encoding="utf-8").splitlines():
        satir = satir.strip()
        if satir:
            kayitlar.append(json.loads(satir))
    return kayitlar


def _tetikleri_yaz(
    kayitlar: list[dict[str, Any]], ajan: str, data_dir: Path | None = None
) -> None:
    yol = _tetik_yolu(ajan, data_dir)
    yol.parent.mkdir(parents=True, exist_ok=True)
    icerik = "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in kayitlar)
    tb.atomic_write_text(yol, icerik)


def tetik_ekle(
    task_id: str, ajan: str, talimat: str = "", data_dir: Path | None = None
) -> dict[str, Any]:
    """Ajanın postasına yeni görev tetikle. Aynı görev için tekrar düşmez."""
    kayitlar = _tetikleri_oku(ajan, data_dir)
    if any(k["task_id"] == task_id and k["durum"] == "bekliyor" for k in kayitlar):
        raise TriggerError(f"{ajan} için bekleyen tetik zaten var: {task_id}")
    kayit = {
        "task_id": task_id,
        "ajan": ajan,
        "talimat": talimat,
        "tarih": _simdi(),
        "durum": "bekliyor",  # bekliyor -> alindi -> teslim
    }
    kayitlar.append(kayit)
    _tetikleri_yaz(kayitlar, ajan, data_dir)
    return kayit


def bekleyen_tetikler(ajan: str, data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Ajanın henüz almadığı (okunmamış) görevleri listele."""
    return [k for k in _tetikleri_oku(ajan, data_dir) if k["durum"] == "bekliyor"]


def tetik_al(
    ajan: str, task_id: str, data_dir: Path | None = None
) -> dict[str, Any]:
    """Tetiği 'alindi' yap ve panodaki görevi aktife çek.
    Bekleyen tetik yoksa TriggerError (ajan panoyu elle kontrol etmiş demektir)."""
    kayitlar = _tetikleri_oku(ajan, data_dir)
    bulundu = False
    for k in kayitlar:
        if k["task_id"] == task_id and k["durum"] == "bekliyor":
            k["durum"] = "alindi"
            k["alma_tarihi"] = _simdi()
            bulundu = True
    if not bulundu:
        raise TriggerError(f"{ajan} için bekleyen tetik yok: {task_id}")
    if tb.gorev_getir(task_id) is None:
        raise TriggerError(f"Görev panoda bulunamadı: {task_id}")
    _tetikleri_yaz(kayitlar, ajan, data_dir)
    tb.gorev_guncelle(task_id, durum="aktif")
    return {"task_id": task_id, "ajan": ajan, "durum": "alindi"}


# ---- Onay kuyruğu (doğrulama zorunluluğu) ----

def _kuyruk_yolu(data_dir: Path | None) -> Path:
    return _data_dir(data_dir) / "onay_kuyrugu.json"


def _kuyruk_oku(data_dir: Path | None) -> list[dict[str, Any]]:
    yol = _kuyruk_yolu(data_dir)
    if not yol.exists():
        return []
    return json.loads(yol.read_text(encoding="utf-8-sig"))


def _kuyruk_yaz(kuyruk: list[dict[str, Any]], data_dir: Path | None) -> None:
    tb.atomic_write_text(
        _kuyruk_yolu(data_dir), json.dumps(kuyruk, ensure_ascii=False, indent=2)
    )


def teslim_et(
    task_id: str,
    ajan: str,
    ozet: str,
    ciktilar: list[str] | None = None,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Ajan işi teslim eder. Görev `review`'a düşer; `done` olması
    kontrolör onayına bağlıdır. Çift teslim engellenir."""
    if not ozet.strip():
        raise TriggerError("Teslim özeti boş olamaz")
    kuyruk = _kuyruk_oku(data_dir)
    if any(k["task_id"] == task_id and k["durum"] == "bekliyor" for k in kuyruk):
        raise TriggerError(f"{task_id} zaten onay kuyruğunda")
    kuyruk.append({
        "task_id": task_id,
        "ajan": ajan,
        "ozet": ozet,
        "ciktilar": ciktilar or [],
        "teslim_tarihi": _simdi(),
        "durum": "bekliyor",  # bekliyor -> onaylandi / reddedildi
    })
    _kuyruk_yaz(kuyruk, data_dir)
    tb.gorev_guncelle(task_id, durum="review", **{"not": f"Teslim ({ajan}): {ozet}"})
    kayitlar = _tetikleri_oku(ajan, data_dir)
    for k in kayitlar:
        if k["task_id"] == task_id and k["durum"] == "alindi":
            k["durum"] = "teslim"
            k["teslim_tarihi"] = _simdi()
    _tetikleri_yaz(kayitlar, ajan, data_dir)
    return {"task_id": task_id, "durum": "review"}


def onay_bekleyenler(data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Kontrolörün inceleyeceği teslimler."""
    return [k for k in _kuyruk_oku(data_dir) if k["durum"] == "bekliyor"]


def _kuyruk_guncelle(
    task_id: str, data_dir: Path | None, **alanlar: Any
) -> dict[str, Any]:
    kuyruk = _kuyruk_oku(data_dir)
    for k in kuyruk:
        if k["task_id"] == task_id and k["durum"] == "bekliyor":
            k.update(alanlar)
            _kuyruk_yaz(kuyruk, data_dir)
            return k
    raise TriggerError(f"Onay kuyruğunda bulunamadı: {task_id}")


def onayla(
    task_id: str, onaylayan: str, data_dir: Path | None = None
) -> dict[str, Any]:
    """Kontrolör onayı → görev `done` (ORCH-05 tüm kilitleri otomatik düşürür)."""
    k = _kuyruk_guncelle(
        task_id, data_dir,
        durum="onaylandi", onaylayan=onaylayan, onay_tarihi=_simdi(),
    )
    tb.gorev_guncelle(task_id, durum="done")
    return k


def reddet(
    task_id: str, onaylayan: str, neden: str, data_dir: Path | None = None
) -> dict[str, Any]:
    """Kontrolör reddi → görev `aktif`'e geri döner; ajan nedenle düzeltir.
    Kilitler düşmez (iş sahanın ajanında kalmaya devam eder)."""
    if not neden.strip():
        raise TriggerError("Reddetme nedeni zorunludur")
    k = _kuyruk_guncelle(
        task_id, data_dir,
        durum="reddedildi", onaylayan=onaylayan, onay_tarihi=_simdi(),
        red_nedeni=neden,
    )
    tb.gorev_guncelle(task_id, durum="aktif", **{"not": f"Red ({onaylayan}): {neden}"})
    return k
