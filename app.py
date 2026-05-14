import time
import os
import re
from collections import Counter
from datetime import datetime

import streamlit as st
from agent.react_agent import ReactAgent
from utils.config_handler import models_config
from model.factory import get_model_by_name
from utils.path_tool import get_abs_path
# 页面配置
st.set_page_config(page_title="智扫通机器人智能客服", page_icon="🤖", layout="wide")

# 标题
st.title("🤖 智扫通机器人智能客服")
st.divider()

# 侧边栏
with st.sidebar:
    st.header("⚙️ 功能控制")

    # 模型选择
    model_options = {m["name"]: f"{m['display_name']} - {m['description']}"
                     for m in models_config.get("models", [])}
    selected_model = st.selectbox(
        "🧠 选择模型",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0,
    )

    # 如果切换模型，重新创建 agent
    if "current_model" not in st.session_state:
        st.session_state["current_model"] = selected_model

    if st.session_state["current_model"] != selected_model:
        st.session_state["current_model"] = selected_model
        new_chat_model = get_model_by_name(selected_model)
        st.session_state["agent"] = ReactAgent(chat_model=new_chat_model)
        st.rerun()

    st.divider()

    if st.button("🗑️ 清除对话记录", use_container_width=True, type="primary"):
        st.session_state["message"] = []
        st.rerun()

    st.divider()
    st.divider()

    # 日志分析看板
    # 日志分析看板
    with st.expander("📊 数据统计", expanded=False):
        if st.button("🔄 刷新统计", use_container_width=True):
            st.rerun()

        log_dir = get_abs_path("logs")

        tool_counts = Counter()
        success_counts = Counter()
        total_calls = 0
        total_success = 0

        if os.path.isdir(log_dir):
            for log_file in os.listdir(log_dir):
                if log_file.endswith(".log"):
                    with open(os.path.join(log_dir, log_file), "r", encoding="utf-8") as f:
                        for line in f:
                            m = re.search(r'\[tool monitor\]执行工具:(\w+)', line)
                            if m:
                                tool_counts[m.group(1)] += 1
                                total_calls += 1
                            m = re.search(r'\[tool monitor\]工具(\w+)调用成功', line)
                            if m:
                                success_counts[m.group(1)] += 1
                                total_success += 1

        col1, col2 = st.columns(2)
        col1.metric("🛠️ 总调用", total_calls)
        col2.metric("✅ 成功率", f"{total_success / total_calls * 100:.1f}%" if total_calls > 0 else "0%")

        if tool_counts:
            st.caption("📌 工具调用排行")
            for tool_name, count in tool_counts.most_common():
                rate = success_counts.get(tool_name, 0) / count * 100
                st.text(f"  {tool_name}: {count}次 ({rate:.0f}%)")

    st.divider()
    st.caption("💡 提示：输入您关于扫地/扫拖机器人的任何问题，"
               "例如选购建议、故障排除、使用技巧等。")
    st.caption("📋 也可以说「生成我的使用报告」来查看个性化报告。")
    st.caption("💡 提示：输入您关于扫地/扫拖机器人的任何问题，"
               "例如选购建议、故障排除、使用技巧等。")
    st.caption("📋 也可以说「生成我的使用报告」来查看个性化报告。")

# 初始化
if "agent" not in st.session_state:
    default_model = models_config.get("default_model", "qwen3-max")
    new_chat_model = get_model_by_name(default_model)
    st.session_state["agent"] = ReactAgent(chat_model=new_chat_model)

if "message" not in st.session_state:
    st.session_state["message"] = []

# 遍历显示历史消息
for message in st.session_state["message"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 用户输入
prompt = st.chat_input("请输入您关于扫地机器人的问题...")

if prompt:
    # 显示用户消息
    with st.chat_message("user"):
        st.write(prompt)

    # 先取历史（不含当前这个问题），再存当前问题
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["message"]
    ]
    st.session_state["message"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🤔 智能客服思考中..."):
            try:
                res_stream = st.session_state["agent"].execute_stream(prompt, history)

                # 遍历生成器拿到完整回答
                full_response = ""
                for chunk in res_stream:
                    full_response = chunk

                # 逐字模拟打字机效果
                display_text = ""
                text_area = st.empty()
                for char in full_response:
                    display_text += char
                    text_area.write(display_text)
                    time.sleep(0.01)

                # 保存完整回答
                if full_response.strip():
                    st.session_state["message"].append({
                        "role": "assistant",
                        "content": full_response.strip()
                    })
                else:
                    st.session_state["message"].append({
                        "role": "assistant",
                        "content": "抱歉，我没有获取到有效的回复，请重试。"
                    })

            except Exception as e:
                error_msg = f"抱歉，处理您的请求时出现异常：{str(e)}"
                st.error(error_msg)
                st.session_state["message"].append({
                    "role": "assistant",
                    "content": error_msg
                })
