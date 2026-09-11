# -*- coding: utf-8 -*-
"""Job Intelligence — Veri kaynakları (scraper'lar)."""

from __future__ import annotations

from .base import BaseJobSource, ScrapedJob, CAREER_PATHS, JOB_KEYWORDS
from .apify_job_source import ApifyJobSource
from .apify_client import ApifyClient, ApifyError
from .company_career import CompanyCareerSource
from .iskur import IskurSource
from .kariyer_net import KariyerNetSource

__all__ = [
    "BaseJobSource",
    "ScrapedJob",
    "CAREER_PATHS",
    "JOB_KEYWORDS",
    "ApifyJobSource",
    "ApifyClient",
    "ApifyError",
    "CompanyCareerSource",
    "IskurSource",
    "KariyerNetSource",
]
