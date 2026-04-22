#!/usr/bin/env python3
"""
IPC Skills 初始化器 - 初始化 IPC Skills Creator 项目

用法:
    python init_ipc_skills.py <project_path> [options]

示例:
    python init_ipc_skills.py ./my-ipc-skills
    python init_ipc_skills.py ./my-ipc-skills --include-examples
"""

import argparse
import sys
from pathlib import Path

SKILL_CREATOR_TEMPLATE = """---
name: ipc-create-skills
description: 自动化创建和更新 IPC skills 的 meta-skill。基于 all_api_spec 数据生成标准化的 IPC skill 文件。
---

# IPC Skills 创建器

用于从 IPC 服务的 API 规范自动生成、安装和更新 IPC skill 文件。

## 核心工作流程

1. **连接 IPC 服务** - 使用 `ipc_client.py` 建立连接
2. **获取 API 规范** - 调用 `all_api_spec` API
3. **解析和提取** - 解析 API 结构，智能提取触发词
4. **生成 skill 文件** - 为每个模块生成标准化 SKILL.md
5. **验证结果** - 确保生成的文件结构正确

## 快速开始

### 生成所有 IPC skills

```bash
python scripts/ipc_skills_creator.py
```

### 生成单个模块

```bash
python scripts/ipc_skills_creator.py --module desktop
```

### 预览模式（不生成文件）

```bash
python scripts/ipc_skills_creator.py --dry-run
```

## 连接 IPC 服务

```python
from scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send("all_api_spec", {})
    result = response.get("payload", {}).get("result", {})
```

**连接信息**:
- 默认主机: `127.0.0.1`
- 默认端口: `9527`
- 协议: TCP Socket

## 前置条件

- FTK_Claw_Bot IPC 服务运行中（端口 9527）
- Python 3.8+
- 输出目录有写入权限
"""

IPC_CLIENT_TEMPLATE = '''# -*- coding: utf-8 -*-
"""
IPC Client - IPC 服务连接客户端
"""

import socket
import json
import uuid
from datetime import datetime


def create_message(action: str, params: dict = None) -> dict:
    return {
        "version": "1.0",
        "type": "request",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "payload": {"action": action, "params": params or {}}
    }


def receive_message(sock: socket.socket) -> dict:
    data = b""
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            raise ConnectionError("连接已关闭")
        data += chunk
        if b"\\n" in chunk:
            break
    return json.loads(data.decode("utf-8").strip())


class IPCClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 9527):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(120)
        self.sock.connect((self.host, self.port))

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def send(self, action: str, params: dict = None, timeout: int = 120) -> dict:
        if not self.sock:
            raise ConnectionError("未连接到 IPC 服务")

        self.sock.settimeout(timeout)
        msg = create_message(action, params)
        self.sock.sendall((json.dumps(msg) + "\\n").encode("utf-8"))

        return receive_message(self.sock)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
'''

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
示例脚本 - 获取所有 API 规范
"""

from ipc_client import IPCClient


def main():
    with IPCClient() as client:
        response = client.send("all_api_spec", {})
        result = response.get("payload", {}).get("result", {})

        if result.get("success"):
            print(f"总 API 数量: {result.get('total_apis')}")

            for module_id, module_data in result.get("actions", {}).items():
                api_count = len(module_data.get("apis", []))
                print(f"  {module_id}: {api_count} APIs")
        else:
            print(f"错误: {result.get('error')}")


if __name__ == "__main__":
    main()
'''


def create_project(project_path: Path, include_examples: bool = False) -> bool:
    """创建 IPC Skills Creator 项目"""
    project_path = project_path.resolve()

    if project_path.exists():
        print(f"[ERROR] 目录已存在: {project_path}")
        return False

    try:
        project_path.mkdir(parents=True)
    except Exception as e:
        print(f"[ERROR] 创建目录失败: {e}")
        return False

    (project_path / "scripts").mkdir()
    (project_path / "references").mkdir()

    skill_md = project_path / "SKILL.md"
    skill_md.write_text(SKILL_CREATOR_TEMPLATE, encoding="utf-8")
    print("[OK] 创建 SKILL.md")

    client_script = project_path / "scripts" / "ipc_client.py"
    client_script.write_text(IPC_CLIENT_TEMPLATE, encoding="utf-8")
    print("[OK] 创建 scripts/ipc_client.py")

    if include_examples:
        example = project_path / "scripts" / "example.py"
        example.write_text(EXAMPLE_SCRIPT, encoding="utf-8")
        example.chmod(0o755)
        print("[OK] 创建 scripts/example.py")

    skill_id = project_path / ".skill_id"
    skill_id.write_text("ipc-create-skills\\n", encoding="utf-8")
    print("[OK] 创建 .skill_id")

    print(f"\\n[OK] 项目已创建: {project_path}")
    print("\\n下一步:")
    print("1. 运行 python scripts/ipc_skills_creator.py --skills-root <path>")
    print("2. 预览: python scripts/ipc_skills_creator.py --dry-run")
    print("3. 生成: python scripts/ipc_skills_creator.py --skills-root ./skills")

    return True


def main():
    parser = argparse.ArgumentParser(description="初始化 IPC Skills Creator 项目")
    parser.add_argument("project_path", help="项目目录路径")
    parser.add_argument("--include-examples", action="store_true", help="包含示例脚本")
    args = parser.parse_args()

    project_path = Path(args.project_path)

    print(f"初始化 IPC Skills Creator 项目: {project_path}")
    print()

    success = create_project(project_path, args.include_examples)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
