"""
MCP Server 示例 —— 用 FastMCP 方式开发（推荐入门）

这是一个最简可用的 MCP server，提供两个工具：
1. calculate: 简单计算器
2. get_weather: 模拟天气查询（演示带参数的工具）

运行方式：
  python server_fastmcp.py          # stdio 模式（默认，Hermes 用这个）
  python server_fastmcp.py --http   # HTTP 模式
"""

from mcp.server.fastmcp import FastMCP

# 创建 server 实例，名字会出现在 Hermes 的 mcp_servers 配置里
mcp = FastMCP("demo-calculator", host="0.0.0.0", port=8765)


@mcp.tool()
def calculate(expression: str) -> str:
    """
    计算数学表达式。
    
    参数:
        expression: 数学表达式，如 "2 + 3 * 4"、"sqrt(144)"、"10 % 3"
    
    返回:
        计算结果的字符串
    """
    import math

    # 安全起见，只允许数学相关操作
    allowed_names = {
        "abs": abs, "round": round,
        "sqrt": math.sqrt, "pow": pow,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e,
        "log": math.log, "log10": math.log10,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """
    查询指定城市的天气（演示用，返回模拟数据）。
    
    参数:
        city: 城市名称，如 "北京"、"Shanghai"
        unit: 温度单位，celsius 或 fahrenheit
    
    返回:
        天气信息字符串
    """
    # 这里是模拟数据，实际开发时你会调用真实 API
    mock_data = {
        "北京": {"temp": 28, "condition": "晴", "humidity": 45},
        "上海": {"temp": 32, "condition": "多云", "humidity": 72},
        "深圳": {"temp": 34, "condition": "雷阵雨", "humidity": 85},
    }

    data = mock_data.get(city)
    if not data:
        return f"未找到城市 '{city}' 的天气数据"

    temp = data["temp"]
    if unit == "fahrenheit":
        temp = temp * 9 / 5 + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"

    return (
        f"📍 {city}\n"
        f"🌡️ 温度: {temp}{unit_symbol}\n"
        f"🌤️ 天气: {data['condition']}\n"
        f"💧 湿度: {data['humidity']}%"
    )


# ---- 启动入口 ----
if __name__ == "__main__":
    import sys

    if "--http" in sys.argv:
        # HTTP 模式：监听 8765 端口，适合远程调用
        print("Starting MCP server on http://0.0.0.0:8765/mcp")
        mcp.run(transport="streamable-http")
    else:
        # stdio 模式：通过 stdin/stdout 通信，Hermes 默认用这个
        mcp.run(transport="stdio")
