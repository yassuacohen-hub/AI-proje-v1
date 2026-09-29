# Borç Defteri — tek kanonik kayıt (D-272)

**Bu dosya borç listesinin tek kaynağıdır.** Devir notu buradan okunur, hafızadan değil.
`AGENTS.md` kararın *gerekçesini* tutar; bu defter *durumunu* tutar.

**Neden ayrı dosya:** `AGENTS.md` içindeki D-kayıtları kronolojik değil (ölçüm D-272/1:
`[…263, 266, 265, 264, 267, 268, 270, 269, 271]`). Bu yüzden bir borcun son durumu dosyada
**aşağıda** değil, **en büyük D numarasında** yazılıdır. Satır sırasıyla okuyan her tur
yanlış okudu — altı tur üst üste (D-265, D-266, D-267/1, D-268/1, D-271/1).

**Kural (D-272):**
1. Bir D-kaydı borç kapatıyor/iptal ediyorsa **aynı turda** bu defter güncellenir.
2. Durum alanı yalnız şu değerleri alır: `ACIK` · `KAPANDI` · `IPTAL` · `KURAL` (borç değil, kural/görev kimliği).
3. `AGENTS.md`'de adı geçip bu defterde olmayan kimlik testi düşürür:
   [`tests/test_dokuman_politikasi.py::test_d272_borc_defteri_eksiksiz()`](../tests/test_dokuman_politikasi.py).
4. Başlık fiil taşımaz (D-271).

---

## Borçlar

| Kimlik | Ölçülen sapma | Durum | Kaynak D | Kapanış D |
|---|---|---|---|---|
| `BORC-NACE-DOGRULAMA-01` | `nace_validity` alanı kaynaksız | ACIK | D-258 | — |
| `BORC-PANO-BORC-00` | borç listesinin kanonik kaydı yok | KAPANDI | D-271 | D-272 |
| `BORC-SCRIPTS-01` | `scripts/` altında 41 `_*` girdi (19 `_tmp_*`, 3 `_olcum_*`, 19 diğer) | ACIK | D-255 | — |
| `BORC-SICIL-DAIRE-01` | 619 firmada sicil no var, sicil dairesi yok | ACIK | D-260 | — |
| `BORC-VKN-01` | VKN kanalı ölü, kaynak bulunamadı | ACIK | D-253 | — |
| `BORC-AD-VARYANT-01` | 31 kısaltma varyantı | IPTAL | D-261 | D-263 |
| `BORC-ADLANDIRMA-01` | kimlik hiç açılmamıştı (devir notu uydurdu) | IPTAL | — | D-271 |
| `BORC-DEDUP-KAYNAK-01` | `content_hash` yinelenmeyi durdurmuyor | KAPANDI | D-261 | D-262 |
| `BORC-DEFTER-IKI-SEMA-01` | kimlik hiç açılmamıştı; uyarı gerçek, borç değil | IPTAL | — | D-271 |
| `BORC-EXTID-01` | `baskentosb.org.tr` kazıyıcısı `external_id` üretmiyordu | KAPANDI | D-261 | D-262 |
| `BORC-GOC-IKI-DEFTER-01` | göç defteri iki değil üç, yazan yol dört | KAPANDI | D-264 | D-265 (son yol D-271) |
| `BORC-KOLON-DUSUR-01` | ölü kolon aktif sanılıyordu | KAPANDI | D-258 | D-259 |
| `BORC-PANEL-TAVAN-01` | panel tavanı sabit yazıyordu | KAPANDI | D-253 | D-258 |
| `BORC-PERF-BANT-01` | performans bandı yanlış; yüzeyin çağıranı yoktu | KAPANDI | D-259 | D-266 |
| `BORC-QUALITY-BETIK-01` | adı geçen betik diskte yok | IPTAL | D-255 | D-271 |
| `BORC-TASFIYE-IKIZ-01` | 22 tasfiye önekli firma öneksiziyle ikiz | KAPANDI | D-263 | D-264 |
| `BORC-TEST-SIRA-01` | test sırası bağımlılığı; iki kirleten | KAPANDI | D-267 | D-271 |
| `VERI-KAYNAK-BAG-01` | 5060 yetim firma, kaynak bağı yok | KAPANDI | D-260 | D-263 |

## Borç değil — kural / görev kimlikleri

Mandal `BORC-*` ile `VERI-*` kimliklerini birlikte tarar; aşağıdakiler borç değil, bu
yüzden ayrı bölümde durur. Silinmezler: adları `AGENTS.md`'de geçtiği sürece defterde kalır.

