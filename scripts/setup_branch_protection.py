#!/usr/bin/env python3
"""
设置 GitHub 分支保护规则

禁止直接 push 到 main，强制所有变更走 PR。
PR 必须通过 README 同步检查才能合并。

使用方法：
  1. 创建 GitHub Personal Access Token（需 repo_admin 权限）
  2. 运行：python scripts/setup_branch_protection.py

  或者直接在 GitHub 网页上手动设置（见下方说明）。
"""

import os
import json
import httpx

# ============================
# 配置
# ============================
REPO_OWNER = "LBP97541135"
REPO_NAME = "evo-murder-game"
BRANCH = "main"

# 从环境变量读取 Token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

if not GITHUB_TOKEN:
    print("=" * 60)
    print("⚠️  需要 GitHub Personal Access Token")
    print("=" * 60)
    print()
    print("请按以下步骤操作：")
    print()
    print("方法一：手动设置（推荐，更简单）")
    print("  1. 打开 https://github.com/LBP97541135/evo-murder-game/settings/branches")
    print("  2. 在 'Branch protection rules' 下点击 'Add rule'")
    print("  3. Branch name pattern: main")
    print("  4. 勾选以下选项：")
    print("     ☑ Require a pull request before merging")
    print("       ☑ Require approvals (1)")
    print("     ☑ Require status checks to pass before merging")
    print("       ☑ 搜索并选择 'check-readme-sync' 检查")
    print("     ☑ Do not allow bypassing the above settings")
    print("  5. 点击 'Create'")
    print()
    print("方法二：通过此脚本自动设置")
    print("  1. 创建 Token: https://github.com/settings/tokens")
    print("     → Generate new token (classic)")
    print("     → 勾选 repo (Full control of private repositories)")
    print("  2. 运行：")
    print("     export GITHUB_TOKEN=ghp_你的token")
    print("     python scripts/setup_branch_protection.py")
    print()
    import sys
    sys.exit(0)


def setup_protection():
    """通过 GitHub API 设置 main 分支保护规则。"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/branches/{BRANCH}/protection"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "required_status_checks": {
            "strict": True,
            "contexts": ["check-readme-sync"],
        },
        "enforce_admins": True,  # 管理员也不能绕过
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1,
        },
        "restrictions": None,  # 不限制谁能 push（所有人走 PR 即可）
        "block_force_pushes": True,  # 禁止 force push
    }

    r = httpx.put(url, headers=headers, json=payload)

    if r.status_code == 200:
        print("✅ main 分支保护规则设置成功！")
        print()
        print("规则：")
        print("  - 禁止直接 push 到 main")
        print("  - 必须走 PR，且需要 1 人 approval")
        print("  - PR 必须通过 'check-readme-sync' 检查才能合并")
        print("  - 管理员也不能绕过")
        print("  - 禁止 force push")
    elif r.status_code == 403:
        print("❌ 权限不足——Token 需要 repo_admin 权限")
        print(f"   详情: {r.text}")
    elif r.status_code == 404:
        print("❌ 仓库不存在或 Token 无权限访问此仓库")
        print(f"   详情: {r.text}")
    else:
        print(f"❌ 设置失败 (HTTP {r.status_code})")
        print(f"   详情: {r.text}")


if __name__ == "__main__":
    setup_protection()
