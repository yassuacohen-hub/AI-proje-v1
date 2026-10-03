#!/bin/sh
# MANDAL-KURULUM-01 / D-255 --- .pre-commit-config.yaml icindeki iki "local"
# mandali dogrudan kosar. `pre_commit` modulu KURULU DEGIL; bu betik onu
# gerektirmez, ag erisimi istemez, yeni bagimlilik eklemez.
#
# Uzak mandallar (bandit, safety) burada YOK. pre-commit kurulursa
# `pre-commit install` bu dosyayi devralir ve hepsini kosar.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1

python -X utf8 scripts/mandal_toctou_koruma.py oncesi

# GUARD-ENC-01: her commit'te (config: always_run)
python -X utf8 scripts/kodlama_denetim.py --kapsam git || exit 1

# MANDAL-CI-01 (D-253): DB'ye bagli oldugu icin always_run DEGIL ---
# yalnizca sema/goc dosyasina dokunan commit tetikler (config: files:).
if git diff --cached --name-only --diff-filter=ACMR \
   | grep -qE '^(src/company_master/schema/|tests/test_goc_defteri\.py$|scripts/goc_defteri\.py$)'
then
  python -X utf8 tests/test_goc_defteri.py || exit 1
fi

# MANDAL-D250-01 (D-250): kimlik tamligi tek kapisi. DB gerekmez (saf hesap),
# bu yuzden her committe kosar (config: always_run).
python -X utf8 tests/test_kalite_puani.py || exit 1

# MANDAL-TOCTOU-01 (D-332): paylasilan index yarisi.
# OLCULEN (2026-10-02): iki kez oldu - 6d86d56 ve 8c84522. Ajan `git add`
# ile `git commit` arasindaki ~8 saniyede index'i baska ajan guncelledi;
# --name-only dogrulamasi TEK kontrol noktasinda calistigi icin sizmayi
# gormedi. Zararsizdi (D-330 sifir referans, D-227 mandali gecti), ama
# tesaduf degil yapidir.
#
# KURAL: index parmak izi mandal ONCESI ve SONRASI karsilastirilir. Degisirse
# "dogrulama gecersiz" sayilir ve commit DURUR. Boylece kanit, commit'te
# olan ile ayni nesneyi gosterir.
#
# NEDEN bu ise yarar: tek kontrol noktasi TOCTOU penceresi birakir;
# mandal bittikten sonra ikinci bir kontrol pencereyi kapatir.

# MANDAL-TOCTOU-01 (D-332): index mandal sirasinda degistiyse kanit gecersiz.
python -X utf8 scripts/mandal_toctou_koruma.py sonrasi
exit $?
