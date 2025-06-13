import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import os
from flask import send_from_directory
from dash.dependencies import MATCH, ALL
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 데이터 불러오기
DATA_PATH = 'final_clustering.csv'
df = pd.read_csv(DATA_PATH)

# 클러스터 설명 예시 
cluster_descriptions = {
    0:  ''' 고위험 그룹
- ESG등급 분포: B+, B, C, D 등 중하위 등급 혼합
- 공시신용등급 분포: BBB-, BB 등급 중심
- 특징 요약: ESG와 신용등급 모두 낮은 소규모 고위험 클러스터. 전반적으로 취약한 구조를 가진 기업군.
''',
    1: ''' 구조적 취약 그룹
- ESG등급 분포: C (48.5%), D (51.5%) → 최하위
- 공시신용등급 분포: CCC 이하 중심
- 특징 요약: ESG와 신용 모두 열위한 대규모 클러스터. 구조적으로 취약하며 개선 여지가 크나, 장기적 지원 필요.
''',
    2: ''' 개선가능 그룹
- ESG등급 분포: B+ (66%), B (34%) → 중간
- 공시신용등급 분포: A~BB 등급 혼재 (신용은 비교적 양호)
- 특징 요약: ESG 성숙도는 중간, 신용등급은 안정적. ESG 측면 개선 시 빠르게 우량 그룹으로 전환 가능.
''',
    3: ''' ESG 우수 그룹
- ESG등급 분포: A 100% → 우수
- 공시신용등급 분포: A~BBB 중심, 일부 CCC/BB 포함
- 특징 요약: ESG등급은 우수하나, 재무적 취약성 존재하는 기업 포함. ESG 투자는 활발하지만 재무 성과와의 괴리가 있는 기업군. 신용 리스크를 동반한 '과도기형' 지속가능 그룹.
''',
    4: ''' 최상위 그룹
- ESG등급 분포: A+ 100% → 최우수
- 공시신용등급 분포: 대부분 AA, 일부 BBB+
- 특징 요약: ESG와 재무적 안정성 모두 최상위 엘리트 클러스터. 전략적 투자 및 ESG 파트너로서의 핵심 기업군.
''',
}

# Dash 앱 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"], suppress_callback_exceptions=True)

# 신용등급, ESG등급 등 컬럼 한글-영문 매핑
col_map = {
    '공시신용등급': '신용등급',
    '감성지수': '사회적신뢰도',
    'ESG등급': 'ESG등급',
    'GMM_Cluster': '클러스터',
    '기업명': '기업명',
}

# ESG보고서 링크 생성 함수 
def make_report_link(company, report_type):
    if report_type == 'ESG':
        # 기업코드 6자리 추출
        row = df[df['기업명'] == company]
        if not row.empty:
            code = str(row.iloc[0]['기업코드']).zfill(6)
            pdf_dir = 'assets'
            try:
                for fname in os.listdir(pdf_dir):
                    if fname.endswith('.pdf') and fname[:6] == code:
                        return f"/assets/{fname}"
            except Exception as e:
                pass
        return '#'
    else:
        return f"https://example.com/{company}_{report_type}.pdf"

# 카드용 주요 지표 계산
def get_main_metrics(df):
    return [
        {
            'title': '총 기업 수',
            'value': f"{df['기업명'].nunique()}개",
            'icon': 'fa-building',
        },
        {
            'title': '평균 신용등급',
            'value': df['공시신용등급'].mode()[0],
            'icon': 'fa-star',
        },
        {
            'title': '평균 사회적신뢰도',
            'value': f"{df['감성지수'].mean():.2f}",
            'icon': 'fa-users',
        },
        {
            'title': '평균 ESG등급',
            'value': df['ESG등급'].mode()[0],
            'icon': 'fa-leaf',
        },
    ]

def get_credit_color(grade):
    if str(grade).startswith('A'):
        return "#1e90ff"  # 파랑
    elif str(grade).startswith('B'):
        return "#ffc107"  # 주황
    else:
        return "#dc3545"  # 빨강

def get_esg_color(grade):
    if grade in ['A+', 'A', 'AA', 'AA+', 'AAA']:
        return "#00bfae"  # 그린
    elif grade in ['B+', 'B']:
        return "#ffc107"  # 주황
    else:
        return "#dc3545"  # 빨강

# Sidebar
sidebar = dbc.Col([
    html.H1("신한 퓨처아카데미 2조", className="display-6", style={"color": "#fff", "marginTop": 30}),
    html.Hr(style={"borderColor": "#444"}),
    html.H3("업체별 검색", className="display-6", style={"color": "#fff", "marginTop": 30}),
    html.Hr(style={"borderColor": "#444"}),

    dbc.Nav([
        dbc.NavLink([html.I(className="fas fa-chart-bar me-2"), "Dashboard"], href="#", active=True),
        dbc.NavLink([html.I(className="fas fa-globe-asia me-2"), "전체분석"], href=""),
        dbc.NavLink([html.I(className="fas fa-search me-2"), "업체검색"], href="#search", id="search-link"),
    ], vertical=True, pills=True, style={"marginBottom": 30}),
    html.Div("Dark Mode", style={"color": "#aaa", "marginTop": "auto", "marginBottom": 10, "fontSize": 14}),
], width=2, style={"background": "#18191a", "minHeight": "100vh", "padding": "0 0.5rem 0 0.5rem"})

