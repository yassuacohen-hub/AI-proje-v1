"""Company Master V1.0 — Ankara B2B şirket evreni.

Bu modül, V10/01_gereksinimler/01_mvp_gereksinimleri.md ve
V10/03_mimari/01_etl_mimarisi.md belgelerinde tanımlanan
Company Master V1.0 altyapısının Python implementasyonudur.

Alt moduller:
    - schema: SQL şema (companies, sources, source_records vb.)
    - etl: Ham veri → normalize → entity resolution → master akışı
    - entity_resolution: VKN + unvan fuzzy matching
    - search: PostgreSQL Full Text Search sarmalayıcısı
    - services: Dış servis istemcileri (NVIDIA NIM vb.)
"""

__version__ = "0.1.0"
