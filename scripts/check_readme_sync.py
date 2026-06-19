#!/usr/bin/env python3
"""
README 同步检查脚本

规则：如果某个子目录内有代码文件被修改，但该目录的 README.md 未被修改，则报错。

适用范围：
  - api/ 下所有子目录（config/ evomap/ agents/ llm/ schemas/ db/ routes/）
  - api/ 本身
  - web/ 下所有子目录（api/ types/ providers/ pages/ components/ constants/ utils/）
  - web/public/
  - docs/
  - scripts/

忽略：
  - 只有 README.md 变化的目录（纯文档更新不算违规）
  - 只有 __init__.py 变化的目录（纯导出更新不算违规）
  - 只有 .env.example / requirements.txt 等配置文件的目录
"""

import os
import subprocess
import sys
from pathlib import Path

# 需要检查 README 同步的目录列表
CHECKED_DIRS = [
    "api",
    "api/config",
    "api/evomap",
    "api/agents",
    "api/llm",
    "api/schemas",
    "api/db",
    "api/routes",
    "web",
    "web/src/api",
    "web/src/types",
    "web/src/providers",
    "web/src/pages",
    "web/src/components",
    "web/src/constants",
    "web/src/utils",
    "web/public",
    "docs",
    "scripts",
]

# 这些文件的变更不算"代码变更"，不触发 README 检查
SKIP_FILES = {
    "README.md",
    "__init__.py",
    ".env.example",
    ".gitignore",
    "requirements.txt",
    "package.json",
    "tsconfig.json",
}

# 代码文件扩展名（变更这些文件需要同步 README）
CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".json", ".html", ".css",
    ".sh", ".yaml", ".yml", ".toml",
}


def get_changed_files(base_ref: str) -> list[str]:
    """获取相对于 base_ref 的所有变更文件列表。"""
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        # 可能 base_ref 不存在（首次 PR），用 HEAD 作对比
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True,
        )
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def classify_changes(changed_files: list[str]) -> dict[str, dict]:
    """将变更文件按目录分类，返回每个目录的 {code_files, readme_changed}。"""
    dir_changes: dict[str, dict] = {}

    for dir_path in CHECKED_DIRS:
        dir_changes[dir_path] = {
            "code_files": [],
            "readme_changed": False,
        }

    for file_path in changed_files:
        # 检查是否是该目录下的文件
        for dir_path in CHECKED_DIRS:
            # file_path 以 dir_path/ 开头，或 file_path 就是 dir_path 内的直接文件
            prefix = dir_path + "/"
            if file_path.startswith(prefix) or (dir_path == "api" and file_path.startswith("api/") and "/" not in file_path[4:]):
                file_name = Path(file_path).name

                if file_name == "README.md":
                    dir_changes[dir_path]["readme_changed"] = True
                elif file_name in SKIP_FILES:
                    continue  # 配置文件变更不算代码变更
                elif Path(file_path).suffix in CODE_EXTENSIONS:
                    # 但 __init__.py 特殊处理——只有导出变更不算
                    if file_name == "__init__.py":
                        continue
                    dir_changes[dir_path]["code_files"].append(file_path)
                else:
                    # 其他文件（如图片等）不算代码变更
                    pass

            # 更精确的匹配：api/ 的直接子文件
            if dir_path == "api" and file_path.startswith("api/") and "/" not in file_path[len("api/"):]:
                file_name = Path(file_path).name
                if file_name == "README.md":
                    dir_changes[dir_path]["readme_changed"] = True
                elif file_name not in SKIP_FILES and Path(file_path).suffix in CODE_EXTENSIONS:
                    dir_changes[dir_path]["code_files"].append(file_path)

    return dir_changes


def check_readme_sync(dir_changes: dict[str, dict]) -> list[str]:
    """检查每个有代码变更的目录是否同步了 README。返回违规列表。"""
    violations = []

    for dir_path, changes in dir_changes.items():
        code_files = changes["code_files"]
        readme_changed = changes["readme_changed"]

        if code_files and not readme_changed:
            violations.append(
                f"❌ {dir_path}/ — 代码变更了 {len(code_files)} 个文件，"
                f"但 README.md 未更新：{', '.join(code_files)}"
            )

    return violations


def main():
    # PR 的 base 分支（目标分支）
    base_ref = os.environ.get("GITHUB_BASE_REF", "main")

    # 获取变更文件
    changed_files = get_changed_files(base_ref)
    if not changed_files:
        print("✅ 没有文件变更，跳过检查")
        sys.exit(0)

    print(f"📋 检查相对于 {base_ref} 的 {len(changed_files)} 个变更文件")
    print(f"📋 变更文件: {changed_files}")
    print()

    # 分类变更
    dir_changes = classify_changes(changed_files)

    # 检查 README 同步
    violations = check_readme_sync(dir_changes)

    if violations:
        print("🚫 README 同步检查失败！")
        print()
        for v in violations:
            print(v)
        print()
        print("💡 修复方法：请在对应的目录中更新 README.md，记录：")
        print("   - 需求变更")
        print("   - 进度更新")
        print("   - 新增疑问")
        print()
        print("   每个目录的 README 格式：职责 / 当前需求 / 进度 / 疑问")
        sys.exit(1)
    else:
        print("✅ README 同步检查通过！所有代码变更都同步了 README")
        sys.exit(0)


if __name__ == "__main__":
    main()
