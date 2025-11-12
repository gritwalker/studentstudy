import streamlit as st
import openai
import requests

SYSTEM_PROMPTS = {
    "일반 챗봇": "당신은 친절한 AI 어시스턴트입니다. 질문에 대해 자세하고 정확하게 답변해주세요.",
    "국어 챗봇": "당신은 국어 전문가입니다. 한국어 문법, 맞춤법, 어휘, 문학 등에 대해 자세하고 정확하게 답변해주세요.",
    "영어 챗봇": "You are an English expert. Please answer questions about English grammar, spelling, vocabulary, literature, etc., in detail and accurately.",
    "영어 RAG 챗봇": "You are an English expert who answers questions based on provided documents. Please answer questions about English grammar, spelling, vocabulary, literature, etc., in detail and accurately, referencing the provided context.",
    "국어 RAG 챗봇": "당신은 제공된 문서를 기반으로 질문에 답변하는 국어 전문가입니다. 한국어 문법, 맞춤법, 어휘, 문학 등에 대해 제공된 문맥을 참조하여 자세하고 정확하게 답변해주세요."
}

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chatbot_mode" not in st.session_state:
    st.session_state.chatbot_mode = "일반 챗봇"
if "general_chatbot_messages" not in st.session_state:
    st.session_state.general_chatbot_messages = []
if "korean_chatbot_messages" not in st.session_state:
    st.session_state.korean_chatbot_messages = []
if "english_chatbot_messages" not in st.session_state:
    st.session_state.english_chatbot_messages = []
if "english_rag_chatbot_messages" not in st.session_state:
    st.session_state.english_rag_chatbot_messages = []
if "korean_rag_chatbot_messages" not in st.session_state:
    st.session_state.korean_rag_chatbot_messages = []

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
    st.sidebar.title("챗봇 모드 선택")

    modes = ["일반 챗봇", "국어 챗봇", "영어 챗봇", "영어 RAG 챗봇", "국어 RAG 챗봇"]
    for mode in modes:
        if st.sidebar.button(mode):
            st.session_state.chatbot_mode = mode

    st.title(st.session_state.chatbot_mode)

    # 현재 챗봇 모드에 맞는 메시지 리스트 선택
    if st.session_state.chatbot_mode == "일반 챗봇":
        messages = st.session_state.general_chatbot_messages
    elif st.session_state.chatbot_mode == "국어 챗봇":
        messages = st.session_state.korean_chatbot_messages
    elif st.session_state.chatbot_mode == "영어 챗봇":
        messages = st.session_state.english_chatbot_messages
    elif st.session_state.chatbot_mode == "영어 RAG 챗봇":
        messages = st.session_state.english_rag_chatbot_messages
    elif st.session_state.chatbot_mode == "국어 RAG 챗봇":
        messages = st.session_state.korean_rag_chatbot_messages
    else:
        messages = st.session_state.general_chatbot_messages # 기본값

    # DeepSeek 클라이언트 초기화
    deepseek_chat_client = openai.OpenAI(
        api_key=st.secrets.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1"
    )

    if not messages:
        messages.append({"role": "assistant", "content": "무엇을 도와드릴까요?"})

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("메시지를 입력하세요"):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 시스템 프롬프트 추가
            system_message = {"role": "system", "content": SYSTEM_PROMPTS[st.session_state.chatbot_mode]}
            chat_messages = [system_message] + messages

            for response in deepseek_chat_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": m["role"], "content": m["content"]} for m in chat_messages],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        messages.append({"role": "assistant", "content": full_response})

if not st.session_state.authenticated:
    login_page()
else:
    main_app()