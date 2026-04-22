# IPC Skills 创建方案

## 基于 `create_ipc_skills` 工具链的自动化技能生成方案

---

## 1. 背景与目标

### 1.1 现状分析

当前 IPC 技能集成存在两套并行方案：

| 方案 | 位置 | 机制 | 状态 |
|------|------|------|------|
| **方案A - 动态集成** | `extra_serve/ipc/` | 运行时动态创建Tool，通过 `IPCDynamicToolFactory` 从 `IPCServiceRegistry` 获取API规范并动态生成Tool实例 | 已实现，但增加了服务层复杂度 |
| **方案B - 静态生成** | `skills/create_ipc_skills/` | 通过独立工具链从 `all_api_spec` 离线生成标准化 SKILL.md 文件，由 Skill Loader 发现加载 | 已实现工具链，但未完全启用 |

### 1.2 目标

**采用方案B**，完全依赖 `skills/create_ipc_skills/` 工具链创建 IPC skills，将其作为 Clawbot 的标准技能文件，通过现有的 Skill 发现和加载机制（`SkillsLoader`）自动加载，无需额外的服务层集成。

### 1.3 核心优势

- **架构简洁**：SKILL.md 文件作为一等公民，由 `SkillsLoader` 统一发现和加载
- **运行时零开销**：无需维护 `IPCServiceRegistry`、`IPCDynamicToolFactory` 等运行时组件
- **标准合规**：生成的技能文件符合通用 Skills 规范，支持热重载
- **离线可用**：技能描述文件离线可读，不依赖 IPC 服务在线

---

## 2. 现有工具链分析

### 2.1 工具链组件

`skills/create_ipc_skills/` 目录已具备完整的工具链：

```
skills/create_ipc_skills/
├── SKILL.md                          # Meta-skill（自身也是一个skill）
├── scripts/
│   ├── ipc_skills_creator.py         # 核心：IPC Skills 自动创建/更新工具
│   ├── ipc_client.py                 # IPC 服务 TCP 客户端
│   ├── init_ipc_skills.py            # 项目初始化器
│   ├── package_skill.py              # 技能打包工具
│   ├── validate_ipc_skill.py         # 技能文件验证器
│   └── utils.py                      # 工具函数
└── references/
    ├── ipc_api_spec.md               # API 规范文档
    ├── ipc_client_guide.md           # 客户端使用指南
    └── meta_skill_template.md        # Meta-skill 模板
```

### 2.2 核心类分析

#### `IPCCreateSkills`（[ipc_skills_creator.py](file:///d:/bot_workspace/FTK_bot/clawbot/clawbot/skills/create_ipc_skills/scripts/ipc_skills_creator.py#L745-L1027)）

主控制器，负责完整的技能创建流程：

```python
creator = IPCCreateSkills(
    skills_root='/path/to/clawbot/skills',  # 自动检测
    host='127.0.0.1',
    port=9527,
    lang='zh',
    generate_meta=True
)

# 批量安装所有 skills
result = creator.install_all_skills(force=False, dry_run=False)

# 更新单个模块
result = creator.update_skill('desktop')
```

#### `ApiSpecParser`（[ipc_skills_creator.py](file:///d:/bot_workspace/FTK_bot/clawbot/clawbot/skills/create_ipc_skills/scripts/ipc_skills_creator.py#L229-L283)）

解析 `all_api_spec` 返回的 API 规范数据。

#### `SkillContentGenerator`（[ipc_skills_creator.py](file:///d:/bot_workspace/FTK_bot/clawbot/clawbot/skills/create_ipc_skills/scripts/ipc_skills_creator.py#L285-L469)）

生成标准化的 SKILL.md 内容，包含：
- YAML Frontmatter（name, description）
- 模块信息表格
- 触发词（智能提取）
- API 列表（每个API独立章节）
- 使用示例（BridgeClient + IPCClient）

#### `MetaSkillGenerator`（[ipc_skills_creator.py](file:///d:/bot_workspace/FTK_bot/clawbot/clawbot/skills/create_ipc_skills/scripts/ipc_skills_creator.py#L471-L743)）

生成顶层 meta SKILL.md，包含：
- 子 Skill 路径索引
- 触发词索引
- 使用场景映射
- 客户端示例

#### `TriggerWordExtractor`（[ipc_skills_creator.py](file:///d:/bot_workspace/FTK_bot/clawbot/clawbot/skills/create_ipc_skills/scripts/ipc_skills_creator.py#L178-L227)）

智能触发词提取：
- 从 API action 名称分割关键词
- 从 description 提取中文/英文关键词
- 自动过滤停用词

### 2.3 对比 `extra_serve/ipc/skill_generator.py`

