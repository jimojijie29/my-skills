---
name: moda-lecture-reconstruction
description: 将莫大仙岳居的金融直播内容重构为专业HTML演示文稿。当用户提到"莫大"、"直播"、"莫大仙岳居"、"公域"、"私域"、"公域直播"、"私域直播"，或需要将直播讲义转换为PPT/HTML格式时触发。Reconstructs 莫大仙岳居 live-stream financial lectures into structured HTML presentations with continuous scroll layout. Use when user mentions 莫大、直播、莫大仙岳居、公域、私域 or needs to convert lecture transcripts into PPT/HTML format.
---

> ## 移植说明 · PORTING NOTE
>
> 本技能已导入为项目级 skill（`.claude/skills/moda-lecture-reconstruction/`，样式参考文件位于 `references/`）。`KNOWLEDGE.md` 与样式参考文件均用相对路径引用，可直接使用。
>
> **运行期数据位置（图片源、跨期检索索引）不能随技能打包，按本地环境指向（均已相对化，从项目根目录解析）：**
> - 第0步扫描命令中的 `Picture` → 指向本项目根目录下的图片源文件夹
> - 「文件命名规范 / 输出文件 / 扩展知识库」中的 `全局索引.md` → 指向本项目根目录下的跨期索引文件（若无则新建）
>
> 技能逻辑本身（工作流、组件规范、A股配色、Python 嵌入脚本模板）与工作区无关，可原样沿用。

---

# 莫大仙岳居直播讲义重构

## 角色定位

你是一位从讲师"莫大仙岳居"声音中"看见"PPT的重构师。每段话语背后，都藏着一张曾经投射在屏幕上的画面。

**价值判断优先级**：培训精髓 > 闲谈枝叶 | 知识骨架 > 表达修饰 | 逻辑主线 > 即兴发挥

**结构化感知**：口语停顿处 = 页面切换点 | 重复强调 = 核心要点 | 案例故事 = 概念诠释

---

## ⭐ 标准工作流（五句话记住）

> **先扫图读数想结构 → 一次写入 HTML → 同步写 Markdown 笔记 → 跑脚本压缩嵌入 → 浏览器双端验收**

- **先扫图读数想结构**：扫描图片 + **Read 数据类图片取数、与口播交叉核对** + 分析文稿 + 规划章节/页面/图片映射，全部想清楚再动手
- **一次写入 HTML**：用 `Write` 工具将完整 HTML（CSS、导航、所有幻灯片、图片引用、图旁数据表）**一次性写入**，不分段追加
- **同步写 Markdown 笔记**：紧接着写 `_notes.md`，内容与 HTML 完全对应，纯文字，用于日后全文检索
- **跑脚本压缩嵌入**：复制 `references/convert_images_template.py` 为 `convert_images_YYYY_MM_DD.py`，图片缩至 ≤1600px 宽并转 WebP 后 Base64 内嵌，输出独立的 `_embedded.html`（目标 ≤5MB）
- **浏览器双端验收**：用 preview 打开 embedded 版，桌面 1400px + 手机 375px 各截一张，确认图片、目录、无横向溢出

> 🏆 **有图讲义范本**：`2026.11.24_私域直播_主跌段未完与反弹套利框架`（23 图，读图列数、WebP 压缩至 3MB、双端验收）。拿不准做法时对照它。

> 📐 **V3.0 默认模板**：写 HTML 前**先 Read `references/style-reference-V3.0.html`**，`<head>` 与文末 `<script>` 原样复制——纸面阅读栏 + 深蓝章节带 + 日/夜切换 + 左侧目录栏 + 封面 KPI 带 + 每章一句话结论。**不要**拿同系列上一期或其他旧讲义当模板（11-10 之前的都是 V2.0）。详见「📐 模板版本」。
>
> 📚 动手前同时读 `KNOWLEDGE.md`（已完成讲义列表的备注里有模板版本、作者署名等约定）。

> ⚠️ 禁止边写边用 StrReplace 追加内容，禁止分多次 Write 拼接 HTML。一次成型是效率和质量的保证。

---

## 工作流程（第0–6步）

> **核心原则**：先扫图片、再读文稿、再生成 HTML —— 确保每个图片引用从一开始就是真实文件名，彻底消除"虚构文件名"的问题。

### 第0步：扫描 Picture/ 文件夹（**必须最先执行**）

在生成任何 HTML 之前，**必须先用 Shell 命令列出 Picture/ 文件夹中的实际图片文件名**：

```bash
python -c "import os, sys; sys.stdout.reconfigure(encoding='utf-8'); files = [f for f in os.listdir(r'Picture') if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]; [print(f) for f in sorted(files)]"
```

