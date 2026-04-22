# -*- coding: utf-8 -*-
"""
IPC Skills Creator - IPC Skills 自动创建/更新工具

此脚本用于基于 all_api_spec API 自动创建和更新 IPC Skill 文件。

功能:
1. 连接 IPC 服务获取 all_api_spec 数据
2. 解析 API 规范并提取结构化信息
3. 为每个模块生成标准化 SKILL.md 文件
4. 自动生成顶层 meta SKILL.md 索引（默认启用）
5. 支持首次安装和增量更新
6. 智能触发词提取和配置
7. 支持中英文版本生成
8. 自动检测并安装到 clawbot/skills/ipc/ 目录

使用方法:
    python ipc_skills_creator.py [options]

参数:
    --module MODULE       指定模块 ID (默认: 所有模块)
    --skills-root PATH    clawbot skills 根目录 (默认: 自动检测)
    --output-dir DIR      输出目录 (已废弃，使用 --skills-root)
    --host HOST           IPC 服务主机 (默认: 自动检测)
    --port PORT           IPC 服务端口 (默认: 9527)
    --lang LANG           语言版本 zh/en (默认: zh)
    --force               强制重新生成
    --dry-run             仅分析不生成
    --verbose             显示详细日志
    --generate-meta       生成 meta SKILL.md (默认启用)
    --no-meta             不生成 meta SKILL.md

作者: Clawbot Team
版本: 1.1.0
"""

import argparse
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Set, Tuple

from loguru import logger

try:
    from ipc_client import IPCClient, create_message, receive_message, send_request
    from utils import (
        detect_skills_root,
        ensure_skill_id,
    )
except ImportError:
    import json
    import socket
    import uuid

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
                raise Exception("连接已关闭")
            data += chunk
            if b"\n" in chunk:
                break
        return json.loads(data.decode("utf-8").strip())

    def send_request(sock: socket.socket, action: str, params: dict, timeout: int = 120, skip_identify: bool = False) -> dict:
        sock.settimeout(timeout)

        if not skip_identify:
            try:
                initial_response = receive_message(sock)
                if initial_response.get("type") == "request" and initial_response.get("payload", {}).get("action") == "request_identify":
                    identify_msg = create_message("identify", {
                        "client_name": "ipc_skills_creator",
                        "workspace": ""
                    })
                    sock.sendall((json.dumps(identify_msg) + "\n").encode("utf-8"))
                    receive_message(sock)
            except socket.timeout:
                pass

        msg = create_message(action, params)
        sock.sendall((json.dumps(msg) + "\n").encode("utf-8"))

        return receive_message(sock)

    class IPCClient:
        def __init__(self, host: str = "127.0.0.1", port: int = 9527):
            self.host = host
            self.port = port
            self.sock = None
            self._identified = False

        def connect(self):
            import socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(120)
            self.sock.connect((self.host, self.port))

        def close(self):
            if self.sock:
                self.sock.close()
                self.sock = None
                self._identified = False

        def send(self, action: str, params: dict = None, timeout: int = 120) -> dict:
            if not self.sock:
                raise Exception("未连接到 IPC 服务")
            skip_identify = self._identified
            result = send_request(self.sock, action, params or {}, timeout, skip_identify)
            self._identified = True
            return result

        def __enter__(self):
            self.connect()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

    def ensure_skill_id(skill_dir, skill_name):
        skill_id_file = Path(skill_dir) / ".skill_id"
        if not skill_id_file.exists():
            skill_id_file.write_text(f"{skill_name}\n", encoding="utf-8")
        return skill_id_file

    def detect_skills_root(start_path=None):
        if start_path is None:
            start_path = Path.cwd()
        current = start_path.resolve()
        for _ in range(10):
            if current == current.parent:
                break
            skills_dir = current / "clawbot" / "skills"
            if skills_dir.exists() and skills_dir.is_dir():
                return current / "clawbot" / "skills"
            current = current.parent
        return None

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")


class CreatorStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CreatorResult:
    status: CreatorStatus
    message: str
    skills_created: List[str] = field(default_factory=list)
    skills_updated: List[str] = field(default_factory=list)
    skills_skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: int = 0
    total_apis: int = 0
    module_count: int = 0


