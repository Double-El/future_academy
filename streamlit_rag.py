import os
import streamlit as st
import pandas as pd
from typing import TypedDict, List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage
from langgraph.graph import StateGraph

# 🔑 OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = "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"

# 📘 상태 정의
class RAGState(TypedDict):
    question: str
    chat_history: List
    answer: str

# 📄 엑셀 → 텍스트
def load_excel_text(uploaded_file):
    df = pd.read_excel(uploaded_file)
    all_text = ""
    for col in df.columns:
        all_text += f"\n\n### {col}:\n"
        all_text += "\n".join([str(val) for val in df[col] if pd.notna(val)])
    return all_text

# 📦 텍스트 → 벡터 저장소
def prepare_vectorstore(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([text])
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_documents(docs, embeddings)
    return vectordb

# 🤖 RAG 노드
def rag_node(state: RAGState) -> RAGState:
    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    for msg in state["chat_history"]:
        memory.chat_memory.add_message(msg)

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=OpenAI(temperature=0),
        retriever=retriever,
        memory=memory,
        return_source_documents=False,
    )
    result = qa_chain.run(state["question"])
    new_history = state["chat_history"] + [
        HumanMessage(content=state["question"]),
        SystemMessage(content=result),
    ]
    return {
        "question": "",
        "answer": result,
        "chat_history": new_history
    }

# 🧠 LangGraph 구축
def build_graph():
    builder = StateGraph(RAGState)
    builder.add_node("RAG", rag_node)
    builder.set_entry_point("RAG")
    builder.set_finish_point("RAG")
    return builder.compile()

# 🚀 Streamlit UI 시작
st.set_page_config(page_title="📊 Excel RAG Chat", layout="wide")
st.title("📊 Excel 기반 멀티턴 RAG 챗봇")

# 📤 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"])

if uploaded_file:
    if "vectorstore" not in st.session_state:
        with st.spinner("📖 엑셀 데이터를 분석 중입니다..."):
            text = load_excel_text(uploaded_file)
            st.session_state.vectorstore = prepare_vectorstore(text)
            st.session_state.graph = build_graph()
            st.session_state.chat_history = []

    # 🔁 사용자 입력
    user_input = st.chat_input("질문을 입력하세요.")
    if user_input:
        rag_state: RAGState = {
            "question": user_input,
            "chat_history": st.session_state.chat_history,
            "answer": ""
        }
        with st.spinner("💡 응답 생성 중..."):
            result_state = st.session_state.graph.invoke(rag_state)
            st.session_state.chat_history = result_state["chat_history"]
            st.session_state.answer = result_state["answer"]

    # 💬 대화 출력
    if "chat_history" in st.session_state:
        for msg in st.session_state.chat_history:
            if isinstance(msg, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(msg.content)
            elif isinstance(msg, SystemMessage):
                with st.chat_message("assistant"):
                    st.markdown(msg.content)
