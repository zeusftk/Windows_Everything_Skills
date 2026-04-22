***

name: ipc-create-skills
description: 自动化创建和更新 IPC skills 的 meta-skill。基于 all\_api\_spec 数据生成标准化的 IPC skill 文件。Invoke when user wants to create IPC skills, generate skills from API specs, update existing IPC skills, or sync API changes to skill files.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# IPC Skills 创建器

用于从 IPC 服务的 API 规范自动生成、安装和更新 IPC skill 文件。

## 核心工作流程

创建或更新 IPC skills 遵循以下流程：

1. **连接 IPC 服务** - 使用 `ipc_client.py` 建立连接
2. **获取 API 规范** - 调用 `all_api_spec` API
3. **解析和提取** - 解析 API 结构，智能提取触发词
4. **生成 skill 文件** - 为每个模块生成标准化 SKILL.md
5. **验证结果** - 自动验证所有生成的文件结构是否正确
6. **生成评估集** - 创建触发词评估集用于优化 
7. **运行评估** - 执行 API 测试并生成报告 
8. **优化触发词** - 基于评估结果优化触发词配置 
9. **打包分发** - 打包 skill 为 .skill 文件 

## 扩展工作流程

### 触发词评估和优化

```
生成 skill → 生成评估集 → 运行评估 → 优化触发词 → 重新生成 skill
```

### 测试驱动开发

```
编写 evals.json → 运行评估 → 查看报告 → 修复问题 → 重新评估
```

### 打包和分发

```
验证 skill → 打包 .skill 文件 → 分发到其他环境 → 安装使用

## 重要：输出路径说明

**默认行为**：所有 IPC skills 生成到系统skills（/path/to/skills）目录下：

```

/path/to/skills/ipc

````

包含：

- `skills/ipc/SKILL.md` - 顶层 meta 索引文件
- `skills/ipc/.skill_id` - 内容为 "ipc"
- `skills/ipc/ipc-desktop/` - 子 skill 目录
- `skills/ipc/ipc-web/` - 子 skill 目录
- ... 其他子 skills

**如果自动检测失败**，可以通过 `skills_root` 参数手动指定：

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

creator = IPCCreateSkills(skills_root='/path/to/clawbot/skills')
result = creator.install_all_skills()
````

## 快速开始

### 生成所有 IPC skills（默认保存到 skills/ipc/）

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

creator = IPCCreateSkills()
result = creator.install_all_skills(force=False, dry_run=False)
print(f"状态: {result.status.value}")
print(f"创建文件: {len(result.skills_created)}")
```

### 生成所有 IPC skills（指定 skills 根目录）

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

creator = IPCCreateSkills(skills_root='/path/to/clawbot/skills')
result = creator.install_all_skills()
```

### 生成单个模块

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

creator = IPCCreateSkills(skills_root='./skills')
result = creator.update_skill('desktop')
```

### 预览模式（不生成文件）

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

creator = IPCCreateSkills()
result = creator.install_all_skills(dry_run=True)
# 仅分析，不生成文件
```

### 禁用 meta SKILL.md 生成

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

creator = IPCCreateSkills(generate_meta=False)
result = creator.install_all_skills()
```

## 生成的 skill 结构

生成的 IPC skills 会自动安装到 clawbot skills 目录：

```
clawbot/skills/
├── ipc/                            # IPC meta-skill（自动生成）
│   ├── .skill_id                   # "ipc"
│   ├── SKILL.md                    # 顶层 meta 索引
│   ├── ipc-desktop/                # 子 skill
│   │   ├── .skill_id               # "ipc-desktop"
│   │   └── SKILL.md
│   ├── ipc-web/
│   ├── ipc-ocr/
│   └── ...
└── create_ipc_skills/              # 创建工具（本 skill）
```

每个生成的 IPC skill 遵循标准结构：

```
ipc-<module>/
├── .skill_id                       # skill 标识
└── SKILL.md                        # skill 说明
```

每个子 SKILL.md **必须严格遵循通用 Skills 规范**，包含以下必需内容：

### 子 SKILL.md 标准结构（必需）

#### 1. YAML Frontmatter（必需，最大 1024 字符）

```yaml
---
name: "ipc-<module>"  # 只能使用字母、数字、连字符
description: "<模块功能>。<API数量>个IPC API。"  # 简洁描述，不超过 500 字符
---
```

**规范要求：**

- `name`: 只能包含字母、数字、连字符（禁止括号、特殊字符）
- `description`: 第三人称，简洁描述模块功能和 API 数量
- 总长度不超过 1024 字符

#### 2. 模块信息表格（必需）

```markdown
## 模块信息

