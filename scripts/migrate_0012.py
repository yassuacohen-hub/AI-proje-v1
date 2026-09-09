# -*- coding: utf-8 -*-
"""0012 migrasyon + product_categories seed (hem Supabase hem yerel PG).

Kullanim: python scripts/migrate_0012.py
"""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text

from company_master.db.connection import get_engine

# V7 sektor yapisindan turetilmis urun katalogu (Ankara OSB odaagi)
PCAT = [
    ("pc_mak_imalat", "Makine İmalat ve CNC İşleme", "28", "Torna, freze, 5-eksen CNC, dişli ve redüktör imalatı"),
    ("pc_metal_isleme", "Metal İşleme ve Döküm", "25", "Pres, döküm, kılavuz, lazer kesim, kaynak ve sac şekillendirme"),
    ("pc_oto_yan", "Otomotiv Yan Sanayi", "29", "Motor-parça, şasi, fren, elektronik alt grup üretimi"),
    ("pc_kimya", "Kimya ve Boya", "20", "Endüstriyel boyalar, temizlik kimyasalları, kaplama"),
    ("pc_gida", "Gıda Üretimi ve Ambalaj", "10", "İşlenmiş gıda, ambalaj, gıda makineleri yedekleri"),
    ("pc_plastik", "Plastik ve Kauçuk Ürünler", "22", "Enjeksiyon, blow, profil ve teknik parça üretimi"),
    ("pc_elektrik", "Elektrik ve Elektronik", "27", "Panolar, motor sargı, kablo ve otomasyon bileşenleri"),
    ("pc_digital", "Yazılım ve Otomasyon", "62", "Endüstriyel yazılım, PLC/SCADA, MES, IoT entegrasyonu"),
    ("pc_ins_tes", "İnşaat ve Tesis Yönetimi", "41", "Fabrika yapımı, çelik konstrüksiyon, tesisat"),
    ("pc_metalik", "Metalik Olmayan Mineral", "23", "Cam, seramik, beton ve refrakter ürünler"),
    ("pc_toptan", "Toptan Ticaret ve Dağıtım", "46", "Yedek parça, hammadde ve ekipman toptan satışı"),
    ("pc_servis", "Endüstriyel Hizmetler", "33", "Makine bakım-onarım, kalibrasyon, iş güvenliği"),
    ("pc_savunma", "Savunma Sanayi Tedariği", "84", "Tier-1/2/3 tedarik zinciri, kalifikasyon süreçleri"),
    ("pc_isgucu", "İşgücü ve İK Hizmetleri", "78", "Uzman işgücü, outsourcing, yetkinlik eğitimi"),
]

SQL_FILES = ["0012_users_and_catalog.sql"]


def seed_pcat(engine) -> None:
    with engine.begin() as c:
        for code, label, nace, desc in PCAT:
            c.execute(text("""
                INSERT INTO product_categories (code, label_tr, nace_group, description)
                VALUES (:code, :label, :nace, :desc)
                ON CONFLICT (code) DO UPDATE SET label_tr = :label, nace_group = :nace, description = :desc
            """), {"code": code, "label": label, "nace": nace, "desc": desc})
    print(f"+ product_categories seed: {len(PCAT)} kategori")


def main() -> None:
    engine = get_engine()
    print(f"DB: {str(engine.url).split('@')[-1]}")
    if "--reset" in sys.argv:
        with engine.begin() as c:
            c.execute(text(
                "DROP TABLE IF EXISTS product_categories, credit_ledger, users CASCADE"))
        print("+ reset: yarim tablolar dusuruldu")
        sys.argv.remove("--reset")
    for name in SQL_FILES:
        sql = io.open(ROOT / "src" / "company_master" / "schema" / "migrations" / name,
                      encoding="utf-8").read()
        # akilli split: yorum satirlarini atla, statement 'n' satir sonundaki ';' ile biter
        stmts, buf = [], []
        for line in sql.splitlines():
            stripped = line.strip()
            if stripped.startswith("--"):
                continue
            buf.append(line)
            if stripped.endswith(";"):
                stmts.append("\n".join(buf).strip())
                buf = []
        tail = "\n".join(buf).strip()
        if tail:
            stmts.append(tail)
        with engine.begin() as c:
            for stmt in stmts:
                if stmt.rstrip().endswith(";"):
                    stmt = stmt.rstrip()[:-1]
                if stmt:
                    c.execute(text(stmt))
        print(f"+ {name} uygulandi")
    seed_pcat(engine)
    # dogrulama
    with engine.connect() as c:
        tabs = c.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name IN ('users','credit_ledger','product_categories')")).fetchall()
        print("dogrulama:", [t[0] for t in tabs])


if __name__ == "__main__":
    main()
