# -*- coding: utf-8 -*-
"""第四版：
①二级抽屉推广到全部板块（二三四五七 + 四红宝书）
②二级抽屉详解字号 14px（比上级正文略大）
③三板块内部：脱水研报/调研日报/评级日报 3 条置顶，且详解为长版完整总结
④排序：公告 → 五 → 三 → 二 → 四 → 七；公告与五默认展开"""
import json
import re

SRC = "sample_20261119_drawer.html"
DST = "sample_20261119_v4.html"

detail_by_key = {}
for f in ["details_sec2.json", "details_sec3.json", "details_sec47.json"]:
    for d in json.load(open(f, encoding="utf-8")):
        detail_by_key[d["key"]] = d["detail"]

# 五板块 JSON key 是短标题，需映射回 HTML 标题（沿用 v3 的 SEC5_MAP）
SEC5_MAP = {
    "储能的近景与远忧（专家会）": "储能的近景与远忧",
    "产业面面观：商品解读": "产业面面观20261118",
    "比特币什么时候会再次上涨？": "比特币什么时候会再次上涨",
    "华为磁电存储核心逻辑": "HW MED磁电存储",
    "CXO&上游26Q3业绩综述": "CXO&上游26Q3",
    "【华泰】风波之后，英伟达交出怎样的答卷": "风波之后，NV交出怎样的答卷",
    "【点金香江】港股通ETF与中资资管国际化": "港股通ETF与中资资管",
    "醋酸酯——大宗商品热点解读": "干胶、醋酸酯",
    "对话慈星股份：机器人如何触摸真实世界": "对话慈星股份与普朗多",
    "从常青贷款看银行的默默担当": "从常青贷款看",
    "东吴证券2027年A股年度展望": "大浪与潜流",
    "君汉胜者-宏观策略介绍": "君汉胜者-宏观策略",
    "科技智汇周谈（英伟达/算力/AI/IDC/半导体）": "科技智汇周谈",
    "甲醇与氯碱产业链深度分析": "甲醇与氯碱",
    "光纤产业投资观点": "光纤产业投资观点",
    "特高压密集推进，配网提升可靠性": "特高压密集推进",
    "谁来稳定负债端？（债市）": "谁来稳定负债端",
    "全球宏观变局，红利逻辑深化": "全球宏观变局",
    "物理AI每日一问：Fable 5.2具身智能泛化": "Fable 52的具身智能",
    "每周策略：银行股批量新高，避风港怎么抓": "银行股批量新高",
    "中芯国际+华虹三季报解读": "中芯国际+华虹宏力三季报",
    "中外头部大模型商业化与财报对比": "中外头部大模型",
    "再推海康威视、网宿科技": "再推海康威视",
    "英伟达发布财报，业绩创纪录": "英伟达发布财报，业绩创纪录",
    "物理AI提速哪些是真机会": "物理AI提速哪些是真机会",
    "通信行业深度合集（中天科技）": "通信行业近期深度报告",
    "特斯拉Optimus物理AI&SpaceX太空算力": "特斯拉Optimus物理AI",
}
_sec5_raw = {d["key"]: d["detail"] for d in json.load(open("details_sec5.json", encoding="utf-8"))}
for html_title, key in SEC5_MAP.items():
    detail_by_key[html_title] = _sec5_raw[key]

# 三板块内部置顶的特殊条目（长版完整总结）
SPECIAL_3 = {"1118脱水研报", "1118调研日报", "1118评级日报"}

html = open(SRC, encoding="utf-8").read()
blocks = re.findall(r"<details[^>]*>.*?</details>", html, re.S)
assert len(blocks) == 6, "顶层块数不对: %d" % len(blocks)

def title_of(b):
    m = re.search(r"<summary[^>]*>(.*?)</summary>", b, re.S)
    t = re.sub(r"<[^>]+>", "", m.group(1)) if m else "?"
    return t.replace("▼", "").strip()

def is_open(b):
    return b.startswith("<details open")

def set_open(b, val=True):
    b = re.sub(r"^<details( open)?", "<details open" if val else "<details", b)
    return b

# ---- 排序：公告 → 五 → 三 → 二 → 四 → 七 ----
def rank(b):
    t = title_of(b)
    if "公告" in t:
        return 0
    if t.startswith("五"):
        return 1
    if t.startswith("三"):
        return 2
    if t.startswith("二"):
        return 3
    if t.startswith("四"):
        return 4
    return 5