> ⚠️ **扩展名大小写陷阱（必读）**：Picture/ 文件夹中的图片扩展名可能是大写（`.PNG`、`.JPG`）或小写（`.png`、`.jpg`），两种情况都会出现。  
> - 扫描命令**必须使用 `.lower().endswith(...)`** 进行不区分大小写匹配，否则大写扩展名的图片会被漏掉，导致误判"无图片"。  
> - HTML 中 `<img src="Picture/文件名">` 引用时，**直接使用 `os.listdir()` 返回的真实文件名**（含原始大小写），不要自行改写扩展名大小写。  
> - 嵌入脚本必须能不区分大小写地匹配文件名：`references/convert_images_template.py` 的 `resolve()` 已处理（先试精确路径，再用 `fn.lower()` 匹配），复制模板即可，不要自己重写。

**得到文件名列表后：**
- 每个文件名本身就是一段描述（如 `两市融资余额数据-3.23.png` = 融资余额图表）
- 根据文件名中的**日期后缀**（`-M.DD`）筛选出本次直播对应的图片
- 建立"图片内容 → 讲义章节"的映射表，再进入下一步

### 图片内容识别规则

| 文件名关键词 | 对应讲义位置 |
|-------------|-------------|
| `融资余额` / `融资盘` | 前言 · 市场数据页 |
| `成交金额` / `沪深均值` | 前言 · 市场数据页 |
| `融资盘流入流出` / `行业板块前十` | 前言 · 融资盘流向页 |
| `美债` / `国债收益率` / `TGA` | 流动性章节 |
| `货币供应量` | 流动性章节 |
| `中美日.*利率对比` | 流动性章节 |
| `国债指数` | 中国国债分析页 |
| `各期国债.*上证` | 中国国债分析页 |
| `光伏` / `晶科` / `福斯特` | 出口机遇 · 光伏章节 |
| `上证指数` / `缺口` | 技术分析 · 上证分析页 |
| `轮中轮` / `指标` | 技术分析 · 周期指标页 |
| `创业板` | 技术分析 · 指数对比页 |
| `科创50` | 技术分析 · 指数对比页 |
| `沪深300` | 技术分析 · 指数对比页 |
| `中证500` / `中证1000` / `国证2000` | 技术分析 · 指数对比页 |
| `恒生指数` / `港元` | 技术分析 · 港股页 |
| `个股名称`（如晶科、福斯特、南方泵业…） | 个股分析页 |

### 第0.5步：读图取数（**数据类图片必须执行**）

文件名只能说明“是什么图”，说明不了“图里是多少”。写 HTML 之前，用 `Read` 工具**打开数据类图片读出数值**，再与口播对照。

| 图片类型 | 是否 Read | 提取什么 |
|---------|----------|---------|
| 数据表 / 宏观图：文件名含 `融资` `成交` `国债` `收益率` `TGA` `货币供应` `汇率` `利率` `息差` `竞价` `宽基` 等 | **必须** | 截止日期口径、最新值、关键区间值、单位；表格类逐行抄录关键行 |
| K 线技术图：`-15分钟图` `-日线图` `-周线图` `-月线图` | 不必逐张 | 图注按文件名写，结构判断以口播为准（控制上下文消耗） |
| 个股图 | 口播有具体价位/数据时才读 | 关键价位 |

每张已读的图记一行速记：`文件名 → 口径日期 / 关键数值 / 单位 / 与口播是否一致`，供第2步直接取用。

### 数据呈现与核对规则

1. **图旁列数**：关键数据不要只“藏在图里”，要在图下方另列 `data-table` 或 `metric-row`，口径（日期、对象）写进表头或 `m-lab`。
   - 范例（11.24）：融资余额多日表「日期 / 融资余额 / 两市增量（▲红 ▼绿）/ 上证指数」，下接一行 `metric-row` 区间汇总（连续 N 日合计、年初至今、某日至今）。
   - 多期限 / 多市场对比（各期美债、中美日息差）用表格或 `metric-row`，不要堆在一段文字里。
2. **派生数算出来并写算式**：连续 N 日流出合计、利差（4.92 − 4.63 = 29bp）、息差（4.92 − 1.59 = 3.33%）等，自己算，算式写进表格说明列或 `m-lab`。
3. **单位换算写清**：如 TGA「880,764 百万美元 ≈ 8808 亿美元」。
4. **口播与图不符时，两边都留**：正文保留口播说法，在 `note-ed` 校注里写出图中数值和差异。例：「口播“接近1000亿”；按图中数据，连续7日流出合计约1315.22亿」。图表自身标注有误（图例写反、日期标错）也写进校注。**不改原意、不臆造**。
5. **封面 KPI 优先用读图得到的硬数据**，`k-lab` 写明日期口径；涨跌数值照常用 `.highlight` / `.green`。
6. 读图得到的数据表**同样迁入 `_notes.md`**（Markdown 表格），保证可检索。

