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
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from . import task_board as tb

# D-192: Ajan Chat Sistemi entegrasyonu
try:
    from company_master.chat import ac as chat_ac
    HAS_CHAT = True
except ImportError:
    HAS_CHAT = False

logger = logging.getLogger(__name__)


class TriggerError(Exception):
    """Tetikleme/onay kuyruğu işlemi reddedildi."""


def _data_dir(data_dir: Path | None) -> Path:
    return Path(data_dir) if data_dir else tb.STATE_DIR


def _simdi() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---- Ajan adı kuralı (D-33, 2026-09-16, Ürün Sahibi emri; D-59 ile merve eklendi) ----
#
# D-60 (KAHİN kararı 2026-09-18): kanonik adlar Türkçe isimlere geçti.
# Kural: araç adı = takma ad, Türkçe ad = kanonik ad.
#   ihsan (roo)            — orkestratör
#   utku  (kilo)           — üretim/hacim
#   salih (merve/continue) — QA/Release Governance
#   yasu  (cline/yasin)    — denetim/review
# Eski adlar takma ad olarak korunur; pano ve tetik geçmişi bozulmasın diye
# her yazım aynı postaya çözümlenir.

AJANLAR: tuple[str, ...] = ("ihsan", "utku", "salih", "yasu", "mimir")

AJAN_TAKMA_ADLAR: dict[str, str] = {
    # utku (araç: kilo)
    "kilo": "utku",
    "kilocode": "utku",
    "kilo_code": "utku",
    "kilo-code": "utku",
    # ihsan (araç: roo)
    "roo": "ihsan",
    "roocode": "ihsan",
    "roo_code": "ihsan",
    "roo-code": "ihsan",
    "roo_orkestrator": "ihsan",
    "orkestrator": "ihsan",
    # salih (araç: continue; eski merve)
    "merve": "salih",
    "continue": "salih",
    "continueide": "salih",
    "continue_ide": "salih",
    "continue-ide": "salih",
    # yasu (araç: cline; KAHİN "yasin" de diyebilir)
    "cline": "yasu",
    "clinebot": "yasu",
    "cline_code": "yasu",
    "yasin": "yasu",
    # mimir (teknik ad: odin_ai) — D-182 besinci kanonik ajan
    "odin_ai": "mimir",
    "odinai": "mimir",
    "abrakadabra": "mimir",
    "claudecode": "claude_code",
    "claude-code": "claude_code",
}


def ajan_normalize(ad: str | None) -> str:
    """Ajan adını kanonik biçime çevirir.

    - Baş/son boşluk atılır, küçük harfe çevrilir (Türkçe İ/I güvenli).
    - "ajan " / "agent " öneki ve "@" atılır ("Ajan kilo" → "kilo").
    - Boşluk ve tire alt çizgiye çevrilir; ardından takma ad tablosu uygulanır.
    Boş ad TriggerError fırlatır.
    """
    ham = (ad or "").strip()
    if not ham:
        raise TriggerError(f"Ajan adı boş olamaz (kanonik adlar: {', '.join(AJANLAR)}).")
    # Ajan adları ASCII'dir: Türkçe İ/ı ayrımı yapılmaz ("KILO" → "kilo").
    ad_l = ham.replace("İ", "i").replace("ı", "i").lower().lstrip("@").strip()
    for onek in ("ajan ", "agent ", "ajan_", "agent_", "ajan-", "agent-"):
        if ad_l.startswith(onek):
            ad_l = ad_l[len(onek):].strip()
            break
    # "ajankilo" gibi bitişik yazımlar
    for onek in ("ajan", "agent"):
        if ad_l.startswith(onek) and len(ad_l) > len(onek):
            ad_l = ad_l[len(onek):].strip()
            break
    ad_l = "_".join(p for p in ad_l.replace("-", " ").replace("_", " ").split() if p)
    return AJAN_TAKMA_ADLAR.get(ad_l, AJAN_TAKMA_ADLAR.get(ad_l.replace("_", ""), ad_l))


