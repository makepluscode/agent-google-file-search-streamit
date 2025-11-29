"""
Gemini File Search 챗봇
Google Gemini File Search API를 활용한 문서 기반 질의응답 웹 애플리케이션
"""

import streamlit as st
from dotenv import load_dotenv

# 로컬 모듈 임포트
from config import PAGE_CONFIG, UPLOAD_CONFIG
from styles import get_custom_css
from gemini_api import initialize_client, create_store, upload_file, query_store
from utils import get_store_stats
from ui_components import (
    render_file_metadata_sidebar,
    render_source_citations,
    render_debug_info,
    render_file_metadata_detail,
    render_example_questions,
    render_footer
)

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(**PAGE_CONFIG)

# 커스텀 CSS 적용
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 세션 상태 초기화
if "client" not in st.session_state:
    st.session_state.client = None
if "store" not in st.session_state:
    st.session_state.store = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files_metadata" not in st.session_state:
    st.session_state.uploaded_files_metadata = []


# ============================================================================
# 메인 UI
# ============================================================================

st.title("🔍 Gemini File Search")
st.markdown("##### 문서 기반 질의응답 시스템")

# ============================================================================
# 사이드바
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ 설정")

    # 클라이언트 초기화
    if not st.session_state.client:
        with st.spinner("클라이언트 초기화 중..."):
            client, error = initialize_client()
            if client:
                st.session_state.client = client
                st.success("✓ 클라이언트 초기화 완료")
            else:
                st.error(f"❌ {error}")
                st.info("💡 .env 파일에 GEMINI_API_KEY를 설정해주세요")
                st.stop()
    else:
        st.success("✓ 클라이언트 연결됨")

    st.divider()

    # Store 관리
    st.markdown("### 📁 Store 관리")

    if not st.session_state.store:
        new_store_name = st.text_input(
            "Store 이름",
            value="Knowledge Base",
            placeholder="Store 이름을 입력하세요"
        )

        if st.button("🎯 Store 생성", use_container_width=True):
            with st.spinner("Store 생성 중..."):
                store, error = create_store(st.session_state.client, new_store_name)
                if store:
                    st.session_state.store = store
                    st.success(f"✓ Store 생성 완료")
                    st.rerun()
                else:
                    st.error(f"❌ 생성 실패: {error}")
    else:
        st.success(f"**활성 Store**")
        st.code(st.session_state.store.display_name)

        if st.button("🔄 새 Store 생성", use_container_width=True):
            st.session_state.store = None
            st.session_state.chat_history = []
            st.session_state.uploaded_files_metadata = []
            st.rerun()

    st.divider()

    # 업로드된 파일 목록
    if st.session_state.uploaded_files_metadata:
        st.markdown("### 📚 업로드된 파일")
        for idx, file_meta in enumerate(st.session_state.uploaded_files_metadata, 1):
            with st.expander(f"{idx}. {file_meta['filename']} ({file_meta['file_size_mb']} MB)"):
                render_file_metadata_sidebar(file_meta)

    st.divider()

    # 통계 및 작업
    if st.session_state.store:
        st.markdown("### 📊 통계")
        stats = get_store_stats(
            st.session_state.uploaded_files_metadata,
            st.session_state.chat_history
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("파일", stats["uploaded_files"])
            st.metric("대화", stats["chat_messages"])
        with col2:
            st.metric("총 크기", f"{stats['total_size_mb']:.1f} MB")
            if stats["total_tokens"] > 0:
                st.metric("총 토큰", f"~{stats['total_tokens']:,}")

        st.divider()

        # 채팅 초기화 버튼
        if st.session_state.chat_history:
            if st.button("🗑️ 채팅 기록 삭제", use_container_width=True, type="secondary"):
                st.session_state.chat_history = []
                st.success("채팅 기록이 삭제되었습니다")
                st.rerun()


# ============================================================================
# 메인 영역
# ============================================================================

if not st.session_state.store:
    st.info("👈 왼쪽 사이드바에서 Store를 생성해주세요")
    st.stop()

# 탭 생성
tab1, tab2 = st.tabs(["💬 질의응답", "📤 파일 업로드"])

# ============================================================================
# Tab 1: 질의응답
# ============================================================================

with tab1:
    # 시작 안내 (채팅 기록이 없을 때)
    if not st.session_state.chat_history:
        if st.session_state.uploaded_files_metadata:
            st.info("💡 **팁:** 업로드된 문서에 대해 자유롭게 질문해보세요!")
            render_example_questions()
        else:
            st.info("📤 먼저 '파일 업로드' 탭에서 문서를 업로드해주세요")

    # 채팅 히스토리 표시
    for chat in st.session_state.chat_history:
        with st.chat_message("user", avatar="👤"):
            st.markdown(chat["question"])

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(chat["answer"])

            # 인용 출처 표시
            if chat.get("debug_info") and chat["debug_info"].get("grounding_chunks"):
                chunks = chat["debug_info"]["grounding_chunks"]
                render_source_citations(chunks)

            # 디버깅 정보 표시
            if chat.get("debug_info") and chat["debug_info"].get("has_grounding"):
                render_debug_info(chat["debug_info"])

    # 질문 입력
    question = st.chat_input("질문을 입력하세요...", key="chat_input")

    if question:
        # 사용자 메시지 표시
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        # AI 답변 생성
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("답변 생성 중..."):
                answer, citations, debug_info, error = query_store(
                    st.session_state.client,
                    question,
                    st.session_state.store.name
                )

                if answer:
                    st.markdown(answer)

                    # 인용 출처 표시
                    if debug_info and debug_info.get("grounding_chunks"):
                        chunks = debug_info["grounding_chunks"]
                        render_source_citations(chunks)
                    else:
                        st.info("📚 업로드된 파일에서 관련 출처를 찾지 못했습니다. 파일을 업로드했는지 확인해주세요.")

                    # 디버깅 정보 표시
                    if debug_info:
                        render_debug_info(debug_info)

                    # 채팅 히스토리에 추가
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "citations": citations,
                        "debug_info": debug_info
                    })
                else:
                    st.error(f"❌ 오류 발생: {error}")


