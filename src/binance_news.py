import requests

BINANCE_ANNOUNCEMENT_URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"

def get_announcements(catalog_id=161, page_no=1, page_size=20):
    params = {
        "type": 1,
        "catalogId": catalog_id,
        "pageNo": page_no,
        "pageSize": page_size,
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.binance.com/en/support/announcement",
        "Accept-Language": "en",
        "lang": "en",
    }
    r = requests.get(BINANCE_ANNOUNCEMENT_URL, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

def save_announcements(catalog_id=161, page_no=1, page_size=20):
    import json
    import time
    from .database import save_news_event

    response = get_announcements(catalog_id, page_no, page_size)
    catalogs = response.get("data", {}).get("catalogs", [])
    articles = catalogs[0].get("articles", []) if catalogs else []
    received_at = time.time()

    for article in articles:
        save_news_event(
            source="BINANCE_OFFICIAL",
            source_id=str(article.get("id")),
            title=article.get("title", ""),
            symbol=None,
            published_at=article.get("releaseDate"),
            received_at=received_at,
            url=None,
            category="announcement",
            data=json.dumps(article, separators=(",", ":")),
        )

    return len(articles)

def filter_alpha_news(articles):
    keywords = ("binance alpha", "alpha will", "alpha listing", "alpha trading")
    return [
        article for article in articles
        if any(k in article.get("title", "").lower() for k in keywords)
    ]

def refresh_alpha_catalysts(catalog_id=161, page_no=1, page_size=20):
    import json
    import time
    from .database import get_connection, save_news_event

    response = get_announcements(catalog_id, page_no, page_size)
    catalogs = response.get("data", {}).get("catalogs", [])
    articles = catalogs[0].get("articles", []) if catalogs else []
    matches = filter_alpha_news(articles)
    received_at = time.time()

    for article in matches:
        news_id = save_news_event(
            source="BINANCE_OFFICIAL",
            source_id=str(article.get("id")),
            title=article.get("title", ""),
            symbol=None,
            published_at=article.get("releaseDate"),
            received_at=received_at,
            url=None,
            category="alpha_catalyst",
            data=json.dumps(article, separators=(",", ":")),
        )

        tokens = extract_alpha_tokens(article.get("title", ""))

        if news_id and tokens:
            conn = get_connection()
            for token in tokens:
                conn.execute(
                    "INSERT OR IGNORE INTO news_alpha_tokens "
                    "(news_id, symbol) VALUES (?, ?)",
                    (news_id, token),
                )
            conn.commit()
            conn.close()

    return len(matches)

def extract_alpha_tokens(title):
    import re

    if not title:
        return []

    match = re.search(r"Alpha Will (?:Remove|List)\s+(.+?)(?:\s+\(\d{4}-\d{2}-\d{2}\))?$", title, re.IGNORECASE)
    if not match:
        return []

    raw = match.group(1)
    raw = re.sub(r"\s+from\s+.*$", "", raw, flags=re.IGNORECASE)

    tokens = []
    for item in raw.split(","):
        token = item.strip()
        token = re.sub(r"\s*\([^)]*\)", "", token).strip()
        if token and re.fullmatch(r"[A-Z0-9]{1,20}", token):
            tokens.append(token)

    return tokens

def detect_news_signal_conflict(symbol, signal_direction, max_age_hours=24):
    """Return recent relevant news that may conflict with a signal."""
    import time
    from .database import get_connection

    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    base = symbol.replace("USDT", "").upper()
    conn = get_connection()
    rows = conn.execute(
        "SELECT source, title, published_at, url FROM news_events "
        "WHERE (UPPER(title) LIKE ? OR UPPER(title) LIKE ?) "
        "AND received_at >= ? ORDER BY received_at DESC",
        (f"%{base}%", f"%{symbol.upper()}%", cutoff)
    ).fetchall()
    conn.close()

    positive_words = (
        "listing", "partnership", "launch", "approval", "upgrade",
        "integration", "adoption", "funding", "bullish", "support"
    )
    negative_words = (
        "delist", "hack", "exploit", "suspend", "lawsuit",
        "ban", "investigation", "negative", "risk"
    )

    direction = (signal_direction or "").upper()
    conflicts = []

    for row in rows:
        title = (row[1] or "").lower()
        positive = any(word in title for word in positive_words)
        negative = any(word in title for word in negative_words)

        conflict = (
            direction in ("BEARISH", "SHORT") and positive
        ) or (
            direction in ("BULLISH", "LONG") and negative
        )

        if conflict:
            conflicts.append({
                "source": row[0],
                "title": row[1],
                "published_at": row[2],
                "url": row[3],
                "conflict": True
            })

    return conflicts

def get_worldwide_crypto_news(limit=20):
    """Fetch recent worldwide crypto news for context/confirmation."""
    import requests

    url = "https://cryptocurrency.cv/api/news"
    response = requests.get(url, params={"limit": limit}, timeout=10)
    response.raise_for_status()
    data = response.json()

    articles = data.get("articles", [])
    return [
        {
            "source": item.get("source"),
            "title": item.get("title"),
            "published_at": item.get("pubDate"),
            "url": item.get("link"),
        }
        for item in articles
        if item.get("title")
    ][:limit]
