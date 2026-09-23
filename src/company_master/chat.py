# -*- coding: utf-8 -*-
"""Ajan Chat Sistemi — D-192 Library.

Append-only JSONL log + lock-safe operations.
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

# ponytail: thread-local lock; upgrade to multiprocess Lock if needed
_LOCK = threading.RLock()


def _data_dir() -> Path:
    """Chat veri dizini."""
    d = Path(__file__).parent.parent.parent / "data" / "orchestrator"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _log_path(name: str = "ajan-chat") -> Path:
    """JSONL dosya yolu."""
    return _data_dir() / f"{name}.jsonl"


def _ensure_log(name: str = "ajan-chat") -> None:
    """Log dosyası varsa oku, yoksa boş oluştur."""
    p = _log_path(name)
    if not p.exists():
        p.touch()


def _ajan_normalize(ad: str | None) -> str:
    """Ajan adını kanonik forma çevir."""
    if not ad:
        return "unknown"
    ad = ad.lower().strip()
    if ad in ("ihsan", "utku", "salih", "yasu"):
        return ad
    # Fallback
    return ad


def ac(
    ajan: str,
    task_id: str,
    sorun: str,
    cozum: str = "",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Sorun aç (problem kayıt).
    
    Args:
        ajan: ajan adı
        task_id: görev ID
        sorun: 1-200 char alıntı
        cozum: 0-300 char çözüm önerisi (isteğe bağlı)
        data_dir: test için custom data dir
    
    Returns:
        Eklenen satır (dict)
    """
    _ensure_log()
    
    satir = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "ajan": _ajan_normalize(ajan),
        "task_id": task_id.upper(),
        "sorun": sorun[:200],
        "cozum": cozum[:300] if cozum else "",
        "durum": "acik",
        "link": "",
    }
    
    satir_json = json.dumps(satir, ensure_ascii=False) + "\n"
    
    # Atomic append
    with _LOCK:
        p = _log_path() if data_dir is None else data_dir / "ajan-chat.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(satir_json)
    
    return satir


def guncelle(
    task_id: str,
    sorun_index: int,
    cozum_guncel: str = "",
    durum: str = "cokundurmus",
    data_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Sorunun çözümünü güncelle.
    
    Args:
        task_id: görev ID
        sorun_index: satır index (0-based)
        cozum_guncel: yeni çözüm metni
        durum: yeni durum (cokundurmus|cozuldu)
        data_dir: test için custom data dir
    
    Returns:
        Güncellenen satır, bulunamaz ise None
    """
    _ensure_log()
    
    with _LOCK:
        p = _log_path() if data_dir is None else data_dir / "ajan-chat.jsonl"
        
        # Oku
        satirlar = []
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                satirlar = [json.loads(line) for line in f if line.strip()]
        
        # Bul ve güncelle
        idx = 0
        guncellenmi_satir = None
        for i, s in enumerate(satirlar):
            if s.get("task_id") == task_id.upper():
                if idx == sorun_index:
                    s["cozum"] = cozum_guncel[:300]
                    s["durum"] = durum
                    s["timestamp"] = datetime.now().isoformat(timespec="seconds")
                    guncellenmi_satir = s
                    break
                idx += 1
        
        if guncellenmi_satir is None:
            return None
        
        # Yaz
        with p.open("w", encoding="utf-8") as f:
            for s in satirlar:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        
        return guncellenmi_satir


def kapat(
    task_id: str,
    sorun_index: int,
    karar: str = "",
    data_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Sorunukapalı işaretle (durum=cozuldu).
    
    Args:
        task_id: görev ID
        sorun_index: satır index
        karar: karar notu
        data_dir: test için custom data dir
    
    Returns:
        Kapalı satır, bulunamaz ise None
    """
    return guncelle(task_id, sorun_index, karar, "cozuldu", data_dir)


def oku(
    task_id: str | None = None,
    son: int | None = None,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Chat mesajlarını oku.
    
    Args:
        task_id: belirli görevle filtrele
        son: son N satırı al
        data_dir: test için custom data dir
    
    Returns:
        Satırlar listesi
    """
    _ensure_log()
    
    p = _log_path() if data_dir is None else data_dir / "ajan-chat.jsonl"
    satirlar = []
    
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            satirlar = [json.loads(line) for line in f if line.strip()]
    
    # Filtre
    if task_id:
        satirlar = [s for s in satirlar if s.get("task_id") == task_id.upper()]
    
    if son:
        satirlar = satirlar[-son:]
    
    return satirlar


def ozet(
    durum: str | None = None,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Durum başına sayı ve sorunlar.
    
    Args:
        durum: filtrele (acik|cokundurmus|cozuldu)
        data_dir: test için custom data dir
    
    Returns:
        Filtrelenmiş satırlar
    """
    satirlar = oku(data_dir=data_dir)
    
    if durum:
        satirlar = [s for s in satirlar if s.get("durum") == durum]
    
    return satirlar


def bulgula(
    konu: str,
    bulgu: str,
    link: str = "",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Tasarım eleştirisi/görüşü kaydı.
    
    Args:
        konu: başlık (örn. "Tasarım Belgesi (D-192)")
        bulgu: eleştiri/görüş metni
        link: ilgili dosya/karar linki
        data_dir: test için custom data dir
    
    Returns:
        Eklenen satır
    """
    satir = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "konu": konu,
        "bulgu": bulgu[:500],
        "link": link,
    }
    
    satir_json = json.dumps(satir, ensure_ascii=False) + "\n"
    
    with _LOCK:
        p = _log_path("ajan-chat-bulgular") if data_dir is None else data_dir / "ajan-chat-bulgular.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(satir_json)
    
    return satir


def bulgular_oku(
    konu: str | None = None,
    son: int | None = None,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Bulgular logunu oku.
    
    Args:
        konu: belirli konuya filtrele
        son: son N bulgular
        data_dir: test için custom data dir
    
    Returns:
        Bulgular listesi
    """
    p = _log_path("ajan-chat-bulgular") if data_dir is None else data_dir / "ajan-chat-bulgular.jsonl"
    satirlar = []
    
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            satirlar = [json.loads(line) for line in f if line.strip()]
    
    if konu:
        satirlar = [s for s in satirlar if konu in s.get("konu", "")]
    
    if son:
        satirlar = satirlar[-son:]
    
    return satirlar
