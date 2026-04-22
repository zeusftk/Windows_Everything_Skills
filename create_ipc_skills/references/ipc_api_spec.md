# IPC API 规范参考文档

## 概述

FTK_Claw_Bot IPC 服务提供 `all_api_spec` API，返回所有已注册模块的完整 API 规范。

## 调用方式

```python
from scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send("all_api_spec", {})
```

## 响应数据结构

### 顶层结构

```json
{
  "success": true,
  "actions": {
    "<module_id>": {
      "id": "模块ID",
      "name": "模块名称",
      "version": "版本号",
      "apis": [...]
    }
  },
  "total_apis": 总数,
  "generated_at": "生成时间"
}
```

### 模块结构

每个模块包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 模块唯一标识 |
| name | string | 模块显示名称 |
| version | string | 模块版本 |
| apis | array | API 列表 |

### API 结构

每个 API 包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| action | string | API 动作名称 |
| api_type | string | API 类型 |
| description | string | API 描述 |
| input_args | object | 输入参数定义 |
| out_args | object | 输出参数定义 |
| test_status | string | 测试状态 |
| supports_submit | boolean | 是否支持 submit |

### 参数结构

每个参数定义包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 参数类型 |
| description | string | 参数描述 |
| required | boolean | 是否必填 |
| default | any | 默认值 |
| enum | array | 枚举值列表 |

## 过滤参数

`all_api_spec` API 支持以下过滤参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| module | string | 按模块过滤 |
| action_filter | string | 按 action 关键词过滤 |

## 示例

### 获取所有 API

```python
response = client.send("all_api_spec", {})
```

### 获取特定模块

```python
response = client.send("all_api_spec", {"module": "desktop"})
```

### 搜索 API

```python
response = client.send("all_api_spec", {"action_filter": "mouse"})
```