---

### 第1步：分析直播内容

识别主题切换点、核心观点、案例，结合第0步的图片清单，规划幻灯片结构。

### 第2步：生成 HTML

**先 Read `references/style-reference-V3.0.html`**，原样复制其 `<head>`（主题脚本 + `<style>` + SVG 素材）与文末 `<script>`；正文按其结构写成 `<section class="slide">`，每个 slide 是一个完整思想单元，**直接引用第0步中真实的图片文件名**。

> 用户说「不需要嵌入图片」时：跳过第0、0.5、3、4步与嵌入脚本，只输出 `_presentation.html` + `_notes.md`（第6步验收改为打开基础版）；说「不需要进入索引」时：不更新 `全局索引.md` 与 `KNOWLEDGE.md`。

### 第2.5步：生成 Markdown 笔记文件（**必须执行**）

HTML 写完后，**立即**用 `Write` 工具输出 `YYYY.MM.DD_类型_主题_notes.md`。

**写入规则**：
- 内容与 HTML **逐章对应**，所有要点、数据、语录、表格均迁移过来（含第0.5步读图得到的数据表与校注）
- **不含**图片引用（`img` 标签）、CSS、导航栏 HTML
- Markdown 表格、引用块（`>`）、加粗均正常使用，保证可检索性
- 完成后在 `全局索引.md` 的对应行中，将 notes 状态更新为 `✓`

**文件结构模板**（根据实际章节数量增减）：

```markdown
# 主题标题

**日期**：YYYY年M月D日　**类型**：公域直播／私域直播　**主讲**：莫大仙岳居

---

## 直播大纲

1. 议题一描述
2. 议题二描述
...

---

## 01 章节名称

### 页面标题

- 要点一（可加粗关键词）
- 要点二
- 数据：**X%** / **X亿** 等关键数字加粗

> "莫大语录原文" ——莫大仙岳居

| 指标 | 数值 | 含义 |
|------|------|------|
| 指标名 | 数值 | 解释 |

---

## 02 章节名称
...

---

## 核心结论速查

- 结论1（一句话）
- 结论2
...

## 莫大语录汇总

> "语录一"
> "语录二"
```

### 第3步：验证图片覆盖率

生成后检查：所有从 Picture/ 扫描到的图片是否都已安排进某一张幻灯片？若有遗漏，补充进去。

### 第4步：编写并运行嵌入脚本

复制 `references/convert_images_template.py` 到项目根目录，改名 `convert_images_YYYY_MM_DD.py`，**只填配置区**：`HTML_FILE`、`OUTPUT_FILE`、`REQUIRED_IMAGES`（直接粘贴第0步的真实文件名）。运行后看最后一行：文件大小 MB、残留未嵌入引用数；退出码 0 才算通过。详见「Python 图片嵌入脚本模板」。

### 第5步：输出文件

每次直播重构完成后，输出以下四个文件：

| 文件 | 说明 |
|------|------|
| `YYYY.MM.DD_类型_主题_presentation.html` | 基础版（引用本地图片路径） |
| `YYYY.MM.DD_类型_主题_presentation_embedded.html` | 独立发布版（图片缩放 + WebP 压缩后 Base64 内嵌，目标 ≤5MB） |
| `YYYY.MM.DD_类型_主题_notes.md` | **纯文字笔记，用于全文检索** |
| `convert_images_YYYY_MM_DD.py` | 图片嵌入脚本（由模板复制） |

完成后同步更新：
- `全局索引.md` — 追加本次讲义的关键词条目
- `KNOWLEDGE.md` — 已完成讲义列表追加新行（图片列写明张数、嵌入率与 embedded 体积）

### 第6步：浏览器双端验收（**必须执行**）

讲义主要在手机上读，必须实际打开检查，不能只凭代码判断。