| 属性 | 值 |
|------|-----|
| 模块ID | <module_id> |
| 名称 | <module_name> |
| 版本 | <version> |
| API数 | <count> |
```

#### 3. 触发词（必需）

```markdown
## 触发词

- 中文: <从 API 提取的中文关键词>
- 英文: <从 API 提取的英文关键词>
```

**智能提取规则：**

- 从 API action 名称分割关键词
- 从 description 提取中文/英文关键词
- 自动过滤停用词

#### 4. 完整 API 列表（必需）

```markdown
## API列表

### <api_name>
描述: <api_description>
指令: `<api_name>`
触发词: <extracted keywords>
输入:
  - `<param>` (<type>): <required/optional>, [default=<value>]
输出:
  - `<field>` (<type>)
```

**格式要求：**

- 每个 API 独立章节
- 参数标注必填/可选
- 可选参数注明默认值
- 输出字段列出类型
- 必须包含指令和触发词字段

#### 5. 使用示例（必需）

```markdown
## 示例

### Clawbot 内置客户端（推荐）

\`\`\`python
from clawbot.extra_serve.ipc.client import BridgeClient

async def main():
    client = BridgeClient()
    await client.connect()
    result = await client.send_request('<api_name>', {}, '<module>')
    await client.disconnect()
\`\`\`

### 外部 Agent 客户端脚本

\`\`\`python
from clawbot.skills.create_ipc_skills.scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send('<api_name>', {})
    result = response.get('payload', {}).get('result', {})
\`\`\`
```

***

### 顶层 Meta SKILL.md 标准结构（必需）

Meta SKILL.md 作为索引文件，**必须严格遵循通用 Skills 规范**，包含以下必需内容：

#### 1. YAML Frontmatter（必需，最大 1024 字符）

```yaml
---
name: "ipc"
description: |
  IPC 自动化技能集，提供系统自动化能力。

provides:
  - desktop
  - web
  - ocr

sub_skills:
  - ipc-desktop
  - ipc-web
  - ipc-ocr

metadata:
  clawbot:
    type: meta
    category: automation
    always: false
    priority: 85
---
```

**规范要求：**

- `name`: 简洁的模块标识符
- `description`: 描述整体功能和规模
- 总长度不超过 1024 字符

#### 2. 概述章节（必需）

```markdown
## 概述

IPC (Inter-Process Communication) 自动化技能集，包含 <N> 个子模块，共 <M> 个API。
```

#### 3. 脚本路径（必需）

```markdown
## 脚本路径

- **Clawbot 内置客户端**: `clawbot.extra_serve.ipc.client.BridgeClient`
- **外部 Agent 客户端**: `clawbot.skills.create_ipc_skills.scripts.ipc_client.IPCClient`
```

#### 4. 子 Skill 路径索引（必需）

用于提高子 skill 文件的检索能力，明确指定每个子 skill 相对于主 SKILL.md 的路径：

```markdown
## 子 Skill 路径索引

所有子 skill 文件相对于本文件所在目录（`skills/ipc/`）的路径：

| Skill 名称 | 相对路径 | 文件 |
|-----------|---------|------|
| **ipc-desktop** | `./ipc-desktop/` | `./ipc-desktop/SKILL.md` |
| **ipc-web** | `./ipc-web/` | `./ipc-web/SKILL.md` |
```

#### 5. 触发词索引（必需）

```markdown
## 触发词索引

- **ipc-desktop**: 鼠标点击, 键盘输入, 窗口操作, ...
- **ipc-web**: 浏览器控制, 网页导航, ...
- **ipc-ocr**: 文字识别, OCR, ...
```

#### 6. 子 Skills 索引表格（必需）

每个子 skill 条目需包含相对路径信息：

```markdown
## 子 Skills

### 桌面自动化
- **ipc-desktop** - 鼠标、键盘、窗口操作 (N APIs)
  - 路径: `ipc-desktop/SKILL.md`

### 网页自动化
- **ipc-web** - 浏览器控制 (N APIs)
  - 路径: `ipc-web/SKILL.md`
```

#### 7. 使用场景说明（必需）

```markdown
## 使用场景

| 场景 | 使用子 Skill |
|------|-------------|
| 自动化桌面操作 | ipc-desktop |
| 控制浏览器 | ipc-web |
| 文字识别 | ipc-ocr |
```

#### 7. 前置条件（必需）

```markdown
## 前置条件

- FTK_Claw_Bot IPC服务运行中（端口9527）
- Python 3.8+
```

#### 8. 使用说明（必需，包含客户端示例）

