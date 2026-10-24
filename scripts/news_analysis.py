"""Conservative, auditable event rules. No category-based business claims.

Rules suggest checks, never establish ROI, demand, causality or local applicability.
Evidence is an exact source excerpt; matching is deliberately narrower than categorisation.
"""
import re
from datetime import datetime
from urllib.parse import urlparse

# Exact-text editorial translations: changes in source wording invalidate the override.
REVIEWED_TRANSLATIONS = {
    "Don't fall for this - how to protect yourself from AI scams": "警惕AI诈骗：如何保护自己",
    'Trading standards officers say AI is "super-charging" existing scams through clones and fake websites.':
        "英国交易标准执法人员表示，AI正通过克隆仿冒和虚假网站，让既有诈骗手法更具欺骗性。",
    "Microsoft pulls out of UK's largest AI data centre": "微软退出英国最大AI数据中心项目",
    "Tech firm Nscale says it is still committed to building the site in Essex.":
        "科技公司Nscale表示，仍计划在英国埃塞克斯建设该数据中心。",
    "Turning the tides: Could hidden sea power energise our coastal towns?":
        "潮汐能能否为沿海城镇提供新的电力来源？",
    "Engineer David Mummery has developed a tidal energy generator that he says can change lives for people living in coastal communities.":
        "工程师David Mummery开发了一种潮汐能发电机；他表示，这项设备有望改变沿海社区居民的生活。",
}


def reviewed_translation(text):
    return REVIEWED_TRANSLATIONS.get(text)


# Each group must occur within the SAME title or sentence. Negation triggers abstention.
RULES = [
    ("ai_impersonation", [r"\bAI\b|artificial intelligence", r"\bscams?\b|\bfraud\b", r"clon|fake websites|impersonat"],
     "验证动作（经营推断）：检查客户转账、供应商收款账户变更及语音指令的复核流程；用已登记号码回拨确认。本文没有证明反诈产品存在付费需求。",
     "风险边界：摘要提到克隆仿冒和虚假网站；不能仅凭声音或网页外观确认交易对象，也不能据此估算本企业损失概率。",
     "经营关联（推断）：若企业接受远程付款指令，这类仿冒手段值得纳入收款及付款审核；报道没有证明AI能降低本企业成本。"),
    ("data_centre_withdrawal", [r"data cent(?:re|er)", r"pulls? out|withdraws?|withdrawal|abandons?"],
     "验证动作（经营推断）：若正采购相关云服务或参与该项目供货，向合同对方核对建设进度、交付承诺与替代方案；尚不能认定出现新的供应订单。",
     "风险边界：退出项目不等于整个项目取消；需另查开发方融资、剩余合作方和履约安排，不能推断全球算力需求下降。",
     "经营关联（推断）：这条消息涉及特定数据中心项目的参与方变化；只有依赖该项目交付的采购或供应计划需要据此复核，不能直接推导本地电价或AI服务价格。"),
    ("tidal_prototype", [r"tidal", r"generator", r"developed|prototype|trial"],
     "验证动作（经营推断）：若考虑沿海供电项目，先索取发电曲线、维护记录、并网条件及单位发电成本；现有摘要不足以支持购买或投资。",
     "风险边界：改善社区生活是研发者的说法；摘要未提供独立测试、商业订单或维护成本，不能把技术原型当成已验证的商业方案。",
     "经营关联（推断）：这是供电技术线索；对工厂是否有价值仍取决于场址、稳定性和全周期成本，不能据此认定用电费用会下降。"),
    ("metal_price_change", [r"\bgold\b|\bsilver\b|\bplatinum\b|\bpalladium\b", r"\bprice\b|\bprices\b", r"rise|risen|rising|surge|fall|drop|declin"],
     "验证动作（经营推断）：核对报道所指金属、报价币种和时点，再用本厂实际库存、未锁价订单与供应商报价检查敞口；不直接给出囤货建议。",
     "风险边界：国际价格变动不等于本地到厂成本同幅变化；汇率、成色、溢价及加工费需另核，不能由单次涨跌预测后市。",
     "经营关联（推断）：若企业采购或回收报道中的金属，报价有效期与未锁价库存值得复核；实际毛利影响尚需本厂数据。"),
    ("factory_automation_trial", [r"factory|manufactur|industrial", r"robot|automat", r"pilot|trial|test"],
     "验证动作（经营推断）：若工序相近，可要求供应商用本厂样件测试节拍、良率、换型与人工复核时间；先验证再估算回收周期。",
     "风险边界：试验结果未必能迁移到本厂的材料、公差及订单批量；摘要不能证明设备已量产或可以替代全部人工。",
     "经营关联（推断）：该试验可作为工序改造的检索线索；经营价值取决于本厂瓶颈和整线成本，暂不能承诺节省金额。"),
    ("tariff_change", [r"tariff|import dut", r"announc|impos|rais|cut|reduc"],
     "验证动作（经营推断）：先查官方税则、生效日、原产地和商品编码，再对照实际采购或出口清单；尚不能认定本企业属于受益方。",
     "风险边界：公告、提议与生效措施可能不同；摘要不足以确认豁免、适用范围或最终税负，不据此直接改价。",
     "经营关联（推断）：若供应链落入适用范围，到岸成本或报价条件可能需要重算；须以官方文本和实际贸易路径核实。"),
]


