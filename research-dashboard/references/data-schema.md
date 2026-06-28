# 看板 8 个数据数组完整字段定义

> 本文件是数据契约。Explore agent 抽数据时严格按本表给字段，HTML 渲染函数也按本表读字段。
> 任何字段语义变更必须先改本文件、再改 dashboard-skeleton.html。

## 数组速览

| 数组 | 数量 | 渲染于 Tab | 必填 |
|------|------|-----------|------|
| `OVERVIEW` | 1 个对象 | 概览 | 是 |
| `CHAIN` | 3 层 × 4-7 节点 | 产业链 | 是 |
| `COMPANIES` | 30-67 家 | 公司速查 | 是 |
| `TIMELINE` | 10-14 条 | 时间轴 | 是 |
| `RISKS` | 6-12 条 | 风险与逻辑 | 是 |
| `SCORES` | 25-30 行 | 公司速查 (矩阵视图) | 扩展 B |
| `GENERATIONS` | 8-12 行 | 产业链顶部 | 扩展 E |
| `ELASTICITY` | 5-8 行 | 概览底部 | 扩展 C |
| `SCENARIOS` | 6 行 × 3 列 | 概览底部 | 扩展 D |
| **serenity 扩展（含扩展 H 时）** | | | |
| `SERENITY_TREE` | 1 个字符串 | 卡口下钻 | 扩展 H |
| `SERENITY_QA` | 4 张表 | 卡口下钻 | 扩展 H |
| `DEEP_CHOKES` | 2-3 个对象 | 卡口下钻 | 扩展 H |
| `CHOKE_PURGE` | 3-5 行 | 卡口下钻 | 扩展 H |
| `CONFIDENCE` | 2 字段 | 卡口下钻 | 扩展 H |
| `SERENITY_DEMUR` | 1 个字符串 | 卡口下钻 | 扩展 H |

---

## 1. OVERVIEW（概览 Tab）

```js
const OVERVIEW = {
  tagline: '...',  // 一句话定位，含 <em>...</em> 黄色高亮关键词
  badges: [
    { num: '~115亿', lbl: '2027 全球市场空间' },
    // 8-12 个 KPI 数字徽章
  ],
  inflections: [
    { y: '2018-2024', t: '实验室阶段', d: '...' },
    { y: '2025', t: '战略拐点', d: '...' },
    { y: '2026', t: '商业化启动', d: '...' },
    { y: '2027-2030', t: '放量期', d: '...' },
  ],
  logics: [
    { t: '逻辑标题', d: '逻辑描述（≤80字）', tags: ['公司A','公司B'] },
    // 3 大投资逻辑
  ]
};
```

**字段说明**：
- `tagline`：可含 `<em>...</em>` 标签做黄色高亮，<= 200 字
- `badges`：每行展示一个数字徽章，4 列网格自适应
- `inflections`：4 阶段，渲染为 4 个卡片（不强制写"年-年"，"2025-Q3"这类格式也行）
- `logics`：每条 `tags` 是受益标的列表，渲染时套 `.tag.cust` 紫色

## 2. CHAIN（产业链 Tab 主体）

```js
const CHAIN = [
  {
    layer: '上游 · 核心零部件',
    pct: '占整机 BOM ~55-65%',  // 该层占比/特征徽章
    nodes: [
      {
        key: 'power_device',  // 与 COMPANIES.seg 严格对齐，点节点跳公司速查
        t: '① 功率器件 (32-40%)',
        d: 'SiC MOSFET / IGBT 模块。海外主导，国产追赶'
      },
      // 4-7 个节点
    ]
  },
  // 3 层（上中下游）
];
```

**字段说明**：
- `key` 必须与 `COMPANIES[].seg` 完全一致；新增 key 同时要更新 `SEG_NAMES` 字典
- `t` 节点标题，开头用 `①②③` 序号 + (% BOM 占比)
- 点 node 的事件绑定通过 `data-seg` 跳到公司速查 Tab

## 3. COMPANIES（公司速查 Tab 主体）

