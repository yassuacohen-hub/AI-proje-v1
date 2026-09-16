# Anthropic Workload Identity — Federasyon Kuralı Düzeltme Kılavuzu

Tarih: 2026-09-16 · Hazırlayan: roo · Kural ID: `fdrl_01N5WFvevBbMMtgkyDk5Vaz9`
Kullanan workflow'lar: `.github/workflows/anthropic-review.yml` (PR inceleme), `.github/workflows/anthropic-ci-explain.yml` (CI hata açıklama).
Ortak adım: `.github/actions/anthropic-oidc/action.yml` (audience `https://api.anthropic.com`).

## GitHub OIDC token'ı gerçekte ne gönderir?

GitHub Actions JWT'sindeki claim'ler **URL değil, kısa değerdir**:

| Claim | GitHub'ın gönderdiği gerçek değer |
|---|---|
| `sub` | `repo:yassuacohen-hub/-AI-proje-v1-Parent-repo:pull_request` (PR) / `repo:yassuacohen-hub/-AI-proje-v1-Parent-repo:ref:refs/heads/main` (push, workflow_run) |
| `repository` | `yassuacohen-hub/-AI-proje-v1-Parent-repo` |
| `repository_owner` | `yassuacohen-hub` |
| `event_name` | `pull_request` (review) · `workflow_run` (ci-explain) · `push` |

## Konsoldaki mevcut değerler → olması gereken

| Alan | Şu an girili (HATALI) | Olması gereken |
|---|---|---|
| Konu öneki (subject prefix) | `repo:https://github.com/HUGINN-MUMINN-command-center/yassuacohen-hub/-AI-proje-v1-Parent-repo:*` | `repo:yassuacohen-hub/-AI-proje-v1-Parent-repo:` |
| `repository_owner` | `https://github.com/HUGINN-MUMINN-command-center` | `yassuacohen-hub` |
| `event_name` (etkinlik_adı) | `push` | **SİL** — PR review `pull_request`, CI-explain `workflow_run` ile tetiklenir; `push` eşitliği ikisini de reddeder |
| `repository` (depo) | `https://github.com/HUGINN-MUMINN-command-center/yassuacohen-hub/-AI-proje-v1-Parent-repo` | `yassuacohen-hub/-AI-proje-v1-Parent-repo` |
| OAuth kapsamı | `org:admin workspace:developer` | **`org:admin` KALDIR** — konsol uyarısı: "kuruluşa tam yönetimsel erişim". CI token'ı yalnız mesaj üretir; `workspace:developer` (veya varsa yalnız inference kapsamı) yeter |
| Token ömrü | 86.400 s | Sorun değil; ihraççı üst sınırı (1.08 sa) zaten kısıtlar. İstenirse 3.600 s |

Doğru olanlar: ihraççı URL `https://token.actions.githubusercontent.com`, JTI tekrar oynatma koruması açık, kural ID action.yml ile aynı, çalışma alanı "tüm alanlar" (kabul edilebilir; istenirse tek alan `wrkspc_013LPgw97ZUzYnJHKxjuj3X8`).

## Marka notu
Kural adı `huginn-mumunn-komuta-merkezi` → doğru yazım **Muninn** (`huginn-muninn-komuta-merkezi`). Teknik etkisi yok; AGENTS.md marka kuralı gereği not düşüldü.

## Doğrulama (sahip düzelttikten sonra roo yapar)
1. PR #14'e küçük bir push → `Anthropic PR Review` job'ı yeşil + PR'da `<!-- anthropic-bot -->` yorumu.
2. Konsol → İş yükü kimliği → "Kimlik doğrulama olayları" sekmesinde başarılı kayıt.
3. `anthropic-ci-explain.yml` yalnız **varsayılan dal** (main) üzerindeki workflow dosyasından tetiklenir → main merge sonrası test edilir.

## cline iş yükü etkisi (roo değerlendirmesi)
- Claude PR incelemesi **diff bazlı statik** bulgu verir (hata, güvenlik, UTF-8/BOM, eksik test). Bu, cline'ın "kod okuma" yükünün ~yarısını alır.
- cline'a kalan: çalıştırarak doğrulama (pytest, Streamlit), pano/brif şartlarına uygunluk, marka/terminoloji, mimari tutarlılık, D-35 türü süreç bulguları. Bunlar diff'ten görülmez.
- Öneri: Claude yorumu geldikten sonra cline yalnız "Claude'un bulgularını doğrula + brif kontrol listesi" yapar; sıfırdan diff okumaz. Bu ORCH-13 brifine madde olarak eklenecek.
