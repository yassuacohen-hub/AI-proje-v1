# Görev Panosu Kullanım Kılavuzu (DOCS-06)

> Kaynak: `src/company_master/orchestrator/task_board.py`
> Durum verisi: `data/orchestrator/task_board.json`
> İlgili: [[DOSYA_KILITLEME_PROTOKOLU]] · [[CHANGELOG]]

## 1. Amaç ve Kaynak Hiyerarşisi

Görev panosu, tüm ajanların (iç + harici) görevlerini tek yerden izleyen
merkezi sistemdir. Veri akışı:

```
data/orchestrator/task_board.json   (SSOT — ham veri)
        │  gorev_ekle / gorev_guncelle (otomatik)
        ▼
data/orchestrator/gorev_panosu.md   (Obsidian görünümü)
        │  agent_sync_yaz() (otomatik)
        ▼
AGENT_SYNC.md                       (kök senkron özeti)
```

`AI proje v1/V10/TODO.md`, insan tarafından okunan görev listesidir ve
panoyla tutarlı tutulur; **çakışma durumunda panonun JSON'u esastır.**
`AGENT_SYNC.md` otomatik üretilir; **elle büyük yeniden yazım yapılmaz.**

## 2. task_board.json Alan Şeması

| Alan | Tip | Açıklama |
|------|-----|----------|
| `task_id` | str | Benzersiz görev kimliği (örn. `P7-14`, `DOCS-05`) |
| `baslik` | str | Görev başlığı |
| `sahip` | str | Sorumlu ajan kimliği |
| `oncelik` | str | `P0` (kritik) … `P3` (düşük) |
| `durum` | str | `plan` / `aktif` / `review` / `done` / `blocked` |
| `baslangic` / `bitis` | str\|null | ISO-8601 zaman damgaları |
| `dosyalar` | list | Kilitle edilen dosya yolları |
| `not` | str | Serbest not alanı |
| `source` | str | `ic` (iç ajan) veya `harici` (harici ajan) |
| `from_agent` | str\|null | Görevi atayan ajan (harici görevlerde) |
| `attempts` | int | Retry sayacı (opsiyonel) |

## 3. Durum Yaşam Döngüsü

```
plan ──gorev_guncelle(durum="aktif")──► aktif ──► review ──► done
  ▲                                     │
  └────────────── blocked ◄─────────────┘
```

- `plan`: kuyrukta, henüz başlamadı.
- `aktif`: sahip ajan çalışıyor.
- `review`: çıktı üretildi, incelemede.
- `done`: tamamlandı; `bitis` dolu, dosya kilitleri bırakıldı.
- `blocked`: engel var; engel açıklaması `not` alanına yazılır.

## 4. API Kullanımı

### gorev_ekle

```python
from src.company_master.orchestrator import task_board as tb

tb.gorev_ekle("ORNEK-01", "Örnek görev", "mimar",
              oncelik="P1", dosyalar=[...],
              source="harici", from_agent="mimar")
```

- Aynı `task_id` tekrar eklenirse `ValueError: Gorev zaten var: ...`
  fırlatır (S-02/S-07 duplika koruması).
- `dosyalar` verildiyse kilitler **atomik** alınır
  (bkz. [[DOSYA_KILITLEME_PROTOKOLU]]).

### gorev_guncelle — `not` anahtar kelimesi tuzağı

`not` Python'da anahtar kelime olduğundan `gorev_guncelle(..., not=...)`
**sözdizimi hatasıdır**. Doğru kullanım:

```python
tb.gorev_guncelle("ORNEK-01", durum="done",
                  **{"not": "Tamamlandı"})
```

Bu davranış `test_gorev_guncelle_not_keyword_argument` testiyle garanti
altındadır (REFACTOR-01).

### Diğer Fonksiyonlar

| Fonksiyon | Amaç |
|-----------|------|
| `gorev_getir(task_id)` | Tek görevi sözlük olarak döner (yoksa `None`) |
| `gorev_listesi(durum=None)` | Tüm görevler; `durum` filtresi opsiyonel |
| `retry_istatistikleri(task_id)` | Retry/backoff ve context decay özeti |
| `handoff_ekle(task_id, agent_id, output_path, summary)` | Çıktı kaydı; aynı `task_id` tekrar gelirse `guncelleme_gecmisi` listesine ekler (duplicate-safe) |
| `handoff_tum()` | Tüm handoff kayıtları |

