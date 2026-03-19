# ModelTalk 技能系统

ModelTalk 支持通过 Function Calling 机制扩展 AI 的能力，让 AI 可以调用外部工具和服务。

## 已实现的技能

### 1. 网络搜索 (web_search)

允许 AI 在互联网上搜索实时信息。

**使用场景：**
- 查询最新新闻
- 获取实时天气信息
- 搜索百科知识
- 查找技术文档

**示例对话：**
```
你: 今天北京的天气怎么样？
AI: 🔍 正在搜索: 北京天气
    [搜索结果...]
    根据搜索结果，今天北京...

你: Python 3.12 有什么新特性？
AI: 🔍 正在搜索: Python 3.12 新特性
    [搜索结果...]
    Python 3.12 的主要新特性包括...
```

**技术实现：**
- 使用 DuckDuckGo API（无需 API key）
- 自动提取摘要和相关信息
- 超时保护（10秒）

### 2. 网页浏览 (web_browse)

访问并提取网页内容，支持解析 HTML 并提取正文。

**使用场景：**
- 查看具体网页内容
- 提取文章正文
- 获取网页标题和链接
- 分析网页结构

**示例对话：**
```
你: 帮我看看这个网页的内容 https://example.com/article
AI: 🌐 正在访问: https://example.com/article
    📄 标题: 文章标题
    📝 内容: [提取的正文内容...]
    🔗 相关链接: [页面中的重要链接...]

你: 访问 GitHub 首页看看有什么
AI: [访问并提取 GitHub 首页内容...]
```

**技术实现：**
- 使用 requests 获取网页
- BeautifulSoup 解析 HTML
- 智能提取正文内容
- 自动过滤脚本和样式
- 内容长度限制（3000字符）

**注意事项：**
- 某些网站可能有反爬虫机制
- 动态加载的内容可能无法获取
- 需要良好的网络连接

### 3. 文件操作 (file_operations)

提供完整的本地文件和目录操作功能。

#### 3.1 列出目录 (list_directory)

**使用场景：**
- 查看文件夹内容
- 浏览项目结构
- 检查文件是否存在

**示例对话：**
```
你: 列出当前目录的文件
AI: 📁 正在列出目录: .
    目录: D:\projects\ModelTalk
    共 5 项:
    📁 CLIProxy/
    📄 modeltalk.py (15.2 KB)
    📄 README.md (8.5 KB)
    ...

你: 看看 C:\Users 下有什么
AI: [列出 C:\Users 目录内容...]
```

#### 3.2 读取文件 (read_file)

**使用场景：**
- 查看文件内容
- 分析代码文件
- 读取配置文件
- 检查日志文件

**示例对话：**
```
你: 读取 config.yaml 文件
AI: 📖 正在读取文件: config.yaml
    文件: D:\projects\config.yaml
    大小: 2.3 KB
    内容:
    --------------------------------------------------
    [文件内容...]
    --------------------------------------------------

你: 帮我看看 README.md 写了什么
AI: [读取并显示 README.md 内容...]
```

**限制：**
- 文本文件最大 1MB
- 显示内容最多 5000 字符
- 支持 UTF-8 和 GBK 编码

#### 3.3 写入文件 (write_file)

**使用场景：**
- 创建新文件
- 修改文件内容
- 保存生成的代码
- 写入配置文件

**示例对话：**
```
你: 创建一个 hello.py 文件，内容是打印 Hello World
AI: ✍️ 正在写入文件: hello.py
    ✅ 文件已保存: D:\projects\hello.py
    大小: 45 B

你: 帮我写一个简单的 HTML 页面保存为 index.html
AI: [创建并保存 HTML 文件...]
```

**注意事项：**
- 会覆盖已存在的文件
- 自动创建父目录
- 使用 UTF-8 编码

#### 3.4 创建目录 (create_directory)

**使用场景：**
- 创建新文件夹
- 组织项目结构
- 批量创建目录

**示例对话：**
```
你: 创建一个名为 test 的文件夹
AI: 📁 正在创建目录: test
    ✅ 目录已创建: D:\projects\test

你: 创建 src/components/ui 目录结构
AI: [创建多级目录...]
```

#### 3.5 删除文件 (delete_file)

**使用场景：**
- 删除临时文件
- 清理无用文件
- 删除空目录

**示例对话：**
```
你: 删除 temp.txt 文件
AI: 🗑️ 正在删除: temp.txt
    ✅ 文件已删除: temp.txt

你: 删除 old_backup 文件夹
AI: [删除目录及其内容...]
```

