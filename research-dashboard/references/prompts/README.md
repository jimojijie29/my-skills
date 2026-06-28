# Kimi CLI 6 轮 Prompt 模板

> 写每个看板时复用本目录下的 prompt。每份都有 `{{占位符}}` 让你按主题填空。
> 使用方式：把 .txt 复制到 `Research Report/<主题>/_synthesis/_pN_xxx.txt`，按主题改占位符，再用 `kimi_run.py -f` 传给 Kimi。

## 文件清单

| 文件 | 用途 | 占位符 |
|------|------|--------|
| `p1_read.txt` | R1 同 SID 读完所有 .md | `{{TOPIC}}` `{{N_FILES}}` |
| `p2_cost.txt` | R2 → 01_成本结构.md | `{{TOPIC}}` `{{INTEGRATOR_HINT}}` |
| `p3_parts.txt` | R3 → 02_零部件深度.md | `{{TOPIC}}` `{{ENV_LIST}}` |
| `p4_companies.txt` | R4 → 03_标的画像.md | `{{TOPIC}}` `{{TICKER_HINTS}}` |
| `p5_whitepaper.txt` | R5 → 04_行业白皮书.md | `{{TOPIC}}` `{{LEAD_DRIVERS}}` |
| `p6_serenity.txt` | R6（可选）→ 05_卡口下钻.md | `{{TOPIC}}` `{{CHOKE_HINTS}}` |

## 通用规则（每份 prompt 都已内置）

1. 全文 ASCII 优先：用 `->` 替代 `→`，`vs` 替代 `↔`，"约"替代 `~`/`≈`，"超过"替代 `>=`
2. 每条数字必须带研报来源标注（机构 + 日期）
3. 末尾明确"写入文件 _synthesis/0X_xxx.md"，让 Kimi 直接落盘
4. 单文件控制在 200-600 行 / 16-36K 字符
5. 章节固定（每份 prompt 内列出小节框架）

## 占位符使用示例（SST 项目）

```
{{TOPIC}} = "固态变压器(SST)"
{{N_FILES}} = "85"
{{INTEGRATOR_HINT}} = "金盘科技 / Eaton / Vertiv / 台达 / 中国西电"
{{ENV_LIST}} = "功率器件 / 高频变压器 / 磁性材料 / 控制IC / 电容 / 散热"
{{TICKER_HINTS}} = "金盘 688676 / 天岳 688234 / 云路 688190 / 士兰 600460 / 顺络 002138"
{{LEAD_DRIVERS}} = "AI算力 capex / 800V HVDC 标准化 / 国产替代"
{{CHOKE_HINTS}} = "SiC 8/12 英寸衬底 / 纳米晶薄带及母合金 / 隔离驱动 IC"
```

## 调用方式

```bash
# 1. R1 用 -p 直接传（短）
kimi_run.py -S "<topic>-$(date +%s)" -w "<work_dir>" -p "$(cat p1_read.txt | sed 's/{{TOPIC}}/SST/' | sed 's/{{N_FILES}}/85/')"

# 2. R2-R6 长 prompt 写文件再传
sed -i 's/{{TOPIC}}/SST/g; s/{{INTEGRATOR_HINT}}/金盘科技/Eaton/g' _synthesis/_p2_cost.txt
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python kimi_run.py \
  -S "<sid>" -w "<work_dir>" -f "<work_dir>/_synthesis/_p2_cost.txt" --timeout 2400
```

## 反模式

- ❌ 修改占位符时只改第一处（多处出现的全替换用 `sed -e`）
- ❌ 直接复制 `serenity方法论.md` 进 p6 prompt（用 `references/serenity-methodology.md` 已内置 ASCII 友好版）
- ❌ R6 prompt 不点名候选卡口（让 Kimi 凭空找最深卡口几乎必然写成清单，必须给 2-3 个候选让它论证或证伪）