class TriggerWordExtractor:
    @staticmethod
    def extract_from_api_action(action: str) -> Set[str]:
        parts = re.split(r'[_-]', action)
        return {part for part in parts if len(part) > 1}

    @staticmethod
    def extract_from_description(description: str) -> Set[str]:
        keywords = set()

        cn_patterns = [
            r'([\u4e00-\u9fa5]{2,4})',
        ]
        for pattern in cn_patterns:
            matches = re.findall(pattern, description)
            keywords.update(matches)

        en_patterns = [
            r'\b(screenshot|click|type|move|drag|scroll|navigate|open|close|get|set|list|create|delete)\b',
            r'\b(mouse|keyboard|window|browser|desktop|ocr|text|file|dir)\b',
        ]
        for pattern in en_patterns:
            matches = re.findall(pattern, description.lower())
            keywords.update(matches)

        return keywords

    @staticmethod
    def extract_from_module(module_id: str, apis: List[dict]) -> dict:
        all_en_triggers = set()
        all_cn_triggers = set()

        for api in apis:
            action_triggers = TriggerWordExtractor.extract_from_api_action(api.get("action", ""))
            desc_triggers = TriggerWordExtractor.extract_from_description(api.get("description", ""))

            all_en_triggers.update(action_triggers)
            all_cn_triggers.update(desc_triggers)

        common_stopwords_en = {'the', 'a', 'an', 'is', 'are', 'to', 'for', 'and', 'or', 'in', 'on', 'at', 'by'}
        all_en_triggers -= common_stopwords_en

        triggers_en = sorted(list(all_en_triggers))[:10]
        triggers_cn = sorted(list(all_cn_triggers))[:10]

        return {
            "triggers_en": triggers_en,
            "triggers_cn": triggers_cn,
        }


class ApiSpecParser:
    def parse_param(self, name: str, data: dict) -> dict:
        return {
            "name": name,
            "type": data.get("type", "Any"),
            "description": data.get("description", ""),
            "required": data.get("required", False),
            "default": data.get("default"),
            "enum": data.get("enum", [])
        }

    def parse_api(self, data: dict) -> dict:
        input_args = {}
        for name, param_data in data.get("input_args", {}).items():
            input_args[name] = self.parse_param(name, param_data)

        out_args = {}
        for name, param_data in data.get("out_args", {}).items():
            out_args[name] = self.parse_param(name, param_data)

        return {
            "action": data.get("action", ""),
            "api_type": data.get("api_type", ""),
            "description": data.get("description", ""),
            "input_args": input_args,
            "out_args": out_args,
            "test_status": data.get("test_status", "unknown"),
            "supports_submit": data.get("supports_submit", False)
        }

    def parse_module(self, module_id: str, data: dict) -> dict:
        apis = []
        for api_data in data.get("apis", []):
            apis.append(self.parse_api(api_data))

        return {
            "id": data.get("id", module_id),
            "name": data.get("name", module_id),
            "version": data.get("version", ""),
            "apis": apis
        }

    def parse_all(self, data: dict) -> dict:
        modules = {}
        for module_id, module_data in data.get("actions", {}).items():
            modules[module_id] = self.parse_module(module_id, module_data)

        return {
            "version": data.get("version", ""),
            "update_date": data.get("update_date", ""),
            "generated_at": data.get("generated_at", ""),
            "modules": modules,
            "total_apis": data.get("total_apis", 0)
        }