**警告：**
- 删除操作不可恢复
- 会递归删除目录内容
- 请谨慎使用

## 如何使用技能

### 启用/禁用技能

1. 输入 `/menu` 打开菜单
2. 选择 `6. 技能管理`
3. 输入技能名称（如 `web_search`）切换状态

### 在代码中配置

编辑 `modeltalk.py`，修改 `skills_enabled` 字典：

```python
self.skills_enabled = {
    "web_search": True,   # True 启用，False 禁用
}
```

## 如何添加新技能

### 步骤 1: 定义工具

在 `get_tools_definition()` 方法中添加新工具定义：

```python
if self.skills_enabled.get("your_skill_name"):
    tools.append({
        "type": "function",
        "function": {
            "name": "your_function_name",
            "description": "工具的详细描述，AI 会根据这个描述决定何时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "参数1的描述"
                    },
                    "param2": {
                        "type": "number",
                        "description": "参数2的描述"
                    }
                },
                "required": ["param1"]
            }
        }
    })
```

### 步骤 2: 实现功能

创建对应的方法：

```python
def your_function_name(self, param1, param2=None):
    """执行具体功能"""
    try:
        # 实现你的功能逻辑
        result = do_something(param1, param2)
        return result
    except Exception as e:
        return f"执行失败: {str(e)}"
```

### 步骤 3: 注册到执行器

在 `execute_function()` 方法中添加分支：

```python
def execute_function(self, function_name, arguments):
    """执行函数调用"""
    if function_name == "web_search":
        return self.web_search(arguments.get("query", ""))
    elif function_name == "your_function_name":
        return self.your_function_name(
            arguments.get("param1"),
            arguments.get("param2")
        )
    else:
        return f"未知的函数: {function_name}"
```

### 步骤 4: 添加到技能开关

在 `__init__()` 方法中添加开关：

```python
self.skills_enabled = {
    "web_search": True,
    "your_skill_name": True,  # 新技能
}
```

在 `manage_skills()` 方法中添加显示名称：

```python
skill_name = {
    "web_search": "网络搜索",
    "your_skill_name": "你的技能名称"
}.get(skill, skill)
```

## 技能开发建议

### 1. 错误处理
- 始终使用 try-except 捕获异常
- 返回友好的错误信息
- 添加超时保护

### 2. 描述清晰
- Function description 要详细说明使用场景
- Parameter description 要说明参数的格式和含义
- 帮助 AI 准确判断何时调用

### 3. 返回格式
- 返回字符串格式的结果
- 结构化数据使用清晰的格式
- 避免返回过长的内容

### 4. 性能考虑
- 添加缓存机制（如果适用）
- 设置合理的超时时间
- 避免阻塞主线程

## 技能示例

### 示例 1: 计算器

```python
# 1. 定义工具
if self.skills_enabled.get("calculator"):
    tools.append({
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算，支持基本的四则运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 2' 或 '10 * 5'"
                    }
                },
                "required": ["expression"]
            }
        }
    })

# 2. 实现功能
def calculate(self, expression):
    """执行数学计算"""
    try:
        # 安全的计算方式
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

# 3. 注册执行器
elif function_name == "calculate":
    return self.calculate(arguments.get("expression", ""))
```

### 示例 2: 文件读取

```python
# 1. 定义工具
if self.skills_enabled.get("file_reader"):
    tools.append({
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "文件路径"
                    }
                },
                "required": ["filepath"]
            }
        }
    })

# 2. 实现功能
def read_file(self, filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"文件内容:\n{content[:500]}..."  # 限制长度
    except Exception as e:
        return f"读取失败: {str(e)}"

# 3. 注册执行器
elif function_name == "read_file":
    return self.read_file(arguments.get("filepath", ""))
```

## 常见问题

### Q: AI 不调用我的工具？
A: 检查 description 是否清晰描述了使用场景，AI 需要根据描述判断何时调用。

### Q: 工具调用失败？
A: 检查参数定义是否正确，确保 required 字段包含必需参数。

### Q: 如何调试工具调用？
A: 在 `execute_function()` 中添加 print 语句，查看传入的参数。

### Q: 支持异步调用吗？
A: 当前版本是同步调用，可以考虑使用线程池实现异步。

## 更多资源

- [OpenAI Function Calling 文档](https://platform.openai.com/docs/guides/function-calling)
- [ModelTalk GitHub 仓库](https://github.com/jingzhi123/ModelTalk)
