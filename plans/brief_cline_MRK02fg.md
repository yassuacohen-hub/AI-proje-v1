# BRIEF - CLINE - MRK-02f + MRK-02g

Hazirlayan: roo (orkestrator)
Hedef ajan: cline
Oncelik: P1
Kapsam: iki bagimsiz gorev. Bolum 1 ve Bolum 2 sirayla yapilir.

---

## BOLUM 0 - ORTAK BAGLAM (once oku)

Proje i18n paketi `src/company_master/i18n/` altinda hazir ve calisiyor.
Dogrulanmis durum (roo tarafindan duman testi yapildi, exit 0):

```
ANAHTAR 182
MENU KPI Ozeti
PARAM 42 kayit listeleniyor.
EN KPI Summary
TON danger danger error
BILINMEYEN yok_boyle_bir_anahtar
BICIM 1.234.567 12,35 1.234,50 TL 14 Eyl 2026 18:30
```

### Paket yuzeyi (import edilecek isimler)

```python
from company_master.i18n import (
    t,            # t(anahtar, *, dil=None, seviye=None, **parametreler) -> str
    ses,          # ses(...) -> Metin  (alanlar: anahtar, metin, katman, ton, ikon, dil, bulundu)
    sayi,         # sayi(deger, ondalik=None) -> str
    para,         # para(deger, birim="TL") -> str
    tarih,        # tarih(deger, saat=False, uzun=False) -> str
    anahtarlar,   # anahtarlar() -> tuple[str, ...]
    sozluk,       # sozluk() -> dict[str, dict]   (ham kayitlar)
    onbellek_temizle,
    dil_ayarla, seviye_ayarla, aktif_dil, aktif_seviye,
    I18nHatasi, ParametreHatasi,
)
```

`Metin` nesnesinin `varyant` ve `streamlit_tipi` property'leri vardir.

### Kaynak dosyalar

| Dosya | Icerik |
|---|---|
| `src/company_master/i18n/ses.json` | 105 kayit, HEPSI `katman: "cerceve"`, anahtarlar `huginn_` / `muninn_` / `odin_` onekli |
| `src/company_master/i18n/ui.json` | 65 kayit: `menu_*` (37), `h1_*` (6), `eylem_*` (10), `durum_*` (6), `veri_*` (4), hata/onay (6 adet `odin_*`/`muninn_*`), anlatisal (6 adet `huginn_*`/`muninn_*`/`odin_*`) |

Her kaydin semasi:

```json
"anahtar_adi": {
  "tr": "metin" veya {"cirak": "...", "usta": "..."},
  "en": "metin",
  "katman": "veri" | "cerceve",
  "ton": "info" | "success" | "warning" | "danger" | "neutral",
  "ikon": "material_symbol_adi"
}
```

`_` ile baslayan anahtarlar meta'dir, motor bunlari atlar (`_aciklama`).

### KESIN YASAK - DOKUNULMAYACAK DOSYALAR

```
src/company_master/i18n/ses.json
src/company_master/i18n/ui.json
src/company_master/i18n/__init__.py
src/company_master/i18n/ton.py
app.py
web_dashboard/tabs/__init__.py
scripts/i18n_ses_uret.py
.env, .env.*
data/orchestrator/**
```

Bu dosyalar roo'nun aktif hattidir. Test kirmizi kalirsa JSON'u DUZELTME, raporla.

### Ortam

Komutlari proje kokunden calistir:

```
set PYTHONIOENCODING=utf-8
set PYTHONPATH=src
```

Repo kokunde `pytest.ini` vardir, dogru sekilde yapilandirilmistir.

---

## BOLUM 1 - MRK-02f: card.py sayi bicimini i18n'e devret

### Amac

`MetricCard._deger_metni` icindeki Turkce sayi bicimleme mantigi `i18n.sayi()` ile birebir ayni.
Kopya mantik tek kaynaga indirilecek.

### Dokunulacak tek dosya

```
src/company_master/ui/components/card.py
```

### Mevcut kod (satir ~129-137)

```python
    def _deger_metni(self) -> str:
        if isinstance(self.deger, bool):
            return "Evet" if self.deger else "Hayir"
        if isinstance(self.deger, int):
            return f"{self.deger:,}".replace(",", ".")
        if isinstance(self.deger, float):
            return f"{self.deger:,.1f}".replace(",", "#").replace(".", ",").replace("#", ".")
        return str(self.deger)
```

NOT: Yukaridaki blok ASCII'ye sadelestirilmis haldir. Dosyadaki gercek metin
"Evet" / "Hayir" yerine Turkce karakterli hali olabilir. Once `read_file` ile
gercek icerigi oku, sonra degistir.

### Yapilacak degisiklik

1. Dosyanin import blogunun sonuna (mevcut `from company_master.ui.base import (...)` satirindan SONRA) ekle:

```python
from company_master.i18n import sayi as _sayi_bicimle
```

