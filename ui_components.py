"""UI 컴포넌트 함수들"""

import streamlit as st


def render_file_metadata_sidebar(file_meta):
    """사이드바에 파일 메타데이터를 렌더링합니다."""
    st.markdown(f"**파일 크기:** {file_meta['file_size_bytes']:,} bytes ({file_meta['file_size_mb']} MB)")
    st.markdown(f"**파일 타입:** `{file_meta['file_type']}`")

    if file_meta.get('character_count') and file_meta['character_count'] != "N/A (binary file)":
        st.markdown(f"**문자 수:** {file_meta['character_count']:,}")
        st.markdown(f"**단어 수:** {file_meta['word_count']:,}")

    if isinstance(file_meta.get('estimated_tokens'), int):
        st.markdown(f"**추정 토큰:** ~{file_meta['estimated_tokens']:,}")
        st.markdown(f"**추정 청크:** ~{file_meta['estimated_chunks']}")

    st.markdown(f"**업로드 시간:** {file_meta['upload_duration_seconds']}초")


def render_source_citations(chunks):
    """검색된 출처를 렌더링합니다."""
    with st.expander(f"📚 검색된 출처 ({len(chunks)}개)", expanded=False):
        for chunk in chunks:
            st.markdown(f"### 출처 {chunk['index']}")

            if "retrieved_context" in chunk:
                ctx = chunk["retrieved_context"]

                if "title" in ctx:
                    st.markdown(f"**📌 제목:** {ctx['title']}")
                if "uri" in ctx:
                    st.markdown(f"**🔗 파일:** `{ctx['uri']}`")
                if "text" in ctx:
                    st.markdown("**📝 참조 텍스트:**")
                    text = ctx['text']
                    if len(text) > 500:
                        st.info(text[:500] + "...")
                        with st.expander("전체 텍스트 보기"):
                            st.code(text, language=None)
                    else:
                        st.info(text)
            else:
                st.warning("출처 정보를 찾을 수 없습니다.")

            if chunk['index'] < len(chunks):
                st.divider()


def render_debug_info(debug_info):
    """디버깅 정보를 렌더링합니다."""
    with st.expander("🔍 상세 디버깅 정보 (전체)", expanded=False):
        st.markdown("### Debug Info 전체 구조")
        st.json(debug_info)

    if debug_info.get("has_grounding"):
        with st.expander("🔍 Grounding 상세 정보", expanded=False):
            # Grounding Chunks 표시
            if debug_info.get("grounding_chunks"):
                st.markdown("## 📦 검색된 문서 청크 (Grounding Chunks)")
                st.markdown("AI가 답변을 생성할 때 참조한 문서 조각들입니다.")

                for chunk in debug_info["grounding_chunks"]:
                    st.markdown(f"### Chunk {chunk['index']}")

                    if "retrieved_context" in chunk:
                        ctx = chunk["retrieved_context"]

                        if "title" in ctx:
                            st.markdown(f"**📌 제목:** {ctx['title']}")
                        if "uri" in ctx:
                            st.markdown(f"**🔗 URI:** `{ctx['uri']}`")
                        if "text" in ctx:
                            st.markdown("**📄 텍스트 내용:**")
                            st.code(ctx['text'], language=None)

                    st.divider()

            # Grounding Supports 표시
            if debug_info.get("grounding_supports"):
                st.markdown("## 🎯 답변 근거 (Grounding Supports)")
                st.markdown("답변의 각 부분이 어떤 문서 청크를 참조했는지 보여줍니다.")

                for support in debug_info["grounding_supports"]:
                    st.markdown(f"### Support {support['index']}")

                    if "segment" in support:
                        seg = support["segment"]
                        st.markdown("**📝 답변 텍스트:**")
                        st.info(seg.get("text", ""))
                        if seg.get("start_index") is not None:
                            st.markdown(f"**위치:** {seg['start_index']} ~ {seg.get('end_index', 'N/A')}")

                    if "chunk_indices" in support:
                        st.markdown(f"**📦 참조 청크:** {support['chunk_indices']}")

                    if "confidence_scores" in support:
                        st.markdown(f"**신뢰도:** {support['confidence_scores']}")

                    st.divider()


def render_file_metadata_detail(file_metadata):
    """파일 메타데이터 상세 정보를 렌더링합니다."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("파일 크기", f"{file_metadata['file_size_mb']} MB")
        if isinstance(file_metadata.get('estimated_tokens'), int):
            st.metric("추정 토큰", f"{file_metadata['estimated_tokens']:,}")

    with col2:
        if file_metadata.get('character_count') and file_metadata['character_count'] != "N/A (binary file)":
            st.metric("문자 수", f"{file_metadata['character_count']:,}")
        if file_metadata.get('word_count') != "N/A":
            st.metric("단어 수", f"{file_metadata['word_count']:,}")

    with col3:
        if isinstance(file_metadata.get('estimated_chunks'), int):
            st.metric("추정 청크", f"{file_metadata['estimated_chunks']}")
        st.metric("업로드 시간", f"{file_metadata['upload_duration_seconds']}초")

    # 청킹 설정 표시
    st.markdown("**⚙️ 청킹 설정:**")
    chunking = file_metadata['chunking_config']
    st.code(f"""
청킹 방식: {chunking['chunking_method']}
최대 토큰/청크: {chunking['max_tokens_per_chunk']}
오버랩 토큰: {chunking['max_overlap_tokens']}
    """.strip())

    # Operation 결과 (고급 정보)
    if file_metadata.get('operation_result') or file_metadata.get('operation_metadata'):
        with st.expander("🔍 Gemini API 응답 (고급)"):
            if file_metadata.get('operation_result'):
                st.markdown("### Operation Result")
                st.json(file_metadata['operation_result'])

            if file_metadata.get('operation_metadata'):
                st.markdown("### Operation Metadata")
                st.json(file_metadata['operation_metadata'])


def render_example_questions():
    """예시 질문을 렌더링합니다."""
    with st.expander("📝 질문 예시 보기"):
        st.markdown("""
        - 이 문서의 주요 내용을 요약해주세요
        - [특정 주제]에 대해 설명해주세요
        - [키워드]가 언급된 부분을 찾아주세요
        - [개념A]와 [개념B]의 차이점은 무엇인가요?
        - 문서에서 중요한 숫자나 통계가 있나요?
        """)


def render_footer():
    """푸터를 렌더링합니다."""
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #808080; font-size: 0.9em; padding: 1rem 0;'>
            <p>Powered by <strong>Google Gemini 2.5 Flash</strong> & <strong>Streamlit</strong></p>
            <p>💡 Tip: Ctrl+K to focus chat input | Ctrl+L to clear (사이드바 버튼 사용)</p>
        </div>
        """,
        unsafe_allow_html=True
    )
