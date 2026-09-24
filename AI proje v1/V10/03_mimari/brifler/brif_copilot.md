# Brif: Copilot — 2026-09-13

## 1. Okuduğum Kararlar
- `02_muninn_super_admin_panel_prd_ve_yol_haritasi.md`: Streamlit sekmeleri, FastAPI admin endpointleri ve fazlı geçiş planı.
- `06_muninn_prd_vs_huginn_analiz.md`: mevcut modül durumu, MVP sonrası roadmap ve teknik borçlar.
- `ADMIN-01-02-03_TASK_BRIEF.md`: admin sekmelerinde ortak UI ve dokümantasyon beklentileri.
- `brifler/brif_roo.md`: operasyon merkezi yaklaşımı, sekme hiyerarşisi ve audit önerileri.

## 2. Öneriler
- Sekme taşıma işlemini tek seferlik büyük refactor yerine dikey dilimler halinde yapın: önce bir sekme, veri sözleşmesi, test ve geri dönüş kontrolü.
- Ortak `tab_context`/render yardımcıları ile başlık, yenileme, boş veri, hata ve son güncelleme davranışlarını standartlaştırın.
- 17+ sekme için sidebar/kategorili navigasyona geçiş eşiğini şimdiden belirleyin; mevcut `st.tabs` yapısını her fazda daha da büyütmeyin.
- Admin endpointleri için ortak cevap zarfı (`status`, `data`, `meta`, `limitations`) kullanın; frontend fallback mantığını azaltın.
- Test stratejisi: loader unit testleri, render contract testleri ve kritik kullanıcı akışları için Playwright smoke testleri birlikte yürüsün.

## 3. Kritikler
- Sekme taşınırken API endpointi, cache TTL'si ve boş veri davranışı birlikte taşınmazsa sessiz veri kaybı veya yanıltıcı dashboard oluşabilir.
- `decision_log.jsonl` yalnızca JSONL dosyası olarak kaldığında çoklu süreç yazımı, arama ve retention güvenilirliği sınırlı kalır.
- Her admin aksiyonunun audit kaydı olmadan güvenlik ve operasyon incelemesi eksik kalır.
- Streamlit mock testleri gerçek layout ve tarayıcı davranışını doğrulamaz; en azından kritik sekmeler için e2e smoke gerekir.

## 4. Eklemeler
- Her sekme için küçük bir kabul sözleşmesi ekleyin: veri kaynağı, beklenen alanlar, empty/error state ve maksimum yükleme süresi.
- CI'da Python testleri yanında `node --check web_dashboard/js/app.js` ve temel frontend smoke testi çalıştırın.
- Task board teslim notlarında test komutu, sonuç, bilinen görev dışı hata ve değişen dosyalar zorunlu alan olsun.
- `AGENT_SYNC.md` üretimini canlı task board ile atomik tutarlılık kontrolüne bağlayın.

## 5. Riskler + Kota Notu
- Kota/kapasite açısından devretme gerektiren bir durum yok.
- En büyük kısa vadeli riskler: navigasyon bloat, dağınık API cevap şemaları ve testlerin yalnızca mock katmanında kalması.
- Öncelik: mevcut MVP sekmelerini stabilize etmek; tenant/faturalama gibi Faz 3 kapsamını erken başlatmamak.

## 6. Yol Haritası Katkısı
- Her faz başlangıcında sekme envanteri, API sözleşmesi ve test matrisi birlikte güncellensin.
- 20 sekmeye yaklaşmadan önce sidebar/kategorili navigasyon için spike ve ölçülebilir UX kabul kriteri açılsın.
- Audit trail PostgreSQL'e taşınana kadar JSONL yazımı atomik/tek-yazar ilkesiyle sınırlandırılsın ve düzenli arşivlensin.
- Yeni sekme tamamlanmış sayılmadan unit, render contract ve kritik akış smoke testleri yeşil olmalı.
