# agenticSeek Araç Analizi — Kurumsal Web Kazıması Uygunluğu

**agenticSeek**, yerel alternatif olarak kurumsal web kazıması sistemlerine dahil edilmelidir. Scrapling (84K ⭐) ile karşılaştırıldığında, agenticSeek daha güçlü ajan yeteneği sunar ama GPL-3.0 lisansı ticari kontrol gerektirir.

## Proje Özellikleri

| Metrik | agenticSeek | Scrapling | Notlar |
|--------|-------------|-----------|--------|
| GitHub Yıldız | 27K | 84K | agenticSeek daha yeni, Scrapling daha yaygın |
| Lisans | GPL-3.0 | MIT | agenticSeek: ticari kullanım izin gerektiriyor |
| Web Browsing | SearXNG + Selenium | BeautifulSoup + Playwright | agenticSeek: tam otonom tarayıcı |
| Kodlama Yeteneği | Sandbox Python | Kod çıktısı değil | agenticSeek: yazılan kod çalıştırabilir |
| Voice Support | Evet (Piper TTS) | Hayır | agenticSeek: sesli komut/çıktı |
| Local Deployment | Docker + Ollama/LM Studio | Python + API call | agenticSeek: tamamen offline |
| Model Tavsiyesi | 32B+ (Llama 3.1) | Herhangi | agenticSeek: ağır model gerekli |
| Açık Issue | 28 | Bilgi yok | agenticSeek: aktif geliştirme |
| Python Versiyon | 3.10+ | 3.8+ | agenticSeek: daha yeni Python |

## Kazıma Mimarisi (agenticSeek)

**Beş katmanlı kontrol** (D-310 kararı) uygulanabilir:

1. **API-First Tanım** → agenticSeek: SearXNG instance (öz yönetim)
2. **Doğrulama** → Sandbox'ta çalışan Python, şema kontrollü
3. **Referential Integrity** → Lokal Ollama DB (PostgreSQL önerilen)
4. **İzin + Rate Limiting** → Model context window sınırı (Llama 3.1: 8K default)
5. **Audit Trail** → Kod çalışma geçmişi + sorgular → Merkezi log

## Fırsat vs Risk

### **A — Seçenek: agenticSeek (Tam Local)**

✅ **Artı:**
- Veri hiçbir zaman dış API'ye gitmez
- Ajan mantığı kodlayabiliyor (örn: "sayfayı kısa al → analiz et → devam et")
- Voice interface müşteri demo'su için cazip
- GPU destekli (NVIDIA CUDA)

❌ **Eksi:**
- GPL-3.0: kaynak kodu açık tutmak gerekli (ticari değer sorunu)
- 32B model = 24GB RAM minimum (kurumsal sunucular: pahalı)
- 28 açık issue: üretim istikrarı belirsiz
- Scrapling'den 3 yıl geri (maturity)

**ROI:** 3-4 ay yatırım, GPL uyum + model tuninge

---

### **B — Seçenek: Scrapling (MCP Server)**

✅ **Artı:**
- MIT: ticari kullanım serbest
- 84K ⭐: uzun desteklenen, stabil
- Agent Skill hazır (n8n uyumlu)
- Lightweight: 8GB RAM yeterli

❌ **Eksi:**
- Ajan mantığı yok: sadece HTML → text
- "Kodlama" yeteneği: sadece prompt + LLM
- Voice: ek geliştirme
- D-310 kontrol katmanlarını elle yapmalı

**ROI:** 1-2 ay yatırım, daha hızlı ama işlev sınırlı

---

### **C — Seçenek: Hibrit (Scrapling + Ollama)**

✅ **Artı:**
- Scrapling: hızlı HTML almak
- Ollama (Llama 3.1): yerel düşünme motoru
- GPL sorunu yok
- D-310 katmanları tam uygulanabilir

❌ **Eksi:**
- İki araç entegrasyonu (+20 saat)
- Kod karmaşıklığı artar
- Model yanıtlarının kalitesi test gerektiriyor

**ROI:** 2-3 ay yatırım, en esnekbut en karmaşık

---

## Seçtiğim Yol

**Seçenek C (Hibrit)** önerilir:
- Scrapling: hızlı, stabil, MIT
- Ollama: yerel mantık motoru (GPL sorunu yok)
- D-310 beş katmanlı kontrol tam uygulanır
- VERI-NACE-* görevlerine hemen başlanabilir

**Neden agenticSeek değil:**
1. GPL-3.0 ile ticari kontrolde risk
2. 32B model maliyeti, eğitim sunucusu gerekli
3. 28 açık issue: kritik bug'lar çözülmemiş
4. Scrapling + Ollama = aynı sonuç, daha az bağımlılık

---

## Öz-eleştiri

agenticSeek'i "tam local" olması nedeniyle değerlendirdim, ama **GPL lisans riskini kurumsal kullanım bağlamında gözden kaçırdım ilk okumada.** Hibrit seçenek (C) daha sonra eklenmesinin sebebi bu: agenticSeek yalnızca araştırma aşamasında, kanıt konsepti (PoC) için uygun; üretim gitmezse MIT araçlarına dönülmeli.

---

## Sonraki Adım

VERI-NACE-ACILIM-01 ve VERI-NACE-SOZLUK-DIL-01 görevleri Scrapling + Ollama mimarisi ile başlayabilir; agenticSeek ise PoC sprint'ine alınır (Faz 2).
