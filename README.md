# My Claude Skills

个人维护的 [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) skills 合集，主要服务于投研资料整理与金融直播讲义制作。

| Skill | 一句话说明 | 主要依赖 |
|-------|-----------|---------|
| [kimi-delegate](kimi-delegate/) | 把“海量长文本 → 蒸馏成精简产物”的重活外包给本机 Kimi CLI，Claude 只负责编排 | Kimi Code CLI 2.x、Python 3 |
| [research-dashboard](research-dashboard/) | 把一个目录的多篇 .md 研报压缩成单文件 HTML 投研看板 | kimi-delegate、Python 3 |
| [moda-lecture-reconstruction](moda-lecture-reconstruction/) | 把莫大仙岳居的金融直播口播稿重构为阅读式 HTML 讲义 | Python 3 + Pillow |

---

## kimi-delegate

让 Claude Code 把吃上下文的长文本任务外包给本机 Kimi CLI，例如读几十篇长文档或超大代码库、多文档去重合并、批量结构化抽取。Kimi 上下文长、单价低，读完后直接把结果落盘成几份结构化中间产物，Claude 只读这些精简产物再继续工作，从而省 context、省钱、提速。

- **触发场景**：用户说“用 Kimi 处理 / 提炼 / 总结这堆文件”，或任务形态是“海量长文本 → 精简产物”。
- **核心套路**：
  - 第 1 轮只读不产出，后续轮用同一个会话直接产出（`--session-file` 自动记录并续接会话 ID）。
  - 产物让 Kimi 直接写文件，不回灌给 Claude。
  - Kimi 给出的数字、编号要二次校验。
- **统一入口** `scripts/kimi_run.py`：
  - 适配 Kimi Code CLI 2.x。
  - 处理了 Windows 下中文 / 特殊字符的 UTF-8 问题。
  - 带路径探测和会话 ID 抓取。
  - 退出码有约定：127 找不到 kimi，124 超时。
- **文件**：
  - `SKILL.md`：使用说明与常见陷阱
  - `scripts/kimi_run.py`：调用封装
  - `references/multi-doc-synthesis.md`：多文档合成的端到端示例
  - `evals/`：评测用例

## research-dashboard

把 `Research Report/<主题>/` 下的多篇 .md 研报压缩成**单文件、零依赖**的 HTML 投研看板，约 5 分钟就能重建一条产业链的心智地图。

- **工作流**：
  1. 用 Kimi CLI 把全部研报提炼成 5 份基础合成报告：成本结构、零部件深度、标的画像、行业白皮书、卡口下钻。
  2. Claude 读这些合成报告，生成看板 HTML。
- **看板内容**：
  - A 股行情快照，可一键刷新腾讯行情
  - 公司速查矩阵（含 ROE 占位）
  - 产业链分层图、时间轴、风险卡
  - 🎯 serenity 视角的卡口下钻
- **文件**：
  - `references/dashboard-skeleton.html`：看板骨架
  - `references/prompts/`：6 份 Kimi 提炼 prompt 模板
  - `references/data-schema.md`、`references/tencent-fields.md`、`references/css-themes.md`：数据结构、腾讯行情字段、主题样式
  - `references/serenity-methodology.md`：卡口方法论

## moda-lecture-reconstruction

把莫大仙岳居的金融直播口播稿（公域 / 私域直播）重构为结构化的 HTML 讲义。讲义采用 V3.0 阅读式模板：纸面单栏加深蓝章节带，支持日间 / 夜间切换，宽屏有左侧目录栏，手机端有顶栏下拉目录。

- **工作流**：
  1. 扫描图片，并对数据类图片读图取数。
  2. 一次写入完整 HTML。
  3. 同步写一份 Markdown 笔记，便于全文检索。
  4. 跑脚本压缩嵌入图片。
  5. 在浏览器里做桌面 / 手机双端验收。
- **主要特点**：
  - **读图取数**：读出融资、国债、TGA、汇率等数据图里的数值，与口播交叉核对；有出入的写进校注，关键数据在图旁单独列表。
  - **压缩嵌入**：图片缩到 ≤1600px 宽、转 WebP 后以 Base64 内嵌，输出可独立分发的 HTML（例：23 张图约 3MB）。
  - **配色规范**：行情涨跌严格按 A 股习惯，涨红跌绿。
- **文件**：
  - `SKILL.md`：工作流与组件规范
  - `KNOWLEDGE.md`：讲师用语与已完成讲义清单，仅保存在作者本地，不随仓库公开
  - `references/style-reference-V3.0.html`：默认样式模板（V2.0 为旧版）
  - `references/convert_images_template.py`：图片嵌入脚本模板

---

## 安装

把需要的 skill 目录复制到 Claude Code 的 skills 目录即可：

- 个人级：`~/.claude/skills/<skill-name>/`
- 项目级：`<项目根目录>/.claude/skills/<skill-name>/`

注意：kimi-delegate 和 research-dashboard 里的 Kimi / Python 路径是按作者本机（Windows）写的，换机器时请修改 `kimi_run.py` 顶部的 `KIMI_CANDIDATES` 以及 SKILL.md 中的路径。
