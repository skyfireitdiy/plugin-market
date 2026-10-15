#!/usr/bin/env python3
"""校验 plugin-market 仓库 plugins/ 目录下所有插件清单的 id 唯一性。

检查项：
1. 每个 plugins/*.yaml 都能被 YAML 解析，且是 mapping。
2. 每个文件必须声明 id 字段。
3. id 在全部清单中唯一（不重复）。
4. 文件名（不含 .yaml 后缀）等于 id（README 约定：文件名 = 插件 id）。

退出码：全部通过返回 0，任一失败返回 1（供 GitHub Action 判定）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# 模板/示例文件不参与校验
SKIP_FILES = {"_example.yaml"}

PLUGINS_DIR = Path(__file__).resolve().parent.parent / "plugins"


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
            continue

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

    if errors:
        print("❌ 插件清单校验失败：")
        for err in errors:
            print(f"   - {err}")
        return 1

    print(f"✅ 校验通过：{len(files)} 个插件清单，id 均唯一且文件名与 id 一致")
    for path in files:
        print(f"   - {path.stem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
