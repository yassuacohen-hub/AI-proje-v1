# Dosya Kilitleme Protokolü (DOCS-05)

> Kaynak: `src/company_master/orchestrator/task_board.py`
> Durum verisi: `data/orchestrator/file_locks.json`
> İlgili: [[GOREV_PANOSU_KULLANIM_KILAVUZU]] · V9 bağlam dokümanı

## 1. Amaç

Bu protokol, aynı çalışma alanında paralel çalışan birden fazla yapay zeka
ajanının (iç ajanlar + harici ajanlar) **aynı dosyayı aynı anda
değiştirmesini engeller**. Kilitler `file_locks.json` üzerinde tutulur;
kilit sahibi olmayan bir ajan, ilgili dosyayı içeren görevi açamaz.

2026-09-11 tarihinde yaşanan olay (P7-12 kilidinin bayat kalması ve test
kirliliğiyle görev panosunun gerilemesi) bu dokümanın yazılmasının ana
gerekçesidir.

## 2. Kilit Kayıt Şeması

`file_locks.json` yapısı:

```json
{
  "src/company_master/intelligence/job_intelligence/sources/kariyer_net.py": {
    "sahip": "kazi_scraper",
    "task_id": "P7-14",
    "kilitlendi": "2026-09-11T13:21:19"
  }
}
```

| Alan | Anlamı |
|------|--------|
| `sahip` | Kilidi tutan ajan kimliği (`kilo`, `mimar`, `kazi_scraper`...) |
| `task_id` | Kilidi açık eden görev kimliği |
| `kilitlendi` | ISO-8601 kilit zamanı (`timespec="seconds"`) |

## 3. API Referansı

Tüm fonksiyonlar `src/company_master/orchestrator/task_board.py` içindedir.

### `_lock_alan(sahip, dosya, task_id)`

- Dosya zaten **başka bir sahibe** kilitliyse `PermissionError` fırlatır:
  `"{dosya} zaten {sahip} tarafindan kilitli (gorev: {task_id})"`.
- Aynı sahip için tekrar çağrılırsa kilidi **yeniler** (zaman damgası
  güncellenir).
- `gorev_ekle(..., dosyalar=[...])` bu fonksiyonu **atomik** olarak
  çağırır: listedeki herhangi bir dosya kilitlenemezse görev **hiç
  eklenmez** ve panoda yarım kayıt oluşmaz.

### `lock_birak(dosya, sahip) -> bool`

- Kilidi yalnızca **sahibi** bırakabilir; sahip eşleşmezse `False` döner
  ve kilit silinmez.
- Görev `done` olduğunda bu çağrı zorunludur; aksi halde kilit bayatlar.

### `lock_durum(dosya) -> dict | None` ve `locklar() -> dict`

- Tek bir dosyanın ya da tüm kilit tablosunun anlık durumunu okur.

## 4. Standart İş Akışı

```python
from src.company_master.orchestrator import task_board as tb

# 1) Görev aç ve dosyaları kilitle (atomik)
tb.gorev_ekle(
    "ORNEK-01", "Örnek görev", "mimar",
    dosyalar=["src/company_master/etl/normalize.py"],
)

# 2) Çalış...

# 3) Bitince durumu güncelle ve kilidi bırak
tb.gorev_guncelle("ORNEK-01", durum="done", **{"not": "Tamamlandı"})
tb.lock_birak("src/company_master/etl/normalize.py", "mimar")
```

## 5. Çakışma Senaryosu

Ajan A `kariyer_net.py` üzerinde `P7-14` ile kilitliyken, ajan B aynı
dosyayı içeren bir görev açmaya kalkarsa:

```
PermissionError: src/.../kariyer_net.py zaten kazi_scraper tarafindan
kilitli (gorev: P7-14)
```

Bu durumda B **dosyaya dokunmaz**; görevi farklı kapsamla açar veya
kullanıcıyla koordine olur (bkz. kök `AGENTS.md` → Görev Panosu kuralları).

## 6. Bayat (Stale) Kilit Temizliği

Kilit sahibi görevi bitirmiş ama kilidi bırakmamışsa:

1. `tb.locklar()` ile tüm kilitleri listele.
2. Kilidin `task_id`'sinin panodaki durumunu kontrol et
   (`tb.gorev_getir(task_id)`). Görev `done` ise kilit **bayat**tır.
3. Kilidin kendi `sahip` değerini kullanarak `tb.lock_birak(...)` çağır.
4. İşlemi `CHANGELOG.md`'ye not et. (2026-09-11: P7-12/P7-13 kilidi bu
   yöntemle temizlendi; P7-14 kilidi aktif görev olduğu için korundu.)

**Yasak:** Başkasının kilidini `file_locks.json` üzerinde elle silmek.
Kilit her zaman API üzerinden, sahiplik kontrolüyle bırakılır.

## 7. Test İzolasyonu Uyarısı (Kritik)

`task_board.py` fonksiyonları **gerçek** `data/orchestrator/` dosyalarına
yazar. Testler bu nedenle yol referanslarını `tmp_path`'e izole etmelidir:

```python
@pytest.fixture(autouse=True)
def _isolated_board(tmp_path, monkeypatch):
    from src.company_master.orchestrator import task_board as tb_module
    state = tmp_path / "state"
    monkeypatch.setattr(tb_module, "STATE_DIR", state)
    monkeypatch.setattr(tb_module, "TASK_BOARD", state / "task_board.json")
    monkeypatch.setattr(tb_module, "FILE_LOCKS", state / "file_locks.json")
    monkeypatch.setattr(tb_module, "STATE_JSON", state / "state.json")
    monkeypatch.setattr(tb_module, "TASK_MD", state / "gorev_panosu.md")
```

2026-09-11 olayı: `test_task_board.py` ve `test_quick_task.py` içindeki
`TASK_BOARD.write_text("[]")` çağrıları **gerçek panoyu boşaltmıştı**;
pano eski bir anlık görüntüye geriledi. Bu yüzden her iki test dosyasına
otomatik izolasyon fixture'ı eklendi (ORCH-01) ve `if __name__ == "__main__"`
blokları (fixture'ı atladıkları için) devre dışı bırakıldı.

## 8. İlgili Dosyalar

| Dosya | Rol |
|-------|-----|
| `src/company_master/orchestrator/task_board.py` | Kilit + pano API'si |
| `data/orchestrator/file_locks.json` | Kilit durumu (SSOT) |
| `data/orchestrator/task_board.json` | Görev panosu (SSOT) |
| `tests/orchestrator/test_task_board.py` | İzole edilmiş pano testleri |
| `AGENTS.md` (kök) | Çoklu ajan koordinasyon kuralları |
