# -*- coding: utf-8 -*-
"""在抽屉版基础上：①五板块置顶（公告后第一个，默认展开）
②五的每条内容后加二级抽屉藏约200字详细总结。"""
import json
import re

SRC = "sample_20261119_drawer.html"
DST = "sample_20261119_v3.html"
DETAILS = json.load(open("details_sec5.json", encoding="utf-8"))
detail_by_key = {d["key"]: d["detail"] for d in DETAILS}

html = open(SRC, encoding="utf-8").read()

# ---- 1. 切出顶层 details 块（此时还没有嵌套）----
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

# ---- 2. 排序：公告(5f6368) → 五 → 二 → 三 → 四 → 七；只有公告和五默认展开 ----
def rank(b):
    t = title_of(b)
    if "公告" in t:
        return 0
    if t.startswith("五"):
        return 1
    if t.startswith("二"):
        return 2
    if t.startswith("三"):
        return 3
    if t.startswith("四"):
        return 4
    return 5

ordered = sorted(blocks, key=rank)

# ---- 3. 五板块注入二级抽屉 ----
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

for i, b in enumerate(ordered):
    if not title_of(b).startswith("五"):
        continue
    matched = 0
    for html_title, key in SEC5_MAP.items():
        detail = detail_by_key.get(key)
        if detail is None:
            raise SystemExit("JSON 缺 key: %s" % key)
        # 在该块内找到对应条目 <p>，在其 </p> 后插入二级抽屉
        pat = re.compile(r"(<p style=\"margin:8px 0\"><b>%s</b>.*?</p>)" % re.escape(html_title), re.S)
        m = pat.search(b)
        if not m:
            raise SystemExit("五板块找不到条目: %s" % html_title)
        nested = (
            m.group(1)
            + '<details style="margin:2px 0 8px"><summary style="color:#1a73e8;font-size:13px;cursor:pointer">📖 展开看详细总结（约200字）</summary>'
            + '<div style="background:#f5f7fa;border-left:3px solid #1a73e8;padding:10px 12px;border-radius:4px;color:#444;font-size:13px;line-height:1.6">'
            + detail + "</div></details>"
        )
        b = b[:m.start()] + nested + b[m.end():]
        matched += 1
    ordered[i] = b
    print("五板块注入二级抽屉: %d 条" % matched)
    break

# ---- 4. 只让公告和五默认展开 ----
final = []
for b in ordered:
    t = title_of(b)
    keep_open = ("公告" in t) or t.startswith("五")
    final.append(set_open(b, keep_open))

# 顶部提示更新
out_html = "".join(final)
out_html = out_html.replace(
    "已把你常看的板块放在最前并展开。",
    "「五、调研会议纪要」已置顶展开，每条下有二级抽屉，点「📖 展开看详细总结」可看约200字详解。",
)
out_html = out_html.replace("正式版每晚 21:05 起每日自动发送", "第三版样例（五置顶+200字详解二级抽屉）")

open(DST, "w", encoding="utf-8").write(out_html)
print("生成:", DST, len(out_html), "字符")
for b in final:
    t = title_of(b)
    print(" -", ("[展开] " if b.startswith("<details open") else "[收起] ") + t[:30])
