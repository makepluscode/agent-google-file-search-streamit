"""UI 스타일 정의"""

from config import COLORS


def get_custom_css():
    """커스텀 CSS 스타일을 반환합니다."""
    return f"""
<style>
    /* 전체 배경 */
    .stApp {{
        background-color: {COLORS['background']};
    }}

    /* 사이드바 */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['sidebar']};
        border-right: 1px solid {COLORS['card']};
    }}

    /* 메인 컨텐츠 영역 */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}

    /* 제목 스타일 */
    h1 {{
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}

    h2, h3 {{
        color: {COLORS['text']};
        font-weight: 600;
    }}

    /* 입력 필드 */
    .stTextInput input, .stTextArea textarea {{
        background-color: {COLORS['card']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
    }}

    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {COLORS['accent']};
        box-shadow: 0 0 0 1px {COLORS['accent']};
    }}

    /* 버튼 */
    .stButton button {{
        background-color: {COLORS['accent']};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }}

    .stButton button:hover {{
        background-color: {COLORS['accent_hover']};
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }}

    /* 탭 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {COLORS['sidebar']};
        padding: 0.5rem;
        border-radius: 10px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: #808080;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['card']};
        color: {COLORS['accent']};
    }}

    /* 채팅 메시지 */
    .stChatMessage {{
        background-color: {COLORS['sidebar']};
        border: 1px solid {COLORS['card']};
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {COLORS['card']};
        border-radius: 8px;
        color: {COLORS['text']};
    }}

    /* 파일 업로더 */
    .stFileUploader {{
        background-color: {COLORS['sidebar']};
        border: 2px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 2rem;
    }}

    /* 성공/에러/정보 메시지 */
    .stSuccess {{
        background-color: #1a2e1a;
        color: {COLORS['success']};
        border-left: 4px solid {COLORS['success']};
    }}

    .stError {{
        background-color: #2e1a1a;
        color: {COLORS['error']};
        border-left: 4px solid {COLORS['error']};
    }}

    .stInfo {{
        background-color: #1a1f2e;
        color: {COLORS['info']};
        border-left: 4px solid {COLORS['info']};
    }}

    /* 구분선 */
    hr {{
        border-color: {COLORS['card']};
    }}

    /* 프로그레스 바 */
    .stProgress > div > div {{
        background-color: {COLORS['accent']};
    }}
</style>
"""