1. `preview_start` 启动 **`lecture-preview-alt`**（端口 8767）。`lecture-preview` 的 8765 常被旧进程占用：那时 preview 会报“分配了别的端口”，但服务其实没起来，页面停在 `chrome-error://`。
2. 用**完整 URL** 打开 **embedded 版**：`preview_eval` 执行 `location.href='http://localhost:8767/'+encodeURIComponent('文件名_presentation_embedded.html')`。
3. 用 `preview_eval` 一次性检查（等 1–2 秒加载）：
   ```js
   ({imgs:document.images.length,
     broken:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length,
     nav:document.querySelectorAll('a[data-sec]').length,
     secs:document.querySelectorAll('section.section-slide[id]').length,
     overflowX:document.documentElement.scrollWidth>document.documentElement.clientWidth})
   ```
   通过标准：`imgs` = `REQUIRED_IMAGES` 数，`broken` = 0，`nav` = `secs`，`overflowX` = false。
4. `preview_resize` 到 `1400×900` 截图：确认左侧目录栏和封面标题断行；再切 `preset: "mobile"`，滚到一个 `.img-pair` 页截图：确认双图上下堆叠、顶栏显示章节名、表格不撑破页面。
5. 结束前 `preview_resize` 设 `preset: "desktop"` 复位视口。发现问题就改 HTML，然后重跑第4步脚本，再验收一次。

---

## 文件命名规范

- **讲义 HTML**：`YYYY.MM.DD_类型_主题_presentation.html`
  - 类型：`公域直播` 或 `私域直播`
  - 示例：`2026.03.10_私域直播_指数群体与交易心法_presentation.html`
- **讲义 Markdown**：`YYYY.MM.DD_类型_主题_notes.md`（与 HTML 同名，后缀改 `_notes.md`）
  - 示例：`2026.03.10_私域直播_指数群体与交易心法_notes.md`
  - **用途**：纯文字版，支持 grep / Obsidian / Everything / IDE 全文检索
- **图片文件**：`描述-M.D.扩展名`，统一放 `Picture/` 文件夹
  - 示例：`两市融资余额-3.10.png`
- **全局索引**：`全局索引.md`（跨期关键词汇总，每次更新）
- **作者署名**：默认「莫大仙岳居」；**例外**：「技术分析3.0 结构与时间」系列课程（第48讲起）署名「绝对实战」，文件名用 `YYYY.MM.DD_技术分析3.0_第N讲_主题_presentation.html`，放项目根目录

---

## 📐 模板版本：V3.0（2026-11 起默认）

> **唯一样式来源**：`references/style-reference-V3.0.html`。动手写 HTML 前**必须先 Read 这个文件**，把其中的 `<head>`（首段主题脚本 + `<style>` + SVG `<symbol>` 素材）和文末 `<script>` **原样复制**，正文按其演示结构填写。
>
> ⚠️ **不要以「同系列上一期讲义」或项目里任何旧 HTML 为模板**。项目中 2026-11-10 之前的讲义（包括技术分析3.0 第55、57讲）都是 V2.0，复制它们就会退回旧模板。若不确定，先用 `ls -t *_presentation.html | head` 看最新一期是否为 V3.0（`<style>` 首行含「讲义模板 V3.0」）。
>
> `references/style-reference-V2.0.html` 为**旧版**，仅在用户明确要求「沿用 V2.0 / 深色全屏幻灯片样式」时使用。

| 版本 | 时间 | 外观 | 状态 |
|------|------|------|------|
| V2.0 | 2026-08 ~ 2026-11-08 | 深色全屏幻灯片、右侧红色圆形导航、幽灵大字、居中封面 | 旧版 |
| **V3.0** | 2026-11-10 起 | 纸面阅读栏（单栏 54rem）+ 深蓝章节带；日间/夜间切换；宽屏左侧目录栏、窄屏顶栏「目录」下拉；楷体语录；SVG 结构示意图 | **默认** |

---

## HTML 结构规范（V3.0）

**布局**：原生连续滚动的**阅读式长文**（非 reveal.js，也不再是每页 100vh 的深色幻灯片）。正文为浅色纸面单栏，封面 / 章节分隔 / 结尾为深蓝色通栏「章节带」；用户可切换日间/夜间。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>YYYY.MM.DD 主标题 - 莫大仙岳居</title>
<script>/* 主题初始化：读 localStorage 'moda-theme'，缺省跟随系统（原样复制参考文件） */</script>
<style>/* ===== 讲义模板 V3.0 ===== 原样复制参考文件 */</style>
</head>
<body>
<svg width="0" height="0" ...><defs><symbol id="k-top">…</symbol><symbol id="k-bot">…</symbol></defs></svg>  <!-- K线示意素材 -->
<div class="progress-bar" id="progressBar"></div>
<header class="topbar">目录按钮 · #curChapter · 夜间按钮</header>
<nav class="quick-nav" id="quickNav">nav-brand · 章节链接 · nav-foot(已读% + 夜间按钮)</nav>
<main>
  <section id="top" class="slide cover-slide"><div class="wrap">…</div></section>
  <section class="slide">…内容页…</section>
  <section id="s-xxx" class="slide section-slide"><div class="wrap">…</div></section>
  …
  <section id="ending" class="slide ending-slide"><div class="wrap">…</div></section>
