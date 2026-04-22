# Meta-Skill 模板规范

## 概述

本文档定义了 IPC skills 生成器创建的顶层 meta-skill 的标准格式。

## Frontmatter 结构

所有 meta-skill 必须包含以下 frontmatter 字段：

```yaml
---
name: <skill-name>
description: |
  <多行描述，包含触发场景>
  
  🔑 触发场景：
  - <场景1>
  - <场景2>
  - <场景3>

provides:
  - <能力1>
  - <能力2>

sub_skills:
  - <子skill1>
  - <子skill2>

metadata:
  clawbot:
    type: meta
    category: <分类>
    always: false
    priority: <优先级 0-100>
    generated_by: <生成器名称>
    generated_at: <生成时间>
---
```

## 字段说明

### 必需字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `name` | string | skill 名称（小写连字符） | `ipc` |
| `description` | string | 多行描述，包含触发场景 | 见下文 |
| `sub_skills` | list | 子 skill 名称列表 | `["ipc-desktop", "ipc-web"]` |
| `metadata` | object | 元数据对象 | 见下文 |

### description 格式

```yaml
description: |
  <一句话简介>
  
  🔑 触发场景：
  - <场景描述1>
  - <场景描述2>
  - <场景描述3>
```

### metadata.clawbot 结构

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 固定为 `meta` |
| `category` | string | 是 | 分类名称 |
| `always` | boolean | 是 | 是否始终加载 |
| `priority` | int | 是 | 优先级（0-100） |
| `generated_by` | string | 否 | 生成器标识 |
| `generated_at` | string | 否 | 生成时间（ISO 8601） |

## 正文结构

Meta-skill 的 markdown 正文应包含以下部分：

```markdown
# <Skill 标题>

## 概述

<简要介绍 meta-skill 的功能，包含模块数量和 API 总数>

## 脚本路径

- 客户端: `clawbot.extra_serve.ipc.client.BridgeClient`
- 同步客户端: `clawbot.skills.create_ipc_skills.scripts.ipc_client.IPCClient`

## 触发词索引

<列出各子 skill 的触发词>

## 子 Skills

### <分类1>
- **<子skill1>** - <描述>

### <分类2>
- **<子skill3>** - <描述>

## 使用流程

```
<流程图或说明>
```

## 使用场景

| 场景 | 使用子 Skill |
|------|-------------|
| <场景1> | <子skill> |

## 前置条件

- <条件1>
- <条件2>

## 使用说明

### 异步客户端（推荐）

```python
from clawbot.extra_serve.ipc.client import BridgeClient

async def main():
    client = BridgeClient()
    await client.connect()
    result = await client.send_request('<api_name>', {}, '<module>')
    await client.disconnect()

import asyncio
asyncio.run(main())
```

### 同步客户端

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send('all_api_spec', {})
    result = response.get('payload', {}).get('result', {})
```

## 相关技能

- **@<相关skill>** - <说明>
```

## 示例

完整的 meta-skill 示例：

```yaml
---
name: ipc
description: |
  IPC 自动化技能集，提供桌面、网页、OCR、微信等系统自动化能力。

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
    generated_by: ipc-create-skills
    generated_at: 2024-01-01T00:00:00
    api_version: 2.1.0
---

# IPC Skills | 系统自动化

## 概述

IPC (Inter-Process Communication) 自动化技能集，包含 3 个子模块，共 67 个API。

## 脚本路径

- 客户端: `clawbot.extra_serve.ipc.client.BridgeClient`
- 同步客户端: `clawbot.skills.create_ipc_skills.scripts.ipc_client.IPCClient`

## 触发词索引

- **ipc-desktop**: 鼠标, 点击, 移动, 拖拽, 滚动, 键盘, 输入, 截图
- **ipc-web**: 浏览器, 导航, 点击, 填充, 等待
- **ipc-ocr**: 文字识别, OCR, 截图识别

## 子 Skills

### 桌面自动化
- **ipc-desktop** - 鼠标、键盘、窗口操作 (27 APIs)

### 网页自动化
- **ipc-web** - 浏览器控制 (37 APIs)

### OCR 识别
- **ipc-ocr** - 文字识别 (3 APIs)

## 使用流程

```
用户需求 → ipc (自动路由) → 对应子 skill → IPC API 调用
```

## 使用场景

| 场景 | 使用子 Skill |
|------|-------------|
| 自动化桌面操作 | ipc-desktop |
| 控制浏览器 | ipc-web |
| 文字识别 | ipc-ocr |

## 前置条件

- FTK_Claw_Bot IPC 服务运行中（端口 9527）
- 相关模块已注册到 IPC 服务

## 使用说明

### 异步客户端（推荐）

```python
from clawbot.extra_serve.ipc.client import BridgeClient

async def main():
    client = BridgeClient()
    await client.connect()
    
    # 调用桌面截图 API
    result = await client.send_request(
        'desktop_screenshot',
        {},
        'desktop'
    )
    
    await client.disconnect()

import asyncio
asyncio.run(main())
```

### 同步客户端

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send('all_api_spec', {})
    result = response.get('payload', {}).get('result', {})
    print(f"总 API 数量: {result.get('total_apis')}")
```

## 相关技能

- **@create_ipc_skills** - 生成和更新 IPC skills
```

## 验证规则

Meta-skill 必须通过以下验证：

1. `name` 为小写连字符格式
2. `description` 非空且包含触发场景
3. `sub_skills` 为非空列表
4. `provides` 为非空列表
5. `metadata.clawbot.type` 为 "meta"
6. `metadata.clawbot.priority` 在 0-100 范围内
7. 正文包含 "## 子 Skills" 部分
8. 所有引用的子 skill 目录存在

## 生成器实现

生成器应：

1. 从 API spec 提取模块列表
2. 为每个模块生成子 skill 文件
3. 生成顶层 meta SKILL.md
4. 创建 `.skill_id` 文件
5. 运行验证脚本
