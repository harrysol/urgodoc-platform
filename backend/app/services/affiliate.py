"""Affiliate-link monetization.

Converts a raw merchant product URL into a revenue-bearing link so every
generated try-on can be monetized via automated affiliate networks:

* **Skimlinks / Sovrn** — wraps *any* merchant in a publisher deep link (the
  network auto-matches the merchant's affiliate program). Preferred because it
  works across the entire long tail of retailers a stylist might paste.
* **Amazon Associates** — appends the associate ``tag`` for amazon.* domains.

If no network is configured, the original URL is returned unchanged.
"""

from __future__ import annotations

from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

from ..config import settings


def to_affiliate_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    # 1. Amazon-specific tagging (highest commission when applicable).
    if settings.AMAZON_ASSOCIATE_TAG and "amazon." in host:
        query = dict(parse_qsl(parsed.query))
        query["tag"] = settings.AMAZON_ASSOCIATE_TAG
        return urlunparse(parsed._replace(query=urlencode(query)))

    # 2. Skimlinks universal deep link covers every other merchant.
    if settings.SKIMLINKS_PUBLISHER_ID:
        return (
            f"https://go.skimresources.com/?id={settings.SKIMLINKS_PUBLISHER_ID}"
            f"&xs=1&url={quote(url, safe='')}"
        )

    # 3. No network configured — return the link untouched.
    return url
