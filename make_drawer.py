# -*- coding: utf-8 -*-
"""把样例 HTML 的各板块包成 <details> 抽屉，并把第七板块提前。"""
import re

SRC = "sample_20261119.html"
DST = "sample_20261119_drawer.html"

html = open(SRC, encoding="utf-8").read()

# 头部到第一个 h3 之前 = header；尾部说明从 <p style="color:#888 开始
first_h3 = html.find("<h3 ")
tail_start = html.find('<p style="color:#888')
header = html[:first_h3]
footer = html[tail_start:]
body = html[first_h3:tail_start]

# 按 h3 切块
parts = re.split(r"(?=<h3 )", body)
sections = []
for p in parts:
    if not p.strip():
        continue
    m = re.search(r"<h3 [^>]*>(.*?)</h3>", p, re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "?"
    sections.append((title, p.strip()))

# 排序：公告(5f6368) → 七 → 其余按原顺序
def rank(sec):
    t, p = sec
    if "#5f6368" in p:
        return 0
    if t.startswith("七"):
        return 1
    return 2

ordered = sorted(sections, key=rank)

out = [header]
for title, p in ordered:
    # 公告和七默认展开，其余收起
    open_attr = " open" if ("#5f6368" in p or title.startswith("七")) else ""
    out.append('<details%s style="margin:6px 0">' % open_attr)
    out.append('<summary style="background:#1a73e8;color:#fff;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">▼ %s（点击展开/收起）</summary>' % title)
    # 去掉原来的 h3 行，保留内容
    content = re.sub(r"^<h3 [^>]*>.*?</h3>", "", p, count=1, flags=re.S)
    out.append(content)
    out.append("</details>")
out.append(footer)

out_html = "".join(out)

# 字号调整：标题 17px，梗概正文 20px（比标题略大）
out_html = out_html.replace(
    '<p style="margin:8px 0"><b>',
    '<p style="margin:10px 0"><b style="font-size:17px;color:#222">',
)
out_html = re.sub(
    r"</b><br>(.*?)<br><span style=\"color:#999",
    r'</b><br><span style="font-size:20px;color:#333;line-height:1.6">\1</span><br><span style="color:#999',
    out_html,
)

# 顶部提示加一句
out_html = out_html.replace(
    "读全文：ima App → 进库 → 搜标题。",
    "读全文：ima App → 进库 → 搜标题。<b>各栏目标题可点击展开/收起</b>，已把你常看的板块放在最前并展开。",
)

open(DST, "w", encoding="utf-8").write(out_html)
print("生成:", DST, len(out_html), "字符")
for t, _ in ordered:
    print(" -", t)
