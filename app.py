import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import time
import psutil
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Correctly initialize the OpenAI client
# Make sure your OPENAI_API_KEY is set in your .env file
try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

# 샘플 고객 데이터 (대출 결과와 사유 추가)
CUSTOMERS = [
    {"id": "SH001", "name": "양명민", "grade": "1등급", "score": 1, "income": 8000, "debt_ratio": 35, "late": "없음", "loan_count": 1, "job": "정규직", "residence": "자가", "collateral": "없음", "result": "승인", "reason": ["높은 신용등급", "안정적인 소득", "낮은 부채비율"]},
    {"id": "SH002", "name": "김신한", "grade": "5등급", "score": 5, "income": 3200, "debt_ratio": 78, "late": "1회(30일)", "loan_count": 2, "job": "계약직", "residence": "월세", "collateral": "없음", "result": "거절", "reason": ["높은 부채비율", "연체이력", "불안정한 고용"]},
    {"id": "SH003", "name": "이신한", "grade": "2등급", "score": 2, "income": 6000, "debt_ratio": 42, "late": "없음", "loan_count": 1, "job": "공무원", "residence": "전세", "collateral": "있음", "result": "승인", "reason": ["안정적인 직업", "담보제공", "양호한 신용이력"]},
    {"id": "SH004", "name": "박신한", "grade": "4등급", "score": 4, "income": 4200, "debt_ratio": 65, "late": "2회(10일, 15일)", "loan_count": 3, "job": "자영업", "residence": "자가", "collateral": "없음", "result": "조건부승인", "reason": ["다중 연체이력", "높은 부채비율", "자영업 위험"]},
    {"id": "SH005", "name": "정신한", "grade": "3등급", "score": 3, "income": 5500, "debt_ratio": 50, "late": "없음", "loan_count": 2, "job": "정규직", "residence": "월세", "collateral": "있음", "result": "승인", "reason": ["적정 소득수준", "담보제공", "양호한 신용이력"]},
    {"id": "SH006", "name": "강신한", "grade": "7등급", "score": 7, "income": 2800, "debt_ratio": 90, "late": "3회(연속)", "loan_count": 4, "job": "아르바이트", "residence": "월세", "collateral": "없음", "result": "거절", "reason": ["최저 신용등급", "연속 연체이력", "불안정한 소득"]},
    {"id": "SH007", "name": "조신한", "grade": "2등급", "score": 2, "income": 7500, "debt_ratio": 30, "late": "없음", "loan_count": 1, "job": "정규직", "residence": "전세", "collateral": "없음", "result": "승인", "reason": ["높은 소득", "낮은 부채비율", "우수한 신용등급"]},
    {"id": "SH008", "name": "윤신한", "grade": "6등급", "score": 6, "income": 3000, "debt_ratio": 85, "late": "2회(연체)", "loan_count": 3, "job": "계약직", "residence": "월세", "collateral": "없음", "result": "거절", "reason": ["높은 부채비율", "연체이력", "불안정한 고용"]},
    {"id": "SH009", "name": "최신한", "grade": "1등급", "score": 1, "income": 9000, "debt_ratio": 28, "late": "없음", "loan_count": 0, "job": "대기업", "residence": "자가", "collateral": "있음", "result": "승인", "reason": ["최고 신용등급", "높은 소득", "담보제공"]},
    {"id": "SH010", "name": "장신한", "grade": "3등급", "score": 3, "income": 4800, "debt_ratio": 55, "late": "없음", "loan_count": 2, "job": "정규직", "residence": "전세", "collateral": "없음", "result": "조건부승인", "reason": ["적정 소득수준", "양호한 신용이력", "다소 높은 부채비율"]}
]

server_start_time = time.time()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content response for favicon

@app.route('/api/all-customers')
def get_all_customers():
    return jsonify(CUSTOMERS)