```js
{
  // 基础
  name: '金盘科技',
  code: '688676',           // 6位数字 / 港股 5 位 / "STM"等海外代码 / "UNLISTED"
  mkt: 'SH',                // SH/SZ/HK/US/TW/DE/FR/CH/UNLISTED
  seg: 'integration',       // 与 CHAIN.nodes.key 严格对齐
  tier: 1,                  // 1=核心 / 2=弹性 / 3=储备
  rating: 5,                // 1-5 星

  // 内容
  highlights: '...',        // 1-2 句关键看点（80-150 字）
  milestones: ['2025-08 完成 10kV 样机', '...'],
  customers: ['英伟达'],    // 客户标签，紫色高亮
  tags: ['SST 龙一', 'AIDC', '🎯 最深卡口'],  // 普通标签；含 🎯 自动套紫色

  // 行情字段（A/H/US 必填，海外仅 note 时为 null）
  price: 87.07,
  change: 8.16,             // 当日涨跌幅 %
  dynPe: 60.87,             // 动态 PE（用 TTM PE 兜底，详见 tencent-fields.md）
  roe: null,                // 净资产收益率 %（加权平均 ROE，腾讯接口不返回；预留占位
                            //   等用户提供数据接口后批量补全；UI 与 dynPe 并列显示）
  pegGrowth: 28.5,          // 预期净利润增速 %
  peg: 2.13,                // dynPe / pegGrowth；<1 绿色 / 1-3 正常 / >3 红
  marketCap: 403.41,        // 总市值（亿元）
  chg5d: -3.18,
  chg20d: 19.75,

  // 52 周位置（260 日 K 线派生，扩展 A）
  pos52w: -17.5,            // 距 52 周高 %
  pct52w: 75,               // 52 周分位 0-100
  valTag: 'warm',           // hot/warm/fair/low（基于 dynPe + pos52w）
  valLbl: '偏高',           // 估值标签文案

  // 海外/未上市
  note: '海外行情请另查'    // price=null 时显示
}
```

**强制约束**：
- `seg` 必须是 `SEG_NAMES` 字典里有的 key；新增环节同时改字典 + CHAIN.nodes
- `code` 用 Python 脚本验证（拿腾讯返回名称比对前 2 字），错代码会污染整个看板
- `tier` 数字越小越核心；T1 占 6-12 家，T2 占 12-20 家，T3 占 10-30 家
- `tags` 含 `🎯` emoji 字串时自动套 `.tag.choke` 紫色（标记 serenity 视角的最深卡口候选）
- `roe` 字段必须保留，腾讯接口不返回 → 默认 `null` 占位；外部数据接入后批量补；浏览器一键刷新行情时**不覆盖** `roe`

**估值温度（valTag）判断逻辑**（用 `dynPe` 计算，**不要用 TTM PE**）：
- `hot`：dynPe ≥ 200，或（dynPe ≥ 60 且 pos52w > -8%）
- `warm`：dynPe 60-200，或 dynPe 为负（亏损预期）
- `fair`：dynPe < 60 且非低吸区
- `low`：dynPe < 60 且 pos52w ≤ -30%（深度回调）

## 4. TIMELINE（时间轴 Tab）

```js
const TIMELINE = [
  { when: '2025-08', t: '关键事件标题', d: '事件描述（含研报来源）' },
  // 10-14 条，按时间正序
];
```

字段简单。`when` 用 `YYYY-MM` 或 `YYYY-Qn` 格式；`d` 末尾标研报来源（如 `——华安证券 2025-08-29`）。

## 5. RISKS（风险与逻辑 Tab）

```js
const RISKS = [
  { lvl: 'r', t: '风险标题', d: '说明', src: '来源：研报共识 + XX 证券 YYYY-MM' },
  { lvl: 'b', t: '🔶 bear case 标题', d: '反向逻辑', src: '🔶 非研报观点，分析师补充' },
];
```

**lvl 取值**：
- `r` 红色：高风险（技术 / 估值透支）
- `y` 黄色：中风险（商业 / 客户）
- `g` 绿色：正面催化（政策 / 标准）
- `b` 紫色：bear case（必须加"非研报观点"标注，与研报观点物理隔离）

## 6. SCORES（三维评分矩阵，扩展 B）

```js
const SCORES = [
  { name: '金盘科技', code: '688676', seg: 'integration',
    v: 5.0, c: 4.5, b: 4.5, total: 4.7, note: 'SST 龙一明牌' },
  // 25-30 行
];
```

- `v` 价值量弹性 / `c` 客户确定性 / `b` 国产化壁垒，5 分制
- `total = (v+c+b) / 3`，向 0.1 取整
- 矩阵视图表头点击切换排序

## 7. GENERATIONS（多代际演进对比，扩展 E）

```js
const GENERATIONS = {
  cols: ['上代', '当代★', '下一代', '远期'],
  rows: [
    { field: '指标名', vals: ['v1', 'v2', 'v3', 'v4'] },
    // 8-12 行
  ],
  note: '当代列高亮★；远期含推算，置信度递减'
};
```

- `cols` 通常 4 列（上代/当代/下代/远期），当代列加 ★
- 渲染时当代列（index=1 或 2，按主题）套 `.hl` 黄色

## 8. ELASTICITY（环节弹性测算，扩展 C）

```js
const ELASTICITY = [
  { seg: '功率器件',
    node: 'SiC MOSFET',
    bomPct: '32-40%',
    perRack: '~290-450 万/MW',  // 单整机/单 GW 价值量
    leader: '天岳 / 士兰 / STM',
    share: '海外 80%+',
    m26: '~50亿',
    m27: '~90亿',
    note: '衬底 40% 降价可传导 4-6 pct 整机降本'  // 可选
  },
];
```

末尾必须有 `note` 字段标"为量级测算，非精确预测"。

## 9. SCENARIOS（三情景表，扩展 D）

