# -*- coding: utf-8 -*-
"""
IPC Client - IPC 服务连接客户端

提供与 FTK_Claw_Bot IPC 服务通信的客户端实现，支持：
- TCP Socket 连接
- 消息发送和接收
- 自动身份识别
- 上下文管理器支持

使用方法:
    from ipc_client import IPCClient

    with IPCClient() as client:
        response = client.send("all_api_spec", {})
        print(response)

作者: Clawbot Team
版本: 1.0.0
"""

import json
import socket
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
        if b"\n" in chunk:
            break
    return json.loads(data.decode("utf-8").strip())


def send_request(
    sock: socket.socket,
    action: str,
    params: dict,
    timeout: int = 120,
    skip_identify: bool = False,
    client_name: str = "ipc_client"
) -> dict:
    sock.settimeout(timeout)

    if not skip_identify:
        try:
            initial_response = receive_message(sock)
            if (
                initial_response.get("type") == "request"
                and initial_response.get("payload", {}).get("action") == "request_identify"
            ):
                identify_msg = create_message("identify", {
                    "client_name": client_name,
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
    def __init__(self, host: str = "127.0.0.1", port: int = 9527, client_name: str = "ipc_client"):
        """
        初始化 IPC 客户端

        Args:
            host: IPC 服务主机地址
            port: IPC 服务端口
            client_name: 客户端标识名称
        """
        self.host = host
        self.port = port
        self.client_name = client_name
        self.sock = None
        self._identified = False

    def connect(self):
        """建立与 IPC 服务的连接"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(120)
        self.sock.connect((self.host, self.port))

    def close(self):
        """关闭与 IPC 服务的连接"""
        if self.sock:
            self.sock.close()
            self.sock = None
            self._identified = False

    def send(self, action: str, params: dict = None, timeout: int = 120) -> dict:
        """
        发送请求到 IPC 服务

        Args:
            action: 动作名称
            params: 请求参数
            timeout: 超时时间（秒）

        Returns:
            dict: 响应数据
        """
        if not self.sock:
            raise ConnectionError("未连接到 IPC 服务")

        skip_identify = self._identified
        result = send_request(
            self.sock,
            action,
            params or {},
            timeout,
            skip_identify,
            self.client_name
        )
        self._identified = True
        return result

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
