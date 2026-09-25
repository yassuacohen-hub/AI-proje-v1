# ADMIN-UX-GELIR-GRUP-01 — Gelir & Paketler Grubu UX Tasarımı

**Ajan:** Utku  
**Aciliyet:** P2  
**Süre:** 2 saat  
**Tür:** UI/UX (Admin Panel menü reorganizasyonu)  
**Kilitli dosya:** `web_dashboard/tabs/__init__.py`, `web_dashboard/tabs/admin_executive.py`, `web_dashboard/tabs/admin_cost.py`  
**Bağımlılık:** Yok  
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

## Neden
Admin panel sidebar menüsünde "executive" ve "maliyet" sekmeleri ayrı gruplarda. UX tasarımına göre bu ikisi "Gelir" (Gelir & Paketler) grubu altında toplanmalı. Kullanıcı bazlı menü yapısı için: kullanıcı gelir kaynaklarını ve paket maliyetlerini aynı grupta görmeli.

## Doğrulanacak Varsayım
- `web_dashboard/tabs/__init__.py` içinde `BOLUMLER` tuple'ında `executive` ve `maliyet` sekmeleri farklı gruplarda (`grup=GRUP_IS` vs `grup=GRUP_SISTEM` gibi)
- Yeni grup: `grup="gelir"` (yeni grup sabiti eklenecek)
- `executive` ve `maliyet` sekmelerinin `grup="gelir"` ve `ust="gelir"` olmalı
- Sidebar menüde "Gelir" grubu açılır menü olarak görünmeli

## Adımlar
1. `web_dashboard/tabs/__init__.py` dosyasında yeni grup sabiti `GRUP_GELIR = "gelir"` ekle
2. `BOLUMLER` tuple'ında `executive` ve `maliyet` sekmelerini güncelle:
   - `grup=GRUP_GELIR`
   - `ust="gelir"` (sidebar grup başlığı)
   - `sira` değerlerini 1, 2 yap (grupun içindeki sıralama)
3. Yeni grup sabiti `GRUP_GELIR` için sidebar menü render desteği kontrol et (varsa ekle)
4. Test: `python -m pytest tests/test_admin_panel_tab.py -v`

## Kabul Kriteri
- [ ] `GRUP_GELIR` sabiti eklendi
- [ ] `executive` sekmesi `grup=GRUP_GELIR, ust="gelir", sira=1`
- [ ] `maliyet` sekmesi `grup=GRUP_GELIR, ust="gelir", sira=2`
- [ ] Sidebar menüde "Gelir" grubu görünüyor
- [ ] `python -m pytest tests/test_admin_panel_tab.py -v` geçiyor

## Kurallar
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id ADMIN-UX-GELIR-GRUP-01 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/web_dashboard/tabs/__init__.py]]