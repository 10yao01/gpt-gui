# 项目介绍

**智慧农语**是一款基于人工智能和大数据技术的农业智能助手，旨在为农民、农业从业者以及农业爱好者提供精准的农业知识、种植建议、病虫害防治方案以及市场行情分析。通过自然语言处理技术，用户可以以对话的形式获取专业的农业指导，提升农业生产效率，降低种植风险。

# 使用方法

GPT-GUI 是一个基于 Python 的应用程序，提供了一个图形用户界面（GUI），用于与 OpenAI 的 GPT 模型进行交互。它使用 Streamlit 库构建用户界面，并通过 OpenAI API 生成响应。

## 安装

1. 克隆仓库并进入项目目录：

复制

```
git clone https://github.com/10yao01/gpt-gui.git
cd gpt-gui
```

1. 安装所需的 Python 包：

复制

```
pip install -r requirements.txt
```

## 使用

1. 设置你的`API KEY`和`BASE_URL`

```python
self.client1 = OpenAI(api_key="KEY", base_url="URL")
self.client2 = OpenAI(base_url="URL")
self.client3 = OpenAI(base_url="URL")
```



2. 运行应用程序：

复制

```
python -m streamlit run app.py
```

## 功能

- 支持选择不同的 GPT 模型，设置模型产生回答的温度。
- 新建会话，删除会话，清空会话，重命名会话。
- 导出与 AI 的聊天记录。
- 根据使用的 token 数量计算对话成本。

## 测试

测试文件位于 `tests/` 目录中。您可以使用 pytest 运行测试：

复制

```
`LLaMA-Factory`pytest tests
```

## `LLaMA-Factory`

使用方式参考[LLaMA-Factory微调方式](LLaMA-Factory/README.md)

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](https://license/) 文件。