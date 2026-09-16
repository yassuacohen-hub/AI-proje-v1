#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anthropic (Workload Identity) ile GitHub otomasyonu — tek script, iki mod.

- ``--mode pr``          : PR diff'ini inceler, PR'daki tek yorumu oluşturur/günceller.
- ``--mode ci-failure``  : Başarısız CI run'ının loglarını özetler (kök neden + çözüm).

Kimlik: GitHub OIDC JWT (``JWT`` env) → ``WorkloadIdentityCredentials``; API anahtarı yok.
Token tasarrufu: diff/log dosya bazlı kırpılır (``MAX_INPUT_CHARS``), gürültü dosyaları
(lock, jsonl, csv, min.js …) diff'ten atılır, gizli değerler maskelenir.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

MARKER = "<!-- anthropic-bot -->"
MAX_INPUT_CHARS = int(os.environ.get("ANTHROPIC_MAX_INPUT_CHARS", "120000"))  # ~30k token
MAX_OUTPUT_TOKENS = int(os.environ.get("ANTHROPIC_MAX_OUTPUT_TOKENS", "3000"))
GITHUB_API = "https://api.github.com"

# Diff'e girmeyecek dosyalar: incelemesi anlamsız, token yakan içerik.
GURULTU_DOSYA = re.compile(
    r"(^|/)(package-lock\.json|poetry\.lock|uv\.lock|Pipfile\.lock)$"
    r"|\.(jsonl|csv|parquet|min\.js|min\.css|svg|png|jpg|ico|lock|snap)$"
    r"|^(data|backups|logs|AI proje v1)/",
    re.IGNORECASE,
)

SISTEM_PR = (
    "Sen kıdemli bir Python/FastAPI/Streamlit/ETL kod inceleme uzmanısın. "
    "Yalnızca gerçek hata, güvenlik riski, veri kaybı, geriye dönük uyumsuzluk, "
    "UTF-8/BOM sorunu ve eksik testleri bildir; üslup yorumu yapma. "
    "Bulguları önem sırasıyla (KRİTİK/ORTA/DÜŞÜK) ve `dosya:satır` referansıyla yaz; "
    "sorun yoksa tek cümleyle 'Engelleyici bulgu yok' de. Kısa ve Türkçe yaz."
)
SISTEM_CI = (
    "Sen bir CI/CD hata analistisin. Verilen GitHub Actions loglarından "
    "(1) kök nedeni, (2) hangi dosya/test/komutun kırıldığını, (3) somut düzeltme adımlarını "
    "en fazla 15 satırda, Türkçe ve madde madde yaz. Tahmin yürütüyorsan belirt."
)


# ---------------------------------------------------------------- yardımcılar
def redact_secrets(text: str) -> str:
    """Anahtar/şifre benzeri değerleri maskeler (modelle paylaşılmadan önce)."""
    text = re.sub(
        r"(?i)\b(api[_-]?key|secret|token|password|passwd|pwd)(\s*[=:]\s*)(?:'[^']*'|\"[^\"]*\"|[^\s,]+)",
        r"\1\2[REDACTED]",
        text,
    )
    return re.sub(r"\b(sk-ant-|gh[pousr]_|AKIA)[A-Za-z0-9_-]{8,}", "[REDACTED]", text)


def diff_filtrele(diff: str) -> str:
    """Gürültü dosyalarını diff'ten çıkarır (``diff --git`` bloklarına göre)."""
    bloklar = re.split(r"(?m)^(?=diff --git )", diff)
    tutulan = []
    for blok in bloklar:
        if not blok.strip():
            continue
        m = re.match(r"diff --git a/(\S+) b/", blok)
        if m and GURULTU_DOSYA.search(m.group(1)):
            continue
        tutulan.append(blok)
    return "".join(tutulan)


def kirp(text: str, limit: int = MAX_INPUT_CHARS) -> tuple[str, bool]:
    """Metni ``limit`` karaktere kırpar; kırpıldıysa ``True`` döner."""
    if len(text) <= limit:
        return text, False
    return text[:limit] + "\n\n[... kırpıldı: girdi token sınırını aştı ...]\n", True


def _github(path: str, method: str = "GET", data: dict | None = None, raw: bool = False) -> Any:
    request = urllib.request.Request(
        f"{GITHUB_API}{path}",
        data=json.dumps(data).encode("utf-8") if data is not None else None,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as resp:
            body = resp.read()
            return body if raw else (json.loads(body) if body else None)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"GitHub API {method} {path}: HTTP {error.code}") from error


def yorum_yaz_veya_guncelle(pr_number: str, body: str) -> None:
    """Aynı PR'da MARKER'lı tek yorumu günceller; yoksa oluşturur (yorum spam'i yok)."""
    repo = os.environ["GITHUB_REPOSITORY"]
    body = f"{MARKER}\n{body}"
    for yorum in _github(f"/repos/{repo}/issues/{pr_number}/comments?per_page=100") or []:
        if MARKER in (yorum.get("body") or ""):
            _github(f"/repos/{repo}/issues/comments/{yorum['id']}", "PATCH", {"body": body})
            return
    _github(f"/repos/{repo}/issues/{pr_number}/comments", "POST", {"body": body})


