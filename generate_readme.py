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
        if md_files:
            depth = root.count(os.sep) - 1
            folder_name = os.path.basename(root)
            header = f"## {'📝 ' if depth == 0 else ''}{folder_name}"
            lines.append(header)
            for file in sorted(md_files):
                file_path = os.path.join(root, file).replace("./", "")
                file_url = f"{BASE_URL}/{quote(file_path)}"
                lines.append(f"- [{file}]({file_url})")
            lines.append("")  # 공백 라인

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    generate_readme()