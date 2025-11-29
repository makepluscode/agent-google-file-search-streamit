# Gemini File Search 챗봇 🔍

![Screenshot](sceenshot.png)

Google Gemini File Search API를 활용한 문서 기반 질의응답 웹 애플리케이션입니다.

## 주요 기능

- 📤 **다중 파일 업로드** (PDF, TXT, DOCX, MD, CSV)
- 💬 **자연어 질의응답** with Gemini 2.5 Flash
- 📚 **상세한 출처 표시** - AI가 참조한 문서 청크 및 근거 표시
- 📊 **업로드 메타데이터** - 파일 크기, 문자/단어/토큰 수, 청크 개수, 업로드 시간 등
- 🔍 **디버깅 정보** - Grounding chunks, supports, citations 실시간 확인
- 🎨 **모던 다크 테마** UI (무채색 + 인디고 강조색)
- ⚡ **벡터DB 없이 빠른 설정** - Gemini API가 자동으로 인덱싱 처리

## 기술 스택

- **Python 3.9+**
- **Streamlit**: 웹 UI 프레임워크
- **Google Gemini 2.5 Flash**: File Search Tool with RAG
- **google-genai SDK**: Gemini API 클라이언트
- **python-dotenv**: 환경 변수 관리
- **uv**: 빠른 Python 패키지 관리자

## 특징

### 📊 상세한 파일 메타데이터
파일 업로드 시 다음 정보를 자동으로 수집하여 표시:
- 파일 크기 (bytes, MB)
- 문자 수, 단어 수 (텍스트 파일)
- 추정 토큰 수
- 추정 청크 개수
- 업로드 소요 시간
- 청킹 설정 (max_tokens_per_chunk: 400, overlap: 40)
- Gemini API Operation 결과

### 🔍 상세한 출처 추적
AI 답변에 대한 투명한 출처 제공:
- **Grounding Chunks**: AI가 답변 생성에 사용한 문서 조각들
- **Grounding Supports**: 답변의 각 부분과 참조 청크 매핑
- **Citations**: 인용된 문서 제목, URI, 텍스트 내용
- 실시간 디버깅 정보로 RAG 프로세스 확인 가능