# Main content area
main_content = dbc.Col([
    html.Div(id="main-area", style={"padding": "2rem 1rem"}),
    dcc.Store(id='company-store', storage_type='local'),
    dcc.Store(id='chatbot-history', data=[], storage_type='local'),
    dcc.Store(id='counter-total-target', data=0, storage_type='local'),
    dcc.Store(id='counter-sentiment-target', data=0, storage_type='local'),
    dcc.Store(id='credit-anim-target', data=0, storage_type='local'),
    dcc.Store(id='credit-anim-current', data=0, storage_type='local')
], width=10)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Container([
        dbc.Row([
            sidebar,
            main_content
        ], style={"minHeight": "100vh", "overflow": "hidden"})
    ], fluid=True)
])

# 콜백: 업체 선택 시 클러스터 설명, 보고서 링크 표시
def get_cluster_desc(cluster):
    return cluster_descriptions.get(cluster, '설명 없음')

@app.callback(
    Output('main-area', 'children'),
    [Input('company-dropdown', 'value'), Input('search-link', 'n_clicks')]
)
def main_area_router(company, search_click):
    try:
        print("company:", company, "search_click:", search_click)
        ctx = dash.callback_context
        if not ctx.triggered:
            metrics = get_main_metrics(df)
            # 카운터 애니메이션용 값 분리
            total_company = df['기업명'].nunique()
            avg_credit = df['공시신용등급'].mode()[0]
            avg_sentiment = round(df['감성지수'].mean(), 2)
            avg_esg = df['ESG등급'].mode()[0]
            # 카드별 id 부여 및 dcc.Interval, dcc.Store 추가
            cards = [
                dbc.Card([
                    dcc.Store(id='counter-total-target', data=total_company, storage_type='local'),
                    dcc.Interval(id='counter-total-interval', interval=20, n_intervals=0, max_intervals=total_company),
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-building fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("총 기업 수", className="card-title", style={"color": "#fff"}),
                        html.H2(id='counter-total', className="card-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{0*0.15}s"}),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-star fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("평균 신용등급", className="card-title", style={"color": "#fff"}),
                        html.H2(avg_credit, id='counter-credit', className="card-text fade-in-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{1*0.15}s"}),
                dbc.Card([
                    dcc.Store(id='counter-sentiment-target', data=avg_sentiment, storage_type='local'),
                    dcc.Interval(id='counter-sentiment-interval', interval=20, n_intervals=0, max_intervals=int(avg_sentiment*100)),
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-users fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("평균 사회적신뢰도", className="card-title", style={"color": "#fff"}),
                        html.H2(id='counter-sentiment', className="card-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{2*0.15}s"}),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-leaf fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("평균 ESG등급", className="card-title", style={"color": "#fff"}),
                        html.H2(avg_esg, id='counter-esg', className="card-text fade-in-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{3*0.15}s"}),
            ]
            fig_credit = px.histogram(df, x='공시신용등급', color='GMM_Cluster', barmode='group', title='신용등급 분포(클러스터별)', template='plotly_dark')
            fig_sentiment = px.box(df, x='GMM_Cluster', y='감성지수', color='GMM_Cluster', title='사회적신뢰도(감성지수) 분포', template='plotly_dark')
            fig_esg = go.Figure()
            
            # Overall ESG Grade
            esg_hist = px.histogram(df, x='ESG등급', color='GMM_Cluster', barmode='group', title='ESG등급 분포', template='plotly_dark')
            for trace in esg_hist.data:
                trace.name = f"ESG등급 - {trace.name}"
                fig_esg.add_trace(trace)
            
            # Environmental Grade
            env_hist = px.histogram(df, x='환경', color='GMM_Cluster', barmode='group', template='plotly_dark')
            for trace in env_hist.data:
                trace.name = f"환경 - {trace.name}"
                trace.visible = 'legendonly'
                fig_esg.add_trace(trace)
            
            # Social Grade
            soc_hist = px.histogram(df, x='사회', color='GMM_Cluster', barmode='group', template='plotly_dark')
            for trace in soc_hist.data:
                trace.name = f"사회 - {trace.name}"
                trace.visible = 'legendonly'
                fig_esg.add_trace(trace)
            
            # Governance Grade
            gov_hist = px.histogram(df, x='지배구조', color='GMM_Cluster', barmode='group', template='plotly_dark')
            for trace in gov_hist.data:
                trace.name = f"지배구조 - {trace.name}"
                trace.visible = 'legendonly'
                fig_esg.add_trace(trace)
            
            fig_esg.update_layout(
                title='ESG등급 분포 (클러스터별)',
                template='plotly_dark',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                font=dict(color="#f5f5f5"),
                xaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
                yaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
            )
            fig_pie = px.pie(df, names='GMM_Cluster', title='클러스터 비율', template='plotly_dark')
            return [
                html.Div([
                    html.H1("Dashboard", style={"color": "#fff", "marginBottom": 20, "fontSize": "2.2rem"}),
                    # 클러스터 선택 드롭다운 추가
                    html.Div([
                        dcc.Dropdown(
                            id='cluster-filter-dropdown',
                            options=[{'label': f'클러스터 {c}', 'value': c} for c in sorted(df['GMM_Cluster'].unique())] + [{'label': '전체', 'value': 'all'}],
                            value='all',
                            clearable=False,
                            style={'width': 200, 'color': '#000', 'marginBottom': 20, 'fontWeight': 700}
                        )
                    ], style={'marginBottom': 10}),
                    dbc.Row([dbc.Col(card) for card in cards], className="mb-2 g-4", style={"marginBottom": 10}),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='credit-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-slide-up"), width=6, style={"padding": "6px"}),
                        dbc.Col(dcc.Graph(id='sentiment-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-zoom-in"), width=6, style={"padding": "6px"}),
                    ], className="g-4", style={"marginBottom": 0}),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='esg-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-slide-up"), width=6, style={"padding": "6px"}),
                        dbc.Col(dcc.Graph(id='pie-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-fade-in"), width=6, style={"padding": "6px"}),
                    ], className="g-4", style={"marginBottom": 0}),
                ], id="main", style={"padding": "1.2rem 0.5rem 0.5rem 0.5rem", "overflow": "hidden"})
            ]
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'search-link':
            table = dash_table.DataTable(
                id='company-list-table',
                columns=[{"name": i, "id": i} for i in ['기업명', '공시신용등급', '감성지수', 'ESG등급', 'GMM_Cluster']],
                data=df.to_dict('records'),
                page_size=20,
                style_table={'overflowX': 'auto', 'background': '#23272f', 'padding': '24px', 'borderRadius': '18px', 'boxShadow': '0 2px 12px #0004', 'height': '600px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center', 'background': '#23272f', 'color': '#fff', 'fontSize': '14px', 'padding': '10px'},
                style_header={'background': '#18191a', 'color': '#6c63ff', 'fontWeight': 'bold', 'fontSize': '16px', 'border': 'none'},
                style_data={'border': 'none'},
                filter_action='native',
                sort_action='native',
            )
            return [
                html.H1("업체 목록", style={"color": "#fff", "marginBottom": 40, "fontSize": "2.6rem", "fontWeight": 800}),
                html.Div(
                    table
                )
            ]
        # 전체분석 클릭 시 대시보드로 이동
        if trigger_id == 'main':
            metrics = get_main_metrics(df)
            # 카운터 애니메이션용 값 분리
            total_company = df['기업명'].nunique()
            avg_credit = df['공시신용등급'].mode()[0]
            avg_sentiment = round(df['감성지수'].mean(), 2)
            avg_esg = df['ESG등급'].mode()[0]
            # 카드별 id 부여 및 dcc.Interval, dcc.Store 추가
            cards = [
                dbc.Card([
                    dcc.Store(id='counter-total-target', data=total_company, storage_type='local'),
                    dcc.Interval(id='counter-total-interval', interval=20, n_intervals=0, max_intervals=total_company),
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-building fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("총 기업 수", className="card-title", style={"color": "#fff"}),
                        html.H2(id='counter-total', className="card-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{0*0.15}s"}),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-star fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("평균 신용등급", className="card-title", style={"color": "#fff"}),
                        html.H2(avg_credit, id='counter-credit', className="card-text fade-in-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{1*0.15}s"}),
                dbc.Card([
                    dcc.Store(id='counter-sentiment-target', data=avg_sentiment, storage_type='local'),
                    dcc.Interval(id='counter-sentiment-interval', interval=20, n_intervals=0, max_intervals=int(avg_sentiment*100)),
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-users fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("평균 사회적신뢰도", className="card-title", style={"color": "#fff"}),
                        html.H2(id='counter-sentiment', className="card-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{2*0.15}s"}),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(html.I(className="fas fa-leaf fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                        html.H5("평균 ESG등급", className="card-title", style={"color": "#fff"}),
                        html.H2(avg_esg, id='counter-esg', className="card-text fade-in-text", style={"color": "#fff"}),
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{3*0.15}s"}),
            ]
            fig_credit = px.histogram(df, x='공시신용등급', color='GMM_Cluster', barmode='group', title='신용등급 분포(클러스터별)', template='plotly_dark')
            fig_sentiment = px.box(df, x='GMM_Cluster', y='감성지수', color='GMM_Cluster', title='사회적신뢰도(감성지수) 분포', template='plotly_dark')
            fig_esg = go.Figure()
            
            # Overall ESG Grade
            esg_hist = px.histogram(df, x='ESG등급', color='GMM_Cluster', barmode='group', title='ESG등급 분포', template='plotly_dark')
            for trace in esg_hist.data:
                trace.name = f"ESG등급 - {trace.name}"
                fig_esg.add_trace(trace)
            
            # Environmental Grade
            env_hist = px.histogram(df, x='환경', color='GMM_Cluster', barmode='group', template='plotly_dark')
            for trace in env_hist.data:
                trace.name = f"환경 - {trace.name}"
                trace.visible = 'legendonly'
                fig_esg.add_trace(trace)
            
            # Social Grade
            soc_hist = px.histogram(df, x='사회', color='GMM_Cluster', barmode='group', template='plotly_dark')
            for trace in soc_hist.data:
                trace.name = f"사회 - {trace.name}"
                trace.visible = 'legendonly'
                fig_esg.add_trace(trace)
            
            # Governance Grade
            gov_hist = px.histogram(df, x='지배구조', color='GMM_Cluster', barmode='group', template='plotly_dark')
            for trace in gov_hist.data:
                trace.name = f"지배구조 - {trace.name}"
                trace.visible = 'legendonly'
                fig_esg.add_trace(trace)
            
            fig_esg.update_layout(
                title='ESG등급 분포 (클러스터별)',
                template='plotly_dark',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                font=dict(color="#f5f5f5"),
                xaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
                yaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
            )
            fig_pie = px.pie(df, names='GMM_Cluster', title='클러스터 비율', template='plotly_dark')
            return [
                html.Div([
                    html.H1("Dashboard", style={"color": "#fff", "marginBottom": 20, "fontSize": "2.2rem"}),
                    # 클러스터 선택 드롭다운 추가
                    html.Div([
                        dcc.Dropdown(
                            id='cluster-filter-dropdown',
                            options=[{'label': f'클러스터 {c}', 'value': c} for c in sorted(df['GMM_Cluster'].unique())] + [{'label': '전체', 'value': 'all'}],
                            value='all',
                            clearable=False,
                            style={'width': 200, 'color': '#000', 'marginBottom': 20, 'fontWeight': 700}
                        )
                    ], style={'marginBottom': 10}),
                    dbc.Row([dbc.Col(card) for card in cards], className="mb-2 g-4", style={"marginBottom": 10}),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='credit-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-slide-up"), width=6, style={"padding": "6px"}),
                        dbc.Col(dcc.Graph(id='sentiment-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-zoom-in"), width=6, style={"padding": "6px"}),
                    ], className="g-4", style={"marginBottom": 0}),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='esg-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-slide-up"), width=6, style={"padding": "6px"}),
                        dbc.Col(dcc.Graph(id='pie-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-fade-in"), width=6, style={"padding": "6px"}),
                    ], className="g-4", style={"marginBottom": 0}),
                ], id="main", style={"padding": "1.2rem 0.5rem 0.5rem 0.5rem", "overflow": "hidden"})
            ]
        # 업체 선택 시: 검색/시각화 화면
        if company:
            row_df = df[df['기업명'] == company]
            if row_df.empty:
                return [html.Div("해당 기업을 찾을 수 없습니다.", style={"color": "red"})]
            row = row_df.iloc[0]
            cluster = row['GMM_Cluster']
            unique_credits = sorted(df['공시신용등급'].dropna().unique(), key=lambda x: (
                ['D', 'C', 'CC', 'CCC', 'B-', 'B', 'B+', 'BB-', 'BB', 'BB+', 'BBB-', 'BBB', 'BBB+', 'A-', 'A', 'A+', 'AA-', 'AA', 'AA+', 'AAA'].index(str(x))
                if str(x) in ['D', 'C', 'CC', 'CCC', 'B-', 'B', 'B+', 'BB-', 'BB', 'BB+', 'BBB-', 'BBB', 'BBB+', 'A-', 'A', 'A+', 'AA-', 'AA', 'AA+', 'AAA'] else 999
            ))
            credit_order = unique_credits
            credit_score = credit_order.index(str(row['공시신용등급'])) if str(row['공시신용등급']) in credit_order else None
            esg_order = ['D', 'C', 'B', 'B+', 'A', 'A+', 'AA', 'AA+', 'AAA']
            esg_score = esg_order.index(str(row['ESG등급'])) if str(row['ESG등급']) in esg_order else None
            if credit_score is not None:
                # Map credit_score to a 0-10 scale for the gauge
                gauge_value = int((credit_score / (len(credit_order)-1)) * 10) if len(credit_order) > 1 else 0
                card_credit = html.Div([
                    dcc.Store(id='credit-anim-target', data=gauge_value, storage_type='local'),
                    dcc.Store(id='credit-anim-current', data=0, storage_type='local'),
                    dcc.Interval(id='credit-anim-interval', interval=30, n_intervals=0, max_intervals=gauge_value),
                    dbc.Card([
                        dbc.CardHeader("신용등급", style={"color": "#fff", "background": "#23272f"}),
                        dbc.CardBody([
                            html.H2(row['공시신용등급'], style={"color": get_credit_color(row['공시신용등급']), "fontWeight": "bold"}),
                            dcc.Graph(id='credit-gauge-graph', config={'displayModeBar': False}, style={'height': 220}),
                        ])
                    ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10})
                ])
            else:
                card_credit = dbc.Card([
                    dbc.CardHeader("신용등급", style={"color": "#fff", "background": "#23272f"}),
                    dbc.CardBody([
                        html.H2("등급 정보 없음", style={"color": "#dc3545", "fontWeight": "bold"}),
                        html.Div("해당 기업의 신용등급 정보가 없습니다.", style={"color": "#fff"})
                    ])
                ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10})
            card_sentiment = dbc.Card([
                dbc.CardHeader("사회적신뢰도", style={"color": "#fff", "background": "#23272f"}),
                dbc.CardBody([
                    html.H2(f"{row['감성지수']:.2f}", style={"color": "#1e90ff", "fontWeight": "bold"}),
                    dbc.Progress(value=row['감성지수']*100, color="info", style={"height": "20px", "background": "#444"}),
                ])
            ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10})
            card_esg = dbc.Card([
                dbc.CardHeader("ESG등급", style={"color": "#fff", "background": "#23272f"}),
                dbc.CardBody([
                    # Overall ESG Grade
                    html.Div([
                        html.H2(row['ESG등급'], style={"color": get_esg_color(row['ESG등급']), "fontWeight": "bold", "marginBottom": "20px"}),
                        html.I(className="fas fa-leaf", style={"color": get_esg_color(row['ESG등급']), "fontSize": 40, "marginBottom": "20px"}),
                    ], style={"textAlign": "center"}),
                    # Individual Components
                    html.Div([
                        # Environmental
                        html.Div([
                            html.I(className="fas fa-tree", style={"color": get_esg_color(row['환경']), "fontSize": 24, "marginBottom": "5px"}),
                            html.H5("환경", style={"color": "#fff", "marginBottom": "5px"}),
                            html.H3(row['환경'], style={"color": get_esg_color(row['환경']), "fontWeight": "bold"}),
                        ], style={"textAlign": "center", "flex": "1"}),
                        # Social
                        html.Div([
                            html.I(className="fas fa-users", style={"color": get_esg_color(row['사회']), "fontSize": 24, "marginBottom": "5px"}),
                            html.H5("사회", style={"color": "#fff", "marginBottom": "5px"}),
                            html.H3(row['사회'], style={"color": get_esg_color(row['사회']), "fontWeight": "bold"}),
                        ], style={"textAlign": "center", "flex": "1"}),
                        # Governance
                        html.Div([
                            html.I(className="fas fa-balance-scale", style={"color": get_esg_color(row['지배구조']), "fontSize": 24, "marginBottom": "5px"}),
                            html.H5("지배구조", style={"color": "#fff", "marginBottom": "5px"}),
                            html.H3(row['지배구조'], style={"color": get_esg_color(row['지배구조']), "fontWeight": "bold"}),
                        ], style={"textAlign": "center", "flex": "1"}),
                    ], style={"display": "flex", "justifyContent": "space-between", "marginTop": "10px"}),
                ])
            ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10})
            card_cluster = dbc.Card([
                dbc.CardHeader("클러스터", style={"color": "#fff", "background": "#23272f"}),
                dbc.CardBody([
                    html.H2(str(row['GMM_Cluster']), style={"color": "#6c63ff", "fontWeight": "bold"}),
                    html.Pre(cluster_descriptions.get(row['GMM_Cluster'], ''), style={"color": "#aaa", "fontSize": 14, "whiteSpace": "pre-wrap", "background": "none", "border": "none"}),
                ])
            ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10})
            return [
                dbc.Row([
                    dbc.Col(card_credit, width=6, style={"padding": "8px"}),
                    dbc.Col(card_sentiment, width=6, style={"padding": "8px"}),
                ], style={"margin": 0, "width": "100%"}),
                dbc.Row([
                    dbc.Col(card_esg, width=6, style={"padding": "8px"}),
                    dbc.Col(card_cluster, width=6, style={"padding": "8px"}),
                ], style={"margin": 0, "width": "100%"}),
                html.Div([
                    html.A('ESG 보고서', href=make_report_link(company, 'ESG'), target='_blank', style={'marginRight': '40px', 'fontSize': 22, 'color': '#6c63ff', 'fontWeight': 700}),
                ], style={'marginBottom': 30})
            ]
        # 아무것도 선택되지 않은 경우(대시보드)
        # Do NOT include any credit-gauge-graph or related components here
        metrics = get_main_metrics(df)
        cards = [
            dbc.Card([
                dbc.CardBody([
                    html.Div(html.I(className=f"fas {m['icon']} fa-2x"), style={"color": "#6c63ff", "marginBottom": 10}),
                    html.H5(m['title'], className="card-title", style={"color": "#fff"}),
                    html.H2(m['value'], className="card-text", style={"color": "#fff"}),
                ])
            ], className="animated-card", style={"background": "#23272f", "border": "none", "borderRadius": 12, "boxShadow": "0 2px 8px #0002", "padding": 10, "animationDelay": f"{i*0.15}s"})
            for i, m in enumerate(metrics)
        ]
        fig_credit = px.histogram(df, x='공시신용등급', color='GMM_Cluster', barmode='group', title='신용등급 분포(클러스터별)', template='plotly_dark')
        fig_sentiment = px.box(df, x='GMM_Cluster', y='감성지수', color='GMM_Cluster', title='사회적신뢰도(감성지수) 분포', template='plotly_dark')
        fig_esg = go.Figure()
        
        # Overall ESG Grade
        esg_hist = px.histogram(df, x='ESG등급', color='GMM_Cluster', barmode='group', title='ESG등급 분포', template='plotly_dark')
        for trace in esg_hist.data:
            trace.name = f"ESG등급 - {trace.name}"
            fig_esg.add_trace(trace)
        
        # Environmental Grade
        env_hist = px.histogram(df, x='환경', color='GMM_Cluster', barmode='group', template='plotly_dark')
        for trace in env_hist.data:
            trace.name = f"환경 - {trace.name}"
            trace.visible = 'legendonly'
            fig_esg.add_trace(trace)
        
        # Social Grade
        soc_hist = px.histogram(df, x='사회', color='GMM_Cluster', barmode='group', template='plotly_dark')
        for trace in soc_hist.data:
            trace.name = f"사회 - {trace.name}"
            trace.visible = 'legendonly'
            fig_esg.add_trace(trace)
        
        # Governance Grade
        gov_hist = px.histogram(df, x='지배구조', color='GMM_Cluster', barmode='group', template='plotly_dark')
        for trace in gov_hist.data:
            trace.name = f"지배구조 - {trace.name}"
            trace.visible = 'legendonly'
            fig_esg.add_trace(trace)
        
        fig_esg.update_layout(
            title='ESG등급 분포 (클러스터별)',
            template='plotly_dark',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(color="#f5f5f5"),
            xaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
            yaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
        )
        fig_pie = px.pie(df, names='GMM_Cluster', title='클러스터 비율', template='plotly_dark')
        return [
            html.Div([
                html.H1("Dashboard", style={"color": "#fff", "marginBottom": 20, "fontSize": "2.2rem"}),
                # 클러스터 선택 드롭다운 추가
                html.Div([
                    dcc.Dropdown(
                        id='cluster-filter-dropdown',
                        options=[{'label': f'클러스터 {c}', 'value': c} for c in sorted(df['GMM_Cluster'].unique())] + [{'label': '전체', 'value': 'all'}],
                        value='all',
                        clearable=False,
                        style={'width': 200, 'color': '#000', 'marginBottom': 20, 'fontWeight': 700}
                    )
                ], style={'marginBottom': 10}),
                dbc.Row([dbc.Col(card) for card in cards], className="mb-2 g-4", style={"marginBottom": 10}),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='credit-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-slide-up"), width=6, style={"padding": "6px"}),
                    dbc.Col(dcc.Graph(id='sentiment-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-zoom-in"), width=6, style={"padding": "6px"}),
                ], className="g-4", style={"marginBottom": 0}),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='esg-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-slide-up"), width=6, style={"padding": "6px"}),
                    dbc.Col(dcc.Graph(id='pie-graph', config={"displayModeBar": False}, style={"height": 260, "marginBottom": 0}, className="graph-fade-in"), width=6, style={"padding": "6px"}),
                ], className="g-4", style={"marginBottom": 0}),
            ], id="main", style={"padding": "1.2rem 0.5rem 0.5rem 0.5rem", "overflow": "hidden"})
        ]
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return [html.Div(f"Error: {e}", style={"color": "red"})]

# 업체 검색 드롭다운을 sidebar에 추가
sidebar.children.insert(3, html.Div([
    dcc.Dropdown(
        id='company-dropdown',
        options=[{'label': name, 'value': name} for name in sorted(df['기업명'].unique())],
        placeholder='업체명을 선택하세요',
        multi=False,
        style={'marginBottom': 20, 'color': '#000'}
    ),
    html.Button('AI챗봇', id='open-chatbot-btn', n_clicks=0, style={'width': '100%', 'background': '#6c63ff', 'color': '#fff', 'fontWeight': 700, 'border': 'none', 'borderRadius': 8, 'padding': '10px', 'marginBottom': 10}),
]))

# Add chatbot modal to the layout (hidden by default)
app.layout.children.append(
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('AI챗봇'), close_button=True, style={'background': '#23272f', 'color': '#fff'}),
        dbc.ModalBody([
            html.Div([
                html.Div(id='chatbot-messages', style={'height': '350px', 'overflowY': 'auto', 'background': '#23272f', 'color': '#fff', 'padding': '10px', 'borderRadius': '8px', 'marginBottom': '10px', 'fontSize': '15px'}),
                dcc.Interval(id='chatbot-scroll-interval', interval=500, n_intervals=0),
            ]),
            dcc.Input(id='chatbot-input', placeholder='메시지를 입력하세요...', type='text', style={'marginBottom': '10px', 'background': '#18191a', 'color': '#fff', 'border': 'none', 'width': '100%'}, debounce=False, autoFocus=True),
            dbc.Button('전송', id='send-chatbot-btn', color='primary', style={'width': '100%', 'background': '#6c63ff', 'border': 'none', 'fontWeight': 700, 'marginBottom': '10px'}),
            dbc.Button('대화 초기화', id='clear-chatbot-btn', color='secondary', style={'width': '100%', 'background': '#444', 'border': 'none', 'fontWeight': 700}),
        ]),
    ], id='chatbot-modal', is_open=False, centered=True, size='lg', backdrop='static', style={'color': '#fff'})
)

