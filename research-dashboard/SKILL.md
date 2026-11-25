---
name: research-dashboard
description: 把一个研报目录（多篇 .md 长文）压缩成单文件 HTML 投研看板，5 分钟可重建产业链心智地图。当用户说"做投研看板/产业链看板/把这堆研报整理一下"或类似请求，且 Research Report/ 下有 .md 研报合集时激活。零依赖单 HTML，含 A 股行情快照、公司速查矩阵（含 ROE 占位 + 一键刷新行情按钮）、产业链分层图、时间轴、风险卡、🎯 serenity 卡口下钻（默认全部启用）。
---

# 投研看板生成 Skill

把 `Research Report/<主题>/` 下的多篇 .md 研报，转成一个**单文件 HTML 交互看板**，作为这个产业链的"5 分钟速查地图"。**默认 6 Tab + 全部 9 项扩展**（含 serenity 卡口下钻 + 一键刷新行情按钮）。

## Skill 目录索引

```
research-dashboard/
├── SKILL.md                          ← 本文件，工作流主线 + 反模式 + 风险
└── references/                       ← 模板与样板（按需 Read，避免每次去翻别处）
    ├── prompts/
    │   ├── README.md                 ← 占位符列表 + sed 替换示例
    │   ├── p1_read.txt               ← R1 读完所有 .md
    │   ├── p2_cost.txt               ← R2 → 01_成本结构.md
    │   ├── p3_parts.txt              ← R3 → 02_零部件深度.md
    │   ├── p4_companies.txt          ← R4 → 03_标的画像.md
    │   ├── p5_whitepaper.txt         ← R5 → 04_行业白皮书.md
    │   └── p6_serenity.txt           ← R6（可选）→ 05_卡口下钻.md
    ├── serenity-methodology.md       ← serenity 方法论 ASCII 友好版（注入 R6 prompt 用）
    ├── data-schema.md                ← 8 个数据数组完整字段定义 + 自检脚本
    ├── tencent-fields.md             ← 腾讯 88 字段速查 + dynPe 字段坑 + _fetch.py 完整代码
    ├── css-themes.md                 ← 4 套黄金主题色 + 选色决策树 + 撞色规避
    └── dashboard-skeleton.html       ← 47KB 完整骨架（HTML+CSS+渲染JS，已通过 node --check）
```

**优先 Read references/ 而不是去翻 `Research Report/<其他主题>/` 下的样板看板**——所有可复用部分都已抽到这里。

## 核心分工：Claude Code 编排，Kimi CLI 执行

**默认两阶段流程**：

1. **Kimi CLI 阶段**：用 Kimi CLI 把全部原始研报压缩成 5 份**基础合成报告**（成本结构 / 零部件深度 / 标的画像 / 行业白皮书 / **卡口下钻**），放到 `_synthesis/`。**默认 5 份全产出**——卡口下钻（serenity 视角）已纳入标准工作流，不再可选。
2. **Claude Code 阶段**：基于合成报告（而非原始研报）抽取 8-10 个数据数组，渲染成 HTML 看板（默认 6 Tab，含 🎯 卡口下钻）

**为什么不直接读原始研报？**
- 原始研报常 30 万字以上，重复内容多、表述口径杂乱
- Kimi 长上下文擅长"多文档去重合并"，Claude Code 擅长"结构化输出+代码生成"
- 5 份 _synthesis 文件已是结构化的中间产物，再做数据抽取又快又准

## 已交付参考（黄金模板）
- `Research Report/固态变压器/SST投研看板.html` — 7 篇研报 → 27 家公司，蓝色主题（v1，5 Tab）
- `Research Report/固态变压器/SST投研看板2.0.html` — **85 篇研报 → 67 家公司，蓝青主题，6 Tab 含 🎯 卡口下钻**（v2，serenity 方法论参考实现）
- `Research Report/机器人/人形机器人投研看板.html` — 13 篇研报 → 55 家公司，紫橙主题（**直读研报版**）
- `Research Report/机器人/机器人产业链投研看板.html` — 同 13 篇研报 → 45 家公司，紫橙主题（**Kimi 提炼版**，推荐工作流参考）
- `Research Report/英伟达rubin/英伟达Rubin产业链投研看板.html` — 9 篇研报 → 59 家公司，绿色主题（含完整 7 个升级扩展 A-G）

**实施前先 Read 一个参考看板作为模板**——HTML 骨架、CSS 变量、JS 渲染函数已经稳定，新看板只需替换 5-8 个数据数组（OVERVIEW / CHAIN / COMPANIES / TIMELINE / RISKS [+ SCORES / GENERATIONS / ELASTICITY / SCENARIOS]）和主题色。**含卡口下钻则参考 SST 2.0**。

---

## 标准工作流（6 步）

### 步骤 1：Kimi CLI 提炼研报到 `_synthesis/`（多轮 session）

