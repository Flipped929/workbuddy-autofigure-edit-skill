#!/usr/bin/env python3
"""
AutoFigure-Edit 更新检查工具
检查 GitHub 上 ResearAI/AutoFigure-Edit 的最新版本，与本地代码进行对比，输出更新摘要。

用法:
    python check_update.py [--local-dir PATH]
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

GITHUB_REPO = "ResearAI/AutoFigure-Edit"
GITHUB_API_COMMITS = f"https://api.github.com/repos/{GITHUB_REPO}/commits?per_page=10"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_COMPARE_URL = f"https://github.com/{GITHUB_REPO}/compare"
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO}"


def fetch_json(url: str, timeout: int = 15) -> dict | list | None:
    """发送 GET 请求并解析 JSON 响应"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "autofigure-edit-skill/1.0", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[错误] 请求失败: {e}")
        return None


def get_local_commit(local_dir: str) -> str | None:
    """获取本地仓库的最新 commit hash"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=local_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_local_version_from_file(local_dir: str) -> str | None:
    """从本地文件读取版本信息（如果有 VERSION 文件）"""
    version_files = ["VERSION", "version.txt", "version"]
    for f in version_files:
        path = Path(local_dir) / f
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    return None


def format_commit_date(date_str: str) -> str:
    """格式化 GitHub commit 日期"""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return date_str


def main():
    parser = argparse.ArgumentParser(description="检查 AutoFigure-Edit 的 GitHub 更新")
    parser.add_argument(
        "--local-dir",
        default=None,
        help="本地 AutoFigure-Edit 源码路径（用于对比版本）",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  AutoFigure-Edit 更新检查器")
    print(f"  仓库: https://github.com/{GITHUB_REPO}")
    print("=" * 60)

    # 1. 获取本地信息
    local_commit = None
    if args.local_dir:
        local_dir = os.path.expanduser(args.local_dir)
        if not os.path.isdir(local_dir):
            print(f"[警告] 本地目录不存在: {local_dir}")
        else:
            local_commit = get_local_commit(local_dir)
            local_version = get_local_version_from_file(local_dir)
            print(f"\n📁 本地路径: {local_dir}")
            if local_commit:
                print(f"   本地 Commit: {local_commit[:12]}...")
            if local_version:
                print(f"   本地版本号: {local_version}")
            if not local_commit and not local_version:
                print("   (无法读取本地版本信息，请确认是 git 仓库或有 VERSION 文件)")

    # 2. 获取远端最新 commits
    print("\n🔍 正在从 GitHub 获取最新信息...")
    commits_data = fetch_json(GITHUB_API_COMMITS)

    if not commits_data:
        print("[错误] 无法连接 GitHub API，请检查网络或稍后重试。")
        print(f"       也可直接访问: {GITHUB_REPO_URL}")
        sys.exit(1)

    latest_commit = commits_data[0]
    latest_sha = latest_commit["sha"]
    latest_msg = latest_commit["commit"]["message"].split("\n")[0]
    latest_date = format_commit_date(latest_commit["commit"]["author"]["date"])
    latest_author = latest_commit["commit"]["author"]["name"]

    print(f"\n✅ 远端最新 Commit:")
    print(f"   SHA    : {latest_sha[:12]}...")
    print(f"   时间   : {latest_date}")
    print(f"   作者   : {latest_author}")
    print(f"   描述   : {latest_msg}")

    # 3. 最近 10 条 commit 摘要
    print(f"\n📋 最近 {len(commits_data)} 条更新记录:")
    print("-" * 55)
    for i, c in enumerate(commits_data):
        sha = c["sha"][:8]
        msg = c["commit"]["message"].split("\n")[0][:55]
        date = format_commit_date(c["commit"]["author"]["date"])[:10]
        marker = "▶ " if i == 0 else "  "
        print(f"{marker}[{sha}] {date}  {msg}")

    # 4. 版本对比
    print()
    if local_commit:
        if local_commit.startswith(latest_sha[:12]) or latest_sha.startswith(local_commit[:12]):
            print("🎉 本地已是最新版本！")
        else:
            # 检查本地 commit 是否在远端列表中
            remote_shas = [c["sha"] for c in commits_data]
            if any(local_commit.startswith(sha[:12]) for sha in remote_shas):
                idx = next(
                    i for i, sha in enumerate(remote_shas)
                    if local_commit.startswith(sha[:12])
                )
                print(f"⬆️  本地版本落后 {idx} 个 commit，建议更新！")
            else:
                print("⚠️  本地版本与远端不在同一历史线（可能是 fork 或本地修改）")
            print(f"\n   更新方式：")
            print(f"   cd <本地目录> && git pull origin main")
            print(f"   或访问: {GITHUB_COMPARE_URL}/{local_commit[:12]}...{latest_sha[:12]}")
    else:
        print(f"📥 如需下载最新版本:")
        print(f"   git clone https://github.com/{GITHUB_REPO}.git")
        print(f"   或下载 ZIP: https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip")

    # 5. 尝试获取 Release 信息
    release_data = fetch_json(GITHUB_API_RELEASES)
    if release_data and "tag_name" in release_data:
        tag = release_data["tag_name"]
        rel_name = release_data.get("name", tag)
        rel_date = format_commit_date(release_data.get("published_at", ""))
        rel_body = release_data.get("body", "")[:300]
        print(f"\n🏷️  最新 Release: {rel_name} ({tag})")
        print(f"   发布时间: {rel_date}")
        if rel_body:
            print(f"   更新说明:\n")
            for line in rel_body.strip().split("\n")[:8]:
                print(f"   {line}")
    else:
        print("\n   (该项目暂无 Release，以最新 commit 为准)")

    print("\n" + "=" * 60)
    print(f"  完整仓库: {GITHUB_REPO_URL}")
    print(f"  论文主页: https://arxiv.org/abs/2603.06674")
    print("=" * 60)


if __name__ == "__main__":
    main()