```markdown
## 使用说明

### Clawbot 内置客户端（推荐）

\`\`\`python
from clawbot.extra_serve.ipc.client import BridgeClient

async def main():
    client = BridgeClient()
    await client.connect()
    result = await client.send_request('api_name', {}, 'module')
    await client.disconnect()
\`\`\`

### 外部 Agent 客户端脚本

\`\`\`python
from clawbot.skills.create_ipc_skills.scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send('api_name', {})
    result = response.get('payload', {}).get('result', {})
\`\`\`
```

***

### ⚠️ 重要：通用 Skills 规范合规性检查

生成的所有 IPC skills **必须符合**以下通用规范：

| 规范项                | 要求                          | 验证方法                |
| ------------------ | --------------------------- | ------------------- |
| **Frontmatter 字段** | 只包含 `name` 和 `description`  | 检查 YAML 头部          |
| **Frontmatter 长度** | 最大 1024 字符                  | `wc -c` 统计          |
| **Name 格式**        | 只含字母、数字、连字符                 | 正则验证 `^[a-z0-9-]+$` |
| **Description 格式** | 第三人称，描述何时使用                 | 人工审核                |
| **SKILL.md 大小**    | 建议 < 500 行                  | `wc -l` 统计          |
| **目录结构**           | 必须包含 `.skill_id` 文件         | 检查文件存在性             |
| **API 字段完整性**      | 包含名称、指令、描述、触发词、输入输出参数       | 内容检查                |
| **示例代码**           | 使用 BridgeClient 或 IPCClient | 代码检查                |

**验证脚本：**

```python
# 验证单个 skill
from clawbot.skills.create_ipc_skills.scripts.validate_ipc_skill import validate_ipc_skill

valid, message = validate_ipc_skill('./skills/ipc-desktop')
print(message)

# 验证所有 IPC skills（需要遍历目录）
from pathlib import Path
import os

ipc_dir = Path('./skills/ipc')
for skill_dir in ipc_dir.iterdir():
    if skill_dir.is_dir() and skill_dir.name.startswith('ipc-'):
        valid, message = validate_ipc_skill(skill_dir)
        print(f"{skill_dir.name}: {message}")
```

## 命令行参数

| 参数                | 说明                    | 默认值                             |
| ----------------- | --------------------- | ------------------------------- |
| `--module`        | 指定模块 ID               | 所有模块                            |
| `--skills-root`   | clawbot skills 根目录    | 自动检测                            |
| `--output-dir`    | 输出目录（已废弃）             | `./skills`                      |
| `--host`          | IPC 服务主机（wsl 访问主机的ip） | `127.0.0.1 （如wsl，则是wsl访问主机的ip）` |
| `--port`          | IPC 服务端口              | `9527 （ftkclawbot设置的 访问主机的端口）`  |
| `--lang`          | 语言版本（zh/en）           | `zh`                            |
| `--force`         | 强制重新生成                | -                               |
| `--dry-run`       | 仅分析不生成                | -                               |
| `--verbose`       | 详细日志                  | -                               |
| `--generate-meta` | 生成 meta SKILL.md      | 启用                              |
| `--no-meta`       | 不生成 meta SKILL.md     | -                               |

## 智能触发词提取

触发词通过 `TriggerWordExtractor` 自动从 API 数据中提取，无需手动配置：

- 从 API action 名称分割关键词
- 从 description 提取中文关键词
- 从 description 提取英文关键词
- 自动过滤停用词

## 前置条件

- FTK\_Claw\_Bot IPC 服务运行中（端口 9527）
- Python 3.8+
- 输出目录有写入权限

## 错误处理

常见错误：

| 错误              | 原因        | 解决方法              |
| --------------- | --------- | ----------------- |
| ConnectionError | IPC 服务未启动 | 启动 FTK\_Claw\_Bot |
| TimeoutError    | 请求超时      | 增加 timeout 参数     |
| PermissionError | 无写入权限     | 检查目录权限            |

## 相关文件

| 文件                                | 说明                         |
| ----------------------------------- | --------------------------- |
| `scripts/ipc_client.py`             | IPC 客户端实现               |
| `scripts/ipc_skills_creator.py`     | Skills 生成脚本              |
| `scripts/init_ipc_skills.py`        | 项目初始化脚本               |
| `scripts/validate_ipc_skill.py`     | Skill 验证脚本              |
| `scripts/package_skill.py`          | Skill 打包脚本 (.skill zip) |
| `scripts/utils.py`                  | 工具函数                    |
| `scripts/eval_triggers.py`          | 触发词评估和优化脚本         |
| `scripts/run_eval.py`               | 评估测试运行脚本             |
| `scripts/eval_viewer.py`            | 评估报告查看器               |
| `scripts/aggregate_benchmark.py`    | 基准测试聚合脚本             |
| `assets/eval_viewer.html`           | 评估报告 HTML 模板          |
| `references/ipc_api_spec.md`        | API 规范详细文档            |
| `references/ipc_client_guide.md`    | 客户端使用指南              |
| `references/meta_skill_template.md` | Meta-skill 模板            |

