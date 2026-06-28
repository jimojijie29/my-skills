# 看板 CSS 主题色与配色规范

> 本文件给出 4 套已验证的黄金主题色组合，做新看板时**直接抄一套**改 `:root` 即可，**不要自创色系**。
> 命名约定：`--accent`（主色）/`--accent2`（辅色）/`--warm`（数字徽章/强调色）/`--purple`（serenity Tab 专用）。

## 色卡选择决策树

```
是否含 serenity 第 6 Tab（扩展 H）？
│
├─ 否（基础 5 Tab）
│  ├─ 主题"科技/电力/AI"：选 蓝青（SST 配色）
│  ├─ 主题"机器人/具身智能"：选 紫橙（机器人配色）
│  └─ 主题"英伟达/算力"：选 绿色（Rubin 配色）
│
└─ 是（含卡口下钻 6 Tab）
   ├─ 主体已是紫色（机器人）：serenity 改用 青绿（cyan）避免撞色
   ├─ 主体是蓝/绿（SST/Rubin）：serenity 用 紫色（purple）✓ 默认推荐
   └─ 主体是橙/红：serenity 用 蓝色（blue）
```

---

## 主题 1：SST 蓝青（已交付）

适用：电力/电子/AI 算力等"高科技 + 严肃 + 偏蓝"主题。

```css
:root{
  --bg:#050a14;            /* 深蓝黑底 */
  --panel:#0a1322;         /* 主面板 */
  --panel2:#0f1a2e;        /* 次级面板 */
  --border:#1c2a44;        /* 边框 */
  --text:#e8efff;          /* 主文字 */
  --muted:#7a8caa;         /* 次级文字 */

  --accent:#3b82f6;        /* 主色：天空蓝 */
  --accent2:#60a5fa;       /* 辅色：浅蓝 */
  --warm:#fbbf24;          /* 数字徽章：金黄 */

  --green:#10b981;
  --red:#ef4444;
  --yellow:#eab308;
  --purple:#a78bfa;        /* serenity Tab 专用紫 */
  --cyan:#22d3ee;          /* 备用青 */

  --g1:linear-gradient(135deg,#3b82f6,#60a5fa);
  --g2:linear-gradient(135deg,#0ea5e9,#22d3ee);
  --g3:linear-gradient(135deg,#a78bfa,#60a5fa);  /* serenity */
  --glow:0 0 18px rgba(59,130,246,0.22);
  --glow2:0 0 14px rgba(34,211,238,0.18);
  --glow3:0 0 18px rgba(167,139,250,0.20);
}
[data-theme="light"]{
  --bg:#f1f5fb;--panel:#fff;--panel2:#e6eef9;--border:#bfd1ea;
  --text:#0c1726;--muted:#4d5e7c;--accent:#1d4ed8;--accent2:#2563eb;
}
```

参考：`Research Report/固态变压器/SST投研看板2.0.html`

---

## 主题 2：机器人紫橙（已交付）

适用：机器人/具身智能/可穿戴等"创新 + 偏暖 + 紫橙"主题。

```css
:root{
  --bg:#0a0612;
  --panel:#150e23;
  --panel2:#1d152d;
  --border:#2d2245;
  --text:#f0e8ff;
  --muted:#9d8bb8;

  --accent:#a855f7;        /* 主色：紫 */
  --accent2:#c084fc;       /* 辅色：浅紫 */
  --warm:#f59e0b;          /* 数字徽章：橙（与紫互补）*/

  --green:#10b981;
  --red:#ef4444;
  --purple:#a855f7;        /* 与主色相同，注意 */

  /* serenity Tab 撞色风险：主色已是紫，必须改用 cyan */
  --serenity:#22d3ee;      /* serenity 改用青绿 */

  --g1:linear-gradient(135deg,#a855f7,#c084fc);
  --g2:linear-gradient(135deg,#f59e0b,#f97316);
}
```

⚠️ **当机器人主题做扩展 H 时**：把 `.tab.serenity.active`、`.section-title.serenity` 等紫色样式全替换为 `--cyan`。即将 SKILL 里"扩展 H 用紫色"全部映射为"机器人主题下用青绿"。

参考：`Research Report/机器人/机器人产业链投研看板.html`

---

## 主题 3：Rubin 绿（已交付）

适用：英伟达/算力 capex/PCB/光模块等"科技 + 偏绿 + 高对比"主题。

```css
:root{
  --bg:#060c05;
  --panel:#0d1608;
  --panel2:#131e0b;
  --border:#1e2f12;
  --text:#e8f2de;
  --muted:#8ba079;

  --accent:#76b900;        /* 主色：英伟达绿 */
  --accent2:#a3e635;       /* 辅色：浅绿 */
  --warm:#fbbf24;          /* 数字徽章：金 */

  --red:#ef4444;
  --yellow:#eab308;
  --purple:#a78bfa;        /* serenity Tab 备用 */

  --g1:linear-gradient(135deg,#76b900,#a3e635);
  --g2:linear-gradient(135deg,#fbbf24,#f97316);
  --glow:0 0 18px rgba(118,185,0,0.18);
}
[data-theme="light"]{
  --bg:#f4f9ee;--panel:#fff;--panel2:#eaf4d8;--border:#cce0a8;
  --text:#14200a;--muted:#4f6a36;--accent:#5a8f00;--accent2:#76b900;
}
```

参考：`Research Report/英伟达rubin/英伟达Rubin产业链投研看板.html`

