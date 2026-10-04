# -*- coding: utf-8 -*-
"""TSG-04 yazma hattı: IlanKaniti -> company_events INSERT pipeline.

Brif: VERI-TSG-04-YAZICI-01
Şema: 0037_tsg_olay_hatti.sql (company_events.source_guid/event_person/person_role)
Eşleme: skills.services.ticaret_sicili_kanit.olay_esle -> (event_type, direction)
Kaynak: data/kanit/ altındaki IlanKaniti JSON dosyaları (TSG-PILOT-20 çıktısı).
"""

from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Proje kökünü Python yoluna ekle (skills modülü için)
PROJE_KOK = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJE_KOK))
sys.path.insert(0, str(PROJE_KOK / "src"))

from sqlalchemy import text
from dotenv import load_dotenv

from skills.services.ticaret_sicili_kanit import olay_esle, IlanKaniti
from company_master.db.connection import get_engine

load_dotenv()

logger = logging.getLogger("tsg_yazici")

KANIT_DIZIN = PROJE_KOK / "data" / "kanit"


@dataclass
class TsgYaziciSonuc:
    """Yazma işlemi sonucu."""
    islenen: int = 0
    eklenen: int = 0
    guncellenen: int = 0
    atlanan: int = 0
    hatalar: list[str] = None

    def __post_init__(self):
        if self.hatalar is None:
            self.hatalar = []


