"""애플리케이션 설정 및 상수"""

# 페이지 설정
PAGE_CONFIG = {
    "page_title": "Gemini File Search",
    "page_icon": "🔍",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 색상 팔레트
COLORS = {
    "background": "#0f0f0f",
    "sidebar": "#1a1a1a",
    "card": "#2a2a2a",
    "border": "#3a3a3a",
    "text": "#e0e0e0",
    "accent": "#6366f1",
    "accent_hover": "#5558e3",
    "success": "#4ade80",
    "error": "#f87171",
    "info": "#60a5fa"
}

# 청킹 설정
CHUNKING_CONFIG = {
    "max_tokens_per_chunk": 400,
    "max_overlap_tokens": 40,
    "chunking_method": "white_space"
}

# Gemini 모델 설정
MODEL_CONFIG = {
    "model_name": "gemini-2.5-flash",
    "temperature": 0.2
}

# 파일 업로드 설정
UPLOAD_CONFIG = {
    "accepted_types": ["pdf", "txt", "docx", "md", "csv"],
    "text_extensions": ['.txt', '.md', '.csv', '.json', '.xml', '.html']
}