@app.route('/api/dashboard-stats')
def get_dashboard_stats():
    """대시보드 요약 통계"""
    df = pd.DataFrame(CUSTOMERS)
    
    total_customers = len(df)
    approved_count = len(df[df['result'] == '승인'])
    rejected_count = len(df[df['result'] == '거절'])
    conditional_count = len(df[df['result'] == '조건부승인'])
    
    approval_rate = (approved_count / total_customers) * 100
    avg_income = df['income'].mean()
    avg_debt_ratio = df['debt_ratio'].mean()
    avg_credit_score = df['score'].mean()
    
    # 등급별 분포
    grade_distribution = df['grade'].value_counts().to_dict()
    
    # 연체율 계산
    late_count = len(df[df['late'] != '없음'])
    late_rate = (late_count / total_customers) * 100
    
    return jsonify({
        'total_customers': total_customers,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'conditional_count': conditional_count,
        'approval_rate': round(approval_rate, 1),
        'avg_income': round(avg_income, 0),
        'avg_debt_ratio': round(avg_debt_ratio, 1),
        'avg_credit_score': round(avg_credit_score, 1),
        'grade_distribution': grade_distribution,
        'late_rate': round(late_rate, 1)
    })

@app.route('/api/radar-chart')
def get_radar_chart():
    """고객 신용도 레이더 차트"""
    df = pd.DataFrame(CUSTOMERS)
    
    # 평균값 계산 (정규화)
    avg_income_norm = (df['income'].mean() - df['income'].min()) / (df['income'].max() - df['income'].min()) * 100
    avg_debt_norm = 100 - (df['debt_ratio'].mean() - df['debt_ratio'].min()) / (df['debt_ratio'].max() - df['debt_ratio'].min()) * 100
    avg_score_norm = 100 - (df['score'].mean() - df['score'].min()) / (df['score'].max() - df['score'].min()) * 100
    
    # 승인률
    approval_rate = (len(df[df['result'] == '승인']) / len(df)) * 100
    
    # 담보 제공률
    collateral_rate = (len(df[df['collateral'] == '있음']) / len(df)) * 100
    
    # 연체율 (역수)
    late_rate = 100 - (len(df[df['late'] != '없음']) / len(df)) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[avg_income_norm, avg_debt_norm, avg_score_norm, approval_rate, collateral_rate, late_rate],
        theta=['소득수준', '부채상태', '신용등급', '승인률', '담보제공', '연체상태'],
        fill='toself',
        name='평균 신용도',
        line_color='#3b82f6',
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="고객 신용도 레이더 차트",
        font=dict(size=12),
        height=400
    )
    
    return jsonify(fig.to_dict())

@app.route('/api/customer-analysis-chart')
def get_customer_analysis_chart():
    """고객 분석 막대 차트 (소득별 분포)"""
    df = pd.DataFrame(CUSTOMERS)
    
    # 소득 구간별 분류
    income_ranges = {
        '3000만원 이하': len(df[df['income'] <= 3000]),
        '3000-5000만원': len(df[(df['income'] > 3000) & (df['income'] <= 5000)]),
        '5000-7000만원': len(df[(df['income'] > 5000) & (df['income'] <= 7000)]),
        '7000만원 이상': len(df[df['income'] > 7000])
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(income_ranges.keys()),
            y=list(income_ranges.values()),
            marker_color=['#ef4444', '#f59e0b', '#3b82f6', '#10b981'],
            text=list(income_ranges.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="고객 소득별 분포",
        xaxis_title="소득 구간",
        yaxis_title="고객 수",
        height=400,
        font=dict(size=12),
        showlegend=False
    )
    
    return jsonify(fig.to_dict())

@app.route('/api/approval-process-chart')
def get_approval_process_chart():
    """심사 프로세스 진행률 차트"""
    df = pd.DataFrame(CUSTOMERS)
    
    # 프로세스 단계별 통계
    total = len(df)
    approved = len(df[df['result'] == '승인'])
    conditional = len(df[df['result'] == '조건부승인'])
    rejected = len(df[df['result'] == '거절'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['승인', '조건부승인', '거절'],
        y=[approved, conditional, rejected],
        marker_color=['#10b981', '#f59e0b', '#ef4444'],
        text=[f'{approved}명', f'{conditional}명', f'{rejected}명'],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="대출 심사 결과 분포",
        height=300,
        font=dict(size=12),
        yaxis_title="고객 수",
        showlegend=False
    )
    
    # Convert the figure to dict and ensure it's JSON serializable
    fig_dict = fig.to_dict()
    return jsonify(fig_dict)

@app.route('/api/grade-distribution-chart')
def get_grade_distribution_chart():
    """신용등급 분포 차트"""
    df = pd.DataFrame(CUSTOMERS)
    grade_counts = df['grade'].value_counts().sort_index()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=grade_counts.index.tolist(),
            values=grade_counts.values.tolist(),
            hole=0.4,
            marker_colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#f97316']
        )
    ])
    
    fig.update_layout(
        title="신용등급 분포",
        height=300,
        font=dict(size=12),
        showlegend=True
    )
    
    return jsonify(fig.to_dict())

