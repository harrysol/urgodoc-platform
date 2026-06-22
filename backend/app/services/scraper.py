"""Headless scraping layer (Playwright + optional residential proxy).

Runs inside the Celery worker (synchronous Playwright API). Captures a full-page
screenshot for the Vision LLM and best-effort extracts the primary product image
URL (used as the cleanest input for Tripo3D's image-to-3D model).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from ..config import settings

logger = logging.getLogger(__name__)

# A realistic desktop UA reduces trivial bot blocks; residential proxies handle
# the harder anti-scraping cases.
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


@dataclass
class ScrapeResult:
    screenshot_bytes: bytes
    screenshot_mime: str
    page_title: str | None
    product_image_url: str | None


class ScraperError(RuntimeError):
    """Raised when the page cannot be loaded or captured."""


def _build_proxy() -> dict | None:
    """Translate proxy env vars into Playwright's proxy config, or None."""
    if not settings.SCRAPER_PROXY_SERVER:
        return None
    proxy: dict[str, str] = {"server": settings.SCRAPER_PROXY_SERVER}
    if settings.SCRAPER_PROXY_USERNAME:
        proxy["username"] = settings.SCRAPER_PROXY_USERNAME
    if settings.SCRAPER_PROXY_PASSWORD:
        proxy["password"] = settings.SCRAPER_PROXY_PASSWORD
    return proxy


# JS evaluated in the page to find the best candidate product image. Prefers
# the Open Graph image, then the largest rendered <img>.
_FIND_IMAGE_JS = """
() => {
    const og = document.querySelector('meta[property="og:image"], meta[name="og:image"]');
    if (og && og.content) return og.content;

    const twitter = document.querySelector('meta[name="twitter:image"]');
    if (twitter && twitter.content) return twitter.content;

    let best = null;
    let bestArea = 0;
    for (const img of Array.from(document.images)) {
        const area = (img.naturalWidth || img.width) * (img.naturalHeight || img.height);
        if (area > bestArea && img.currentSrc) {
            bestArea = area;
            best = img.currentSrc;
        }
    }
    return best;
}
"""


def capture_product_page(url: str) -> ScrapeResult:
    """Load ``url`` headlessly and return a screenshot + product image URL."""
    proxy = _build_proxy()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                proxy=proxy,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            try:
                context = browser.new_context(
                    user_agent=_USER_AGENT,
                    viewport={"width": 1366, "height": 1024},
                    locale="en-US",
                )
                page = context.new_page()
                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=settings.SCRAPER_TIMEOUT_MS,
                )
                # Let lazy-loaded hero imagery settle.
                page.wait_for_timeout(1500)

                title = page.title()
                try:
                    product_image_url = page.evaluate(_FIND_IMAGE_JS)
                except Exception:  # noqa: BLE001 — image discovery is best-effort
                    product_image_url = None

                screenshot = page.screenshot(full_page=True, type="png")
                return ScrapeResult(
                    screenshot_bytes=screenshot,
                    screenshot_mime="image/png",
                    page_title=title,
                    product_image_url=product_image_url,
                )
            finally:
                browser.close()
    except PlaywrightTimeoutError as exc:
        raise ScraperError(f"Timed out loading {url}") from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Scrape failed for %s", url)
        raise ScraperError(f"Failed to scrape {url}: {exc}") from exc