## 脚本资源

### 触发词评估和优化

```bash
# 生成触发词评估集
python scripts/eval_triggers.py ./skills/ipc-desktop --mode generate

# 评估当前触发词效果
python scripts/eval_triggers.py ./skills/ipc-desktop --mode evaluate --eval-set evals/trigger_evals.json

# 优化触发词配置
python scripts/eval_triggers.py ./skills/ipc-desktop --mode optimize --eval-set evals/trigger_evals.json --max-iterations 5
```

### 运行评估测试

```bash
# 创建 evals/evals.json
{
  "skill_name": "ipc-desktop",
  "evals": [
    {
      "id": 1,
      "prompt": "点击屏幕位置 (100, 200)",
      "expected_output": "鼠标点击成功",
      "api_action": "desktop_mouse_click",
      "api_module": "desktop",
      "api_params": {"x": 100, "y": 200},
      "expectations": ["点击操作返回成功状态"]
    }
  ]
}

# 运行评估
python scripts/run_eval.py --skill-path ./skills/ipc-desktop --evals ./evals/evals.json

# 查看评估报告
python scripts/eval_viewer.py ./skills/ipc-desktop/evals/report.json --open
```

### 打包和分发

```bash
# 打包单个 skill 为 .skill 文件（zip 格式）
python scripts/package_skill.py ./skills/ipc-desktop

# 指定输出目录
python scripts/package_skill.py ./skills/ipc-desktop ./dist
```

### 基准测试聚合

```bash
# 聚合多个评估报告
python scripts/aggregate_benchmark.py ./skills/ipc-desktop/evals --skill-name ipc-desktop
```

## 快速参考

```python
# 初始化项目
from clawbot.skills.create_ipc_skills.scripts.init_ipc_skills import create_project
from pathlib import Path

create_project(Path('./my-ipc-skills'), include_examples=True)

# 生成所有 skills（默认到 clawbot/skills/ipc/）
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

creator = IPCCreateSkills()
result = creator.install_all_skills()

# 生成单个模块
creator = IPCCreateSkills()
result = creator.update_skill('desktop')

# 预览模式
creator = IPCCreateSkills()
result = creator.install_all_skills(dry_run=True)

# 验证生成的 skill
from clawbot.skills.create_ipc_skills.scripts.validate_ipc_skill import validate_ipc_skill

valid, message = validate_ipc_skill('./skills/ipc-desktop')
print(message)

# 打包 skill
from clawbot.skills.create_ipc_skills.scripts.package_skill import package_skill
from pathlib import Path

packaged = package_skill(Path('./skills/ipc-desktop'))
```

## 客户端使用示例

### Clawbot 内置客户端示例

```python
from clawbot.extra_serve.ipc.client import BridgeClient

async def example():
    # 创建并连接客户端
    client = BridgeClient()
    await client.connect()
    
    try:
        # 获取所有 API 规范
        result = await client.send_request('all_api_spec', {}, 'api_spec')
        print(f"API 总数: {result.get('total_apis')}")
        
        # 调用桌面模块 API
        result = await client.send_request('desktop_mouse_click', 
            {'x': 100, 'y': 200}, 'desktop')
        print(f"点击结果: {result}")
    finally:
        await client.disconnect()

import asyncio
asyncio.run(example())
```

### 外部 Agent 客户端脚本示例

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_client import IPCClient

# 方式一：使用上下文管理器（推荐）
with IPCClient() as client:
    # 获取所有 API 规范
    response = client.send('all_api_spec', {})
    result = response.get('payload', {}).get('result', {})
    print(f"API 总数: {result.get('total_apis')}")
    
    # 调用桌面模块 API
    response = client.send('desktop_mouse_click', {'x': 100, 'y': 200})
    result = response.get('payload', {}).get('result', {})
    print(f"点击结果: {result}")

# 方式二：手动管理连接
client = IPCClient(host='127.0.0.1', port=9527)
client.connect()
try:
    response = client.send('all_api_spec', {})
    result = response.get('payload', {}).get('result', {})
    print(f"结果: {result}")
finally:
    client.close()
```

