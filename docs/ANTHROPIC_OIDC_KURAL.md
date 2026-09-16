# Anthropic Workload Identity — Federasyon Kuralı Düzeltme Kılavuzu

Tarih: 2026-09-16 · Hazırlayan: roo · Kural ID: `fdrl_01N5WFvevBbMMtgkyDk5Vaz9`
Kullanan workflow'lar: `.github/workflows/anthropic-review.yml` (PR inceleme), `.github/workflows/anthropic-ci-explain.yml` (CI hata açıklama).
Ortak adım: `.github/actions/anthropic-oidc/action.yml` (audience `https://api.anthropic.com`).

## GitHub OIDC token'ı gerçekte ne gönderir?

GitHub Actions JWT'sindeki claim'ler **URL değil, kısa değerdir**:

| Claim | GitHub'ın gönderdiği gerçek değer |
|---|---|
| `sub` | **Gerçek değer (Anthropic denetim logu 2026-09-16 22:27, `req_011Cf7uUfGpojKnvwaGVfzvC`):** `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:pull_request` (PR) / `…@1364885446:ref:refs/heads/main` (workflow_run). GitHub bu repo için owner/repo adına `@ID` ekliyor. |
| `repository` | `yassuacohen-hub/-AI-proje-v1-Parent-repo` |
| `repository_owner` | `yassuacohen-hub` |
| `event_name` | `pull_request` (review) · `workflow_run` (ci-explain) · `push` |

## Konsoldaki mevcut değerler → olması gereken

| Alan | Şu an girili (HATALI) | Olması gereken |
|---|---|---|
| Konu öneki (subject prefix) | `repo:https://github.com/HUGINN-MUMINN-command-center/yassuacohen-hub/-AI-proje-v1-Parent-repo:*` | `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:` (sonda `*` YOK; `@ID` ekleri ŞART — logdaki gerçek `sub` böyle) |
| `repository_owner` | `https://github.com/HUGINN-MUMINN-command-center` | `yassuacohen-hub` |
| `event_name` (etkinlik_adı) | `push` | **SİL** — PR review `pull_request`, CI-explain `workflow_run` ile tetiklenir; `push` eşitliği ikisini de reddeder |
| `repository` (depo) | `https://github.com/HUGINN-MUMINN-command-center/yassuacohen-hub/-AI-proje-v1-Parent-repo` | `yassuacohen-hub/-AI-proje-v1-Parent-repo` |
| OAuth kapsamı | `org:admin workspace:developer` | **`org:admin` KALDIR** — konsol uyarısı: "kuruluşa tam yönetimsel erişim". CI token'ı yalnız mesaj üretir; `workspace:developer` (veya varsa yalnız inference kapsamı) yeter |
| Token ömrü | 86.400 s | Sorun değil; ihraççı üst sınırı (1.08 sa) zaten kısıtlar. İstenirse 3.600 s |

Doğru olanlar: ihraççı URL `https://token.actions.githubusercontent.com`, JTI tekrar oynatma koruması açık, kural ID action.yml ile aynı, çalışma alanı "tüm alanlar" (kabul edilebilir; istenirse tek alan `wrkspc_013LPgw97ZUzYnJHKxjuj3X8`).

## Deneme 1 sonucu (2026-09-16 22:27) — BAŞARISIZ: `match_subject_prefix`

Push `782427b` → job çalıştı, JWT Anthropic'e ulaştı (ihraççı, audience, `repository`, `repository_owner`, `event_name=pull_request` hepsi doğru). Tek red sebebi konu öneki: kuralda `repo:yassuacohen-hub/-AI-proje-v1-Parent-repo:*`, tokenda `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:pull_request`. İki fark: (1) `*` literal, (2) `@233441674` ve `@1364885446` ID ekleri eksik. Düzeltme: önek alanına `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:` yaz.

## Deneme 2 sonucu (2026-09-16 22:43) — YİNE BAŞARISIZ: `match_subject_prefix`