@app.route('/api/xai-explanation/<customer_id>')
def get_xai_explanation(customer_id):
    """XAI 설명 생성"""
    customer = next((c for c in CUSTOMERS if c['id'] == customer_id), None)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    # 간단한 XAI 설명 로직
    if customer['result'] == '거절':
        reasons = customer['reason']
        explanation = f"고객 {customer['name']}님의 대출이 거절된 주요 사유는 다음과 같습니다:\n\n"
        for i, reason in enumerate(reasons, 1):
            explanation += f"{i}. {reason}\n"
        explanation += f"\n신용등급: {customer['grade']}, 부채비율: {customer['debt_ratio']}%, 연체이력: {customer['late']}"
    elif customer['result'] == '승인':
        reasons = customer['reason']
        explanation = f"고객 {customer['name']}님의 대출이 승인된 주요 사유는 다음과 같습니다:\n\n"
        for i, reason in enumerate(reasons, 1):
            explanation += f"{i}. {reason}\n"
        explanation += f"\n신용등급: {customer['grade']}, 소득: {customer['income']}만원, 부채비율: {customer['debt_ratio']}%"
    else:
        reasons = customer['reason']
        explanation = f"고객 {customer['name']}님의 대출이 조건부승인된 사유는 다음과 같습니다:\n\n"
        for i, reason in enumerate(reasons, 1):
            explanation += f"{i}. {reason}\n"
        explanation += f"\n추가 서류나 담보가 필요할 수 있습니다."
    
    return jsonify({
        "customer_name": customer['name'],
        "result": customer['result'],
        "explanation": explanation,
        "risk_score": customer['score'],
        "income": customer['income'],
        "debt_ratio": customer['debt_ratio']
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request. JSON body required."}), 400

    customer_id = data.get('customer_id')
    user_message = data.get('message')

    if not all([customer_id, user_message]):
        return jsonify({"error": "Missing 'customer_id' or 'message'"}), 400
        
    customer = next((c for c in CUSTOMERS if c['id'] == customer_id), None)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    # Construct a detailed prompt for the AI
    prompt_messages = [
        {
            "role": "system",
            "content": f"""당신은 전문적인 금융 상담사입니다. 고객의 대출 심사 결과에 대해 친절하고 명확하게 설명해주세요.

고객 정보:
- 이름: {customer['name']}
- 신용등급: {customer['grade']} (점수: {customer['score']})
- 연소득: {customer['income']}만원
- 부채비율: {customer['debt_ratio']}%
- 연체이력: {customer['late']}
- 대출결과: {customer['result']}
- 심사사유: {', '.join(customer['reason'])}

답변 지침:
1. 완전한 문장으로 답변하세요
2. 고객의 상황을 이해하고 공감하는 톤을 유지하세요
3. 구체적이고 실용적인 조언을 제공하세요
4. 한국어로 자연스럽게 답변하세요
5. 최소 2-3문장으로 구성된 완전한 답변을 제공하세요"""
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    try:
        # Check if the client and API key are available
        if not client or not client.api_key:
            return jsonify({"reply": "OpenAI API key is not configured or client failed to initialize. Please check your environment variables."})

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=prompt_messages,
            max_tokens=300,  # 토큰 수 증가
            temperature=0.7
        )
        
        if completion.choices and completion.choices[0].message:
            reply = completion.choices[0].message.content
            # Ensure reply is not None before stripping
            reply = reply.strip() if reply else "AI did not return a message."
        else:
            reply = "No response from AI."

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"OpenAI API error: {e}")
        # 더 자연스러운 데모 응답
        if customer['result'] == '승인':
            mock_reply = f"안녕하세요! {customer['name']}님의 대출 심사 결과를 말씀드리겠습니다. 축하드립니다! 대출이 승인되었습니다. {customer['name']}님은 {customer['grade']} 등급으로 양호한 신용상태를 보유하고 계시며, 연소득 {customer['income']}만원으로 안정적인 소득을 확인했습니다. 부채비율 {customer['debt_ratio']}%는 적정 수준이며, 연체이력도 없어 신뢰할 수 있는 고객으로 판단되었습니다. 앞으로도 좋은 신용관리를 유지해주시기 바랍니다."
        elif customer['result'] == '거절':
            mock_reply = f"안녕하세요, {customer['name']}님. 대출 심사 결과를 말씀드리게 되어 죄송합니다. 현재 대출이 거절되었습니다. 주요 사유는 {', '.join(customer['reason'])} 때문입니다. {customer['grade']} 등급으로 신용도가 다소 낮고, 부채비율 {customer['debt_ratio']}%가 높은 편이며, 연체이력도 있어 위험도가 높다고 판단되었습니다. 신용회복을 위해 연체 해결과 부채비율 개선을 우선적으로 진행하시는 것을 권장드립니다."
        else:
            mock_reply = f"안녕하세요, {customer['name']}님. 대출 심사 결과를 말씀드리겠습니다. 조건부승인으로 결정되었습니다. {customer['grade']} 등급으로 신용도가 보통이며, 연소득 {customer['income']}만원과 부채비율 {customer['debt_ratio']}%를 종합적으로 고려한 결과입니다. 추가 서류나 담보 제공이 필요할 수 있으며, 구체적인 조건은 담당자와 상담하시면 됩니다."
        
        return jsonify({"reply": mock_reply})

@app.route('/api/server-status')
def server_status():
    uptime = int(time.time() - server_start_time)
    mem = psutil.virtual_memory()
    return jsonify({
        'status': 'ok',
        'uptime_sec': uptime,
        'memory_percent': mem.percent,
        'memory_used_mb': int(mem.used / 1024 / 1024),
        'memory_total_mb': int(mem.total / 1024 / 1024)
    })

@app.route('/api/customer-trends')
def get_customer_trends():
    """고객 트렌드 분석 데이터"""
    df = pd.DataFrame(CUSTOMERS)
    
    # 월별 승인률 트렌드 (가상 데이터)
    monthly_trends = {
        'labels': ['1월', '2월', '3월', '4월', '5월', '6월'],
        'approval_rates': [75, 78, 82, 79, 85, 88],
        'customer_counts': [45, 52, 48, 61, 55, 58]
    }
    
    # 등급별 평균 소득
    grade_income = df.groupby('grade')['income'].mean().to_dict()
    
    # 연령대별 분포 (가상 데이터)
    age_distribution = {
        '20대': 15,
        '30대': 35,
        '40대': 28,
        '50대': 18,
        '60대': 4
    }
    
    return jsonify({
        'monthly_trends': monthly_trends,
        'grade_income': grade_income,
        'age_distribution': age_distribution
    })

@app.route('/api/customer-details/<customer_id>')
def get_customer_details(customer_id):
    """고객 상세 정보 (동적 데이터 포함)"""
    customer = next((c for c in CUSTOMERS if c['id'] == customer_id), None)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    # 동적 데이터 추가
    import random
    from datetime import datetime, timedelta
    
    # 최근 활동 내역 (가상 데이터)
    recent_activities = [
        {
            'date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'activity': '대출 상담 신청',
            'status': '완료'
        },
        {
            'date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'activity': '서류 제출',
            'status': '완료'
        },
        {
            'date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'activity': '심사 진행',
            'status': '진행중'
        }
    ]
    
    # 리스크 점수 계산
    risk_score = 100 - (customer['score'] * 10) + (customer['debt_ratio'] * 0.5)
    if customer['late'] != '없음':
        risk_score += 20
    
    # 추천 상품
    if customer['result'] == '승인':
        recommended_products = ['개인신용대출', '담보대출', '카드론']
    elif customer['result'] == '조건부승인':
        recommended_products = ['소액대출', '담보대출']
    else:
        recommended_products = ['신용회복대출', '소액대출']
    
    return jsonify({
        'customer': customer,
        'recent_activities': recent_activities,
        'risk_score': round(risk_score, 1),
        'recommended_products': recommended_products,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(debug=True, port=5500)