---

## 主题 4：serenity 紫色叠加（扩展 H 专属）

不是独立主题，是叠加在主题 1/3 之上的"第 6 Tab 专属配色"。

```css
:root{
  /* ...主题 1/3 的所有变量保留... */
  --purple:#a78bfa;
  --g3:linear-gradient(135deg,#a78bfa,#60a5fa);  /* 配蓝 */
  --glow3:0 0 18px rgba(167,139,250,0.20);
}

/* serenity Tab 专属类（与基础 5 Tab 区分）*/
.tab.serenity.active{
  color:var(--purple);
  border-bottom-color:var(--purple);
  background:rgba(167,139,250,0.10);
}
.section-title.serenity::before{background:var(--g3);}

.choke-hero{
  background:linear-gradient(135deg,rgba(167,139,250,0.10),var(--panel));
  border:1px solid rgba(167,139,250,0.30);
  border-radius:var(--radius);padding:22px;margin-bottom:20px;
}
.choke-hero h2{color:var(--purple);}
.choke-hero .lead em{color:var(--purple);font-weight:700;}

/* 树根图（ASCII）*/
.tree{
  font-family:'JetBrains Mono',Menlo,Consolas,monospace;
  font-size:12px;background:var(--panel2);
  border:1px solid var(--border);
  padding:18px;white-space:pre;overflow-x:auto;line-height:1.65;
}
.tree mark{background:rgba(167,139,250,0.18);color:var(--purple);padding:0 4px;border-radius:3px;}

/* 4 张物理追问表 */
.qa-table{width:100%;border-collapse:collapse;font-size:12.5px;}
.qa-table th,.qa-table td{
  border-bottom:1px solid var(--border);padding:9px 11px;
  text-align:left;vertical-align:top;
}
.qa-table thead th{background:var(--panel2);color:var(--accent2);font-weight:700;}
.qa-table .y{color:#34d399;font-weight:700;}     /* 是 */
.qa-table .n{color:var(--muted);}                /* 否 */
.qa-table .choke-hit{                            /* 卡口行整行紫色 */
  background:rgba(167,139,250,0.10);
  font-weight:700;color:var(--purple);
}

/* 卡口中卡口卡片（每个深卡口一张）*/
.deep-card{
  background:linear-gradient(135deg,rgba(167,139,250,0.06),var(--panel));
  border:1px solid rgba(167,139,250,0.30);
  border-radius:var(--radius);padding:18px;margin-bottom:14px;
}
.deep-card h4{color:var(--purple);font-weight:800;}
.deep-card .targets{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.deep-card .targets .pill{
  background:rgba(167,139,250,0.10);
  border:1px solid rgba(167,139,250,0.32);
  color:var(--purple);padding:4px 11px;border-radius:14px;font-size:12px;font-weight:600;
}
.deep-card .targets .pill.cn{                    /* A 股标的用蓝色 */
  background:rgba(59,130,246,0.10);
  border-color:rgba(59,130,246,0.4);color:var(--accent2);
}

/* 免责说明（紫色虚线框）*/
.demur{
  background:rgba(167,139,250,0.05);
  border:1px dashed rgba(167,139,250,0.4);
  border-radius:var(--radius-sm);
  padding:12px 14px;font-size:12px;color:var(--muted);
}
.demur b{color:var(--purple);}

/* 公司卡片：含 🎯 字符的 tag 自动套紫色 */
.tag.choke{
  background:rgba(167,139,250,0.12);
  border-color:rgba(167,139,250,0.4);
  color:var(--purple);font-weight:700;
}
```

---

## 通用规范（所有主题都遵守）

### 数字徽章颜色规则

`.badge .num` 用 `--g1` 主色渐变，`.tier-1` 黄色（`--warm`），`.tier-2` 主色，`.tier-3` 灰色。

### 涨跌色（A 股反向）

```css
.up{color:#f87171;}     /* 红 = 涨 */
.down{color:#34d399;}   /* 绿 = 跌 */
```

注意 A 股是"红涨绿跌"，与美股相反——所有主题统一遵守 A 股惯例。

### 估值温度（valTag）

```css
.vtag.hot{background:rgba(239,68,68,0.18);color:#f87171;}    /* PE极高/高位高估 */
.vtag.warm{background:rgba(251,191,36,0.14);color:var(--warm);}  /* 偏高/亏损 */
.vtag.fair{background:rgba(主色,0.14);color:var(--accent2);}    /* 相对合理 */
.vtag.low{background:rgba(16,185,129,0.14);color:#34d399;}    /* 回调低吸区 */
```

`.vtag.fair` 的颜色随主题变（蓝主题用蓝、绿主题用绿）。

### Light 模式

每个主题都建议提供 `[data-theme="light"]` 覆盖，确保 `--bg`/`--panel`/`--text` 三色能切换。Light 模式只覆盖关键变量，渐变和 vtag 颜色继承即可。

---

## 选色规则总结

1. **不要自创色系**：上面 4 套已验证，新主题挑差异化的复用
2. **避免与已交付看板撞色**：SST 蓝、机器人紫橙、Rubin 绿，三个色系互不重合
3. **serenity Tab 主色不能等于基础 Tab 主色**：机器人主题做扩展 H 时强制改用 `--cyan`
4. **数字徽章用 `--g1` 渐变文字**：所有主题统一规范
5. **涨跌色 A 股反向**（红涨绿跌）所有主题统一