# Callback to open/close chatbot modal (dbc.Modal n_close prop 제거, 기본 패턴)
@app.callback(
    Output('chatbot-modal', 'is_open'),
    [Input('open-chatbot-btn', 'n_clicks')],
    [State('chatbot-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_chatbot_modal(n_open, is_open):
    if n_open:
        return not is_open
    return is_open

# Callback to display chat messages (업체별로 분리)
@app.callback(
    Output('chatbot-messages', 'children'),
    [Input('chatbot-history', 'data'), Input('company-dropdown', 'value')]
)
def update_chatbot_messages(history, company):
    if not company or not history or company not in history or not history[company]:
        return html.Div([
            html.Div(f"{company or '기업'} 전문가 AI챗봇과 대화를 시작하세요.", style={'color': '#aaa', 'fontStyle': 'italic'})
        ])
    company_history = history[company]
    return [
        html.Div([
            html.B('나', style={'color': '#6c63ff'}), html.Span(f': {msg["user"]}', style={'marginLeft': 8})
        ], style={'marginBottom': 6}) if msg['role'] == 'user' else
        html.Div([
            html.B('AI챗봇', style={'color': '#00bfae'}), html.Span(f': {msg["assistant"]}', style={'marginLeft': 8})
        ], style={'marginBottom': 10, 'marginLeft': 16})
        for msg in company_history
    ]

# Callback to send message to ChatGPT API and update chat history, 업체별 히스토리 분리 및 대화 초기화/입력창 초기화 통합, 예외처리 및 print 디버깅 추가
@app.callback(
    [Output('chatbot-history', 'data'), Output('chatbot-input', 'value')],
    [
        Input('send-chatbot-btn', 'n_clicks'),
        Input('chatbot-input', 'n_submit'),
        Input('clear-chatbot-btn', 'n_clicks'),
        Input('company-dropdown', 'value')
    ],
    [
        State('chatbot-input', 'value'),
        State('chatbot-history', 'data'),
        State('company-dropdown', 'value')
    ],
    prevent_initial_call=True
)
def handle_chatbot_input(n_clicks, n_submit, n_clear, company_change, user_input, history, company):
    import sys
    import traceback
    ctx = dash.callback_context
    print(f"triggered: {ctx.triggered}", file=sys.stderr)
    print(f"user_input: {user_input}, history: {history}, company: {company}", file=sys.stderr)
    if not ctx.triggered:
        raise PreventUpdate
    trigger = ctx.triggered[0]['prop_id']
    # 업체 변경 시 입력창만 비움, history는 그대로
    if trigger == 'company-dropdown.value':
        print("[DEBUG] Company changed, clearing input only", file=sys.stderr)
        return dash.no_update, ""
    # 대화 초기화 버튼
    if trigger == 'clear-chatbot-btn.n_clicks':
        print("[DEBUG] Chatbot history cleared", file=sys.stderr)
        return {}, ""
    # 메시지 전송(버튼/엔터)
    if not company or not user_input:
        print("[DEBUG] No company or user_input, PreventUpdate", file=sys.stderr)
        raise PreventUpdate
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        print('[ERROR] OpenAI API Key is missing!', file=sys.stderr)
        return dash.no_update, ""
    if history is None or not isinstance(history, dict):
        print('[DEBUG] history is None or not dict, initializing to {}', file=sys.stderr)
        history = {}
    company_history = history.get(company, [])
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"당신은 {company}에 대한 전문가이자 열정이 넘치는 AI챗봇입니다. "
                        "기업 분석시에는 {company} 중심으로 답변하세요 "
                        "질문에 대해 핵심만 간결하고 명확하게 답변하세요. "
                        "불필요하게 장황하게 설명하지 마세요."
                        "당신은 유쾌하면서 위트있게 설명합니다."
                    )
                },
                *[{"role": "user", "content": msg['user']} for msg in company_history if msg['role'] == 'user'],
                {"role": "user", "content": user_input}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print('[ERROR] Exception in OpenAI API call or response:', file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        answer = f"[오류] 답변을 가져올 수 없습니다: {e}"
    company_history.append({'role': 'user', 'user': user_input})
    company_history.append({'role': 'assistant', 'assistant': answer})
    history[company] = company_history
    print(f"[DEBUG] Updated history for {company}: {company_history}", file=sys.stderr)
    return history, ""

# Add clientside callback for auto-scroll
app.clientside_callback(
    """
    function(n_intervals) {
        var msgDiv = document.getElementById('chatbot-messages');
        if (msgDiv) {
            msgDiv.scrollTop = msgDiv.scrollHeight;
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('chatbot-messages', 'data-dummy', allow_duplicate=True),
    Input('chatbot-scroll-interval', 'n_intervals'),
    prevent_initial_call=True
)

server = app.server

@server.route('/esg_pdfs/<path:filename>')
def serve_esg_pdf(filename):
    return send_from_directory('esg_pdfs', filename)

@app.callback(
    Output('credit-gauge-graph', 'figure'),
    [Input('credit-anim-interval', 'n_intervals')],
    [State('credit-anim-target', 'data')],
    prevent_initial_call=True
)
def animate_credit_gauge(n_intervals, target):
    if n_intervals is None or target is None:
        raise PreventUpdate
    value = min(n_intervals, target)
    # Gauge config for 0-10 scale, 5 segments, semi-circular, styled like the image
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'font': {'size': 60, 'color': '#168386', 'family': 'Arial Black'}, 'suffix': "/10"},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkgray", 'dtick': 2},
            'bar': {'color': "#168386", 'thickness': 0.18},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 2], 'color': '#F24B26'},
                {'range': [2, 4], 'color': '#E88B1F'},
                {'range': [4, 6], 'color': '#F2C230'},
                {'range': [6, 8], 'color': '#7AC36A'},
                {'range': [8, 10], 'color': '#3CA878'},
            ],
            'threshold': {
                'line': {'color': "#168386", 'width': 6},
                'thickness': 0.8,
                'value': value
            }
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    fig.update_layout(
        margin={'t': 0, 'b': 0, 'l': 0, 'r': 0},
        paper_bgcolor="white",
        font={'color': "#168386", 'family': "Arial Black"}
    )
    return fig

# 카운터 콜백: 총 기업 수
@app.callback(
    Output('counter-total', 'children'),
    [Input('counter-total-interval', 'n_intervals')],
    [State('counter-total-target', 'data')]
)
def update_counter_total(n, target):
    if n is None or target is None:
        return '0개'
    value = min(n, target)
    return f"{value}개"

# 카운터 콜백: 평균 사회적신뢰도
@app.callback(
    Output('counter-sentiment', 'children'),
    [Input('counter-sentiment-interval', 'n_intervals')],
    [State('counter-sentiment-target', 'data')]
)
def update_counter_sentiment(n, target):
    if n is None or target is None:
        return '0.00'
    value = min(n, int(target*100)) / 100
    return f"{value:.2f}"

# 클러스터별 그래프 업데이트 콜백
@app.callback(
    [Output('credit-graph', 'figure'),
     Output('sentiment-graph', 'figure'),
     Output('esg-graph', 'figure'),
     Output('pie-graph', 'figure')],
    [Input('cluster-filter-dropdown', 'value')]
)
def update_cluster_graphs(selected_cluster):
    if selected_cluster == 'all':
        dff = df.copy()
    else:
        dff = df[df['GMM_Cluster'] == selected_cluster]

    # 1. 신용등급 분포: 수평 누적 막대그래프
    credit_order = ['D', 'C', 'CC', 'CCC', 'B-', 'B', 'B+', 'BB-', 'BB', 'BB+', 'BBB-', 'BBB', 'BBB+', 'A-', 'A', 'A+', 'AA-', 'AA', 'AA+', 'AAA']
    fig_credit = px.bar(
        dff,
        y='공시신용등급',
        color='GMM_Cluster',
        orientation='h',
        title='신용등급 분포 (클러스터별)',
        template='plotly_dark',
        category_orders={'공시신용등급': credit_order},
        labels={'공시신용등급': '신용등급', 'count': '기업 수', 'GMM_Cluster': '클러스터'}
    )
    fig_credit.update_layout(
        barmode='stack',
        title_x=0.5,
        title_font_size=20,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # 2. 사회적 신뢰도: 바이올린 플롯
    fig_sentiment = px.violin(
        dff,
        x='GMM_Cluster',
        y='감성지수',
        color='GMM_Cluster',
        box=True,
        points='all',
        title='사회적신뢰도 분포 (클러스터별)',
        template='plotly_dark',
        labels={'GMM_Cluster': '클러스터', '감성지수': '사회적신뢰도'}
    )
    fig_sentiment.update_layout(
        title_x=0.5,
        title_font_size=20,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # 3. ESG등급: 히트맵
    esg_pivot = dff.pivot_table(index='ESG등급', columns='GMM_Cluster', values='기업명', aggfunc='count', fill_value=0)
    esg_order = ['D', 'C', 'B', 'B+', 'A', 'A+', 'AA', 'AA+', 'AAA']
    esg_pivot = esg_pivot.reindex(esg_order)
    fig_esg = go.Figure(data=go.Heatmap(
        z=esg_pivot.values,
        x=[str(c) for c in esg_pivot.columns],
        y=esg_pivot.index,
        colorscale='YlGnBu',
        colorbar=dict(title='기업 수'),
        hoverongaps=False
    ))
    fig_esg.update_layout(
        title='ESG등급-클러스터별 분포 (히트맵)',
        title_x=0.5,
        title_font_size=20,
        xaxis_title='클러스터',
        yaxis_title='ESG등급',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40),
        font=dict(color="#f5f5f5"),
        xaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
        yaxis=dict(color="#f5f5f5", tickfont=dict(color="#f5f5f5"), titlefont=dict(color="#f5f5f5")),
    )

    # 4. 클러스터 비율: 도넛형 파이차트
    cluster_counts = dff['GMM_Cluster'].value_counts()
    fig_pie = px.pie(
        values=cluster_counts.values,
        names=cluster_counts.index,
        title='클러스터 비율',
        template='plotly_dark',
        hole=0.5,
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
    )
    fig_pie.update_layout(
        title_x=0.5,
        title_font_size=20,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=80)
    )
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='클러스터 %{label}<br>비율: %{percent}<extra></extra>'
    )

    return fig_credit, fig_sentiment, fig_esg, fig_pie

if __name__ == '__main__':
    app.run(debug=True)