</main>
<script>/* 进度条 + 章节高亮 + 顶栏章节名 + 目录开合 + 主题切换（原样复制参考文件） */</script>
</body>
</html>
```

**硬性约定**（脚本依赖这些，缺一不可）：
- 所有页面用 `<section class="slide …">`，全部放在 `<main>` 里；封面 `id="top"`，结尾 `id="ending"`
- 导航每个章节链接：`<a href="#s-xxx" class="quick-nav-btn" data-sec title="章节短标题"><span class="n">01</span>章节短标题</a>`；`title` 会显示在窄屏顶栏
- `data-sec` 链接数量 = 带 `id` 的 `section-slide` 数量，`href` 与 `id` 一一对应
- 顶部固定 `↑ 封面`（`#top`），底部固定 `↓ 结论速查`（`#ending`，无 `data-sec`）
- `nav-brand` 写作者与日期类型（如「莫大仙岳居 / 2026.11.17 私域直播」）；`nav-foot` 内需有 `#readPct` 和 `.theme-toggle`
- 顶栏和 `nav-foot` 各有一个 `.theme-toggle` 按钮，脚本同时更新两处

### 章节 id 命名约定

| 常见章节 | 推荐 id |
|---------|---------|
| 聊聊市场 / 外盘 | `s-market` / `s-us` |
| 交易规则 / 方法课 | `s-trade` / `s-method` |
| 指数分析 | `s-index` |
| 个股 | `s-stock` |
| 宏观背景 | `s-macro` |
| 周期 | `s-cycle` |
| 操作策略 | `s-ops` |

导航里写**完整的短标题**（4–8 字，如「美债急升与外盘」），不再用 2 字圆钮简称。

---

## 页面组件（V3.0）

> CSS 全部在参考文件里，这里只说明**用法**。完整可运行示例见 `references/style-reference-V3.0.html`。

### 1. 封面 `cover-slide`

```html
<section id="top" class="slide cover-slide">
 <div class="wrap">
  <p class="cover-meta"><span>私域直播</span><span>2026年11月17日 周二</span><span>主讲 莫大仙岳居</span></p>
  <div class="cover-head">
    <div>
      <h1 class="cover-title">主标题写成判断句，<br>两行以内</h1>
      <p class="cover-subtitle">2–3 句导语：本期核心判断、依据、应对。</p>
    </div>
    <svg class="cover-k" viewBox="20 46 664 258" role="img" aria-label="…"><use href="#k-top" width="720" height="320"/></svg>
  </div>
  <div class="kpi-strip">…kpi × 4–5…</div>
  <div class="cover-agenda"><h2>直播大纲</h2><ol><li>…</li></ol></div>
 </div>
</section>
```

- 标题风格：**判断句**（「重置未完，不抄没有确定性的底」），而不是「主题A与主题B」式的名词堆叠；首行 ≤5 个汉字，避免中等宽度下单字断行
- KPI 优先放第0.5步读图得到的硬数据，`k-lab` 写明日期口径
- `cover-k` 为右侧示意 K 线：下跌主题用 `#k-top`（高位平台→下行），筑底/上涨主题用 `#k-bot`（下跌→回升）；不合适可删
- `cover-agenda` 用 `<ol>`，序号自动生成，**不要**手写数字

### 2. KPI 带 / 指标行 `kpi-strip` · `metric-row`

```html
<div class="kpi-strip">
  <div class="kpi"><div class="k-val highlight">+42<small>bp</small></div><div class="k-lab">美国2年期收益率，11月5日以来升幅</div></div>
  <div class="kpi"><div class="k-val">126<small>/161 T</small></div><div class="k-lab">中性数字不加颜色</div></div>
  <div class="kpi"><div class="k-val gold">小仓 差价</div><div class="k-lab">结论 / 建议</div></div>
</div>
```

正文用 `.metric-row` > `.metric` > `.m-val` / `.m-lab`，样式相同。数值单位放 `<small>`；涨 `.highlight`，跌 `.green`，结论 `.gold`，中性不加类。`k-lab` 写清楚数字的口径（时间、对象）。

### 3. 章节分隔 `section-slide`（含一句话结论）