class SkillContentGenerator:
    def __init__(self, lang: str = "zh"):
        self.lang = lang
        self._all_apis = []

    def generate(self, module_id: str, module_spec: dict, triggers: dict = None) -> str:
        self._all_apis = module_spec.get("apis", [])
        if triggers is None:
            triggers = TriggerWordExtractor.extract_from_module(module_id, module_spec.get("apis", []))

        name_cn = module_spec.get("name", module_id)
        name_en = module_spec.get("name", module_id)
        triggers_cn = triggers.get("triggers_cn", [])
        triggers_en = triggers.get("triggers_en", [])

        display_name = name_cn if self.lang == "zh" else name_en
        triggers_list = triggers_en if self.lang == "en" else triggers_cn

        content = self._generate_frontmatter(module_id, display_name, triggers_list)
        content += self._generate_overview(module_id, module_spec, name_cn, name_en, triggers)
        content += self._generate_api_list(module_spec["apis"])
        content += self._generate_usage_example(module_id)
        content += self._generate_notes()

        return content

    def _generate_frontmatter(self, module_id: str, name: str, triggers: List[str]) -> str:
        api_count = len(self._all_apis)
        description = f"{name}自动化。{api_count}个IPC API。"

        return f'''---
name: "ipc-{module_id}"
description: "{description}"
---

'''

    def _generate_overview(self, module_id: str, module_spec: dict, name_cn: str, name_en: str, triggers: dict = None) -> str:
        if triggers is None:
            triggers = {}
        triggers_cn = triggers.get("triggers_cn", [])
        triggers_en = triggers.get("triggers_en", [])

        return f'''# IPC {name_en}

## 模块信息

| 属性 | 值 |
|------|-----|
| 模块ID | {module_id} |
| 名称 | {name_cn} |
| 版本 | {module_spec.get("version", "N/A")} |
| API数 | {len(module_spec["apis"])} |

## 触发词

- 中文: {", ".join(triggers_cn) if triggers_cn else "无"}
- 英文: {", ".join(triggers_en) if triggers_en else "无"}

## API列表

'''

    def _generate_api_list(self, apis: List[dict]) -> str:
        lines = []
        for api in apis:
            action = api["action"]
            desc = api["description"]

            cn_triggers = set()
            en_triggers = set()

            if desc:
                for t in TriggerWordExtractor.extract_from_description(desc):
                    if re.search(r'[\u4e00-\u9fa5]', t):
                        cn_triggers.add(t)
                    else:
                        en_triggers.add(t)

            action_parts = TriggerWordExtractor.extract_from_api_action(action)
            en_triggers.update(action_parts)

            trigger_str = ", ".join(sorted(cn_triggers)[:5] + sorted(en_triggers)[:5])

            lines.append(f"### {action}\n\n")
            lines.append(f"描述: {desc}\n")
            lines.append(f"指令: `{action}`\n")
            lines.append(f"触发词: {trigger_str}\n\n")

            if api["input_args"]:
                lines.append("输入:\n")
                for name, param in api["input_args"].items():
                    default = f", 默认={param['default']}" if param.get("default") is not None else ""
                    required = "必填" if param.get("required") else "可选"
                    lines.append(f"  - `{name}` ({param['type']}): {required}{default}\n")
                lines.append("\n")

            if api["out_args"]:
                lines.append("输出:\n")
                for name, param in api["out_args"].items():
                    lines.append(f"  - `{name}` ({param['type']})\n")
                lines.append("\n")

        return "".join(lines)

    def _generate_usage_example(self, module_id: str) -> str:
        first_api = self._all_apis[0]["action"] if self._all_apis else "api_name"
        first_api_params = "{}"
        if self._all_apis and self._all_apis[0].get("input_args"):
            sample_params = {}
            for param_name, param_info in self._all_apis[0]["input_args"].items():
                param_type = param_info.get("type", "str")
                if param_type == "int":
                    sample_params[param_name] = 0
                elif param_type == "float":
                    sample_params[param_name] = 0.0
                elif param_type == "bool":
                    sample_params[param_name] = False
                elif param_type in ("List[str]", "List"):
                    sample_params[param_name] = []
                elif param_type in ("Dict", "dict"):
                    sample_params[param_name] = {}
                else:
                    sample_params[param_name] = ""
            import json
            first_api_params = json.dumps(sample_params, ensure_ascii=False)

        return f'''## 示例

### Clawbot 内置客户端（推荐）

```python
from clawbot.extra_serve.ipc.client import BridgeClient

async def main():
    client = BridgeClient()
    await client.connect()

    # 调用 {module_id} 模块的 {first_api} API
    result = await client.send_request(
        '{first_api}',
        {first_api_params},
        '{module_id}'
    )

    print(f"结果: {{result}}")
    await client.disconnect()

import asyncio
asyncio.run(main())
```

### 外部 Agent 客户端脚本

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_client import IPCClient

# 使用上下文管理器（推荐）
with IPCClient() as client:
    response = client.send('{first_api}', {first_api_params})
    result = response.get('payload', {{}}).get('result', {{}})
    print(f"结果: {{result}}")

# 或手动管理连接
client = IPCClient()
client.connect()
try:
    response = client.send('{first_api}', {first_api_params})
    result = response.get('payload', {{}}).get('result', {{}})
    print(f"结果: {{result}}")
finally:
    client.close()
```

'''

    def _generate_notes(self) -> str:
        return '''## 注意事项

1. 所有 API 调用通过 IPC 服务（端口 9527）进行
2. 必填参数必须提供，可选参数可以省略
3. 调用前确保 IPC 服务已启动
4. Clawbot 环境使用内置 BridgeClient，其他 Agent 使用 ipc_client.py 脚本
'''


