"""유틸리티 함수들"""


def get_store_stats(uploaded_files_metadata, chat_history):
    """현재 Store의 통계 정보를 반환합니다."""
    stats = {
        "uploaded_files": len(uploaded_files_metadata),
        "total_size_mb": sum(f.get("file_size_mb", 0) for f in uploaded_files_metadata),
        "total_tokens": sum(
            f.get("estimated_tokens", 0) if isinstance(f.get("estimated_tokens"), int) else 0
            for f in uploaded_files_metadata
        ),
        "chat_messages": len(chat_history)
    }
    return stats