```html
<section id="s-us" class="slide section-slide">
 <div class="wrap">
  <div class="section-num">01</div>
  <div>
    <h2>美债急升：加息预期一周拉满</h2>
    <p>章节副标题，一两句。</p>
    <div class="tldr"><b>一句话结论：</b>先给答案再论证。</div>
  </div>
 </div>
</section>
```

V3.0 **没有** `section-tag`、`data-ghost` 幽灵大字，不要加。

### 4. 内容页 `section.slide`

- 标题 `<h3>` 写成**完整判断句**，不加「■」等前缀符号
- 页首导语用 `<p class="lead">`
- 要点用 `<ul class="bullet-list">`；关键词用 `<strong>`，需要荧光笔强调用 `<span class="gold">`
- 相邻内容页之间自动出现细分隔线，无需手动加

### 5. 提示框（7 种语义，同一结构）

`data-box`（数据）· `insight-box`（洞察）· `strategy-box`（策略）· `danger-box`（风险）· `tech-box`（技术）· `cycle-box`（周期）· `stock-box`（个股）。结构统一为 `<div class="xxx-box"><div class="box-title">标题</div><p>…</p> 或 <ul class="bullet-list">…</ul></div>`，只靠左线与标题色区分。

### 6. 对比与分栏

- `vs-wrap`：`左 box` + `<div class="vs-mid">→</div>` + `右 box`，用于「之前 vs 现在」「旧规则 vs 新规则」
- `two-col` / `three-col`：并排 box

### 7. 流程与时间类

| 组件 | 用途 | 写法要点 |
|------|------|---------|
| `ol.chain` | 传导链、因果链 | `<ol class="chain"><li>…</li></ol>`，编号和箭头自动生成 |
| `ol.steps` | 历史时间线、操作步骤 | 每个 `<li>` 内容包在 `<span>` 里 |
| `.timebar` | 时间跨度对比（如 358T vs 161T） | `<div><span>标签</span><i style="--w:70%"></i><b>数值</b></div>`；进行中用 `i.dash` |
| `.weeks` | N 周倒计时（如七周防御期） | 7 个 `<span>` + 空 `<span>` + `<span class="end">` |

### 8. 表格

一律包一层 `<div class="table-wrap">`（窄屏可横向滚动）；首列自动加粗，**不要**再给首列加 `class="gold"`。

### 9. 语录 `quote-box`

```html
<div class="quote-box">闹肚子的时候，任何一个屁都不值得信任。<cite>莫大仙岳居</cite></div>
```

楷体显示；正文**不加引号**（左侧「由样式生成），`<cite>` 里只写名字，不加「——」。

### 10. 结构示意图 `figure`（SVG）

用于口播中描述的形态（扩张平台、底背离、三波段等），**示意而非真实行情**：

```html
<figure class="figure">
  <figcaption>结构示意图，非真实行情。红涨绿跌。</figcaption>
  <svg viewBox="14 6 684 298" role="img" aria-label="…">
    <use href="#k-top" width="720" height="320"/>
    <g class="kc-m"><circle cx="160" cy="28" r="16"/><text x="160" y="35">1</text></g>
  </svg>
  <ol class="legend"><li>与圆圈 1 对应的说明</li></ol>
</figure>
```

### 11. 校注 `note-ed`

口播错字、日期口误、数字存疑、名称未说出等，放 `<p class="note-ed"><b>校注：</b>…</p>`，**不改动原意**、不臆造。

### 12. 结尾 `ending-slide`

`<h2>结论速查</h2>` + `two-col`（左：核心结论列表；右：读图口诀 / 操作口诀 + 1–2 条 `quote-box`）+ 一行 `tag-pill` 关键词 + `<p class="signoff">`（落款，如「夜梦吉祥。」）+ `<p class="muted">` 免责声明。

---

## 配色规范（V3.0）

颜色全部走 CSS 变量，日/夜两套由 `:root[data-theme="dark"]` 自动切换，**正文里不要写死 hex 颜色**。

| 变量 | 日间 | 夜间 | 用途 |
|------|------|------|------|
| `--paper` / `--surface` | `#F2F4F7` / `#FFFFFF` | `#0A111E` / `#111B2E` | 纸面 / 卡片 |
| `--ink` / `--ink-2` / `--ink-3` | `#131B2E` … | `#E7EBF3` … | 正文三级灰阶 |
| `--band` | `#0F3460` | `#10284C` | 封面 / 章节 / 结尾深蓝带 |
| `--up` | `#D4233F` | `#F0506A` | **上涨（红）**，仅用于涨 |
| `--down` | `#0B8A47` | `#27C27A` | **下跌（绿）**，仅用于跌 |
| `--mark` | `#FFE35A` | 半透明金 | `.gold` 荧光笔底色 |
| `--c-data` … `--c-stock` | 见参考文件 | 见参考文件 | 7 种提示框语义色 |

