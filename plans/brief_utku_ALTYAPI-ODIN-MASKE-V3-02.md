# ALTYAPI-ODIN-MASKE-V3-02 — Brief (utku)

**Başlık:** [ALTYAPI] ALTYAPI-ODIN-MASKE-V3-01 kodu depoda yok — `sunum.py` V3 kaynak katmanını testten yeniden yaz (2s)
**Öncelik:** P1 · **Kit:** `ALTYAPI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/sunum.py`
**Bağımlılık:** yok (ALTYAPI-ODIN-MASKE-V3-01 done ama kodu kayıp)
**Hub:** `hubs/ORKESTRASYON_AJANLAR_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif.

## Neden
- `tests/test_odin_kapi_olcumu.py:30-47` `company_master.sunum`'dan `ODIN_KAYNAK_MUSTERI, ODIN_KAYNAK_TANIM, ODIN_KAYNAKLAR, _odin_kaynak_temizle, odin_kaynak_dogrula, odin_musteri_cikis_kapisi` import eder → **ImportError**, dosya toplanamıyor.
- `src/company_master/sunum.py` (HEAD = çalışma kopyası) bu adların hiçbirini içermiyor (`findstr ODIN_KAYNAK` → 0).
- Pano kaydı ALTYAPI-ODIN-MASKE-V3-01 `done` (2026-10-04T20:15, "35 test passed"). Commit `5928730a` mesajı: "sunum.py (utku kilitli, aktif) haric tutuldu". Sonrasında `reset: moving to HEAD` ×5 (reflog 2026-10-04). Kod ne commit'te, ne 10 stash'te, ne 24 dangling blob'da. **Kayıp.**
- Test dosyası commit'lenmiş (`5928730a`), yani şartname elde; sadece uygulama yok.

## Doğrulanacak varsayım
- `tests/test_odin_kapi_olcumu.py` tek şartnamedir; **test dosyasına dokunulmaz** (D-211 ikiz yasağı, D-256/4 kırılma denemeleri içeride).
- `sunum.py:342` `odin_kapi_olcumu(model_yaniti)` ve `:281` `maskeleme_odin(metin, hedef)` mevcut imzalar; `kaynak=` **opsiyonel** parametre eklenir, eski çağrılar bozulmaz (`odin_kapi_olcumu(ham, kaynak=ODIN_KAYNAK_MUSTERI) == odin_kapi_olcumu(ham)` test :369).
- `ODIN_KAYNAKLAR == {"v3"}`, `ODIN_KAYNAK_MUSTERI == "v3"`, `ODIN_KAYNAK_TANIM` dict `{"v3": <maske küme>}` (test :~200 `set(ODIN_KAYNAK_TANIM) == set(ODIN_KAYNAKLAR) == {"v3"}`).
- `_odin_kaynak_temizle`: `"V3"→"v3"`, `3→"v3"`, `"  v3  "→"v3"`, `"v1"→"v1"`, `None→""`.
- `odin_kaynak_dogrula`: fail-closed — tanımsız/belirsiz (`"v9"`, `"v1"`, boş) → `ODIN_KAYNAK_MUSTERI`.
- `odin_musteri_cikis_kapisi(metin, kaynak=None) -> dict`; anahtarlar en az `kaynak`, `kaynak_istenen`, `kapi`, `kapi_tanimli`; `kaynak="v1"` istenirse `kaynak_istenen="v1"`, `kaynak="v3"`, uyuşmazlıkta `kapi == ODIN_KAPI_INCELEME` (D-339, test :~320-345).
- `sunum.__all__` var (:~50) → yeni 6 ad eklenir (test :408-414 `__all__` denetler).
- Varsayım tutmuyorsa **dur**, `ajan_chat.py ac` ile sorun aç; uydurma.

## Adımlar
1. `python -m pytest tests\test_odin_kapi_olcumu.py -x -q` → ImportError'ı gör (başlangıç ölçümü).
2. Testi baştan sona oku; her assert'i şartname maddesine çevir (yukarıdaki liste eksikse testi esas al).
3. `sunum.py`'de `## Odin` bölümüne (`:268` `_ODIN_YASAK_DESENLER` civarı) sabitler + 3 fonksiyon + `maskeleme_odin`/`odin_kapi_olcumu`'na `kaynak=None` parametresi.
4. `__all__` güncelle.
5. Kırılma denemesi (D-256/4): `odin_kaynak_dogrula`'da fail-closed dalını geçici kaldır → ilgili test kırmızı → geri al → yeşil. Teslim notuna yaz.
6. `python -m pytest tests\test_odin_kapi_olcumu.py tests\test_sunum*.py -q` tamamı yeşil.
7. **Commit et** (`HUGINN_AJAN=utku`), çalışma kopyasında bırakma — bu görev tam olarak o yüzden açıldı.

## Kabul kriteri
- [ ] `pytest tests\test_odin_kapi_olcumu.py` → collected, 0 failed, 0 error.
- [ ] `git log -1 -- src/company_master/sunum.py` yeni commit'i gösterir (kod depoda).
- [ ] Eski çağrılar (`kaynak` vermeyen) aynı sonucu verir: `grep -rn "maskeleme_odin(\|odin_kapi_olcumu(" src web_app.py` çıkan tüm çağrı yerleri değişmeden çalışır.
- [ ] Kırılma denemesi teslim notunda (hangi satır, hangi test kırmızıya döndü).
- [ ] Hub satırı yazıldı.

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- Test dosyasını değiştirme; sadece `sunum.py`.
- **Teslimden önce** `hubs/ORKESTRASYON_AJANLAR_HUB.md` "Kapanan işler" bölümüne `ALTYAPI-ODIN-MASKE-V3-02` satırı yaz (B-14).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Varsayım tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.

```bash
python scripts/ajan_chat.py ac utku ALTYAPI-ODIN-MASKE-V3-02 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id ALTYAPI-ODIN-MASKE-V3-02
python scripts/chat_gonder.py --to ihsan --type hata --task-id ALTYAPI-ODIN-MASKE-V3-02 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id ALTYAPI-ODIN-MASKE-V3-02 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan utku
```

- Çıkış `0` = **İŞ VAR** → hemen yap.
- Çıkış `3` = 60 dk iş gelmedi → ihsan'a kısa rapor yaz, sonra kapat.

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[plans/brief_utku_ALTYAPI-ODIN-MASKE-V3-01]]
- [[hubs/ORKESTRASYON_AJANLAR_HUB]]
