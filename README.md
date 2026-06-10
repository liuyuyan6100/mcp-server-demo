# MCP Server 开发指南

## 项目结构

```
mcp-server-demo/
├── server_fastmcp.py   # FastMCP 方式（推荐，简洁）
├── server_raw.py        # 原生 SDK 方式（底层，灵活）
├── test_server.py       # 测试脚本
└── README.md            # 本文件
```

## 快速开始

```bash
# 1. 初始化环境（创建 venv + 安装依赖）
bash setup.sh

# 2. 运行测试
.venv/bin/python test_server.py          # 测试 FastMCP 版本
.venv/bin/python test_server.py raw      # 测试原生 SDK 版本

# 或者先激活 venv，之后直接用 python
source .venv/bin/activate
python test_server.py
```

## 两种开发方式对比

### FastMCP（推荐入门）
- 用装饰器 `@mcp.tool()` 自动从函数签名生成 JSON Schema
- 参数类型从 type hints 自动推断
- docstring 自动变成工具描述
- 启动一行代码：`mcp.run()`

### 原生 SDK（底层）
- 手动定义 `inputSchema`（JSON Schema 格式）
- 手动实现 `list_tools()` 和 `call_tool()` 两个处理函数
- 更接近协议本身，适合需要精细控制的场景

## 如何接入 Hermes

在 `~/.hermes/config.yaml` 中添加：

```yaml
mcp_servers:
  demo:
    command: "/home/ubuntu/mcp-server-demo/.venv/bin/python"
    args: ["/home/ubuntu/mcp-server-demo/server_fastmcp.py"]
```

重启 Hermes 后，会自动发现并注册两个工具：
- `mcp_demo_calculate` — 计算数学表达式
- `mcp_demo_get_weather` — 查询天气

## MCP 协议通信流程

```
客户端 (Hermes)                    Server (你的代码)
    |                                  |
    |-- initialize 请求 ------------->|
    |<-- initialize 响应 -------------|   (serverInfo, capabilities)
    |                                  |
    |-- tools/list 请求 ------------->|
    |<-- tools/list 响应 -------------|   (工具名称 + inputSchema)
    |                                  |
    |-- tools/call 请求 ------------->|
    |   (name + arguments)             |
    |<-- tools/call 响应 -------------|   (TextContent 结果)
    |                                  |
```

## 核心概念

### Tool 定义
每个工具需要：
- **name**: 唯一名称
- **description**: 描述（LLM 会读这个来决定什么时候用）
- **inputSchema**: JSON Schema 格式的参数定义

### 传输方式
- **stdio**: 通过 stdin/stdout 通信，Hermes 默认用这个
- **HTTP/StreamableHTTP**: 监听端口，适合远程调用

### 安全注意事项
- 不要在 tool 实现里做危险操作（直接执行用户输入的代码等）
- 使用参数校验（FastMCP 的 type hints 会自动校验）
- 敏感信息通过 `env` 配置传入，不要硬编码

## 进阶话题

- **Resources**: 暴露可读取的数据源（文件、数据库等）
- **Prompts**: 预定义的提示词模板
- **Sampling**: Server 主动请求 LLM 做推理（需要客户端支持）
- **错误处理**: 返回 `isError: true` 的结果
- **进度通知**: 长时间运行的工具可以发送进度更新
