# -*- coding: utf-8 -*-
"""OSB ihale ilan izleyicisi.
VERI-02: OSB portallarından ihale ilanlarını izler, yeni ilanları tespit eder.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from company_master.etl.scrapers.base_osfb_scraper import BaseOsfbScraper, BaseOsfbFirma


logger = logging.getLogger("osb_tender_monitor")


@dataclass
class IhaleIlan:
    """İhale ilanı veri sınıfı (İngilizce sütun adlarıyla uyumlu)."""
    source_id: str
    source_tender_id: str
    tender_title: str
    tender_type: str | None = None
    usul: str | None = None
    announcement_date: str | None = None
    question_answer_due: str | None = None
    bid_deadline: str | None = None
    opening_date: str | None = None
    province: str | None = None
    district: str | None = None
    osb_name: str | None = None
    estimated_cost: float | None = None
    unit: str | None = None
    description: str | None = None
    document_url: str | None = None
    status: str = "active"
    source_tender_url: str | None = None
    crawled_at: str = datetime.now().isoformat()


class OsbTenderMonitor(BaseOsfbScraper):
    """OSB ihale ilanlarını izleyen scraper."""

    # OSB portal ayarları
    SOURCE_CONFIGS = {
        "baskentosb.org.tr": {
            "base_url": "https://baskentosb.org.tr",
            "liste_url_sablonu": "/ihale-listesi?sayfa={sayfa}",
            "detay_url_sablonu": "/ihale-detay/{ilan_id}",
            "active": True,
        },
        "ostim.org.tr": {
            "base_url": "https://www.ostim.org.tr",
            "liste_url_sablonu": "/ihale-ilanlari?page={sayfa}",
            "detay_url_sablonu": "/ihale-detay/{ilan_id}",
            "active": True,
        },
    }

    USER_AGENT = "Mozilla/5.0 (compatible; HuginnTenderMonitor/1.0)"

    # Durum eşleştirme (İngilizce)
    DURUM_ESLEME = {
        "devam ediyor": "active",
        "açık": "active",
        "kapalı": "completed",
        "iptal": "cancelled",
        "duyuru": "announcement",
    }

    def __init__(self, kaynak_adlari: list[str] | None = None):
        super().__init__()
        self.kaynak_adlari = kaynak_adlari or list(self.SOURCE_CONFIGS.keys())
        self.veritabani_baglantisi = None  # SQLAlchemy engine veya connection
        # Session başlat
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT or "Mozilla/5.0"})

    def _kaynak_bul(self, kaynak_adi: str) -> dict | None:
        """Kaynak konfigürasyonunu bulur."""
        return self.SOURCE_CONFIGS.get(kaynak_adi)

    def _veritabani_baglantisi_al(self):
        """Veritabanı bağlantısını alır (SQLAlchemy engine)."""
        if self.veritabani_baglantisi is None:
            from sqlalchemy import create_engine
            from dotenv import load_dotenv
            load_dotenv()
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable not set")
            self.veritabani_baglantisi = create_engine(db_url)
        return self.veritabani_baglantisi

    def _kaynak_kaydet_veya_al(self, kaynak_adi: str) -> str:
        """Kaynakı kaydeder veya mevcutsa ID'sini döner."""
        engine = self._veritabani_baglantisi_al()
        config = self._kaynak_bul(kaynak_adi)
        if not config:
            raise ValueError(f"Bilinmeyen kaynak: {kaynak_adi}")

        with engine.begin() as conn:
            # Kaynak var mı kontrol et
            result = conn.execute(
                text("SELECT source_id FROM ihale_kaynaklari WHERE name = :adi"),
                {"adi": kaynak_adi}
            ).fetchone()

            if result:
                return str(result[0])

            # Yeni kaynak ekle
            result = conn.execute(text("""
                INSERT INTO ihale_kaynaklari (name, base_url, liste_url_sablonu, detay_url_sablonu, is_active)
                VALUES (:adi, :base_url, :liste_sablon, :detay_sablon, :aktif)
                RETURNING source_id
            """), {
                "adi": kaynak_adi,
                "base_url": config["base_url"],
                "liste_sablon": config["liste_url_sablonu"],
                "detay_sablon": config["detay_url_sablonu"],
                "aktif": config.get("active", True),
            })
            return str(result.fetchone()[0])

    def _ilan_kaydet(self, ilan: IhaleIlan) -> tuple[str, bool]:
        """İlanı kaydeder. Döner: (ilan_id, yeni_mi)."""
        engine = self._veritabani_baglantisi_al()

        with engine.begin() as conn:
            # İlan var mı kontrol et
            result = conn.execute(text("""
                SELECT ilan_id FROM ihale_ilanlari
                WHERE source_id = :source_id AND source_tender_id = :source_tender_id
            """), {
                "source_id": ilan.source_id,
                "source_tender_id": ilan.source_tender_id,
            }).fetchone()

            if result:
                # Mevcut ilanı güncelle
                ilan_id = str(result[0])
                conn.execute(text("""
                    UPDATE ihale_ilanlari SET
                        tender_title = :tender_title,
                        tender_type = :tender_type,
                        usul = :usul,
                        announcement_date = :announcement_date,
                        question_answer_due = :question_answer_due,
                        bid_deadline = :bid_deadline,
                        opening_date = :opening_date,
                        province = :province,
                        district = :district,
                        osb_name = :osb_name,
                        estimated_cost = :estimated_cost,
                        unit = :unit,
                        description = :description,
                        document_url = :document_url,
                        status = :status,
                        source_tender_url = :source_tender_url,
                        updated_at = NOW()
                    WHERE ilan_id = :ilan_id
                """), {
                    "tender_title": ilan.tender_title,
                    "tender_type": ilan.tender_type,
                    "usul": ilan.usul,
                    "announcement_date": ilan.announcement_date,
                    "question_answer_due": ilan.question_answer_due,
                    "bid_deadline": ilan.bid_deadline,
                    "opening_date": ilan.opening_date,
                    "province": ilan.province,
                    "district": ilan.district,
                    "osb_name": ilan.osb_name,
                    "estimated_cost": ilan.estimated_cost,
                    "unit": ilan.unit,
                    "description": ilan.description,
                    "document_url": ilan.document_url,
                    "status": ilan.status,
                    "source_tender_url": ilan.source_tender_url,
                    "ilan_id": ilan_id,
                })
                return ilan_id, False

            # Yeni ilan ekle
            result = conn.execute(text("""
                INSERT INTO ihale_ilanlari (
                    source_id, source_tender_id, tender_title, tender_type, usul,
                    announcement_date, question_answer_due, bid_deadline,
                    opening_date, province, district, osb_name, estimated_cost, unit,
                    description, document_url, status, source_tender_url, crawled_at
                ) VALUES (
                    :source_id, :source_tender_id, :tender_title, :tender_type, :usul,
                    :announcement_date, :question_answer_due, :bid_deadline,
                    :opening_date, :province, :district, :osb_name, :estimated_cost, :unit,
                    :description, :document_url, :status, :source_tender_url, :crawled_at
                ) RETURNING ilan_id
            """), {
                "source_id": ilan.source_id,
                "source_tender_id": ilan.source_tender_id,
                "tender_title": ilan.tender_title,
                "tender_type": ilan.tender_type,
                "usul": ilan.usul,
                "announcement_date": ilan.announcement_date,
                "question_answer_due": ilan.question_answer_due,
                "bid_deadline": ilan.bid_deadline,
                "opening_date": ilan.opening_date,
                "province": ilan.province,
                "district": ilan.district,
                "osb_name": ilan.osb_name,
                "estimated_cost": ilan.estimated_cost,
                "unit": ilan.unit,
                "description": ilan.description,
                "document_url": ilan.document_url,
                "status": ilan.status,
                "source_tender_url": ilan.source_tender_url,
                "crawled_at": ilan.crawled_at,
            })
            ilan_id = str(result.fetchone()[0])
            return ilan_id, True

    def _tarih_parse_et(self, tarih_str: str | None) -> str | None:
        """Tarih stringini ISO formatına çevirir."""
        if not tarih_str:
            return None
        # Yaygın tarih formatlarını dene
        for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%d %B %Y"):
            try:
                return datetime.strptime(tarih_str.strip(), fmt).date().isoformat()
            except ValueError:
                continue
        return None

    def _maliyet_parse_et(self, maliyet_str: str | None) -> tuple[float | None, str | None]:
        """Maliyet stringini sayı ve birime ayırır."""
        if not maliyet_str:
            return None, None
        # TL, ₺, bin TL, milyon TL vb. formatları temizle
        s = maliyet_str.strip()
        birim = "TL"
        if "milyon" in s.lower():
            birim = "milyon TL"
        elif "bin" in s.lower():
            birim = "bin TL"
        # Sayıyı çıkar
        sayi_match = re.search(r"[\d.,]+", s.replace(".", "").replace(",", "."))
        if sayi_match:
            try:
                return float(sayi_match.group()), birim
            except ValueError:
                pass
        return None, None

    def fetch_firma_liste(self, page: int = 1) -> list:
        """Base class uyumu için - ihale ilanları için kullanılır."""
        # Bu metod base class'ta abstract ama ihale izleyicide farklı çalışır
        # sayfa_dongusu() metodunu kullanın
        return []

    def fetch_firma_detay(self, slug: str) -> dict[str, Any]:
        return {}

    def scrape(self, detay_al: bool = False) -> Iterator[IhaleIlan]:
        """Tüm aktif kaynakları tarar ve yeni ilanları yield eder."""
        for kaynak_adi in self.kaynak_adlari:
            config = self._kaynak_bul(kaynak_adi)
            if not config or not config.get("active", True):
                continue

            source_id = self._kaynak_kaydet_veya_al(kaynak_adi)
            self.log.info("%s kaynağı taranıyor...", kaynak_adi)

            # Liste sayfalarını tara
            for sayfa in range(1, self.MAX_SAYFA + 1):
                try:
                    ilanlar = self._kaynak_liste_tara(kaynak_adi, config, sayfa)
                    if not ilanlar:
                        self.log.info("%s sayfa %d boş — bitti", kaynak_adi, sayfa)
                        break

                    # Her ilan için detay sayfasını tara
                    for ilan in ilanlar:
                        ilan.source_id = source_id
                        ilan_id, yeni_mi = self._ilan_kaydet(ilan)
                        if yeni_mi:
                            self.log.info("Yeni ilan: %s (%s)", ilan.tender_title, ilan.source_tender_id)
                        yield ilan

                    time.sleep(self.RATE_LIMIT_SECONDS)

                except Exception as e:
                    self.log.error("%s sayfa %d hatası: %s", kaynak_adi, sayfa, e)
                    # Hata görünür kıl - sessiz başarılı yok
                    raise

    def _kaynak_liste_tara(self, kaynak_adi: str, config: dict, sayfa: int) -> list[IhaleIlan]:
        """Kaynak listesi sayfasını tarar ve ilan listesi döner."""
        # Bu metot her kaynak için override edilmeli
        # Base implementasyon: genel bir liste sayfası parser'ı
        url = config["base_url"] + config["liste_url_sablonu"].format(sayfa=sayfa)
        self.log.debug("%s sayfa %d taranıyor: %s", kaynak_adi, sayfa, url)

        try:
            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
        except Exception as e:
            self.log.error("%s sayfa %d erişilemedi: %s", kaynak_adi, sayfa, e)
            raise

        soup = BeautifulSoup(response.content, "html.parser")

        # Bu kısım her portal için özelleştirilmeli
        # Base implementasyon: genel tablo/list yapısını dener
        ilanlar = []
        # Örnek: tablo satırları veya kart yapıları
        for item in soup.select("table tbody tr, .ilan-karti, .ilan-item, .table-row"):
            ilan = self._ilan_parse_et(item, kaynak_adi, config)
            if ilan:
                ilanlar.append(ilan)

        return ilanlar

    def _ilan_parse_et(self, element: BeautifulSoup, kaynak_adi: str, config: dict) -> IhaleIlan | None:
        """HTML elementinden ilan bilgilerini çıkarır."""
        # Bu metot her portal için özelleştirilmeli
        # Base implementasyon: genel seçicileri dener
        try:
            # İlan başlığı
            baslik_elem = element.select_one("td:nth-child(1), .ilan-baslik, .title, h3, h4, a")
            tender_title = baslik_elem.get_text(strip=True) if baslik_elem else None

            # İlan ID (genellikle linkte veya data attribute'ünde)
            link_elem = element.select_one("a[href]")
            source_tender_id = None
            source_tender_url = None
            if link_elem:
                href = link_elem.get("href", "")
                source_tender_url = config["base_url"] + href if href.startswith("/") else href
                # ID'yi URL'den çıkar
                id_match = re.search(r"[/=](\d+)(?:/|$)", href)
                if id_match:
                    source_tender_id = id_match.group(1)
                else:
                    source_tender_id = href.split("/")[-1].split("?")[0]

            if not tender_title or not source_tender_id:
                return None

            # Diğer alanlar - portal özel implementasyonu gerektirir
            return IhaleIlan(
                source_id="",  # sonra doldurulacak
                source_tender_id=source_tender_id,
                tender_title=tender_title,
                source_tender_url=source_tender_url,
            )
        except Exception as e:
            self.log.warning("İlan parse hatası: %s", e)
            return None