class MetaSkillGenerator:
    @staticmethod
    def generate(modules: dict, output_dir: Path, spec_info: dict = None) -> Path:
        skill_md = output_dir / "SKILL.md"
        content = MetaSkillGenerator._generate_content(modules, spec_info)
        skill_md.write_text(content, encoding="utf-8")
        return skill_md

    @staticmethod
    def _generate_content(modules: dict, spec_info: dict = None) -> str:
        module_ids = sorted(modules.keys())
        sub_skills = [f"ipc-{mid}" for mid in module_ids]

        provides_list = []
        for mid in module_ids:
            name = modules[mid].get("name", mid).replace(" ", "-").lower()
            provides_list.append(name)

        sub_skills_str = "\n".join([f"  - {s}" for s in sub_skills])
        provides_str = "\n".join([f"  - {p}" for p in provides_list])

        modules_overview = MetaSkillGenerator._generate_modules_overview(modules)
        sub_skill_paths = MetaSkillGenerator._generate_sub_skill_paths(modules)
        trigger_index = MetaSkillGenerator._generate_trigger_index(modules)
        usage_scenarios = MetaSkillGenerator._generate_usage_scenarios(modules)

        version = spec_info.get("version", "N/A") if spec_info else "N/A"
        generated_at = spec_info.get("generated_at", "") if spec_info else ""
        total_apis = sum(len(m.get("apis", [])) for m in modules.values())

        return f'''---
name: ipc
description: |
  IPC 自动化技能集，提供桌面、网页、OCR、微信等系统自动化能力。

provides:
{provides_str}

sub_skills:
{sub_skills_str}

metadata:
  clawbot:
    type: meta
    category: automation
    always: false
    priority: 85
    generated_by: ipc-create-skills
    generated_at: {generated_at}
    api_version: {version}
---

# IPC Skills | 系统自动化

## 概述

IPC (Inter-Process Communication) 自动化技能集，包含 {len(modules)} 个子模块，共 {total_apis} 个API。

## 脚本路径

- **Clawbot 内置客户端**: `clawbot.extra_serve.ipc.client.BridgeClient`
- **外部 Agent 客户端**: `clawbot.skills.create_ipc_skills.scripts.ipc_client.IPCClient`

## 子 Skill 路径索引

所有子 skill 文件相对于本文件所在目录（`skills/ipc/`）的路径：

{sub_skill_paths}

## 触发词索引

{trigger_index}

## 子 Skills

{modules_overview}

## 使用流程

```
用户需求 → ipc (自动路由) → 对应子 skill → IPC API 调用
```

## 使用场景

{usage_scenarios}

## 前置条件

- FTK_Claw_Bot IPC 服务运行中（端口 9527）
- 相关模块已注册到 IPC 服务

## 使用说明

### Clawbot 内置客户端（推荐）

```python
from clawbot.extra_serve.ipc.client import BridgeClient

async def main():
    client = BridgeClient()
    await client.connect()

    # 调用桌面截图 API
    result = await client.send_request(
        'desktop_screenshot',
        {{}},
        'desktop'
    )

    # 调用其他模块 API
    # result = await client.send_request('api_name', {{}}, 'module_name')

    await client.disconnect()

import asyncio
asyncio.run(main())
```

### 外部 Agent 客户端脚本

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_client import IPCClient

# 方式一：使用上下文管理器（推荐）
with IPCClient() as client:
    # 获取所有 API 规范
    response = client.send('all_api_spec', {{}})
    result = response.get('payload', {{}}).get('result', {{}})
    print(f"总 API 数量: {{result.get('total_apis')}}")

    # 调用特定模块 API
    # response = client.send('api_name', {{'param': 'value'}})
    # result = response.get('payload', {{}}).get('result', {{}})

# 方式二：手动管理连接
client = IPCClient()
client.connect()
try:
    response = client.send('desktop_screenshot', {{}})
    result = response.get('payload', {{}}).get('result', {{}})
    print(f"结果: {{result}}")
finally:
    client.close()
```

## 相关技能

- **@create_ipc_skills** - 生成和更新 IPC skills
'''

    @staticmethod
    def _generate_modules_overview(modules: dict) -> str:
        sections = []
        category_map = {
            "desktop": ("桌面自动化", "鼠标、键盘、窗口、文件操作"),
            "web": ("网页自动化", "浏览器控制、网页操作"),
            "ocr": ("OCR 识别", "文字识别、截图 OCR"),
            "system": ("系统控制", "系统信息、进程管理"),
            "embedding": ("AI 嵌入", "向量嵌入、语义搜索"),
            "app_registry": ("应用注册", "应用注册管理"),
            "api_spec": ("API 规范", "API 规范查询"),
            "opencli": ("CLI 执行", "命令行执行"),
            "wechat": ("微信集成", "微信自动化"),
        }

        for module_id in sorted(modules.keys()):
            module = modules[module_id]
            api_count = len(module.get("apis", []))
            category, desc = category_map.get(module_id, (module_id, "IPC 操作"))
            relative_path = f"ipc-{module_id}/SKILL.md"
            sections.append(f"### {category}\n- **ipc-{module_id}** - {desc} ({api_count} APIs)\n  - 路径: `{relative_path}`")

        return "\n\n".join(sections)

    @staticmethod
    def _generate_sub_skill_paths(modules: dict) -> str:
        """生成子 skill 的相对路径索引表格"""
        table = "| Skill 名称 | 相对路径 | 文件 |\n"
        table += "|-----------|---------|------|\n"

        for module_id in sorted(modules.keys()):
            skill_name = f"ipc-{module_id}"
            relative_dir = f"./{skill_name}/"
            skill_file = f"./{skill_name}/SKILL.md"
            skill_id_file = f"./{skill_name}/.skill_id"

            table += f"| **{skill_name}** | `{relative_dir}` | `{skill_file}`<br>`{skill_id_file}` |\n"

        return table

    @staticmethod
    def _generate_trigger_index(modules: dict) -> str:
        lines = []
        for module_id in sorted(modules.keys()):
            module = modules[module_id]
            apis = module.get("apis", [])

            cn_triggers = set()
            en_triggers = set()

            for api in apis:
                action = api.get("action", "")
                desc = api.get("description", "")

                all_triggers = TriggerWordExtractor.extract_from_description(desc)
                action_triggers = TriggerWordExtractor.extract_from_api_action(action)

                for t in all_triggers:
                    if re.search(r'[\u4e00-\u9fa5]', t):
                        cn_triggers.add(t)
                    else:
                        en_triggers.add(t)

                en_triggers.update(action_triggers)

            triggers_str = ", ".join(sorted(cn_triggers) + sorted(en_triggers))
            if len(triggers_str) > 200:
                triggers_str = triggers_str[:200] + "..."

            lines.append(f"- **ipc-{module_id}**: {triggers_str}")

        return "\n".join(lines)

    @staticmethod
    def _generate_usage_scenarios(modules: dict) -> str:
        scenario_map = {
            "desktop": [
                ("自动化桌面操作", "ipc-desktop"),
                ("鼠标点击和移动", "ipc-desktop"),
                ("键盘输入和快捷键", "ipc-desktop"),
                ("窗口管理和操作", "ipc-desktop"),
                ("文件读写和管理", "ipc-desktop"),
                ("PowerShell 命令执行", "ipc-desktop"),
            ],
            "web": [
                ("浏览器自动化控制", "ipc-web"),
                ("网页导航和交互", "ipc-web"),
                ("表单填写和提交", "ipc-web"),
            ],
            "ocr": [
                ("文字识别 OCR", "ipc-ocr"),
                ("截图文字提取", "ipc-ocr"),
            ],
            "system": [
                ("系统信息查询", "ipc-system"),
                ("进程管理", "ipc-system"),
            ],
            "embedding": [
                ("语义搜索", "ipc-embedding"),
                ("向量嵌入", "ipc-embedding"),
            ],
        }

        default_scenarios = [
            ("自动化操作", "对应模块"),
        ]

        scenarios = []
        for module_id in sorted(modules.keys()):
            module_scenarios = scenario_map.get(module_id, default_scenarios)
            scenarios.extend(module_scenarios)

        if not scenarios:
            scenarios = default_scenarios

        table = "| 场景 | 使用子 Skill |\n"
        table += "|------|-------------|\n"
        for scenario, skill in scenarios:
            table += f"| {scenario} | {skill} |\n"

        return table


