import os
import sys
import json
import requests
from datetime import datetime
from openai import OpenAI
from bs4 import BeautifulSoup
from pathlib import Path

class AIAssistant:
    def __init__(self):
        # 配置客户端
        self.client = OpenAI(
            api_key="sk-KoGcRgiUapPJBQd64",
            base_url="http://localhost:8317/v1"
        )
        
        # 会话历史
        self.conversation_history = []
        
        # 获取可用模型
        self.model_name = self.get_available_model()
        
        # 会话文件路径
        self.history_file = os.path.join(os.path.dirname(__file__), "chat_history.json")
        
        # 技能开关
        self.skills_enabled = {
            "web_search": True,      # 网络搜索
            "web_browse": True,      # 网页浏览
            "file_operations": True, # 文件操作
        }
        
        # 加载历史会话
        self.load_history()
    
    def get_available_model(self):
        """获取可用的模型"""
        print("正在获取可用模型列表...")
        try:
            models = self.client.models.list()
            print("\n可用的模型：")
            for i, model in enumerate(models.data, 1):
                print(f"  {i}. {model.id}")
            
            if models.data:
                model_name = "gpt-5.3-codex"  # 默认使用指定模型
                print(f"\n使用模型: {model_name}")
                return model_name
            else:
                print("\n未找到可用模型，使用默认值")
                return "default"
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            print("使用默认模型名称")
            return "default"
    
    def load_history(self):
        """加载历史会话"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                print(f"已加载 {len(self.conversation_history)} 条历史消息")
        except Exception as e:
            print(f"加载历史失败: {e}")
            self.conversation_history = []
    
    def save_history(self):
        """保存会话历史"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")
    
    def add_message(self, role, content):
        """添加消息到会话历史"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
    
    def get_chat_messages(self):
        """获取用于API调用的消息格式"""
        messages = []
        
        # 添加系统提示（如果启用了技能）
        if any(self.skills_enabled.values()):
            system_prompt = "你是一个有用的AI助手，可以使用多种工具来帮助用户。\n\n"
            system_prompt += "重要提示：\n"
            
            if self.skills_enabled.get("web_search"):
                system_prompt += "- 当用户询问实时信息、最新新闻、天气等需要搜索的内容时，使用 web_search 工具\n"
            
            if self.skills_enabled.get("web_browse"):
                system_prompt += "- 当用户提供网址或要求访问网页时，使用 browse_webpage 工具\n"
            
            if self.skills_enabled.get("file_operations"):
                system_prompt += "- 当用户要求'创建文件'、'生成代码'、'保存为文件'、'写入文件'时，必须使用 write_file 工具\n"
                system_prompt += "- 当用户要求'查看文件'、'读取文件'时，使用 read_file 工具\n"
                system_prompt += "- 当用户要求'列出文件'、'查看目录'时，使用 list_directory 工具\n"
                system_prompt += "- 当用户要求'创建文件夹'、'新建目录'时，使用 create_directory 工具\n"
            
            system_prompt += "\n请主动使用这些工具来完成用户的请求，不要只是描述如何做，而是直接调用工具执行操作。"
            
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史消息
        messages.extend([
            {"role": msg["role"], "content": msg["content"]} 
            for msg in self.conversation_history 
            if msg["role"] in ["user", "assistant"]
        ])
        
        return messages
    
    def get_tools_definition(self):
        """获取可用工具的定义"""
        tools = []
        
        if self.skills_enabled.get("web_search"):
            tools.append({
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "在互联网上搜索信息。当用户询问实时信息、最新新闻、天气、股票价格或任何需要联网查询的内容时使用此工具。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词或问题"
                            }
                        },
                        "required": ["query"]
                    }
                }
            })
        
        if self.skills_enabled.get("web_browse"):
            tools.append({
                "type": "function",
                "function": {
                    "name": "browse_webpage",
                    "description": "访问并提取网页内容。当用户提供具体的网址或需要查看某个网页的详细内容时使用。可以提取网页的标题、正文、链接等信息。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "要访问的网页URL地址，必须是完整的URL（包含http://或https://）"
                            }
                        },
                        "required": ["url"]
                    }
                }
            })
        
        if self.skills_enabled.get("file_operations"):
            tools.extend([
                {
                    "type": "function",
                    "function": {
                        "name": "list_directory",
                        "description": "列出指定目录下的文件和文件夹。当用户想查看某个文件夹的内容时使用。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "目录路径，可以是相对路径或绝对路径。默认为当前目录（.）"
                                }
                            },
                            "required": ["path"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "description": "读取文件内容。当用户想查看某个文件的内容时使用。支持文本文件。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "文件路径，可以是相对路径或绝对路径"
                                }
                            },
                            "required": ["filepath"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "write_file",
                        "description": "创建或覆盖文件内容。当用户要求创建文件、生成代码、保存内容、写入文件时必须使用此工具。例如：'创建一个HTML页面'、'生成Python脚本'、'保存为文件'、'写一个配置文件'等场景都应该调用此工具。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "文件路径，包含文件名和扩展名。例如：'index.html'、'script.py'、'config.json'"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "要写入的完整文件内容"
                                }
                            },
                            "required": ["filepath", "content"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_directory",
                        "description": "创建新目录。当用户想创建新文件夹时使用。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "要创建的目录路径"
                                }
                            },
                            "required": ["path"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_file",
                        "description": "删除文件或目录。当用户明确要求删除文件或文件夹时使用。请谨慎使用此功能。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "要删除的文件或目录路径"
                                }
                            },
                            "required": ["path"]
                        }
                    }
                }
            ])
        
        return tools if tools else None
    
    def web_search(self, query):
        """执行网络搜索"""
        try:
            # 使用 DuckDuckGo 的即时答案 API（无需 API key）
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            print(f"🔍 正在搜索: {query}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 提取搜索结果
                results = []
                
                # 即时答案
                if data.get("AbstractText"):
                    results.append(f"摘要: {data['AbstractText']}")
                
                # 相关主题
                if data.get("RelatedTopics"):
                    results.append("\n相关信息:")
                    for i, topic in enumerate(data["RelatedTopics"][:3], 1):
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append(f"{i}. {topic['Text']}")
                
                if results:
                    return "\n".join(results)
                else:
                    return f"未找到关于 '{query}' 的详细信息，建议尝试更具体的搜索词。"
            else:
                return f"搜索请求失败，状态码: {response.status_code}"
                
        except requests.Timeout:
            return "搜索超时，请检查网络连接或稍后重试。"
        except Exception as e:
            return f"搜索出错: {str(e)}"
    
    def browse_webpage(self, url):
        """浏览网页并提取内容"""
        try:
            print(f"🌐 正在访问: {url}")
            
            # 设置请求头，模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "无标题"
            
            # 移除脚本和样式标签
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # 提取正文内容
            # 优先查找常见的内容容器
            content_tags = soup.find_all(['article', 'main', 'div'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['content', 'article', 'post', 'entry', 'main']
            ))
            
            if content_tags:
                text = ' '.join([tag.get_text(separator=' ', strip=True) for tag in content_tags])
            else:
                # 如果没找到特定容器，提取所有段落
                paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                text = ' '.join([p.get_text(separator=' ', strip=True) for p in paragraphs])
            
            # 清理文本
            text = ' '.join(text.split())
            
            # 限制长度
            max_length = 3000
            if len(text) > max_length:
                text = text[:max_length] + "...\n\n[内容过长，已截断]"
            
            # 提取链接（可选）
            links = soup.find_all('a', href=True)
            important_links = []
            for link in links[:5]:  # 只取前5个链接
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                if href.startswith('http') and link_text:
                    important_links.append(f"- {link_text}: {href}")
            
            result = f"📄 标题: {title_text}\n\n"
            result += f"📝 内容:\n{text}\n"
            
            if important_links:
                result += f"\n🔗 相关链接:\n" + "\n".join(important_links)
            
            return result
            
        except requests.Timeout:
            return f"访问超时: {url}"
        except requests.RequestException as e:
            return f"访问失败: {str(e)}"
        except Exception as e:
            return f"解析网页出错: {str(e)}"
    
    def list_directory(self, path="."):
        """列出目录内容"""
        try:
            print(f"📁 正在列出目录: {path}")
            
            path_obj = Path(path)
            if not path_obj.exists():
                return f"路径不存在: {path}"
            
            if not path_obj.is_dir():
                return f"不是目录: {path}"
            
            items = []
            for item in sorted(path_obj.iterdir()):
                if item.is_dir():
                    items.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    size_str = self._format_size(size)
                    items.append(f"📄 {item.name} ({size_str})")
            
            if not items:
                return f"目录为空: {path}"
            
            result = f"目录: {path_obj.absolute()}\n"
            result += f"共 {len(items)} 项:\n\n"
            result += "\n".join(items)
            
            return result
            
        except PermissionError:
            return f"没有权限访问: {path}"
        except Exception as e:
            return f"列出目录失败: {str(e)}"
    
    def read_file(self, filepath):
        """读取文件内容"""
        try:
            print(f"📖 正在读取文件: {filepath}")
            
            path_obj = Path(filepath)
            if not path_obj.exists():
                return f"文件不存在: {filepath}"
            
            if not path_obj.is_file():
                return f"不是文件: {filepath}"
            
            # 检查文件大小
            size = path_obj.stat().st_size
            if size > 1024 * 1024:  # 1MB
                return f"文件过大 ({self._format_size(size)})，建议使用其他工具打开"
            
            # 尝试读取文本文件
            try:
                with open(path_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(path_obj, 'r', encoding='gbk') as f:
                        content = f.read()
                except:
                    return f"无法读取文件（可能是二进制文件）: {filepath}"
            
            # 限制显示长度
            max_length = 5000
            if len(content) > max_length:
                content = content[:max_length] + f"\n\n[文件过长，已截断。总长度: {len(content)} 字符]"
            
            result = f"文件: {path_obj.absolute()}\n"
            result += f"大小: {self._format_size(size)}\n"
            result += f"\n内容:\n{'-'*50}\n{content}\n{'-'*50}"
            
            return result
            
        except PermissionError:
            return f"没有权限读取: {filepath}"
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    def write_file(self, filepath, content):
        """写入文件"""
        try:
            print(f"✍️ 正在写入文件: {filepath}")
            
            path_obj = Path(filepath)
            
            # 创建父目录（如果不存在）
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(path_obj, 'w', encoding='utf-8') as f:
                f.write(content)
            
            size = path_obj.stat().st_size
            return f"✅ 文件已保存: {path_obj.absolute()}\n大小: {self._format_size(size)}"
            
        except PermissionError:
            return f"没有权限写入: {filepath}"
        except Exception as e:
            return f"写入文件失败: {str(e)}"
    
    def create_directory(self, path):
        """创建目录"""
        try:
            print(f"📁 正在创建目录: {path}")
            
            path_obj = Path(path)
            path_obj.mkdir(parents=True, exist_ok=True)
            
            return f"✅ 目录已创建: {path_obj.absolute()}"
            
        except PermissionError:
            return f"没有权限创建目录: {path}"
        except Exception as e:
            return f"创建目录失败: {str(e)}"
    
    def delete_file(self, path):
        """删除文件或目录"""
        try:
            print(f"🗑️ 正在删除: {path}")
            
            path_obj = Path(path)
            if not path_obj.exists():
                return f"路径不存在: {path}"
            
            if path_obj.is_file():
                path_obj.unlink()
                return f"✅ 文件已删除: {path}"
            elif path_obj.is_dir():
                # 删除目录及其内容
                import shutil
                shutil.rmtree(path_obj)
                return f"✅ 目录已删除: {path}"
            else:
                return f"未知的路径类型: {path}"
                
        except PermissionError:
            return f"没有权限删除: {path}"
        except Exception as e:
            return f"删除失败: {str(e)}"
    
    def _format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def execute_function(self, function_name, arguments):
        """执行函数调用"""
        if function_name == "web_search":
            return self.web_search(arguments.get("query", ""))
        elif function_name == "browse_webpage":
            return self.browse_webpage(arguments.get("url", ""))
        elif function_name == "list_directory":
            return self.list_directory(arguments.get("path", "."))
        elif function_name == "read_file":
            return self.read_file(arguments.get("filepath", ""))
        elif function_name == "write_file":
            return self.write_file(
                arguments.get("filepath", ""),
                arguments.get("content", "")
            )
        elif function_name == "create_directory":
            return self.create_directory(arguments.get("path", ""))
        elif function_name == "delete_file":
            return self.delete_file(arguments.get("path", ""))
        else:
            return f"未知的函数: {function_name}"
    
    def send_message(self, user_input):
        """发送消息并获取回复"""
        # 添加用户消息
        self.add_message("user", user_input)
        
        try:
            # 准备消息历史
            messages = self.get_chat_messages()
            
            print("AI正在思考中...")
            
            # 获取工具定义
            tools = self.get_tools_definition()
            
            # 发送请求
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": True
            }
            
            # 如果有可用工具，添加到请求中
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**request_params)
            
            # 处理流式响应
            assistant_reply = ""
            tool_calls = []
            current_tool_call = None
            
            print("\nAI助手: ", end="", flush=True)
            
            for chunk in response:
                delta = chunk.choices[0].delta
                
                # 处理文本内容
                if delta.content is not None:
                    content = delta.content
                    assistant_reply += content
                    print(content, end="", flush=True)
                
                # 处理工具调用
                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        if tool_call_delta.index is not None:
                            # 新的工具调用
                            if current_tool_call is None or tool_call_delta.index != current_tool_call.get('index'):
                                if current_tool_call:
                                    tool_calls.append(current_tool_call)
                                current_tool_call = {
                                    'index': tool_call_delta.index,
                                    'id': tool_call_delta.id or '',
                                    'type': 'function',
                                    'function': {
                                        'name': tool_call_delta.function.name or '',
                                        'arguments': tool_call_delta.function.arguments or ''
                                    }
                                }
                            else:
                                # 继续累积参数
                                if tool_call_delta.function.arguments:
                                    current_tool_call['function']['arguments'] += tool_call_delta.function.arguments
            
            # 添加最后一个工具调用
            if current_tool_call:
                tool_calls.append(current_tool_call)
            
            print("\n")  # 换行
            
            # 如果有工具调用，执行它们
            if tool_calls:
                print("🔧 正在使用工具...")
                
                # 添加助手的工具调用消息
                self.add_message("assistant", assistant_reply if assistant_reply else None)
                
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    print(f"📞 调用函数: {function_name}")
                    print(f"📝 参数: {function_args}")
                    
                    # 执行函数
                    function_result = self.execute_function(function_name, function_args)
                    print(f"✅ 结果: {function_result}\n")
                    
                    # 添加工具结果到消息历史
                    messages.append({
                        "role": "assistant",
                        "content": assistant_reply if assistant_reply else None,
                        "tool_calls": [{
                            "id": tool_call['id'],
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(function_args, ensure_ascii=False)
                            }
                        }]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": function_result
                    })
                
                # 再次调用 API 获取最终回复
                print("AI正在整理答案...")
                final_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                    stream=True
                )
                
                final_reply = ""
                print("\nAI助手: ", end="", flush=True)
                
                for chunk in final_response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        final_reply += content
                        print(content, end="", flush=True)
                
                print("\n")
                
                # 添加最终回复
                self.add_message("assistant", final_reply)
                assistant_reply = final_reply
            else:
                # 没有工具调用，直接添加回复
                self.add_message("assistant", assistant_reply)
            
            # 保存历史
            self.save_history()
            
            return assistant_reply
            
        except Exception as e:
            error_msg = f"请求失败: {e}"
            print(f"\n{error_msg}")
            return error_msg
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "="*50)
        print("AI助手 - 命令菜单")
        print("="*50)
        print("1. 继续对话")
        print("2. 查看会话历史")
        print("3. 清空会话历史")
        print("4. 切换模型")
        print("5. 导出会话")
        print("6. 技能管理")
        print("7. 退出")
        print("="*50)
    
    def manage_skills(self):
        """管理技能开关"""
        print("\n" + "="*50)
        print("技能管理")
        print("="*50)
        print("当前技能状态:")
        for skill, enabled in self.skills_enabled.items():
            status = "✅ 已启用" if enabled else "❌ 已禁用"
            skill_name = {
                "web_search": "网络搜索",
                "web_browse": "网页浏览",
                "file_operations": "文件操作"
            }.get(skill, skill)
            print(f"  {skill_name}: {status}")
        print("="*50)
        print("\n输入技能名称切换状态:")
        print("  - web_search (网络搜索)")
        print("  - web_browse (网页浏览)")
        print("  - file_operations (文件操作)")
        print("  - back (返回)")
        
        choice = input("\n请选择: ").strip().lower()
        
        if choice == 'back':
            return
        elif choice in self.skills_enabled:
            self.skills_enabled[choice] = not self.skills_enabled[choice]
            status = "启用" if self.skills_enabled[choice] else "禁用"
            print(f"\n已{status}技能: {choice}")
        else:
            print("\n无效的技能名称")
    
    def show_history(self):
        """显示会话历史"""
        if not self.conversation_history:
            print("\n暂无会话历史")
            return
        
        print(f"\n会话历史 (共{len(self.conversation_history)}条消息):")
        print("-" * 50)
        
        for i, msg in enumerate(self.conversation_history, 1):
            role_name = "用户" if msg["role"] == "user" else "AI助手"
            timestamp = msg.get("timestamp", "未知时间")
            print(f"\n[{i}] {role_name} ({timestamp}):")
            print(msg["content"])
            print("-" * 30)
    
    def clear_history(self):
        """清空会话历史"""
        confirm = input("\n确定要清空所有会话历史吗？(y/N): ").strip().lower()
        if confirm == 'y':
            self.conversation_history = []
            try:
                if os.path.exists(self.history_file):
                    os.remove(self.history_file)
                print("会话历史已清空")
            except Exception as e:
                print(f"清空历史文件失败: {e}")
        else:
            print("操作已取消")
    
    def export_history(self):
        """导出会话历史"""
        if not self.conversation_history:
            print("\n暂无会话历史可导出")
            return
        
        # 导出文件也放在model-test目录下
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"AI助手会话记录\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"使用模型: {self.model_name}\n")
                f.write("="*50 + "\n\n")
                
                for i, msg in enumerate(self.conversation_history, 1):
                    role_name = "用户" if msg["role"] == "user" else "AI助手"
                    timestamp = msg.get("timestamp", "未知时间")
                    f.write(f"[{i}] {role_name} ({timestamp}):\n")
                    f.write(f"{msg['content']}\n")
                    f.write("-" * 30 + "\n\n")
            
            print(f"\n会话历史已导出到: {filename}")
        except Exception as e:
            print(f"导出失败: {e}")
    
    def run(self):
        """运行AI助手"""
        print("🤖 AI助手已启动！")
        print(f"当前使用模型: {self.model_name}")
        print("输入 '/menu' 查看命令菜单，输入 '/quit' 退出")
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n你: ").strip()
                
                # 处理特殊命令
                if user_input.lower() in ['/quit', '/exit', '退出']:
                    print("\n再见！👋")
                    break
                elif user_input.lower() == '/menu':
                    self.show_menu()
                    choice = input("\n请选择操作 (1-7): ").strip()
                    
                    if choice == '1':
                        continue  # 继续对话
                    elif choice == '2':
                        self.show_history()
                    elif choice == '3':
                        self.clear_history()
                    elif choice == '4':
                        self.model_name = self.get_available_model()
                    elif choice == '5':
                        self.export_history()
                    elif choice == '6':
                        self.manage_skills()
                    elif choice == '7':
                        print("\n再见！👋")
                        break
                    else:
                        print("无效选择，请重试")
                    continue
                elif user_input.lower() == '/clear':
                    self.clear_history()
                    continue
                elif user_input.lower() == '/history':
                    self.show_history()
                    continue
                elif not user_input:
                    print("请输入消息内容")
                    continue
                
                # 发送消息
                self.send_message(user_input)
                
            except KeyboardInterrupt:
                print("\n\n程序被中断，正在退出...")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")
                continue

if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.run()