**前置检查**：先 `ls Research Report/<主题>/` 列出全部 .md 文件清单，再 `mkdir _synthesis`。

**Kimi CLI 调用方式**（Kimi Code CLI 2.x，统一走 kimi-delegate 的 `kimi_run.py`；脚本已内置 UTF-8 与路径探测）：

```bash
PY="C:/Users/Administrator/scoop/shims/python.exe"
# 用 kimi-delegate skill 自带的 kimi_run.py（Windows 宽字符 + UTF8 + 候选路径探测 + 会话 ID 抓取）
KIMI_RUN="C:/Users/Administrator/.claude/skills/kimi-delegate/scripts/kimi_run.py"
SF="<topic_dir>/_synthesis/.kimi_session"   # 会话文件；要重新开局就先删掉它

# 第 1 轮：让 Kimi 读完所有研报（仅确认，不输出）；新建会话并把 ID 写入 $SF
"$PY" "$KIMI_RUN" --session-file "$SF" -w "<topic_dir>" -f "<topic_dir>/_synthesis/_p1_read.txt"

# 第 2-N 轮：同一个会话文件续会话，产 _synthesis/01-05_*.md
"$PY" "$KIMI_RUN" --session-file "$SF" -w "<topic_dir>" -f "<topic_dir>/_synthesis/_p2_cost.txt" --timeout 2400
```

> Kimi 2.x 的会话 ID 只能由 Kimi 生成（`session_xxx`），**不能自编**；旧写法 `-S "<topic>-research-$(date +%s)"` 在 2.x 下会失败。`-S` 只用于续接一个已知的 `session_xxx`。

**6 份 prompt 模板已内置在 skill 自带的 `references/prompts/` 下** —— 默认 6 份全跑（含 R6 卡口下钻），把 6 个 .txt 复制到项目 `_synthesis/` 下，按主题改 `{{TOPIC}}` `{{N_FILES}}` `{{CHOKE_HINTS}}` 等占位符：

```bash
# Read references/prompts/README.md 看完整占位符列表与 sed 示例
cp "C:/Users/Administrator/.claude/skills/research-dashboard/references/prompts/"p*.txt \
   "Research Report/<主题>/_synthesis/"
# 然后 sed -i 's/{{TOPIC}}/<主题中文名>/g' _synthesis/_p*.txt
```

| 轮次 | 输出文件 | Prompt 文件 | 是否必需 |
|---|---|---|---|
| 1 | （无，仅确认）| `references/prompts/p1_read.txt` | 是 |
| 2 | `_synthesis/01_成本结构.md` | `references/prompts/p2_cost.txt` | 是 |
| 3 | `_synthesis/02_零部件深度.md` | `references/prompts/p3_parts.txt` | 是 |
| 4 | `_synthesis/03_标的画像.md` | `references/prompts/p4_companies.txt` | 是 |
| 5 | `_synthesis/04_行业白皮书.md` | `references/prompts/p5_whitepaper.txt` | 是 |
| 6 | `_synthesis/05_卡口下钻.md` | `references/prompts/p6_serenity.txt` | **是（默认必跑）** |

每轮使用 `run_in_background:true` 后**轮询输出文件落盘**——Kimi 实际写完文件后还会卡几分钟在 stdout 等待，看到目标 .md 大小达到预期（>15K）就 `TaskStop`，节省 5-10 分钟挂机时间。同一会话文件跨轮串行，不要并发调用同一会话。

**Kimi CLI 关键陷阱**：
- ❌ 直接 bash 调 `kimi -p "中文..."`：会因 `↔` `→` 等字符 GBK 崩溃 → 一律走 `kimi_run.py`（已内置 UTF-8）
- ❌ 自编会话 ID 传 `-S`，或每轮换会话：前者 2.x 直接失败，后者每轮重读研报浪费时间和 token → 全程同一个 `--session-file`
- ❌ Prompt 里夹复杂 Unicode 字符（如 `↔` `≈`）：可能反向喂回时再次崩溃，用 ASCII 替代
- ❌ 看到 kimi_run.py 报"超时"立即重试：先看目标文件是否已落盘，落了就当成功（Kimi 写完文件后会挂在 stdout，跟超时无关）
- ✅ 每轮 prompt 末尾明确 `写入文件 _synthesis/0X_xxx.md`，让 Kimi 直接落盘
- ✅ 期望产出 200-600 行 / 16-32K 单文件，超过说明 prompt 太宽，控制在 6-10 个小节内
- ✅ 长 prompt（>2KB）写到 UTF-8 文件再用 `kimi_run.py -f` 传，避免 argv 乱码

### 步骤 2：并行读 `_synthesis/`（Explore agent）

**不要再读原始研报**。并行启动 4 个 Explore agent，各管一个维度，输入源是 `_synthesis/` 下的 5 份文件：

