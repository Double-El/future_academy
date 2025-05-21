from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_anthropic import ChatAnthropic
import asyncio
import sys
import os

async def main():
    # Anthropic의 Claude 모델 초기화
    model = ChatAnthropic(
        model_name="claude-3-7-sonnet-latest", 
        temperature=0, 
        max_tokens=20000
    )

    # Python 인터프리터 경로 설정
    # 방법 1: raw string 사용
    python_path = r"C:\Users\User\AppData\Local\Microsoft\WindowsApps\python.exe"
    # 또는 방법 2: forward slash 사용
    # python_path = "C:/Users/User/AppData/Local/Microsoft/WindowsApps/python.exe"
    # 또는 방법 3: double backslash 사용
    # python_path = "C:\\Users\\User\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe"

    # MCP 서버 프로세스 생성
    process = await asyncio.create_subprocess_exec(
        python_path,
        "mcp_server_local.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # StdIO 클라이언트를 사용하여 서버와 통신
    async with stdio_client(StdioServerParameters(
        command=python_path,
        args=["mcp_server_local.py"]
    )) as (read, write):
        # 클라이언트 세션 생성
        async with ClientSession(read, write) as session:
            # 연결 초기화
            await session.initialize()

            # MCP 도구 로드
            tools = await load_mcp_tools(session)
            print("Loaded tools:", tools)

            # 에이전트 생성
            agent = create_react_agent(model, tools)

            # 에이전트 응답 스트리밍
            async for chunk in agent.astream({"messages": "서울의 날씨는 어떠니?"}):
                print(chunk)

    # 프로세스 종료
    process.terminate()
    await process.wait()

if __name__ == "__main__":
    asyncio.run(main()) 