文字类：`.highlight` = `--up` 红；`.green` = `--down` 绿；`.gold` = 荧光笔强调；`.muted` = 次要说明；`.num` = 等宽数字字体。

---

## ⚠️ 行情数据涨跌颜色规范（A股习惯，必须遵守）

> **中国A股习惯：涨红跌绿**，与西方习惯（涨绿跌红）完全相反。  
> 生成 HTML 时，所有涉及市场行情的涨跌数据，**必须严格遵守 A股配色标准**。

### 颜色对照表

| 含义 | 符号 | 正确颜色 | 颜色值 | 错误示范（西方习惯） |
|------|------|----------|--------|---------------------|
| 上涨 / 领涨 / 涨幅 | ▲ `+` | **红色** | `var(--up)`（`.highlight`） | ~~绿色~~ |
| 下跌 / 领跌 / 跌幅 | ▼ `-` | **绿色** | `var(--down)`（`.green`） | ~~红色~~ |

### 适用场景（这些地方必须用A股配色）

```html
<!-- 夜盘/外盘行情数据表格 -->
<td><span class="green">▼ -0.81%</span></td>       <!-- 下跌 → 绿色 -->
<td><span class="highlight">▲ +2.15%</span></td>   <!-- 上涨 → 红色 -->

<!-- 板块领涨领跌描述 -->
<span class="highlight">领涨</span>   <!-- .highlight = var(--up) 红色，用于上涨 -->
<span class="green">领跌</span>       <!-- .green = var(--down) 绿色，用于下跌 -->

<!-- 融资余额增减 -->
<span class="highlight">▲ +126亿</span>   <!-- 流入增加 → 红色 -->
<span class="green">▼ -126亿</span>       <!-- 流出减少 → 绿色 -->
```

### 不适用场景（这些地方颜色含义与涨跌无关，保持原样）

```html
<!-- V3.0：红绿只给涨跌。风险、警示、结论用提示框或荧光笔，不要借红绿表达 -->
<div class="danger-box">...</div>                <!-- 风险：橙色左线 -->
<div class="strategy-box">...</div>              <!-- 策略：深蓝左线 -->
<span class="gold">建议操作方向</span>            <!-- 重点：荧光笔 -->
<strong>顶部信号</strong>                         <!-- 一般强调：加粗 -->
```

### 生成检查清单

每次生成 HTML 后，搜索以下关键词进行颜色校验：
- 搜索 `▼` → 确认所有下跌箭头在 `.green` 内（绿色）
- 搜索 `▲` → 确认所有上涨箭头在 `.highlight` 内（红色）
- 搜索 `领涨` → 确认使用 `.highlight`；搜索 `领跌` → 确认使用 `.green`
- 搜索 `style="color:#` → V3.0 正文不应出现写死的颜色（夜间模式会失效）
- 搜索 `section-tag`、`data-ghost`、`scroll-indicator`、`cover-badge` → 出现即说明混入了 V2.0 结构

### Box 组件类型

```css
.data-box      /* 数据展示 — 蓝灰 --c-data */
.insight-box   /* 核心洞察 — 金褐 --c-insight */
.strategy-box  /* 操作策略 — 深蓝 --c-strategy */
.danger-box    /* 风险警示 — 橙 --c-danger */
.tech-box      /* 技术分析 — 紫 --c-tech */
.cycle-box     /* 周期分析 — 棕 --c-cycle */
.stock-box     /* 个股分析 — 青 --c-stock */
```

**样式参考文件**（本技能 `references/` 目录）：
- **`references/style-reference-V3.0.html`** — **默认**。完整 CSS / 主题脚本 / 导航脚本 / SVG 素材 + 全部组件演示（抽取自 2026.11.10、11.17 两期讲义）
- `references/style-reference-V2.0.html` — 旧版，仅在用户明确要求时使用
- `references/convert_images_template.py` — 图片嵌入脚本模板（缩放 + WebP 压缩 + 缺图/残留检查）

---

## 配图嵌入规范