| Agent | 输入文件 | 输出目标 |
|---|---|---|
| Agent A — 公司清单 | `03_标的画像.md` | COMPANIES 数组（按"环节×梯队"30-60 家，含代码/客户/看点/星级/**ROE 占位**） |
| Agent B — 行业全景 | `01_成本结构.md` + `04_行业白皮书.md` | OVERVIEW + TIMELINE + RISKS（一句话定位/数字徽章/4 阶段/3 大逻辑/6 风险点） |
| Agent C — 产业链分层 | `02_零部件深度.md` | CHAIN 数组（上中下游/各环节占比/国产化率/卡脖子环节） |
| Agent D — serenity 卡口 | `05_卡口下钻.md` | SERENITY_TREE / DEEP_CHOKES / CHOKE_PURGE / CONFIDENCE / SERENITY_DEMUR（默认必需） |

每个 agent 给明确的输出格式（Markdown 表格/列表）和字数上限（500-800 字），避免回灌过多文本占用主 context。

**Kimi 提炼后的优势**：4 个 Explore agent 不再面对 30 万字原文，而是面对 5 份 ~500 行的结构化中间产物，准确率显著提升、context 占用降低 80%。

### 步骤 3：四问确认（AskUserQuestion）

数据抽取完成后，用一次 AskUserQuestion 同时问 4 个问题（不要分多次问）：

1. **覆盖广度**：核心 ~25 / 全梯队 ~50+ / 精简 ~15（推荐选项打"推荐"）
2. **未上市/海外标的**：纳入但不拉行情 / 仅 A 股+港股 / 仅 A 股
3. **产业链分层主轴**：按价值量分（推荐）/ 按上中下游分 / 按技术象限分
4. **设计复用程度**：完全复用模板 / 复用结构调整视觉 / 重新设计

> 注意：「是否启用 serenity 卡口下钻」**已不再问**——默认必跑 R6 + 渲染第 6 Tab。如果用户明确说"快速版/不要 serenity"才删掉。

### 步骤 4：批量拉 A 股+港股+美股行情（一次性 Python 脚本）

写一个临时 `_fetch.py`，用腾讯财经 API 一次性拉所有 A/H/US 股行情 + 260 日 K 线（同时算 5/20 日累计涨跌 + 52 周高低位置），输出 `_snapshot.json`。**不要循环调用 a-stock-data skill 的多个端点**——单脚本批量拉效率高 100 倍。

**完整可复制的实现见 `references/tencent-fields.md`**，含：
- `tencent_quote(batch)` 批量行情（A/H/US 通用前缀）+ 字段索引表 + 脏数据过滤
- `kline_metrics(code, mkt)` 260 日 K 线 → (chg5d, chg20d, pos52w, pct52w)
- `val_tag(dyn_pe, pos)` 估值温度 hot/warm/fair/low + 文案
- 代码合理性校验（拿腾讯返回中文名前 2 字比对）

**关键约束**：
- **dynPe 字段**：直接用 `vals[39]` TTM PE 兜底（超过 1e6 视为脏数据置 null）。**不要用 `vals[62]`**——实测多为负或异常大值（详见 references/tencent-fields.md "重大踩坑"段）
- **ROE 字段拉取（推荐 Tushare Pro）**：腾讯接口不返回 ROE，COMPANIES 数据 schema 里**预留 `roe: null` 占位**。**首选 Tushare Pro `fina_indicator` 接口**：
  ```python
  import os, tushare as ts
  ts.set_token(os.environ["TUSHARE_TOKEN"])
  pro = ts.pro_api()
  for ts_code in ["300476.SZ", "002463.SZ", ...]:
      df = pro.fina_indicator(ts_code=ts_code, fields="ts_code,end_date,roe_waa,roe")
      if not df.empty:
          roe = df.iloc[0]["roe_waa"]  # 加权 ROE，最新一期
  ```
  A 股 100 家 ~30 秒搞定，无需子进程/xlsx 解析。**港股/美股需 5000 积分**（普通账号 `hk_fina_indicator` / `us_fina_indicator` 无权限），fallback 路径：用 `mx-finance-data` skill（`python {SKILL}/scripts/get_data.py --query "xxx 最近一期净资产收益率ROE(加权)"`，单次最多 5 实体，输出 xlsx 在 `cwd/miaoxiang/mx_finance_data/`）。
- **K 线必须拉 260 根**：算 52 周位置需要全年数据；早期版本拉 25 根的脚本必须迁移
- **港股前缀 `hk`**（如 02577 英诺赛科）；台股 / 德股 / 法股 / 瑞股标 `note` 不拉
- **单批 ≤ 25 只**：URL 太长会触发腾讯端截断
- **GBK 编码 + errors="replace"**：忽略奇怪字符，否则会偶发崩溃

### 步骤 5：基于骨架模板生成 HTML

**不要从零写，也不要 Read 别处的参考看板**——skill 已自带完整骨架：

```bash
# 1. 复制骨架 + 修改占位符
cp "C:/Users/Administrator/.claude/skills/research-dashboard/references/dashboard-skeleton.html" \
   "Research Report/<主题>/<主题>投研看板.html"

# 2. 替换占位符 {{TOPIC}} {{SUB_TITLE}} {{SNAPSHOT_DATE}} {{N_SYNTHESIS}} {{N_COMPANIES}}
# 3. 把生成好的数据数组直接覆盖文件里的 /* TODO */ 占位（OVERVIEW/CHAIN/COMPANIES 等）
# 4. 调主题色：改 :root 的 --accent / --accent2 / --warm
```

**关键：一次写到位，不要分多步打补丁**

写一个 `_make.py`（或直接写到看板文件），**一次性**完成：
1. 读 skeleton
2. 替换 5 个占位符（TOPIC/SUB_TITLE/SNAPSHOT_DATE/N_SYNTHESIS/N_COMPANIES）
3. **整体替换**每个 `const X = ...;` 为完整数据数组（OVERVIEW / CHAIN / COMPANIES / TIMELINE / RISKS / SCORES / GENERATIONS / ELASTICITY / SCENARIOS / SERENITY_TREE / DEEP_CHOKES / CHOKE_PURGE / CONFIDENCE / SERENITY_DEMUR / RACK_VALUE / SHIPMENT 等）
4. 调主题色（改 `:root` 的 `--accent`/`--accent2`）
5. 拉行情（_fetch.py 单独跑）→ 拉 ROE（Tushare 单独跑）→ 数据合并到 COMPANIES → 写入 HTML

**反模式（曾踩坑）**：基于"上次的看板"做 `replace` 打补丁加新字段。**replace 的 anchor 文案稍有不同（如 `负(亏损)` vs `负(亏损预期)`）就静默失败**——`const newVar = ...` 没注入，但模板里 `${newVar}` 已经写上 → `--check` 通过 → 浏览器打开渲染失败 Tab 空白。**正确做法：永远从 skeleton 重生成**，不在已生成看板上做增量 patch。

**配套参考（必读）**：
- **`references/data-schema.md`** —— 8 个数据数组（OVERVIEW/CHAIN/COMPANIES/TIMELINE/RISKS + SCORES/GENERATIONS/ELASTICITY/SCENARIOS）+ serenity 6 个数据结构（SERENITY_TREE/DEEP_CHOKES/CHOKE_PURGE 等）的**完整字段定义**与对齐自检脚本
- **`references/css-themes.md`** —— 4 套黄金主题色（SST 蓝青 / 机器人紫橙 / Rubin 绿 / serenity 紫色叠加）+ 选色决策树 + 撞色规避规则
- **`references/dashboard-skeleton.html`** —— 47KB 完整骨架（HTML+CSS+全部渲染 JS+所有事件绑定，已通过 `node --check`），数据数组占位待填

**Tab 结构**（默认 6 Tab，含卡口下钻）：
- **6 Tab（默认）**：概览 / 产业链 / 公司速查 / 时间轴 / 风险与逻辑 / 🎯 卡口下钻——骨架默认含全部 6 Tab，按 `references/data-schema.md` 第 10-15 节填 SERENITY_TREE / DEEP_CHOKES / CHOKE_PURGE / CONFIDENCE / SERENITY_DEMUR
- **5 Tab（极少用，需用户明确说"不要 serenity"）**：删除 nav 里 `<div class="tab serenity">`、删除 `PANELS.serenity`、删除 `renderSerenity` 函数

**Footer 注明数据源链路**：骨架已内置 `基于 Kimi CLI 提炼的 {{N_SYNTHESIS}} 份合成报告 · {{N_COMPANIES}} 家行情来自腾讯财经 · 单文件零依赖 · 数据截止 {{SNAPSHOT_DATE}}`，把占位符替换即可。

**公司速查 Tab 增强（默认启用）**：

公司速查 Tab 顶部 toolbar 含 **「🔄 刷新行情」按钮**，用户点击后浏览器直接 fetch 腾讯财经接口（CORS 已开放 `Access-Control-Allow-Origin: *`），刷新所有 A 股的：

- price（当前价）
- change（日涨跌幅 %）
- pe（动态 PE = TTM PE）
- chg5d / chg20d（5/20 日累计涨跌幅，从 K 线接口算）
- pos52w / pct52w（52 周高位距离 + 分位）
- valTag / valLbl（估值温度根据新 PE+pos52w 重新计算）

**实现要点**（已内置在 `dashboard-skeleton.html`）：
- `qt.gtimg.cn` 是 GBK 编码：用 `fetch().then(r => r.arrayBuffer()).then(buf => new TextDecoder('gbk').decode(buf))` 解码
- 单批 ≤ 20 只，多批并行 `Promise.all`
- K 线接口 `web.ifzq.gtimg.cn` 是 UTF-8，可用 `r.json()`
- 刷新过程中按钮显示 `🔄 刷新中…` 防重复点击
- 刷新完成后 toast 显示 "已更新 X 家 / Y 家"
- ROE 字段腾讯不返回，刷新时**不动 ROE**（保留原值或 null 占位），等待外部数据源接入

### 步骤 6：闭合检查 + JS 语法验证 + 浏览器打开

写完后必查三件事：

```bash
# 1. 闭合 + 数组数量
python -c "
c = open('xxx看板.html','r',encoding='utf-8').read()
print('script open/close:', c.count('<script>'), '/', c.count('</script>'))
print('html close:', c.count('</html>'))
print('COMPANIES count:', c.count('{name:'))
print('CHAIN nodes:', c.count('{key:'))
print('TIMELINE items:', c.count('{when:'))
print('RISKS items:', c.count('{lvl:'))
print('SCORES rows:', c.count('total:'))
print('ROE 占位:', c.count('roe:'))
print('刷新按钮:', c.count('id=\"refreshQuotesBtn\"'))
print('DEEP_CHOKES (扩展H):', c.count('reasons:'))
"

