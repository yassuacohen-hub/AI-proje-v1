# DOC-ADMIN-DURUM-SENKRON-15 — Brief (utku)

**Başlık:** [DOC] Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı (1s)
> ⏳ belirsiz — KAHİN onayı: Başlık panoyla eşitlendi (D-77: pano kaynaktır). Bu brief'in
> gövdesi işin kapsamını D-197 tek-durum **ayrıştırması** olarak genişletiyor; pano başlığı
> yalnız "bayat satır düzeltme" diyor. Kapsamın hangisi olduğu KAHİN kararıdır.
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196) · **Kural:** AGENTS.md D-197
**Kilitli dosya:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — kapanista "Kapanan isler" bolumune task_id satiri yazilir (B-14).

## Neden
SSOT kendi kendisiyle çelişiyor: §14 satır 473-474'te EK BULGU-9 ve EK BULGU-10 **giderildi** yazıyor, ama §8.4 satır 323-324 hâlâ "**P0**", §10 satır 364 hâlâ "P0 · Kritik" gösteriyor; §10 satır 366/368 "girdisiz" diyor ama `users.last_login` v0016 ile eklendi.

**Kök neden bu satırların bayatlaması değil — aynı bilginin beş bölümde çoğaltılmış olması.** Tek tek eşitlemek semptomu siler, kaynağı bırakır: bir sonraki görevde tekrar ayrışır. Bu görev **yapıyı** değiştirir (D-197): durum ve öncelik tek noktada, §7'de tutulur; diğer bölümler yalnız tanım ve gerekçe yazar. Ayrıştırma bittiğinde "senkron" diye bir iş kalmaz — senkronlanacak ikinci kopya yoktur.

## Doğrulanacak varsayım
- SSOT dosyası `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` tek doğruluk kaynağı ve başka kopyası yok varsayıldı. İkinci kopya bulursan **dur**, panoya sorun aç.
- Brief'teki satır numaraları (§14:473-474, §8.4:323-324, §10:364/366/368/369, §12:415/417, §2:326-328) yazıldığı andaki hâliyle geçerli varsayıldı. Dosya o günden beri değiştiyse satırlar kaymıştır: **önce başlıkla (§ numarası) bul**, satır numarasına körlemesine yazma.
- §7 İzlenebilirlik Matrisi tablo biçiminde ve her açık madde için bir satır taşıyabilir varsayıldı. Satır eksikse §8/§9/§10/§12'deki **mevcut** maddeden taşınır; yoktan madde **uydurulmaz**.
- Durum etiketi sözlüğü `✅` / `⬜` / `devam`, öncelik kümesi `P0`/`P1`/`P2` varsayıldı. Başka etiket çıkarsa **dur**, KAHİN'e sor.
- §8/§9/§10/§11/§12'deki her maddenin §7'de bir karşılığı **vardır veya açılabilir** varsayıldı. Karşılığı olmayan madde çıkarsa etiketi silme — **dur**, listeyi panoya bildir.
- Durum etiketi silinince bölümün anlamı bozulmuyor varsayıldı (tanım metni kendi başına ayakta). Bozuluyorsa **dur**, o satırı raporla.

## Adımlar
1. **§7'yi tek durum kaynağı yap.** §8/§9/§10/§11/§12'de geçip §7'de satırı olmayan her maddeyi §7'ye taşı: madde kimliği, durum (`✅`/`⬜`/`devam`), öncelik (`P0`/`P1`/`P2`), kanıt (`dosya:satır` veya TASK-ID). Taşıma sırasında §14'teki "giderildi" kayıtlarını kanıt olarak kullan; kanıtsız hiçbir satır `✅` olmaz.
2. **§8 / §9 / §10 / §11 / §12'den durum ve öncelik etiketlerini kaldır.** Silinecek: `✅` / `⬜` / `devam` işaretleri, `P0`/`P1`/`P2` etiketleri, "Kritik"/"bitti"/"açık" gibi durum sıfatları, tamamlanma yüzdeleri. **Kalacak:** ne yapılacağı, neden gerektiği, teknik tanım. Satır silme yok — yalnız etiket kaldırma (D-186).
3. **Bayat gerçek ifadelerini düzelt** (durum değil, olgu): §10 sıra 3 ve sıra 5'teki "girdisiz" ifadesi yanlış — `users.last_login` v0016 ile eklendi; kalan gerçek eksik arama/AI logu (`VERI-ADMIN-AKTIVITE-LOG-13`). §10 sıra 6 (A9): MAU var, eksik olan gerçek DAU (`UI-ADMIN-DAU-17`). Bu cümleler tanım metnidir, kalır — sadece doğrulanır.
4. **§14'ü saf değişiklik günlüğüne indir.** Her satır "tarih · kim · neyi değiştirdi" olur. Toplam/kalan/yüzde/ilerleme özeti taşıyan satırlar §14'ten çıkar; karşılığı §7'de zaten vardır.
5. **§2 kapsama oranı satırlarını (326-328)** yüzde değil ham sayaç biçimine çevir: `Açık görev — P0: n · P1: n · P2: n (kaynak: §7 matrisi)`. Sayılar §7'den **sayılır**, tahmin edilmez.
6. **Çelişki kuralını dosyaya yaz.** §7 başlığının hemen altına tek satır: "Durum ve öncelik yalnız bu tabloda tutulur; başka bölümle çelişirse bu tablo doğrudur (AGENTS.md D-197)."

## Kabul kriteri
- [ ] **§7 dışında hiçbir bölümde durum/öncelik etiketi kalmadı.** Doğrulama: dosyada `✅`, `⬜`, `P0`, `P1`, `P2` geçen tüm satırlar listelenir; §7 ve §14 dışı sonuç **sıfır** olmalı. Sonuç rapora yapıştırılır.
- [ ] §7 matrisi §8/§9/§10/§11/§12'deki her maddeyi kapsıyor — kapsanmayan madde yok (liste ile kanıtlanır).
- [ ] Hiçbir satır kanıtsız `✅` işaretlenmedi (`dosya:satır` veya TASK-ID zorunlu).
- [ ] §14'te toplam/kalan/yüzde satırı kalmadı; yalnız değişiklik kayıtları var.
- [ ] §2'de yüzde ifadesi kalmadı; yerinde P0/P1/P2 sayacı var ve sayılar §7 ile birebir tutuyor.
- [ ] Hiçbir bölüm/madde silinmedi; yalnız etiketler taşındı (D-186). Satır sayısı düşüşü yalnız etiket kaldırmayla açıklanabilir olmalı.

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi yalnız SSOT §7 (İzlenebilirlik Matrisi) satırına işle; §14'e değişiklik kaydı düş (D-197). Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id DOC-ADMIN-DURUM-SENKRON-15 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
