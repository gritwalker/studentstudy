import streamlit as st
import openai
import requests

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "일반 챗봇"
if "messages" not in st.session_state:
    st.session_state.messages = []

def login_page():
    st.title("로그인")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("로그인"):
        if password == st.secrets.get("APP_PASSWORD"):
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")

def main_app():
    st.sidebar.title("메뉴")
    if st.sidebar.button("일반 챗봇"):
        st.session_state.current_page = "일반 챗봇"

    st.title("일반 챗봇")

    # DeepSeek 클라이언트 초기화
    deepseek_chat_client = openai.OpenAI(
        api_key=st.secrets.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "무엇을 도와드릴까요?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("메시지를 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in deepseek_chat_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if not st.session_state.authenticated:
    login_page()
else:
    main_app()