| Kimlik | Ne | Durum | D |
|---|---|---|---|
| `VERI-ETIKET-01` | her blok kaynağını söyler | KURAL | D-213 |
| `VERI-HAYALET-TEMIZ-01` | 9412 firma + UNIQUE indeks, onaylandı | KURAL | D-260 |
| `VERI-KAYNAK-TURU-01` | kaynak türü sözleşmesi | KURAL | D-235 |
| `VERI-KAZIYICI-DONGU-01` | kazıyıcı döngü sözleşmesi | KURAL | D-235 |
| `VERI-KOLON-IKIZ-01` | `companies.vergi_no` ikiz kolon ölçümü | KURAL | D-245 |
| `VERI-NACE-KOLON-01` | 0 kaçak NACE etiketi, onaylandı | KURAL | D-260 |
| `VERI-NACE-SOZLUK-01` | 3319 NACE kodu, onaylandı | KURAL | D-260 |
| `VERI-NACE-TEMIZ-01` | 554 `invalid_cleared`, onaylandı | KURAL | D-260 |
| `VERI-GORUNURLUK-01` | **böyle bir kimlik yok.** D-272/5'in anlattığı hayalet; o metni yazmak hayaleti gerçek bir dizeye çevirdi. Deftere iptal olarak girer, çünkü çıkarmanın yolu kaydı silmek olurdu | IPTAL | D-272 |

## Ölçülmüş sayılar (D-272)

- `AGENTS.md`'de kimlik: **71**. Mandalın gördüğü (`BORC|VERI`): **27**. Dışında kalan: **45**.
- Borç (gerçek): **18** — açık 4, kapandı 10, iptal 4.
- **Kapanmış ama açık/çelişkili sanılan: 2** — `BORC-KOLON-DUSUR-01` ve `BORC-PANEL-TAVAN-01`.
  D-271/6 bunları "çelişki" ilan etti; çelişki yoktu, satır sırası yanlış okundu
  (s2920=D-256 "kapanmadı" → s2945=D-258 "kapandı"; s3037=D-258 → s3121=D-259).
- 45 kimlik mandalın regex kapsamı dışında (`NACE-*`, `KVKK-*`, `GOC-*`, `SEMA-*`…).
  Bu bilinen kör nokta; genişletme ayrı bir tur işi — kapsam büyütmek defteri şişirir,
  fayda ölçülmedi.
- **26 → 27:** D-272/5 metni hayalet kimliği tek başına andığı için mandalın gördüğü kimlik
  bir arttı. Kayıt tutmanın kendisi ölçümü değiştirdi; sayı kılıfına uydurulmadı, gerçeğe
  çekildi (D-271'in tavanı 3 değil 4 yapmasıyla aynı karar).

## Devir — sonraki oturum (D-272 sonrası)

Bu bölüm devir notunun kaynağıdır (D-219 mantığı). Ajan hafıza dosyasına yazılmadı: ölçüldü,
dört `*_project_context.md` dosyasında bu hattın hiçbir izi yok — hat panoya bağlı değil,
doğrudan ürün sahibiyle yürüyor.

- **Kaldığım yer:** D-272 yazıldı ve commit'lendi; hat kapalı. **Hash yazılmıyor:** bu satıra
  hash yazan commit hash'i değiştirir (sonsuz gerileme — ilk yazımda `18fe5a6`/`120416d`
  hemen bayatladı). Konum dalın tepesidir: alt depo `chore/monorepo-merge`, üst depo `master`;
  `git log --oneline -3` ile okunur.
- **Test tabanı yeni:** **4511 passed, 12 skipped** — sabit sıra (`-p no:randomly`, 170.87s)
  ve **iki** rastgele tohum (`--randomly-seed=272`, 185.94s; `=273`, 204.21s). Üçüncü koşu
  bu dosyanın ve D-272/5'in son düzenlemelerinden **sonra** yapıldı; düzenlemeler takımı
  bozmadı. Eski taban 4510'du; fark tam olarak yeni mandaldır. Toplama çerçevesi:
  `4522 → koşu → 4522` (sapma yok).
- **Sıra artık ölçülebilir:** `pytest-randomly` 5.0.0 kurulu. Bundan sonra "rastgele sırada
  yeşil" iddiası **tohumla birlikte** yazılır, yoksa beyandır (D-260).
- **Ürün sahibi kararı bekliyor (taşıma YAPILMADI):** eşzamanlı ajan izolasyonu, D-272/7'deki
  üç seçenek. Önerim 1+2 (sıra düzeni + var olan kilidi zorlamak); ayrı worktree canlı
  veritabanını ayırmadığı için tek başına yetmez.
- **Açık 4 borç, öncelik ürün sahibinde:** `BORC-VKN-01` (kaynak yok, MERSIS A/B kararına
  bağlı), `BORC-NACE-DOGRULAMA-01`, `BORC-SICIL-DAIRE-01` (§5 saklı karar), `BORC-SCRIPTS-01`.
- **Araç tuzağı (bu turda üç kez):** `apply_diff` bu dosyada tutmadı; çok satırlı
  `python -c` cmd.exe'de **sessizce hiçbir şey yapmadı** — çıktı yok, çıkış kodu 0.
  Tek satır `-c` veya gerçek dosya kullan; "komut geçti" ekranı kanıt değil (D-260).
- **Bir sonraki turda ilk iş:** bu defteri oku, `AGENTS.md`'yi baştan tarama. Borcun son sözü
  **en yüksek D numarasında**dır, dosyadaki son satırda değil.

## Ilgili Nodlar

- [[AGENTS]]
- [[docs/HEDEF_VERI_KAPSAMI]]