def _tarih_parse_et(tarih_str: str | None) -> date | None:
    """Tarih stringini date'e çevirir (GG.AA.YYYY veya YYYY-AA-GG)."""
    if not tarih_str:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d.%m.%y"):
        try:
            return datetime.strptime(tarih_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _kisi_ve_rol_cikar(tescil_edilen_husus: str | None) -> tuple[str | None, str | None]:
    """Tescil edilen husus metninden kişi adı ve rolünü çıkarır.

    Örnek: "ANONİM ŞİRKET (SERMAYE ARTIRIMI) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET
    Değişiklik - Sermaye Artırımı" -> event_person=None, person_role=None
    (Kişi bilgisi ayrı bir alanda gelmiyor, ilan türünden çıkarılmaz.)

    Not: TSG-PILOT-20 ölçümünde icra/iflas için ayrı kutu yoktu; kişi
    bilgisi ilan türü etiketi içinde mevcut değil. Bu fonksiyon şimdilik
    None döner; ileride kişi çıkarma mantığı eklenirse genişletilebilir.
    """
    # Şimdilik kişi/rol bilgisi ilan metninde yok; ileride regex ile
    # "ortak", "müdür", "tasfiye memuru" gibi kalıplar aranabilir.
    return None, None


def ilan_turu_normalize_et(ilan_turu: str | None) -> str | None:
    """İlan türü etiketini normalize eder (büyük harf, boşluk temizliği)."""
    if not ilan_turu:
        return None
    return re.sub(r"\s+", " ", ilan_turu.strip().upper())


def kanit_dosyalarini_oku() -> list[dict]:
    """data/kanit/ altındaki tüm JSON dosyalarını okur."""
    dosyalar = []
    for dosya in sorted(KANIT_DIZIN.glob("*.json")):
        try:
            veri = json.loads(dosya.read_text(encoding="utf-8"))
            veri["_dosya_adi"] = dosya.name
            dosyalar.append(veri)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Kanıt dosyası okunamadı: %s (%s)", dosya.name, e)
    return dosyalar


def _source_guid_olustur(kanit: dict) -> str:
    """Kanıt anahtarı oluşturur (dosya adı bazlı, benzersiz)."""
    # Dosya adı zaten benzersiz: ilan_sira_no-gazete_sayi-gazete_sayfa.json
    # _dosya_adi alanında .json uzantılı olarak duruyor
    dosya_adi = kanit.get("_dosya_adi", "")
    if dosya_adi.endswith(".json"):
        return dosya_adi[:-5]  # .json'u çıkar
    # Fallback: alanlardan oluştur (E = empty)
    def temiz(v):
        return "".join(c for c in (v or "") if c.isalnum()).upper() or "E"
    ilan = temiz(kanit.get("ilan_sira_no"))
    sayi = temiz(kanit.get("gazete_sayi"))
    sayfa = temiz(kanit.get("gazete_sayfa"))
    return f"{ilan}-{sayi}-{sayfa}"


def tsg_pipeline_calistir(dry_run: bool = False) -> TsgYaziciSonuc:
    """TSG yazma hattını çalıştırır.

    Args:
        dry_run: True ise veritabanına yazmaz, sadece raporlar.

    Returns:
        TsgYaziciSonuc: İşlem özeti.
    """
    sonuc = TsgYaziciSonuc()
    engine = get_engine()

    kanitlar = kanit_dosyalarini_oku()
    logger.info("TSG pipeline başlıyor: %d kanıt dosyası bulundu", len(kanitlar))

    # 1) Tüm şirketleri tek sorguda getir (ticaret_sicil_no -> company_id)
    with engine.connect() as conn:
        sirket_map = {
            row[0].strip(): str(row[1])
            for row in conn.execute(text("""
                SELECT trade_registry_number, company_id
                FROM companies
                WHERE trade_registry_number IS NOT NULL
            """)).fetchall()
        }
    logger.info("Şirket haritası yüklendi: %d firma", len(sirket_map))

    # 2) Mevcut source_guid'leri tek sorguda getir (duplicate kontrolü için)
    with engine.connect() as conn:
        mevcut_guidler = {
            row[0] for row in conn.execute(text("""
                SELECT source_guid FROM company_events WHERE source_guid IS NOT NULL
            """)).fetchall()
        }
    logger.info("Mevcut source_guid sayısı: %d", len(mevcut_guidler))

    # 3) Toplu INSERT için veri topla
    insert_verileri = []
    guncelle_sirketler = set()

    for kanit in kanitlar:
        sonuc.islenen += 1

        try:
            # 1) Firma bul (ticaret_sicil_no ile, memory'den)
            sicil_no = kanit.get("ticaret_sicil_no")
            company_id = sirket_map.get(sicil_no.strip()) if sicil_no else None

            if not company_id:
                logger.debug("Firma bulunamadı: sicil_no=%s, dosya=%s",
                           sicil_no, kanit.get("_dosya_adi"))
                sonuc.atlanan += 1
                continue

            # 2) source_guid (kanıt anahtarı - dosya adı bazlı, benzersiz)
            source_guid = _source_guid_olustur(kanit)

            # 3) Duplicate kontrolü (memory'den)
            if source_guid in mevcut_guidler:
                sonuc.atlanan += 1
                logger.debug("Duplicate source_guid atlandı: %s", source_guid)
                continue

            # 4) event_type ve direction
            ilan_turu = ilan_turu_normalize_et(kanit.get("il_turu"))
            event_type, direction = olay_esle(ilan_turu)

            # 5) event_date
            event_date = _tarih_parse_et(kanit.get("yayin_tarihi"))

            # 6) detection_date
            detection_date = date.today()

            # 7) event_person ve person_role
            event_person, person_role = _kisi_ve_rol_cikar(kanit.get("tescil_edilen_husus"))

            insert_verileri.append({
                "company_id": company_id,
                "event_type": event_type,
                "event_date": event_date,
                "detection_date": detection_date,
                "direction": direction,
                "source_guid": source_guid,
                "event_person": event_person,
                "person_role": person_role,
                "magnitude": None,
                "confidence": 0.9,
            })
            guncelle_sirketler.add((company_id, event_date))

        except Exception as e:
            hata_msg = f"Kanıt işlenemedi: {kanit.get('_dosya_adi', 'bilinmiyor')} - {e}"
            logger.error(hata_msg)
            sonuc.hatalar.append(hata_msg)

    # 4) Toplu INSERT
    if insert_verileri and not dry_run:
        logger.info("Toplu INSERT: %d kayıt", len(insert_verileri))
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO company_events (
                    company_id, event_type, event_date, detection_date,
                    direction, source_guid, event_person, person_role,
                    magnitude, confidence
                ) VALUES (
                    :company_id, :event_type, :event_date, :detection_date,
                    :direction, :source_guid, :event_person, :person_role,
                    :magnitude, :confidence
                )
            """), insert_verileri)
        sonuc.eklenen = len(insert_verileri)
        logger.info("INSERT tamamlandı: %d kayıt", sonuc.eklenen)

    # 5) companies.last_verified_on güncelle
    if guncelle_sirketler and not dry_run:
        logger.info("last_verified_on güncelleniyor: %d firma", len(guncelle_sirketler))
        with engine.begin() as conn:
            for company_id, tarih in guncelle_sirketler:
                conn.execute(text("""
                    UPDATE companies
                    SET last_verified_on = :tarih
                    WHERE company_id = :cid
                """), {"tarih": tarih, "cid": company_id})
        sonuc.guncellenen = len(guncelle_sirketler)
        logger.info("Güncelleme tamamlandı")

    logger.info("TSG pipeline tamamlandı: işlenen=%d, eklenen=%d, guncellenen=%d, "
                "atlanan=%d, hatalar=%d",
                sonuc.islenen, sonuc.eklenen, sonuc.guncellenen,
                sonuc.atlanan, len(sonuc.hatalar))
    return sonuc


def main():
    """CLI giriş noktası."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    import argparse
    parser = argparse.ArgumentParser(description="TSG-04 yazma hattı")
    parser.add_argument("--dry-run", action="store_true", help="Sadece raporla, yazma")
    args = parser.parse_args()

    sonuc = tsg_pipeline_calistir(dry_run=args.dry_run)

    print(f"\n=== TSG Pipeline Sonucu ===")
    print(f"İşlenen:  {sonuc.islenen}")
    print(f"Eklenen:  {sonuc.eklenen}")
    print(f"Güncellenen: {sonuc.guncellenen}")
    print(f"Atlanan:  {sonuc.atlanan}")
    print(f"Hatalar:  {len(sonuc.hatalar)}")
    if sonuc.hatalar:
        for h in sonuc.hatalar[:5]:
            print(f"  - {h}")

    if sonuc.hatalar:
        exit(1)


if __name__ == "__main__":
    main()
