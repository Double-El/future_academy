# XAI 대출 관리 시스템 (XAI Loan Management System)

설명 가능한 AI(Explainable AI) 기반 대출 심사 대시보드입니다. 고객의 대출 신청에 대한 결정 사유를 투명하고 이해하기 쉽게 설명하는 시스템입니다.

## 주요 기능 (Features)

### 대시보드 (Dashboard)
- **고객 목록**: 모든 대출 신청자의 기본 정보 표시
- **실시간 통계**: 승인/거절 현황 실시간 업데이트
- **위험도 분석**: 부채 대비 소득 비율, 신용 점수, 고용 안정성 분석
- **반응형 디자인**: 모든 화면 크기에 최적화

###  XAI 챗봇 (XAI Chatbot)
- **투명한 설명**: AI가 대출 결정 사유를 자연어로 설명
- **실시간 대화**: 고객별 맞춤형 상담 서비스
- **건설적 제안**: 향후 개선 방안 제시

###  위험도 분석 (Risk Analysis)
- **부채 대비 소득 비율**: 상환 능력 평가
- **신용 점수**: 과거 상환 이력 분석
- **고용 안정성**: 소득 안정성 평가

## 설치 및 실행 (Installation & Setup)

### 1. 저장소 클론
```bash
git clone <repository-url>
cd XAI_v3
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
1. `env_example.txt` 파일을 `.env`로 복사
```bash
cp env_example.txt .env
```

2. `.env` 파일을 편집하여 OpenAI API 키 설정
```bash
# OpenAI API 키를 발급받아 설정
OPENAI_API_KEY=your_actual_api_key_here
```

### 5. 애플리케이션 실행
```bash
# 방법 1: 자동 설정 확인 및 실행 (권장)
python start.py

# 방법 2: 직접 실행
python app.py
```

### 6. 브라우저에서 접속
```
http://localhost:5000
```

## 사용법 (Usage)

### 1. 고객 선택
- 왼쪽 패널의 고객 목록에서 원하는 고객을 클릭
- 고객의 상세 정보와 위험도 분석이 표시됩니다

### 2. XAI 챗봇 사용
- 고객을 선택하면 오른쪽 패널의 챗봇이 활성화됩니다
- 대출 결정 사유에 대해 질문하세요
- AI가 투명하고 이해하기 쉽게 설명해드립니다

### 3. 위험도 분석 확인
- 고객 상세 정보 하단에서 위험도 분석을 확인
- 각 지표별 위험 수준과 설명을 제공합니다

## 기술 스택 (Tech Stack)

### Backend
- **Flask**: Python 웹 프레임워크
- **OpenAI API**: GPT-3.5-turbo 모델 사용
- **Flask-CORS**: 크로스 오리진 리소스 공유

### Frontend
- **Bootstrap 5**: 반응형 UI 프레임워크
- **Font Awesome**: 아이콘 라이브러리
- **Vanilla JavaScript**: ES6+ 클래스 기반 구조

### 데이터
- **Sample Data**: 실제 대출 신청 데이터 시뮬레이션
- **Risk Metrics**: 부채 대비 소득 비율, 신용 점수 등

## API 엔드포인트 (API Endpoints)

### 고객 정보
- `GET /api/all-customers`: 모든 고객 정보 조회
- `GET /api/loan-status/<customer_id>`: 특정 고객 대출 상태 조회

### 위험도 분석
- `GET /api/risk-analysis/<customer_id>`: 고객별 위험도 분석

### XAI 챗봇
- `POST /api/chat`: AI 기반 대출 설명 생성

## 프로젝트 구조 (Project Structure)

```
XAI_v2/
├── app.py                 # Flask 메인 애플리케이션
├── start.py              # 자동 설정 확인 및 실행 스크립트
├── requirements.txt       # Python 의존성
├── env_example.txt       # 환경 변수 예시
├── README.md             # 프로젝트 문서
├── templates/
│   └── dashboard.html    # 메인 대시보드 템플릿
└── static/
    ├── css/
    │   └── custom.css    # 추가 스타일링
    └── js/
        └── dashboard.js  # 대시보드 JavaScript 로직
```

## 환경 요구사항 (Requirements)

- Python 3.8+
- OpenAI API 키
- 웹 브라우저 (Chrome, Firefox, Safari, Edge)

## 라이선스 (License)

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여 (Contributing)

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