## 5. Görünüm Dosyalarını Yenileme

- `gorev_ekle`/`gorev_guncelle` çağrıları `_md_yaz()` üzerinden
  `gorev_panosu.md`'yi otomatik günceller. Markdown yazıcısı `gorulen_ids`
  setiyle duplika satırları atlar (S-07).
- `AGENT_SYNC.md` için: `tb.agent_sync_yaz()` — panodan tam yeniden üretim.
  Dosya "Otomatik Olusturuldu" stiliyle başlıyorsa tamamen yeniden yazılır;
  manuel içerik varsa otomatik bölüm sona eklenir.
- `data/orchestrator/AGENT_SYNC.md` kopyası kök dosyayla eş tutulur.

## 6. quick_task.py — Hızlı Harici Görev

```powershell
python scripts/quick_task.py --from-agent mimar --agent claude_code `
    --task ORNEK-99 --title "Araştırma" --task-type research `
    --run-mode orchestrator --review
```

Sıra: `brief_olustur` (workspace/external/<agent>/brief_<id>.md) →
`dispatch` (panoya kayıt + çalıştırma) → `--review` verilirse `review`
(PASS → done + handoff + AGENT_SYNC; FAIL → blocked).

Uçtan uca doğrulama: `tests/orchestrator/test_quick_task.py`
(VALIDATE-01).

## 7. Orkestratör CLI

```powershell
python -m src.company_master.orchestrator.cli dispatch <brief.json> `
    [--run-mode orchestrator|agent]
