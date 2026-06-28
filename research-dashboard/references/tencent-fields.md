# 腾讯财经 API 字段速查 + 已知踩坑

> URL: `https://qt.gtimg.cn/q={prefix}{code}`，多只用 `,` 拼，单批最多 25-30 只
> 编码：**GBK**（必须 `decode("gbk", errors="replace")`）
> 字段分隔：返回值用 `~` 分隔约 88 个字段
> 不限频，不需要 cookie/header

## 市场前缀

| 前缀 | 市场 | 代码格式 |
|------|------|---------|
| `sh` | 沪市 | 6位 (60xxxx, 688xxx, 9xxxxx) |
| `sz` | 深市 | 6位 (000xxx, 002xxx, 300xxx, 301xxx) |
| `bj` | 北交所 | 6位 (8xxxxx) |
| `hk` | 港股 | 5位 (00700, 02577) |
| `us` | 美股 | 字母代码 (AAPL, NVDA) |

德股（DE）/法股（FR）/瑞股（CH）/台股（TW）腾讯**不稳定**，建议直接标 `note: "XX 市场行情请另查"`。

## 关键字段索引（实测校准 2026-06-15）

| 索引 | 含义 | 示例值 |
|------|------|--------|
| 1 | 名称 | 金盘科技 |
| 2 | 代码 | 688676 |
| 3 | **当前价** | 87.74 |
| 4 | 昨收 | 80.50 |
| 5 | 今开 | 83.00 |
| 6 | 总成交量(手) | 11007401 |
| 7 | 外盘 | 6995012 |
| 8 | 内盘 | 3993179 |
| 9-18 | 买一~买五（价 + 量） | |
| 19-28 | 卖一~卖五（价 + 量） | |
| 31 | 涨跌额 | 7.24 |
| **32** | **涨跌幅%** | **8.99** |
| 33 | 最高 | 88.17 |
| 34 | 最低 | 81.80 |
| 37 | 成交额(万元) | 93961 |
| **38** | **换手率%** | 2.39 |
| **39** | **TTM PE** | 60.69 |
| 41 | 最高 | 88.17 |
| 42 | 最低 | 81.80 |
| **43** | **振幅%（不是 PB！）** | 7.91 |
| **44** | **总市值(亿元)** | 403.41 |
| **45** | **流通市值(亿元)** | 403.41 |
| **46** | **PB(市净率)** | 8.31 |
| **47** | **涨停价** | 96.60 |
| **48** | **跌停价** | 64.40 |
| 49 | 量比 | 2.18 |
| **52** | **PE(静态)** | 89.71 |
| **62** | （字段不稳定，A 股多为负数或无意义） | -2.14 |
| **65** | （字段不稳定，部分股票为预期增速但常无效） | 12.40 |

## 重大踩坑（每次都要记得）

### ⚠️ vals[62] 不是 forward PE（dynPe）

早期版本的 SKILL.md 让 `dynPe = vals[62]`，但实测：
- 金盘 688676：`vals[62] = -2.14`（同期 TTM PE = 60.69）
- 麦格米特 002851：`vals[62]` 偶尔是正数，偶尔异常大（10^6+）
- 美股 STM/Onsemi：`vals[62]` 干脆是 `8 亿`级数字（明显是别的字段）

**结论**：**直接用 `vals[39]` TTM PE 作为看板的 dynPe**，并加合理性过滤：

```python
ttm_pe = flt(vals[39]) if len(vals) > 39 else None
# 超 1e6 视为脏数据
if ttm_pe is not None and (ttm_pe > 1e6 or ttm_pe < -1e6):
    ttm_pe = None
dyn_pe = ttm_pe  # 看板内"动态 PE"统一显示 TTM PE
```

### ⚠️ vals[43] 是振幅，不是 PB

网上很多教程把 43 写成 PB——**错的**。**PB 在索引 46**。如果 SKILL 或脚本里出现 `pb: vals[43]` 立即修正。

### ⚠️ 编码必须 GBK

```python
raw = urllib.request.urlopen(url, timeout=15).read().decode("gbk", errors="replace")
```

不写 `errors="replace"` 偶尔会因奇怪字符报 UnicodeDecodeError。

### ⚠️ 字段数量校验

每只股票字段数不固定（A 股约 90、港股约 50、美股约 60）。访问 `vals[N]` 前必须 `if len(vals) > N: ...`，否则 IndexError。

```python
def flt(v, default=None):
    try: return float(v) if v and v not in ('-','--','') else default
    except: return default

ttm_pe = flt(vals[39]) if len(vals) > 39 else None
mcap   = flt(vals[44]) if len(vals) > 44 else None
```

### ⚠️ 单批最多 25-30 只

URL 太长（超过 ~700 字符）会触发腾讯端的截断。批量循环 `BATCH = 20`，每批 sleep 0.4s。

## K 线接口（260 日，用于算 5/20 日累计 + 52 周位置）

URL: `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={prefix}{code},day,,,260,qfq`

返回字段：
- A 股 / 港股：`data[prefix+code].qfqday` 或 `.day`，每行 `[日期, 开, 收, 高, 低, 成交量]`
- 美股部分：`data[prefix+code].kline`

```python
def kline_metrics(code, mkt):
    p = "sh" if (mkt in ("SH","SZ") and code.startswith(("6","9"))) else \
        "sz" if mkt in ("SH","SZ") else \
        "hk" if mkt == "HK" else \
        "us" if mkt == "US" else None
    if not p: return (None,)*4
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={p}{code},day,,,260,qfq"
    raw = urllib.request.urlopen(url, timeout=15).read().decode("utf-8", errors="replace")
    node = json.loads(raw).get("data", {}).get(p+code, {})
    k = node.get("qfqday") or node.get("day") or node.get("kline") or []
    cs = [float(r[2]) for r in k if len(r) >= 3]
    if len(cs) < 21: return (None,)*4
    cur = cs[-1]
    c5 = round((cur-cs[-6])/cs[-6]*100, 2) if len(cs) >= 6 else None
    c20 = round((cur-cs[-21])/cs[-21]*100, 2)
    hi, lo = max(cs), min(cs)
    pos = round((cur-hi)/hi*100, 1)        # 距 52 周高%（≤0）
    pct = round((cur-lo)/(hi-lo)*100, 0)   # 52 周分位 0-100
    return c5, c20, pos, pct
```

## 估值温度判断（valTag）

```python
def val_tag(dyn_pe, pos):
    """⚠ 必须传 dyn_pe（TTM PE 兜底版），传 vals[62] 会大量误判"""
    if dyn_pe is None: return "warm", "估值待察"
    if dyn_pe < 0: return "warm", "亏损"
    if dyn_pe >= 200: return "hot", "PE极高"
    if dyn_pe >= 60:
        return ("hot","高位高估") if (pos is not None and pos > -8) else ("warm","偏高")
    if pos is not None and pos <= -30: return "low", "回调低吸区"
    return "fair", "相对合理"
```

## 代码校验：用名称比对防错代码

研报里偶尔股票代码会写错（如云路 688490 实际 688190）。拿腾讯返回的 `vals[1]` 中文简称比对前 2 字：

```python
ret_name = quote.get("name", "")
if name[:2] not in ret_name and ret_name[:2] not in name:
    print(f"⚠ 代码可能错: {name}({code}) -> 腾讯返回 {ret_name}")
```
