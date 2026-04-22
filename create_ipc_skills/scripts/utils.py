#!/usr/bin/env python3
"""
工具函数集合 - IPC Skills Creator 辅助工具
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List


def normalize_skill_name(name: str) -> str:
    """标准化 skill 名称为小写连字符格式"""
    normalized = name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case_name(name: str) -> str:
    """将连字符名称转换为标题格式"""
    return " ".join(word.capitalize() for word in name.split("-"))


def extract_module_name(module_id: str) -> str:
    """从模块 ID 提取显示名称"""
    return module_id.replace("_", " ").title()


def format_api_table(apis: List[Dict[str, Any]]) -> str:
    """格式化 API 列表为 Markdown 表格"""
    if not apis:
        return "无 API"

    table = "| API | 描述 | 测试状态 |\n"
    table += "|-----|------|----------|\n"

    for api in apis:
        action = api.get("action", "N/A")
        desc = api.get("description", "N/A")
        status = api.get("test_status", "unknown")
        table += f"| `{action}` | {desc} | {status} |\n"

    return table


def count_apis_by_type(apis: List[Dict[str, Any]]) -> Dict[str, int]:
    """按 API 类型统计数量"""
    type_counts = {}
    for api in apis:
        api_type = api.get("api_type", "unknown")
        type_counts[api_type] = type_counts.get(api_type, 0) + 1
    return type_counts


def validate_json_structure(data: Dict[str, Any], required_keys: List[str]) -> bool:
    """验证 JSON 数据结构是否包含必需键"""
    return all(key in data for key in required_keys)


def save_json(data: Dict[str, Any], path: Path) -> None:
    """保存数据为 JSON 文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Dict[str, Any]:
    """从 JSON 文件加载数据"""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def generate_skill_id(name: str) -> str:
    """生成 skill_id 内容"""
    return name


def ensure_skill_id(skill_dir: Path, skill_name: str) -> Path:
    """确保 skill 目录包含 .skill_id 文件"""
    skill_id_file = skill_dir / ".skill_id"
    if not skill_id_file.exists():
        skill_id_file.write_text(f"{skill_name}\n", encoding="utf-8")
    return skill_id_file


def detect_clawbot_root(start_path: Path = None) -> Path | None:
    """向上查找 clawbot 项目根目录"""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    for _ in range(10):
        if current == current.parent:
            break

        skills_dir = current / "clawbot" / "skills"
        if skills_dir.exists() and skills_dir.is_dir():
            return current

        if (current / "skills").exists() and (current / "skills").is_dir():
            if (current / "clawbot").exists():
                return current

        current = current.parent

    return None


def detect_skills_root(start_path: Path = None) -> Path | None:
    """检测 clawbot skills 根目录"""
    clawbot_root = detect_clawbot_root(start_path)
    if clawbot_root:
        skills_dir = clawbot_root / "clawbot" / "skills"
        if skills_dir.exists():
            return skills_dir
        skills_dir2 = clawbot_root / "skills"
        if skills_dir2.exists():
            return skills_dir2
    return None
