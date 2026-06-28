#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kimi_run.py — 让 Claude Code 以 headless 方式驱动本机 Kimi CLI 的统一封装。

为什么要用这个脚本而不是直接 bash 拼 `kimi ...`：
  1) Windows 下直接用 bash 把中文 prompt 拼进 argv 容易 GBK 乱码/崩溃；
     这里用 python subprocess（走 Windows 宽字符 API）+ PYTHONUTF8=1 最稳。
  2) kimi/python 经常不在 PATH，脚本内置候选路径 + 探测兜底，换机器也能用。
  3) 统一 headless 参数（--quiet 干净输出 / --afk 无人值守 / -y 自动批准 /
     -S 复用 session），避免每个项目重抄一遍、抄错。

典型用法（Claude Code 用 Bash 工具调用）：
  # 单轮：prompt 直接传
  python kimi_run.py -S mysid -w "D:/proj/docs" -p "读完当前目录所有 .md，回复'已读完'"

  # 复杂/超长/中文 prompt：写到 UTF-8 文件再传，最稳
  python kimi_run.py -S mysid -w "D:/proj/docs" -f /tmp/prompt2.txt

  # 同一个 -S 跨多轮续会话：Kimi 只读一次输入，后面每轮直接产出
  python kimi_run.py -S mysid -w "D:/proj/docs" -p "把要点写入 _out/summary.md"

退出码即 kimi 的退出码；stdout 是 Kimi 的最终回答（--quiet 模式）。
"""
import argparse
import os
import shutil
import subprocess
import sys

# 本机硬编码优先（kimi/python 不在 PATH），找不到再探测兜底。
# 换机器时改这里，或让探测逻辑命中。
KIMI_CANDIDATES = [
    r"C:\Users\Administrator\.local\bin\kimi.exe",
    os.path.expanduser("~/.local/bin/kimi.exe"),
    os.path.expanduser("~/.local/bin/kimi"),
    "kimi.exe",
    "kimi",
]


def find_kimi():
    for c in KIMI_CANDIDATES:
        # 带路径分隔符或 .exe 的当成具体文件，存在即用
        if (os.sep in c) or c.lower().endswith(".exe"):
            if os.path.exists(c):
                return c
        else:
            p = shutil.which(c)
            if p:
                return p
    sys.stderr.write(
        "[kimi_run] 找不到 kimi 可执行文件。请把真实路径加到本脚本 KIMI_CANDIDATES，"
        "或确认已 `kimi login`。\n"
    )
    sys.exit(127)


def main():
    ap = argparse.ArgumentParser(description="Headless Kimi CLI runner (UTF-8 safe).")
    ap.add_argument("-S", "--session", required=True,
                    help="会话 ID。跨多轮复用同一个 ID 让 Kimi 只读一次输入。")
    ap.add_argument("-w", "--work-dir", required=True,
                    help="Kimi 的工作目录（它在这里读输入、写输出文件）。")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("-p", "--prompt", help="直接传入的 prompt 文本。")
    g.add_argument("-f", "--prompt-file", help="从 UTF-8 文件读 prompt（长/中文 prompt 推荐）。")
    ap.add_argument("-m", "--model", default=None, help="可选：指定 Kimi 模型。")
    ap.add_argument("--timeout", type=int, default=None,
                    help="可选：超时秒数（默认无）。Kimi 单轮重活常 60-180s。")
    ap.add_argument("--verbose", action="store_true",
                    help="用 --print（含事件脚手架）替代 --quiet，调试用。")
    args = ap.parse_args()

    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as fh:
            prompt = fh.read()
    else:
        prompt = args.prompt

    kimi = find_kimi()
    cmd = [kimi]
    cmd += ["--print"] if args.verbose else ["--quiet"]
    cmd += ["--afk", "-y", "-S", args.session, "-w", args.work_dir]
    if args.model:
        cmd += ["-m", args.model]
    cmd += ["-p", prompt]

    # 关键：强制 UTF-8，否则 Windows 下 ↔ → ≈ 等字符会按 GBK 崩。
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        proc = subprocess.run(cmd, env=env, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"[kimi_run] 超时 {args.timeout}s，已放弃。可调大 --timeout 或拆分 prompt。\n")
        sys.exit(124)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