| 维度 | `IPCSkillGenerator` | `IPCCreateSkills` |
|------|---------------------|-------------------|
| **位置** | `extra_serve/ipc/` | `skills/create_ipc_skills/` |
| **职责** | 简单生成 SKILL.md 文件 | 完整的技能创建工具链 |
| **功能** | 仅生成主技能和模块技能 | 包含解析、生成、验证、打包全流程 |
| **触发词** | 不支持 | 智能提取 |
| **验证** | 无 | 内置验证器 |
| **Meta SKILL.md** | 简单版本 | 完整标准格式（路径索引、触发词索引等） |
| **使用方式** | 需要集成到服务 | 独立运行，CLI 工具 |

**结论**：`IPCSkillGenerator` 功能薄弱，`IPCCreateSkills` 工具链更完整、更成熟，应作为唯一方案。

---

## 3. 方案设计

### 3.1 架构设计

```
┌──────────────────────────────────────────────────────────────┐
│                     FTK_Claw_Bot IPC 服务                      │
│                        (Windows 主机, 端口 9527)               │
│                        提供 all_api_spec API                   │
└──────────────────────┬───────────────────────────────────────┘
                       │ TCP Socket
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              skills/create_ipc_skills/ 工具链                  │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ IPCClient   │→ │ ApiSpecParser│→ │ SkillContentGen    │   │
│  │ (TCP连接)    │  │ (解析API规范) │  │ (生成SKILL.md内容)  │   │
│  └─────────────┘  └──────────────┘  └────────────────────┘   │
│                                                    │          │
│                                          ┌─────────▼────────┐ │
│                                          │ MetaSkillGen     │ │
│                                          │ (生成顶层索引)    │ │
│                                          └─────────┬────────┘ │
│                                                    │          │
│                                          ┌─────────▼────────┐ │
│                                          │ ValidateIPC      │ │
│                                          │ (验证技能文件)    │ │
│                                          └──────────────────┘ │
└──────────────────────┬───────────────────────────────────────┘
                       │ 生成 SKILL.md 文件
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              clawbot/skills/ipc/  技能目录                     │
│                                                              │
│  ipc/                                                      │
│  ├── SKILL.md              ← Meta SKILL（索引文件）           │
│  ├── .skill_id             ← "ipc"                           │
│  ├── ipc-desktop/          ← 桌面自动化子技能                 │
│  │   ├── SKILL.md                                           │
│  │   └── .skill_id                                          │
│  ├── ipc-web/                                             │
│  │   ├── SKILL.md                                           │
│  │   └── .skill_id                                          │
│  └── ...                                                    │
└──────────────────────┬───────────────────────────────────────┘
                       │ SkillsLoader 自动发现
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                     Clawbot Skill Engine                      │
│                                                              │
│  SkillsLoader → 扫描 skills/ 目录 → 解析 SKILL.md → 注册技能   │
│  MasterAgent → 根据用户意图匹配技能 → 注入上下文 → 执行         │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 技能生成流程

```
用户/定时触发
    │
    ▼
┌─────────────────────┐
│ 1. 连接 IPC 服务     │  IPCClient(host, port)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. 获取 all_api_spec │  client.send("all_api_spec", {})
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. 解析 API 规范     │  ApiSpecParser.parse_all()
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. 为每个模块生成     │  SkillContentGenerator.generate()
│    SKILL.md 文件     │  TriggerWordExtractor.extract()
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. 生成 Meta SKILL   │  MetaSkillGenerator.generate()
│    顶层索引文件       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. 验证生成结果      │  validate_ipc_skill()
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 7. SkillsLoader      │  下次技能加载时自动发现
│    自动发现新技能     │
└─────────────────────┘
```

### 3.3 生成的技能文件结构

```
clawbot/skills/ipc/
│
├── SKILL.md                          # 顶层 meta skill
│   ├── name: "ipc"
│   ├── description: "IPC 自动化技能集..."
│   ├── provides: [desktop, web, ocr, ...]
│   ├── sub_skills: [ipc-desktop, ipc-web, ...]
│   ├── metadata.clawbot.type: "meta"
│   ├── metadata.clawbot.priority: 85
│   └── 正文：概述、脚本路径、子Skill路径索引、触发词索引...
│
├── .skill_id                         # 内容: "ipc"
│
├── ipc-desktop/                      # 桌面自动化子技能
│   ├── SKILL.md
│   │   ├── name: "ipc-desktop"
│   │   ├── description: "桌面自动化。27个IPC API。"
│   │   └── 正文：模块信息、触发词、API列表、示例
│   └── .skill_id                     # 内容: "ipc-desktop"
│
├── ipc-web/                          # 网页自动化子技能
│   ├── SKILL.md
│   └── .skill_id
│
└── ...                               # 其他模块
```

### 3.4 技能文件内容规范

#### 子技能 SKILL.md 格式

```markdown
---
name: "ipc-desktop"
description: "桌面自动化。27个IPC API。"
---

