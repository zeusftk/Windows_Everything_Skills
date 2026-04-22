#!/usr/bin/env python3
"""
IPC Skill 验证器 - 验证生成的 IPC Skill 文件结构

用法:
    python validate_ipc_skill.py <skill_directory>

示例:
    python validate_ipc_skill.py ./skills/ipc-desktop
    python validate_ipc_skill.py ./skills/ipc-web
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "metadata",
    "always",
    "license",
    "allowed-tools",
    "version",
    "provides",
    "use_cases",
}
PLACEHOLDER_MARKERS = ("[todo", "todo:")


def _extract_frontmatter(content: str) -> str | None:
    """提取 YAML frontmatter 内容"""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return None


def _parse_simple_frontmatter(frontmatter_text: str) -> dict[str, str] | None:
    """当 PyYAML 不可用时的简单解析器"""
    parsed: dict[str, str] = {}
    current_key: str | None = None

    for raw_line in frontmatter_text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        is_indented = raw_line[:1].isspace()
        if is_indented:
            if current_key is None:
                return None
            current_value = parsed[current_key]
            parsed[current_key] = f"{current_value}\n{stripped}" if current_value else stripped
            continue

        if ":" not in stripped:
            return None

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            return None

        if value in {"|", ">"}:
            parsed[key] = ""
            current_key = key
            continue

        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        parsed[key] = value
        current_key = key

    return parsed


def _load_frontmatter(frontmatter_text: str) -> tuple[dict | None, str | None]:
    """加载 frontmatter，优先使用 PyYAML"""
    if yaml is not None:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as exc:
            return None, f"YAML 格式错误: {exc}"
        if not isinstance(frontmatter, dict):
            return None, "frontmatter 必须是字典"
        return frontmatter, None

    frontmatter = _parse_simple_frontmatter(frontmatter_text)
    if frontmatter is None:
        return None, "YAML 格式错误"
    return frontmatter, None


def _validate_skill_name(name: str, folder_name: str) -> str | None:
    """验证 skill 名称格式"""
    if not re.fullmatch(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", name):
        return f"名称 '{name}' 必须是连字符或下划线小写格式"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return f"名称过长 ({len(name)} 字符)"
    if name != "ipc" and "ipc-" not in name:
        return "IPC skill 名称应为 'ipc' 或以 'ipc-' 开头"
    return None


def _validate_description(description: str) -> str | None:
    """验证描述内容"""
    trimmed = description.strip()
    if not trimmed:
        return "描述不能为空"
    lowered = trimmed.lower()
    if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
        return "描述仍包含 TODO 占位符"
    if len(trimmed) > 1024:
        return f"描述过长 ({len(trimmed)} 字符)"
    return None


def _validate_api_list_content(content: str) -> list[str]:
    """验证 API 列表内容"""
    warnings = []

    has_api_section = (
        "## API列表" in content
        or "## API List" in content
        or "## 功能索引" in content
    )
    if not has_api_section:
        warnings.append("缺少 API 列表部分")

    if "### " not in content:
        warnings.append("未找到 API 详情部分")

    has_param_or_func = (
        "输入:" in content
        or "输出:" in content
        or "描述:" in content
    )
    if not has_param_or_func:
        warnings.append("缺少参数或功能描述说明")

    if "指令:" not in content:
        warnings.append("API 列表缺少 '指令' 字段")

    if "触发词:" not in content:
        warnings.append("API 列表缺少 '触发词' 字段")

    has_triggers_section = "## 触发词" in content
    if not has_triggers_section:
        warnings.append("缺少触发词列表部分")

    if "## 示例" not in content and "## 使用示例" not in content:
        warnings.append("缺少示例部分")

    if "BridgeClient" not in content and "IPCClient" not in content:
        warnings.append("示例代码应使用 BridgeClient 或 IPCClient")

    if "## 模块信息" not in content:
        warnings.append("缺少模块信息部分")

    has_module_info = (
        "模块ID" in content
        and "名称" in content
        and "版本" in content
        and "API数" in content
    )
    if not has_module_info:
        warnings.append("模块信息应包含模块ID、名称、版本、API数")

    return warnings


def _validate_meta_skill_content(content: str, frontmatter: dict) -> list[str]:
    warnings = []

    if "sub_skills" not in frontmatter:
        warnings.append("meta skill 缺少 'sub_skills' 字段")
    elif not isinstance(frontmatter["sub_skills"], list):
        warnings.append("'sub_skills' 必须是列表")
    elif len(frontmatter["sub_skills"]) == 0:
        warnings.append("'sub_skills' 不能为空")

    if "provides" not in frontmatter:
        warnings.append("meta skill 缺少 'provides' 字段")

    if "metadata" not in frontmatter:
        warnings.append("meta skill 缺少 'metadata' 字段")

    if "## 子 Skills" not in content:
        warnings.append("缺少 '子 Skills' 部分")

    if "## 子 Skill 路径索引" not in content:
        warnings.append("meta skill 缺少 '子 Skill 路径索引' 部分")

    if "## 脚本路径" not in content:
        warnings.append("meta skill 缺少 '脚本路径' 部分")

    if "## 使用说明" not in content and "## 使用说明" not in content:
        warnings.append("meta skill 缺少 '使用说明' 部分")

    if "BridgeClient" not in content and "IPCClient" not in content:
        warnings.append("meta skill 示例代码应使用 BridgeClient 或 IPCClient")

    if "## 触发词索引" not in content:
        warnings.append("meta skill 缺少 '触发词索引' 部分")

    if "## 概述" not in content:
        warnings.append("meta skill 缺少 '概述' 部分")

    has_relative_paths = "./ipc-" in content and "SKILL.md" in content
    if not has_relative_paths:
        warnings.append("meta skill 应包含子 skill 的相对路径信息")

    return warnings


def validate_ipc_skill(skill_path) -> tuple[bool, str]:
    """验证 IPC Skill 文件结构"""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        return False, f"目录不存在: {skill_path}"
    if not skill_path.is_dir():
        return False, f"不是目录: {skill_path}"

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "缺少 SKILL.md"

    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"无法读取 SKILL.md: {exc}"

    frontmatter_text = _extract_frontmatter(content)
    if frontmatter_text is None:
        return False, "frontmatter 格式错误"

    frontmatter, error = _load_frontmatter(frontmatter_text)
    if error:
        return False, error

    if "name" not in frontmatter:
        return False, "缺少 'name' 字段"
    if "description" not in frontmatter:
        return False, "缺少 'description' 字段"

    name = frontmatter["name"]
    if not isinstance(name, str):
        return False, "name 必须是字符串"
    name_error = _validate_skill_name(name.strip(), skill_path.name)
    if name_error:
        return False, name_error

    description = frontmatter["description"]
    if not isinstance(description, str):
        return False, "description 必须是字符串"
    desc_error = _validate_description(description)
    if desc_error:
        return False, desc_error

    is_meta = frontmatter.get("metadata", {}).get("clawbot", {}).get("type") == "meta"
    api_warnings: list[str] = []
    if is_meta:
        meta_warnings = _validate_meta_skill_content(content, frontmatter)
        api_warnings.extend(meta_warnings)
    else:
        api_warnings = _validate_api_list_content(content)

    message = "验证通过"
    if api_warnings:
        message += f" (警告: {', '.join(api_warnings)})"

    return True, message


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python validate_ipc_skill.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_ipc_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
