import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from typing import Tuple, Any
from config import MODEL_MAPPING, COST_PER_TOKEN, DEFAULT_MESSAGES
from conversation import ConversationManager

load_dotenv()

class GPTChat:
    def __init__(self, api_key: str):
        st.set_page_config(page_title='Chat', page_icon='💬')
        self.client = OpenAI(api_key=api_key, base_url="https://api.chatanywhere.tech/v1")
        self.MODEL_MAPPING = MODEL_MAPPING
        self.COST_PER_TOKEN = COST_PER_TOKEN
        self.DEFAULT_MESSAGES = DEFAULT_MESSAGES
        self.conv_manager = ConversationManager()
        self.initialize_session_state()

    def initialize_session_state(self):
        initial_state = {
            'generated': [],
            'past': [],
            'messages': self.DEFAULT_MESSAGES.copy(),
            'model_name': [],
            'cost': [],
            'total_tokens': [],
            'total_cost': 0.0
        }
        for key, value in initial_state.items():
            st.session_state.setdefault(key, value)
        # 初始化会话名称（仅在首次运行时）
        if 'conversation_name' not in st.session_state:
            st.session_state['conversation_name'] = 'default_conversation'

    def reset_conversation(self):
        st.session_state.update({
            'generated': [],
            'past': [],
            'messages': self.DEFAULT_MESSAGES.copy(),
            'model_name': [],
            'cost': [],
            'total_tokens': [],
            'total_cost': 0.0
        })
    
    @st.dialog(("新建会话"))
    def new_conversation(self):
        name = st.text_input("请输入会话名称:")
        if st.button("OK"):
            if name.strip():
                self.reset_conversation()
                st.session_state['conversation_name'] = name
                st.rerun()


    def rename_conversation(self, new_name):
        if new_name.strip():
            st.session_state['conversation_name'] = new_name.strip()

    def delete_conversation(self):
        keys_to_delete = ['generated', 'past', 'messages', 'model_name', 'cost', 'total_tokens', 'total_cost']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]


    def export_conversation(self):
        # Implement the export functionality (for now it can be a simple download)
        conversation_data = {
            'past': st.session_state['past'],
            'generated': st.session_state['generated'],
            'cost': st.session_state['cost'],
            'total_cost': st.session_state['total_cost']
        }
        st.download_button(
            label="Download Conversation",
            data=str(conversation_data),
            file_name=f"{st.session_state['conversation_name']}_conversation.txt",
            mime="text/plain"
        )

    def clear_conversation(self):
        self.reset_conversation()

    def generate_response(self, prompt: str, model_name: str) -> Tuple[str, Any]:
        st.session_state['messages'].append({'role': 'user', 'content': prompt})

        completion = self.client.chat.completions.create(
            model=model_name,
            messages=st.session_state['messages'],
            # TODO 
            # 支持自定义温度
            temperature=0,
        )
        response = completion.choices[0].message.content
        st.session_state['messages'].append({'role': 'assistant', 'content': response})

        return response, completion.usage

    def process_user_input(self, user_input: str, model_name: str) -> Tuple[str, Any]:
        output, usage = self.generate_response(user_input, model_name)
        return output, usage

    def calculate_cost(self, model_name: str, usage: Any) -> float:
        return (usage.prompt_tokens * self.COST_PER_TOKEN[model_name]['prompt'] +
                usage.completion_tokens * self.COST_PER_TOKEN[model_name]['completion'])

    @staticmethod
    def display_chat_history(response_container: st.container):
        with response_container:
            for user_message, ai_message in zip(st.session_state['past'], st.session_state['generated']):
                st.chat_message(name='user', avatar='🧑').markdown(user_message)
                st.chat_message(name='ai', avatar='🤖').markdown(ai_message)

    def chat_demo(self):
        st.markdown('# 急急急', unsafe_allow_html=True)
        st.markdown('## 输入任意文本开始对话', unsafe_allow_html=True)

        model_name = st.sidebar.radio('选择模型:', self.MODEL_MAPPING)
        counter_placeholder = st.sidebar.empty()
        counter_placeholder.write(f"当前会话总成本: ${st.session_state['total_cost']:.5f}")

        st.sidebar.markdown('---')
        st.sidebar.markdown('## 会话管理')

        # 会话管理按钮
        col1, col2 = st.sidebar.columns([1, 1])
        with col1:
            if st.button("新建"):
                self.new_conversation()
        with col2:
            if st.button("重命名"):
                self.rename_conversation_modal()

        # 显示当前会话名称
        st.sidebar.write(f"当前会话: {st.session_state['conversation_name']}")

        # 会话管理按钮
        col3, col4 = st.sidebar.columns([1, 1])
        with col3:
            # 导出和清空按钮
            if st.button('导出记录'):
                self.export_conversation()
        with col4:
            if st.button('清空对话'):
                self.clear_conversation()

        
        # 用户输入处理
        user_input = st.chat_input(placeholder='请输入消息...', key='input')
        if user_input:
            output, usage = self.process_user_input(user_input, model_name)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
            st.session_state['model_name'].append(model_name)
            st.session_state['total_tokens'].append(usage.total_tokens)

            cost = self.calculate_cost(model_name, usage)
            st.session_state['cost'].append(cost)
            st.session_state['total_cost'] += cost

        # 显示聊天记录
        self.display_chat_history(st.container())
        counter_placeholder.write(f"当前会话总成本: ${st.session_state['total_cost']:.5f}")

    @st.dialog("重命名会话")
    def rename_conversation_modal(self):
        """重命名会话对话框"""
        new_name = st.text_input("请输入新会话名称:", value=st.session_state['conversation_name'])
        if st.button("确认"):
            self.rename_conversation(new_name)
            st.rerun()

if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")  # Fetch the API key from environment variables
    gpt_chat = GPTChat(api_key)
    gpt_chat.chat_demo()