Push `bbc1070` → run 35159024076 (#20), `req_011Cf7vimAJQnoTqCJmRmRWQ`. Token tarafı deneme 1 ile birebir aynı (`sub` = `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:pull_request`, tüm claim'ler doğru). Aynı red → kuraldaki önek hâlâ bu `sub`'ın başlangıcı değil. Olasılıklar: (a) düzenleme kaydedilmedi ("test ettim, kapattım"), (b) kopyalarken baş/son boşluk veya `*` kaldı, (c) eski değer (`@ID`'siz) duruyor. Kontrol: kuralın **görüntüleme** sayfasında (Edit değil) "Subject prefix" satırının ekran görüntüsü.

Yedek plan (prefix garanti eşleşsin): öneğe `sub`'ın tamamını yaz → `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:pull_request`. Önek eşleşmesi tam eşleşmeyi de kapsar; `workflow_run` (ci-explain) o zaman ayrı kural ister — main merge sonrası eklenir.

## Deneme 3 sonucu (2026-09-16 22:54) — YİNE BAŞARISIZ: `match_subject_prefix` (kural doğru görünürken)

Push `684db76` → run 35159892457 (#21), `req_011Cf7waaTW79addPR28PfUo`. Kuralın görüntüleme sayfası ekran görüntüsüyle teyitli: önek `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:`, tokendaki `sub` bunun devamı. Buna rağmen red → Anthropic'in önek karşılaştırması bizim beklediğimiz düz `startswith` değil ya da kayıtlı değerde görünmez karakter/boşluk var.

Tanı planı (Deneme 4): öneği **elle** `repo:` yaz (kopyalama yok → görünmez karakter riski sıfır). Güvenlik düşmez: `repository` ve `repository_owner` eşitlik koşulları zaten yalnız bu depoyu geçirir; fork PR'larının `repository` claim'i fork deposudur, reddedilir.
- `success` → önek mantığı çalışıyor, sorun uzun değerdeydi; `repo:` + claim koşulları kalıcı çözüm olarak kabul edilebilir (ya da kademeli uzatılır).
- yine `failure` → Anthropic tarafı (format/bug); Anthropic destek + `request_id` ile bilet.

## Deneme 4 sonucu (2026-09-16 23:07) — YİNE BAŞARISIZ: `match_subject_prefix` → "Static = TAM EŞLEŞME" hipotezi doğrulandı

Push `65b60a6` → run 35160844030 (#22), `req_011Cf7xYeQTDnti8cQvoFj4H`, created 23:07:23Z. Önek yalnızca `repo:` iken bile red → önek/`startswith` mantığı hiç çalışmıyor. Kural ekranında Match rozeti **"Static"**, alan etiketi **"Subject pattern"**: Static mod büyük olasılıkla **tam metin eşleşmesi** yapıyor (`sub == pattern`), bu yüzden hiçbir kısmi değer geçmez. (Hata kodu adı `match_subject_prefix` yanıltıcı; iç kontrolün adı.)

Çözüm planı (Deneme 5): Subject pattern alanına `sub`'ın **tamamını** yaz:
`repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:pull_request`
- `success` → ÇALIŞIYOR; not: `workflow_run` (ci-explain) için `sub` sonu `:workflow_run` olur → main merge sonrası ikinci kural gerekir.
- yine `failure` → Anthropic destek bileti; request_id'ler: `req_011Cf7uUfGpojKnvwaGVfzvC` (#19), `req_011Cf7vimAJQnoTqCJmRmRWQ` (#20), `req_011Cf7waaTW79addPR28PfUo` (#21), `req_011Cf7xYeQTDnti8cQvoFj4H` (#22).

## Konsol "Test connection" kodu hakkında (2026-09-16 23:25)

Konsolun gösterdiği Python örneği (`read_token()` + `WorkloadIdentityCredentials`) **yerelde çalışmaz**: `/path/to/token` diye bir dosya yok; GitHub OIDC JWT yalnızca Actions koşusu içinde (`id-token: write`) üretilir. Örnekteki tüm kimlikler `.github/actions/anthropic-oidc/action.yml` ile birebir aynı (kural/org/servis hesabı/çalışma alanı/model) → kod tarafında değişiklik gerekmez. Gerçek test = PR'a push → "Anthropic PR Review" job'u.

Kural son hali (sahip kaydetti): konu öneki `repo:yassuacohen-hub/-AI-proje-v1-Parent-repo:*`, `repository_owner`, `repository` doğru; `event_name` satırı silindi; kapsam `workspace:developer`.

## Kopyala-yapıştır: düzenleme formu alan alan (sahip için)

| # | Form alanı | Yapılacak | Yazılacak değer |
|---|---|---|---|
| 1 | Kural adı | değiştir | `huginn-muninn-komuta-merkezi` |
| 2 | Tanım | değiştir | `GitHub Actions PR review + CI hata aciklama` |
| 3 | İhraççı | dokunma | `github-actions` |
| 4 | Eşleştirme | "Desen eşleşmesi" seçili kalsın | — |
| 5 | Konu modeli / Subject prefix | tamamını sil, yaz | `repo:yassuacohen-hub@233441674/-AI-proje-v1-Parent-repo@1364885446:` — **sonda `*` yok, `@ID` ekleri var** |
| 6 | Ek talep `repository_owner` | sağdaki değeri değiştir | `yassuacohen-hub` |
| 7 | Ek talep `event_name = push` | **çöp kutusu ile SİL** | — |
| 8 | Ek talep `repository` | sağdaki değeri değiştir | `yassuacohen-hub/-AI-proje-v1-Parent-repo` |
| 9 | Beklenen hedef kitle | boş bırak | (boş = `https://api.anthropic.com`, action.yml ile aynı) |
| 10 | Çalışma alanları (aşağıda) | "Tüm çalışma alanları" kalabilir | — |
| 11 | OAuth kapsamı (aşağıda) | `org:admin` kaldır, sadece | `workspace:developer` |
| 12 | Token ömrü | dokunma | 86400 |
| 13 | Kaydet | | |

Not: Konu modelinde sondaki `*` şart — PR'da `:pull_request`, CI-explain'de `:ref:refs/heads/main` ile bitiyor, ikisini de kapsar.

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
