"""Gemini API 관련 함수들"""

import os
import time
import uuid
from google import genai
from google.genai import types
from config import CHUNKING_CONFIG, MODEL_CONFIG, UPLOAD_CONFIG


def initialize_client():
    """환경 변수에서 API 키를 로드하고 클라이언트를 초기화합니다."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None, "GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다."

        os.environ["GEMINI_API_KEY"] = api_key
        client = genai.Client()
        return client, None
    except Exception as e:
        return None, str(e)


def create_store(client, store_name):
    """File Search Store를 생성합니다."""
    try:
        store = client.file_search_stores.create(
            config={"display_name": store_name}
        )
        return store, None
    except Exception as e:
        return None, str(e)


def upload_file(client, file, store_name):
    """파일을 업로드하고 인덱싱합니다."""
    try:
        # 파일 메타데이터 수집
        file_metadata = {
            "filename": file.name,
            "file_size_bytes": file.size,
            "file_size_mb": round(file.size / (1024 * 1024), 2),
            "file_type": os.path.splitext(file.name)[1],
            "chunking_config": CHUNKING_CONFIG.copy()
        }

        # 임시 파일 생성
        file_ext = os.path.splitext(file.name)[1]
        temp_file = f"temp_{uuid.uuid4().hex}{file_ext}"

        file_content = file.getbuffer()
        with open(temp_file, "wb") as f:
            f.write(file_content)

        # 텍스트 파일인 경우 문자 수 계산
        if file_ext.lower() in UPLOAD_CONFIG['text_extensions']:
            try:
                text_content = file_content.tobytes().decode('utf-8')
                file_metadata["character_count"] = len(text_content)
                file_metadata["word_count"] = len(text_content.split())
                file_metadata["estimated_tokens"] = len(text_content) // 4
            except:
                file_metadata["character_count"] = "N/A (binary file)"
                file_metadata["word_count"] = "N/A"
                file_metadata["estimated_tokens"] = "N/A"
        else:
            file_metadata["character_count"] = "N/A (binary file)"
            file_metadata["word_count"] = "N/A"
            file_metadata["estimated_tokens"] = file.size // 4

        # 파일 업로드
        start_time = time.time()
        operation = client.file_search_stores.upload_to_file_search_store(
            file=temp_file,
            file_search_store_name=store_name,
            config={
                "display_name": file.name,
                "chunking_config": {
                    "white_space_config": {
                        "max_tokens_per_chunk": CHUNKING_CONFIG["max_tokens_per_chunk"],
                        "max_overlap_tokens": CHUNKING_CONFIG["max_overlap_tokens"]
                    }
                }
            }
        )

        # 업로드 완료 대기
        while not operation.done:
            time.sleep(2)
            operation = client.operations.get(operation)

        file_metadata["upload_duration_seconds"] = round(time.time() - start_time, 2)

        # Operation 결과 메타데이터 수집
        if hasattr(operation, 'result'):
            result = operation.result
            file_metadata["operation_result"] = {}
            for attr in dir(result):
                if not attr.startswith('_'):
                    try:
                        value = getattr(result, attr)
                        if not callable(value):
                            file_metadata["operation_result"][attr] = str(value)
                    except:
                        pass

        if hasattr(operation, 'metadata'):
            metadata = operation.metadata
            file_metadata["operation_metadata"] = {}
            for attr in dir(metadata):
                if not attr.startswith('_'):
                    try:
                        value = getattr(metadata, attr)
                        if not callable(value):
                            file_metadata["operation_metadata"][attr] = str(value)
                    except:
                        pass

        # 청크 개수 추정
        if isinstance(file_metadata["estimated_tokens"], int):
            estimated_chunks = max(1, file_metadata["estimated_tokens"] // CHUNKING_CONFIG["max_tokens_per_chunk"])
            file_metadata["estimated_chunks"] = estimated_chunks
        else:
            file_metadata["estimated_chunks"] = "N/A"

        # 임시 파일 정리
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return True, file_metadata, None

    except Exception as e:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)
        return False, None, str(e)


def query_store(client, question, store_name):
    """Store에 질문하고 답변을 받습니다."""
    try:
        response = client.models.generate_content(
            model=MODEL_CONFIG["model_name"],
            contents=question,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ],
                temperature=MODEL_CONFIG["temperature"]
            )
        )

        # 디버깅 정보 수집
        debug_info = {
            "has_grounding": False,
            "grounding_chunks": [],
            "grounding_supports": [],
            "citations": [],
            "raw_response_info": {}
        }

        citations = []

        # API 응답 구조 확인을 위한 로깅
        print("\n" + "="*80)
        print("🔍 Gemini API Response Debug")
        print("="*80)

        # response 객체의 모든 속성 확인
        print("\n📦 Response 객체 속성:")
        for attr in dir(response):
            if not attr.startswith('_'):
                try:
                    value = getattr(response, attr)
                    if not callable(value):
                        print(f"  - {attr}: {type(value).__name__}")
                except:
                    pass

        # automatic_function_calling_history 확인
        if hasattr(response, 'automatic_function_calling_history') and response.automatic_function_calling_history:
            print(f"\n📜 automatic_function_calling_history 발견! 개수: {len(response.automatic_function_calling_history)}")
            for idx, history_item in enumerate(response.automatic_function_calling_history):
                print(f"\n  History {idx}:")
                for attr in dir(history_item):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(history_item, attr)
                            if not callable(value):
                                print(f"    - {attr}: {type(value).__name__}")
                        except:
                            pass

        # parts 확인
        if hasattr(response, 'parts') and response.parts:
            print(f"\n📄 response.parts 발견! 개수: {len(response.parts)}")
            for idx, part in enumerate(response.parts):
                print(f"\n  Part {idx}:")
                for attr in dir(part):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(part, attr)
                            if not callable(value):
                                print(f"    - {attr}: {type(value).__name__}")
                        except:
                            pass

        # candidates 확인
        grounding_metadata = None
        if hasattr(response, 'candidates') and response.candidates:
            print(f"\n✅ candidates 발견! 개수: {len(response.candidates)}")

            for idx, candidate in enumerate(response.candidates):
                print(f"\n  Candidate {idx}:")
                for attr in dir(candidate):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(candidate, attr)
                            if not callable(value):
                                print(f"    - {attr}: {type(value).__name__}")
                                if attr == "grounding_metadata" and value:
                                    grounding_metadata = value
                                    print(f"      ✅ grounding_metadata 발견!")
                        except:
                            pass

                # candidate.content 확인
                if hasattr(candidate, 'content') and candidate.content:
                    print(f"\n  Candidate {idx} Content:")
                    for attr in dir(candidate.content):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(candidate.content, attr)
                                if not callable(value):
                                    print(f"    - {attr}: {type(value).__name__}")
                            except:
                                pass

        # grounding_metadata 처리 (response 직접 또는 candidates[0]에서)
        if not grounding_metadata and hasattr(response, "grounding_metadata"):
            grounding_metadata = response.grounding_metadata

        if grounding_metadata:
            debug_info["has_grounding"] = True
            print("\n✅ grounding_metadata 존재!")
            print(f"  타입: {type(grounding_metadata)}")

            # grounding_metadata의 모든 속성 확인
            print("\n📋 grounding_metadata 속성:")
            for attr in dir(grounding_metadata):
                if not attr.startswith('_'):
                    try:
                        value = getattr(grounding_metadata, attr)
                        if not callable(value):
                            print(f"  - {attr}: {type(value).__name__}")
                            if hasattr(value, '__len__') and not isinstance(value, str):
                                try:
                                    print(f"    (길이: {len(value)})")
                                except:
                                    pass
                    except:
                        pass

            # grounding_chunks 수집 및 citations로 변환
            if hasattr(grounding_metadata, "grounding_chunks"):
                chunks_list = grounding_metadata.grounding_chunks
                print(f"\n📦 grounding_chunks 발견! 개수: {len(list(chunks_list)) if chunks_list else 0}")

                for idx, chunk in enumerate(grounding_metadata.grounding_chunks, 1):
                    print(f"\n  Chunk {idx}:")

                    # chunk의 모든 속성 확인
                    for attr in dir(chunk):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(chunk, attr)
                                if not callable(value):
                                    print(f"    - {attr}: {type(value).__name__}")
                            except:
                                pass
                    chunk_data = {"index": idx}

                    if hasattr(chunk, "web") and chunk.web:
                        chunk_data["web"] = str(chunk.web)

                    if hasattr(chunk, "retrieved_context") and chunk.retrieved_context:
                        ctx = chunk.retrieved_context
                        chunk_data["retrieved_context"] = {}
                        citation_item = {}

                        # retrieved_context의 모든 속성 확인
                        print(f"\n    🔍 Retrieved Context {idx} 속성:")
                        for attr in dir(ctx):
                            if not attr.startswith('_'):
                                try:
                                    value = getattr(ctx, attr)
                                    if not callable(value):
                                        print(f"      - {attr}: {type(value).__name__} = {repr(value)[:100]}")
                                except:
                                    pass

                        if hasattr(ctx, "title"):
                            chunk_data["retrieved_context"]["title"] = ctx.title
                            citation_item["title"] = ctx.title

                        if hasattr(ctx, "uri"):
                            chunk_data["retrieved_context"]["uri"] = ctx.uri
                            citation_item["uri"] = ctx.uri
                            citation_item["source"] = ctx.uri

                        if hasattr(ctx, "text"):
                            chunk_data["retrieved_context"]["text"] = ctx.text
                            citation_item["text"] = ctx.text

                        if citation_item:
                            citations.append(citation_item)

                    debug_info["grounding_chunks"].append(chunk_data)

                print(f"\n✅ 총 {len(debug_info['grounding_chunks'])}개 chunks 수집 완료")
            else:
                print("\n❌ grounding_chunks 속성이 없습니다!")

            # grounding_supports 수집
            if hasattr(grounding_metadata, "grounding_supports"):
                for idx, support in enumerate(grounding_metadata.grounding_supports, 1):
                    support_data = {"index": idx}

                    if hasattr(support, "segment"):
                        seg = support.segment
                        support_data["segment"] = {
                            "text": getattr(seg, "text", ""),
                            "start_index": getattr(seg, "start_index", None),
                            "end_index": getattr(seg, "end_index", None)
                        }

                    if hasattr(support, "grounding_chunk_indices") and support.grounding_chunk_indices is not None:
                        support_data["chunk_indices"] = list(support.grounding_chunk_indices)

                    if hasattr(support, "confidence_scores") and support.confidence_scores is not None:
                        support_data["confidence_scores"] = list(support.confidence_scores)

                    debug_info["grounding_supports"].append(support_data)

            # citations 수집
            if hasattr(grounding_metadata, "citations"):
                for idx, citation in enumerate(grounding_metadata.citations, 1):
                    citation_data = {}
                    for attr in dir(citation):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(citation, attr)
                                if not callable(value):
                                    citation_data[attr] = value
                            except:
                                pass
                    citations.append(citation_data)
                    debug_info["citations"].append(citation_data)
        else:
            print("\n❌ grounding_metadata가 없습니다!")
            debug_info["raw_response_info"]["has_grounding_metadata"] = False

        print("\n" + "="*80)
        print(f"📊 최종 수집 결과:")
        print(f"  - has_grounding: {debug_info['has_grounding']}")
        print(f"  - grounding_chunks: {len(debug_info['grounding_chunks'])}개")
        print(f"  - grounding_supports: {len(debug_info['grounding_supports'])}개")
        print(f"  - citations: {len(debug_info['citations'])}개")
        print("="*80 + "\n")

        return response.text, citations, debug_info, None

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, None, None, str(e)
