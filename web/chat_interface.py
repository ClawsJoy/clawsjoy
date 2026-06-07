#!/usr/bin/env python3
"""Chat Agent - 语音交互 + 聊天训练界面"""

import base64
import json
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# 语音识别（需要安装: pip install speechrecognition pyaudio）
try:
    import speech_recognition as sr

    SPEECH_AVAILABLE = True
except:
    SPEECH_AVAILABLE = False

st.set_page_config(page_title="ClawsJoy Chat - 智能对话", page_icon="💬", layout="wide")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "training_data" not in st.session_state:
    st.session_state.training_data = []

# 侧边栏 - 训练面板
with st.sidebar:
    st.title("🎯 聊天训练")
    st.markdown("---")

    # 训练数据收集
    st.subheader("📝 添加训练数据")
    with st.form("training_form"):
        user_input = st.text_area("用户输入", height=80)
        expected_response = st.text_area("期望回复", height=80)
        submitted = st.form_submit_button("💾 保存训练数据")

        if submitted and user_input and expected_response:
            st.session_state.training_data.append(
                {
                    "input": user_input,
                    "output": expected_response,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            st.success("训练数据已保存!")

    st.markdown("---")

    # 训练数据统计
    st.subheader("📊 训练统计")
    st.metric("训练样本数", len(st.session_state.training_data))

    # 导出/导入
    if st.button("📤 导出训练数据"):
        import json

        json_str = json.dumps(st.session_state.training_data, ensure_ascii=False)
        st.download_button("下载", json_str, file_name="training_data.json")

    st.markdown("---")
    st.caption(f"会话ID: {hash(str(st.session_state))}")

# 主界面 - 聊天区域
st.title("🤖 ClawsJoy 智能对话助手")

# 语音输入按钮（右上角）
col1, col2, col3 = st.columns([6, 1, 1])
with col2:
    if SPEECH_AVAILABLE and st.button("🎤 语音输入"):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("正在聆听...")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language="zh-CN")
                st.session_state.voice_input = text
                st.success(f"识别: {text}")
            except:
                st.error("无法识别语音")

with col3:
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

# 聊天历史显示
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])
                if "feedback" not in msg:
                    col1, col2, col3 = st.columns([1, 1, 8])
                    with col1:
                        if st.button("👍", key=f"like_{msg['id']}"):
                            msg["feedback"] = "good"
                            st.success("感谢反馈!")
                    with col2:
                        if st.button("👎", key=f"dislike_{msg['id']}"):
                            msg["feedback"] = "bad"
                            st.warning("已记录，会改进!")

# 输入区域
input_col1, input_col2 = st.columns([6, 1])
with input_col1:
    user_input = st.chat_input("输入消息...", key="chat_input")
with input_col2:
    if st.session_state.get("voice_input"):
        user_input = st.session_state.voice_input
        del st.session_state.voice_input

if user_input:
    # 添加用户消息
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
            "id": len(st.session_state.messages),
            "timestamp": datetime.now().isoformat(),
        }
    )

    # 调用后端API
    with st.spinner("思考中..."):
        try:
            # 检查是否有匹配的训练数据
            response = None
            for train in st.session_state.training_data:
                if train["input"] in user_input:
                    response = train["output"]
                    break

            if not response:
                # 调用你的chat_agent API
                resp = requests.post(
                    "http://localhost:5000/api/v5/chat",
                    json={"message": user_input, "user_id": "web_user"},
                )
                if resp.status_code == 200:
                    response = resp.json().get("response", "抱歉，我无法回答")
                else:
                    response = "服务暂时不可用"

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "id": len(st.session_state.messages),
                }
            )
            st.rerun()
        except Exception as e:
            st.error(f"错误: {e}")

# 训练建议
if len(st.session_state.messages) > 5 and len(st.session_state.training_data) < 10:
    st.info("💡 提示: 在侧边栏添加训练数据可以提升对话质量!")
