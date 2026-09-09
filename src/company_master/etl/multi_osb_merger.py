# -*- coding: utf-8 -*-
"""Multi-OSB merger: OSTİM + İvedik + Başkent + ASO verilerini birleştir."""

import pandas as pd
import logging
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from company_master.db.connection import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")


def load_osb_data(osb_name: str, file_pattern: str) -> pd.DataFrame:
    """OSB verisini dosyadan yükle."""
    files = list(DATA_DIR.glob(f"{file_pattern}/*"))
    if not files:
        logger.warning(f"{osb_name}: Veri dosyası bulunamadı.")
        return pd.DataFrame()
    df = pd.concat([pd.read_json(f, lines=True) for f in files], ignore_index=True)
    df["_osb_source"] = osb_name
    logger.info(f"{osb_name}: {len(df)} firma yüklendi.")
    return df


def deduplicate_companies(df: pd.DataFrame) -> pd.DataFrame:
    """Firmaları VKN veya isim üzerinden deduplicate et."""
    # VKN ile öncelik
    df_dedup = df.sort_values(
        ["tax_number", "_osb_source"],
        ascending=[True, False],
        na_position="last"
    )
    # VKN bazlı ilk kayıtları al
    df_dedup = df_dedup.drop_duplicates(subset=["tax_number"], keep="first")
    # VKN yoksa isim bazlı deduplicate
    df_dedup = df_dedup.drop_duplicates(subset=["legal_name"], keep="first")
    return df_dedup


def merge_to_database(df: pd.DataFrame):
    """Birleştirilmiş veriyi PostgreSQL'e yaz."""
    engine = get_engine()
    records = df.to_dict(orient="records")
    if not records:
        logger.warning("Yazılacak kayıt yok.")
        return 0
    # Upsert (ON CONFLICT)
    stmt = insert(text("companies")).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tax_number"],
        set_={
            "legal_name": stmt.excluded.legal_name,
            "trade_name": stmt.excluded.trade_name,
            "address": stmt.excluded.address,
            "phone": stmt.excluded.phone,
            "website_domain": stmt.excluded.website_domain,
            "nace_code": stmt.excluded.nace_code,
            "osb_parsel": stmt.excluded.osb_parsel,
            "is_osb_member": True,
            "updated_at": "NOW()",
        }
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    return len(records)


def run_merger():
    """Multi-OSB merge işlemini çalıştır."""
    logger.info("Multi-OSB Merger başlatılıyor...")

    # OSB verilerini yükle
    ostim = load_osb_data("OSTİM", "ostim/firmalar*.jsonl")
    ivedik = load_osb_data("İvedik", "ivedik/firmalar*.jsonl")
    baskent = load_osb_data("Başkent", "baskent/firmalar*.jsonl")
    aso = load_osb_data("ASO", "aso/firmalar*.jsonl")

    # Tüm verileri birleştir
    all_data = pd.concat([ostim, ivedik, baskent, aso], ignore_index=True)
    logger.info(f"Toplam ham kayıt: {len(all_data)}")

    # Deduplicate
    merged = deduplicate_companies(all_data)
    logger.info(f"Benzersiz kayıt: {len(merged)}")

    # Database'e yaz
    count = merge_to_database(merged)
    logger.info(f"✓ {count} firma PostgreSQL'e yazıldı.")

    # Özet rapor
    summary = merged.groupby("_osb_source").size()
    logger.info("\nKaynak Dağılımı:")
    for src, cnt in summary.items():
        logger.info(f"  {src}: {cnt}")
    
    return merged


if __name__ == "__main__":
    run_merger()