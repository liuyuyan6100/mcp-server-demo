"""
测试 MCP server 的脚本

用法：
  python test_server.py              # 测试 FastMCP 版本
  python test_server.py raw          # 测试原生 SDK 版本
"""

import subprocess
import sys
import json


def test_server(script: str):
    """启动 server，发送 MCP 请求，验证响应"""

    print(f"🧪 测试 MCP server: {script}")
    print("=" * 50)

    # MCP 协议的初始化请求
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    }

    # 列出工具的请求
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }

    # 调用工具的请求（根据 script 选择不同的工具）
    if "fastmcp" in script:
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {"expression": "2 + 3 * 4"},
            },
        }
    else:
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {"a": 17, "b": 25},
            },
        }

    # 将请求转换为 JSON 行（每行一个 JSON 对象）
    requests = [init_request, list_tools_request, call_request]
    input_data = "\n".join(json.dumps(r) for r in requests)

    # 启动 server 进程
    proc = subprocess.Popen(
        ["python3", script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = proc.communicate(input=input_data, timeout=10)

    print("📨 Server 回复:")
    for line in stdout.strip().split("\n"):
        if line.strip():
            try:
                data = json.loads(line)
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"  (非 JSON): {line[:200]}")

    if stderr.strip():
        print(f"\n⚠️ stderr 输出:\n{stderr[:500]}")

    print(f"\n✅ 测试完成，退出码: {proc.returncode}")


if __name__ == "__main__":
    target = "server_fastmcp.py" if len(sys.argv) < 2 else "server_raw.py"
    test_server(target)
