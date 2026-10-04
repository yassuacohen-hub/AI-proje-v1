# -*- coding: utf-8 -*-
from .scrapers.ostim_scraper import scrape_tum_osb
from .scrapers.aso_scraper import run_full_scrape
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


TASK_ID = "SCRAPE-005-KAZIMA-DOCKER-INTEGRATION"


def _satir_sayisi(yol: Path) -> int:
    """Dosyadaki satır sayısı; yoksa 0."""
    if not yol.exists():
        return 0
    with yol.open("rb") as f:
        return sum(1 for _ in f)


def _denetim_kaydet(
    kaynak: str, *, basarili: bool, kayit: int, hata: str | None = None
) -> bool:
    """Bir kaynak için `scrape_audit_log` denetim kaydı bırakır (D-310 katman 5).

    `0050_scrape_audit_log.sql` tablosu ve tek yazıcısı (`etl/scrape_kayit.py::KazimaYazici`)
    diskte vardı; pipeline onu **çağırmıyordu**. Bu yüzden tablo 8 kayıtta
    kalıyor, koşu denetlenemiyordu. Eksik olan çağrıdır, şema değil.

    Kayıt yazılamazsa `False` döner ve çağıran koşuyu başarısız sayar:
    denetlenemeyen koşu, denetlenmiş başarıdan farksız değildir (D-260).

    Import bilerek geç: modül DB'siz ortamda da içe aktarılabilir kalsın.
    """
    try:
        from .scrape_kayit import KazimaYazici

        KazimaYazici(kaynak, task_id=TASK_ID).audit_kaydet(
            f"pipeline://{kaynak}",
            action="scrape",
            status="success" if basarili else "error",
            bayt=kayit,
            hata=hata,
        )
        return True
    except Exception as e:  # noqa: BLE001 — denetim katmanı yutmayacak
        logging.error(
            "DENETIM KAYDI YAZILAMADI (%s): %s — bu kosu denetlenemez, "
            "kabul kriteri 3 olculemez.",
            kaynak,
            e,
        )
        return False


def scrape_all() -> bool:
    """Tüm OSB kaynaklarını kazı.

    Döner: tüm kaynaklar başarılıysa True, en az biri hata verdiyse veya
    kayıt üretmediyse False.

    Hata yutulmaz: çağıran taraf (refresh_pipeline.step_scrape) yeşil
    sinyal yerine gerçek durumu görür (D-224).

    Boş başarı kapısı: kayıt üretmeyen bir kaynak başarılı sayılmaz.
    D-310 yalnız exception akışını kapatıyordu; üretilmeyen veri de
    başarısızlıktır, aksi halde pipeline sıfır iş yapıp yeşil raporlar.
    """
    logging.info("ETL Pipeline başladı")

    basarili = True

    ostim_kayit = 0
    ostim_hata: str | None = None
    try:
        logging.info("OSTİM scrape başlatılıyor...")
        ostim_output = Path("data/ostim/firmalar_full.jsonl")
        ostim_output.parent.mkdir(parents=True, exist_ok=True)
        # scrape_tum_osb bir generator fonksiyon; cagirmak govdesini
        # calistirmaz, yalnizca uretilen nesneyi dondurur. Tunetilmezse
        # hicbir HTTP istegi yapilmaz, robots.txt kontrolu bile
        # calismaz ve dosya hic yazilmaz. Bu yuzden mutlaka tuketilir.
        ostim_kayit = sum(1 for _ in scrape_tum_osb(output_path=ostim_output))
        if ostim_kayit == 0:
            ostim_hata = "0 kayit uretildi"
            logging.error("OSTİM scrape 0 kayıt üretti — başarı sayılmaz.")
            basarili = False
        else:
            logging.info(f"OSTİM scrape tamamlandı ({ostim_kayit} kayıt).")
    except Exception as e:
        ostim_hata = str(e)
        logging.error(f"OSTİM scrape hatası: {e}")
        basarili = False

    if not _denetim_kaydet(
        "ostim.org.tr",
        basarili=ostim_hata is None,
        kayit=ostim_kayit,
        hata=ostim_hata,
    ):
        basarili = False

    aso_kayit = 0
    aso_hata: str | None = None
    try:
        logging.info("ASO scrape başlatılıyor...")
        aso_dir = Path("data/aso")
        aso_dir.mkdir(parents=True, exist_ok=True)
        aso_cikti = aso_dir / "aso_full.jsonl"
        onceki = _satir_sayisi(aso_cikti)
        run_full_scrape()
        yeni = _satir_sayisi(aso_cikti)
        aso_kayit = yeni - onceki
        if aso_kayit == 0:
            aso_hata = f"yeni kayit yok ({onceki} -> {yeni})"
            logging.error(
                f"ASO scrape yeni kayıt üretmedi ({onceki} -> {yeni}) — başarı sayılmaz."
            )
            basarili = False
        else:
            logging.info(f"ASO scrape tamamlandı ({aso_kayit} yeni kayıt).")
    except Exception as e:
        aso_hata = str(e)
        logging.error(f"ASO scrape hatası: {e}")
        basarili = False

    if not _denetim_kaydet(
        "aso.org.tr",
        basarili=aso_hata is None,
        kayit=aso_kayit,
        hata=aso_hata,
    ):
        basarili = False

    if basarili:
        logging.info("ETL Pipeline tamamlandı.")
    else:
        logging.error("ETL Pipeline HATA İLE tamamlandı (en az bir kaynak başarısız).")

    return basarili


if __name__ == "__main__":
    scrape_all()