class BaskentOSBScraper(OsbTenderMonitor):
    """Başkent OSB portalı için özel scraper."""

    def __init__(self):
        super().__init__(kaynak_adlari=["baskentosb.org.tr"])

    def _kaynak_liste_tara(self, kaynak_adi: str, config: dict, sayfa: int) -> list[IhaleIlan]:
        url = config["base_url"] + config["liste_url_sablonu"].format(sayfa=sayfa)
        self.log.debug("Başkent OSB sayfa %d taranıyor: %s", sayfa, url)

        try:
            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
        except Exception as e:
            self.log.error("Başkent OSB sayfa %d erişilemedi: %s", sayfa, e)
            raise

        soup = BeautifulSoup(response.content, "html.parser")
        ilanlar = []

        # Başkent OSB özel selector'ları
        # Tablo yapısı: <table><tbody><tr><td>...</td></tr></tbody>
        for row in soup.select("table.table tbody tr, .table tbody tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            try:
                # Sütunlar: İlan No, Başlık, Tarih, Durum, Detay linki
                ilan_no = cells[0].get_text(strip=True)
                baslik_elem = cells[1].find("a") or cells[1]
                baslik = baslik_elem.get_text(strip=True)
                tarih_str = cells[2].get_text(strip=True) if len(cells) > 2 else None
                durum_str = cells[3].get_text(strip=True) if len(cells) > 3 else None

                link_elem = cells[-1].find("a") if cells else None
                source_tender_url = None
                source_tender_id = None
                if link_elem and link_elem.get("href"):
                    href = link_elem["href"]
                    source_tender_url = config["base_url"] + href if href.startswith("/") else href
                    id_match = re.search(r"[/=](\d+)(?:/|$)", href)
                    source_tender_id = id_match.group(1) if id_match else href.split("/")[-1]

                if not source_tender_id:
                    source_tender_id = ilan_no

                ilan = IhaleIlan(
                    source_id="",  # sonra doldurulacak
                    source_tender_id=source_tender_id,
                    tender_title=baslik,
                    announcement_date=self._tarih_parse_et(tarih_str),
                    status=self.DURUM_ESLEME.get(durum_str.lower(), durum_str) if durum_str else "active",
                    source_tender_url=source_tender_url,
                )
                ilanlar.append(ilan)

            except Exception as e:
                self.log.warning("Başkent OSB ilan parse hatası: %s", e)
                continue

        return ilanlar


class OstimOSBScraper(OsbTenderMonitor):
    """OSTİM OSB portalı için özel scraper."""

    def __init__(self):
        super().__init__(kaynak_adlari=["ostim.org.tr"])

    def _kaynak_liste_tara(self, kaynak_adi: str, config: dict, sayfa: int) -> list[IhaleIlan]:
        url = config["base_url"] + config["liste_url_sablonu"].format(sayfa=sayfa)
        self.log.debug("OSTİM OSB sayfa %d taranıyor: %s", sayfa, url)

        try:
            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
        except Exception as e:
            self.log.error("OSTİM OSB sayfa %d erişilemedi: %s", sayfa, e)
            raise

        soup = BeautifulSoup(response.content, "html.parser")
        ilanlar = []

        # OSTİM OSB özel selector'ları
        for item in soup.select(".ilan-listesi .ilan, .ilan-list .item, table tbody tr"):
            try:
                baslik_elem = item.select_one(".baslik, .title, h3, h4, td:nth-child(1) a, .ilan-baslik a")
                baslik = baslik_elem.get_text(strip=True) if baslik_elem else None

                link_elem = item.select_one("a[href]")
                source_tender_url = None
                source_tender_id = None
                if link_elem and link_elem.get("href"):
                    href = link_elem["href"]
                    source_tender_url = config["base_url"] + href if href.startswith("/") else href
                    id_match = re.search(r"[/=](\d+)(?:/|$)", href)
                    source_tender_id = id_match.group(1) if id_match else href.split("/")[-1].split("?")[0]

                tarih_elem = item.select_one(".tarih, .date, .ilan-tarih, td:nth-child(2)")
                tarih_str = tarih_elem.get_text(strip=True) if tarih_elem else None

                durum_elem = item.select_one(".durum, .status, .ilan-durum, td:nth-child(3)")
                durum_str = durum_elem.get_text(strip=True) if durum_elem else None

                if not baslik or not source_tender_id:
                    continue

                ilan = IhaleIlan(
                    source_id="",
                    source_tender_id=source_tender_id,
                    tender_title=baslik,
                    announcement_date=self._tarih_parse_et(tarih_str),
                    status=self.DURUM_ESLEME.get(durum_str.lower(), durum_str) if durum_str else "active",
                    source_tender_url=source_tender_url,
                )
                ilanlar.append(ilan)

            except Exception as e:
                self.log.warning("OSTİM OSB ilan parse hatası: %s", e)
                continue

        return ilanlar


def main():
    """Ana çalıştırma fonksiyonu."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Her kaynak için ayrı scraper örneği oluştur
    scrapers = [
        BaskentOSBScraper(),
        OstimOSBScraper(),
    ]

    toplam_yeni = 0
    toplam_taranan = 0

    for scraper in scrapers:
        try:
            scraper.log.info("%s scraper başlatılıyor...", scraper.__class__.__name__)
            yeni_sayisi = 0
            taranan_sayisi = 0

            for ilan in scraper.scrape():
                taranan_sayisi += 1
                if hasattr(ilan, '_yeni_mi') and ilan._yeni_mi:
                    yeni_sayisi += 1

            scraper.log.info("%s: %d ilan tarandı, %d yeni", scraper.__class__.__name__, taranan_sayisi, yeni_sayisi)
            toplam_yeni += yeni_sayisi
            toplam_taranan += taranan_sayisi

        except Exception as e:
            scraper.log.error("%s scraper hatası: %s", scraper.__class__.__name__, e)
            # Hata görünür kıl - sessiz başarılı yok
            raise

    print(f"\nToplam: {toplam_taranan} ilan tarandı, {toplam_yeni} yeni ilan tespit edildi.")


if __name__ == "__main__":
    main()
