# IPC Client 使用指南

## 概述

`ipc_client.py` 提供与 FTK_Claw_Bot IPC 服务通信的 TCP 客户端实现。

## 基本用法

### 使用上下文管理器（推荐）

```python
from scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send("all_api_spec", {})
    print(response)
```

### 手动管理连接

```python
from scripts.ipc_client import IPCClient

client = IPCClient(host="127.0.0.1", port=9527)

try:
    client.connect()
    response = client.send("ping", {})
    print(response)
finally:
    client.close()
```

## API 参考

### IPCClient 类

#### 构造函数

```python
IPCClient(host="127.0.0.1", port=9527, client_name="ipc_client")
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| host | string | "127.0.0.1" | IPC 服务主机地址 |
| port | int | 9527 | IPC 服务端口 |
| client_name | string | "ipc_client" | 客户端标识名称 |

#### 方法

##### connect()

建立与 IPC 服务的连接。

##### close()

关闭与 IPC 服务的连接。

##### send(action, params=None, timeout=120)

发送请求到 IPC 服务。

| 参数 | 类型 | 说明 |
|------|------|------|
| action | string | 动作名称 |
| params | dict | 请求参数 |
| timeout | int | 超时时间（秒） |

**返回值**: dict - 响应数据

## 连接信息

| 参数 | 值 |
|------|-----|
| 协议 | TCP Socket |
| 默认主机 | 127.0.0.1 |
| 默认端口 | 9527 |
| 编码 | UTF-8 |
| 超时 | 120 秒 |

## WSL 环境配置

在 WSL 中运行时，需要使用 Windows 主机 IP：

```python
import os

# 方法1: 环境变量
host = os.environ.get('FTK_IPC_HOST', '172.18.0.1')

# 方法2: 从 resolv.conf 获取
def get_wsl_ip():
    try:
        with open('/etc/resolv.conf') as f:
            for line in f:
                if line.startswith('nameserver'):
                    return line.split()[-1]
    except:
        pass
    return '172.18.0.1'

with IPCClient(host=get_wsl_ip()) as client:
    ...
```

## 消息格式

### 请求消息

```json
{
  "version": "1.0",
  "type": "request",
  "id": "UUID",
  "timestamp": "ISO8601",
  "payload": {
    "action": "动作名称",
    "params": {}
  }
}
```

### 响应消息

```json
{
  "version": "1.0",
  "type": "response",
  "id": "UUID",
  "timestamp": "ISO8601",
  "payload": {
    "result": {
      "success": true,
      ...
    }
  }
}
```

## 错误处理

### 常见错误

| 错误类型 | 原因 | 解决方法 |
|----------|------|----------|
| ConnectionError | 服务未启动 | 启动 IPC 服务 |
| socket.timeout | 请求超时 | 增加 timeout 参数 |
| ConnectionRefusedError | 端口未开放 | 检查防火墙 |
| ConnectionError("连接已关闭") | 连接断开 | 重新连接 |

### 错误处理示例

```python
from scripts.ipc_client import IPCClient
import socket

try:
    with IPCClient() as client:
        response = client.send("all_api_spec", {})
        result = response.get("payload", {}).get("result", {})
        
        if result.get("success"):
            print("成功")
        else:
            print(f"API 错误: {result.get('error')}")
            
except socket.timeout:
    print("连接超时")
except ConnectionRefusedError:
    print("连接被拒绝")
except Exception as e:
    print(f"未知错误: {e}")
```

## 身份识别

客户端连接时会自动进行身份识别：

```python
identify_msg = {
    "client_name": "ipc_client",
    "workspace": ""
}
```

## 使用示例

### 示例 1: 获取 API 规范

```python
from scripts.ipc_client import IPCClient

def get_api_specs(module=None):
    with IPCClient() as client:
        params = {}
        if module:
            params["module"] = module
        
        response = client.send("all_api_spec", params)
        return response.get("payload", {}).get("result", {})

specs = get_api_specs("desktop")
print(f"总 API: {specs['total_apis']}")
```

### 示例 2: 列出所有模块

```python
from scripts.ipc_client import IPCClient

with IPCClient() as client:
    response = client.send("all_api_spec", {})
    result = response.get("payload", {}).get("result", {})
    
    for module_id, module_data in result.get("actions", {}).items():
        api_count = len(module_data.get("apis", []))
        print(f"{module_id}: {api_count} APIs")
```

### 示例 3: 搜索 API

```python
from scripts.ipc_client import IPCClient

def search_api(keyword):
    with IPCClient() as client:
        response = client.send("all_api_spec", {"action_filter": keyword})
        result = response.get("payload", {}).get("result", {})
        
        if result.get("success"):
            for module_id, module_data in result.get("actions", {}).items():
                for api in module_data.get("apis", []):
                    print(f"[{module_id}] {api['action']}: {api['description']}")

search_api("mouse")
```
