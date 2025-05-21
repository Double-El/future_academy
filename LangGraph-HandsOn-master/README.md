# LangGraph 핸즈온 튜토리얼

LangGraph를 활용한 에이전트 핸즈온 튜토리얼 입니다.

**참고하면 좋은 자료**

- [LangChain 한국어 튜토리얼🇰🇷](https://wikidocs.net/book/14314)
- [LangChain 한국어 튜토리얼 Github 소스코드](https://github.com/teddylee777/langchain-kr)
- [테디노트 YouTube](https://www.youtube.com/c/@teddynote)
- [테디노트 블로그](https://teddylee777.github.io/)
- [테디노트 YouTube 로 RAG 배우기!](https://teddylee777.notion.site/YouTube-RAG-10a24f35d12980dc8478c750faa752a2?pvs=74)
- [RAG 비법노트](https://fastcampus.co.kr/data_online_teddy)


## 소개
이 프로젝트는 LangGraph를 사용하여 AI 에이전트를 구축하고 실행하는 방법을 보여주는 예제와 가이드를 제공합니다. 

## 설치 방법(Local)

```bash
git clone https://github.com/teddylee777/LangGraph-HandsOn.git
cd LangGraph-HandsOn
pip install -r requirements.txt
```

- [일반 튜토리얼 버전](00-langgraph.ipynb)
- [음성 튜토리얼 버전](00-langgraph-(VoiceTutorial).ipynb)

## Google Colab

- [일반 튜토리얼 버전](https://colab.research.google.com/drive/1ERAveGAEvs8tR2KykSpddslUtOUx4CnF?usp=sharing)

- [음성 튜토리얼 버전](https://colab.research.google.com/drive/1U-cO5Swv2Ae0c10khpuul1J7ARqCJ7Ty?usp=sharing)

## 환경 설정

**OpenAI API Key 설정**
- https://wikidocs.net/233342

**웹 검색을 위한 API 키 발급 주소**
- https://app.tavily.com/

회원 가입 후 API Key를 발급합니다.

프로젝트 루트에 .env_sample 파일을 복사하여 .env 파일을 생성하고 다음과 같이 필요한 환경 변수를 설정하세요.

```bash
# 환경 변수 설정
export OPENAI_API_KEY="your_openai_api_key_here"
export TAVILY_API_KEY="your_tavily_api_key_here"
```

## LangSmith 추적 설정

LangSmith 추적을 활성화하려면 다음 환경 변수를 설정하세요:

```bash
export LANGSMITH_API_KEY="your_langsmith_api_key_here"
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT_NAME="LangGraph Hands-On"
export LANGSMITH_API_URL="https://api.smith.langchain.com"
```

## 사용 방법

`00-langgraph.ipynb` 노트북 파일을 열어 실습을 시작하세요.

## 목차

이 저장소에는 다음과 같은 예제가 포함되어 있습니다.

- **Part 0. 환경 설정**
- **Part 1. 기본 ReAct Agent 구현**
  - 도구 (Tools) 설정
  - 그래프 실행
- **Part 2. 멀티턴 대화를 위한 단기 메모리: checkpointer**
  - MemorySaver
- **Part 3. LangGraph 워크플로우 구현**
  - State 정의
  - 노드(Node) 정의
  - 그래프 생성
- **Part 4. Routing**
  - 그래프 생성
- **Part 5. Fan-out / Fan-in**
  - 일부만 Fan-out 하는 방법
- **Part 6. 대화 기록 요약을 추가하는 방법**
- **Part 7. Human in the Loop**
- **Part 8. Long-Term Memory**

## 의존성

- Python 3.11
- langchain
- langgraph
- jupyter
- openai
- langchain-teddynote

## 라이선스

```
MIT License

Copyright (c) 2025 테디노트

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

----

Happy coding! 🚀