def ciktiyi_yayinla(baslik: str, govde: str) -> None:
    """PR varsa yorum; her durumda job özetine (GITHUB_STEP_SUMMARY) yazar."""
    metin = f"## {baslik}\n\n{govde}"
    ozet = os.environ.get("GITHUB_STEP_SUMMARY")
    if ozet:
        with open(ozet, "a", encoding="utf-8") as f:
            f.write(metin + "\n")
    pr = os.environ.get("PR_NUMBER", "").strip()
    if pr:
        yorum_yaz_veya_guncelle(pr, metin)
    else:
        print(metin)


# ---------------------------------------------------------------- girdiler
def get_pull_request_diff() -> str:
    base_ref = os.environ["GITHUB_BASE_REF"]
    subprocess.run(
        ["git", "fetch", "--quiet", "origin", f"{base_ref}:refs/remotes/origin/{base_ref}"],
        check=True, capture_output=True, text=True,
    )
    # text=True kullanılmaz: eski cp1254 baytları (ör. 0xFD) UTF-8 çözümünü patlatır (PR #14 bulgusu).
    result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=20", f"origin/{base_ref}...HEAD"],
        check=True, capture_output=True,
    )
    return result.stdout.decode("utf-8", errors="replace")


def get_failed_job_logs(run_id: str) -> str:
    """Başarısız job'ların loglarını indirir; her job için son 200 satırı tutar."""
    repo = os.environ["GITHUB_REPOSITORY"]
    jobs = (_github(f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100") or {}).get("jobs", [])
    parcalar = []
    for job in jobs:
        if job.get("conclusion") != "failure":
            continue
        try:
            ham = _github(f"/repos/{repo}/actions/jobs/{job['id']}/logs", raw=True)
            satirlar = ham.decode("utf-8", errors="replace").splitlines()
        except RuntimeError as err:
            satirlar = [f"(log alınamadı: {err})"]
        # Zaman damgalarını sil (token tasarrufu), hata bölgesine odaklan.
        satirlar = [re.sub(r"^\S+T\S+Z ", "", s) for s in satirlar]
        parcalar.append(f"### Job: {job.get('name')}\n```\n" + "\n".join(satirlar[-200:]) + "\n```")
    return "\n\n".join(parcalar)


# ---------------------------------------------------------------- model
def claude_sor(system: str, prompt: str) -> str:
    import anthropic  # geç import: testler SDK'sız çalışsın
    from anthropic import WorkloadIdentityCredentials

    client = anthropic.Anthropic(
        credentials=WorkloadIdentityCredentials(
            identity_token_provider=lambda: os.environ["JWT"],
            federation_rule_id=os.environ["FEDERATION_RULE_ID"],
            organization_id=os.environ["ANTHROPIC_ORGANIZATION_ID"],
            service_account_id=os.environ["ANTHROPIC_SERVICE_ACCOUNT_ID"],
            workspace_id=os.environ["ANTHROPIC_WORKSPACE_ID"],
        ),
    )
    msg = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        max_tokens=MAX_OUTPUT_TOKENS,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


# ---------------------------------------------------------------- modlar
def mod_pr() -> None:
    diff = diff_filtrele(redact_secrets(get_pull_request_diff()))
    if not diff.strip():
        ciktiyi_yayinla("Anthropic PR incelemesi", "İncelenecek kod değişikliği bulunamadı (yalnızca veri/doküman dosyaları).")
        return
    diff, kirpildi = kirp(diff)
    review = claude_sor(
        SISTEM_PR,
        "Aşağıdaki GitHub PR diff'ini incele; her bulgu için neden ve kısa düzeltme önerisi ekle.\n\n"
        f"```diff\n{diff}\n```",
    )
    if kirpildi:
        review += "\n\n> ⚠️ Diff büyük olduğu için kırpıldı; inceleme ilk bölümü kapsar."
    ciktiyi_yayinla("Anthropic PR incelemesi", review)


def mod_ci_failure() -> None:
    run_id = os.environ["RUN_ID"]
    loglar = redact_secrets(get_failed_job_logs(run_id))
    if not loglar.strip():
        ciktiyi_yayinla("CI hata açıklaması", "Başarısız job bulunamadı.")
        return
    loglar, _ = kirp(loglar)
    aciklama = claude_sor(SISTEM_CI, f"Başarısız CI run logları:\n\n{loglar}")
    run_url = os.environ.get("RUN_URL", "")
    ciktiyi_yayinla("CI hata açıklaması", f"{aciklama}\n\n🔗 Run: {run_url}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["pr", "ci-failure"], default="pr")
    args = p.parse_args(argv)
    {"pr": mod_pr, "ci-failure": mod_ci_failure}[args.mode]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
