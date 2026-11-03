# 최종 버전 (v2.1 final) 노트북·모델 정리

최종 챗봇에 실제로 쓰인 것만 진행 순서대로 모았습니다. 원본은 `../v2.1/`에 그대로 있고, 여기 파일은 복사본입니다 (파일 이름 앞 번호 = 발표 순서, 뒤 = 원래 노트북 이름).

## 진행 순서

| # | 노트북 (원래 번호) | 하는 일 | 최종 버전에 남은 것 | 핵심 결과 |
|---|---|---|---|---|
| 01 | 02_health_embedding | 건강 질문 선별, 문단 DB 459,067개, bge 임베딩 + FAISS 인덱스 | DB · 인덱스 · 평가셋 | 의료 사이트 33곳 기준 건강 질문 |
| 02 | 03_retrieval_rerank | BM25 vs dense vs 하이브리드, 재정렬 비교 | bge 검색 후보 100, MiniLM | dense가 BM25의 약 2배 |
| 03 | 08_rag_chatbot_v21 | 첫 RAG 평가, 거절 기준 정하기 | 거절 기준 MiniLM < 4.92 (검증 하위 5%) | 정답률 .736 (LLM만 .618) |
| 04 | 11_rerank_compare_v21 | 재정렬 모델 6종 + 앙상블 비교 | bge-reranker-large + v2-m3 앙상블 | MRR@10 .445 → .474 |
| 05 | 14_judge_eval_v21 | F1 대신 LLM 심판 평가 도입 | 평가 기준 (Qwen2.5-14B 심판) | 사람 판정과 일치 .88 |
| 06 | 16_gen_compare_v21 | 검색 Top-5/10 × 생성 모델 4종 | Top-10, Qwen3-8B | 정답률 .782 (+4.6, 유의) |
| 07 | 17_dpo_v21 | DPO v1 학습 (지어낸 답 줄이기) | **DPO v1 어댑터** | 진짜 답 없음 거절 .652 → .804 |
| 08 | 20_typo_gate_v21 | 오타·문법 흔들린 질문 대응 | 재검색 B2 (고친 질문 ≥ 6.0) | 오타 질문 정답률 .148 → .622 (실험 결과, 최종 챗봇에선 끔 — 아래 참고) |
| 09 | 23_final_eval_v21 | 최종 지표: 어댑터 × 재검색 × 원래/오타 질문 | final_choice.json | 실행 중 |
| 10 | 08f_final_chatbot_v21 | 최종 챗봇 (Gradio) | — | 데모 질문 자동 테스트 |

빠진 실험 (v2.1 폴더에만 있음): 06 문장형 LoRA(폐기, .450) · 09 쿼리 재작성/HyDE(이득 없음) · 10 LLM 거절 판정(점수보다 못함) · 15 SFT v2(원본 못 넘음) · 18 프롬프트·거절 기준(변경 없음) · 19 DPO 거절 기준(변경 없음) · 22 DPO v2(진짜 답 없음 거절 .652로 하락, 미사용).

## 최종 파이프라인

> **11/03 B안 결정**: 발표 기준 챗봇은 재검색 없음(DPO v1·A). 23번 시험 정답률 .770 · 잘못거절 .080 · 근거충실 .942 · 진짜 답없음 거절 .804. 재검색(B2)은 노트북의 `RETRY_FIX = True`로 켤 수 있음(정답 .782, 오타 정답 .634, 진짜 답없음 거절 .739).

질문 → (한국어면 번역) → bge-base + FAISS 후보 100 → MiniLM 최고점 < 4.92면 거절 → bge-reranker 앙상블 상위 10 → Qwen3-8B + DPO v1 → 답 [n]

## 모델

| 역할 | 모델 | 종류 | 위치 |
|---|---|---|---|
| 1차 검색 임베딩 | BAAI/bge-base-en-v1.5 | 사전학습 (HF) | 자동 다운로드 |
| 거절 점수 | cross-encoder/ms-marco-MiniLM-L-6-v2 | 사전학습 (HF) | 자동 다운로드 |
| 재정렬 | BAAI/bge-reranker-large, BAAI/bge-reranker-v2-m3 | 사전학습 (HF) | 자동 다운로드 |
| 생성 | Qwen/Qwen3-8B | 사전학습 (HF) | 자동 다운로드 |
| 생성 어댑터 | **DPO v1 LoRA** (r16, α32, β 0.1, 224쌍) | **우리가 학습** | 드라이브 `rag_msmarco/final_v21/models/dpo_v1_adapter/` (원본 `rag_msmarco/health/dpo/adapter/`) |
| 평가 심판 | Qwen/Qwen2.5-14B-Instruct | 사전학습 (HF), 챗봇에는 안 씀 | 자동 다운로드 |

## 데이터 (드라이브 `MyDrive/rag_msmarco/health/`, 복사하지 않음)

| 파일 | 내용 |
|---|---|
| `corpus.jsonl` | 문단 459,067개 (211MB) |
| `faiss_bge_flatip.index` | bge 임베딩 FAISS 인덱스 (1.4GB) |
| `eval.jsonl` | 시험 650 (답 있음 500 + 답 없음 100 + 분야 밖 50) |
| `final/final_config.json` | 챗봇 설정 (드라이브 `rag_msmarco/final_v21/`에도 복사) |
| `judge_eval/judgments.jsonl` | 심판 채점 캐시 |

## Python 스크립트 (`py/`)

| 파일 | 원본 노트북 | 내용 |
|---|---|---|
| `py/train_dpo_v1.py` | 07 (17_dpo_v21) | DPO v1 학습: 후보 답 생성 → 심판 채점 → 선호 쌍 224개 → DPO 학습 → 평가 |
| `py/rag_pipeline_dpo_v1.py` | 10 (08f) | 최종 챗봇 추론: 검색 → 거절 → 재정렬 → Qwen3-8B + DPO v1 → Gradio |

노트북 코드 셀을 순서 그대로 옮긴 것 (설명은 주석, `!pip`은 주석 처리). 드라이브 마운트 등 Colab 전용 코드 포함.

## DPO v1 학습 데이터 (`data/dpo_v1/`, 드라이브 `rag_msmarco/final_v21/data/dpo_v1/`에도 있음)

| 파일 | 내용 |
|---|---|
| `pairs.jsonl` | 실제 학습에 쓴 선호 쌍 224개 (정답 vs 오답 137 · 거절 vs 지어낸 답 67 · 근거 답 vs 근거 없음 20). 필드: qid, query, pids(문단 번호 Top-5), chosen, rejected, kind |
| `candidates.jsonl` | train 건강 질문 2,465개 × Qwen3-8B 후보 답 3개 (greedy 1 + sampling 2) |
| `questions_sft_v2_candidates.jsonl` | 출발 질문 목록 (15 SFT v2와 같음): 질문, 검색 문단 Top-5, 참고 정답 |
| `train_log.csv` | 학습 쌍별 loss, 보상 정확도 |
| `results_summary.md` | 17번 결과 요약 |
