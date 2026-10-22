"""Belgelerdeki fikirleri kodda ara: dosya:satir kaniti."""
import re, os, json
ROOT = "Huginn Data Insights"
ROOTS = [f"{ROOT}/{d}" for d in ("src", "web_dashboard", "scripts", "frontend/app", "frontend/src", "supabase", "tests", "agent_bilo", "workflows")]
INC = (".py", ".tsx", ".ts", ".yml", ".yaml", ".sql")
SKIP = ("node_modules", ".next", "_ARSIV", "_arsiv", "__pycache__", ".venv")
FIKIR = {
    "cmdk_spotlight": r"cmdk|CommandDialog|Command\.Input|spotlight",
    "json_ld_paywall": r"isAccessibleForFree|application/ld\+json",
    "sse_stream": r"EventSource|text/event-stream|StreamingResponse",
    "sonner_toast": r"from ['\"]sonner['\"]|toast\(",
    "webhook_sinyal": r"webhook",
    "ihale_ekap_dmo": r"ekap|\bdmo\b|ihale",
    "profil_inceleyen": r"inceleyen|profile_view|viewed_by",
    "derin_rapor_24s": r"derin.?rapor|deep.?report|24.?saat",
    "atil_kapasite": r"at[ıi]l.?kapasite|hurda|kapasite_ilan",
    "programmatic_seo": r"generateStaticParams|sitemap|robots",
    "kong_gateway": r"kong",
    "mtls": r"mtls|client_cert|ssl_client",
    "celery_karantina": r"celery|quarantine|karantina",
    "kvkk_maskele": r"maskele|mask_|kvkk|pii",
    "fraud_paravan": r"fraud|paravan|sahte.?sirket",
    "findeks_plg": r"findeks|cek.?endeks|protesto",
    "ubo_ortaklik": r"\bubo\b|ortakl[ıi]k|parent_vkn|shareholder",
    "redis_cache": r"redis",
    "docker_compose": r"docker.?compose|healthcheck",
    "rate_limit": r"rate.?limit|slowapi",
    "kredi_hediye_promo": r"promosyon|promotion|hediye.?kredi|welcome.?credit",
    "tier_scope": r"scope.*kredi|kredi_dus|network:read|fraud:read",
}
hits = {k: [] for k in FIKIR}
rx = {k: re.compile(v, re.I) for k, v in FIKIR.items()}
import itertools
for dp, dn, fn in itertools.chain.from_iterable(os.walk(r) for r in ROOTS if os.path.isdir(r)):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(INC):
            continue
        p = os.path.join(dp, f)
        try:
            lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
        except Exception:
            continue
        for i, l in enumerate(lines):
            for k, r in rx.items():
                if r.search(l) and len(hits[k]) < 8:
                    hits[k].append(f"{p.replace(chr(92), '/')}:{i+1} | {l.strip()[:120]}")
out = []
for k in FIKIR:
    out.append(f"\n## {k}: {len(hits[k])}{'+' if len(hits[k])>=8 else ''}")
    out += ["  " + h for h in hits[k]]
open("_tmp/fikir_kod_out.txt", "w", encoding="utf-8").write("\n".join(out))
print({k: len(v) for k, v in hits.items()})
