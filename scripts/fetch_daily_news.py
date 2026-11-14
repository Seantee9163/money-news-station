import hashlib
import html
import os
from urllib.parse import urlparse

try:
    from .news_analysis import analyze, reviewed_translation, validate_payload
except ImportError:
    from news_analysis import analyze, reviewed_translation, validate_payload
import json
import re
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

TOPIC_KEYWORDS = {
    "赚钱机会": [r"\bopportunit(?:y|ies)\b", r"\bstartup\b", r"\bsmall business\b", r"\bcreator economy\b", r"\bside hustle\b"],
    "商业趋势": [r"\bbusiness\b", r"\bconsumer\b", r"\bretail\b", r"\bsupply chain\b", r"\bmarket demand\b", r"\bpricing\b"],
    "投资动向": [r"\binvest(?:ment|or|ing)\b", r"\bfund\b", r"\bcapital\b", r"\bipo\b", r"\bmerger\b", r"\bacquisition\b", r"\bbuyback\b"],
    "政策变化": [r"\bpolicy\b", r"\bregulation\b", r"\btariff\b", r"\btax\b", r"\bcentral bank\b", r"\binterest rate\b", r"\bsanction\b"],
    "AI工具": [r"\bai\b", r"\bartificial intelligence\b", r"\bgenerative ai\b", r"\bmachine learning\b", r"\bllm\b", r"\bchatbot\b", r"\bautomation\b", r"\bai agent\b"],
    "电商": [r"\be-?commerce\b", r"\bonline shopping\b", r"\bmarketplace\b", r"\bcross-border commerce\b"],
    "制造业": [r"\bmanufactur(?:ing|er)\b", r"\bfactory\b", r"\bindustrial\b", r"\bproduction\b", r"\bsemiconductor\b", r"\bchipmaker\b"],
    "贵金属": [r"\bgold\b", r"\bsilver\b", r"\bplatinum\b", r"\bpalladium\b", r"\bprecious metal(?:s)?\b"],
    "能源与资源": [r"\boil\b", r"\bgas\b", r"\bcopper\b", r"\blithium\b", r"\brare earth\b", r"\bmining\b", r"\benergy\b"],
    "新兴赛道": [r"\bclean energy\b", r"\bbattery\b", r"\brobotics\b", r"\bbiotech\b", r"\bquantum\b", r"\bspace tech\b", r"\bdata cent(?:er|re)\b"],
}

CATEGORY_PRIORITY = {
    "赚钱机会": 9,
    "投资动向": 8,
    "政策变化": 8,
    "AI工具": 8,
    "贵金属": 8,
    "制造业": 7,
    "能源与资源": 7,
    "电商": 7,
    "新兴赛道": 7,
    "商业趋势": 6,
}

FEEDS = [
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "source": "BBC"},
    {"url": "https://feeds.bbci.co.uk/news/technology/rss.xml", "source": "BBC"},
    {"url": "https://www.ft.com/rss/home", "source": "Financial Times"},
]

CJK_RE = re.compile(r"[\u3400-\u9fff]")


def request_bytes(url: str, timeout: int = 25) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "money-news-station-bot/3.0 (+https://github.com/Seantee9163/money-news-station)"
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def has_chinese(text: str) -> bool:
    return bool(CJK_RE.search(text or ""))


def translate_google(text: str) -> str:
    params = urlencode(
        {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": text,
        }
    )
    raw = request_bytes("https://translate.googleapis.com/translate_a/single?" + params, timeout=20)
    data = json.loads(raw.decode("utf-8"))
    parts = []
    for segment in data[0] or []:
        if segment and segment[0]:
            parts.append(segment[0])
    return "".join(parts).strip()


def translate_mymemory(text: str) -> str:
    if len(text) > 450:
        raise ValueError("Fallback translation would truncate source")
    params = urlencode({"q": text, "langpair": "en|zh-CN"})
    raw = request_bytes("https://api.mymemory.translated.net/get?" + params, timeout=20)
    data = json.loads(raw.decode("utf-8"))
    if str(data.get("responseStatus")) != "200":
        raise ValueError("Translation provider rejected request")
    return (data.get("responseData", {}).get("translatedText") or "").strip()


def translate_zh(text: str) -> str:
    text = strip_html(text)
    if not text:
        return ""
    reviewed = reviewed_translation(text)
    if reviewed:
        return reviewed
    if has_chinese(text):
        return text

    last_error = None
    for attempt in range(2):
        try:
            translated = translate_google(text)
            if has_chinese(translated):
                return translated
        except Exception as exc:
            last_error = exc
        time.sleep(0.4 + attempt * 0.4)

    try:
        translated = translate_mymemory(text)
        if has_chinese(translated):
            return translated
    except Exception as exc:
        last_error = exc

    raise RuntimeError(f"Chinese translation failed: {last_error or 'no Chinese output'}")


def category_scores(text: str):
    scores = {}
    for category, patterns in TOPIC_KEYWORDS.items():
        score = sum(1 for pattern in patterns if re.search(pattern, text, flags=re.I))
        if score:
            scores[category] = score
    return scores


def detect_category(text: str):
    scores = category_scores(text)
    if not scores:
        return None, 0
    category = max(scores, key=lambda c: (scores[c], CATEGORY_PRIORITY[c]))
    return category, scores[category]


