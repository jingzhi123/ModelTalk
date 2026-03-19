# ModelTalk

<div align="center">

**一个简洁优雅的 AI 模型对话测试工具**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [配置说明](#配置说明)

</div>

---

## 项目简介

ModelTalk 是一个命令行 AI 对话助手，让你可以轻松测试和体验各种 AI 模型。通过集成 CLIProxy 代理服务，你可以使用统一的接口访问 OpenAI、Gemini、Claude、Codex 等多种 AI 服务。

### 为什么选择 ModelTalk？

- 🎯 **简单直接** - 无需复杂配置，开箱即用
- 💬 **流畅体验** - 支持流式输出，实时查看 AI 回复
- 📚 **完整记录** - 自动保存对话历史，随时回顾
- 🔄 **灵活切换** - 轻松在不同 AI 模型间切换
- 🛠️ **技能扩展** - 支持网络搜索、网页浏览、文件操作等实用技能
- 🤖 **智能执行** - AI 可以真正执行操作，而不只是告诉你怎么做

## 功能特性

### 核心功能

- ✨ **流式对话输出** - 实时显示 AI 回复，体验更流畅
- 💾 **会话历史管理** - 自动保存所有对话，支持查看和导出
- 🔄 **模型切换** - 动态获取可用模型列表，一键切换
- 📝 **对话导出** - 将会话记录导出为文本文件
- ⌨️ **友好交互** - 简洁的命令行界面，支持快捷命令
- 🎨 **时间戳记录** - 每条消息都带有时间戳

### AI 技能系统 🔧

ModelTalk 支持通过 Function Calling 扩展 AI 能力，让 AI 可以真正执行操作：

#### 🌐 网络搜索
- 实时搜索互联网信息
- 查询最新新闻、天气、百科知识
- 使用 DuckDuckGo API（无需 API key）

#### 🌍 网页浏览
- 访问并提取网页内容
- 智能解析 HTML，提取正文
- 获取网页标题、链接等信息

#### 📁 文件操作
- **列出目录** - 查看文件夹内容和结构
- **读取文件** - 查看文本文件内容（支持 UTF-8/GBK）
- **写入文件** - 创建或修改文件，生成代码
- **创建目录** - 新建文件夹和目录结构
- **删除文件** - 删除文件或目录（谨慎使用）

**示例对话：**
```
你: 搜索一下 Python 最新版本
AI: 🔍 正在搜索...

你: 访问 https://example.com 看看内容
AI: 🌐 正在访问...

你: 创建一个 HTML 页面保存为 index.html
AI: ✍️ 正在写入文件...
    ✅ 文件已保存

你: 列出当前目录的文件
AI: 📁 正在列出目录...
```

详细的技能使用说明请查看 [SKILLS.md](SKILLS.md)

### CLIProxy 代理服务

ModelTalk 依赖 [CLIProxy](https://github.com/router-for-me/CLIProxyAPI) 提供统一的 API 接口：

- 🔌 OpenAI 兼容的 API 接口
- 🌐 支持多种 AI 服务（Gemini、Claude、Codex、Qwen、iFlow 等）
- 🔐 OAuth 登录支持
- ⚖️ 多账户负载均衡
- 🔄 自动重试和故障转移
- 🖼️ 多模态输入支持

## 快速开始

### 环境要求

- Python 3.7 或更高版本
- Windows/Linux/macOS
- CLIProxy 代理服务（需单独下载）

### 安装步骤

**1. 下载并配置 CLIProxy**

首先从官方仓库下载 CLIProxy：

```bash
# 访问 CLIProxy 官方仓库
https://github.com/router-for-me/CliProxyAPI

# 下载对应平台的可执行文件
# Windows: cli-proxy-api.exe
# Linux/macOS: cli-proxy-api
```

创建 `config.yaml` 配置文件：

```yaml
port: 8317

api-keys:
  - sk-your-api-key-here

auth-dir: "~/.cli-proxy-api"
```

启动 CLIProxy 服务：

```bash
./cli-proxy-api.exe  # Windows
# 或
./cli-proxy-api      # Linux/macOS
```

**2. 安装 ModelTalk**

克隆本仓库：

```bash
git clone https://github.com/jingzhi123/ModelTalk.git
cd ModelTalk
```

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

依赖包括：
- `openai` - OpenAI API 客户端
- `requests` - HTTP 请求库（用于网络搜索和网页浏览）
- `beautifulsoup4` - HTML 解析库（用于网页内容提取）

**3. 运行 ModelTalk**

```bash
python modeltalk.py
```

## 使用指南

### 开始对话

启动后直接输入问题即可：

```
🤖 AI助手已启动！
当前使用模型: gpt-5.3-codex
输入 '/menu' 查看命令菜单，输入 '/quit' 退出

你: 你好，介绍一下你自己

AI助手: 你好！我是一个AI助手...
```

### 命令菜单

输入 `/menu` 打开功能菜单：

```
==================================================
AI助手 - 命令菜单
==================================================
1. 继续对话
2. 查看会话历史
3. 清空会话历史
4. 切换模型
5. 导出会话
6. 技能管理
7. 退出
==================================================
```

### 技能管理

通过菜单选项 6 可以管理 AI 技能：

```
==================================================
技能管理
==================================================
当前技能状态:
  网络搜索: ✅ 已启用
  网页浏览: ✅ 已启用
  文件操作: ✅ 已启用
==================================================

输入技能名称切换状态:
  - web_search (网络搜索)
  - web_browse (网页浏览)
  - file_operations (文件操作)
  - back (返回)
```

### 快捷命令

| 命令 | 功能 |
|------|------|
| `/menu` | 显示命令菜单 |
| `/history` | 查看会话历史 |
| `/clear` | 清空会话历史 |
| `/quit` 或 `/exit` | 退出程序 |

### 会话管理

- **自动保存**: 所有对话自动保存到 `chat_history.json`
- **持久化**: 重启程序后自动加载历史记录
- **导出功能**: 导出为 `chat_export_YYYYMMDD_HHMMSS.txt` 格式

## 配置说明

### ModelTalk 配置

在 `modeltalk.py` 中修改连接设置：

```python
self.client = OpenAI(
    api_key="sk-your-api-key",           # 与 CLIProxy 配置一致
    base_url="http://localhost:8317/v1"  # CLIProxy 服务地址
)
```

### CLIProxy 配置

CLIProxy 需要单独下载和配置。详细配置请参考 [CLIProxy 官方文档](https://github.com/router-for-me/CliProxyAPI)。

**主要配置项：**

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `port` | 服务端口 | 8317 |
| `api-keys` | API 密钥列表 | - |
| `auth-dir` | 认证信息目录 | `~/.cli-proxy-api` |
| `proxy-url` | 上游代理（可选） | - |
| `debug` | 调试模式 | false |

## 项目结构

```
ModelTalk/
├── modeltalk.py               # 主程序
├── chat_history.json          # 会话历史（自动生成）
├── chat_export_*.txt          # 导出的对话记录（自动生成）
├── requirements.txt           # Python 依赖
├── SKILLS.md                  # 技能系统文档
├── README.md                  # 项目说明
├── LICENSE                    # 许可证
└── .gitignore                 # Git 忽略规则
```

注意：CLIProxy 需要单独下载，不包含在本仓库中。

## 常见问题

<details>
<summary><b>Q: 连接失败怎么办？</b></summary>

确保 CLIProxy 服务已启动并运行在正确的端口（默认 8317）。可以通过访问 `http://localhost:8317` 检查服务状态。
</details>

<details>
<summary><b>Q: API 密钥错误？</b></summary>

检查 `modeltalk.py` 中的 API 密钥是否与 `CLIProxy/config.yaml` 中配置的密钥一致。
</details>

<details>
<summary><b>Q: 如何添加更多 AI 模型？</b></summary>

在 CLIProxy 的 `config.yaml` 中配置相应的 API 密钥，支持 Gemini、Claude、Codex 等多种服务。详见 [CLIProxy 文档](https://github.com/router-for-me/CliProxyAPI)。
</details>

<details>
<summary><b>Q: 会话历史存储在哪里？</b></summary>

会话历史保存在 `chat_history.json` 文件中，可以手动备份或删除。
</details>

<details>
<summary><b>Q: AI 技能是什么？如何使用？</b></summary>

AI 技能是通过 Function Calling 实现的扩展功能，让 AI 可以执行实际操作。目前支持：
- 网络搜索：搜索实时信息
- 网页浏览：访问和提取网页内容
- 文件操作：读写文件、管理目录

使用方法：直接在对话中提出需求，AI 会自动调用相应工具。例如："搜索 Python 教程"、"创建一个 HTML 文件"。

详见 [SKILLS.md](SKILLS.md)
</details>

<details>
<summary><b>Q: 如何禁用某个技能？</b></summary>

输入 `/menu` -> 选择 `6. 技能管理` -> 输入技能名称（如 `web_search`）即可切换开关。
</details>

<details>
<summary><b>Q: 文件操作安全吗？</b></summary>

文件操作功能会直接修改本地文件，请注意：
- 写入文件会覆盖已存在的文件
- 删除操作不可恢复
- 建议在测试环境中使用
- 可以通过技能管理禁用文件操作功能
</details>

## 依赖项目

本项目依赖以下开源项目：

- **[CLIProxy API](https://github.com/router-for-me/CliProxyAPI)** - 提供统一的 AI API 代理服务
- **[OpenAI Python SDK](https://github.com/openai/openai-python)** - OpenAI 官方 Python 客户端
- **[Requests](https://github.com/psf/requests)** - HTTP 请求库
- **[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)** - HTML/XML 解析库

## 开发路线图

- [x] 基础对话功能
- [x] 会话历史管理
- [x] 流式输出支持
- [x] 网络搜索技能
- [x] 网页浏览技能
- [x] 文件操作技能
- [ ] 更多 AI 技能（计算器、天气查询等）
- [ ] 配置文件支持
- [ ] 对话分组管理
- [ ] 自定义提示词模板
- [ ] 对话统计和分析
- [ ] 多语言界面
- [ ] GUI 图形界面

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

感谢以下项目和贡献者：

- [CLIProxy API](https://github.com/router-for-me/CliProxyAPI) 团队
- OpenAI 的 Function Calling 功能
- 所有为本项目做出贡献的开发者

## 联系方式

- 📧 Email: abc231@foxmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/jingzhi123/ModelTalk/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！**

Made with ❤️ by JohnConner

</div>
