[[Huginn Data Insights/data/orchestrator/AGN-STACK-01_bulgu_2026-09-18_cline.md]]

# AGN-STACK-01 — crewAI + langchain-openai kurulum ve kıyaslama görevi (cline, 2026-09-18)

**Sahip emri:** "pip install crewai langchain-openai; buna bakıp kendisi araştırsın — bu sistemi geliştirmek için bir yöntem geliştirilmiş; ikisini kıyasla ve çözüm önerileriyle tetik mektubu gönder, raporlu."

## 1. Kurulum (cline, tamamlanmış — roo tekrar kurmayacak)
```
python -m pip install crewai langchain-openai
→ crewai 1.15.22 / langchain_openai 1.6.2 kuruldu
→ bilinen çakışma: opentelemetry-instrumentation 0.60b0 vs opentelemetry-semantic-conventions 0.65b0
  (crewai'nin kendi otel zinciri; proje testlerinde etki gözlenmedi)

python -c "import web_app, crewai, langchain_openai" → birlikte import OK
python -m pytest tests/test_auth_gate.py tests/test_admin_auth_login.py -q → 18 passed
python -X utf8 scripts/kodlama_denetim.py → temiz
```
**Kural notu:** `requirements.txt`'ye EKLENMEDİ (S-04 örüntüsü) — kalıcı bağımlılık kararı roo/sahip'te; pilot kararına kadar venv-bazlı kalır.

## 2. Roo'ya tetik mektubu (gönderildi — `AGN-STACK-01`)
**Görev:** crewAI + langchain-openai ile mevcut Huginn orkestrasyon sisteminin kıyası ve çözüm önerileri (raporlu).
Kapsam:
1. **Araştır (kendin):** crewAI v1 mimarisi — Agent/Task/Crew, `process` türleri (sequential/hierarchical), tools, memory, LLM başına model+fallback; langchain-openai'in rolü (provider katmanı). D-48 çerçevesinde değerlendir.
2. **Kıyas:** mevcut Huginn orkestratörü (roo/kilo/cline + task_board.json + posta/tetik + onay kuyruğu + kodlama_denetim + pytest süiti + ALARM/nöbetçi) ↔ crewAI. Tablo: görev dağıtımı, denetim/onay, kalıcılık, gözlemlenebilirlik, maliyet, öğrenme eğrisi, hata kurtarma.
3. **Ponytail/YAGNI çerçevesi (RESEARCH-PONYTALE ile bağla):** crewAI eklemek gerçek bir boşluğu dolduruyor mu, yoksa YAGNI mi? Karşı argümanları da yaz.
4. **Çözüm önerileri:** en az 3 senaryo — (a) entegrasyon YOK (mevcut sistem + hedeflenen iyileştirmeler), (b) hibrit: crewAI'ı yalnız alt-görev/araç-çağrı worker'ı olarak (insan-onaylı kapı koruması korunur), (c) tam geçiş (önerilmemesi bekleniyor; gerekçeler). Her senaryo için maliyet/token etkisi (TAKIP.md model zinciriyle: ücretsiz OR/Groq + OR ücretli + Sonnet) ve riskler.
5. **Pilot önerisi:** seçilen senaryo için küçük, geri döndürülebilir pilot (kapsam + kabul kriterleri + geri alma adımı).
6. **Rapor:** `data/orchestrator/AGN-STACK-01_rapor_roo.md` (yapılanlar, kıyas tablosu, öneri, pilot planı, test sayısı) + kapsam dışı bulgu varsa `_bulgular_`.
7. **Kısıtlar:** requirements değişikliği YOK · 9Router + docs/brand dokunma · commit YOK · UI dosyası değişirse streamlit_restart zorunlu · kurulum cline tarafından yapıldı (tekrar kurma).