### HTML 中图片引用（V3.0 写法）
```html
<!-- 单图：放进 figure，标题写在 figcaption -->
<figure class="figure">
  <figcaption>两市融资余额-3.10</figcaption>
  <img class="chart-img" src="Picture/两市融资余额-3.10.png" alt="两市融资余额">
</figure>

<!-- 双图并排：img-pair（窄屏自动上下堆叠） -->
<div class="img-pair">
  <figure class="figure"><img class="chart-img" src="Picture/15秒背离-3.10.png" alt="15秒级别背离"><figcaption>15秒背离</figcaption></figure>
  <figure class="figure"><img class="chart-img" src="Picture/主要指数筹码分布对比-3.10.png" alt="主要指数筹码分布"><figcaption>筹码分布</figcaption></figure>
</div>
```

> `src="Picture/…"` 的写法保持不变，嵌入脚本照常工作。`.chart-img` / `.figure` / `.img-pair` 已在 2026.11.24 有图讲义（23 图）中实测，桌面、手机两端显示正常。

### 双端适配硬约定（手机优先）

讲义主要在手机上读。V3.0 的 CSS 已经处理好响应式，正文只要**不破坏它**：

- 图片一律放进 `.figure`（标题写在 `figcaption`）。同一主题的两张图用 `.img-pair` 并排，≤768px 时自动上下堆叠。不要用自写的 flex/grid 排图。
- 表格一律包 `.table-wrap`（窄屏可横向滑动），列数尽量 ≤5，长说明放最后一列。
- 正文**不写**固定宽度、`style="width:…"`、写死的颜色。唯一例外是 `.timebar` 的 `--w`。
- 封面标题首行 ≤5 个汉字（如「主跌未完，」「重置未完，」），否则中等宽度下会单字断行。
- 写完后按「第6步」实际打开验收，不要凭代码推断“应该没问题”。

### 图片放置页面对应关系
- 市场数据类 → 「两市融资余额」「沪深均指与融资余额/成交金额」「融资盘流入流出板块前十」页面
- 筹码分布类 → 「主要指数筹码分布对比分析」页面
- 背离分析类 → 「多级别技术分析实战体系」页面（15s/1m/4m/15m/1h/日线）
- 同一页里，数据类图片下方紧跟第0.5步整理的数据表或 `metric-row`（见「数据呈现与核对规则」）

---

## Python 图片嵌入脚本模板

**模板文件**：`references/convert_images_template.py`（以 11.24 实跑通过的脚本为蓝本）。每期复制到项目根目录，改名 `convert_images_YYYY_MM_DD.py`，**只改配置区**：

```python
HTML_FILE = "YYYY.MM.DD_类型_主题_presentation.html"
OUTPUT_FILE = "YYYY.MM.DD_类型_主题_presentation_embedded.html"
PICTURE_DIR = "Picture"
REQUIRED_IMAGES = ["两市融资金额数据汇总-11.24.PNG", ...]   # 第0步扫描得到的真实文件名
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `MAX_WIDTH` | `1600` | 宽度超过就等比缩放（LANCZOS）。图内文字很小时可调到 1800 |
| `WEBP_QUALITY` | `85` | WebP 质量。文字发糊时调到 90 |
| `TARGET_MB` | `5` | embedded 超过就提示；项目硬上限 10MB |

脚本行为：
- 需要 Pillow（`pip install pillow`）：先 `convert("RGB")`，再缩放，再转 WebP 内嵌。没有 Pillow 时退回原样嵌入，体积会大很多。
- **`Picture/` 原图不改动**，只压缩内嵌副本。
- 扩展名大小写不敏感（`resolve()` 先试精确路径，再做 `fn.lower()` 匹配）。
- 运行前检查 `REQUIRED_IMAGES` 是否齐全，并备份 `_backup.html`。
- 最后打印文件 MB 数和残留 `src="Picture/` 数。退出码 0 表示全部嵌入；2 表示有缺图或有残留。

效果参考：11.24 共 23 张图，原图合计 17MB；不压缩的 embedded 是 23MB，压缩后 3.02MB，图表文字依然清晰。

---

## 核心技术指标术语

| 指标 | 说明 |
|------|------|
| 背离分析 | 多级别（15s/1m/4m/15m/1h/日线）顶底背离 |
| 筹码分布 | 成本集中区、套牢盘、获利盘分布 |
| 融资余额 | 市场流动性与情绪综合指标 |
| 扩张平台 | 莫大独创价格整理形态理论 |
| 波段结构 | 三波段/五波段上行推动与调整 |
| BB段回撤 | 扩张平台内的标准回调位置 |

---

## 扩展知识库

重构讲义时，请同时参考：
- **[KNOWLEDGE.md](KNOWLEDGE.md)** — 莫大投资哲学、习惯用语、个股黑话、已完成讲义列表
- **[全局索引.md](全局索引.md)** — 所有讲义的关键词跨期索引，支持全文搜索定位