ordered = sorted(blocks, key=rank)

# ---- 三板块内部排序：特殊 3 条提到最上面 ----
for i, b in enumerate(ordered):
    if title_of(b).startswith("三"):
        # 条目是若干 <p ...><b>标题</b>...</p>（可能后跟二级抽屉，切前还没有）
        paras = re.findall(r"<p style=\"margin:10px 0\"><b style=\"[^\"]*\">.*?</b>.*?</p>", b, re.S)
        head = b[: b.index('<p style="margin:10px 0"><b')]
        def para_title(p):
            m = re.match(r"<p style=\"margin:10px 0\"><b style=\"[^\"]*\">(.*?)</b>", p, re.S)
            return m.group(1)
        special = [p for p in paras if para_title(p) in SPECIAL_3]
        normal = [p for p in paras if para_title(p) not in SPECIAL_3]
        body = "".join(special) + "".join(normal)
        tail = b[b.rindex("</p>") + 4:]
        ordered[i] = head + body + tail
        print("三板块重排: 特殊 %d 条置顶 / 普通 %d 条" % (len(special), len(normal)))
        break

# ---- 全板块注入二级抽屉 ----
total_injected = 0
total_missing = []
for i, b in enumerate(ordered):
    t = title_of(b)
    if "公告" in t:
        continue  # 公告 1 条不用详解
    # 提取该块内所有条目 <p>
    pat = re.compile(r"(<p style=\"margin:10px 0\"><b style=\"[^\"]*\">(.*?)</b>.*?</p>)", re.S)
    out = b
    offset = 0
    injected = 0
    for m in pat.finditer(b):
        para, key = m.group(1), m.group(2)
        detail = detail_by_key.get(key)
        if detail is None:
            total_missing.append((t[:12], key))
            continue
        if key in SPECIAL_3:
            summary_txt = "📖 展开看完整总结（详版）"
            box_style = "background:#fff8ee;border-left:3px solid #e6a23c"
        else:
            summary_txt = "📖 展开看详细总结（约200字）"
            box_style = "background:#f5f7fa;border-left:3px solid #1a73e8"
        nested = (
            para
            + '<details style="margin:2px 0 8px"><summary style="color:#1a73e8;font-size:15px;cursor:pointer">'
            + summary_txt + "</summary>"
            + '<div style="' + box_style + ';padding:12px 14px;border-radius:4px;color:#333;font-size:20px;line-height:1.7">'
            + detail + "</div></details>"
        )
        s = m.start() + offset
        e = m.end() + offset
        out = out[:s] + nested + out[e:]
        offset += len(nested) - len(para)
        injected += 1
    ordered[i] = out
    total_injected += injected
    print("%s: 注入 %d 条" % (t[:14], injected))

if total_missing:
    print("⚠️ 缺详解 %d 条:" % len(total_missing))
    for sec, key in total_missing:
        print("   [%s] %s" % (sec, key))

# ---- 只让公告和五默认展开 ----
final = []
for b in ordered:
    t = title_of(b)
    keep_open = ("公告" in t) or t.startswith("五")
    final.append(set_open(b, keep_open))

out_html = "".join(final)
out_html = out_html.replace(
    "「五、调研会议纪要」已置顶展开，每条下有二级抽屉，点「📖 展开看详细总结」可看约200字详解。",
    "全部板块每条都有二级抽屉，点「📖 展开看详细总结」看约200字详解；第三部分的脱水研报/调研日报/评级日报置顶且有更完整的详版总结。",
)
out_html = out_html.replace(
    "已把你常看的板块放在最前并展开。",
    "「五、调研会议纪要」已置顶展开，全部板块支持二级抽屉。",
)
out_html = out_html.replace("正式版每晚 21:05 起每日自动发送", "第五版样例（全板块二级抽屉+标题17px/正文20px+三板块特殊置顶）")

open(DST, "w", encoding="utf-8").write(out_html)
print("生成:", DST, len(out_html), "字符")
for b in final:
    t = title_of(b)
    print(" -", ("[展开] " if b.startswith("<details open") else "[收起] ") + t[:30])
