---
name: kimi-delegate
description: 让 Claude Code 把"读海量长文本/代码 → 压缩、总结、去重合并、批量结构化抽取"这类吃上下文的脏活外包给本机 Kimi CLI（长上下文、便宜、可落盘），Claude 自己只负责编排并消费蒸馏后的结果。当用户说"用 Kimi 处理/提炼/总结这堆文件"、要读几十篇长文档或超大代码库、做多文档去重合并、把一堆原始材料压成几份结构化中间产物，或任何"单次塞进 Claude 上下文不划算"的长文本任务时，主动使用本 skill。即使用户没点名 Kimi，只要任务形态是"海量长文本 → 蒸馏成精简产物"且本机装了 Kimi CLI，也应考虑用它来省 context、省钱、提速。
---

# Kimi 外包：Claude 编排，Kimi 干重活

## 核心理念

Claude Code 擅长**编排、结构化输出、写代码、调工具**；Kimi CLI 擅长**长上下文的"读海量、去重、合并、压缩"**且单价低。把两者拼起来：

> 让 Kimi 把"几十万字原始材料"嚼成几份"几百行的结构化中间产物"，Claude 只读这些中间产物再干自己擅长的活。

这样做的收益：
- **省 context**：Claude 不必把 30 万字塞进自己窗口，只读蒸馏后的 ~500 行。
- **省钱提速**：长文档去重合并是 Kimi 的主场，比 Claude 自己硬读便宜得多。
- **可落盘复用**：Kimi 直接把产物写成文件，成为后续可迭代的中间资产。

**判断要不要外包**：

**第一原则——用户说了算**。只要用户**明确点名"用 Kimi"/"让 Kimi 来"/"外包给 Kimi"**，就直接照办、按下面的流程跑，**不要用"体量太小"去否决用户的明确指令**。哪怕输入不大，用户既然指定了 Kimi（可能是想省自己 context、或想对比、或后续还要追加大批量），照做即是。下面的"体量启发式"只用于**用户没指定、由你自己拿主意**的场合。

用户没指定时，由你判断：
- ✅ 输入是"多篇长文 / 超大代码库 / 一堆原始材料"，且目标是"压成精简产物"
- ✅ 用户明说"别全塞进你自己上下文"/"你别直接读"——这是要你外包的强信号
- ✅ 同一批输入要产出多份不同切面的总结（一次读、多次产出，session 复用收益大）
- ✅ 任务重复枯燥但量大（批量抽取、批量改写）
- ⚖️ 输入小、你一眼能读完，且用户没点名 Kimi → 直接做更快，没必要起 Kimi
- ⚠️ 需要精确事实/数字且不可错 → 可外包初稿，但**必须二次校验**（Kimi 长文去重稳，但具体百分比/代码/编号会漂）
- ⚠️ 需要调用本项目专有工具链/MCP 才能完成 → 留给 Claude 自己做

---

## 步骤 0：定位 kimi / python（本机不在 PATH）

本机（Windows 11，bash 缺 coreutils）裸命令 `kimi`/`python` 都不在 PATH，**优先用硬编码全路径**，命中不了再探测：

- Kimi Code CLI 2.x（2026-11 实测 2.4.1）：`C:\Users\Administrator\.kimi-code\bin\kimi.exe`
- Python 3.12：`C:\Users\Administrator\scoop\shims\python.exe`
- 本 skill 脚本：`C:\Users\Administrator\.claude\skills\kimi-delegate\scripts\kimi_run.py`

`kimi_run.py` 内部已带路径探测兜底，换机器时改它顶部的 `KIMI_CANDIDATES` 即可。

> `~/.local/bin/` 下的 `kimi-cli.exe`（1.x）和 `kimi-legacy.exe` 是旧版，官方已停止维护，**别用**。
> 旧版的 `--quiet / --afk / -w` 和自定义 `-S <任意名>` 在 2.x 里都没了，脚本已按 2.x 重写。
文件系统操作用 Glob/Read 工具或 `python -c`，**别用 ls/cat/find**（本机 bash 无 coreutils）。

