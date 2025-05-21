import streamlit as st
from PIL import Image
import sqlite3
from datetime import datetime
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText

# Display logo at the top, centered
logo = Image.open("logo.png")
col1, col2, col3 = st.columns([1,2,1])
with col1:
    st.write("")
with col2:
    st.image(logo, width=110)
with col3:
    st.write("")

# Custom CSS for styling (mimicking the image)
st.markdown('''
    <style>
    body {
        background: #eaf4fb !important;
    }
    .main-container {
        background-color: #eaf4fb;
        padding: 30px 0 0 0;
        border-radius: 0 0 30px 30px;
        margin-bottom: 20px;
        max-width: 100vw;
    }
    .rate-box, .goal-section {
        max-width: 92vw;
        margin-left: auto;
        margin-right: auto;
    }
    .stApp {
        background: transparent !important;
    }
    .rate-box {
        display: flex;
        justify-content: space-around;
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        padding: 24px 0;
        margin-bottom: 16px;
    }
    .rate-item {
        text-align: center;
        min-width: 120px;
    }
    .rate-title {
        color: #888;
        font-size: 15px;
        margin-bottom: 4px;
    }
    .rate-main {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .rate-sub {
        color: #1a73e8;
        font-size: 16px;
        font-weight: bold;
    }
    .join-btn {
        width: 100%;
        background: #1a73e8;
        color: #fff;
        border: none;
        border-radius: 14px;
        padding: 18px 0;
        font-size: 22px;
        font-weight: bold;
        margin: 32px 0 24px 0;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(26,115,232,0.08);
        letter-spacing: 1px;
    }
    .goal-section {
        background: #fff;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .goal-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 6px;
    }
    .goal-desc {
        color: #888;
        margin-bottom: 12px;
    }
    .goal-btn {
        width: 100%;
        background: #f5f7fa;
        color: #222;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        margin-bottom: 8px;
        text-align: left;
    }
    .future-letter-btn {
        width: 100%;
        background: #ffe6b3;
        color: #b8860b;
        border: none;
        border-radius: 8px;
        padding: 14px;
        font-size: 17px;
        font-weight: bold;
        margin-bottom: 16px;
        cursor: pointer;
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        background: #f5f7fa;
        border-radius: 8px;
    }
    /* Make buttons and inputs touch-friendly */
    button, .stButton>button, .join-btn, .goal-btn, .future-letter-btn {
        min-height: 48px;
        font-size: 18px;
        border-radius: 12px;
    }
    /* Remove Streamlit's default padding */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    </style>
''', unsafe_allow_html=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('future_letters.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS future_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            letter_content TEXT NOT NULL,
            delivery_date DATE NOT NULL,
            created_date DATE NOT NULL,
            is_delivered BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

# Email sending function (user must fill in their SMTP credentials)
def send_email(to_email, subject, body):
    smtp_server = "smtp.gmail.com"  # Change if not using Gmail
    smtp_port = 587
    smtp_user = "e.factorials@gmail.com"  # <-- Put your email here
    smtp_password = "pzsa zdjd hake sdff"  # <-- Put your app password here

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email send failed:", e)
        return False

def main():
    # Top bar (simulate with columns)
    st.markdown('<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0 0 0;">'
                '<span style="font-size:22px;font-weight:bold;">한 달부터 적금</span>'
                '<span>'
                '<span style="margin-right:10px;">😊</span>'
                '<span style="margin-right:10px;">🎤</span>'
                '<span>🏠</span>'
                '</span>'
                '</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#7daed3;font-size:15px;margin-bottom:10px;">#일별주별 #1개월이상 #내맘대로</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="rate-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="rate-item">'
                    '<div class="rate-title">이자율</div>'
                    '<div class="rate-main">기본 연 <span style="color:#1a73e8;">2.05%</span></div>'
                    '<div class="rate-sub">최고 연 4.05%</div>'
                    '<div style="color:#888;font-size:13px;">(12개월 이내, 세전)</div>'
                    '</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="rate-item">'
                    '<div class="rate-title">저축한도</div>'
                    '<div class="rate-main">일 2만원 이내</div>'
                    '<div style="color:#888;font-size:13px;">(매일 입금 시)</div>'
                    '</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Join button
    if not st.session_state.get('joined', False):
        if st.button("가입하기", key="join_btn", help="가입하기", use_container_width=True):
            st.session_state['joined'] = True
        # Custom styled button (HTML for full control)
        # st.markdown('<button class="join-btn">가입하기</button>', unsafe_allow_html=True)
        st.markdown('<style>.join-btn {display:block;}</style>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align:center; margin-top:60px; font-size:22px; color:#1a73e8; font-weight:bold;">'
            '<br>적금 가입을 축하합니다 🎉'
            '</div>', unsafe_allow_html=True)
        if st.button("돌아가기", key="back_btn", help="돌아가기", use_container_width=True):
            st.session_state['joined'] = False
        st.stop()  # Prevents the rest of the page from rendering

    # Goal section
    st.markdown('<div class="goal-section">', unsafe_allow_html=True)
    st.markdown('<div class="goal-title">상황에 따라 필요한 목돈을 미리 준비해 보세요</div>', unsafe_allow_html=True)
    st.markdown('<div class="goal-desc">미래의 내가 뿌듯할 거예요.</div>', unsafe_allow_html=True)
    st.markdown('<button class="goal-btn">1년에 한 번, 생일 준비 🎂</button>', unsafe_allow_html=True)
    st.markdown('<button class="goal-btn">올해 여행 미리 계획하기 ✈️</button>', unsafe_allow_html=True)
    st.markdown('<button class="goal-btn">멋지게 효도하기 😎</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Future letter section
    st.markdown('<div class="goal-section">', unsafe_allow_html=True)
    st.markdown('<div class="goal-title">미래의 나에게 편지쓰기</div>', unsafe_allow_html=True)
    if st.button("미래의 나에게 편지 쓰기", key="future_letter_btn"):
        st.session_state['show_letter_form'] = True
    if st.session_state.get('show_letter_form', False):
        show_letter_form()
    st.markdown('</div>', unsafe_allow_html=True)

    # View letters section
    st.markdown('<div class="goal-section">', unsafe_allow_html=True)
    st.markdown('<div class="goal-title">내가 쓴 미래 편지 보기</div>', unsafe_allow_html=True)
    show_view_letters()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_letter_form():
    st.subheader("미래의 나에게 편지 쓰기")
    email = st.text_input("이메일 주소를 입력하세요", key="letter_email")
    letter_content = st.text_area("미래의 나에게 쓸 편지 내용을 입력하세요", height=150, key="letter_content")
    delivery_date = st.date_input("편지를 받을 날짜를 선택하세요", min_value=datetime.now().date(), key="letter_date")
    if st.button("미래의 나에게 편지 보내기", key="save_letter_btn"):
        if email and letter_content and delivery_date:
            save_letter(email, letter_content, delivery_date)
            # Send the email immediately (for demo; for real, schedule for delivery_date)
            subject = "미래의 나에게 쓴 편지"
            body = f"안녕하세요!\n\n아래는 신한은행에서 적금 가입하셨을 때 미래의 자신에게 쓴 편지입니다:\n\n{letter_content}\n\n도착 예정일: {delivery_date}"
            sent = send_email(email, subject, body)
            if sent:
                st.success("편지가 저장되었고 이메일로도 발송되었습니다!")
            else:
                st.warning("편지는 저장되었지만 이메일 발송에 실패했습니다.")
            st.session_state['show_letter_form'] = False
        else:
            st.error("모든 항목을 입력해주세요.")
    if st.button("취소", key="cancel_letter_btn"):
        st.session_state['show_letter_form'] = False

def show_view_letters():
    st.markdown(
        "<div style='margin-bottom:8px; color:#1a73e8; font-weight:bold;'>"
        "🔍 이메일 주소로 미래 편지를 조회할 수 있습니다."
        "</div>", unsafe_allow_html=True
    )
    email = st.text_input(
        "이메일 주소",
        placeholder="example@email.com",
        key="view_email"
    )
    if email:
        letters = get_letters(email)
        if letters:
            for letter in letters:
                with st.expander(f"{letter['created_date']} 작성 - {letter['delivery_date']} 도착 예정"):
                    st.write(letter['letter_content'])
                    st.write("상태:", "도착" if letter['is_delivered'] else "대기중")
        else:
            st.info("해당 이메일로 저장된 편지가 없습니다.")

def save_letter(email, content, delivery_date):
    conn = sqlite3.connect('future_letters.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO future_letters (email, letter_content, delivery_date, created_date)
        VALUES (?, ?, ?, ?)
    ''', (email, content, delivery_date, datetime.now().date()))
    conn.commit()
    conn.close()

def get_letters(email):
    conn = sqlite3.connect('future_letters.db')
    c = conn.cursor()
    c.execute('''
        SELECT letter_content, delivery_date, created_date, is_delivered
        FROM future_letters
        WHERE email = ?
        ORDER BY delivery_date DESC
    ''', (email,))
    letters = c.fetchall()
    conn.close()
    return [{
        'letter_content': letter[0],
        'delivery_date': letter[1],
        'created_date': letter[2],
        'is_delivered': letter[3]
    } for letter in letters]

if __name__ == "__main__":
    if 'show_letter_form' not in st.session_state:
        st.session_state['show_letter_form'] = False
    main() 