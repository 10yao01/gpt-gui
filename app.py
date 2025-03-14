import os
import streamlit as st
from openai import OpenAI
from typing import Tuple, Any
from config import MODEL_MAPPING, COST_PER_TOKEN, DEFAULT_MESSAGES
from datetime import datetime

class GPTChat:
    def __init__(self):
        # 设置页面标题和图标
        st.set_page_config(page_title='Chat', page_icon='💬')
        # print("key: {}".format(api_key))
        # 创建三个OpenAI客户端，分别使用不同的API密钥和基础URL
        self.client1 = OpenAI(api_key="KEY", base_url="URL")
        self.client2 = OpenAI(base_url="URL")
        self.client3 = OpenAI(base_url="URL")

        
        # 定义模型映射、每令牌成本和默认消息
        self.MODEL_MAPPING = MODEL_MAPPING
        self.COST_PER_TOKEN = COST_PER_TOKEN
        self.DEFAULT_MESSAGES = DEFAULT_MESSAGES
        # 初始化会话状态
        self.initialize_session_state()

    def initialize_session_state(self):
        # 初始化会话状态
        initial_state = {
            'conversations': {  # 存储所有会话
                'default_conversation': {
                    'generated': [],  # 存储生成的消息
                    'past': [],  # 存储过去的消息
                    'messages': self.DEFAULT_MESSAGES.copy(),  # 默认消息
                    'model_name': [],  # 模型名称
                    'cost': [],  # 成本
                    'total_tokens': [],  # 总tokens
                    'total_cost': 0.0  # 总成本
                }
            },
            'current_conversation': 'default_conversation',  # 当前会话名称
            'conversation_names': ['default_conversation']   # 会话名称列表
        }
        
        # 将初始状态设置到session_state中
        for key, value in initial_state.items():
            st.session_state.setdefault(key, value)

    # 获取当前对话中的数据
    def get_current_data(self, key):
        # 从session_state中获取当前对话的数据
        return st.session_state['conversations'][st.session_state['current_conversation']].get(key, [])

    # 设置当前对话的键值对
    def set_current_data(self, key, value):
        # 在session_state中，将当前对话的键值对设置为传入的键和值
        st.session_state['conversations'][st.session_state['current_conversation']][key] = value
    
    @st.dialog(("新建会话"))
    def new_conversation(self):
        # 获取用户输入的会话名称
        name = st.text_input("请输入会话名称:")
        # 如果用户点击了OK按钮
        if st.button("OK"):
            # 如果会话名称不为空且会话名称不在会话列表中
            if name.strip() and name not in st.session_state['conversation_names']:
                # 创建新会话
                st.session_state['conversations'][name] = {
                    'generated': [],  # 生成的内容
                    'past': [],  # 过去的内容
                    'messages': self.DEFAULT_MESSAGES.copy(),  # 默认消息
                    'model_name': [],  # 模型名称
                    'cost': [],  # 成本
                    'total_tokens': [],  # 总tokens
                    'total_cost': 0.0  # 总成本
                }
                # 设置当前会话为新建的会话
                st.session_state['current_conversation'] = name
                # 将会话名称添加到会话列表中
                st.session_state['conversation_names'].append(name)
                # 重新运行程序
                st.rerun()

    def switch_conversation(self, name):
        # 判断name是否在st.session_state['conversations']中
        if name in st.session_state['conversations']:
            # 将st.session_state['current_conversation']设置为name
            st.session_state['current_conversation'] = name
            # 重新运行程序
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
        # 如果会话列表长度大于1，则删除当前会话
        if len(st.session_state['conversations']) > 1:
            current = st.session_state['current_conversation']
            del st.session_state['conversations'][current]
            st.session_state['conversation_names'].remove(current)
            # 切换到第一个会话
            st.session_state['current_conversation'] = st.session_state['conversation_names'][0]
            st.rerun()
        else:
            # 否则，显示错误信息
            st.error("至少保留一个会话", icon="⚠️")

    def clear_conversation(self):
        # 获取当前对话的名称
        current_name = st.session_state['current_conversation']
        # 将当前对话的名称对应的对话内容清空，重新赋值为默认值
        st.session_state['conversations'][current_name] = {
            'generated': [],  # 生成的内容
            'past': [],  # 过去的内容
            'messages': self.DEFAULT_MESSAGES.copy(),  # 默认消息
            'model_name': [],  # 模型名称
            'cost': [],  # 成本
            'total_tokens': [],  # 总tokens
            'total_cost': 0.0  # 总成本
        }

    def generate_response(self, prompt: str, model_name: str, temperature: float) -> Tuple[str, Any]:
        # 获取当前的消息数据
        current_messages = self.get_current_data('messages')
        # 将用户输入的消息添加到当前的消息数据中
        current_messages.append({'role': 'user', 'content': prompt})

        # 根据模型名称选择不同的客户端
        if 'gpt' in model_name:
            # 使用client1生成回复
            completion = self.client1.chat.completions.create(
                model=model_name,
                messages=current_messages,
                temperature=temperature,
            )
        elif 'sft' in model_name:
            # 使用client2生成回复
            completion = self.client2.chat.completions.create(
                model=model_name,
                messages=current_messages,
                temperature=temperature,
            )
        else:
            # 使用client3生成回复
            completion = self.client3.chat.completions.create(
                model=model_name,
                messages=current_messages,
                temperature=temperature,
            )
        
        # 获取生成的回复
        response = completion.choices[0].message.content
        # 将生成的回复添加到当前的消息数据中
        current_messages.append({'role': 'assistant', 'content': response})
        # 更新当前的消息数据
        self.set_current_data('messages', current_messages)
        # 返回生成的回复和使用的资源
        return response, completion.usage

    def process_user_input(self, user_input: str, model_name: str, temperature: float) -> Tuple[str, Any]:
        # 生成模型响应
        output, usage = self.generate_response(user_input, model_name, temperature)
        # 更新当前会话数据
        self.set_current_data('past', self.get_current_data('past') + [user_input])
        self.set_current_data('generated', self.get_current_data('generated') + [output])
        self.set_current_data('model_name', self.get_current_data('model_name') + [model_name])
        self.set_current_data('total_tokens', self.get_current_data('total_tokens') + [usage.total_tokens])
        
        # 计算模型费用
        cost = self.calculate_cost(model_name, usage)
        self.set_current_data('cost', self.get_current_data('cost') + [cost])
        return output, usage

    # 修改calculate_cost方法更新总成本
    def calculate_cost(self, model_name: str, usage: Any) -> float:
        # 计算模型使用成本
        cost = (usage.prompt_tokens * self.COST_PER_TOKEN[model_name]['prompt'] +
                usage.completion_tokens * self.COST_PER_TOKEN[model_name]['completion'])
        # 将当前成本加入总成本
        self.set_current_data('total_cost', self.get_current_data('total_cost') + cost)
        # 返回当前成本
        return cost

    @staticmethod
    # 定义一个函数，用于显示聊天历史
    def display_chat_history(response_container: st.container):
        # 使用with语句，将response_container作为上下文管理器
        with response_container:
            # 获取当前会话的数据
            current_data = st.session_state['conversations'][st.session_state['current_conversation']]
            # 遍历当前会话的过去和生成的消息
            for user_msg, ai_msg in zip(current_data['past'], current_data['generated']):
                # 显示用户消息
                st.chat_message(name='user', avatar='🧑').markdown(user_msg)
                # 显示AI消息
                st.chat_message(name='ai', avatar='🤖').markdown(ai_msg)

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

        # counter_placeholder = st.sidebar.empty()
        # current_cost = self.get_current_data('total_cost')
        # counter_placeholder.write(f"当前会话总成本: ${current_cost:.5f}")

        temperature = st.sidebar.slider("温度", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

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

        
        # 用户输入处理
        user_input = st.chat_input(placeholder='请输入消息...', key='input')
        if user_input:
            output, usage = self.process_user_input(user_input, model_name, temperature)

        
        # 会话管理按钮
        col3, col4 = st.sidebar.columns([1, 1])
        with col3:
            if st.button('清空对话'):
                self.clear_conversation()
        with col4:
            current_data = st.session_state['conversations'][st.session_state['current_conversation']]
            conversation_data = {
                'past': current_data['past'],
                'generated': current_data['generated'],
                'cost': current_data['cost'],
                'total_cost': current_data['total_cost']
            }
            now = datetime.now()
            st.download_button(
                label="下载记录",
                icon=":material/download:",
                data=str(conversation_data),
                file_name=f"{st.session_state['current_conversation']}_{now:%Y-%m-%d %H.%M}.txt",
                mime="text/txt"
            )

        # 显示聊天记录
        self.display_chat_history(st.container())
        # counter_placeholder.write(f"当前会话总成本: ${self.get_current_data('total_cost'):.5f}")

    @st.dialog("重命名会话")
    def rename_conversation_modal(self):
        """重命名会话对话框"""
        # 输入新会话名称
        new_name = st.text_input("请输入新会话名称:", value=st.session_state['current_conversation'])
        # 点击确认按钮后，调用rename_conversation方法，传入新会话名称
        if st.button("确认"):
            self.rename_conversation(new_name)

if __name__ == '__main__':
    gpt_chat = GPTChat()
    gpt_chat.chat_demo()