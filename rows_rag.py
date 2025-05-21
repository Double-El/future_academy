import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph, StateGraph
from langchain_core.tools import tool
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()

# --- Define the state class ---
class AgentState:
    def __init__(self, messages=None, current_row=0, df=None, file_path=None, should_stop=False, step_count=0):
        self.messages = messages if messages else []
        self.current_row = current_row
        self.df = df
        self.file_path = file_path
        self.should_stop = should_stop
        self.step_count = step_count

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    @classmethod
    def from_dict(cls, state_dict):
        return cls(
            messages=state_dict.get("messages", []),
            current_row=state_dict.get("current_row", 0),
            df=state_dict.get("df", None),
            file_path=state_dict.get("file_path", None),
            should_stop=state_dict.get("should_stop", False),
            step_count=state_dict.get("step_count", 0)
        )

    def to_dict(self):
        return {
            "messages": self.messages,
            "current_row": self.current_row,
            "df": self.df,
            "file_path": self.file_path,
            "should_stop": self.should_stop,
            "step_count": self.step_count
        }

# --- Define tools ---
@tool
def get_current_row(state: AgentState) -> str:
    """Retrieves the current row from the Excel file.
    
    Args:
        state (AgentState): The current state containing the DataFrame and row index.
        
    Returns:
        str: The current row as a string, or a message if no file is loaded or end of file is reached.
    """
    if state.df is None:
        return "No Excel file loaded yet."
    if state.current_row >= len(state.df):
        return "End of file reached."
    return state.df.iloc[state.current_row].to_string()

@tool
def move_to_next_row(state: AgentState) -> str:
    """Moves to the next row in the Excel file.
    
    Args:
        state (AgentState): The current state containing the DataFrame and row index.
        
    Returns:
        str: A message indicating the current row number or if the end of file is reached.
    """
    if state.df is None:
        return "No Excel file loaded yet."
    state.current_row += 1
    if state.current_row >= len(state.df):
        return "End of file reached."
    return f"Moved to row {state.current_row + 1}"

# --- Create the workflow ---
def create_workflow():
    llm = ChatOpenAI(temperature=0.1)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant helping to analyze Excel data row by row. "
                   "엑셀 파일 안에 있는 각 열마다 인물 데이터가 있어. episode 컬럼까지 포함해서 답변해줘. "
                   "Each row contains information about each individual in a bank, including profiles and episodes. "
                   "If you need to know more about the individual, you can make it up. "
                   "Use the tools provided to interact with the data. "
                   "When you are done with the analysis, say 'end' to stop the conversation."
                   "Whenever you answer a question, make sure to search data in the given excel file."
                   "업로드된 complete data에 기반하여 한글로 답변해줘."),
        ("placeholder", "{messages}"),
    ])

    workflow = StateGraph(dict)  # 👈 use dict as state type

    def agent(state_dict):
        state = AgentState.from_dict(state_dict)

        messages = [{"role": msg["role"], "content": msg["content"]} for msg in state.messages]
        response = (prompt | llm).invoke({"messages": messages})

        state.add_message("assistant", response.content)
        state.step_count += 1
        state.should_stop = (
            "end" in response.content.lower()
            or "stop" in response.content.lower()
            or state.step_count >= 20
        )

        return state.to_dict()

    def end(state_dict):
        state = AgentState.from_dict(state_dict)
        return state.to_dict()

    def should_continue(state_dict):
        return not state_dict.get("should_stop", False)

    workflow.add_node("agent", agent)
    workflow.add_node("end", end)

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            True: "agent",
            False: "end"
        }
    )

    workflow.set_entry_point("agent")
    return workflow.compile()

# --- Streamlit app ---
def main():
    st.title("Excel Row Analysis with LangGraph")

    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])

    if uploaded_file is not None:
        if 'uploaded_filename' not in st.session_state or st.session_state.uploaded_filename != uploaded_file.name:
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.state = AgentState()
            st.session_state.state.df = pd.read_excel(uploaded_file)
            st.session_state.workflow = create_workflow()

        st.write("Complete Data:")
        st.dataframe(st.session_state.state.df)

        if st.session_state.state.current_row < len(st.session_state.state.df):
            st.write("Current Row (Highlighted):")
            current_row = st.session_state.state.df.iloc[st.session_state.state.current_row]
            st.dataframe(current_row.to_frame().T)

        user_input = st.text_input("Ask about the current row or request to move to the next row:")

        if user_input:
            st.session_state.state.add_message("user", user_input)

            result = st.session_state.workflow.invoke({
                "messages": st.session_state.state.messages,
                "current_row": st.session_state.state.current_row,
                "df": st.session_state.state.df,
                "file_path": st.session_state.state.file_path,
                "should_stop": st.session_state.state.should_stop,
                "step_count": st.session_state.state.step_count
            })

            st.session_state.state.messages = result["messages"]
            st.session_state.state.current_row = result["current_row"]
            st.session_state.state.df = result["df"]
            st.session_state.state.file_path = result["file_path"]
            st.session_state.state.should_stop = result["should_stop"]
            st.session_state.state.step_count = result["step_count"]

            for message in st.session_state.state.messages:
                if message["role"] == "user":
                    st.write(f"🧑‍💬 User: {message['content']}")
                else:
                    st.write(f"🤖 Assistant: {message['content']}")

if __name__ == "__main__":
    main()