```js
const SCENARIOS = {
  rows: [
    { f: '出货量(2027)', bear: '~6万台', base: '~9万台', bull: '~12万台+' },
    // 6 行：出货量/渗透率/市场规模/单价/A 股链含义/...
  ],
  note: '量级敏感性示意，非精确预测'
};
```

bear/base/bull 三列分别套红/中/绿色。

---

## serenity 扩展（扩展 H，6 个数据结构）

### 10. SERENITY_TREE（树根图）

```js
const SERENITY_TREE = `整机龙头
        |
        v
... 用 ASCII 字符画的树根图，关键卡口节点用 <mark>...</mark> 紫色高亮 ...`;
```

末尾包裹在 `<div class="tree">${SERENITY_TREE}</div>` 里，CSS 已为 `.tree mark` 设紫色背景。

### 11. SERENITY_QA（4 层物理追问表）

```js
const SERENITY_QA = {
  layer1: { title: '4.1 整机层', rows: [
    { node: 'SST 整机', oligo: '海外 60%+', expand: '1-2 年', alt: 'HVDC 可替代', mustUse: '终局必用', isChoke: '否' },
  ]},
  layer2: { title: '4.2 部件层', rows: [/*...*/] },
  layer3: { title: '4.3 材料层', rows: [/*...*/] },
  layer4: { title: '4.4 专用设备层 (资料薄)', rows: [/*...*/] },
};
```

- `isChoke` 取值 `'否(替代多)'` / `'弱卡口'` / `'中卡口'` / `'强卡口'` / `'深卡口'`
- 渲染时 `isChoke` 含"卡口"且非"否"的整行套 `.choke-hit` 紫色高亮

### 12. DEEP_CHOKES（卡口中卡口，2-3 个）

```js
const DEEP_CHOKES = [
  {
    name: 'SiC 8/12 英寸衬底',
    reasons: [
      '不可替代：硅基 IGBT 在开关频率与损耗上无法替代',
      '供给刚性：8 英寸 2-3 年扩产；12 英寸 3-5 年',
      '寡头垄断：Wolfspeed / 天岳 / Coherent；天岳市占 22.8%',
      '没人看见：市场盯模块/器件，衬底是"材料里的材料"'
    ],
    transmission: '英伟达 800V DC -> SST 整机 -> SiC MOSFET -> SiC 衬底',
    targets: [
      { kind: 'cn', label: 'A 股：天岳先进 688234' },
      { kind: 'oversea', label: '海外：Wolfspeed (WOLF)' },
    ]
  },
  // 严格 2-3 个
];
```

- `reasons` 必须 4 条，分别对应 serenity 四个物理追问
- `targets[].kind` 取 `cn`(A 股，蓝色) / `oversea`(海外，紫色) / `hk`(港股，紫色)

### 13. CHOKE_PURGE（多维排雷）

```js
const CHOKE_PURGE = [
  { name: '天岳先进', code: '688234',
    capacity: '8 英寸批量；12 英寸已展出',
    orders: '切入英飞凌/博世/安森美',
    cert: '多家 Tier1 车规',
    val: '2027E PE 约 89 倍',
    gov: '实控人稳定，无重大减持',
    verdict: '值得跟踪'
  },
  // 3-5 家
];
```

`verdict` 取值 `'值得跟踪'` / `'待观察'` / `'暂避'`。

### 14. CONFIDENCE（置信度分层）

```js
const CONFIDENCE = {
  high: '超级周期 / 龙头入口 / SiC 衬底市占——多源研报交叉验证',
  medium: '专用设备层 / "没人看见"维度——研报覆盖薄 / 主观判断'
};
```

### 15. SERENITY_DEMUR（免责说明）

```js
const SERENITY_DEMUR = '本 Tab 是 serenity 方法论产物，不是研报共识。卡口候选可能因技术迭代而失效。本视角与"概览/产业链"形成对照——04 选整机+下游，05 选上游+材料，两者几乎不重合。不构成投资建议。';
```

包裹在 `<div class="demur">` 紫色虚线框里。

---

## 字段对齐自检清单

写完 _data.js 后，run 这段 Python 校验：

```python
import re
text = open('SST投研看板.html', encoding='utf-8').read()

# 1. seg 一致性：所有 COMPANIES[].seg 必须出现在 SEG_NAMES 字典里
seg_names = set(re.findall(r"'(\w+)':", text.split('SEG_NAMES = {')[1].split('}')[0]))
company_segs = set(re.findall(r"seg:\s*['\"](\w+)['\"]", text))
unknown = company_segs - seg_names
assert not unknown, f"未定义的 seg: {unknown}"

# 2. CHAIN.nodes.key 必须是 SEG_NAMES 子集
# 3. COMPANIES[].code 用 Python 拿腾讯接口名称二次校验

# 4. 各数组数量
assert text.count('{name:') >= 30, "COMPANIES 不足 30 家"
assert 2 <= text.count('reasons:') <= 3, "DEEP_CHOKES 必须 2-3 个"
```
