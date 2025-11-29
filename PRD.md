# PRD: Gemini File Search 챗봇

## 개요
Google Gemini File Search API를 활용한 문서 기반 질의응답 웹 애플리케이션

## 목표
- 복잡한 벡터DB 설정 없이 문서를 업로드하고 질문할 수 있는 시스템 구축
- Streamlit 기반의 직관적이고 모던한 UI 제공
- RAG 시스템의 투명성 확보 (출처 추적 및 디버깅 정보 제공)
- 상세한 파일 메타데이터 수집 및 표시

## 핵심 기능

### 1. 환경 설정
- .env 파일에서 GEMINI_API_KEY 자동 로드
- uv 패키지 관리자 사용
- pyproject.toml 기반 의존성 관리

### 2. Store 관리
- File Search Store 생성
- Store 이름 커스터마이징
- 현재 활성 Store 표시

### 3. 파일 업로드
- 다중 파일 동시 업로드 (PDF, TXT, DOCX, MD, CSV)
- 임시 파일 처리 및 자동 정리
- Chunking 설정:
  - max_tokens_per_chunk: 400
  - max_overlap_tokens: 40
  - chunking_method: white_space
- 업로드 진행률 표시
- 비동기 업로드 작업 완료 대기
- **상세한 파일 메타데이터 수집:**
  - 파일 크기 (bytes, MB)
  - 문자 수, 단어 수 (텍스트 파일)
  - 추정 토큰 수
  - 추정 청크 개수
  - 업로드 소요 시간
  - Operation result 및 metadata
- **메타데이터 영구 표시:**
  - 사이드바에 업로드된 파일 목록 및 간단한 정보
  - 파일 업로드 탭에 상세 메타데이터 표시
  - 청킹 설정 및 Gemini API 응답 정보 제공

### 4. 질의응답
- 자연어 질문 입력
- Gemini 2.5 Flash 모델 사용
- Temperature 0.2로 일관된 답변
- 채팅 히스토리 관리 (세션 지속)
- **상세한 출처 추적:**
  - Grounding Chunks: AI가 참조한 문서 조각들 표시
  - 각 출처의 제목, URI, 참조 텍스트 제공
  - 긴 텍스트는 요약 + 확장 가능
- **디버깅 정보:**
  - Debug Info 전체 구조 (JSON)
  - Grounding Chunks 상세 정보
  - Grounding Supports (답변-청크 매핑)
  - Citations 데이터
  - has_grounding 플래그로 그라운딩 여부 확인