# IPC Desktop

## 模块信息

| 属性 | 值 |
|------|-----|
| 模块ID | desktop |
| 名称 | 桌面自动化 |
| 版本 | 1.0.0 |
| API数 | 27 |

## 触发词

- 中文: 鼠标, 点击, 键盘, 输入, 截图, 窗口
- 英文: mouse, click, keyboard, type, screenshot, window

## API列表

### desktop_mouse_click

描述: 鼠标点击指定坐标
指令: `desktop_mouse_click`
触发词: 鼠标, 点击, mouse, click

输入:
  - `x` (int): 必填
  - `y` (int): 必填
  - `button` (str): 可选, 默认=left

输出:
  - `success` (bool)

## 示例

### Clawbot 内置客户端（推荐）

```python
from clawbot.extra_serve.ipc.client import BridgeClient

async def main():
    client = BridgeClient()
    await client.connect()
    result = await client.send_request('desktop_mouse_click', {'x': 100, 'y': 200}, 'desktop')
    await client.disconnect()

import asyncio
asyncio.run(main())
```
```

---

## 4. 实施方案

### 4.1 阶段一：清理与优化

#### 4.1.1 标记废弃 `extra_serve/ipc/skill_generator.py`

不需要删除，但应标记为废弃，在新方案稳定后再移除。

需要废弃的组件：
- [ ] `extra_serve/ipc/skill_generator.py` - IPCSkillGenerator 类
- [ ] `extra_serve/ipc/tool_factory.py` - IPCDynamicToolFactory 类（如果不再需要动态创建Tool）

需要保留的组件（仍然有用）：
- `extra_serve/ipc/client.py` - BridgeClient（技能示例代码使用）
- `extra_serve/ipc/registry.py` - IPCServiceRegistry（可选，用于运行时API查询）
- `extra_serve/ipc/models.py` - 数据模型

#### 4.1.2 优化工具链

需要优化的点：

1. **路径检测增强**
   - 当前 `detect_skills_root()` 向上查找 `clawbot/skills` 目录
   - 需要支持 WSL 环境下的路径映射
   - 增加配置化路径支持

2. **增量更新优化**
   - 添加文件 hash 对比，跳过未变更的模块
   - 支持部分更新（仅更新指定模块的 SKILL.md）

3. **验证增强**
   - 完善 `validate_ipc_skill.py` 的验证规则
   - 添加 YAML frontmatter 格式严格验证

### 4.2 阶段二：集成到启动流程

#### 4.2.1 启动时自动同步

在 Clawbot 启动时（`clawbot gateway`），自动执行技能同步：

```python
# 伪代码：在 gateway 启动流程中
async def sync_ipc_skills_on_startup():
    """启动时同步 IPC skills"""
    try:
        from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills
        
        creator = IPCCreateSkills()
        result = creator.install_all_skills(force=False)
        
        if result.status.value == "success":
            logger.info(f"IPC skills 同步完成: {len(result.skills_created)} 个技能")
        elif result.status.value == "skipped":
            logger.info("IPC skills 已是最新，无需更新")
    except Exception as e:
        logger.warning(f"IPC skills 同步失败: {e}")
```

#### 4.2.2 定时同步任务

通过 `CronService` 配置定时任务，定期同步技能：

```python
# 每 30 分钟同步一次
cron.schedule("*/30 * * * *", sync_ipc_skills)
```

#### 4.2.3 手动触发

用户可以通过对话触发技能同步：

```
用户: "更新 IPC 技能"
Bot: 触发 create_ipc_skills meta-skill，执行同步
```

### 4.3 阶段三：验证与测试

#### 4.3.1 单元测试

```python
# tests/unit/skills/test_ipc_skills_creator.py

async def test_fetch_api_specs():
    """测试 API 规范获取"""
    pass

async def test_parse_api_specs():
    """测试 API 规范解析"""
    pass

async def test_generate_skill_content():
    """测试技能内容生成"""
    pass

async def test_validate_generated_skills():
    """测试生成的技能文件验证"""
    pass
```

#### 4.3.2 集成测试

```python
# tests/integration/test_ipc_skills_integration.py

async def test_full_skill_generation_cycle():
    """测试完整的技能生成周期"""
    pass

async def test_skill_loading_after_generation():
    """测试生成后技能加载"""
    pass
