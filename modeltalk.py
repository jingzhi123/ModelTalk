import os
import sys
import json
from datetime import datetime
from openai import OpenAI

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
        return [{"role": msg["role"], "content": msg["content"]} 
                for msg in self.conversation_history if msg["role"] in ["user", "assistant"]]
    
    def send_message(self, user_input):
        """发送消息并获取回复"""
        # 添加用户消息
        self.add_message("user", user_input)
        
        try:
            # 准备消息历史
            messages = self.get_chat_messages()
            
            print("AI正在思考中...")
            
            # 发送请求
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True  # 启用流式输出
            )
            
            # 处理流式响应
            assistant_reply = ""
            print("\nAI助手: ", end="", flush=True)
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    assistant_reply += content
                    print(content, end="", flush=True)
            
            print("\n")  # 换行
            
            # 添加助手回复到历史
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
        print("6. 退出")
        print("="*50)
    
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
                    choice = input("\n请选择操作 (1-6): ").strip()
                    
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