### 5. UI 구성
**디자인 컨셉:**
- 모던 다크 테마 (무채색 기반)
- 강조 색상: 인디고 (#6366f1)
- 반응형 레이아웃
- 직관적인 정보 계층화

**사이드바:**
- ⚙️ 설정 섹션
  - 클라이언트 초기화 상태 표시
- 📁 Store 관리 섹션
  - Store 생성 UI
  - 현재 Store 정보 표시
  - 새 Store 생성 버튼
- 📚 업로드된 파일 목록
  - 파일명, 크기 표시
  - Expander로 간단한 메타데이터 확인

**메인 영역:**
- 2개 탭 구조
  - Tab 1: 💬 질의응답
    - 채팅 인터페이스 (사용자/AI 메시지)
    - 검색된 출처 Expander (auto-expand)
    - 디버깅 정보 Expander
  - Tab 2: 📤 파일 업로드
    - 파일 선택 UI
    - 업로드 진행률 바
    - 업로드된 파일 상세 정보 (영구 표시)
    - 메트릭 카드 (파일 크기, 토큰, 청크 등)
    - 청킹 설정 및 Operation 결과

## 기술 스택

### 패키지 관리
- **uv**: 빠른 Python 패키지 관리자
- **pyproject.toml**: 프로젝트 의존성 정의

### 백엔드
- **Python 3.9+**
- **google-genai**: Gemini API 연동
- **python-dotenv**: .env 파일 환경변수 로드

### 프론트엔드
- **Streamlit**: 웹 UI 프레임워크
- 페이지 설정:
  - page_title: "Gemini File Search"
  - page_icon: "🔍"
  - layout: "wide"
  - initial_sidebar_state: "expanded"

### UI 디자인
- **커스텀 CSS**: Streamlit markdown으로 주입
- **색상 팔레트**:
  - 배경: #0f0f0f (다크 블랙)
  - 사이드바: #1a1a1a
  - 카드/입력: #2a2a2a
  - 텍스트: #e0e0e0
  - 강조: #6366f1 (인디고)
  - 성공: #4ade80 (그린)
  - 에러: #f87171 (레드)
  - 정보: #60a5fa (블루)
- **컴포넌트 스타일링**:
  - 둥근 모서리 (border-radius: 8-12px)
  - 부드러운 전환 효과 (transition: 0.2s)
  - 호버 효과 (shadow, color change)
  - 일관된 패딩 및 간격

## 프로젝트 구조

```
google-search-api-streamit/
├── .env                    # API Key 저장 (git ignore)
├── .env.example           # 환경변수 템플릿
├── pyproject.toml         # uv 프로젝트 설정
├── .gitignore
├── PRD.md
├── README.md
└── app.py                 # Streamlit 앱 메인 파일
```

## 환경 변수

**.env 파일:**
```
GEMINI_API_KEY=your_api_key_here
```

## 의존성 (pyproject.toml)

```toml
[project]
name = "google-search-api-streamit"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "streamlit",
    "google-genai",
    "python-dotenv"
]
```

## 데이터 모델

### 세션 상태
```python
{
  "client": genai.Client,
  "store": FileSearchStore 객체 또는 None,
  "chat_history": [
    {
      "question": str,
      "answer": str,
      "citations": list,
      "debug_info": {
        "has_grounding": bool,
        "grounding_chunks": [
          {
            "index": int,
            "retrieved_context": {
              "title": str,
              "uri": str,
              "text": str
            }
          }
        ],
        "grounding_supports": [
          {
            "index": int,
            "segment": {
              "text": str,
              "start_index": int,
              "end_index": int
            },
            "chunk_indices": list,
            "confidence_scores": list
          }
        ],
        "citations": list
      }
    }
  ],
  "uploaded_files_metadata": [
    {
      "filename": str,
      "file_size_bytes": int,
      "file_size_mb": float,
      "file_type": str,
      "character_count": int or "N/A",
      "word_count": int or "N/A",
      "estimated_tokens": int or "N/A",
      "estimated_chunks": int or "N/A",
      "upload_duration_seconds": float,
      "chunking_config": {
        "max_tokens_per_chunk": 400,
        "max_overlap_tokens": 40,
        "chunking_method": "white_space"
      },
      "operation_result": dict,
      "operation_metadata": dict
    }
  ]
}
```

## 주요 함수

### 1. initialize_client()
- .env에서 GEMINI_API_KEY 로드
- genai.Client 초기화
- 반환: (client, error)

### 2. create_store(client, store_name)
- File Search Store 생성
- display_name 설정
- 반환: (store, error)

### 3. upload_file(client, file, store_name)
- 파일을 임시 저장 후 업로드
- **상세 메타데이터 수집:**
  - 파일 정보 (이름, 크기, 타입)
  - 텍스트 분석 (문자/단어/토큰 수)
  - 청크 추정
  - 업로드 시간 측정
  - Operation result/metadata
- chunking_config 적용
- 임시 파일 자동 정리
- 반환: (success, file_metadata, error)

### 4. query_store(client, question, store_name)
- Gemini 2.5 Flash 모델로 질의
- File Search Tool 사용
- **디버깅 정보 수집:**
  - grounding_metadata 파싱
  - grounding_chunks 추출 및 변환
  - grounding_supports 수집
  - citations 수집
- 반환: (answer, citations, debug_info, error)

## 사용자 플로우

### 초기 설정
1. .env 파일에 GEMINI_API_KEY 설정
2. uv로 의존성 설치 (`uv sync`)
3. Streamlit 앱 실행 (`uv run streamlit run app.py`)

### 앱 사용
4. **클라이언트 초기화**: 자동으로 .env에서 API Key 로드
5. **Store 생성**:
   - 사이드바에서 Store 이름 입력
   - "🎯 Store 생성" 버튼 클릭
6. **파일 업로드** (📤 파일 업로드 탭):
   - 파일 선택 (여러 개 가능)
   - "⬆️ 업로드 시작" 클릭
   - 진행률 및 메타데이터 확인
   - 사이드바에서 업로드된 파일 목록 확인
7. **질문하기** (💬 질의응답 탭):
   - 채팅 입력창에 질문 입력
   - 답변 확인
   - 📚 검색된 출처 확인 (자동 확장)
   - 🔍 디버깅 정보 확인 (선택적)
8. **메타데이터 확인**:
   - 사이드바에서 간단한 파일 정보
   - 파일 업로드 탭에서 상세 메타데이터
   - 토큰 수, 청크 개수, 업로드 시간 등

## 설치 및 실행

```bash
# 1. uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. .env 파일 생성
cp .env.example .env
# GEMINI_API_KEY 설정

# 3. 의존성 설치
uv sync

# 4. 앱 실행
uv run streamlit run app.py
```

## 에러 핸들링

- .env 파일 없을 시 에러 메시지 표시
- API Key 없을 시 초기화 실패 알림
- Store 생성 실패 시 에러 메시지 표시
- 파일 업로드 실패 시 파일별 에러 표시
- 임시 파일 자동 정리 (업로드 완료 후)

## 개발 우선순위

### Phase 1 (MVP) ✅ 완료
- [x] 프로젝트 초기 설정 (pyproject.toml, .env.example)
- [x] Streamlit 기본 구조
- [x] .env에서 API Key 로드
- [x] Store 생성 기능
- [x] 파일 업로드 (단일)
- [x] 기본 질의응답
- [x] 채팅 히스토리

### Phase 2 ✅ 완료
- [x] 다중 파일 업로드
- [x] 인용 출처 표시
- [x] 진행률 바
- [x] 에러 핸들링 개선

### Phase 3 (고급 기능) ✅ 완료
- [x] 모던 다크 테마 UI
- [x] 상세한 파일 메타데이터 수집
- [x] 메타데이터 영구 표시 (사이드바 + 메인 탭)
- [x] Grounding chunks/supports 추적
- [x] 디버깅 정보 UI 통합
- [x] 출처 텍스트 확장 가능 표시
- [x] 메트릭 카드 레이아웃
- [x] 청킹 설정 표시
- [x] Operation 결과 표시

### 향후 개선 사항 (선택적)
- [ ] 파일 삭제 기능
- [ ] Store 영구 저장
- [ ] 채팅 히스토리 내보내기
- [ ] 파일 검색 필터링
- [ ] 다국어 지원

## 제약사항

- Gemini API 무료 티어 사용량 제한
- 파일당 최대 크기 제한 (Gemini API 규격 따름)
- 인터넷 연결 필수
- Store는 세션 단위로 관리 (영구 저장 없음)

## 성공 지표

### 기능적 지표
- ✅ uv로 5분 내 프로젝트 설정 완료
- ✅ 파일 업로드 후 인덱싱 완료 (파일 크기에 따라 가변)
- ✅ 질문 입력 후 5초 이내 답변 생성
- ✅ 정확한 인용 출처 제공 (Grounding chunks 기반)
- ✅ 모든 업로드 파일의 메타데이터 수집 및 표시
- ✅ 디버깅 정보를 통한 RAG 프로세스 투명성 확보

### UX 지표
- ✅ 직관적인 탭 구조
- ✅ 모던하고 깔끔한 다크 테마
- ✅ 실시간 진행률 피드백
- ✅ 확장 가능한 정보 계층 (Expander)
- ✅ 사이드바를 통한 빠른 파일 확인

## 주요 달성 사항

### 투명성 (Transparency)
- **RAG 프로세스 가시화**: Grounding chunks와 supports를 통해 AI가 실제로 어떤 문서를 참조했는지 명확히 표시
- **상세한 디버깅 정보**: JSON 형태로 전체 응답 구조 확인 가능
- **메타데이터 추적**: 파일 업로드부터 청킹, 인덱싱까지 전 과정 정보 제공

### 사용성 (Usability)
- **Zero-config 벡터DB**: 복잡한 벡터DB 설정 없이 Gemini API가 모든 인덱싱 처리
- **즉시 사용 가능**: .env 설정만으로 3분 내 시작
- **직관적 UI**: 탭 구조로 명확한 기능 분리
- **실시간 피드백**: 업로드, 질의 모든 단계에서 상태 표시

### 확장성 (Extensibility)
- **모듈화된 함수**: 각 기능이 독립적으로 작동
- **세션 상태 관리**: 파일 메타데이터와 채팅 히스토리 지속
- **에러 핸들링**: 모든 주요 작업에 try-except 및 사용자 피드백

### 개발자 경험 (DX)
- **uv 기반 빠른 설정**: 전통적인 pip보다 10배 빠른 의존성 설치
- **pyproject.toml**: 표준 Python 프로젝트 구조
- **명확한 코드 구조**: 함수별 책임 분리
- **풍부한 메타데이터**: 디버깅과 최적화에 필요한 모든 정보 수집
