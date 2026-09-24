# API-ADMIN-CHURN-3SINYAL-16 — Brief (utku)

**Başlık:** [API] Churn kuralını 3 sinyale genişlet → churn.py tam formül (2s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/churn.py`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — kapanista "Kapanan isler" bolumune task_id satiri yazilir (B-14).

## Neden
SSOT §9 K1 (satır 340): PRD formülü `sinyal = Σ(1 for g in (g_giris, g_arama, g_ai) if g>=14)`. Şu an `risk_etiketi()` yalnız `last_login` ile çalışıyor → 🟡 kısmi, formülün 2/3'ü eksik. §10 sıra 5 (satır 368) bunu P1 açık tutuyor. `-14` ile arama/AI verisi akmaya başlayınca eksik kalan tek şey formül.

## Doğrulanacak varsayım
- `src/company_master/churn.py` içinde `risk_etiketi(son_giris, bugun)` fonksiyonu bu imzayla var varsayıldı. İmza farklıysa **dur**, panoya sorun aç, uydurma.
- `web_dashboard/tabs/musteri_yonetimi.py:272` bu fonksiyonun tek çağıranı varsayıldı. Satır kaymış veya başka çağıran varsa **önce çağıranları tara**, sonra yaz.
- Mevcut 14 günlük giriş yok eşiği kodda sabit varsayıldı; 3-sinyal sürümünde de aynı eşik korunacak. Kodda başka değer varsa **dur**, KAHİN'e sor.
- `risk_etiketi_3sinyal(...)` dönüşü `{0:"Yok",1:"Düşük",2:"Orta",3:"Yüksek"}` eşlemesi varsayıldı; UI bu 4 etiketi gösterecek. Başka etiket seti isteniyorsa **dur**.
- Üçüncü sinyalin veri kaynağı (`-13` aktivite logu) mevcut varsayıldı. Tablo yoksa sinyal sessizce 0 sayılmaz — **dur**, bağımlılığı bildir.
- Eski `risk_etiketi` çağrıları kırılmayacak (geriye dönük uyum) varsayıldı. Kırılması gerekiyorsa KAHİN onayı şart.

## Adımlar
1. Mevcut `risk_etiketi(son_giris, bugun)` saf fonksiyonunu **bozma** — geriye uyumlu kalsın (çağıran `musteri_yonetimi.py:272` var).
2. Yeni saf fonksiyon: `risk_etiketi_3sinyal(son_giris, son_arama, son_ai, bugun) -> str`, eşik 14 gün, çıktı `{0:"Yok", 1:"Düşük", 2:"Orta", 3:"Yüksek"}`.
3. `None` girdi = "o sinyalde hiç aktivite yok" = riskli sinyal say (14g'den eski gibi davran); bu kararı docstring'e yaz.
4. Doctest ile kenar durumları: 3 sinyal de taze, 3'ü de bayat, karışık, hepsi `None`.
5. `musteri_yonetimi.py` çağrısını yeni fonksiyona taşı — SQL'e `son_arama` / `son_ai` alt sorgularını `user_activity_log` üzerinden ekle.

## Kabul kriteri
- [ ] `risk_etiketi_3sinyal()` doctest'leri geçiyor (en az 5 senaryo, `None` dahil).
- [ ] Eski `risk_etiketi()` hâlâ çalışıyor, mevcut testler kırılmadı.
- [ ] Panelde risk kolonu 3 sinyalden besleniyor — kanıt `dosya:satır`.

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; ML kullanma — kural tabanlı kal (SSOT §9 İlke).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id API-ADMIN-CHURN-3SINYAL-16 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