class IPCCreateSkills:
    def __init__(self, output_dir: str = "./skills", host: str = "127.0.0.1", port: int = 9527, lang: str = "zh", verbose: bool = False, generate_meta: bool = True, skills_root: str = None):
        self.original_output_dir = Path(output_dir)
        self.host = host
        self.port = port
        self.lang = lang
        self.verbose = verbose
        self.generate_meta = generate_meta
        self.parser = ApiSpecParser()
        self.content_generator = SkillContentGenerator(lang)

        if skills_root:
            self.skills_root = Path(skills_root)
        else:
            detected = detect_skills_root()
            if detected:
                self.skills_root = detected
                logger.info("自动检测到 skills 根目录: {}", detected)
            else:
                self.skills_root = Path.cwd()
                logger.warning("未检测到 clawbot/skills 目录，将使用当前目录")

        self.output_dir = self.skills_root / "ipc"
        logger.info('输出目录: {}', self.output_dir)

        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")

    def fetch_api_specs(self, module: str = None, action_filter: str = None) -> dict:
        params = {}
        if module:
            params["module"] = module
        if action_filter:
            params["action_filter"] = action_filter

        with IPCClient(self.host, self.port) as client:
            logger.info("获取 all_api_spec 数据...")
            response = client.send("all_api_spec", params)

            api_result = response.get("payload", {}).get("result", {})
            if not api_result.get("success"):
                raise Exception(f"获取 API 规范失败: {api_result.get('error')}")

            logger.info('成功获取 {} 个 API 规范', api_result.get('total_apis'))
            return api_result

    def create_skill_file(self, module_id: str, module_spec: dict, force: bool = False) -> Path:
        skill_dir = self.output_dir / f"ipc-{module_id}"
        skill_dir.mkdir(parents=True, exist_ok=True)

        ensure_skill_id(skill_dir, f"ipc-{module_id}")

        skill_file = skill_dir / "SKILL.md"

        if skill_file.exists() and not force:
            logger.info('跳过 {}: Skill 文件已存在 (使用 --force 强制重新生成)', module_id)
            return skill_file

        triggers = TriggerWordExtractor.extract_from_module(module_id, module_spec.get("apis", []))
        content = self.content_generator.generate(module_id, module_spec, triggers)
        skill_file.write_text(content, encoding="utf-8")
        logger.info('生成 Skill 文件: {}', skill_file)

        return skill_file

    def _validate_skill(self, skill_dir: Path) -> Tuple[bool, str]:
        """验证单个 skill 文件结构"""
        try:
            try:
                from validate_ipc_skill import validate_ipc_skill
                return validate_ipc_skill(skill_dir)
            except ImportError:
                pass

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                return False, "缺少 SKILL.md"

            content = skill_md.read_text(encoding="utf-8")
            if not content.startswith("---"):
                return False, "frontmatter 格式错误"

            if "name:" not in content:
                return False, "缺少 name 字段"
            if "description:" not in content:
                return False, "缺少 description 字段"

            return True, "验证通过"
        except Exception as e:
            return False, str(e)

    def install_all_skills(self, force: bool = False, dry_run: bool = False) -> CreatorResult:
        start_time = time.time()
        result = CreatorResult(status=CreatorStatus.SUCCESS, message="")

        try:
            logger.info("=" * 60)
            logger.info("IPC Skills Creator v1.1.0")
            logger.info("=" * 60)

            api_result = self.fetch_api_specs()
            spec = self.parser.parse_all(api_result)

            result.total_apis = spec["total_apis"]
            result.module_count = len(spec["modules"])

            logger.info('版本: {}', spec.get('version', 'N/A'))
            logger.info('生成时间: {}', spec.get('generated_at', 'N/A'))
            logger.info('模块数量: {}', result.module_count)

            if dry_run:
                logger.info("[DRY RUN] 仅分析模式，不生成文件")
                for module_id, module_spec in spec["modules"].items():
                    logger.info('  - {}: {} 个 API', module_id, len(module_spec['apis']))
                result.message = "分析完成（dry-run 模式）"
                return result

            self.output_dir.mkdir(parents=True, exist_ok=True)

            for module_id, module_spec in spec["modules"].items():
                try:
                    skill_file = self.create_skill_file(module_id, module_spec, force)

                    if skill_file.exists() and skill_file.stat().st_mtime > start_time:
                        if force:
                            result.skills_updated.append(str(skill_file))
                        else:
                            result.skills_created.append(str(skill_file))
                    else:
                        result.skills_skipped.append(str(skill_file))
                except Exception as e:
                    logger.error('生成 {} Skill 失败: {}', module_id, e)
                    result.errors.append(f"{module_id}: {e}")

            if self.generate_meta:
                logger.info("生成 meta SKILL.md...")
                MetaSkillGenerator.generate(spec["modules"], self.output_dir, spec)
                ensure_skill_id(self.output_dir, "ipc")
                logger.info('生成 meta SKILL.md: {}', self.output_dir / 'SKILL.md')

            logger.info("验证生成结果...")
            validation_errors = []
            if self.generate_meta:
                meta_skill_file = self.output_dir / "SKILL.md"
                if meta_skill_file.exists():
                    meta_ok, meta_msg = self._validate_skill(self.output_dir)
                    if not meta_ok:
                        validation_errors.append(f"meta skill: {meta_msg}")
                    else:
                        logger.info("  meta SKILL.md 验证通过")
            for module_id in spec["modules"].keys():
                sub_dir = self.output_dir / f"ipc-{module_id}"
                if sub_dir.exists():
                    sub_ok, sub_msg = self._validate_skill(sub_dir)
                    if not sub_ok:
                        validation_errors.append(f"{module_id}: {sub_msg}")
                    else:
                        logger.info('  ipc-{} 验证通过', module_id)
            if validation_errors:
                for e in validation_errors:
                    logger.warning('  验证问题: {}', e)
                result.errors.extend(validation_errors)
                if result.status == CreatorStatus.SUCCESS:
                    result.status = CreatorStatus.PARTIAL
            else:
                logger.info("所有文件验证通过")

            result.message = f"成功生成 {len(result.skills_created)} 个 Skill 文件"

            if result.errors:
                result.status = CreatorStatus.PARTIAL
            else:
                result.status = CreatorStatus.SUCCESS

        except Exception as e:
            logger.error('执行失败: {}', e)
            result.status = CreatorStatus.FAILED
            result.message = str(e)
            result.errors.append(str(e))

        finally:
            result.duration_ms = int((time.time() - start_time) * 1000)

            logger.info("=" * 60)
            logger.info("执行结果")
            logger.info("=" * 60)
            logger.info('状态: {}', result.status.value)
            logger.info('消息: {}', result.message)
            logger.info('耗时: {}ms', result.duration_ms)

            if result.skills_created:
                logger.info('创建文件: {}', len(result.skills_created))
                for f in result.skills_created:
                    logger.info('  + {}', f)

            if result.skills_updated:
                logger.info('更新文件: {}', len(result.skills_updated))
                for f in result.skills_updated:
                    logger.info('  ~ {}', f)

            if result.skills_skipped:
                logger.info('跳过文件: {}', len(result.skills_skipped))
                for f in result.skills_skipped:
                    logger.info('  - {}', f)

            if result.errors:
                logger.warning('错误: {}', len(result.errors))
                for e in result.errors:
                    logger.warning('  ! {}', e)

            logger.info("=" * 60)

        return result

    def update_skill(self, module_id: str) -> CreatorResult:
        start_time = time.time()
        result = CreatorResult(status=CreatorStatus.SUCCESS, message="")

        try:
            logger.info('更新模块: {}', module_id)

            api_result = self.fetch_api_specs(module=module_id)
            spec = self.parser.parse_all(api_result)

            if module_id not in spec["modules"]:
                raise Exception(f"模块 {module_id} 不存在")

            module_spec = spec["modules"][module_id]
            result.total_apis = len(module_spec["apis"])
            result.module_count = 1

            self.output_dir.mkdir(parents=True, exist_ok=True)

            skill_file = self.create_skill_file(module_id, module_spec, force=True)
            result.skills_updated.append(str(skill_file))

            if self.generate_meta:
                logger.info("更新 meta SKILL.md...")
                all_modules = {}
                for existing_dir in self.output_dir.iterdir():
                    if existing_dir.is_dir() and existing_dir.name.startswith("ipc-") and existing_dir.name != f"ipc-{module_id}":
                        skill_id_file = existing_dir / ".skill_id"
                        if skill_id_file.exists():
                            mid = skill_id_file.read_text(encoding="utf-8").strip().replace("ipc-", "", 1)
                            all_modules[mid] = {"name": existing_dir.name.replace("ipc-", "").title(), "apis": []}
                all_modules[module_id] = module_spec
                MetaSkillGenerator.generate(all_modules, self.output_dir, spec)
                ensure_skill_id(self.output_dir, "ipc")
                logger.info('更新 meta SKILL.md: {}', self.output_dir / 'SKILL.md')

            if self.generate_meta:
                logger.info("验证更新结果...")
                sub_ok, sub_msg = self._validate_skill(self.output_dir / f"ipc-{module_id}")
                if not sub_ok:
                    logger.warning('  ipc-{} 验证问题: {}', module_id, sub_msg)
                    result.errors.append(f"{module_id}: {sub_msg}")
                else:
                    logger.info('  ipc-{} 验证通过', module_id)

                meta_ok, meta_msg = self._validate_skill(self.output_dir)
                if not meta_ok:
                    logger.warning('  meta SKILL.md 验证问题: {}', meta_msg)
                    result.errors.append(f"meta: {meta_msg}")
                else:
                    logger.info("  meta SKILL.md 验证通过")

                if result.errors:
                    result.status = CreatorStatus.PARTIAL

            result.message = f"成功更新 {module_id}"

        except Exception as e:
            logger.error('更新失败: {}', e)
            result.status = CreatorStatus.FAILED
            result.message = str(e)
            result.errors.append(str(e))

        finally:
            result.duration_ms = int((time.time() - start_time) * 1000)

        return result


