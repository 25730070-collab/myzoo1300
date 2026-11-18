# -*- coding: utf-8 -*-
"""
여행 숙소 성향 테스트 (Streamlit)
- MBTI처럼 4가지 양극 성향을 조합해 16가지 유형으로 분류
- 실행: streamlit run app.py
- 필요 패키지: streamlit>=1.36, pandas
"""

import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────
# 1. 페이지 설정 & 밝은 보라색 테마 (CSS)
# ─────────────────────────────────────────────
st.set_page_config(page_title="여행 숙소 성향 테스트", page_icon="🛎️", layout="centered")

st.markdown(
    """
    <style>
    /* 전체 배경: 밝은 보라 그라데이션 */
    .stApp { background: linear-gradient(180deg, #f5efff 0%, #fbf8ff 100%); }
    /* 질문 카드 (border=True 컨테이너) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border: 1px solid #e3d4fb !important;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(124, 77, 255, 0.10);
    }
    /* 버튼 */
    .stButton > button {
        background: #8b5cf6; color: white; border: none;
        border-radius: 12px; padding: 0.6rem 1.4rem; font-weight: 700;
    }
    .stButton > button:hover { background: #7c3aed; color: white; }
    .stButton > button:disabled { background: #d9c9fb; color: #fff; }
    /* 진행률 바 색상 */
    .stProgress > div > div > div > div { background-color: #8b5cf6; }
    h1, h2, h3 { color: #5b21b6; }
    .type-box {
        background: linear-gradient(135deg, #ede4ff, #f8f3ff);
        border-radius: 20px; padding: 1.6rem; text-align: center;
        border: 1px solid #d8c4fb;
    }
    .type-code { font-size: 2.6rem; font-weight: 800; color: #6d28d9; letter-spacing: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# 2. 성향 축 정의 (각 축은 왼쪽 극 ↔ 오른쪽 극)
# ─────────────────────────────────────────────
AXES = [
    {"name": "소비 성향", "left": ("E", "가성비"), "right": ("P", "프리미엄")},
    {"name": "입지 성향", "left": ("L", "위치·효율"), "right": ("V", "감성·분위기")},
    {"name": "활동 성향", "left": ("R", "휴식"), "right": ("A", "활동")},
    {"name": "계획 성향", "left": ("C", "계획형"), "right": ("S", "즉흥형")},
]

# ─────────────────────────────────────────────
# 3. 16가지 결과 유형 (코드 순서: 소비-입지-활동-계획)
# ─────────────────────────────────────────────
TYPES = {
    "ELRC": ("🎯", "알뜰 플래너", "가성비 + 효율 + 휴식 + 계획", "꼼꼼하게 준비하고 숙소에서 편하게 쉬는 실속형", "역세권 비즈니스호텔, 조식 포함 중가 호텔"),
    "ELRS": ("🧳", "가벼운 실속 휴식러", "가성비 + 효율 + 휴식 + 즉흥", "마음 가는 대로 떠나 가까운 숙소에서 푹 쉬는 실속형", "당일 특가 호텔, 역 근처 게스트하우스"),
    "ELAC": ("🗺️", "동선 마스터", "가성비 + 효율 + 활동 + 계획", "숙소는 거점, 동선을 촘촘히 짜서 알차게 누비는 타입", "중심가 호스텔, 교통 요지 저가 호텔"),
    "ELAS": ("🎒", "뚜벅이 모험가", "가성비 + 효율 + 활동 + 즉흥", "가방 하나 메고 발길 닿는 대로, 잠은 가까운 곳에서", "도미토리, 캡슐호텔, 야간 체크인 숙소"),
    "EVRC": ("📓", "감성 알뜰 기록가", "가성비 + 감성 + 휴식 + 계획", "합리적 가격의 분위기 좋은 숙소를 미리 찾아두는 타입", "한옥 스테이, 감성 독채 펜션"),
    "EVRS": ("🌿", "소확행 힐러", "가성비 + 감성 + 휴식 + 즉흥", "우연히 만난 아늑한 숙소에서 소소한 행복을 느끼는 타입", "동네 게스트하우스, 작은 민박"),
    "EVAC": ("📸", "가성비 감성 탐험가", "가성비 + 감성 + 활동 + 계획", "예쁜 곳을 알뜰하게 엮어 계획적으로 다니는 타입", "에어비앤비 로컬 숙소, 감성 호스텔"),
    "EVAS": ("🎈", "자유로운 방랑자", "가성비 + 감성 + 활동 + 즉흥", "그날그날 끌리는 곳에서 자유롭게 머무는 타입", "캠핑, 글램핑, 로컬 게스트하우스"),
    "PLRC": ("🏨", "호텔 정석 매니저", "프리미엄 + 효율 + 휴식 + 계획", "좋은 위치의 검증된 고급 호텔을 미리 확보하는 타입", "도심 5성급 호텔, 라운지 이용 가능 객실"),
    "PLRS": ("🥂", "시티뷰 럭셔리 힐러", "프리미엄 + 효율 + 휴식 + 즉흥", "마음 내키면 도심 고급 호텔에서 호캉스를 즐기는 타입", "시티뷰 스위트, 호캉스 패키지"),
    "PLAC": ("🚀", "프로 일정 설계자", "프리미엄 + 효율 + 활동 + 계획", "편안한 거점 호텔에서 완벽한 일정으로 움직이는 타입", "관광지 인근 프리미엄 호텔"),
    "PLAS": ("⚡", "도심 즉흥 플레이어", "프리미엄 + 효율 + 활동 + 즉흥", "좋은 위치의 숙소를 즉석에서 잡고 도시를 즐기는 타입", "번화가 부티크 호텔, 루프탑 호텔"),
    "PVRC": ("🛁", "리조트 완벽주의자", "프리미엄 + 감성 + 휴식 + 계획", "분위기와 시설을 꼼꼼히 따져 완벽한 휴식을 설계하는 타입", "풀빌라, 럭셔리 리조트"),
    "PVRS": ("🌴", "오션뷰 로열 힐러", "프리미엄 + 감성 + 휴식 + 즉흥", "눈 앞에 펼쳐진 뷰에 끌려 바로 머무르는 타입", "오션뷰 리조트, 온천 료칸"),
    "PVAC": ("🎨", "부티크 컬렉터", "프리미엄 + 감성 + 활동 + 계획", "개성 있는 숙소를 수집하듯 계획해 다니는 타입", "디자인 호텔, 부티크 호텔"),
    "PVAS": ("🦋", "럭셔리 노마드", "프리미엄 + 감성 + 활동 + 즉흥", "분위기 좋은 최고의 숙소를 따라 자유롭게 이동하는 타입", "스위트 호텔, 프라이빗 빌라"),
}

# ─────────────────────────────────────────────
# 4. 질문 10개
#   axis: 소속 축 인덱스 / kind: radio 또는 slider
#   radio  → 선택지 2개 (왼쪽 극 / 오른쪽 극)
#   slider → 1~5 (1=왼쪽 극, 5=오른쪽 극)
# ─────────────────────────────────────────────
QUESTIONS = [
    {"axis": 0, "kind": "radio", "q": "숙소 예산을 정할 때 나는?",
     "opts": ["같은 돈이면 다른 곳에 더 쓰고, 숙소는 잠만 자면 OK", "숙소가 여행의 하이라이트! 조금 더 내도 좋은 곳이 좋다"]},
    {"axis": 0, "kind": "slider", "q": "1박 가격이 2배라도 시설과 서비스가 훨씬 좋다면?",
     "labels": ("절대 안 낸다", "기꺼이 낸다")},
    {"axis": 0, "kind": "radio", "q": "후기와 가격이 이렇게 다르다면 어느 쪽?",
     "opts": ["평점 4.2점, 가격이 저렴한 숙소", "평점 4.8점, 가격이 비싼 숙소"]},
    {"axis": 1, "kind": "slider", "q": "숙소를 고를 때 더 중요한 것은?",
     "labels": ("교통·접근성", "분위기·인테리어")},
    {"axis": 1, "kind": "radio", "q": "두 숙소 중 하나를 고른다면?",
     "opts": ["역에서 도보 3분, 평범한 숙소", "역에서 멀지만 뷰가 멋진 숙소"]},
    {"axis": 1, "kind": "slider", "q": "사진이 예쁘게 나오는 숙소인지가 나에게 얼마나 중요한가요?",
     "labels": ("전혀 중요하지 않다", "매우 중요하다")},
    {"axis": 2, "kind": "radio", "q": "여행 중 숙소에서 보내는 시간은?",
     "opts": ["수영장·침대에서 푹 쉬며 오래 머문다", "짐만 두고 잠깐 들렀다가 바로 나간다"]},
    {"axis": 2, "kind": "slider", "q": "낮 시간 일정은 어떤 스타일인가요?",
     "labels": ("숙소에서 여유롭게 쉬기", "쉴 틈 없이 돌아다니기")},
    {"axis": 3, "kind": "radio", "q": "숙소 예약은 보통 언제 하나요?",
     "opts": ["몇 달 전부터 비교해서 미리 예약한다", "출발 직전이나 현지에서 정한다"]},
    {"axis": 3, "kind": "slider", "q": "환불 불가 특가 vs 무료 취소 가능 요금, 나의 선택은?",
     "labels": ("일정 확정! 환불불가로 싸게", "취소 가능한 쪽이 마음 편하다")},
]
TOTAL = len(QUESTIONS)


# ─────────────────────────────────────────────
# 5. 상태 관리 함수
# ─────────────────────────────────────────────
def init_state():
    st.session_state.setdefault("submitted", False)
    st.session_state.setdefault("touched", set())  # 슬라이더를 움직여 응답한 질문 번호


def touch(i):
    """슬라이더 값을 건드렸을 때 '응답함'으로 기록 (콜백)"""
    st.session_state["touched"].add(i)


def is_answered(i):
    if QUESTIONS[i]["kind"] == "radio":
        return st.session_state.get(f"q{i}") is not None
    return i in st.session_state["touched"]


def reset_test():
    """다시 검사하기: 모든 응답과 결과 초기화 (콜백)"""
    for i in range(TOTAL):
        st.session_state.pop(f"q{i}", None)
    st.session_state["touched"] = set()
    st.session_state["submitted"] = False


def submit():
    st.session_state["submitted"] = True


def get_value(i):
    """질문 응답을 1~5 값으로 변환 (1=왼쪽 극, 5=오른쪽 극)"""
    q = QUESTIONS[i]
    ans = st.session_state.get(f"q{i}")
    if q["kind"] == "radio":
        return 1 if ans == q["opts"][0] else 5
    return ans


def calc_scores():
    """축별 오른쪽 극 비율(%)을 계산 -> 50% 미만이면 왼쪽 극 (동점은 왼쪽 극)"""
    sums = {a: [] for a in range(len(AXES))}
    for i, q in enumerate(QUESTIONS):
        sums[q["axis"]].append((get_value(i) - 1) / 4 * 100)  # 1→0%, 5→100%
    results = []
    for a, axis in enumerate(AXES):
        right = sum(sums[a]) / len(sums[a])
        left = 100 - right
        letter = axis["right"][0] if right > 50 else axis["left"][0]
        results.append({"axis": axis, "left": left, "right": right, "letter": letter})
    return results


# ─────────────────────────────────────────────
# 6. 화면: 질문 페이지
# ─────────────────────────────────────────────
def render_test():
    st.title("🛎️ 여행 숙소 성향 테스트")
    st.write("10개의 질문에 답하면 나의 **여행 숙소 유형**을 알려드려요.")

    # 전체 응답 진행률
    done = sum(is_answered(i) for i in range(TOTAL))
    st.progress(done / TOTAL, text=f"응답 진행률 {done} / {TOTAL}")

    for i, q in enumerate(QUESTIONS):
        with st.container(border=True):  # 질문별 카드
            st.markdown(f"**Q{i + 1}. {q['q']}**")
            if q["kind"] == "radio":
                st.radio("선택", q["opts"], index=None, key=f"q{i}", label_visibility="collapsed")
            else:
                st.slider("선택", 1, 5, 3, key=f"q{i}", label_visibility="collapsed",
                          on_change=touch, args=(i,))
                st.caption(f"1 = {q['labels'][0]}  ·  5 = {q['labels'][1]}")

    st.button("결과 보기 ✨", on_click=submit, disabled=(done < TOTAL))
    if done < TOTAL:
        st.caption("모든 질문에 답하면 결과 보기 버튼이 활성화돼요. (슬라이더는 한 번 움직여야 응답으로 인정)")


# ─────────────────────────────────────────────
# 7. 화면: 결과 페이지
# ─────────────────────────────────────────────
def render_result():
    scores = calc_scores()
    code = "".join(s["letter"] for s in scores)
    emoji, name, combo, desc, stays = TYPES[code]

    st.title("🎉 나의 여행 숙소 유형")
    st.markdown(
        f"""
        <div class="type-box">
            <div style="font-size:3rem">{emoji}</div>
            <div class="type-code">{code}</div>
            <h2 style="margin:0.2rem 0">{name}</h2>
            <div style="color:#7c3aed;font-weight:600">{combo}</div>
            <p style="margin-top:0.8rem">{desc}</p>
            <p style="margin:0">🏠 <b>어울리는 숙소</b> : {stays}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4가지 성향 그래프 (왼쪽 극 % / 오른쪽 극 %를 가로 막대로 표시)
    st.subheader("📊 4가지 성향 분석")
    rows, labels = [], []
    for s in scores:
        a = s["axis"]
        labels.append(f"{a['name']} ({a['left'][1]} ↔ {a['right'][1]})")
        rows.append({"왼쪽 성향(%)": round(s["left"], 1), "오른쪽 성향(%)": round(s["right"], 1)})
    df = pd.DataFrame(rows, index=labels)
    st.bar_chart(df, horizontal=True, color=["#8b5cf6", "#d8b4fe"])

    for s in scores:
        a = s["axis"]
        st.write(
            f"**{a['name']}** — {a['left'][0]} {a['left'][1]} {s['left']:.0f}%  |  "
            f"{a['right'][0]} {a['right'][1]} {s['right']:.0f}%  →  **{s['letter']}**"
        )

    st.button("🔄 다시 검사하기", on_click=reset_test)


# ─────────────────────────────────────────────
# 8. 메인
# ─────────────────────────────────────────────
init_state()
if st.session_state["submitted"]:
    render_result()
else:
    render_test()