def parse_items(feed_bytes: bytes, default_source: str):
    root = ET.fromstring(feed_bytes)
    out = []

    for item in root.findall(".//channel/item"):
        out.append(
            (
                (item.findtext("title") or "").strip(),
                (item.findtext("link") or "").strip(),
                (item.findtext("description") or "").strip(),
                (item.findtext("pubDate") or "").strip(),
                (item.findtext("source") or "").strip() or default_source,
            )
        )

    if not out:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//a:entry", ns):
            link_el = next((el for el in entry.findall("a:link", ns)
                            if el.get("rel", "alternate") == "alternate"), None)
            out.append(
                (
                    (entry.findtext("a:title", default="", namespaces=ns) or "").strip(),
                    (link_el.attrib.get("href", "") if link_el is not None else "").strip(),
                    (entry.findtext("a:summary", default="", namespaces=ns) or "").strip(),
                    (entry.findtext("a:published", default="", namespaces=ns) or "").strip(),
                    default_source,
                )
            )
    return out


def parse_date(pub_raw: str):
    if not pub_raw:
        return None
    try:
        dt = parsedate_to_datetime(pub_raw)
        return dt if dt.tzinfo else None
    except Exception:
        try:
            dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            return dt if dt.tzinfo else None
        except Exception:
            return None


def build_candidates():
    now = datetime.now(timezone.utc)
    collected = []
    seen = set()
    seen_links = set()

    for feed in FEEDS:
        try:
            xml_bytes = request_bytes(feed["url"])
            feed_items = parse_items(xml_bytes, feed["source"])
        except Exception as exc:
            print(f"[WARN] Failed to fetch {feed['source']}: {exc}")
            continue

        for title, link, desc, pub_raw, source in feed_items:
            title = strip_html(title)
            desc = strip_html(desc)
            link = link.strip()
            try:
                parsed_link = urlparse(link)
            except ValueError:
                continue
            allowed_hosts = {"BBC": {"www.bbc.co.uk", "www.bbc.com"},
                             "Financial Times": {"www.ft.com"}}
            if (not title or parsed_link.scheme != "https" or
                    parsed_link.hostname not in allowed_hosts[feed["source"]] or
                    parsed_link.username or parsed_link.password):
                continue

            key = re.sub(r"\W+", " ", title.lower()).strip()
            if key in seen or link in seen_links:
                continue

            category, keyword_score = detect_category(f"{title} {desc}")
            if not category:
                continue

            pub_dt = parse_date(pub_raw)
            if pub_dt is None:
                continue
            age_hours = (now - pub_dt.astimezone(timezone.utc)).total_seconds() / 3600
            if age_hours < -1 / 6 or age_hours > 72:
                continue
            seen.add(key)
            seen_links.add(link)
            freshness = max(0, 72 - age_hours) / 12
            relevance = keyword_score * 4 + CATEGORY_PRIORITY[category] + freshness

            collected.append(
                {
                    "original_title": title,
                    "original_desc": desc,
                    "category": category,
                    "source_name": feed["source"],
                    "published_at": pub_dt.isoformat(),
                    "published_raw": pub_raw,
                    "retrieved_at": now.isoformat(),
                    "feed_url": feed["url"],
                    "source_url": link,
                    "date": pub_dt.date().isoformat(),
                    "_score": relevance,
                    "_ts": pub_dt.timestamp(),
                }
            )

    collected.sort(key=lambda x: (x["_score"], x["_ts"]), reverse=True)
    return collected


def localize_item(candidate: dict) -> dict:
    title_zh = translate_zh(candidate["original_title"])
    desc_source = candidate["original_desc"] or candidate["original_title"]
    desc_zh = translate_zh(desc_source)

    if not has_chinese(title_zh) or not has_chinese(desc_zh):
        raise RuntimeError("Localized title/summary is not Chinese")

    category = candidate["category"]
    analysis = analyze(candidate, title_zh)
    stable_id = int(hashlib.md5(candidate["source_url"].encode("utf-8")).hexdigest()[:8], 16)

    return {
        "id": stable_id,
        "title": title_zh,
        "category": category,
        "date": candidate["date"],
        "summary": f"【{category}】{desc_zh}",
        "opportunity": analysis["opportunity"],
        "content": f"来源摘要（非全文）：{desc_zh}\n证据边界：仅依据来源标题及RSS摘要，未核验全文或独立证实来源说法。",
        "source_name": candidate["source_name"],
        "source_url": candidate["source_url"],
        "risk": analysis["risk"],
        "why_it_matters": analysis["why_it_matters"],
        "analysis": analysis["metadata"],
        "original_title": candidate["original_title"],
        "original_desc": candidate["original_desc"],
        "published_at": candidate.get("published_at"),
        "published_raw": candidate.get("published_raw"),
        "retrieved_at": candidate.get("retrieved_at"),
        "feed_url": candidate.get("feed_url"),
        "translation_status": "reviewed" if all(reviewed_translation(t) for t in
            (candidate["original_title"], desc_source)) else "machine_unreviewed",
        "is_featured": False,
    }


def main():
    candidates = build_candidates()
    payload = []

    for candidate in candidates[:15]:
        if len(payload) >= 5:
            break
        try:
            item = localize_item(candidate)
            payload.append(item)
            print(f"[OK] {item['category']}: {item['title']}")
        except Exception as exc:
            print(f"[WARN] Translation skipped: {candidate['original_title']} ({exc})")

    if len(payload) < 3:
        print(f"[ERROR] Only {len(payload)} Chinese news items produced. Existing site data will be preserved.")
        sys.exit(1)

    payload[0]["is_featured"] = True

    for item in payload:
        for field in ("title", "summary", "content", "opportunity", "risk", "why_it_matters"):
            if not has_chinese(item[field]):
                print(f"[ERROR] Non-Chinese output detected in {field}: {item[field]}")
                sys.exit(1)

    validate_payload(payload)
    with open("news-data.json.tmp", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace("news-data.json.tmp", "news-data.json")

    print(f"news-data.json updated with {len(payload)} Chinese opportunity-focused items.")


if __name__ == "__main__":
    main()
