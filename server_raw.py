"""
MCP Server 示例 —— 用原生 mcp SDK 开发（底层方式）

这种方式更接近 MCP 协议本身，适合需要精细控制的场景。

运行方式：
  python server_raw.py
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 创建 server 实例
server = Server("demo-raw-calculator")


# ---- 第一步：定义工具列表 ----
# 用 @server.list_tools() 装饰器告诉 MCP 客户端"我有哪些工具"
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add",
            description="将两个数字相加",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数字"},
                    "b": {"type": "number", "description": "第二个数字"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="greet",
            description="生成一条问候语",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "被问候的人的名字"},
                    "language": {
                        "type": "string",
                        "enum": ["zh", "en"],
                        "description": "语言，zh=中文，en=英文",
                        "default": "zh",
                    },
                },
                "required": ["name"],
            },
        ),
    ]


# ---- 第二步：实现工具调用逻辑 ----
# 用 @server.call_tool() 装饰器处理"Agent 调用某个工具"的请求
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add":
        a = arguments["a"]
        b = arguments["b"]
        result = a + b
        return [TextContent(type="text", text=f"{a} + {b} = {result}")]

    elif name == "greet":
        person_name = arguments["name"]
        lang = arguments.get("language", "zh")
        if lang == "en":
            greeting = f"Hello, {person_name}! Nice to meet you."
        else:
            greeting = f"你好，{person_name}！很高兴认识你。"
        return [TextContent(type="text", text=greeting)]

    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]


# ---- 第三步：启动 server ----
async def main():
    # stdio_server 会接管 stdin/stdout，与 MCP 客户端通信
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
