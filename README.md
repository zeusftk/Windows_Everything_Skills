# Windows Everything Skills

IPC 自动化技能集，为 AI Agent 提供 Windows 系统控制能力。

## 功能

- **桌面自动化**：鼠标、键盘、窗口、文件、PowerShell、虚拟桌面、多显示器
- **浏览器控制**：网页导航、元素交互、标签页管理、任务队列
- **微信集成**：消息发送、会话管理
- **OCR 识别**：文字识别、屏幕文本点击
- **CLI 适配器**：命令行工具集成
- **向量嵌入**：语义搜索、相似度计算

## 安装流程

1. 运行 FTK\_Claw\_Bot
2. 将 `create_ipc_skills` 添加到支持 skill 的 agent 或 coding 应用的 skills 文件夹下，如 OpenClaw、OpenCode、Hermes、Trea 等
3. 输入 "使用 create\_ipc\_skills 安装 ipc 技能"
4. 等待完成

## 使用方法

### Agent 对话方式

```
使用 create_ipc_skills 安装 ipc 技能
```

安装后即可通过自然语言调用 IPC API：

- "点击屏幕中央"
- "打开 Chrome 浏览器"
- "发送微信消息给张三"
- "识别截图中的文字"


## 项目结构

```
create_ipc_skills/
├── scripts/           # 核心脚本
│   ├── ipc_skills_creator.py   # SKILL.md 生成器
│   ├── ipc_client.py          # IPC 客户端
│   └── ...
├── references/        # 参考文档
└── assets/            # 评估可视化模板
```

## 前置条件

- FTK\_Claw\_Bot IPC 服务运行中（端口 9527）
- Python 3.8+

