import os
from urllib.parse import quote

README_PATH = "README.md"
BASE_URL = "https://github.com/heeom/TIL/blob/base"

def generate_readme():
    lines = [
        "# 📚 Today I Learned",
        "",
        "하루 동안 학습한 내용을 정리한 저장소입니다.",
        "",
    ]

    for root, dirs, files in sorted(os.walk(".")):
        if root.startswith("./.") or "node_modules" in root:
            continue
        md_files = [f for f in files if f.endswith(".md") and f != "README.md"]
        relative_path = os.path.relpath(root, ".")
        depth = relative_path.count(os.sep)
        indent = "  " * depth
        folder_name = os.path.basename(root)

        if depth == 0:
            lines.append(f"## 🗂️ {folder_name}")
        else:
            lines.append(f"{indent}- ### 📝 {folder_name}")

        for file in sorted(md_files):
            file_path = os.path.join(root, file).replace("./", "")
            file_url = f"{BASE_URL}/{quote(file_path)}"
            filename_without_ext = os.path.splitext(file)[0]
            lines.append(f"{indent}  - [{filename_without_ext}]({file_url})")

        if md_files or depth == 0:
            lines.append("")

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    generate_readme()