2. `_deger_metni` govdesini sadece su hale getir:

```python
    def _deger_metni(self) -> str:
        return _sayi_bicimle(self.deger)
```

Docstring varsa koru. Fonksiyon imzasi ve donus tipi degismeyecek.

### Dairesel import kontrolu

`company_master.i18n` paketi `company_master.ui` paketini import ETMEZ (sadece
kendi `ton.py` dosyasini kullanir). Dairesel import riski yoktur.

### Dogrulama komutlari

```
set PYTHONIOENCODING=utf-8 && set PYTHONPATH=src && python -m pytest tests/test_ui_components.py -q
set PYTHONIOENCODING=utf-8 && set PYTHONPATH=src && python -m pytest tests/test_ui_components.py::test_metric_card_turkce_sayi_bicimi -q
```

### Kabul kriterleri

- [ ] `tests/test_ui_components.py` tamami yesil (0 failed)
- [ ] `test_metric_card_turkce_sayi_bicimi` yesil
- [ ] `card.py` icinde artik `.replace(",", "#")` gecmiyor
- [ ] Baska hicbir dosya degismedi

---

## BOLUM 2 - MRK-02g: tests/test_i18n.py - 13 bekci testi

### Amac

Dil paketinin sozlesmesini kalici olarak koruyan test dosyasi. Ileride biri
yanlis anahtar eklerse test kirmizi olacak.

### Olusturulacak tek dosya

```
tests/test_i18n.py
```

Dosya UTF-8 olacak, BOM OLMAYACAK. Ilk satir `# -*- coding: utf-8 -*-`.

### Ortak yardimci (dosyanin basina)

```python
import json
import re
from pathlib import Path

import pytest

from company_master.i18n import (
    I18nHatasi,
    ParametreHatasi,
    anahtarlar,
    onbellek_temizle,
    ses,
    sozluk,
    t,
)

KOK = Path(__file__).resolve().parents[1] / "src" / "company_master" / "i18n"
SES_DOSYA = KOK / "ses.json"
UI_DOSYA = KOK / "ui.json"

TONLAR = {"info", "success", "warning", "danger", "neutral"}
KATMANLAR = {"veri", "cerceve"}


def _ham(dosya: Path) -> dict:
    veri = json.loads(dosya.read_text(encoding="utf-8"))
    return {k: v for k, v in veri.items() if not k.startswith("_")}


SES_KAYITLAR = _ham(SES_DOSYA)
UI_KAYITLAR = _ham(UI_DOSYA)
TUM_KAYITLAR = {**SES_KAYITLAR, **UI_KAYITLAR}
```

### 13 BEKCI - her biri ayri test fonksiyonu

Cok kayitli kontrollerde `@pytest.mark.parametrize("anahtar", sorted(...))`
kullan, boylece hangi anahtarin patladigi test adindan okunur.

| # | Test adi | Kural | Kapsam |
|---|---|---|---|
| 1 | `test_bekci_01_tr_ve_en_kumeleri_esit` | Her kayitta hem `tr` hem `en` anahtari var | TUM |
| 2 | `test_bekci_02_deger_bos_degil` | `tr`/`en` degerleri bos string degil; obje ise icindeki her varyant bos degil | TUM |
| 3 | `test_bekci_03_bilinmeyen_anahtar_cokmez` | `t("gercekten_olmayan_bir_anahtar")` cagrisi istisna atmaz ve anahtarin kendisini dondurur; `ses(...).bulundu is False` | - |
| 4 | `test_bekci_04_ses_json_marka_oneki` | `ses.json` anahtari `huginn_` / `muninn_` / `odin_` ile baslar | SADECE ses.json |
| 5 | `test_bekci_05_ses_json_en_az_uc_parca` | `ses.json` anahtari `_` ile bolununce en az 3 parca | SADECE ses.json |
| 6 | `test_bekci_06_ton_gecerli` | `ton` alani varsa 5 degerden biri; yoksa testi atlama, `ton` alaninin VARLIGI zorunlu | TUM |
| 7 | `test_bekci_07_eksik_parametre_acik_hata` | `t("veri_sonuc_sayisi")` -> `ParametreHatasi`; `t("veri_sonuc_sayisi", sayi=5, fazla=1)` -> `ParametreHatasi`; `t("veri_sonuc_sayisi", sayi=5)` -> "5" gecer | - |
| 8 | `test_bekci_08_katman_zorunlu` | Her kayitta `katman` var ve `veri` veya `cerceve` | TUM |
| 9 | `test_bekci_09_veri_katmani_duz_string` | `katman == "veri"` olan kayitlarda `tr` ve `en` MUTLAKA `str` (dict olamaz) | TUM |
| 10 | `test_bekci_10_veri_katmaninda_mitoloji_yok` | `katman == "veri"` kayitlarinda yasakli sozcuk gecmez | TUM |
| 11 | `test_bekci_11_cerceve_objede_cirak_zorunlu` | `katman == "cerceve"` ve `tr` bir dict ise `cirak` anahtari var ve bos degil | TUM |
| 12 | `test_bekci_12_en_asla_obje_degil` | Hicbir kayitta `en` degeri dict degil | TUM |
| 13 | `test_bekci_13_marka_yazim_hatasi_yok` | Tum metinlerde hatali marka yazimi yok | TUM |