def ajan_goster(ad: str | None) -> str:
    """D-61: ekrana/rapora yazılan ajan hitabı BÜYÜK HARF (Türkçe i→İ).

    Kanonik ad küçük kalır (dosya adı, pano alanı); yalnız gösterim büyür.
    """
    return ajan_normalize(ad).replace("i", "İ").upper()


# ---- Posta kutusu (tetikler) ----

def _tetik_yolu(ajan: str, data_dir: Path | None = None) -> Path:
    return _data_dir(data_dir) / "triggers" / f"{ajan_normalize(ajan)}.jsonl"


def _tetikleri_oku(ajan: str, data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Ajanın tetik dosyasını okur. UTF-8 BOM toleranslı."""
    yol = _tetik_yolu(ajan, data_dir)
    if not yol.exists():
        return []
    kayitlar: list[dict[str, Any]] = []
    # utf-8-sig BOM'u otomatik atlar
    for satir in yol.read_text(encoding="utf-8-sig").splitlines():
        satir = satir.strip()
        if satir:
            kayitlar.append(json.loads(satir))
    return kayitlar


def _tetikleri_yaz(
    kayitlar: list[dict[str, Any]], ajan: str, data_dir: Path | None = None
) -> None:
    # Dedup by (task_id, durum) — ponytail: future=full rebuild if scaling needs it
    seen: set[tuple] = set()
    dedupe = []
    for k in kayitlar:
        key = (k["task_id"], k["durum"])
        if key not in seen:
            seen.add(key)
            dedupe.append(k)
    yol = _tetik_yolu(ajan, data_dir)
    yol.parent.mkdir(parents=True, exist_ok=True)
    icerik = "".join(json.dumps(k, ensure_ascii=False) + "\n" for k in dedupe)
    tb.atomic_write_text(yol, icerik)


def tetik_ekle(
    task_id: str, ajan: str, talimat: str = "", data_dir: Path | None = None
) -> dict[str, Any]:
    """Ajanın postasına yeni görev tetikle. Aynı görev için tekrar düşmez."""
    ajan = ajan_normalize(ajan)  # D-33: kayıtta da kanonik ad
    kayitlar = _tetikleri_oku(ajan, data_dir)
    if any(k["task_id"] == task_id and k["durum"] == "bekliyor" for k in kayitlar):
        raise TriggerError(f"{ajan} için bekleyen tetik zaten var: {task_id}")
    # ORCH-12: Idempotency — tamamlanmış göreve tekrar tetik DÜŞMEZ.
    gorev = tb.gorev_getir(task_id)
    if gorev and gorev.get("durum") == "done":
        raise TriggerError(f"{task_id} zaten done — tekrar tetik düşmez (idempotency)")
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


#: S-06: Posta kutusunda tetik yokken panodan alınabilecek görev durumları.
PANO_ALINABILIR_DURUMLAR = ("plan", "bekliyor")


def tetik_al(
    ajan: str, task_id: str, data_dir: Path | None = None
) -> dict[str, Any]:
    """Tetiği 'alindi' yap ve panodaki görevi aktife çek.

    S-06: Bekleyen tetik yoksa görev doğrudan panodan alınmaya çalışılır.
    Koşul: görev panoda var + `sahip == ajan` + durumu `plan`/`bekliyor`.
    Aksi halde TriggerError (başkasının görevi veya zaten alınmış/bitmiş iş).
    """
    ajan = ajan_normalize(ajan)
    kayitlar = _tetikleri_oku(ajan, data_dir)
    bulundu = False
    for k in kayitlar:
        if k["task_id"] == task_id and k["durum"] == "bekliyor":
            k["durum"] = "alindi"
            k["alma_tarihi"] = _simdi()
            bulundu = True
    gorev = tb.gorev_getir(task_id)
    if not bulundu:
        # S-06: pano fallback — panoya elle eklenmiş (tetiksiz) görevler için.
        if gorev is None:
            raise TriggerError(f"Görev panoda bulunamadı: {task_id}")
        if ajan_normalize(gorev.get("sahip") or "-") != ajan:
            raise TriggerError(
                f"Görev {task_id} '{gorev.get('sahip')}' ajanına ait; {ajan} alamaz"
            )
        if gorev.get("durum") not in PANO_ALINABILIR_DURUMLAR:
            raise TriggerError(
                f"{ajan} için bekleyen tetik yok: {task_id} "
                f"(pano durumu: {gorev.get('durum')})"
            )
        tb.gorev_guncelle(task_id, durum="aktif")
        return {"task_id": task_id, "ajan": ajan, "durum": "alindi", "kaynak": "pano"}
    if gorev is None:
        raise TriggerError(f"Görev panoda bulunamadı: {task_id}")
    _tetikleri_yaz(kayitlar, ajan, data_dir)
    tb.gorev_guncelle(task_id, durum="aktif")
    return {"task_id": task_id, "ajan": ajan, "durum": "alindi", "kaynak": "tetik"}


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

    # ORCH-12: Otomatik onaylı görevler (isbirligi destek görevleri)
    # Kim+ne zaman+hedef bilgisi isbirligi_raporu.jsonl denetim izine yazılır.
    gorev = tb.gorev_getir(task_id) or {}
    if gorev.get("otomatik_onay"):
        try:
            from . import isbirligi  # dongusel import onlemi
            onayla(task_id, f"oto:{ajan}", data_dir)
            isbirligi.destek_raporu(gorev, f"oto:{ajan}")
        except Exception as exc:  # onay hatası teslimi çökertmesin
            print(f"  [ORCH-12] otomatik onay hatasi: {exc}")

    kayitlar = _tetikleri_oku(ajan, data_dir)
    for k in kayitlar:
        if k["task_id"] == task_id and k["durum"] == "alindi":
            k["durum"] = "teslim"
            k["teslim_tarihi"] = _simdi()
    _tetikleri_yaz(kayitlar, ajan, data_dir)

    # Zincir devam et: tamamlanan görevin sonrası tetiklensin
    sonraki = zincir_devam_et(task_id, ajan, data_dir)
    if sonraki:
        logger.info(f"⏭ ZİNCİR: {sonraki['task_id']} tetiklendi (önceki: {task_id})")

    return {"task_id": task_id, "durum": "review"}


def onay_bekleyenler(data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Kontrolörün inceleyeceği teslimler.

    ORCH-13: iki kaynağı birleştirir —
    1) onay kuyruğu (bekliyor)  2) tetik dosyasındaki 'teslim' kayıtları
    (ajanlar bazen teslimi tetik dosyasına yazar, kuyruğa yazmaz).
    """
    kuyruk = [k for k in _kuyruk_oku(data_dir) if k["durum"] == "bekliyor"]
    bilinen = {k["task_id"] for k in kuyruk}
    try:
        from . import duzen  # lokal: döngüsel risk yok
        ajanlar = duzen.AJANLAR
    except Exception:
        ajanlar = list(AJANLAR)
    for ajan in ajanlar:
        try:
            for k in _tetikleri_oku(ajan, data_dir):
                if k["durum"] == "teslim" and k["task_id"] not in bilinen:
                    g = tb.gorev_getir(k["task_id"]) or {}
                    if g.get("durum") != "done":  # zaten onaylanmışsa gösterme
                        kuyruk.append({
                            "task_id": k["task_id"], "ajan": ajan,
                            "ozet": (g.get("not") or "")[:120],
                            "teslim_tarihi": k.get("teslim_tarihi", ""),
                            "durum": "bekliyor", "kaynak": "tetik",
                        })
                        bilinen.add(k["task_id"])
        except Exception:
            pass
    return kuyruk


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
    """Kontrolör onayı → görev `done` (ORCH-05 tüm kilitleri otomatik düşürür).

    ORCH-13 fallback: teslim onay kuyruğuna yazılmamışsa (ajan tetik dosyasını
    elle düzenlediğinde olur), tetik kaydından onaylanır — sistem çökmez.
    """
    try:
        k = _kuyruk_guncelle(
            task_id, data_dir,
            durum="onaylandi", onaylayan=onaylayan, onay_tarihi=_simdi(),
        )
    except TriggerError:
        # Fallback: tetik dosyasındaki 'teslim' kaydından onayla.
        # GÜVENLİK: gerçek teslim kanıtı yoksa hata — var olmayan/teslim
        # edilmemiş görev sessizce done edilemez (idempotency + bütünlük).
        g = tb.gorev_getir(task_id) or {}
        ajan = g.get("sahip", "")
        teslim_var = False
        if ajan:
            kayitlar = _tetikleri_oku(ajan, data_dir)
            for rk in kayitlar:
                if rk["task_id"] == task_id and rk["durum"] == "teslim":
                    rk["durum"] = "done"
                    rk["onaylayan"] = onaylayan
                    rk["onay_tarihi"] = _simdi()
                    teslim_var = True
            _tetikleri_yaz(kayitlar, ajan, data_dir)
        # Panoda teslim/review durumu da teslim kanıtı sayılır (ajan tetik
        # dosyasını güncellememiş olabilir ama görevi panoya teslim etmişse).
        if not teslim_var and g.get("durum") in ("teslim", "review"):
            teslim_var = True
        if not teslim_var:
            raise TriggerError(f"Onay kuyruğunda bulunamadı: {task_id}")
        k = {"task_id": task_id, "ajan": ajan, "durum": "onaylandi",
             "onaylayan": onaylayan, "onay_tarihi": _simdi(), "kaynak": "tetik-fallback"}
    tb.gorev_guncelle(task_id, durum="done")

    # ORCH-13 kalıcı düzeltme: onay -> zincir devamı + blokaj kapıları otomatik.
    # (Nöbetçi çalışmasa bile elle onay zinciri ilerletir.)
    devam = None
    try:
        devam = zincir_devam_et(task_id, k.get("ajan", ""), data_dir)
    except Exception:
        devam = None
    try:
        from . import duzen  # lokal import: döngüsel risk yok
        kapilar = duzen.blokaj_guncelle()
    except Exception:
        kapilar = {}
    k["zincir_devam"] = (devam or {}).get("task_id") if isinstance(devam, dict) else (devam[0]["task_id"] if devam else None)
    k["kapilar_acilan"] = kapilar.get("acilan", []) if isinstance(kapilar, dict) else []
    
    # D-190: MIMIR architect rapor otomasyonu
    # Görev done oldu → architect mod ise rapor yaz (zero insan müdahalesi tasarım)
    try:
        gorev = tb.gorev_getir(task_id) or {}
        if gorev.get("mod") == "architect":
            from company_master.intelligence.mimir_rapor import MimirRaporYazici
            yazici = MimirRaporYazici()
            yazici.rapor_yazmayi_tetikle(task_id)
    except Exception:
        logger.exception("Rapor yazma hatası", exc_info=True)
    
    return k


# S-07 (sahip kararı 2026-09-16): otomatik onay yalnız P2 ve altı.
# P0/P1 görevler roo tarafından ELLE onaylanır; tekrar ihlalde oto-nobetci kapatılır.
ELLE_ONAY_ONCELIKLERI: frozenset[str] = frozenset({"P0", "P1"})


def otomatik_onaylanabilir(task_id: str) -> tuple[bool, str]:
    """Bir teslimin oto-nobetci/hepsini-tamamla ile onaylanıp onaylanamayacağı.

    Dönüş: (onaylanabilir, gerekçe).
    - Pano dışı görev (D-35 hayalet onay) → False
    - `oncelik` P0/P1 → False (S-07: elle roo onayı)
    - Diğer (P2, P3, ...) → True
    """
    g = tb.gorev_getir(task_id)
    if not g:
        return False, "panoda yok (D-35)"
    oncelik = str(g.get("oncelik") or "P2").strip().upper()
    if oncelik in ELLE_ONAY_ONCELIKLERI:
        return False, f"{oncelik} elle onay (S-07)"
    return True, oncelik


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
def tetik_uyari_ekle(ajan: str, task_id: str, data_dir: Path | None = None) -> dict[str, Any]:
    """Nobetci tarafından tetik fırlatma uyarısı ekle (uyari_tarihi + uyari_sayisi)."""
    kayitlar = _tetikleri_oku(ajan, data_dir)
    bulundu = False
    for k in kayitlar:
        if k["task_id"] == task_id and k["durum"] == "bekliyor":
            k["uyari_tarihi"] = _simdi()
            k["uyari_sayisi"] = k.get("uyari_sayisi", 0) + 1
            bulundu = True
    if bulundu:
        _tetikleri_yaz(kayitlar, ajan, data_dir)
    return {"task_id": task_id, "uyari_sayisi": kayitlar[-1].get("uyari_sayisi", 1) if bulundu else 0}
def gorev_zinciri(task_ids: list[str], ajan: str, talimat: str = "", data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Görev zinciri oluştur: ilk görev hemen tetiklenir, diğerleri 'zincir_bekleme' durumunda bekler.

    Ajan ilk görevi teslim edince otomatik sonraki tetiklenir.

    Args:
        task_ids: Sıralı görev ID listesi (örn. ['P7-23', 'P7-4'])
        ajan: Tüm görevlerin sahibi
        talimat: Tüm görevler için ortak talimat (opsiyonel)

    Returns:
        Oluşturulan tetik kayıtları
    """
    if not task_ids:
        raise TriggerError("Zincir için en az 1 görev gerekli")

    kayitlar = []

    # İlk görev hemen tetiklenir
    ilk = tetik_ekle(task_ids[0], ajan, talimat, data_dir)
    kayitlar.append(ilk)

    # Diğerleri zincir_bekleme durumunda
    for i in range(1, len(task_ids)):
        onceki_id = task_ids[i - 1]
        simdiki_id = task_ids[i]

        # Zincir kaydı oluştur (bekliyor yerine zincir_bekleme)
        kayit = {
            "task_id": simdiki_id,
            "ajan": ajan,
            "talimat": talimat,
            "tarih": _simdi(),
            "durum": "zincir_bekleme",
            "onceki_gorev": onceki_id,  # Bu görev tamamlanınca tetikle
        }

        # Bu ajanın tetik dosyasına ekle
        mevcut = _tetikleri_oku(ajan, data_dir)
        mevcut.append(kayit)
        _tetikleri_yaz(mevcut, ajan, data_dir)
        kayitlar.append(kayit)

    return kayitlar


def zincir_devam_et(tamamlanan_task_id: str, ajan: str, data_dir: Path | None = None) -> dict[str, Any] | None:
    """Tamamlanan göreve bağlı zincirdeki sonraki görevi otomatik tetikle.

    teslim_et() içinden çağrılır.

    Returns:
        Tetiklenen görev kaydı veya None (zincir yok)
    """
    kayitlar = _tetikleri_oku(ajan, data_dir)

    # Zincirde bekleyen görev var mı?
    for k in kayitlar:
        if k.get("durum") == "zincir_bekleme" and k.get("onceki_gorev") == tamamlanan_task_id:
            # Durumu bekliyor'a çevir (normal tetik)
            k["durum"] = "bekliyor"
            k.pop("onceki_gorev", None)
            k["tarih"] = _simdi()  # Tetik zamanı güncelle
            _tetikleri_yaz(kayitlar, ajan, data_dir)
            return k

    return None

def zincir_kalan(ajan: str, data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Zincirde onceki teslime bagli bekleyen gorevler (durum: zincir_bekleme)."""
    return [k for k in _tetikleri_oku(ajan, data_dir) if k.get("durum") == "zincir_bekleme"]


#: D-55 rol son ekleri — rapor dosya adinda ajan adi GECMEZ.
AJAN_ROLU: dict[str, str] = {
    "ihsan": "orkestrator",
    "utku": "uretim",
    "salih": "denetim",
    "yasu": "denetim",
}


def rapor_postala(
    ajan: str, baslik: str, rapor_yolu: str,
    hedef: str = "ihsan", data_dir: Path | None = None,
) -> dict[str, Any]:
    """Zincir bitis raporunu hedef ajanin postasina `rapor` kaydi olarak dusur.

    Ayni posta dosyasi kullanilir; durum `rapor` oldugu icin `bekleyen_tetikler`
    (durum == bekliyor) bu kaydi gorev sanmaz.
    
    D-192: Rapor WARNING/ERROR içerse, chat.ac() ile sorun kaydı yapılır.
    """
    ajan = ajan_normalize(ajan)
    hedef = ajan_normalize(hedef)
    kayitlar = _tetikleri_oku(hedef, data_dir)
    kayit = {
        "task_id": f"RAPOR-{ajan.upper()}",
        "ajan": hedef,
        "gonderen": ajan,
        "talimat": baslik,
        "rapor_yolu": rapor_yolu,
        "tarih": _simdi(),
        "durum": "rapor",
    }
    kayitlar.append(kayit)
    _tetikleri_yaz(kayitlar, hedef, data_dir)
    
    # D-192: Rapor özetini oku ve sorun seviyesi logları chat.ac() ile kaydet
    if HAS_CHAT:
        try:
            rapor_path = Path(rapor_yolu)
            if rapor_path.exists():
                rapor_icerik = rapor_path.read_text(encoding="utf-8", errors="ignore")
                # WARNING veya ERROR varsa sorun kaydı yap
                if "WARNING" in rapor_icerik or "ERROR" in rapor_icerik:
                    # İlk 200 char rapor özeti
                    ozet = rapor_icerik.split("\n")[0][:200]
                    chat_ac(
                        ajan=ajan,
                        task_id=kayit["task_id"],
                        sorun=f"Rapor: {ozet}",
                        cozum="",
                        data_dir=data_dir
                    )
        except Exception as e:
            logger.warning(f"D-192 chat.ac() hatası: {e}", exc_info=False)
    
    return kayit


def raporlar(hedef: str = "ihsan", data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Hedef ajanin postasina dusen zincir raporlari."""
    return [k for k in _tetikleri_oku(hedef, data_dir) if k.get("durum") == "rapor"]


def zincir_uzat(ajan: str, yeni_task_ids: list[str], talimat: str = "", data_dir: Path | None = None) -> list[dict[str, Any]]:
    """Mevcut zinciren sonuna yeni görev(ler) ekle.

    Örnek:
        # roo'nun mevcut zinciri: P7-24 → simple_1
        zincir_uzat('roo', ['YENI-1', 'YENI-2'])
        # Sonuç: P7-24 → simple_1 → YENI-1 → YENI-2

    Args:
        ajan: Zincir sahibi
        yeni_task_ids: Eklenecek görev ID'leri
        talimat: Yeni görevler için talimat

    Returns:
        Eklenen tetik kayıtları
    """
    kayitlar = _tetikleri_oku(ajan, data_dir)

    # Zinciren sonunu bul (en son eklenen görev)
    son_task_id = None
    for k in kayitlar:
        if k.get("durum") in ("zincir_bekleme", "bekliyor", "alindi"):
            son_task_id = k["task_id"]

    if not son_task_id:
        # Zincir yoksa yeni oluştur
        return gorev_zinciri(yeni_task_ids, ajan, talimat, data_dir)

    # Yeni görevleri zinciren sonuna ekle
    eklenen = []
    onceki = son_task_id
    for task_id in yeni_task_ids:
        kayit = {
            "task_id": task_id,
            "ajan": ajan,
            "talimat": talimat,
            "tarih": _simdi(),
            "durum": "zincir_bekleme",
            "onceki_gorev": onceki,
        }
        kayitlar.append(kayit)
        eklenen.append(kayit)
        onceki = task_id

    _tetikleri_yaz(kayitlar, ajan, data_dir)
    return eklenen