### 🎨 모던 UI/UX
- 다크 테마 기반 무채색 디자인
- 인디고(#6366f1) 강조색
- 반응형 레이아웃
- 직관적인 탭 구조
- 확장 가능한 섹션으로 정보 계층화

## 설치 및 실행

### 1. uv 설치 (없는 경우)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 프로젝트 클론 및 이동

```bash
cd google-search-api-streamit
```

### 3. 환경변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 API Key 입력
# GEMINI_API_KEY=your_api_key_here
```

**API Key 발급**: https://aistudio.google.com/apikey

### 4. 의존성 설치

```bash
uv sync
```

### 5. 앱 실행

#### 방법 1: 직접 실행 (개발용)
```bash
uv run streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 이 열립니다.

#### 방법 2: systemd 서비스로 실행 (프로덕션/항상 실행)
```bash
# 서비스 등록, 활성화 및 시작
sudo ./service.sh start

# 서비스 상태 확인
./service.sh status

# 서비스 중지
sudo ./service.sh stop

# 서비스 재시작
sudo ./service.sh restart

# 서비스 로그 보기
./service.sh logs

# 서비스 완전히 제거
sudo ./service.sh disable
```

**서비스 등록 시 장점:**
- 시스템 부팅 시 자동 시작
- 비정상 종료 시 자동 재시작
- 백그라운드에서 항상 실행
- systemd로 중앙 관리

## 사용 방법

1. **Store 생성**: 사이드바에서 Store 이름을 입력하고 생성 버튼 클릭
2. **파일 업로드**: "📤 파일 업로드" 탭에서 문서 파일 선택 및 업로드
   - 업로드 후 자세한 메타데이터 확인 가능 (파일 크기, 문자 수, 토큰 수, 청크 개수 등)
   - 사이드바에서 업로드된 파일 목록 확인
3. **질문하기**: "💬 질의응답" 탭에서 질문 입력
4. **답변 확인**:
   - AI 답변 및 검색된 출처 표시
   - 각 출처의 제목, 파일명, 참조 텍스트 확인
   - 디버깅 정보로 Grounding 데이터 상세 확인

## 프로젝트 구조

```
google-search-api-streamit/
├── .env                # API Key (git ignore)
├── .env.example        # 환경변수 템플릿
├── .gitignore
├── pyproject.toml      # 프로젝트 설정
├── PRD.md             # 제품 요구사항 문서
├── README.md          # 프로젝트 설명
├── CLAUDE.md          # Claude Code 가이드
│
├── app.py             # Streamlit 메인 앱 (UI 구성)
├── config.py          # 설정 및 상수
├── styles.py          # CSS 스타일 정의
├── gemini_api.py      # Gemini API 연동 로직
├── ui_components.py   # UI 컴포넌트 함수들
├── utils.py           # 유틸리티 함수들
└── service.sh         # systemd 서비스 관리 스크립트
```

## 개발 환경 설정

```bash
# 개발 의존성 포함 설치
uv sync --extra dev

# 코드 포맷팅
uv run black .

# 린팅
uv run ruff check .
```

## API 설정

### 청킹 설정 (Chunking Configuration)
- **방식**: White space chunking
- **최대 토큰/청크**: 400 tokens
- **오버랩 토큰**: 40 tokens

### Gemini 모델 설정
- **모델**: gemini-2.5-flash
- **Temperature**: 0.2 (정확성 우선)
- **Tools**: File Search with custom store

## 제약사항

- Gemini API 무료 티어 사용량 제한 존재
- 인터넷 연결 필수
- 파일당 최대 크기 제한 (Gemini API 규격 따름)
- PDF의 경우 텍스트 추출 품질은 PDF 구조에 따라 다를 수 있음

## 디버깅 및 개발

### 디버깅 정보 확인
질의응답 시 다음 디버깅 정보를 Web UI에서 확인 가능:
- Debug Info 전체 구조 (JSON)
- Grounding Chunks 상세 정보
- Grounding Supports 매핑
- Citations 데이터

### 커스터마이징
- `app.py`의 CSS 섹션에서 테마 색상 변경 가능
- `temperature` 파라미터로 답변 창의성 조정
- 청킹 설정 (`max_tokens_per_chunk`, `max_overlap_tokens`) 조정 가능

## 트러블슈팅

**Q: 출처가 표시되지 않아요**
- 파일이 정상적으로 업로드되었는지 확인 (사이드바 또는 파일 업로드 탭)
- 디버깅 정보에서 `has_grounding: true` 확인
- `grounding_chunks` 배열이 비어있지 않은지 확인

**Q: 파일 업로드가 느려요**
- 파일 크기에 따라 업로드 및 인덱싱 시간이 소요됨
- 업로드 메타데이터에서 소요 시간 확인 가능
- 여러 파일은 순차적으로 처리됨

**Q: API 에러가 발생해요**
- `.env` 파일에 `GEMINI_API_KEY`가 올바르게 설정되었는지 확인
- API 키 할당량이 남아있는지 확인: https://aistudio.google.com/apikey
- 네트워크 연결 상태 확인

## 참고 자료

- [Google Gemini File Search 공식 문서](https://ai.google.dev/gemini-api/docs/file-search)
- [원본 튜토리얼 블로그](https://jangwook.net/ko/blog/ko/google-gemini-file-search-rag-tutorial/)
- [Gemini API Keys](https://aistudio.google.com/apikey)

## 라이선스

MIT

---

이 프로젝트는 Google Gemini File Search Tool을 활용한 RAG(Retrieval Augmented Generation) 시스템 구현 예제입니다.
