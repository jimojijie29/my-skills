"""莫大讲义图片嵌入脚本模板（WebP 压缩版）

用法：复制到项目根目录，改名为 convert_images_YYYY_MM_DD.py，只填写「配置区」后运行：
    python convert_images_YYYY_MM_DD.py

行为：
- 把 HTML 中 <img src="Picture/..."> 替换为 Base64 内联，输出独立的 *_presentation_embedded.html
- 有 Pillow 时：宽度 > MAX_WIDTH 等比缩放，并转 WebP（quality=WEBP_QUALITY）；Picture/ 原图不改动
- 无 Pillow 时：退回原样嵌入（体积会大很多，建议 pip install pillow）
- 扩展名大小写不敏感（.PNG / .png 均可）
- 退出码：0 = 全部嵌入；1 = 找不到 HTML；2 = 有缺图或残留未嵌入引用
范本：2026.11.24 私域直播，23 张图，原图 17MB → embedded 3.02MB
"""
import base64
import os
import re
import shutil
import sys

# ── 配置区（只改这里）──────────────────────────────────
HTML_FILE = "YYYY.MM.DD_类型_主题_presentation.html"
OUTPUT_FILE = "YYYY.MM.DD_类型_主题_presentation_embedded.html"
PICTURE_DIR = "Picture"
REQUIRED_IMAGES: list[str] = [
    # 直接粘贴第0步扫描得到的真实文件名（保留原始大小写），例如：
    # "两市融资金额数据汇总-11.24.PNG",
]
# ────────────────────────────────────────────────────────

MAX_WIDTH = 1600        # 嵌入前缩放上限；图内文字很小时可调到 1800
WEBP_QUALITY = 85       # 文字发糊时可调到 90
TARGET_MB = 5           # 超过则提示；项目硬上限 10MB
MIME = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}


def encode(full_path: str) -> tuple[str, bytes]:
    """返回 (mime, bytes)。有 Pillow 时缩放并转 WebP，否则原样读取。"""
    try:
        from io import BytesIO

        from PIL import Image
    except ImportError:
        ext = os.path.splitext(full_path)[1].lower().lstrip(".")
        with open(full_path, "rb") as f:
            return MIME.get(ext, "png"), f.read()
    with Image.open(full_path) as im:
        im = im.convert("RGB")
        if im.width > MAX_WIDTH:
            im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
        buf = BytesIO()
        im.save(buf, "WEBP", quality=WEBP_QUALITY, method=6)
    return "webp", buf.getvalue()


def resolve(base_dir: str, img_path: str) -> str | None:
    """返回图片真实路径；精确路径不存在时做大小写不敏感匹配。"""
    full_path = os.path.join(base_dir, img_path)
    if os.path.exists(full_path):
        return full_path
    filename = os.path.basename(img_path).lower()
    pic_abs = os.path.join(base_dir, PICTURE_DIR)
    for fn in os.listdir(pic_abs):
        if fn.lower() == filename:
            return os.path.join(pic_abs, fn)
    return None


def embed_images(html_content: str, base_dir: str) -> str:
    def replace_src(match: re.Match) -> str:
        img_path = match.group(1)
        full_path = resolve(base_dir, img_path)
        if not full_path:
            print(f"  WARNING missing: {img_path}")
            return match.group(0)
        mime, data = encode(full_path)
        b64 = base64.b64encode(data).decode()
        print(f"  OK: {os.path.basename(full_path)}（{len(data) // 1024} KB）")
        return f'src="data:image/{mime};base64,{b64}"'

    return re.sub(r'src="(Picture/[^"]+)"', replace_src, html_content)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, HTML_FILE)
    out_path = os.path.join(base_dir, OUTPUT_FILE)

    if not os.path.exists(html_path):
        print(f"错误：找不到 {HTML_FILE}")
        return 1

    missing = [n for n in REQUIRED_IMAGES if not resolve(base_dir, f"{PICTURE_DIR}/{n}")]
    if missing:
        print("缺少图片：", *missing, sep="\n  ")

    backup = html_path.replace(".html", "_backup.html")
    shutil.copy2(html_path, backup)
    print(f"备份已创建: {os.path.basename(backup)}")

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("开始嵌入图片...")
    embedded = embed_images(content, base_dir)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(embedded)

    remaining = len(re.findall(r'src="Picture/', embedded))
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\n完成！输出文件: {OUTPUT_FILE}（{size_mb:.2f} MB，未嵌入引用 {remaining} 处）")
    if size_mb > TARGET_MB:
        print(f"提示：超过 {TARGET_MB}MB 目标，可下调 MAX_WIDTH 或 WEBP_QUALITY")
    return 0 if remaining == 0 and not missing else 2


if __name__ == "__main__":
    sys.exit(main())