# 2. JS 语法（必做，骨架就是这么验过的）
python -c "
import re
text = open('xxx看板.html', encoding='utf-8').read()
m = re.search(r'<script>(.+?)</script>', text, re.DOTALL)
stub = '''
const document = { querySelectorAll:()=>[], getElementById:()=>({addEventListener:()=>{},dataset:{},innerHTML:'',value:''}), body:{dataset:{}} };
const window = { scrollTo:()=>{} };
const fetch = ()=>Promise.resolve({arrayBuffer:()=>Promise.resolve(new ArrayBuffer(0)),json:()=>Promise.resolve({})});
const TextDecoder = function(){this.decode=()=>'';};
'''
open('_check.js','w',encoding='utf-8').write(stub + m.group(1))
"
'/c/Program Files/nodejs/node.exe' --check _check.js && echo 'JS SYNTAX OK'

# 3. 运行时验证：实际调用每个 renderXxx 看是否抛 ReferenceError（**必跑，比 --check 严格**）
node -e "
const fs=require('fs');
const html=fs.readFileSync('xxx看板.html','utf8');
const m=html.match(/<script>([\s\S]+?)<\/script>/);
const stub=\`
const document={querySelectorAll:()=>[],getElementById:()=>({addEventListener:()=>{},dataset:{},innerHTML:'',value:'',disabled:false,textContent:'',focus:()=>{},setSelectionRange:()=>{}}),body:{dataset:{}}};
const window={scrollTo:()=>{}};
const fetch=()=>Promise.resolve({arrayBuffer:()=>Promise.resolve(new ArrayBuffer(0)),json:()=>Promise.resolve({})});
class TextDecoder{decode(b){return ''}}
\`;
try{
  eval(stub+m[1]);
  ['renderOverview','renderChain','renderCompanies','renderTimeline','renderRisk','renderSerenity'].forEach(fn=>{
    try{const out=eval(fn+'()');console.log(fn,'OK',out.length,'chars');}
    catch(e){console.log(fn,'ERR:',e.message);}
  });
}catch(e){console.log('eval ERR:',e.message);}
"

# 4. 浏览器打开
start '' 'xxx看板.html'
```

