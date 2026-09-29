"""KAPALI göç yolu (D-266, D-271).

Bu modül eskiden `schema/migrations/` altındaki SQL dosyalarını uygular ve
kendi `schema_migrations` kaydını tutardı. **Düşürüldü.**

Neden düşürüldü, ölçümle:

1. **Çağıranı yoktu.** `apply_migrations` / `main` fonksiyonlarını kod
   tabanında çağıran tek bir yer bile yoktu; yalnız `python -m` ile elle
   çalıştırılabiliyordu. D-266: çağıranı olmayan kod onarılmaz, düşürülür.
2. **İkinci defter doğuruyordu.** D-264'te ölçüldü: bu yol defteri 23 →
   15 kaydına geri almıştı. `goc_defteri.py` ile aynı tabloya farklı
   kurallarla yazan ikinci bir kapı, defteri anlatıcı olmaktan çıkarır
   (D-265: üç defter tutan sistem hiçbirine güvenemez).
3. **Şemayı nitelendirmiyordu.** `FROM schema_migrations` yazıyordu;
   canlı DB'de bu ad üç şemada birden var (public, auth, realtime).

Tek göç kapısı:

    python scripts/goc_defteri.py --uygula 00NN_x.sql   # tek göç
    python scripts/goc_defteri.py --uygula-tumu         # kurulum/deploy
    python scripts/goc_defteri.py                        # rapor (yazmaz)

Mandal: `tests/test_data_log.py::test_goc_yazma_yollari_kapali`.
"""

from __future__ import annotations

import sys

_KAPALI = (
    "company_master.db.migrate KAPALI (D-266/D-271). Göç tek kapıdan geçer:\n"
    "    python scripts/goc_defteri.py --uygula <dosya.sql>\n"
    "    python scripts/goc_defteri.py --uygula-tumu\n"
    "Bu yol ikinci bir defter doğurduğu için düşürüldü (D-264: defter 23 → 15)."
)


def apply_migrations(database_url: str | None = None):  # noqa: ARG001
    raise RuntimeError(_KAPALI)


def main() -> int:
    print(_KAPALI, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
