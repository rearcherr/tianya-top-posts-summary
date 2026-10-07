import json, html, re
from collections import Counter, defaultdict

items = json.load(open(r"C:\Users\rearcher\WorkBuddy\2026-10-07-19-03-52\tianya\output\items.json", encoding="utf-8"))

# strip leading "N. " from titles
for it in items:
    it["title"] = re.sub(r"^\d+\.\s*", "", it["title"])
    it["num"] = re.match(r"^(\d+)\.", items[items.index(it)]["title"]) if False else None

# assign order numbers
for i, it in enumerate(items, 1):
    m = re.match(r"^(\d+)\.\s*(.*)$", items[i-1]["title"])
    it["no"] = i
    it["clean"] = m.group(2) if m else it["title"]

E = html.escape
CAT_ORDER = ["房地产/楼市", "宏观经济/金融", "股市/投资", "社会观察/阶层", "历史/军事",
             "国际关系/地缘", "政治/体制", "商业/营销", "职场/个人成长", "哲学/方法论",
             "玄学/命理/中医", "灵异/悬疑", "文学/小说", "其他"]
cnt = Counter(i["cat"] for i in items)

# group
groups = defaultdict(list)
for it in items:
    groups[it["cat"]].append(it)

def card(it):
    pts = "".join(f'<li>{E(p)}</li>' for p in it["pts"])
    ev = f'<div class="ev"><b>关键论据</b>{E(it["ev"])}</div>' if it["ev"] else ""
    q = f'<div class="q">{E(it["quote"])}</div>' if it["quote"] else ""
    cr = f'<div class="cr"><b>立场</b>{E(it["cred"])}</div>' if it["cred"] else ""
    return f'''<article class="card" data-cat="{E(it["cat"])}" id="p{it["no"]}">
<header><span class="no">{it["no"]}</span><h3>{E(it["clean"])}</h3><span class="tag">{E(it["cat"])}</span></header>
<p class="core">{E(it["core"])}</p>
<ol>{pts}</ol>
{ev}{q}{cr}
</article>'''

sections = []
for c in CAT_ORDER:
    if c not in groups:
        continue
    lst = groups[c]
    sections.append(f'<section><h2 class="cat">{E(c)} <em>{len(lst)} 篇</em></h2>' + "".join(card(i) for i in lst) + "</section>")

nav = "".join(f'<button data-f="{E(c)}">{E(c)} <span>{cnt[c]}</span></button>' for c in CAT_ORDER if c in groups)

html_doc = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>天涯顶级神帖 · 逐篇观点总结</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;background:#f4f5f7;color:#1c1e21;line-height:1.75;padding-bottom:60px}}
header.top{{background:linear-gradient(135deg,#1f2937,#374151);color:#fff;padding:38px 24px;text-align:center}}
header.top h1{{font-size:26px;font-weight:700;letter-spacing:.5px}}
header.top p{{opacity:.75;font-size:14px;margin-top:8px}}
.wrap{{max-width:980px;margin:0 auto;padding:0 16px}}
nav{{position:sticky;top:0;background:#fff;border-bottom:1px solid #e3e5e8;padding:10px 16px;display:flex;gap:7px;flex-wrap:wrap;z-index:10;box-shadow:0 1px 4px rgba(0,0,0,.05)}}
nav button{{border:1px solid #d3d6da;background:#fff;border-radius:16px;padding:5px 13px;font-size:13px;cursor:pointer;color:#4a4f55;font-family:inherit;transition:.15s}}
nav button:hover{{background:#f0f2f5}}
nav button.on{{background:#2563eb;color:#fff;border-color:#2563eb}}
nav button span{{opacity:.6;font-size:11px}}
section{{margin-top:34px}}
h2.cat{{font-size:18px;font-weight:700;color:#111;padding:0 0 10px;border-bottom:2px solid #e3e5e8;margin-bottom:16px;display:flex;align-items:baseline;gap:9px}}
h2.cat em{{font-style:normal;font-size:12px;color:#6b7280;font-weight:500}}
.card{{background:#fff;border:1px solid #e3e5e8;border-radius:9px;padding:18px 20px;margin-bottom:13px;scroll-margin-top:64px}}
.card header{{display:flex;align-items:flex-start;gap:10px;margin-bottom:11px;flex-wrap:wrap}}
.card .no{{background:#f0f2f5;color:#6b7280;border-radius:5px;padding:2px 7px;font-size:12px;font-weight:600;flex-shrink:0}}
.card h3{{font-size:16px;font-weight:650;flex:1;min-width:200px;line-height:1.5;color:#111827}}
.card .tag{{background:#eef2ff;color:#4338ca;border-radius:4px;padding:2px 8px;font-size:11px;white-space:nowrap}}
.core{{background:#f9fafb;border-left:3px solid #2563eb;padding:10px 13px;border-radius:0 5px 5px 0;font-size:14.5px;color:#1f2937;margin-bottom:11px}}
.card ol{{margin:0 0 11px;padding-left:21px}}
.card ol li{{font-size:14px;margin-bottom:6px;color:#374151}}
.ev,.cr{{font-size:13px;color:#4b5563;margin-top:8px;padding:8px 11px;background:#fafafa;border-radius:5px}}
.ev b,.cr b{{color:#111;margin-right:7px;font-weight:600}}
.q{{margin-top:10px;padding:9px 13px;background:#fffbeb;border-left:3px solid #f59e0b;color:#78350f;font-size:13.5px;border-radius:0 5px 5px 0;font-style:italic}}
.hide{{display:none}}
footer{{text-align:center;color:#9ca3af;font-size:13px;margin-top:44px}}
</style></head><body>
<header class="top"><h1>天涯顶级神帖 · 逐篇观点总结</h1>
<p>共 {len(items)} 篇 · 源自「天涯顶级神帖230篇」资料包 · 每篇含核心观点、论据、金句与立场评估</p></header>
<nav id="nav"><button class="on" data-f="all">全部 {len(items)}</button>{nav}</nav>
<div class="wrap" id="wrap">{"".join(sections)}
<footer>由 WorkBuddy 自动提取与整理 · 观点均转述自原作者，不代表整理者立场</footer>
</div>
<script>
const nav=document.getElementById('nav'),cards=[...document.querySelectorAll('.card')],secs=[...document.querySelectorAll('section')];
nav.addEventListener('click',e=>{{
  const b=e.target.closest('button'); if(!b)return;
  nav.querySelectorAll('button').forEach(x=>x.classList.remove('on')); b.classList.add('on');
  const f=b.dataset.f;
  secs.forEach(s=>{{
    const ok = f==='all'||s.querySelector('h2.cat').textContent.includes(f);
    s.classList.toggle('hide',!ok);
  }});
  window.scrollTo({{top:0,behavior:'smooth'}});
}});
</script></body></html>'''

out = r"C:\Users\rearcher\WorkBuddy\2026-10-07-19-03-52\tianya\output\天涯神帖_逐篇观点总结.html"
open(out, "w", encoding="utf-8").write(html_doc)
print("written", out, len(html_doc))

# index markdown
idx = ["# 天涯神帖 · 分类索引\n"]
for c in CAT_ORDER:
    if c not in groups:
        continue
    idx.append(f"\n## {c}（{len(groups[c])} 篇）\n")
    for it in groups[c]:
        idx.append(f"- {it['no']}. **{it['clean']}** —— {it['core'][:70]}")
open(r"C:\Users\rearcher\WorkBuddy\2026-10-07-19-03-52\tianya\output\分类索引.md", "w", encoding="utf-8").write("\n".join(idx))
print("index done")
