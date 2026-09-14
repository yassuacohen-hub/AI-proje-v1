# BRIEF - KILO - MRK-02h: messages.js ureticisi

Hazirlayan: roo (orkestrator)
Hedef ajan: kilo
Oncelik: P2
Bagimlilik: YOK. Bagimsiz calisabilir.

---

## BOLUM 0 - AMAC

Huginn (port 8000, saf HTML/CSS/JS) tarayicida calisir, Python i18n paketini
import edemez. Bu yuzden Python sozlugunden **uretilmis** bir JS dosyasi lazim.

Tek kaynak (SSOT) Python tarafindaki JSON'lardir. JS dosyasi ELLE YAZILMAZ,
her zaman script ile uretilir.

Bu gorevde IKI dosya olusturulacak:

1. `src/company_master/i18n/disa_aktar.py` - uretici modul + CLI
2. `web_dashboard/js/messages.js` - scriptin urettigi cikti (elle yazilmaz, script calistirilarak uretilir)

---

## BOLUM 1 - MEVCUT DURUM (degistirilmeyecek)

`src/company_master/i18n/` paketi hazir ve calisiyor. Kullanacagin yuzey:

```python
from company_master.i18n import sozluk

kayitlar = sozluk()   # dict[str, dict[str, Any]]
```

`sozluk()` `ses.json` + `ui.json` dosyalarini birlestirip dondurur.
`_` onekli meta anahtarlar zaten filtrelenmistir.
Toplam 182 kayit doner.

Her kaydin yapisi:

```python
{
    "tr": "metin"  ya da  {"cirak": "...", "usta": "..."},
    "en": "metin",
    "katman": "veri" | "cerceve",
    "ton": "info" | "success" | "warning" | "danger" | "neutral",
    "ikon": "material_symbol_adi"    # bazen yok
}
```

### KESIN YASAK - DOKUNULMAYACAK DOSYALAR

```
src/company_master/i18n/ses.json
src/company_master/i18n/ui.json
src/company_master/i18n/__init__.py
src/company_master/i18n/ton.py
src/company_master/ui/**
tests/**
app.py
web_dashboard/tabs/**
web_dashboard/index.html
.env, .env.*
data/orchestrator/**
```

Bu gorevde SADECE su iki dosya olusturulur/degistirilir:

```
src/company_master/i18n/disa_aktar.py       (YENI)
web_dashboard/js/messages.js                (YENI - script uretir)
```

---

## BOLUM 2 - disa_aktar.py SARTNAMESI

### Dosya basligi

Ilk satir `# -*- coding: utf-8 -*-`, UTF-8, BOM YOK.
Modul docstring'i Turkce yaz.

### Hangi anahtarlar disa aktarilacak

Huginn'in ihtiyaci olanlar. Filtre kurali:

```python
HUGINN_ONEKLERI = ("menu_h_", "eylem_", "durum_", "veri_", "huginn_")
```

Bir anahtar disa aktarilir EGER:
- Bu oneklerden biriyle basliyorsa, VEYA
- `ODIN_ORTAK` listesinde ise (asagida)

```python
# Huginn'in de gosterdigi ortak hata/onay metinleri
ODIN_ORTAK = (
    "odin_baglanti_koptu",
    "odin_sunucu_hatasi",
    "odin_zaman_asimi",
    "muninn_yetki_yok",
    "muninn_oturum_doldu",
)
```