# ============================================================================
# Tab 2: 파일 업로드
# ============================================================================

with tab2:
    st.markdown("### 📤 파일 업로드")
    st.markdown("업로드된 파일은 자동으로 인덱싱되어 질의응답에 사용됩니다.")

    uploaded_files = st.file_uploader(
        "파일을 선택하세요 (PDF, TXT, DOCX, MD, CSV)",
        accept_multiple_files=True,
        type=UPLOAD_CONFIG["accepted_types"],
        help="여러 파일을 동시에 선택할 수 있습니다"
    )

    if uploaded_files:
        st.markdown(f"**선택된 파일:** {len(uploaded_files)}개")

        col1, col2 = st.columns([3, 1])
        with col2:
            upload_button = st.button("⬆️ 업로드 시작", type="primary", use_container_width=True)

        if upload_button:
            progress_bar = st.progress(0)
            status_text = st.empty()

            success_count = 0

            for i, file in enumerate(uploaded_files):
                status_text.markdown(f"**업로드 중:** `{file.name}`")

                success, file_metadata, error = upload_file(
                    st.session_state.client,
                    file,
                    st.session_state.store.name
                )

                if success:
                    st.success(f"✓ {file.name} 업로드 완료")
                    st.session_state.uploaded_files_metadata.append(file_metadata)
                    success_count += 1
                else:
                    st.error(f"✗ {file.name}: {error}")

                progress_bar.progress((i + 1) / len(uploaded_files))

            status_text.markdown(f"**완료:** {success_count}/{len(uploaded_files)}개 파일 업로드 성공")
            st.balloons()

    st.divider()

    # 업로드된 파일 메타데이터 영구 표시
    if st.session_state.uploaded_files_metadata:
        st.markdown("### 📊 업로드된 파일 상세 정보")
        st.markdown(f"총 **{len(st.session_state.uploaded_files_metadata)}개** 파일이 업로드되었습니다.")

        for idx, file_metadata in enumerate(st.session_state.uploaded_files_metadata, 1):
            with st.expander(f"{idx}. {file_metadata['filename']} ({file_metadata['file_size_mb']} MB)", expanded=False):
                render_file_metadata_detail(file_metadata)


# ============================================================================
# 푸터
# ============================================================================

render_footer()
