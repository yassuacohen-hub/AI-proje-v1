# system_prompt.md

Evrensel Ajan Kuralları

## 1. İlk Adım (HER SOHBETİN BAŞINDA)
- Posta kutusunu kontrol et: `python scripts/gorev_kutusu.py bak --ajan <AJAN>`
- Bekleyen görevi al: `python scripts/gorev_kutusu.py al --ajan <AJAN> --task-id <ID>`
- Brif dosyasını oku ve işi yap
- Teslim et: `python scripts/gorev_kutusu.py teslim --ajan <AJAN> --task-id <ID> --ozet "..."

## 2. İletişim ve Akıl Yürütme
- Tüm iletişim ve thinking %100 TÜRKÇE
- Düşünce adımları kısa maddeler halinde
- Kodlar ve API'ler İngilizce olabilir; kullanıcı açıklaması Türkçe

## 3. Token Optimizasyonu
- Dev dosyaları parçalı oku
- Brifleri öz tut
- Tekrarlayan döngüleri durdur

## 4. Marka Terminolojisi
- Huginn = Müşteri, Muninn = Admin, Odin = Backend Orchestrator

## 5. Ortak Skill Havuzu Yönetimi
- `.agents/skills/` herkesin ortak kaynağı
- Fetch değil, kopya: yetenek ortak havuzdaysa referans al, kopya yapma
- Metin ağırlıklı SKILL.md, resim değil
- Görev odaklı değil, yetenek odaklı
- Skill Bekçi mevcut: havuzu denetler, çakışma tespit eder

## 6. FastAPI Backend Kuralları
- async def zorunlu (sync kod yok)
- routers/services/repositories/schemas katmanları
- response_model ile data hiding
- PostgreSQL: AsyncSession + eager loading (selectinload/joinedload)
- MongoDB: BSON ObjectId safe parsing, Motor
- passlib[bcrypt] + Depends(get_current_user)

## 7. Genel Kod Kalitesi
- PEP 8, tip açıklamaları
- Her özellik için birim test
- Hardcoded secret yok
- Test edilmemiş iş teslim edilmez

## 8. Test
- `python -X utf8 -m pytest tests/ -q`
- 1413 test passed hedefi


## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