#### Bekci 4 ve 5 icin ONEMLI MUAFIYET

`ui.json` anahtarlari bu iki kuraldan TAMAMEN MUAFTIR.
Sebep: `menu_kpi`, `h1_musteri`, `eylem_ara`, `durum_aktif` gibi anahtarlar
marka onegi tasimaz ve 2 parcalidir; bu tasarim geregidir.
Bu iki testi SADECE `SES_KAYITLAR` uzerinde parametrize et.

#### Bekci 10 - yasakli sozcuk listesi

```python
MITOLOJIK_SOZCUKLER = (
    "huginn", "muninn", "odin", "bifrost", "bifrost",
    "diyar", "kuzgun", "taht", "muhur",
)
```

Karsilastirma kucuk harfe cevirerek yapilacak. Turkce karakter iceren
varyantlari da yakalamak icin metni once `casefold()` uygula, sonra
su normalizasyonu yap: `o->o`, `u->u`, `i->i` gibi ASCII katlamasi gerekmiyor;
bunun yerine liste icine Turkce yazimlari da ekle:

```python
MITOLOJIK_SOZCUKLER = (
    "huginn", "muninn", "odin", "bifröst", "bifrost",
    "diyar", "kuzgun", "taht", "mühür", "muhur",
)
```

Kontrol: `veri` katmanindaki `tr` + `en` metinlerinin `casefold()` halinde
bu sozcuklerden hicbiri GECMEYECEK.

BEKLENEN SONUC: Bu test simdi YESIL olmalidir. `odin_baglanti_koptu` gibi
anahtarlar `veri` katmanindadir ama metinleri bilerek mitolojisizdir
("Baglanti kesildi (503). Yeniden deneniyor."). Anahtar ADI kontrole DAHIL
DEGILDIR, sadece METIN kontrol edilir. Bunu karistirma.

#### Bekci 13 - hatali yazim deseni

```python
HATALI_YAZIM = re.compile(r"Muginn|Hugin\b|Munin\b|Hugginn|Munnin|Odinn", re.IGNORECASE)
```

Tum kayitlarin `tr` + `en` metinleri (obje ise tum varyantlari) bu desenle
eslesmeyecek.

### Ek testler (bekci disi, 4 adet)

```python
def test_onbellek_temizleme_calisir():
    # onbellek_temizle() cagrisi istisna atmaz, sonrasinda t() hala calisir

def test_anahtar_sayisi_beklenen_aralikta():
    # len(anahtarlar()) == len(TUM_KAYITLAR) ve >= 170

def test_ses_ve_ui_anahtar_cakismasi_yok():
    # set(SES_KAYITLAR) & set(UI_KAYITLAR) bos olmali

def test_seviye_fallback_calisir():
    # t("huginn_liste_bos", seviye="cirak") ve seviye="usta" FARKLI metin dondurur
    # ikisi de bos degil
```

### Dogrulama komutlari

```
set PYTHONIOENCODING=utf-8 && set PYTHONPATH=src && python -m pytest tests/test_i18n.py -q
set PYTHONIOENCODING=utf-8 && set PYTHONPATH=src && python -m pytest tests/test_i18n.py -q --tb=short
```

### Beklenen cikti ornegi

```
...................................................................      [100%]
XXX passed in 0.5s
```

### Kabul kriterleri

- [ ] `tests/test_i18n.py` olusturuldu, UTF-8, BOM yok
- [ ] 13 bekcinin hepsi ayri test fonksiyonu olarak var
- [ ] Ek 4 test var
- [ ] Tum testler yesil VEYA kirmizi kalanlar raporlandi (JSON DUZELTILMEDI)
- [ ] `src/company_master/i18n/` altindaki hicbir dosya degismedi

---

## BOLUM 3 - TESLIM PROTOKOLU

Isi bitirince:

```
python scripts/gorev_kutusu.py teslim --ajan cline --task-id MRK-02F --ozet "card.py _deger_metni i18n.sayi() delegasyonu; test_ui_components yesil"
python scripts/gorev_kutusu.py teslim --ajan cline --task-id MRK-02G --ozet "tests/test_i18n.py 13 bekci + 4 ek test; N passed"
```

Teslim ozetinde MUTLAKA belirt:
1. Kac test gecti / kac test kaldi
2. Bekci testlerinden KIRMIZI kalan varsa: hangi anahtar, hangi bekci, tam metin
3. Dokunulan dosyalarin tam listesi

Gorev `review` durumuna duser, `done` YAPMA. Onayi orkestrator verir.