python -m src.company_master.orchestrator.cli review <task_id>
python -m src.company_master.orchestrator.cli status
python -m src.company_master.orchestrator.cli errors [--agent ...] [--task ...]
python -m src.company_master.orchestrator.cli sync
```

- Bilinen harici ajanlar: `cursor_grok`, `copilot`, `claude_code`,
  `roo_code`, `harici_ajan`.
- `orchestrator` modu görevi dahili çalıştırır (harici subprocess yok).

## 8. Test Kuralları

- Panoya yazan her test `tmp_path` + `monkeypatch` ile izole olmalı
  (bkz. [[DOSYA_KILITLEME_PROTOKOLU]] §7).
- Çalıştırma: `python -m pytest tests/orchestrator/ -q` — `pytest.ini`
  (`pythonpath = src`) sayesinde ek ortam değişkeni gerekmez.

## 9. Güncelleme Sorumlulukları

| Olay | Güncellenecek |
|------|---------------|
| Görev açıldı | `gorev_ekle` (pano otomatik) + `TODO.md` satırı |
| Görev bitti | `gorev_guncelle(durum="done")` + kilit bırakma + `TODO.md` + `CHANGELOG.md` |
| Karar değişti | `project_state.md` + gerekirse V9 bağlam dokümanı |
| Test eklendi | `CHANGELOG.md` test sayısı notu |

## 10. Proje Sağlık Simülasyonu — `simulasyon` (D-198, zorunlu kapı)

### 10.1 Ne / Neden / Ne Zaman

| Soru | Cevap |
|------|-------|
| **Ne?** | Projenin kalıcı sağlık aracı. Pano, arşiv, brief'ler ve SSOT'u 8 kontrolden geçirir. |
| **Neden var?** | 2026-09-24 süreç denetimi: aynı iş iki kez üretildi, brifsiz görev atandı, SSOT'ta çelişkili durum kaldı. Hepsi ancak iş bittikten sonra fark edildi. |
| **Ne çözüyor?** | Bu hataları **tur başlamadan önce** yakalar; sorun üretime değil ekrana düşer. |
| **Ne zaman?** | Her üretim ve her planlama turundan önce. Çıkış kodu 0 değilken tur başlamaz (D-198). |
| **Riski var mı?** | Yok. Salt okunur: hiçbir dosyaya yazmaz. İstediğin kadar çalıştırabilirsin. |
| **Ne kadar sürer?** | Birkaç saniye; tamamı yerel dosya okuması, ağ/DB erişimi yok. |

### 10.2 Kullanım

| Komut | Ne zaman kullanılır |
|-------|---------------------|
| `set PYTHONIOENCODING=utf-8 && python scripts/gorev_kutusu.py simulasyon` | Normal tur öncesi. Bulguların ilk 5 örneğini `dosya:satır` olarak gösterir. |
| `set PYTHONIOENCODING=utf-8 && python scripts/gorev_kutusu.py simulasyon --kuru` | Hızlı bakış / CI. Yalnız sayı + çıkış kodu; örnek satır basmaz. |

`set PYTHONIOENCODING=utf-8` Windows cp1254 konsolu içindir (D-86).

### 10.3 Çıkış kodu = kararın kendisi

| Kod | Anlam | Ne yapılır |
|-----|-------|------------|
| `0` | Temiz | Tur başlayabilir. |
| `1` | Uyarı var | İş durmaz (D-65), ama uyarılar tur planına girer. Orkestratör bilerek devam eder. |
| `2` | Hata var | Tur **başlamaz**. Önce hata kapatılır, simülasyon yeniden çalıştırılır. |

### 10.4 Sekiz kontrol — hangi risk, hangi çözüm

| # | Kontrol | Yakaladığı risk | Bulgu çıkarsa çözüm | Seviye | Bulgu |
|---|---------|-----------------|---------------------|--------|-------|
| 1 | Pano ↔ arşiv `task_id` çakışması | Kapanmış iş panoya ikinci kez girer, aynı iş iki kez üretilir | Panodaki kaydı sil veya yeni `task_id` ver | HATA | B-01 |
| 2 | Pano `brief` yolu diskte var mı | Ajan brifsiz iş alır, kapsamı kendi uydurur (D-66 ihlali) | Brifi yaz veya panodaki yolu düzelt | HATA | B-03 |
| 3 | Açık görevde `dosyalar` (kilit) boş mu | İki ajan aynı dosyaya yazar, biri diğerini ezer | Brifteki kilitli dosyayı panoya taşı | UYARI | B-04 |
| 4 | `dependencies` kaydı var mı / kapandı mı | Önkoşulu bitmemiş iş başlatılır, yarıda takılır | Sırayı düzelt veya bilerek devam et (D-65) | UYARI | B-12 |
| 5 | SSOT'ta yüzde satırı (§14 hariç) | "%60 tamam" satırı bayatlar, yanlış karar verdirir | Yüzdeyi sil; ilerleme yalnız §7'de sayıyla durur (D-197 k.5) | UYARI | B-07 |
| 6 | SSOT §8-§12'de durum/öncelik etiketi | Aynı işin durumu iki yerde farklı yazar | Etiketi §7'ye taşı, bölümde yalnız içerik kalsın (D-197 k.1-2) | UYARI | B-09 |
| 7 | Brief `_brief_sablon.md` başlıklarına uyuyor mu | Kabul kriteri yazmayan brif, "bitti mi?" tartışması doğurur | Eksik başlığı brife ekle | UYARI | B-17 |
| 8 | Kapanan görev SSOT/hub'da iz bırakmış mı | İş biter, belge güncellenmez; bilgi ajanın kafasında kalır | Kapanışı SSOT veya ilgili hub'a bir satır olarak yaz | UYARI | B-14 |

### 10.5 Okuma kuralları

| Çıktı | Anlamı |
|-------|--------|
| `OK` | Kontrol çalıştı, bulgu yok |
| `UYARI n adet` / `HATA n adet` | Bulgu sayısı + ilk 5 örnek `dosya:satır` |
| `ATLANDI: gerekçe` | Kontrol o an uygulanamadı (ör. SSOT diskte yok). **Uydurma `OK` yazılmaz** — kanıtsız iddia yasak. |

### 10.6 Neden ayrı bir denetim betiği değil

| Seçenek | Sonuç | Karar |
|---------|-------|-------|
| Ayrı `ssot_durum_denetim.py` | Bugün bir dosya, altı ay sonra `data/_tmp/` mezarlığı. B-15 bunun kanıtı: 5 artık betik birikmişti. | Reddedildi |
| `gorev_kutusu.py` içinde alt komut | Kontroller zaten panoyu ve arşivi okuyan modülün yanında; tek giriş noktası, tek bakım yeri | **Seçildi** |
| Git hook / CI zorunluluğu | Yerel geliştirmede sessizce atlanır, ajan turunu kapsamaz | İleride eklenebilir, önce komut yerleşsin |

---

## 11. Klon Sonrası İlk Beş Komut (taşınma hazırlığı, TUR-B2 2026-09-24)

Sunucu değişince ya da yeni makinede sıfırdan başlarken **sırayla** bu beş komut koşulur.
Amaç: "depo indi ama ajan neyi okuyacağını bilmiyor" durumunu ortadan kaldırmak.
Komutlar Windows `cmd.exe` içindir (D-86: her Python çağrısında `PYTHONIOENCODING=utf-8`).

| # | Ne | Komut |
|---|----|-------|
| 1 | Depoyu klonla ve dala geç | `git clone <repo-url> "Huginn Data Insights" && cd "Huginn Data Insights" && git checkout chore/monorepo-merge` |
| 2 | Sanal ortam + bağımlılıklar | `python -m venv .venv && .venv\Scripts\activate && pip install -r requirements-app.txt -r requirements-dev.txt` |
| 3 | Sağlık kapısı (D-198) | `set PYTHONIOENCODING=utf-8 && python scripts\gorev_kutusu.py simulasyon --kuru` |
| 4 | Sıradaki işi gör | `set PYTHONIOENCODING=utf-8 && python scripts\gorev_kutusu.py bak --ajan <ajan_adi>` |
| 5 | Kuralları oku (D-168) | `type AGENTS.md` — oturum başında zorunlu; hub-önce okuma için [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] |

**3. adımın çıkış kodu kararın kendisidir** (bkz. §10.3): `0` temiz, `1` uyarı — tur başlar,
`2` hata — tur **başlamaz**, önce bulgu kapatılır. Klon sonrası `2` görülürse sorun taşınmada
değil panodadır; `git log` ile son commit'e bakılır.

`.env` klonla gelmez ve gelmemelidir (Adım 2 güvenlik kapısı). 2. adımdan sonra:
`copy .env.example .env` ardından anahtarlar kasadan elle doldurulur.

### 11.1 Docker ile ayağa kaldırma

Taşınma Docker ile yapılacak. Servisler [[docker-compose]] içinde tanımlı; profilsiz servisler
varsayılan olarak kalkar, profilli olanlar açıkça istenir.

| Amaç | Komut | Adres |
|------|-------|-------|
| Önce `.env` | `copy .env.example .env` + anahtarları doldur | — |
| API (FastAPI/uvicorn) | `docker compose up -d --build api` | http://localhost:8000 |
| Streamlit arayüzü | `docker compose up -d --build streamlit` | http://localhost:8501 |
| Yerel PostgreSQL (dev/test) | `docker compose --profile localdb up -d db` | `localhost:5433` → kapsayıcıda 5432 |
| Tek seferlik sağlık işi | `docker compose --profile jobs run --rm healthcheck` | stdout |
| Günlükler / durdurma | `docker compose logs -f` · `docker compose down` | — |

Yerel PG kullanılacaksa `DATABASE_URL` **5433**'e çevrilir; aksi halde `.env`'deki Supabase
bağlantısı geçerlidir. Docker yolu tercih edilse bile **3. adımdaki `simulasyon` kapısı atlanmaz** —
kapsayıcı ayakta olması panonun sağlıklı olduğu anlamına gelmez.

`Makefile` yardımcı kısayollar sunar (`make install`, `make test`, `make docker-up`) ancak
`make clean` ve bazı hedefler Unix araçları (`find`, `rm`) varsayar ve `docker-compose` (tireli,
eski) sözdizimi kullanır. Windows'ta yukarıdaki doğrudan komutlar esastır.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[scripts/gorev_kutusu]]
- [[tests/test_gorev_kutusu_simulasyon]]
- [[tests/test_gorev_kutusu_hafiza]]
- [[docker-compose]]
- [[Dockerfile]]
