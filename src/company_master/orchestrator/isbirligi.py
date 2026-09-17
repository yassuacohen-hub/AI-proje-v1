# -*- coding: utf-8 -*-
"""ORCH-12: Ajan işbirliği — boşta ajanlar başka görevlere güvenli katkı.

Senaryo: kilo'nun posta kutusu boş ama roo'nun COP-15 görevi plan'da.
        kilo bu görevin TESTİNİ yazabilir → görev sahibi roo değişmez,
        kilo yalnızca güvenli dizinlere (tests/, docs/, plans/) dokunur.

Güvenlik kuralları:
- Destek ajanı YALNIZCA ``tests/``, ``docs/``, ``plans/`` altına yazar
  -> hedef görevin dosya kilitleriyle asla çakışmaz (duzen.cakisirma_analizi doğrular).
- Hedefi aktif/kilitli olan göreve destek önerilmez.
- Tüm işlemler ``isbirligi_raporu.jsonl`` denetim izine yazılır
  (kim + ne zaman + hedef + ne yaptı) — otomatik onayda 'kim ne yaptı' hep bellidir.

Akış:
    python scripts/gorev_kutusu.py yardim
    python scripts/gorev_kutusu.py destek-al --ajan kilo --hedef COP-15 --rol test
    # kilo alir -> test yazar -> teslim eder -> OTOMATIK ONAY -> hedefe islenir
"""
from __future__ import annotations

import json
from datetime import datetime

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger
from src.company_master.orchestrator.duzen import AJANLAR, cakisirma_analizi

GUVENLI_DIZINLER = ("tests/", "docs/", "plans/")
_RAPOR_YOLU = "isbirligi_raporu.jsonl"


def _simdi() -> str:
    return datetime.now().isoformat(timespec="seconds")


def bos_ajanlar() -> list[str]:
    """Posta kutusu bos + aktif/review gorevi olmayan ajanlar."""
    mesgul = {t["sahip"] for t in tb.gorev_listesi()
              if t.get("durum") in ("aktif", "review")}
    return [a for a in AJANLAR
            if a != "orkestrator" and a not in mesgul and not trigger.bekleyen_tetikler(a)]


def yardim_edilebilir(destek_ajani: str, limit: int = 5) -> list[dict]:
    """Aday gorevler: durum plan/blocked, sahibi baskasi, kilitleri bos.
    Oneri: 'test' (tests/ alti) veya 'arastirma' (docs/ alti)."""
    sonuc: list[dict] = []
    for t in tb.gorev_listesi():
        if t.get("durum") not in ("plan", "blocked"):
            continue
        if t.get("sahip") == destek_ajani:
            continue
        # Hedefin kendi gorev kilidi cakis sayilmaz (plan gorevde kilit atilidir).
        # Baska bir aktif isin tuttugu dosyalar cakisma -> destek onerme.
        analiz = cakisirma_analizi(t["task_id"], t.get("dosyalar", []) or [])
        if analiz["cakisan"]:
            continue
        rol = "test" if t.get("dosyalar") else "arastirma"
        sonuc.append({
            "task_id": t["task_id"], "sahip": t.get("sahip"),
            "durum": t.get("durum"), "baslik": t["baslik"][:45], "rol": rol,
        })
        if len(sonuc) >= limit:
            break
    return sonuc


def _destek_dosyalari(hedef: dict, rol: str) -> list[str]:
    tid = hedef["task_id"].lower()
    return [f"tests/test_{tid}_isbirligi.py"] if rol == "test" else [f"docs/isbirligi_{tid}.md"]


def destek_al(destek_ajani: str, hedef_task_id: str, rol: str = "test") -> dict:
    """Destek gorevi olusturur + ajana tetik duser.
    Gorev otomatik onaylidir (trigger.teslim_et onaylar); hedefin not'una islenir."""
    if rol not in ("test", "arastirma"):
        raise ValueError("rol yalnizca 'test' veya 'arastirma' olabilir")
    hedef = tb.gorev_getir(hedef_task_id)
    if not hedef:
        raise ValueError(f"Hedef gorev yok: {hedef_task_id}")
    if hedef.get("durum") not in ("plan", "blocked"):
        raise ValueError(
            f"Hedef {hedef_task_id} durumu {hedef.get('durum')} — "
            "yalnizca plan/blocked gorevlere destek verilebilir")
    if hedef.get("sahip") == destek_ajani:
        raise ValueError(
            f"Hedef {hedef_task_id} sahibi {destek_ajani} — kendi gorevine destek verilemez")

    destek_id = f"{hedef_task_id}-DESTEK-{destek_ajani.upper()}"
    if tb.gorev_getir(destek_id):
        raise ValueError(f"Destek gorevi zaten var: {destek_id}")

    tb.gorev_ekle(destek_id, f"[DESTEK:{rol}] {hedef['baslik'][:45]}",
                  destek_ajani, "P1", dosyalar=_destek_dosyalari(hedef, rol))
    tb.gorev_guncelle(destek_id, destek_icin=hedef_task_id, rol=rol, otomatik_onay=True)
    trigger.tetik_ekle(
        destek_id, destek_ajani,
        f"DESTEK: {hedef_task_id} icin {rol} ciktisi yaz (yalnizca tests/docs/plans).")
    destekler = list(hedef.get("destek", []))
    destekler.append({"ajan": destek_ajani, "rol": rol, "task_id": destek_id})
    tb.gorev_guncelle(hedef_task_id, destek=destekler)
    return {"gorev": tb.gorev_getir(destek_id), "hedef": hedef_task_id}


def destek_raporu(destek_gorevi: dict, onaylayan: str) -> dict:
    """Otomatik onay sonrasi: denetim izine yaz + hedef gorev not'una isle.

    Kullanici istegi: 'bir sorun olursa kimin ne yaptigi belli olsun.'"""
    hedef_id = destek_gorevi.get("destek_icin")
    rapor = {
        "tarih": _simdi(),
        "destek_task": destek_gorevi["task_id"],
        "ajan": destek_gorevi.get("sahip"),
        "hedef": hedef_id,
        "rol": destek_gorevi.get("rol"),
        "ozet": str(destek_gorevi.get("not") or destek_gorevi.get("baslik"))[:150],
        "onaylayan": onaylayan,
    }
    yol = tb.STATE_DIR / _RAPOR_YOLU
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "a", encoding="utf-8") as f:
        f.write(json.dumps(rapor, ensure_ascii=False) + "\n")

    if hedef_id and tb.gorev_getir(hedef_id):
        g = tb.gorev_getir(hedef_id)
        yeni_not = (f"{g.get('not', '')} | DESTEK[{onaylayan}]: "
                    f"{rapor['ajan']} ({rapor['rol']}) -> {rapor['destek_task']}")
        tb.gorev_guncelle(hedef_id, **{"not": yeni_not[:450]})
    return rapor


def isbirligi_ozeti() -> str:
    """Token dostu ozet: bosta ajanlar + ilk onerileri."""
    satirlar = []
    for a in bos_ajanlar():
        ilk = yardim_edilebilir(a, limit=1)
        satirlar.append(f"{a}->{ilk[0]['task_id']}({ilk[0]['rol']})" if ilk else f"{a}->yok")
    return f"BOSTA: {', '.join(bos_ajanlar()) or '-'} | ONERI: {'; '.join(satirlar) or '-'}"
