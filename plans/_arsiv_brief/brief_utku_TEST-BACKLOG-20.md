# TEST-BACKLOG-20 — Brief (utku)

**Başlık:** [TEST] Tam suite'teki 20 basarisiz testi sifira indir (8s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** çoklu — faz başlıklarında tek tek yazılı
**Bağımlılık:** yok
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bu tek görev, 6 faz. Faz başına ayrı brif/görev/tetik açılmaz.

## Neden

`pytest tests/ -q` → **20 failed**, 4260 passed, 12 skipped. Bu backlog D-214'ten beri
[`AGENTS.md:949`](../AGENTS.md:949) "kapsam dışı bırakılan" listesinde bekliyor.
20 hatanın hepsi tek tek koşturulup gövdesi okundu — **hayalet yok, hepsi gerçek kusur**
(D-216'daki 8 hayalet görevin aksine).

## Doğrulanacak varsayım

- `pytest tests/ -q` çıktısının **20 failed** olduğu varsayıldı. Sayı farklıysa **dur**, panoya sorun aç.
- `src/company_master/schema/migrations/0016_users_last_login.down.sql` ve
  `0017_user_activity_log.down.sql` dosyalarının **migrations kökünde** olduğu varsayıldı (doğrulandı).
  Yoksa **dur**, uydurma.
- `src/company_master/schema/migrations/down/` dizininde **16 dosya** olduğu, en az 19 beklendiği varsayıldı.
  Farklıysa **dur**, panoya sorun aç.
- `company_master.core.error_handling` modülünde `setup_logging` bulunduğu varsayıldı
  ([`tests/test_error_handling.py:28`](../tests/test_error_handling.py:28) import'u böyle). Farklıysa **dur**.
- [`web_dashboard/tabs/admin_mfa.py`](../web_dashboard/tabs/admin_mfa.py) ve
  [`ana_kontrol.py`](../web_dashboard/tabs/ana_kontrol.py) dosyalarının var olduğu varsayıldı (doğrulandı).
- `migrate.py` yolunun `src/company_master/schema/migrations/migrate.py` olduğu varsayıldı (doğrulandı;
  `schema/migrate.py` **yok**, `db/migrate.py` ayrı dosya). Karıştırma.

---

## Adımlar

Fazları **sırayla** yap, her fazdan sonra o fazın test dosyalarını koştur.
Hepsi bitince tam suite'i bir kez koştur ve tek raporla teslim et.

---

## Faz A — Migration down düzeni (9 test) — P1, veri kaybı riski

**Kök neden 1:** `0017_user_activity_log.down.sql` ve `0016_users_last_login.down.sql`
migrations **kökünde** duruyor. Olması gereken: `migrations/down/0017_user_activity_log.sql`,
`migrations/down/0016_users_last_login.sql`.
Kökte kaldıkları için [`migrate.py`](../src/company_master/schema/migrations/migrate.py) up-glob'una
takılıyor — rollback SQL'i **ileri migration sanılıp çalıştırılabilir**. Tabloyu düşüren DDL bu,
yani veri kaybı. Bu yüzden P1.

**Kök neden 2:** `down/` altında 16 dosya var, en az 19 bekleniyor → 3 migration'ın rollback'i hiç yok.

Testler:
```
tests/test_migration_0017.py  (5 test: down_exists, down_drops_table,
                               down_drops_indexes, down_cleans_schema_migrations,
                               no_root_down_file)
tests/test_schema_validation.py (4 test: migration_files_exist, migration_down_files_content,
                                 migration_down_files_format, migrations_apply_rollback)
```

Yapılacak:
1. İki `.down.sql` dosyasını `git mv` ile `down/` altına kanonik adla taşı (`.down.sql` → `.sql`).
   `git mv` kullan, kopyala-sil değil — dosya geçmişi kopmasın.
2. Eksik 3 down dosyasını yaz. Her biri kendi up'ını **tam** geri alsın: tablo/index düşür +
   `schema_migrations` satırını temizle. Hangi 3'ü olduğunu `test_migration_files_exist` çıktısı söylüyor.
3. `test_migration_0017_no_root_down_file` bir regresyon bekçisi — kökte tekrar `.down.sql`
   oluşmasını engelliyor. **Zayıflatma**, koda uy.
4. `migrate.py` glob'una tek satırlık savunma ekle: `.down.sql` up olarak yüklenmesin.

---

## Faz B — Sayfa iskeleti (3 test) — D-214/D-215 devamı

```
tests/test_sayfa_iskeleti.py::test_ekran_section_kullanir[admin_mfa]
tests/test_sayfa_iskeleti.py::test_ekranda_subheader_kalmaz[admin_mfa]
tests/test_sayfa_iskeleti.py::test_ekranda_elle_markdown_baslik_kalmaz[ana_kontrol]
```

- [`web_dashboard/tabs/admin_mfa.py`](../web_dashboard/tabs/admin_mfa.py): SECTIONS sözleşmesine
  geçir, elle `st.subheader` bırakma.
- [`web_dashboard/tabs/ana_kontrol.py`](../web_dashboard/tabs/ana_kontrol.py): elle yazılmış
  markdown başlığı (`## ...`) kaldır, section başlığına devret.
- Bu iki dosyaya D-215'te dokunuldu, bağlam taze. Menü ağacını **bozmadan** yap —
  `test_tabs_ia.py` ve `test_auth_gate.py` yeşil kalmalı.

---

## Faz C — Log altyapısı (3 test)

```
tests/test_error_handling.py::TestSetupLogging::test_json_format_kapaliyken_insan_okuunur
tests/test_error_handling.py::TestFileRotation::test_dosya_hedefine_yazilir
tests/test_error_handling.py::TestFileRotation::test_stdout_ve_dosya_ikili_cikti
```

Hedef modül: `company_master.core.error_handling` → `setup_logging`.
- JSON kapalıyken insan-okunur formatter'a düşmüyor.
- Dosya hedefi yazılmıyor; stdout + dosya ikili çıktı kurulmuyor.
- Stdlib `logging.handlers.RotatingFileHandler` yeterli — yeni bağımlılık ekleme.

---

## Faz D — API rotaları (2 test)

```
tests/test_api_integration.py::TestRotaEnvanteri::test_tum_api_rotalari_tanimli_listeyle_eslesir
tests/test_api_integration.py::TestVeriUclari::test_match_gecersiz_buyer_404
```

- Rota envanteri ile gerçek rotalar ayrışmış: envanteri **gerçeğe göre** güncelle, tersini değil —
  ama önce ayrışan rotanın kasıtlı mı yoksa unutulmuş mu olduğunu kontrol et.
- Geçersiz `buyer` için 404 dönmüyor. Bu bir **giriş doğrulama** açığı; 404'ü doğru yerde ver,
  testi gevşetme.

---

## Faz E — Denetim (2 test)

```
tests/test_marka_denetim_muafiyet.py::test_kok_denetimi_temiz
tests/test_pano_denetim.py::test_pano_yolu_kanonik
```

- Kök marka denetimi kirli: muafiyet listesine körlemesine ekleme yapma, **neden** kirli olduğunu bul.
- Pano yolu kanonik değil — D-168 pano yolu tek olmalı. Worktree kopyaları karışıyor olabilir.

---

## Faz F — Kullanıcı ayarları (1 test)

```
tests/test_user_settings.py::test_panel_formu_sema_uzerinden_uretir
```

Panel formu şemadan üretilmiyor, elle kodlanmış. Şema tek kaynak olsun.

---

## Kabul kriteri

- [ ] Faz A: `pytest tests/test_migration_0017.py tests/test_schema_validation.py -q` → 0 failed
- [ ] Faz B: `pytest tests/test_sayfa_iskeleti.py tests/test_tabs_ia.py tests/test_auth_gate.py -q` → 0 failed
- [ ] Faz C: `pytest tests/test_error_handling.py -q` → 0 failed
- [ ] Faz D: `pytest tests/test_api_integration.py -q` → 0 failed
- [ ] Faz E: `pytest tests/test_marka_denetim_muafiyet.py tests/test_pano_denetim.py -q` → 0 failed
- [ ] Faz F: `pytest tests/test_user_settings.py -q` → 0 failed
- [ ] **Tam suite: `pytest tests/ -q` → 0 failed** (20 → 0), passed sayısı 4260'tan düşmesin

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; stdlib + mevcut paketlerle çöz.
- **Teslimden önce** `hubs/ADMIN_DASHBOARD_HUB.md` "Kapanan işler" bölümüne `TEST-BACKLOG-20` yaz (B-14 kapısı).

### Yasak

- Test `skip`/`xfail` işaretlemek veya assert gevşetmek. 20 testin hepsi gerçek kusur gösteriyor.
- Faz sırasını bozmak: A veri kaybı riski taşıyor, ilk o.
- Faz başına ayrı görev/brif açmak (D-217).

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Brifi yeniden okuyup bekleme — **yaz**:

- Yukarıdaki varsayımlardan biri kodda tutmuyorsa → sorun aç, **uydurma, durma**.
- Bir faz tıkandıysa → sorun aç, **sonraki faza geç**, zinciri durdurma. KAHİN karar verir.
- @mention aldıysan → P1 olduğu için **10-15 dk** içinde cevap zorunlu.

```bash
python scripts/ajan_chat.py ac utku TEST-BACKLOG-20 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id TEST-BACKLOG-20
python scripts/chat_gonder.py --to ihsan --type hata --task-id TEST-BACKLOG-20 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim-et --ajan utku --task-id TEST-BACKLOG-20 \
  --rapor "20 test kapatildi: A=9 B=3 C=3 D=2 E=2 F=1; tam suite 20->0; bloke: yok"
```

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