---

## 步骤 1：用封装脚本调 Kimi（不要直接 bash 拼参数）

**统一入口是 `scripts/kimi_run.py`**，它封好了 headless 调用 + UTF-8 安全 + 路径探测 + 会话 ID 抓取：

```bash
PY="C:/Users/Administrator/scoop/shims/python.exe"
RUN="C:/Users/Administrator/.claude/skills/kimi-delegate/scripts/kimi_run.py"

# 多轮（推荐）：会话文件。首轮新建会话并把 ID 存进去，后续轮自动续接
"$PY" "$RUN" --session-file "<工作目录>/_out/.kimi_session" -w "<工作目录>" -p "<指令>"

# 长/复杂/含特殊字符的 prompt：写 UTF-8 文件再传（最稳）
"$PY" "$RUN" --session-file "<工作目录>/_out/.kimi_session" -w "<工作目录>" -f "/tmp/kimi_prompt.txt"

# 单轮：不传会话参数 = 新会话；或 -S session_xxx 显式续接
"$PY" "$RUN" -w "<工作目录>" -p "<指令>"
```

脚本实际跑的是 `kimi [-S <ID>] [-m <模型>] -p <prompt>`，进程 cwd 设为 `-w`。参数：
| 参数 | 作用 |
|---|---|
| `--session-file <路径>` | 存在则续接其中的会话；运行成功后写入本轮会话 ID。**多轮全程用同一个文件 = 只读一次输入** |
| `-S <session_xxx>` | 显式续接已知会话（和 `--session-file` 二选一） |
| `-w <dir>` | Kimi 的工作目录（即进程 cwd），它在这里读输入、写产物 |
| `-p` / `-f` | prompt 文本 / prompt 文件 |
| `-m` / `--timeout` / `--verbose` | 模型别名 / 超时秒数 / 转发 Kimi 的思考过程（stderr）调试用 |

输出约定：stdout 只有 Kimi 的最终答案（已去掉 `• ` 前缀和续行缩进）；stderr 一行 `[kimi_run] session: session_xxx`。
退出码：kimi 本身的退出码；找不到 kimi=127，超时=124，工作目录不存在=2，用会话文件却抓不到 ID=3。

Kimi Code 2.x 的几个硬约束（脚本已处理，直接调 kimi 时要记得）：
- `-p` 模式下读写文件自动执行，不需要也**不能**加 `-y`/`--yolo` 或 `--auto`（会报 `Cannot combine --prompt with ...`）。
- 没有 `-w`，工作目录就是进程 cwd；需要额外目录用 `--add-dir`。
- 会话 ID 不能自定义，只能从首轮 stderr 末尾 `To resume this session: kimi -r session_xxx` 里抓。

> 为什么不直接 bash `kimi -p "中文..."`：Windows 下中文/特殊字符进 argv 容易 GBK 崩，
> 打印 Kimi 输出（含 `•`）到 GBK 控制台也会崩。脚本走 python subprocess（宽字符 API）+ UTF-8 输出，已实测 `↔ → ≈` 不崩。

---

## 步骤 2：标准编排循环（一次读、多轮产出、直接落盘）

核心套路三招，缺一个收益就打折：

**① 一次读 + session 复用**
第 1 轮只让 Kimi 读完全部输入、回一句"已读完"，**不产出**；后续每轮用**同一个 `--session-file`** 续会话直接产出。换会话 = 每轮重读，浪费 token 和时间。

```bash
WD="D:/proj/原始材料"
SF="$WD/_out/.kimi_session"   # 会话文件；要重新开局就先删掉它

# 轮1：吃进全部输入（新建会话，ID 自动写入 $SF）
"$PY" "$RUN" --session-file "$SF" -w "$WD" -p "你是资深分析员。依次读完当前目录所有 .md（共 N 个），\
完整理解后只回复'已读完 N 个文件，核心主题：XXX'，不要其他输出。"
```

