# -*- coding: utf-8 -*-
"""P7-40: Export fonksiyonu — KPI ve veri tablolarindan CSV/Excel indir.

Kullanim:
    - KPI metriklerini CSV/Excel olarak indir
    - Veri tablolarini filtreli olarak export et
    - Audit log export
    - Task board export

ADMIN-ROO-01 (Aşama C):
    - ``except Exception: pass`` / ``return None`` sessiz yutmaları kaldırıldı.
    - Veri okuyucu ``(df, hata)`` sözleşmesine geçti; hata ``hata_kutusu`` ile
      kullanıcıya gösterilir, log'a yazılır; veri yoksa ``bos_durum``.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine  # noqa: E402
from company_master.ui import bos_durum, hata_kutusu  # noqa: E402

log = logging.getLogger(__name__)

DB_IPUCU = "DATABASE_URL `.env` içinde doğru mu? `docker compose ps` ile servisi kontrol edin."
PANO_IPUCU = "`data/orchestrator/task_board.json` var mı ve geçerli JSON mu?"

#: Sorgu türü → (SQL, tek satır mı?)
_SORGULAR: dict[str, tuple[str, bool]] = {
    "kpi": (
        """
        SELECT COUNT(*) as total_firma,
               AVG(data_quality_score) as avg_quality,
               SUM(CASE WHEN tax_number IS NOT NULL AND tax_number != '' THEN 1 ELSE 0 END) as with_vkn,
               SUM(CASE WHEN website_domain IS NOT NULL AND website_domain != '' THEN 1 ELSE 0 END) as with_web,
               SUM(CASE WHEN primary_phone IS NOT NULL AND primary_phone != '' THEN 1 ELSE 0 END) as with_phone,
               SUM(CASE WHEN primary_email IS NOT NULL AND primary_email != '' THEN 1 ELSE 0 END) as with_email
        FROM companies
        WHERE is_ankara=TRUE
        """,
        True,
    ),
    "companies": (
        """
        SELECT company_id, legal_name, tax_number, company_type, status,
               data_quality_score, entity_confidence, is_ankara, is_osb_member,
               primary_phone, primary_email, website_domain, nace_code,
               establishment_date, updated_at
        FROM companies
        WHERE is_ankara=TRUE
        LIMIT 5000
        """,
        False,
    ),
    "audit": (
        """
        SELECT id, timestamp, level, logger_name, message, extra,
               user_id, session_id, ip_address, action, resource_type,
               resource_id, result, created_at
        FROM audit_logs
        ORDER BY timestamp DESC
        LIMIT 10000
        """,
        False,
    ),
}


def _db_sorgu_oku(query_type: str) -> tuple[pd.DataFrame | None, str | None]:
    """``_SORGULAR`` içindeki SQL'i çalıştırır → ``(df, hata)``.

    Satır yoksa ``(boş DataFrame, None)``; DB hatasında ``(None, "Tür: mesaj")``.
    """
    sql, tek_satir = _SORGULAR[query_type]
    try:
        engine = get_engine()
        with engine.connect() as conn:
            sonuc = conn.execute(text(sql)).mappings()
            if tek_satir:
                row = sonuc.first()
                kayitlar = [dict(row)] if row else []
            else:
                kayitlar = [dict(r) for r in sonuc.all()]
        return pd.DataFrame(kayitlar), None
    except Exception as exc:  # noqa: BLE001 - sürücü/bağlantı hataları çeşitli
        log.warning("Export sorgusu okunamadı (%s): %s", query_type, exc)
        return None, f"{type(exc).__name__}: {exc}"


def _pano_oku(board_path: Path | None = None) -> tuple[pd.DataFrame | None, str | None]:
    """Görev panosu JSON'unu DataFrame'e çevirir → ``(df, hata)``."""
    yol = board_path or (ROOT / "data" / "orchestrator" / "task_board.json")
    if not yol.exists():
        return pd.DataFrame(), None
    try:
        tasks = json.loads(yol.read_text(encoding="utf-8"))
        return pd.DataFrame(tasks), None
    except (OSError, ValueError, TypeError) as exc:
        log.warning("Görev panosu okunamadı (%s): %s", yol, exc)
        return None, f"{type(exc).__name__}: {exc}"


def _export_verisi_oku(query_type: str) -> tuple[pd.DataFrame | None, str | None]:
    """Sorgu türüne göre veri okur → ``(df, hata)``; bilinmeyen tür → ``(None, mesaj)``."""
    if query_type in _SORGULAR:
        return _db_sorgu_oku(query_type)
    if query_type == "tasks":
        return _pano_oku()
    return None, f"Bilinmeyen export türü: {query_type!r}"


@st.cache_data(ttl=60)
def load_export_data(query_type: str) -> tuple[pd.DataFrame | None, str | None]:
    """Farklı veri türleri için ``(DataFrame, hata)`` döndürür (60 sn önbellek)."""
    return _export_verisi_oku(query_type)


def _excel_bytes(df: pd.DataFrame) -> bytes | None:
    """DataFrame'i bellekte .xlsx'e yazar (FIX-YONETIM-01).

    `df.to_excel()` bir yazıcı/yol ister; önceki kod bunu vermediği için
    "missing 1 required positional argument: 'excel_writer'" hatası veriyordu.
    openpyxl yoksa None döner (çağıran CSV'ye yönlendirir).
    """
    try:
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        return buffer.getvalue()
    except ImportError:
        return None


def render_export_tab() -> None:
    """Export sekmesini gosterir."""
    st.subheader("📥 Veri Export")

    export_type = st.radio(
        "Export Turu",
        ["KPI Metrikleri", "Firma Verileri", "Audit Log", "Gorev Panosu"],
        horizontal=True,
    )

    type_map = {
        "KPI Metrikleri": "kpi",
        "Firma Verileri": "companies",
        "Audit Log": "audit",
        "Gorev Panosu": "tasks",
    }

    query_type = type_map.get(export_type, "kpi")
    df, hata = load_export_data(query_type)

    if hata:
        ipucu = PANO_IPUCU if query_type == "tasks" else DB_IPUCU
        hata_kutusu(f"{export_type} verisi okunamadı", hata, ipucu)
        return

    if df is not None and not df.empty:
        st.success(f"✅ {len(df)} kayit yuklendi")
        st.dataframe(df.head(100), width="stretch", hide_index=True)

        col_csv, col_excel = st.columns(2)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with col_csv:
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📄 CSV İndir",
                data=csv,
                file_name=f"export_{query_type}_{timestamp}.csv",
                mime="text/csv",
            )

        with col_excel:
            excel_bytes = _excel_bytes(df)
            if excel_bytes is None:
                st.warning("Excel için `openpyxl` kurulu değil; CSV indirmeyi kullanın.")
            else:
                st.download_button(
                    label="📊 Excel İndir",
                    data=excel_bytes,
                    file_name=f"export_{query_type}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
    else:
        bos_durum(
            f"{export_type} için export edilecek veri bulunamadı.",
            ikon="📥",
            aksiyon="Başka bir export türü seçin veya veri yüklemesini bekleyin.",
        )
