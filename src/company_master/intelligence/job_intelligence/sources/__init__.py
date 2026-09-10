# -*- coding: utf-8 -*-
"""Job Intelligence — Veri kaynakları (scraper'lar)."""
from __future__ import annotations

from .base import BaseJobSource
from .apify_job_source import ApifyJobSource

__all__ = ["BaseJobSource", "ApifyJobSource"]