def main():
    parser = argparse.ArgumentParser(description="IPC Skills Creator - 自动创建/更新 IPC Skills")
    parser.add_argument("--module", help="指定模块 ID")
    parser.add_argument("--output-dir", default="./skills", help="输出目录（已废弃，使用 --skills-root）")
    parser.add_argument("--skills-root", default=None, help="clawbot skills 根目录")
    parser.add_argument("--host", default="127.0.0.1", help="IPC 服务主机")
    parser.add_argument("--port", type=int, default=9527, help="IPC 服务端口")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="语言版本")
    parser.add_argument("--force", action="store_true", help="强制重新生成")
    parser.add_argument("--dry-run", action="store_true", help="仅分析不生成")
    parser.add_argument("--verbose", action="store_true", help="详细日志")
    parser.add_argument("--generate-meta", action="store_true", default=True, help="生成 meta SKILL.md（默认启用）")
    parser.add_argument("--no-meta", action="store_false", dest="generate_meta", help="不生成 meta SKILL.md")
    args = parser.parse_args()

    creator = IPCCreateSkills(
        output_dir=args.output_dir,
        host=args.host,
        port=args.port,
        lang=args.lang,
        verbose=args.verbose,
        generate_meta=args.generate_meta,
        skills_root=args.skills_root
    )

    if args.module:
        result = creator.update_skill(args.module)
    else:
        result = creator.install_all_skills(force=args.force, dry_run=args.dry_run)

    return 0 if result.status in [CreatorStatus.SUCCESS, CreatorStatus.PARTIAL] else 1


if __name__ == "__main__":
    sys.exit(main())
