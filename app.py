import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from typing import Tuple, Any
from config import MODEL_MAPPING, COST_PER_TOKEN, DEFAULT_MESSAGES
from datetime import datetime
import requests

load_dotenv()

class GPTChat:
    def __init__(self, api_key: str):
        st.set_page_config(page_title='Chat', page_icon='💬')
        # print("key: {}".format(api_key))
        self.client1 = OpenAI(api_key="sk-P3N9W5E4ZbDU7GRwoiHL4tJaFXsliJHBrXAFmHannHs9i9CT", base_url="https://api.chatanywhere.tech/v1")
        self.client2 = OpenAI(base_url="http://172.18.32.119:8000/v1")
        
        self.MODEL_MAPPING = MODEL_MAPPING
        self.COST_PER_TOKEN = COST_PER_TOKEN
        self.DEFAULT_MESSAGES = DEFAULT_MESSAGES
        self.initialize_session_state()

    def initialize_session_state(self):
        initial_state = {
            'conversations': {  # 存储所有会话
                'default_conversation': {
                    'generated': [],
                    'past': [],
                    'messages': self.DEFAULT_MESSAGES.copy(),
                    'model_name': [],
                    'cost': [],
                    'total_tokens': [],
                    'total_cost': 0.0
                }
            },
            'current_conversation': 'default_conversation',  # 当前会话名称
            'conversation_names': ['default_conversation']   # 会话名称列表
        }
        
        for key, value in initial_state.items():
            st.session_state.setdefault(key, value)

    def get_current_data(self, key):
        return st.session_state['conversations'][st.session_state['current_conversation']].get(key, [])

    def set_current_data(self, key, value):
        st.session_state['conversations'][st.session_state['current_conversation']][key] = value
    
    @st.dialog(("新建会话"))
    def new_conversation(self):
        name = st.text_input("请输入会话名称:")
        if st.button("OK"):
            if name.strip() and name not in st.session_state['conversation_names']:
                # 创建新会话
                st.session_state['conversations'][name] = {
                    'generated': [],
                    'past': [],
                    'messages': self.DEFAULT_MESSAGES.copy(),
                    'model_name': [],
                    'cost': [],
                    'total_tokens': [],
                    'total_cost': 0.0
                }
                st.session_state['current_conversation'] = name
                st.session_state['conversation_names'].append(name)
                st.rerun()

    def switch_conversation(self, name):
        if name in st.session_state['conversations']:
            st.session_state['current_conversation'] = name
            st.rerun()


    def rename_conversation(self, new_name):
        # 这里还要获取之前的名称 然后将名称修改
        if new_name.strip() and new_name != st.session_state['current_conversation']:
            old_name = st.session_state['current_conversation']
            # 更新会话数据
            st.session_state['conversations'][new_name] = st.session_state['conversations'].pop(old_name)
            # 更新名称列表
            index = st.session_state['conversation_names'].index(old_name)
            st.session_state['conversation_names'][index] = new_name
            # 更新当前会话名称
            st.session_state['current_conversation'] = new_name
            st.rerun()
    
    @st.dialog("删除会话")
    def delete_current_conversation(self):
        if len(st.session_state['conversations']) > 1:
            current = st.session_state['current_conversation']
            del st.session_state['conversations'][current]
            st.session_state['conversation_names'].remove(current)
            # 切换到第一个会话
            st.session_state['current_conversation'] = st.session_state['conversation_names'][0]
            st.rerun()
        else:
            st.error("至少保留一个会话", icon="⚠️")

    def clear_conversation(self):
        current_name = st.session_state['current_conversation']
        st.session_state['conversations'][current_name] = {
            'generated': [],
            'past': [],
            'messages': self.DEFAULT_MESSAGES.copy(),
            'model_name': [],
            'cost': [],
            'total_tokens': [],
            'total_cost': 0.0
        }

    def generate_response(self, prompt: str, model_name: str) -> Tuple[str, Any]:
        current_messages = self.get_current_data('messages')
        current_messages.append({'role': 'user', 'content': prompt})

        if 'gpt' in model_name:
            completion = self.client1.chat.completions.create(
                model=model_name,
                messages=current_messages,
                temperature=0,
            )
        else:
            completion = self.client2.chat.completions.create(
                model=model_name,
                messages=current_messages,
                temperature=0,
            )
        
        response = completion.choices[0].message.content
        current_messages.append({'role': 'assistant', 'content': response})
        self.set_current_data('messages', current_messages)
        return response, completion.usage

    def process_user_input(self, user_input: str, model_name: str) -> Tuple[str, Any]:
        output, usage = self.generate_response(user_input, model_name)
        # 更新当前会话数据
        self.set_current_data('past', self.get_current_data('past') + [user_input])
        self.set_current_data('generated', self.get_current_data('generated') + [output])
        self.set_current_data('model_name', self.get_current_data('model_name') + [model_name])
        self.set_current_data('total_tokens', self.get_current_data('total_tokens') + [usage.total_tokens])
        
        cost = self.calculate_cost(model_name, usage)
        self.set_current_data('cost', self.get_current_data('cost') + [cost])
        return output, usage

    # 修改calculate_cost方法更新总成本
    def calculate_cost(self, model_name: str, usage: Any) -> float:
        cost = (usage.prompt_tokens * self.COST_PER_TOKEN[model_name]['prompt'] +
                usage.completion_tokens * self.COST_PER_TOKEN[model_name]['completion'])
        self.set_current_data('total_cost', self.get_current_data('total_cost') + cost)
        return cost

    @staticmethod
    def display_chat_history(response_container: st.container):
        with response_container:
            current_data = st.session_state['conversations'][st.session_state['current_conversation']]
            for user_msg, ai_msg in zip(current_data['past'], current_data['generated']):
                st.chat_message(name='user', avatar='🧑').markdown(user_msg)
                st.chat_message(name='ai', avatar='🤖').markdown(ai_msg)

    # def update_client(self, model_name):
    #     """根据模型名称更新客户端"""
    #     print(f"正在切换模型到: {model_name}")  # 调试日志
    #     if "gpt" in model_name:
    #         self.client = OpenAI(api_key="sk-P3N9W5E4ZbDU7GRwoiHL4tJaFXsliJHBrXAFmHannHs9i9CT", base_url="https://api.chatanywhere.tech/v1")
    #         print(f"已切换到GPT模型: {model_name}")
    #     elif "qwen" in model_name:
    #         self.client = OpenAI(api_key="", base_url="http://172.18.32.119:8000/v1")
    #         print(f"已切换到千问模型: {model_name}")

    def chat_demo(self):
        st.markdown('# 智慧农语', unsafe_allow_html=True)
        # st.markdown('## 输入任意文本开始对话', unsafe_allow_html=True)

        # 添加模型选择回调
        def on_model_change():
            selected_model = st.session_state.model_select_key  # 从session_state获取当前选择
            # self.update_client(selected_model)  # 更新客户端
            st.toast(f"模型已切换至: {selected_model}", icon="✅")

        # 带回调的模型选择组件
        model_name = st.sidebar.selectbox(
            '选择模型:',
            self.MODEL_MAPPING,
            key='model_select_key',
            on_change=on_model_change  # 绑定回调函数
        )
        
        # 初始化客户端（处理首次加载和session重置）
        if 'model_select_key' not in st.session_state:
            st.session_state.model_select_key = model_name
        # 初始化客户端（首次运行或session重置时）
        # if not hasattr(self, 'client') or not self.client:
        #     self.update_client(model_name)

        counter_placeholder = st.sidebar.empty()
        current_cost = self.get_current_data('total_cost')
        counter_placeholder.write(f"当前会话总成本: ${current_cost:.5f}")

        st.sidebar.markdown('---')
        st.sidebar.markdown('## 会话管理')

        # 会话管理按钮
        col1, col2, col3 = st.sidebar.columns([1, 1, 1])
        with col1:
            if st.button("新建"):
                self.new_conversation()
        with col2:
            if st.button("重命名"):
                self.rename_conversation_modal()
        with col3:
            if st.button("删除"):
                self.delete_current_conversation()

        for name in st.session_state['conversation_names']:
            btn_type = "primary" if name == st.session_state['current_conversation'] else "secondary"
            if st.sidebar.button(name, key=f"convo_{name}", type=btn_type):
                self.switch_conversation(name)


        # 会话管理按钮
        col3, col4 = st.sidebar.columns([1, 1])
        with col3:
            current_data = st.session_state['conversations'][st.session_state['current_conversation']]
            # Implement the export functionality (for now it can be a simple download)
            conversation_data = {
                'past': current_data['past'],
                'generated': current_data['generated'],
                'cost': current_data['cost'],
                'total_cost': current_data['total_cost']
            }
            now = datetime.now()
            st.download_button(
                label="导出记录",
                data=str(conversation_data),
                file_name=f"{st.session_state['current_conversation']}_{now:%Y-%m-%d %H.%M}.txt",
                mime="text/txt"
            )
        with col4:
            if st.button('清空对话'):
                self.clear_conversation()

        
        # 用户输入处理
        user_input = st.chat_input(placeholder='请输入消息...', key='input')
        if user_input:
            output, usage = self.process_user_input(user_input, model_name)

        # 显示聊天记录
        self.display_chat_history(st.container())
        counter_placeholder.write(f"当前会话总成本: ${self.get_current_data('total_cost'):.5f}")

    @st.dialog("重命名会话")
    def rename_conversation_modal(self):
        """重命名会话对话框"""
        new_name = st.text_input("请输入新会话名称:", value=st.session_state['current_conversation'])
        if st.button("确认"):
            self.rename_conversation(new_name)

if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")  # Fetch the API key from environment variables
    gpt_chat = GPTChat(api_key)
    gpt_chat.chat_demo()