> **关键经验**：`node --check` 只查**静态语法**（括号匹配、分号），**不查运行时引用**。曾踩坑：在 `priceLine()` 里加 `<span>${roeStr}</span>`，但 patch 时 anchor 文案不匹配（`负(亏损)` vs `负(亏损预期)`），`const roeStr = ...` 没注入成功 → `--check` 通过 → 浏览器打开"公司速查"Tab 整个空白。**渲染函数实际调用一次**（步骤 3）是唯一可靠的检查。

**清理临时文件**：`rm _fetch.py _snapshot.json _check.js _data.js _render.js _merge_*.py _make_*.py`

**保留**：`_synthesis/`（含 05 卡口下钻是后续迭代关键资料）+ 最终 `xxx投研看板.html`。

---

## 数据 schema 与代码模板速查

写数据数组、拉行情、新增 CHAIN 节点时，**直接 Read 对应 references 文件**：

| 我要做的事 | Read 这个 |
|-----------|----------|
| 写 OVERVIEW / CHAIN / COMPANIES / SCORES 等数据数组 | `references/data-schema.md` |
| 写 `_fetch.py` 拉腾讯行情 + K 线 | `references/tencent-fields.md` |
| 选主题色、做 serenity 紫色 Tab 配色 | `references/css-themes.md` |
| 抄看板 HTML/CSS/JS 骨架 | `references/dashboard-skeleton.html`（已通过 node --check） |
| 跑 Kimi 6 轮合成报告 | `references/prompts/p1-p6.txt` + `prompts/README.md` |
| 注入 serenity 方法论给 Kimi | `references/serenity-methodology.md` |

