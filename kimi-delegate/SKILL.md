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

- Kimi CLI v1.44+：`C:\Users\Administrator\.local\bin\kimi.exe`
- Python 3.12：`C:\Users\Administrator\scoop\shims\python.exe`
- 本 skill 脚本：`C:\Users\Administrator\.claude\skills\kimi-delegate\scripts\kimi_run.py`

`kimi_run.py` 内部已带路径探测兜底，换机器时改它顶部的 `KIMI_CANDIDATES` 即可。
文件系统操作用 Glob/Read 工具或 `python -c`，**别用 ls/cat/find**（本机 bash 无 coreutils）。

---

## 步骤 1：用封装脚本调 Kimi（不要直接 bash 拼参数）

**统一入口是 `scripts/kimi_run.py`**，它封好了 headless 参数 + UTF-8 安全 + 路径探测：

```bash
PY="C:/Users/Administrator/scoop/shims/python.exe"
RUN="C:/Users/Administrator/.claude/skills/kimi-delegate/scripts/kimi_run.py"

# 直接传 prompt
"$PY" "$RUN" -S "<会话ID>" -w "<Kimi工作目录>" -p "<指令>"

# 长/复杂/含特殊字符的 prompt：写 UTF-8 文件再传（最稳）
"$PY" "$RUN" -S "<会话ID>" -w "<Kimi工作目录>" -f "/tmp/kimi_prompt.txt"
```

脚本等价于跑：`kimi --quiet --afk -y -S <ID> -w <dir> -p <prompt>`，含义：
| 参数 | 作用 |
|---|---|
| `--quiet` | headless 干净输出（只回最终答案，无事件脚手架） |
| `--afk` | 无人值守模式，不等交互 |
| `-y` | 自动批准所有动作（读写文件等） |
| `-S <ID>` | 复用/续接会话；**同一 ID 跨轮 = 只读一次输入** |
| `-w <dir>` | Kimi 的工作目录，它在这里读输入、写产物 |
| `-p` / `-f` | prompt 文本 / prompt 文件 |

> 为什么不直接 bash `kimi -p "中文..."`：Windows 下中文/特殊字符进 argv 容易 GBK 崩。
> 脚本走 python subprocess（宽字符 API）+ `PYTHONUTF8=1`，已实测 `↔ → ≈` 不崩。

---

## 步骤 2：标准编排循环（一次读、多轮产出、直接落盘）

核心套路三招，缺一个收益就打折：

**① 一次读 + session 复用**
第 1 轮只让 Kimi 读完全部输入、回一句"已读完"，**不产出**；后续每轮用**同一个 `-S` ID** 续会话直接产出。换 ID = 每轮重读，浪费 token 和时间。

```bash
SID="proj-$(python -c 'import time;print(int(time.time()))')"
WD="D:/proj/原始材料"

# 轮1：吃进全部输入
"$PY" "$RUN" -S "$SID" -w "$WD" -p "你是资深分析员。依次读完当前目录所有 .md（共 N 个），\
完整理解后只回复'已读完 N 个文件，核心主题：XXX'，不要其他输出。"
```

**② 让 Kimi 直接写文件，不要把长文回灌给 Claude**
每轮 prompt 末尾明确"**写入文件 `_out/0X_xxx.md`**"。产物落盘后 Claude 再按需 Read，避免长文挤占 Claude 的 context。

```bash
# 轮2..N：同 SID 续会话，各产一份
"$PY" "$RUN" -S "$SID" -w "$WD" -p "基于已读内容，产出'成本结构'分析，6-10 个小节，\
200-600 行，写入文件 _out/01_成本结构.md。完成后只回复'已写入 01_成本结构.md'。"
```

**③ 后台跑 + 轮询**
Kimi 单轮重活常 60-180s。用 `run_in_background: true` 起 Bash 任务，再用 `TaskOutput` block 等结果，多轮之间串行推进（后一轮依赖前一轮的会话状态，不要并行同一个 SID）。

读产物时：若有多份且彼此独立，**派并行 Explore agent 各读一份**，别自己一份份 Read 占 context。

---

## 步骤 3：校验 Kimi 的产出（重要）

Kimi 在"长文去重/结构化"上很稳，但**具体事实会漂**——百分比、股票/产品编号、人名、代码行号都可能错。涉及这些时：
- 用脚本/工具对关键事实二次核验（如代码编号回查、数字交叉比对）；
- 在最终产物里标注数据来源与时点，提醒"这是 Kimi 提炼初稿"。

---

## 关键陷阱（每条都踩过）

- ❌ **不加 UTF-8**：直接 bash 调 kimi 传中文/`↔→≈` 会 GBK 崩 → 用 `kimi_run.py`（已内置）。
- ❌ **每轮换 SID**：每轮重读输入，token 翻倍 → 全程一个 SID 续会话。
- ❌ **把长产物回灌 Claude**：让 Kimi 写文件，Claude 按需读。
- ❌ **并行复用同一个 SID**：会话状态会打架 → 同一 SID 串行；要并行就开多个 SID + 多份输入。
- ❌ **prompt 太宽导致产物失控**：每轮限定范围（"6-10 小节 / 200-600 行"），宽了就拆轮。
- ❌ **盲信 Kimi 的数字/编号**：关键事实二次校验。
- ❌ **用户没点名时给小任务也外包**：输入小、用户没指定，就 Claude 直接做，别为调 Kimi 而调 Kimi。（用户点名了 Kimi 则照办，不受此限。）
- ⚠️ **在后台子 agent 里调 Kimi**：后台 subagent 默认 Bash 被禁，拉不起 Kimi.exe。Kimi 调用要在**主线程**跑；若必须在子 agent 里跑，先确认它有 Bash 权限。需要并行多份产物时，主线程开多个 SID 串/并行调，别指望后台子 agent 替你调 Kimi。

---

## 完整示例

把"多篇长研报 → 4 份结构化合成报告"的端到端实操（多轮 prompt 模板、后台轮询、并行读产物）写在 `references/multi-doc-synthesis.md`。需要做"多文档压缩成几份中间产物"类任务时读它当模板。

> 这套机制最初从投研看板 skill 抽象而来——那里用它把 13 篇研报压成 4 份合成报告再渲染 HTML。本 skill 是其通用化版本，任何"海量长文本→蒸馏"场景都可复用。
