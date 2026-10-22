# -*- coding: utf-8 -*-
"""SON-6 kaydina final dogrulama sonucunu ekle (qwen alias duzeltmesi + 14/14).
Idempotent: ayni ifede varsa tekrar eklemez."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
ESKI = "Kanıt: **14/14 takma ad `completed` (3-9 sn)**"
YENI = ("Kanıt: **14/14 takma ad 2/2 denemede metin üretti (en kötü 12,5 sn)** — "
        "`_tmp/son_alias_guven.py`. Bu turda iki hedef daha değişti: "
        "`glm-5.3` → reasoning modeli 1/3 metin verdiği için nemotron-3.5'e, "
        "`qwen3.8-flash-next` → 152 sn timeout sonrası `bzl/auto:free`'ye "
        "(ölçülen 3/3, ort 4,7 sn). DERS: combo hedefi seçerken tek test YETMEZ — "
        "3 tekrar + METİN üretimi şart (status=completed ama metin boş olabilir, "
        "GUI'de 'Düşünüyor'da kalır = kullanıcı için takılmayla aynı).")

metin = HEDEF.read_text(encoding="utf-8")
if "2/2 denemede metin üretti" in metin:
    print("zaten guncel — dokunulmadı")
elif ESKI not in metin:
    raise SystemExit("ÇAPA bulunamadı, elle kontrol et")
else:
    HEDEF.write_text(metin.replace(ESKI, YENI, 1), encoding="utf-8")
    geri = HEDEF.read_text(encoding="utf-8")
    print("GUNCELLENDI · satir:", geri.count("\n") + 1,
          "· yeni ifade var mi:", "2/2 denemede metin üretti" in geri)