**两个最容易踩的字段坑**（其余在 references 里详述）：
- COMPANIES 的 `dynPe` **直接用 `vals[39]` TTM PE 兜底**（>1e6 或 <-1e6 视为脏数据置 null）。**不要用 `vals[62]`** —— 实测 A 股多为负或异常大值。
- 估值温度 `valTag` 基于 `dynPe + pos52w` 计算（公式见 `references/tencent-fields.md` 末尾），SST 2.0 已校准。

**新增 CHAIN 节点同步检查**：`CHAIN.nodes[].key` 必须与 `SEG_NAMES` 字典 key、`COMPANIES[].seg` 严格对齐；点节点跳公司速查 Tab 的事件绑定通过 `data-seg` 自动匹配（骨架 `bindPanelEvents` 已写好）。

## 升级看板最佳实践（9 个扩展，默认全启用）

完成基础 6 步后，以下 9 个扩展让看板从"信息展示"升级到"辅助决策"。**全部默认启用** —— `references/dashboard-skeleton.html` 已内置全部扩展的 CSS、渲染函数、事件绑定，**只需填数据数组就能用**。仅当用户明确说"不要某个扩展"时才删除对应 HTML/数据数组段。

| 扩展 | 名称 | 数据数组 | 适用场景 |
|------|------|---------|----------|
| **A** | 估值位置标签 | COMPANIES.pos52w/pct52w/valTag/valLbl | 默认启用，公司卡片名旁色块 |
| **B** | 三维评分矩阵 | `SCORES`（来自 03_标的画像） | 公司速查 Tab 双视图切换 |
| **C** | 环节弹性测算 | `ELASTICITY`（来自 01_成本结构 + 04_白皮书） | 概览底部，价值量×份额×市场空间 |
| **D** | 三情景表 | `SCENARIOS` | 概览底部 bear/base/bull 敏感性 |
| **E** | 多代际对比 | `GENERATIONS`（来自 01_成本结构） | 产业链 Tab 顶部 H100→Rubin→Feynman |
| **F** | 风险升级 + bear case | `RISKS` 加 `lvl:'b'` 紫色卡片 + `src` 字段 | 风险 Tab 平衡多空，物理隔离非研报观点 |
| **G** | 公司速查排序下拉 | 默认/星级/20日涨幅/动态PE/距52周高/市值/**ROE** | 公司速查 Tab 工具栏 |
| **H** | **🎯 serenity 卡口下钻** | `SERENITY_TREE / DEEP_CHOKES / CHOKE_PURGE / CONFIDENCE / SERENITY_DEMUR` | **默认启用**第 6 Tab，与 04 白皮书"全链路视角"对照 |
| **I** | **🔄 公司速查刷新行情** | 浏览器 fetch 腾讯接口 → 更新 price/chg/pe/chg5d/chg20d/pos52w | **默认启用**公司速查 Tab toolbar 按钮 |

每个扩展的字段定义详见 **`references/data-schema.md`**；对应 CSS 类详见 **`references/css-themes.md`**；HTML/JS 实现已写入骨架。

### 扩展 H（serenity 卡口下钻）说明

**为什么默认启用**：A-G 是"展示形式升级"，H 是"投资逻辑视角切换"。04 白皮书选整机+下游、列出 30-60 家受益标的；05 卡口选上游+材料、收敛到 2-3 个真正"替不了+扩不出+寡头+没人看"的最深卡口。两个视角**几乎不重合**——这才是 serenity 相对于"全链路雨露均沾"的核心价值。**默认必跑**让每份看板都有这层纵深视角。

**实施流程**：

1. **跑 Kimi R6 产 `_synthesis/05_卡口下钻.md`**：用 `references/prompts/p6_serenity.txt`（已嵌入 `references/serenity-methodology.md` 的 ASCII 友好版）。**强制在 prompt 里点名 2-3 个候选最深卡口**让 Kimi 严肃论证或证伪——否则会写成另一份零部件清单。

2. **审阅 05 报告**（不能跳）。读完 05 全文，必查 3 件事：
   - **设备层是否过薄**：4.4 专用设备层 < 4 行算薄；置信度章节明确标注"中置信度/资料薄"
   - **"没人看见"维度交叉校验**：用估值数据辅助——PE 89 倍/距 52 周高 -8% 严格不算"没人看见"，PE 5 倍/分位低 才算
   - **必须有"04 vs 05 范式对照"段落**：04 选整机+下游、05 选上游+材料的对比是核心价值

3. **渲染独立 "🎯 卡口下钻" Tab**：骨架已含全部 CSS + renderSerenity + Tab nav，按 `references/data-schema.md` 第 10-15 节填 `SERENITY_TREE / DEEP_CHOKES / CHOKE_PURGE / CONFIDENCE / SERENITY_DEMUR`。

4. **CSS 紫色配色**：默认主题（蓝/绿/橙）下用 `--purple` 紫色 Tab；机器人主题（紫橙）下要避撞色，详见 `references/css-themes.md`"主题 4：serenity 紫色叠加"。

5. **公司卡片标记**：COMPANIES 数组里给最深卡口候选打 `tags:['..., '🎯 最深卡口']`（含 🎯 字符的 tag 自动套 `.tag.choke` 紫色），公司速查 Tab 也能识别这是 serenity 视角的核心标的。

### 扩展 I（公司速查刷新行情）说明

**为什么默认启用**：投研看板生成后，行情数据会随时间过期。**单文件零依赖 + 浏览器直连腾讯接口**让用户随时一键拉最新价。

**实施要点**：
- 按钮放在公司速查 Tab toolbar（搜索框、排序下拉旁）
- 点击后调 `qt.gtimg.cn`（GBK，用 TextDecoder 解码）+ `web.ifzq.gtimg.cn` K 线接口
- **CORS 已确认开放**（`Access-Control-Allow-Origin: *`）
- 仅刷新 A 股+港股+美股；未上市标的（`price: null`）跳过
- ROE 字段腾讯不返回，刷新时不覆盖（保留 null 或外部接入数据）
- 刷新完毕后 `mount()` 重渲染当前 Tab，新数据立即显示

### 扩展实施 checklist

行情脚本改拉 260 日 K 线 → Explore agent 抽 SCORES/GENERATIONS/ELASTICITY → CSS 新增（valTag/dtable/smatrix/scen/bear card）→ 数组注入 → 渲染/事件绑定 → **JS 语法验证**（必做）：

```bash
# 提取 <script> 块，加 DOM stub，用 node --check 验证语法（node 路径见下）
/c/Program\ Files/nodejs/node.exe --check _check.js && echo "JS SYNTAX OK"
```

闭合检查追加 `SCORES/total:` / `perRack:` / `{field:` / `bear:` 的 count 验证。**含扩展 H 时再加** `DEEP_CHOKES`（`isChoke:`/`reasons:`/`transmission:` 的 count，预期 2-3 个）和 `CHOKE_PURGE`（`verdict:` 的 count，预期 3-5 个）的存在性检查；如果数据数组在 .qa-table 里直接展开，则 grep `choke-hit` 紫色行计数 ≥ 6（4 张表合计强卡口数）。

清理 `_check.js`、`_fetch.py`、`_snapshot.json`、`_companies_merged.json`、`_data.js`、`_render.js` 等中间产物，**保留 `_synthesis/`**（含 05 卡口下钻是后续迭代的关键纵深资料）。

> 完整扩展参考：
> - Rubin 看板（`Research Report/英伟达rubin/英伟达Rubin产业链投研看板.html`）—— 7 个扩展 A-G 全应用，69 家公司 + 7 数组，80KB；
> - SST 2.0 看板（`Research Report/固态变压器/SST投研看板2.0.html`）—— **唯一含扩展 H 卡口下钻 6 Tab 的实现**，67 家公司，125KB，蓝青主+紫色 serenity Tab。

---

## 反模式（不要做）

- ❌ **跳过 Kimi 提炼直接让 Explore 读原始研报**：除非用户明确说"快速版/不要 Kimi"，默认走两阶段流程
- ❌ **基于上次的看板做 patch 加新字段**：`replace` 的 anchor 文案稍微不同就静默失败，引用的变量没定义但 `--check` 通过，浏览器打开 Tab 空白。**永远从 skeleton 重生成**——一个 `_make.py` 把全部数据数组+占位符一次注入，不要分多步打补丁
- ❌ **`node --check` 后就以为 OK**：`--check` 不查 ReferenceError；`${someVar}` 模板里引用未定义变量它不报。**必须用 `node -e "eval(全部 JS); renderCompanies()"` 实际跑一遍渲染函数**
- ❌ **绕过 `kimi_run.py` 直接调 kimi**：Windows GBK 编码会因 `↔` 等字符崩溃
- ❌ **Kimi 自编会话 ID 或每轮换会话**：2.x 不认自编 ID；换会话浪费 token。必须同一个 `--session-file` 续会话
- ❌ **自己 Read 全部 _synthesis 文件**：交给 3 个 Explore agent 并行
- ❌ 一只一只调 a-stock-data：写脚本批量拉，几秒搞定
- ❌ 引入 React/Vue/Chart.js/CDN：违背"双击就开"原则
- ❌ 把行情数据放到外部 JSON 文件：必须内嵌在 HTML 里
- ❌ **拉 ROE 默认用 mx-finance-data**：单次最多 5 实体 + 子进程 + xlsx 解析（行/列两种格式都可能）+ 输出目录跟 cwd 走容易找不到。**A 股 ROE 一律先用 Tushare `pro.fina_indicator(ts_code, fields="roe_waa,roe")`**，DataFrame 直接返回，59 家 20 秒。港股/美股 Tushare 普通账号无权时再 fallback mx
- ❌ **新增 Tab 或重新设计风格**：除非用户明确要求 serenity 视角（启用扩展 H 第 6 Tab），保持 5 Tab 一致体验
- ❌ 漏写 `</script>`：每次都查一遍
- ❌ 给未上市标的瞎编行情：`price: null` + `note` 字段处理
- ❌ 生成完删 `_synthesis/`：保留作为下次迭代的中间产物，省一次 Kimi 调用
- ❌ **行情只拉 25 日 K 线**：改拉 260 日才能算 52 周位置（一个接口参数的事）
- ❌ **弹性测算不标置信度**：必须在表格下方注明「量级测算，非精确预测」
- ❌ **bear case 和研报观点混排**：紫色卡片必须加「非研报观点」标注，物理隔离
- ❌ **用 bash coreutils（ls/find/cat）**：本机 bash 无 coreutils，改用 Glob/Read 工具或 python -c 脚本
- ❌ **见 Kimi"超时"就重启**：Kimi 写完文件后 stdout 会卡 1-3 分钟，**先看目标 .md 文件落盘了没**，落了就 TaskStop 进下一轮
- ❌ **serenity 卡口下钻不读 04 白皮书**：05 必须基于 01-04 做纵深，否则会写成另一份 04（重复零部件清单）
- ❌ **05 把 04 选过的整机厂当卡口**：金盘/麦格米特/科士达 这些是"04 视角"的标的，05 要钻到上游材料/设备层；候选不重合才有对照价值
- ❌ **05 卡口候选超过 3 个**：4 个以上意味着没收敛到"最深"，serenity 强制 2-3 个；扩展到 4 个就退化成清单了
- ❌ **05 直接放 04 已写过的"全链路"图谱**：树根图必须钻到材料层和专用设备层，且关键卡口节点用 `<mark>` 紫色标记
- ❌ **05 漏写置信度章节**：设备层研报覆盖薄是常态，必须明确分"高置信度（多源研报）vs 中置信度（serenity 推断）"
- ❌ **serenity Tab 主题色与基础 Tab 撞色**：`--purple` 不能等于 `--accent`；机器人看板若主题已是紫色，serenity Tab 改用青绿/品红等差异化色

## 风险点

- **Kimi 输出准确性需校验**：4 份合成报告里的股票代码、市占率数字偶有口径不一，关键代码要用 Python 脚本 + 腾讯行情返回名称二次校验。Kimi 在长文档去重上很稳，但具体百分比仍可能漂移。
- 研报里的股票代码可能写错（SST 看板时云路股份 688490 实际是 688190；机器人看板时北特科技被研报标"未上市"实际是 A 股 603009）。**所有代码先用 Python 脚本验一遍**。
- 数据时点容易过期：HTML header 必须显式标注 `数据截止 YYYY-MM-DD`，提醒用户这是静态快照。
- 重新生成时不要手动改 HTML 里的行情数字：重跑步骤 4 的脚本更稳。
- **如果 `_synthesis/` 已存在**：直接进入步骤 2，跳过 Kimi 调用；用户若要"重新提炼"则先删除 `_synthesis/`。
- **bash 环境无 coreutils**：本机 Git-bash PATH 只有 Windows 系统目录，`ls`/`cat`/`find`/`which` 均不可用，文件操作改用 Glob/Read 工具或 python -c 脚本（`/c/Users/Administrator/scoop/shims/python.exe`）。
- **node 路径**：`/c/Program Files/nodejs/node.exe`，可用于 JS 语法验证（`node --check`）。
- **腾讯 vals[62] 不是 forward PE**：实测 A 股 `vals[62]` 多为负或异常大值（不是真正的动态 PE）。看板里的 `dynPe` **直接用 `vals[39]` TTM PE** 兜底（超 1e6 视为脏数据置 null），不要再套 `vals[62]`。SST 2.0 看板已修正，机器人/Rubin 看板早期版本仍按 vals[62]，重跑时同步迁移。
- **serenity 卡口扩展（H）的资料薄风险**：85 篇研报里整机/部件层覆盖密集，但**专用设备层**（CVD 反应炉、纳米晶制带机、衬底切割抛光设备）研报往往只点名 1-2 行。05 卡口下钻必须在置信度章节明确分层："高置信度（研报实据）"vs"中置信度（serenity 推断/资料薄）"。如果某主题语料完全没有材料/设备层（如周报+整机点评为主），不要硬拗 05，标注"建议补充材料层定向检索后再做"。
- **serenity 方法论已内置 skill**：`references/serenity-methodology.md` 是 ASCII 友好版（已替换 `↔ → ≈`），`references/prompts/p6_serenity.txt` 已嵌入完整方法论 + 7 段固定模板。**不再依赖外部路径** `D:\AI_Tools\finance\serenity方法论.md`（仅作历史备份）。

