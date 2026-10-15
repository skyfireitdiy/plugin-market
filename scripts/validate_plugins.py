#!/usr/bin/env python3
"""校验 plugin-market 仓库 plugins/ 目录下所有插件清单。

检查项：
1. 每个 plugins/*.yaml 都能被 YAML 解析，且是 mapping。
2. 必填字段（id/name/description/repo/author/license）存在且为非空字符串。
3. 可选字段类型正确（branch/logo 为字符串，categories 为字符串列表）。
4. id 在全部清单中唯一（不重复）。
5. 文件名（不含 .yaml 后缀）等于 id（README 约定：文件名 = 插件 id）。
6. repo 为合法 git 地址（https:// 或 git@ 形式），且通过 git ls-remote
   验证仓库可达、声明的分支（默认 main）存在。

退出码：全部通过返回 0，任一失败返回 1（供 GitHub Action 判定）。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

# 模板/示例文件不参与校验
SKIP_FILES = {"_example.yaml"}

PLUGINS_DIR = Path(__file__).resolve().parent.parent / "plugins"

# 必填字段：必须存在且为非空字符串
REQUIRED_FIELDS = ("id", "name", "description", "repo", "author", "license")
# 可选字符串字段
OPTIONAL_STR_FIELDS = ("branch", "logo")

# 合法 repo 地址：https://host/owner/repo(.git)
# 仅接受 https:// 形式：市场与插件仓库均为公开仓库，https 匿名 clone 不依赖
# 凭据，CI runner（无 SSH key）与客户端均可访问；git@ 形式在 CI 会认证失败误报。
_REPO_RE = re.compile(
    r"^https?://[^\s/]+/[^\s/]+/[^\s/]+(?:\.git)?$"
)

LS_REMOTE_TIMEOUT = 30  # 秒


def _check_required_fields(data: dict, filename: str, errors: list[str]) -> None:
    """校验必填字段非空字符串、可选字段类型。"""
    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if not value or not isinstance(value, str) or not value.strip():
            errors.append(
                f"{filename}: 必填字段 '{field}' 缺失或不是非空字符串"
            )

    for field in OPTIONAL_STR_FIELDS:
        value = data.get(field)
        if value is not None and not isinstance(value, str):
            errors.append(f"{filename}: 可选字段 '{field}' 应为字符串")

    categories = data.get("categories")
    if categories is not None:
        if not isinstance(categories, list) or not all(
            isinstance(c, str) for c in categories
        ):
            errors.append(f"{filename}: 'categories' 应为字符串列表")


def _check_repo_url(data: dict, filename: str, errors: list[str]) -> None:
    """校验 repo 地址格式与可达性（含分支存在性）。"""
    repo = (data.get("repo") or "").strip()
    if not repo:
        return  # 必填字段检查已覆盖缺失场景
    if not _REPO_RE.match(repo):
        errors.append(
            f"{filename}: repo '{repo}' 不是合法 https git 地址"
            "（应为 https://host/owner/repo 或 https://host/owner/repo.git；"
            "公开仓库请用 https 形式，git@ 形式在 CI 无法匿名校验）"
        )
        return

    branch = (data.get("branch") or "main").strip()
    try:
        proc = subprocess.run(
            ["git", "ls-remote", "--heads", repo, branch],
            capture_output=True,
            text=True,
            timeout=LS_REMOTE_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        errors.append(f"{filename}: 校验 repo '{repo}' 超时（{LS_REMOTE_TIMEOUT}s）")
        return
    except Exception as e:  # noqa: BLE001 - git 命令异常统一收集
        errors.append(f"{filename}: 校验 repo '{repo}' 执行失败: {e}")
        return

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        err_msg = detail[-1] if detail else "git ls-remote 失败"
        errors.append(f"{filename}: repo '{repo}' 不可达: {err_msg}")
        return

    if not proc.stdout.strip():
        errors.append(
            f"{filename}: repo '{repo}' 不存在分支 '{branch}'"
        )


def main() -> int:
    if not PLUGINS_DIR.is_dir():
        print(f"❌ plugins/ 目录不存在: {PLUGINS_DIR}")
        return 1

    files = sorted(
        p for p in PLUGINS_DIR.glob("*.yaml") if p.name not in SKIP_FILES
    )
    if not files:
        print("⚠️  plugins/ 下没有任何 .yaml 清单文件（模板除外）")
        return 0

    errors: list[str] = []
    seen: dict[str, Path] = {}  # id -> 首次出现的文件

    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001 - 解析错误统一收集
            errors.append(f"{path.name}: YAML 解析失败: {e}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.name}: 顶层不是 mapping（应为键值对结构）")
            continue

        plugin_id = data.get("id")
        if not plugin_id or not isinstance(plugin_id, str):
            errors.append(f"{path.name}: 缺少字符串类型 id 字段")
        else:
            # 文件名（不含后缀）应等于 id
            stem = path.stem
            if stem != plugin_id:
                errors.append(
                    f"{path.name}: 文件名 '{stem}' 与 id '{plugin_id}' 不一致"
                )
            # id 唯一性
            if plugin_id in seen:
                errors.append(
                    f"{path.name}: id '{plugin_id}' 与 {seen[plugin_id].name} 重复"
                )
            else:
                seen[plugin_id] = path

        _check_required_fields(data, path.name, errors)
        _check_repo_url(data, path.name, errors)

    if errors:
        print("❌ 插件清单校验失败：")
        for err in errors:
            print(f"   - {err}")
        return 1

    print(f"✅ 校验通过：{len(files)} 个插件清单，格式正确、id 唯一、repo 可达")
    for path in files:
        print(f"   - {path.stem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