```

#### 4.3.3 验证清单

| 验证项 | 方法 | 预期结果 |
|--------|------|----------|
| SKILL.md 文件结构 | `validate_ipc_skill.py` | 全部通过 |
| YAML frontmatter 格式 | 解析验证 | 符合规范 |
| 触发词提取 | 人工审核 | 准确、无重复 |
| API 列表完整性 | 对比 all_api_spec | 100% 覆盖 |
| 示例代码可执行性 | 实际运行 | 无错误 |
| SkillsLoader 发现 | 启动日志 | 自动发现所有技能 |

---

## 5. 使用方式

### 5.1 CLI 使用

```bash
# 生成所有 IPC skills（默认到 clawbot/skills/ipc/）
python skills/create_ipc_skills/scripts/ipc_skills_creator.py

# 指定 skills 根目录
python skills/create_ipc_skills/scripts/ipc_skills_creator.py --skills-root /path/to/clawbot/skills

# 预览模式（不生成文件）
python skills/create_ipc_skills/scripts/ipc_skills_creator.py --dry-run

# 更新单个模块
python skills/create_ipc_skills/scripts/ipc_skills_creator.py --module desktop

# 强制重新生成
python skills/create_ipc_skills/scripts/ipc_skills_creator.py --force

# 详细日志
python skills/create_ipc_skills/scripts/ipc_skills_creator.py --verbose
```

### 5.2 Python API 使用

```python
from clawbot.skills.create_ipc_skills.scripts.ipc_skills_creator import IPCCreateSkills

# 创建生成器
creator = IPCCreateSkills(
    skills_root='/path/to/clawbot/skills',
    host='127.0.0.1',
    port=9527,
    lang='zh',
    generate_meta=True
)

# 生成所有 skills
result = creator.install_all_skills(force=False, dry_run=False)
print(f"状态: {result.status.value}")
print(f"创建文件: {len(result.skills_created)}")

# 更新单个模块
result = creator.update_skill('desktop')
```

### 5.3 通过 Meta-Skill 触发

`skills/create_ipc_skills/SKILL.md` 本身就是一个 meta-skill，可以通过对话触发：

```
用户: "帮我更新 IPC 技能"
Bot: 触发 @create_ipc_skills，执行安装流程
```

---

## 6. 与现有系统的集成点

### 6.1 SkillsLoader 集成

`SkillsLoader`（[skill_loader.py](file:///d:/bot_workspace/FTK_bot/clawbot/clawbot/agent/skill_loader.py)）会自动扫描以下目录：
- 工作区技能目录
- 内置技能目录（`clawbot/skills/`）
- OpenSpace 同步技能目录

生成的 IPC skills 位于 `clawbot/skills/ipc/`，会被 `SkillsLoader` 自动发现和加载，**无需额外集成代码**。

### 6.2 Hot Reload 集成

`skills/hot_reload/` 模块会监控技能文件变更：
- 当 IPC skills 更新时，热重载机制会自动检测并重新加载
- 无需重启 Clawbot

### 6.3 Skill Engine 集成

`openspace/skill_engine/registry.py` 中的 `SkillRegistry` 会：
- 发现并注册所有技能
- 支持通过 LLM 匹配用户意图和技能
- 注入技能上下文到对话

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| IPC 服务未启动 | 无法获取 API 规范 | 降级使用缓存，启动时重试 |
| API 规范变更 | 技能文件过时 | 定时同步任务自动更新 |
| 技能文件过大 | 上下文注入过多 | 按需加载子技能，设置大小限制 |
| WSL 路径问题 | 文件写入失败 | 增强路径检测，支持配置化 |

---

## 8. 总结

### 8.1 方案对比

| 维度 | 方案A（动态集成） | 方案B（静态生成） |
|------|-------------------|-------------------|
| **架构复杂度** | 高（需要服务层组件） | 低（标准技能文件） |
| **运行时开销** | 高（维护注册中心、工厂） | 零（文件静态加载） |
| **可维护性** | 低（耦合严重） | 高（独立工具链） |
| **离线可用性** | 否 | 是 |
| **工具成熟度** | 基础功能 | 完整工具链 |
| **标准合规** | 非标准 | 符合通用 Skills 规范 |

### 8.2 推荐方案

**采用方案B**，完全依赖 `skills/create_ipc_skills/` 工具链：

1. 使用 `IPCCreateSkills` 生成标准化 SKILL.md 文件
2. 生成的文件放置到 `clawbot/skills/ipc/` 目录
3. 由 `SkillsLoader` 自动发现和加载
4. 通过 `CronService` 定时同步，保持技能最新

### 8.3 后续行动

- [ ] 执行 `python skills/create_ipc_skills/scripts/ipc_skills_creator.py --dry-run` 验证工具链
- [ ] 在 WSL 环境下测试完整生成流程
- [ ] 添加启动时自动同步逻辑
- [ ] 配置定时同步任务
- [ ] 废弃 `extra_serve/ipc/skill_generator.py`（标记 deprecated）
- [ ] 编写集成测试
- [ ] 更新文档
