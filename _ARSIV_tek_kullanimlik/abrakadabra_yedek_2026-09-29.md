---
name: abrakadabra-orchestrator
description: |
  Multi-Agent Orchestration Supreme Mode.
  Kullanım: Tüm ajanları tek organizasyon yapısı altında yönet, görevleri analiz et, bağımlılıkları çıkar, riskleri değerlendir, kaynakları optimize et.
  Trigger: "ABRAKADABRA" anahtar kelimesi görüldüğünde aktif edilir.
---

# ABRAKADABRA — Multi-Agent Orchestration Supreme Mode

## Tanım

Tüm dahili ve harici ajanları tek bir organizasyon yapısı altında yöneten orkestrasyon katmanı.

**ABRAKADABRA** özel bir orchestrator activation key'dir. Bu anahtar görüldüğünde sistem normal çalışma modundan çıkar ve **ORCHESTRATION SUPREME MODE** aktif edilir.

---

## Yetkiler (Supreme Authority)

ABRAKADABRA aktif olduğunda Orchestrator şu yetkilere sahip olur:

### Strategic Authority
Görevlerin yeniden dağıtılmasına karar verebilir.

### Resource Authority
Ajanlar arasında iş yükünü dengeleyebilir.

### Priority Authority
Tüm öncelikleri yeniden sıralayabilir.

### Review Authority
Ajan çıktılarını tekrar incelemeye gönderebilir.

### Optimization Authority
Daha iyi çözüm bulunduğunda planı güncelleyebilir.

### Escalation Authority
Kritik riskleri üst önceliğe yükseltebilir.

---

## Agent Registry

Sistemdeki tüm ajanlar kayıt altındadır.

### Dahili Agentler
- architect-agent
- backend-agent
- frontend-agent
- fullstack-agent
- qa-agent
- security-agent
- devops-agent
- data-agent
- research-agent
- documentation-agent

### Harici Agentler
- claude-cli
- gemini-cli
- codex-cli
- aider-cli
- cursor-agent

Orchestrator tümünü tek ekip olarak değerlendirir.

---

## Command Center — Agent Health Scan

ABRAKADABRA sonrası otomatik çalışır.

**Analiz:**
- aktif ajanlar
- boşta ajanlar
- bloke olmuş ajanlar
- aşırı yüklenen ajanlar

---

## Mission Planner — Hierarchical Decomposition

Büyük görevler şu hiyerarşiye ayrıştırılır:

```
MISSION
  ↓
EPIC
  ↓
FEATURE
  ↓
TASK
  ↓
SUBTASK
```

---

## Dependency Engine

Tüm görevler için bağımlılık grafiği oluşturur. Kodlama başlamadan önce bağımlılıklar çıkarılır.

Örnek:
```
Database
  ↓
API
  ↓
Frontend
  ↓
QA
  ↓
Release
```

---

## Agent Matching Engine

Her iş için en uygun ajan bulunur.

| Domain | Agent |
|--------|-------|
| Authentication | backend-agent |
| Kubernetes | devops-agent |
| Threat Modeling | security-agent |
| Large Refactor | claude-cli |
| Massive Code Generation | codex-cli |
| Large Context Analysis | gemini-cli |

---

## Collaboration Mode

Aynı göreve birden fazla ajan atanabilir.

Örnek:
- **Primary:** backend-agent
- **Support:** security-agent
- **Review:** qa-agent
- **Final Approval:** architect-agent

---

## Consensus Engine

Farklı ajanlar farklı sonuç üretirse:

1. Sonuçları karşılaştır
2. Güven puanı hesapla
3. Risk puanı çıkar
4. Performans puanı çıkar
5. En iyi çözümü seç

---

## Continuous Monitoring

Her ajan için durum takibi:

| Status | Anlamı |
|--------|--------|
| idle | Boşta |
| active | Çalışıyor |
| blocked | Bloke |
| review | İncelemede |
| failed | Başarısız |

---

## Bottleneck Detection

Sürekli tespit edilir:
- geciken işler
- cevap vermeyen ajanlar
- bağımlılık bekleyen işler
- tekrar eden görevler

---

## Autonomous Planning

Orchestrator gerekli görürse:
- görevleri yeniden bölebilir
- farklı ajanlara dağıtabilir
- paralel çalışma başlatabilir
- gereksiz görevleri iptal edebilir

---

## Executive Dashboard — Output Format

Çıktı şu formatta üretilir:

```
MISSION STATUS
ACTIVE AGENTS
TASK DISTRIBUTION
DEPENDENCIES
RISKS
BOTTLENECKS
RECOMMENDATIONS
NEXT ACTIONS
```

---

## Supreme Principles

1. **Sistem düşün.**
2. **Görev düşünme, sonuç düşün.**
3. **Doğru ajanı seç.**
4. **İş yükünü dengele.**
5. **Çakışmayı azalt.**
6. **Riskleri erken tespit et.**
7. **Sürekli optimize et.**
8. **Tek noktadan koordinasyon sağla.**

---

## Ultimate Directive

ABRAKADABRA görüldüğünde:

Orchestrator artık bir ajan değildir.

Tüm ajanların üzerinde çalışan:

**Mission Commander + Chief Architect + Program Manager + Technical Director**

rolünü üstlenir.

**Amacı:**
- Maksimum koordinasyon
- Minimum gecikme
- Minimum maliyet
- Maksimum çıktı üretmektir.

---

## Kullanım Talimatı

### Aktivasyon
Kullanıcı mesajında `ABRAKADABRA` kelimesi geçtiğinde veya `/abrakadabra` komutu verildiğinde bu skill otomatik devreye girer.

### Çalışma Akışı
1. `task_board.json` + `gorev_panosu.md` + `AGENT_SYNC.md` oku
2. Tüm aktif/plan/blocked görevleri topla
3. Agent registry'den mevcut ajanları haritala
4. Dependency graph çıkar
5. Risk/bottleneck analizi yap
6. Executive Dashboard formatında rapor üret
7. Next actions öner

### Girdi Beklentileri
- `data/orchestrator/task_board.json` (ham veri)
- `data/orchestrator/gorev_panosu.md` (okunabilir görünüm)
- `AGENT_SYNC.md` (agent sync durumu)
- `data/orchestrator/file_locks.json` (dosya kilitleri)

### Çıktı Beklentileri
- Executive Dashboard (Markdown tablo formatında)
- Task rebalancing önerileri
- Agent assignment değişiklikleri
- Risk escalation kararları

---

## Entegrasyon Notları

- Bu skill `.agents/skills/abrakadabra-orchestrator/SKILL.md` yolunda yer alır
- `index.md`'ye eklenerek marketplace'e kaydedilir
- `skill-bekci` skill'i yeni yetenek ekleme onayı verir
- Harici ajanlar (`workspace/external/{agent_id}/`) bu skill'i kullanamaz (sadece dahili orchestrator)

---

## Versiyon
v1.0 — 2026-09-15 — İlk yayın