def analyze(candidate, title_zh):
    evidence = []
    for field in ("original_title", "original_desc"):
        text = candidate.get(field, "")
        if text:
            evidence.append({"id": f"E{len(evidence)+1}", "field": field, "quote": text,
                             "source_url": candidate["source_url"]})
    matched = None
    for rule in RULES:
        for ev in evidence:
            for sentence in re.split(r"(?<=[.!?])\s+", ev["quote"]):
                if re.search(r"\b(?:not|never|denies|denied|no evidence|rumou?r|may|might|could)\b", sentence, re.I):
                    continue
                if all(re.search(pattern, sentence, re.I) for pattern in rule[1]):
                    matched = (rule, ev["id"])
                    break
            if matched:
                break
        if matched:
            break
    anchor = f"围绕《{title_zh}》："
    if matched:
        rule, evidence_id = matched
        opportunity, risk, why = (anchor + text for text in rule[2:])
        rule_id, status = rule[0], "limited_rss_evidence"
        references = [evidence_id]
    else:
        rule_id, status = None, "insufficient_evidence"
        references = [e["id"] for e in evidence]
        opportunity = anchor + "证据不足：当前标题和摘要未匹配到可审计的经营事件规则，暂不提出获客、投资或扩产机会。需先核对全文及事件适用范围。"
        risk = anchor + "判断限制：现有材料不能区分完整事实、预测与评论；不据此估算市场需求、收益或本企业成本变化。"
        why = anchor + "重要性待确认：还需明确具体影响对象、发生时间及可验证变化，当前不认定与本企业经营直接相关。"
    return {"opportunity": opportunity, "risk": risk, "why_it_matters": why,
            "metadata": {"version": "event-rules-v1", "status": status, "rule_id": rule_id,
                         "evidence_scope": "rss_title_and_description_only",
                         "source_verification": "publisher_feed_not_independently_verified",
                         "evidence": evidence,
                         "field_evidence": {key: references for key in
                                            ("opportunity", "risk", "why_it_matters")}}}


def validate_payload(payload):
    if not isinstance(payload, list) or len(payload) < 3:
        raise ValueError("Need at least 3 valid items; preserve existing data")
    seen, triples = set(), set()
    for item in payload:
        if item["id"] in seen:
            raise ValueError("Duplicate article ID")
        seen.add(item["id"])
        url = urlparse(item["source_url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("Invalid source URL")
        published = datetime.fromisoformat(item["published_at"])
        if published.tzinfo is None or published.date().isoformat() != item["date"]:
            raise ValueError("Publication date must come from timestamp")
        for field in ("title", "summary", "content", "opportunity", "risk", "why_it_matters"):
            if not re.search(r"[\u3400-\u9fff]", item.get(field, "")):
                raise ValueError(f"Missing Chinese {field}")
        triple = tuple(item[k] for k in ("opportunity", "risk", "why_it_matters"))
        if triple in triples:
            raise ValueError("Duplicate analysis")
        triples.add(triple)
        meta = item["analysis"]
        evidence = {e["id"]: e for e in meta["evidence"]}
        if not evidence:
            raise ValueError("Missing source evidence")
        for e in evidence.values():
            if e["quote"] != item[e["field"]] or e["source_url"] != item["source_url"]:
                raise ValueError("Evidence differs from source")
        for field in ("opportunity", "risk", "why_it_matters"):
            refs = meta["field_evidence"].get(field, [])
            if not refs or any(ref not in evidence for ref in refs):
                raise ValueError("Missing field evidence")
