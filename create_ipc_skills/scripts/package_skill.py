#!/usr/bin/env python3
"""
IPC Skill Packager - 打包 IPC Skill 为可分发的 .skill 文件

用法:
    python package_skill.py <skill_directory> [output_directory]

示例:
    python package_skill.py ./skills/ipc-desktop
    python package_skill.py ./skills/ipc-desktop ./dist
"""

import sys
import zipfile
from pathlib import Path

try:
    from validate_ipc_skill import validate_ipc_skill
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from validate_ipc_skill import validate_ipc_skill


def _is_within(path: Path, root: Path) -> bool:
    """检查路径是否在根目录内"""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _cleanup_partial_archive(skill_filename: Path) -> None:
    """清理不完整的归档文件"""
    try:
        if skill_filename.exists():
            skill_filename.unlink()
    except OSError:
        pass


def package_skill(skill_path, output_dir=None):
    """
    打包 IPC Skill 为 .skill 文件（zip 格式）

    Args:
        skill_path: skill 目录路径
        output_dir: 输出目录，默认为当前目录

    Returns:
        打包后的 .skill 文件路径，或 None 表示失败
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"[ERROR] 目录不存在: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"[ERROR] 不是目录: {skill_path}")
        return None

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] SKILL.md 不存在: {skill_path}")
        return None

    print("验证 skill 结构...")
    valid, message = validate_ipc_skill(skill_path)
    if not valid:
        print(f"[ERROR] 验证失败: {message}")
        print("   请先修复验证错误再打包。")
        return None
    print(f"[OK] {message}\n")

    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    excluded_dirs = {".git", ".svn", ".hg", "__pycache__", "node_modules", ".trae", "evals", "dist"}

    files_to_package = []
    resolved_archive = skill_filename.resolve()

    for file_path in skill_path.rglob("*"):
        if file_path.is_symlink():
            print(f"[ERROR] 不允许包含符号链接: {file_path}")
            _cleanup_partial_archive(skill_filename)
            return None

        rel_parts = file_path.relative_to(skill_path).parts
        if any(part in excluded_dirs for part in rel_parts):
            continue

        if file_path.is_file():
            resolved_file = file_path.resolve()
            if not _is_within(resolved_file, skill_path):
                print(f"[ERROR] 文件超出 skill 根目录: {file_path}")
                _cleanup_partial_archive(skill_filename)
                return None

            if resolved_file == resolved_archive:
                print(f"[WARN] 跳过输出归档文件: {file_path}")
                continue

            files_to_package.append(file_path)

    try:
        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_package:
                arcname = Path(skill_name) / file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)
                print(f"  已添加: {arcname}")

        print(f"\n[OK] 成功打包 skill 到: {skill_filename}")
        return skill_filename

    except Exception as e:
        _cleanup_partial_archive(skill_filename)
        print(f"[ERROR] 创建 .skill 文件失败: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_directory> [output_directory]")
        print("\n示例:")
        print("  python package_skill.py ./skills/ipc-desktop")
        print("  python package_skill.py ./skills/ipc-desktop ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"打包 skill: {skill_path}")
    if output_dir:
        print(f"   输出目录: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
