import time

import streamlit as st


def build_agent():
    from agent.react_agent import ReactAgent

    return ReactAgent()


st.set_page_config(page_title="长期记忆个人助理", layout="centered")
st.title("长期记忆个人助理")
st.caption("结合长期记忆、个人资料库与本地知识检索的 ReAct Agent Demo")
st.divider()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = "default"

if "message" not in st.session_state:
    st.session_state["message"] = []

if "agent" not in st.session_state:
    try:
        st.session_state["agent"] = build_agent()
    except Exception as exc:
        st.error(f"初始化失败：{exc}")
        st.info("请先配置模型 API Key，并确认 data 目录下已准备好知识库资料。")
        st.stop()

with st.sidebar:
    st.subheader("会话控制")
    if st.button("清空当前对话", use_container_width=True):
        st.session_state["message"] = []
        st.session_state["session_id"] = "default"
        st.rerun()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input("请输入问题，例如：根据我的项目资料，给我当前阶段的推进建议")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})
    response_messages = []

    with st.spinner("正在整理资料并生成回复..."):
        res_stream = st.session_state["agent"].execute_stream(prompt, session_id=st.session_state["session_id"])

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                for char in chunk:
                    time.sleep(0.005)
                    yield char

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        st.session_state["message"].append({"role": "assistant", "content": "".join(response_messages).strip()})
        st.rerun()
