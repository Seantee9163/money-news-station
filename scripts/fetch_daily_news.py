import hashlib
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

CATEGORY_COPY = {
    "赚钱机会": (
        "机会观察：寻找能够形成订单、服务收入或可验证现金流的公司与细分市场。",
        "风险提示：热点机会可能快速拥挤，需核对需求持续性、成本结构与真实现金流。",
        "为什么重要：这类变化可能直接创造新的收入入口、客户需求或商业模式。",
    ),
    "商业趋势": (
        "机会观察：关注消费行为、价格、供应链与渠道变化中出现的新需求和效率工具。",
        "风险提示：趋势不等于利润，需确认企业能否把需求变化转化为毛利和现金流。",
        "为什么重要：商业趋势往往先改变订单与成本，再传导到企业利润和估值。",
    ),
    "投资动向": (
        "机会观察：跟踪资金流向、并购、IPO与战略投资，寻找被资本重新定价的产业链。",
        "风险提示：估值上涨和账面收益不等于现金流，需区分真实经营改善与资本市场波动。",
        "为什么重要：大额资金流向通常会改变行业竞争、扩产速度与未来估值中枢。",
    ),
    "政策变化": (
        "机会观察：关注政策受益行业、合规服务、替代供应链与区域市场重新分配。",
        "风险提示：政策执行时间、范围与豁免条款可能改变，市场预期也可能快速反转。",
        "为什么重要：政策可以直接改变成本、准入、贸易路径与企业盈利空间。",
    ),
    "AI工具": (
        "机会观察：优先寻找能替代人工、提高成交率、降低运营成本并可量化ROI的AI应用。",
        "风险提示：仅有技术演示、缺乏客户付费和真实工作流嵌入的产品淘汰速度会很快。",
        "为什么重要：AI正在从概念阶段进入收入与成本验证阶段，商业价值开始分化。",
    ),
    "电商": (
        "机会观察：关注跨境渠道、履约、库存周转、支付与提高复购率的工具和服务。",
        "风险提示：平台规则、广告成本、关税和物流费用变化可能迅速压缩利润。",
        "为什么重要：电商利润越来越由流量成本、履约效率与库存速度共同决定。",
    ),
    "制造业": (
        "机会观察：关注自动化、设备升级、降本工艺、近岸制造与关键零部件供应商。",
        "风险提示：制造业资本投入高，若订单和产能利用率低于预期，回收周期会明显拉长。",
        "为什么重要：制造端的扩产与降本会直接形成设备、材料、零部件和服务订单。",
    ),
    "贵金属": (
        "机会观察：关注黄金、白银、铂金的供需、回收、精炼、零售溢价与相关产业链。",
        "风险提示：贵金属受利率、美元、地缘风险与资金流影响，短期波动可能放大。",
        "为什么重要：贵金属既是金融资产也是工业与消费原料，价格变化会同时影响投资与实体需求。",
    ),
    "能源与资源": (
        "机会观察：关注能源、矿产、航运、精炼、回收与替代供应链中的价格和订单变化。",
        "风险提示：资源价格容易受地缘政治、库存、政策和产量变化影响，波动通常较大。",
        "为什么重要：能源与原材料是制造、运输和算力的底层成本，价格变化会向多个行业传导。",
    ),
    "新兴赛道": (
        "机会观察：关注商业化速度加快、订单开始形成并获得长期资本支持的新技术产业。",
        "风险提示：新兴产业估值与技术路线变化快，需重点验证客户、成本和规模化能力。",
        "为什么重要：新赛道在早期常由技术突破转成资本开支，随后形成供应链与服务机会。",
    ),
}

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
    return re.sub(r"\s+", " ", text).strip()


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
    params = urlencode({"q": text[:450], "langpair": "en|zh-CN"})
    raw = request_bytes("https://api.mymemory.translated.net/get?" + params, timeout=20)
    data = json.loads(raw.decode("utf-8"))
    return (data.get("responseData", {}).get("translatedText") or "").strip()


def translate_zh(text: str) -> str:
    text = strip_html(text)
    if not text:
        return ""
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
            link_el = entry.find("a:link", ns)
            out.append(
                (
                    (entry.findtext("a:title", default="", namespaces=ns) or "").strip(),
                    (link_el.attrib.get("href", "") if link_el is not None else "").strip(),
                    (entry.findtext("a:summary", default="", namespaces=ns) or "").strip(),
                    (entry.findtext("a:updated", default="", namespaces=ns) or "").strip(),
                    default_source,
                )
            )
    return out


def parse_date(pub_raw: str) -> datetime:
    if not pub_raw:
        return datetime.now(timezone.utc)
    try:
        dt = parsedate_to_datetime(pub_raw)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        try:
            dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)


def build_candidates():
    now = datetime.now(timezone.utc)
    collected = []
    seen = set()

    for feed in FEEDS:
        try:
            xml_bytes = request_bytes(feed["url"])
        except Exception as exc:
            print(f"[WARN] Failed to fetch {feed['source']}: {exc}")
            continue

        for title, link, desc, pub_raw, source in parse_items(xml_bytes, feed["source"]):
            title = strip_html(title)
            desc = strip_html(desc)
            link = link.strip()
            if not title or not link:
                continue

            key = re.sub(r"\W+", " ", title.lower()).strip()
            if key in seen:
                continue
            seen.add(key)

            category, keyword_score = detect_category(f"{title} {desc}")
            if not category:
                continue

            pub_dt = parse_date(pub_raw)
            age_hours = max(0, (now - pub_dt.astimezone(timezone.utc)).total_seconds() / 3600)
            freshness = max(0, 72 - age_hours) / 12
            relevance = keyword_score * 4 + CATEGORY_PRIORITY[category] + freshness

            collected.append(
                {
                    "original_title": title,
                    "original_desc": desc,
                    "category": category,
                    "source_name": source,
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
    opportunity, risk, why = CATEGORY_COPY[category]
    stable_id = int(hashlib.md5(candidate["source_url"].encode("utf-8")).hexdigest()[:8], 16)

    return {
        "id": stable_id,
        "title": title_zh,
        "category": category,
        "date": candidate["date"],
        "summary": f"【{category}】{desc_zh}",
        "opportunity": opportunity,
        "content": f"新闻要点：{desc_zh}",
        "source_name": candidate["source_name"],
        "source_url": candidate["source_url"],
        "risk": risk,
        "why_it_matters": why,
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

    with open("news-data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"news-data.json updated with {len(payload)} Chinese opportunity-focused items.")


if __name__ == "__main__":
    main()