`menu_` ile baslayip `menu_h_` ile BASLAMAYAN anahtarlar (Muninn menuleri)
disa AKTARILMAZ. `h1_*` anahtarlari da AKTARILMAZ (Muninn'e ait).

### Cikti JS formati

Uretilecek dosya sablonu (birebir bu yapida):

```javascript
// -*- coding: utf-8 -*-
// OTOMATIK URETILDI - ELLE DUZENLEMEYIN
// Kaynak: src/company_master/i18n/ses.json + ui.json
// Uretici: src/company_master/i18n/disa_aktar.py
// Uretim: python -m company_master.i18n.disa_aktar

export const MESSAGES = {
  "tr": {
    "anahtar_adi": { "metin": "...", "katman": "veri", "ton": "neutral", "ikon": "..." },
    ...
  },
  "en": {
    "anahtar_adi": { "metin": "...", "katman": "veri", "ton": "neutral", "ikon": "..." },
    ...
  }
};

export const VARSAYILAN_DIL = "tr";
export const VARSAYILAN_SEVIYE = "usta";

let _dil = VARSAYILAN_DIL;

export function dilAyarla(dil) {
  if (dil in MESSAGES) { _dil = dil; }
  return _dil;
}

export function aktifDil() { return _dil; }

export function ses(anahtar, parametreler) {
  const tablo = MESSAGES[_dil] || MESSAGES[VARSAYILAN_DIL];
  let kayit = tablo[anahtar];
  if (!kayit) { kayit = MESSAGES[VARSAYILAN_DIL][anahtar]; }
  if (!kayit) {
    return { metin: anahtar, katman: "veri", ton: "neutral", ikon: "circle", bulundu: false };
  }
  let metin = kayit.metin;
  if (parametreler) {
    for (const [ad, deger] of Object.entries(parametreler)) {
      metin = metin.split("{" + ad + "}").join(String(deger));
    }
  }
  return { metin: metin, katman: kayit.katman, ton: kayit.ton, ikon: kayit.ikon, bulundu: true };
}

export function t(anahtar, parametreler) {
  return ses(anahtar, parametreler).metin;
}
```

### Seviye kurali (ONEMLI)

Bir kaydin `tr` degeri obje ise (`{"cirak": ..., "usta": ...}`), JS ciktisina
**`usta` varyanti** yazilir. Huginn su an tek varyant kullaniyor.
`usta` yoksa `cirak` kullanilir.

`en` degeri her zaman duz string'dir, oldugu gibi yazilir.

### `ikon` alani yoksa

Kayitta `ikon` yoksa tona gore varsayilan kullan:

```python
TON_IKON_VARSAYILAN = {
    "info": "info",
    "success": "check_circle",
    "warning": "warning",
    "danger": "error",
    "neutral": "circle",
}
```

### Fonksiyon yuzeyi (disa_aktar.py icinde tanimlanacak)

```python
HEDEF: Final[Path]        # repo koku / "web_dashboard" / "js" / "messages.js"

def huginn_anahtarlari() -> tuple[str, ...]:
    """Disa aktarilacak anahtarlari sirali dondurur."""

def kayit_donustur(anahtar: str, kayit: dict, dil: str) -> dict:
    """Tek kaydi JS'e yazilacak sade dict'e cevirir (metin/katman/ton/ikon)."""

def js_uret() -> str:
    """Tam messages.js icerigini string olarak uretir."""

def yaz(hedef: Path | None = None) -> Path:
    """Icerigi diske yazar (UTF-8, LF satir sonu). Yazilan yolu dondurur."""

def kontrol(hedef: Path | None = None) -> bool:
    """Diskteki dosya uretilecek icerikle ayni mi? CI icin."""

def main() -> int:
    """CLI giris noktasi."""
```

### CLI (argparse)

```
python -m company_master.i18n.disa_aktar              -> uretir ve yazar
python -m company_master.i18n.disa_aktar --kontrol    -> yazmaz, fark varsa exit 1
python -m company_master.i18n.disa_aktar --hedef X    -> ozel hedef yolu
```

Ciktiyi Turkce ve kisa yaz, ornegin:

```
URETILDI : web_dashboard/js/messages.js
ANAHTAR  : 61
DIL      : tr, en
```

`--kontrol` modunda fark varsa:

```
FARK VAR : web_dashboard/js/messages.js guncel degil
Cozum    : python -m company_master.i18n.disa_aktar
```

ve `return 1`. Fark yoksa `GUNCEL : ...` yazip `return 0`.

### JSON kacisi

Metinleri JS'e gomerkan Python `json.dumps(..., ensure_ascii=False)` kullan.
Turkce karakterler oldugu gibi kalsin (dosya UTF-8).

### Satir sonu

Dosyayi `newline="\n"` ile yaz (LF). Windows'ta CRLF olusmasin.

---

## BOLUM 3 - DOGRULAMA

```
set PYTHONIOENCODING=utf-8 && set PYTHONPATH=src && python -m company_master.i18n.disa_aktar
set PYTHONIOENCODING=utf-8 && set PYTHONPATH=src && python -m company_master.i18n.disa_aktar --kontrol
```

Ikinci komut `GUNCEL` yazip exit 0 vermeli.

JS sozdizimi kontrolu (node varsa):

```
node --input-type=module -e "import('./web_dashboard/js/messages.js').then(m => { console.log('ANAHTAR', Object.keys(m.MESSAGES.tr).length); console.log('T', m.t('durum_aktif')); console.log('PARAM', m.t('veri_sonuc_sayisi', {sayi: 42})); console.log('BILINMEYEN', m.t('yok_boyle')); })"
```

Beklenen:

```
ANAHTAR 61
T Aktif
PARAM 42 kayit listeleniyor.
BILINMEYEN yok_boyle
```

Not: anahtar sayisi tam 61 olmayabilir, yaklasik 55-70 arasi normaldir.
Onemli olan `t()` fonksiyonunun dogru calismasi.

Node yoksa bu adimi atla ve teslimde "node yok, JS runtime dogrulamasi
yapilamadi" diye belirt.

---

## BOLUM 4 - KABUL KRITERLERI

- [ ] `src/company_master/i18n/disa_aktar.py` olusturuldu, UTF-8, BOM yok
- [ ] Modulde `huginn_anahtarlari`, `kayit_donustur`, `js_uret`, `yaz`, `kontrol`, `main` var
- [ ] `web_dashboard/js/messages.js` uretildi (elle yazilmadi)
- [ ] `messages.js` basinda "OTOMATIK URETILDI - ELLE DUZENLEMEYIN" uyarisi var
- [ ] `--kontrol` komutu exit 0 veriyor
- [ ] Muninn'e ait `menu_*` (menu_h_ olmayan) ve `h1_*` anahtarlari JS'te YOK
- [ ] `ses.json`, `ui.json`, `__init__.py`, `ton.py` DEGISMEDI
- [ ] Baska hicbir dosya degismedi

---

## BOLUM 5 - TESLIM PROTOKOLU

```
python scripts/gorev_kutusu.py teslim --ajan kilo --task-id MRK-02H --ozet "disa_aktar.py + messages.js uretildi; --kontrol exit 0; N anahtar"
```

Teslim ozetinde belirt:
1. Kac anahtar disa aktarildi
2. `--kontrol` ciktisi
3. Node dogrulamasi yapildi mi, sonucu ne
4. Dokunulan dosyalarin tam listesi

Gorev `review` durumuna duser, `done` YAPMA. Onayi orkestrator verir.
