# -*- coding: utf-8 -*-
"""P7-4: CareerPagesApifySource testleri."""
from __future__ import annotations

import pytest

from src.company_master.intelligence.job_intelligence.sources.career_apify_source import (
    CareerPagesApifySource,
)


def test_default_init():
    src = CareerPagesApifySource(apify_token="test-token")
    assert src.source_name == "career-pages-apify"
    assert src.actor_id == "apify/website-crawler"
    assert src.max_pages == 50
    assert src._company_urls == []


def test_custom_init():
    src = CareerPagesApifySource(
        source_name="test-career",
        actor_id="apify/company-career",
        apify_token="test-token",
        max_pages=25,
    )
    assert src.source_name == "test-career"
    assert src.actor_id == "apify/company-career"
    assert src.max_pages == 25


def test_set_company_urls():
    src = CareerPagesApifySource(apify_token="test-token")
    urls = ["https://example.com/kariyer", "https://example2.com/jobs"]
    src.set_company_urls(urls)
    assert src._company_urls == urls


def test_build_run_input_empty():
    src = CareerPagesApifySource(apify_token="test-token")
    run_input = src._build_run_input()
    assert run_input["startUrls"] == []
    assert run_input["maxPages"] == 1


def test_build_run_input_with_urls():
    src = CareerPagesApifySource(
        max_pages=5, apify_token="test-token",
    )
    src.set_company_urls([
        "https://example.com/kariyer",
        "https://example2.com/jobs",
    ])
    run_input = src._build_run_input()
    assert len(run_input["startUrls"]) == 2
    assert run_input["maxPages"] == 2


def test_build_run_input_limited():
    src = CareerPagesApifySource(
        max_pages=3, apify_token="test-token",
    )
    src.set_company_urls([
        f"https://example{i}.com/kariyer" for i in range(10)
    ])
    run_input = src._build_run_input()
    assert len(run_input["startUrls"]) == 3


def test_apify_item_to_scraped_job():
    src = CareerPagesApifySource(apify_token="test-token")
    item = {
        "url": "https://example.com/job/1",
        "title": "Yazılım Geliştirici",
        "description": "Python, Django geliştirme",
        "id": "job-1",
    }
    job = src._apify_item_to_scraped_job(item)
    assert job is not None
    assert job.title == "Yazılım Geliştirici"
    assert job.source_url == "https://example.com/job/1"
    assert job.raw_data == item


def test_parse_job_listing_empty():
    src = CareerPagesApifySource(apify_token="test-token")
    assert src.parse_job_listing("", "https://example.com") == []


def test_parse_job_listing_no_keywords():
    src = CareerPagesApifySource(apify_token="test-token")
    html = "<html><body>Merhaba dünya</body></html>"
    assert src.parse_job_listing(html, "https://example.com") == []


def test_parse_job_listing_with_jobs():
    src = CareerPagesApifySource(apify_token="test-token")
    html = """
    <html><body>
    <div class="job">
        <h2>Yazılım Geliştirici - Kariyer</h2>
        <p>Python Django backend pozisyon</p>
    </div>
    <div class="job">
        <h2>Frontend Developer - Job Opening</h2>
        <p>React TypeScript frontend</p>
    </div>
    </body></html>
    """
    jobs = src.parse_job_listing(html, "https://example.com")
    assert len(jobs) == 2
    for j in jobs:
        assert j.source_name == "career-pages-apify"
        assert j.location_country == "Türkiye"
    for j in jobs:
        assert j.source_name == "career-pages-apify"
        assert j.location_country == "Türkiye"
