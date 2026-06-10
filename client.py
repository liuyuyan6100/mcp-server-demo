"""
MCP 客户端示例 —— 调用远程 MCP Server

两种方式：
  python client.py           # 用 MCP SDK 客户端（推荐，封装了协议细节）
  python client.py --raw     # 用原始 HTTP 请求（学习协议用）

依赖：同 server，都是 mcp 包
"""

import asyncio
import json
import sys

# ============================================================
# 方式一：MCP SDK 客户端（推荐）
# SDK 封装了 initialize、session 管理、SSE 解析等细节
# ============================================================

async def call_with_sdk():
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.client.session import ClientSession

    url = "http://127.0.0.1:8765/mcp"
    print(f"[SDK] 连接 MCP Server: {url}")
    print("=" * 50)

    # streamablehttp_client 是异步上下文管理器
    # 它返回 (读流, 写流, get_session_id) 三元组
    async with streamablehttp_client(url) as (read_stream, write_stream, _):
        # 用读写流创建 ClientSession
        async with ClientSession(read_stream, write_stream) as session:
            # ---- 第一步：initialize（自动完成）----
            await session.initialize()
            print(f"[1] 初始化完成")
            print(f"    Server 能力: {session.get_server_capabilities()}")

            # ---- 第二步：列出工具 ----
            tools_result = await session.list_tools()
            print(f"\n[2] 可用工具 ({len(tools_result.tools)} 个):")
            for tool in tools_result.tools:
                print(f"    - {tool.name}: {tool.description.strip()[:40]}...")

            # ---- 第三步：调用 calculate ----
            print(f"\n[3] 调用 calculate('2 + 3 * 4'):")
            result = await session.call_tool("calculate", {"expression": "2 + 3 * 4"})
            for content in result.content:
                print(f"    结果: {content.text}")

            # ---- 第四步：调用 get_weather ----
            print(f"\n[4] 调用 get_weather('上海'):")
            result = await session.call_tool("get_weather", {"city": "上海"})
            for content in result.content:
                print(f"    结果:\n    " + content.text.replace("\n", "\n    "))


# ============================================================
# 方式二：原始 HTTP 请求（学习协议用）
# 手动处理 initialize、session ID、SSE 格式
# ============================================================

async def call_with_raw_http():
    import httpx

    base_url = "http://127.0.0.1:8765/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Origin": "http://localhost:8765",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        # ---- 第一步：initialize ----
        print(f"[Raw HTTP] 连接 MCP Server: {base_url}")
        print("=" * 50)

        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "python-raw-client", "version": "1.0"},
            },
        }

        resp = await client.post(base_url, json=init_req, headers=headers)
        session_id = resp.headers.get("mcp-session-id")
        print(f"[1] initialize 响应:")
        print(f"    Session ID: {session_id}")

        # 解析 SSE 格式的响应体
        body = resp.text
        for line in body.split("\n"):
            if line.startswith("data: "):
                data = json.loads(line[6:])
                print(f"    Server: {data['result']['serverInfo']}")

        # 后续请求都要带 session ID
        headers["mcp-session-id"] = session_id

        # ---- 第二步：notifications/initialized ----
        notify_req = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        await client.post(base_url, json=notify_req, headers=headers)
        print(f"\n[2] 已发送 initialized 通知")

        # ---- 第三步：tools/list ----
        list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = await client.post(base_url, json=list_req, headers=headers)
        tools_data = parse_sse(resp.text)
        tools = tools_data["result"]["tools"]
        print(f"\n[3] 可用工具 ({len(tools)} 个):")
        for t in tools:
            print(f"    - {t['name']}: {t['description'].strip()[:40]}...")

        # ---- 第四步：tools/call ----
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {"expression": "sqrt(144) + 10"},
            },
        }
        resp = await client.post(base_url, json=call_req, headers=headers)
        call_data = parse_sse(resp.text)
        print(f"\n[4] 调用 calculate('sqrt(144) + 10'):")
        print(f"    结果: {call_data['result']['content'][0]['text']}")


def parse_sse(text: str) -> dict:
    """从 SSE 格式的响应中提取 JSON 数据"""
    for line in text.split("\n"):
        if line.startswith("data: "):
            return json.loads(line[6:])
    raise ValueError(f"无法从 SSE 响应中解析数据: {text[:200]}")


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    if "--raw" in sys.argv:
        print(">>> 原始 HTTP 模式（展示协议细节）\n")
        asyncio.run(call_with_raw_http())
    else:
        print(">>> MCP SDK 模式（推荐）\n")
        asyncio.run(call_with_sdk())