**② 让 Kimi 直接写文件，不要把长文回灌给 Claude**
每轮 prompt 末尾明确"**写入文件 `_out/0X_xxx.md`**"。产物落盘后 Claude 再按需 Read，避免长文挤占 Claude 的 context。

```bash
# 轮2..N：同一个会话文件续会话，各产一份
"$PY" "$RUN" --session-file "$SF" -w "$WD" -p "基于已读内容，产出'成本结构'分析，6-10 个小节，\
200-600 行，写入文件 _out/01_成本结构.md。完成后只回复'已写入 01_成本结构.md'。"
```

**③ 后台跑 + 轮询**
Kimi 单轮重活常 60-180s。用 `run_in_background: true` 起 Bash 任务，完成时会自动通知你，多轮之间串行推进（后一轮依赖前一轮的会话状态，不要并行同一个会话）。实测 2.x 简单轮约 10-15s。

读产物时：若有多份且彼此独立，**派并行 Explore agent 各读一份**，别自己一份份 Read 占 context。

---

## 步骤 3：校验 Kimi 的产出（重要）

Kimi 在"长文去重/结构化"上很稳，但**具体事实会漂**——百分比、股票/产品编号、人名、代码行号都可能错。涉及这些时：
- 用脚本/工具对关键事实二次核验（如代码编号回查、数字交叉比对）；
- 在最终产物里标注数据来源与时点，提醒"这是 Kimi 提炼初稿"。

---

## 关键陷阱（每条都踩过）

- ❌ **不加 UTF-8**：直接 bash 调 kimi 传中文/`↔→≈` 会 GBK 崩 → 用 `kimi_run.py`（已内置）。
- ❌ **每轮换会话**：每轮重读输入，token 翻倍 → 全程一个 `--session-file` 续会话。
- ❌ **自己编会话 ID 传 `-S`**：2.x 只能续接已存在的 `session_xxx`，编的名字会失败 → 用 `--session-file` 让脚本抓 ID。
- ❌ **直接调 kimi 加 `-y`/`--auto`/`--quiet`/`-w`**：2.x 下要么不存在、要么不能和 `-p` 合用 → 走 `kimi_run.py`。
- ❌ **把长产物回灌 Claude**：让 Kimi 写文件，Claude 按需读。
- ❌ **并行复用同一个会话**：会话状态会打架 → 同一会话串行；要并行就用多个会话文件 + 多份输入。
- ❌ **prompt 太宽导致产物失控**：每轮限定范围（"6-10 小节 / 200-600 行"），宽了就拆轮。
- ❌ **盲信 Kimi 的数字/编号**：关键事实二次校验。
- ❌ **用户没点名时给小任务也外包**：输入小、用户没指定，就 Claude 直接做，别为调 Kimi 而调 Kimi。（用户点名了 Kimi 则照办，不受此限。）
- ⚠️ **在后台子 agent 里调 Kimi**：后台 subagent 默认 Bash 被禁，拉不起 Kimi.exe。Kimi 调用要在**主线程**跑；若必须在子 agent 里跑，先确认它有 Bash 权限。需要并行多份产物时，主线程开多个会话文件串/并行调，别指望后台子 agent 替你调 Kimi。

---

## 完整示例

把"多篇长研报 → 4 份结构化合成报告"的端到端实操（多轮 prompt 模板、后台轮询、并行读产物）写在 `references/multi-doc-synthesis.md`。需要做"多文档压缩成几份中间产物"类任务时读它当模板。

> 这套机制最初从投研看板 skill 抽象而来——那里用它把 13 篇研报压成 4 份合成报告再渲染 HTML。本 skill 是其通用化版本，任何"海量长文本→蒸馏"场景都可复用。
