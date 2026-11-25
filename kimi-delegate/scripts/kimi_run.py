#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kimi_run.py — 让 Claude Code 以 headless 方式驱动本机 Kimi Code CLI（2.x）的统一封装。

为什么要用这个脚本而不是直接 bash 拼 `kimi ...`：
  1) Windows 下直接用 bash 把中文 prompt 拼进 argv 容易 GBK 乱码/崩溃；
     这里用 python subprocess（走 Windows 宽字符 API）+ UTF-8 输出最稳。
  2) kimi 经常不在 PATH，脚本内置候选路径 + 探测兜底，换机器也能用。
  3) Kimi Code 2.x 不能自定义会话 ID：新会话的 ID 只出现在 stderr 末尾。
     脚本负责抓取它，并可存进 --session-file，下一轮自动续接。
  4) 清理输出：stdout 只留最终答案（去掉 "• " 前缀和续行缩进），
     思考过程（stderr）默认丢弃，--verbose 时原样转发。

Kimi Code 2.x 的 headless 调用就是 `kimi -p "<prompt>"`（工作目录 = 进程 cwd）。
注意 -p 不能与 -y/--yolo、--auto 合用；-p 模式下读写文件会自动执行。

典型用法（Claude Code 用 Bash 工具调用）：
  # 多轮推荐：用会话文件，首轮新建会话并记下 ID，后续轮自动续接
  python kimi_run.py --session-file "D:/proj/docs/_out/.kimi_session" -w "D:/proj/docs" -p "读完所有 .md，回复'已读完'"
  python kimi_run.py --session-file "D:/proj/docs/_out/.kimi_session" -w "D:/proj/docs" -f /tmp/prompt2.txt

  # 单轮：不传会话参数即新会话
  python kimi_run.py -w "D:/proj/docs" -p "总结 README.md"

  # 显式续接已知会话
  python kimi_run.py -S session_xxxxxxxx -w "D:/proj/docs" -p "继续"

stdout：Kimi 的最终回答。stderr 最后一行：`[kimi_run] session: <ID>`。
退出码：kimi 的退出码；找不到 kimi 为 127，超时为 124，抓不到会话 ID 为 3。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

# 本机硬编码优先，找不到再走 PATH 探测。换机器时改这里。
KIMI_CANDIDATES = [
    r"C:\Users\Administrator\.kimi-code\bin\kimi.exe",
    os.path.expanduser("~/.kimi-code/bin/kimi.exe"),
    os.path.expanduser("~/.kimi-code/bin/kimi"),
]
KIMI_PATH_NAMES = ["kimi"]

SESSION_RE = re.compile(r"(session_[0-9a-fA-F-]{8,})")
BULLET = "\u2022 "
CONT_INDENT = "  "
EXIT_NOT_FOUND = 127
EXIT_TIMEOUT = 124
EXIT_NO_SESSION = 3


def find_kimi():
    for c in KIMI_CANDIDATES:
        if os.path.isfile(c):
            return c
    for name in KIMI_PATH_NAMES:
        p = shutil.which(name)
        if p:
            return p
    sys.stderr.write(
        "[kimi_run] 找不到 kimi 可执行文件。请把真实路径加到本脚本 KIMI_CANDIDATES，"
        "或确认已安装 Kimi Code 并 `kimi login`。\n"
    )
    sys.exit(EXIT_NOT_FOUND)


def read_session_file(path):
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            sid = fh.read().strip()
        return sid or None
    return None


def write_session_file(path, sid):
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(sid + "\n")


def clean_answer(raw):
    """去掉 Kimi 输出的 '• ' 前缀和续行的两格缩进。"""
    lines = []
    for line in raw.splitlines():
        if line.startswith(BULLET):
            line = line[len(BULLET):]
        elif line.startswith(CONT_INDENT):
            line = line[len(CONT_INDENT):]
        lines.append(line)
    return "\n".join(lines).strip("\n")


def parse_args():
    ap = argparse.ArgumentParser(description="Headless Kimi Code CLI runner (UTF-8 safe).")
    sess = ap.add_mutually_exclusive_group()
    sess.add_argument("-S", "--session",
                      help="续接已有会话 ID（形如 session_xxx）。不传则新建会话。")
    sess.add_argument("--session-file",
                      help="会话 ID 存放文件：存在则续接其中的会话，运行后写入本轮会话 ID。多轮推荐。")
    ap.add_argument("-w", "--work-dir", required=True,
                    help="Kimi 的工作目录（作为进程 cwd；它在这里读输入、写输出文件）。")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("-p", "--prompt", help="直接传入的 prompt 文本。")
    g.add_argument("-f", "--prompt-file", help="从 UTF-8 文件读 prompt（长/中文 prompt 推荐）。")
    ap.add_argument("-m", "--model", default=None, help="可选：指定 Kimi 模型别名。")
    ap.add_argument("--timeout", type=int, default=None,
                    help="可选：超时秒数（默认无）。Kimi 单轮重活常 60-180s。")
    ap.add_argument("--verbose", action="store_true",
                    help="把 Kimi 的 stderr（思考过程）原样转发，调试用。")
    return ap.parse_args()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()

    if not os.path.isdir(args.work_dir):
        sys.stderr.write(f"[kimi_run] 工作目录不存在：{args.work_dir}\n")
        sys.exit(2)

    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as fh:
            prompt = fh.read()
    else:
        prompt = args.prompt

    resume_id = args.session or read_session_file(args.session_file)

    cmd = [find_kimi()]
    if resume_id:
        cmd += ["-S", resume_id]
    if args.model:
        cmd += ["-m", args.model]
    cmd += ["-p", prompt]

    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(cmd, cwd=args.work_dir, env=env,
                              capture_output=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"[kimi_run] 超时 {args.timeout}s，已放弃。可调大 --timeout 或拆分 prompt。\n")
        sys.exit(EXIT_TIMEOUT)

    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")

    if args.verbose or proc.returncode != 0:
        sys.stderr.write(err if err.endswith("\n") else err + "\n")

    answer = clean_answer(out)
    if answer:
        sys.stdout.write(answer + "\n")

    found = SESSION_RE.findall(err)
    sid = found[-1] if found else resume_id
    if sid:
        sys.stderr.write(f"[kimi_run] session: {sid}\n")
        if args.session_file and proc.returncode == 0:
            write_session_file(args.session_file, sid)
    elif proc.returncode == 0 and args.session_file:
        sys.stderr.write("[kimi_run] 未能从 Kimi 输出中抓到会话 ID，下一轮无法续接。\n")
        sys.exit(EXIT_NO_SESSION)

    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
