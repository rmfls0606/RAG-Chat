<!-- ppt-master-schema: design-spec/v1 -->
# 의료 RAG 챗봇 최종 파이프라인 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | medical_rag_final_20261103 |
| Canvas Format | ppt169 (1280 × 720) |
| Page Count | 14 |
| Primary Language | ko-KR |
| Target Audience | 멋사 NLP 6기 강사·멘토와 동료 수강생. RAG·임베딩·LLM 기본 개념은 알지만 이 프로젝트의 세부 실험과 지표 설계는 처음 봄 |
| Communication Intent | MS MARCO 건강 분야 RAG 챗봇의 최종 파이프라인을 검색 단계와 생성 단계로 나눠 설명하고, 지표를 어떻게 세우고(LLM 심판) 그 지표로 각 개선을 어떻게 증명했는지 보고한다. 직접 학습한 DPO가 왜 필요했고 무엇을 개선했는지를 강조하며, 남은 한계를 솔직하게 밝힌다. |
| Desired Audience Outcome | 청중이 파이프라인의 각 단계와 그 근거 지표를 이해하고, 정답률 .618 → .770과 지어낸 답 35% → 20%가 믿을 만한 숫자라고 납득한다 |
| Core Message / Ask / Action | 믿을 수 있는 지표(LLM 심판, 검증-시험 분리, 신뢰구간)를 먼저 세웠기 때문에, 근거 안에서만 답하는 의료 챗봇을 정답률을 지키면서 더 안전하게(DPO) 만들 수 있었다 |
| Delivery Context | 주 용도: 발표자가 진행하는 15분 프로젝트 최종 발표 (현장 프로젝션). 부 용도: 발표 후 공유되는 결과 자료 |
| Artifact Afterlife | 프로젝트 결과 기록과 포트폴리오 자료로 보관 |
| Reading Mode | balanced |
| Content Strategy | balanced default — source md(presentation_final_pipeline.md)의 12장 구성과 수치를 유지하고, 표지와 결론 장을 더해 14장으로 재구성 |
| Design Style | 파이프라인 레일 — custom mode + soft-rounded visual style, 그래프 매칭 블루 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — final Stage-2 proactive policy |
| Custom Animations | disabled — final Stage-2 proactive policy |
| Narration Audio | disabled — final Stage-2 proactive policy |
| Created Date | 2026-11-03 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px left/right, 48 px top/bottom |
| Content Area | x 64–1216, y 48–672 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: instructional, pyramid
- **Mode Behavior**: 파이프라인을 앞에서 뒤로 걸어가며 설명하는 교육형 흐름에, 각 단계 슬라이드는 결론형 제목을 붙인다. 표지 → 결과 요약 → 데이터 → 전체 도식 다음, 검색 단계(①1차 검색 ②재정렬 ③검색 거절)와 생성 단계(④생성 ⑤DPO)를 순서대로 다루고, 지표 파트에서는 '심판이란 무엇인가'를 먼저 정의한 뒤 신뢰성 근거를 보인다. 단계마다 '무엇을 했나 → 어떤 지표로 쟀나 → 얼마나 좋아졌나'를 같은 순서로 반복한다.
- **Visual style**: soft-rounded
- **Theme**: 그래프와 같은 거의 흰 바탕 위의 둥근 카드와 옅은 블루 면. 상단 파이프라인 레일(검색 ①②③ → 생성 ④⑤ → 지표)이 본문 장마다 반복되고 현재 위치만 채워진 노드로 켜진다 — 청중이 지금 파이프라인 어디를 보고 있는지 알려 주는 길잡이 모티프(반복 재사용, 활성 노드만 바뀜). 표지·결론은 primary 남색 면을 자신 있게 쓴다.
- **Tone**: 친절하고 정돈된 기술 보고 — 숫자는 크게, 설명은 짧게

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FCFCFB | 모든 장 바탕 (그래프 PNG 바탕과 동일) |
| Secondary background | #EEF4FC | 카드 면, 검색 단계 구역 띠, 레일 비활성 노드 면 |
| Primary | #12355B | 제목, 표지·결론 면, 생성 단계 강조 |
| Accent | #2A78D6 | 최종·채택 값, 레일 활성 노드, 핵심 수치 (그래프의 파랑과 동일) |
| Secondary accent | #EB6834 | 비교 대상·대가·주의 (그래프의 주황과 동일) |
| Body text | #1F2328 | 본문 |
| Secondary text | #52514E | 캡션, 출처 줄, 주석 |
| Divider | #E2E1DC | 구분선, 카드 테두리, 표 선 |
| Muted | #C3C2B7 | 비채택·기준선 표시 (그래프의 회색과 동일) |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 둥근 인상의 현대 고딕, Bold | Pretendard | Pretendard | sans-serif |
| Body | 같은 계열 Regular/Medium | Pretendard | Pretendard | sans-serif |

- **Title stack**: Pretendard, sans-serif
- **Body stack**: Pretendard, sans-serif
- **Font note**: Pretendard는 사용자가 확인한 글꼴로, 발표 PC에 설치되어 있어야 같은 모양으로 보인다 (PPTX는 글꼴을 내장하지 않음)

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 24 |
| Title | 42 |
| Subtitle | 32 |
| Annotation | 18 |
| Lead | 28 |
| Cover title | 64 |
| Hero number | 72 |
| Footnote | 15 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 상단 레일 → 결론형 제목 → 큰 수치 또는 그래프 → 짧은 해석 → 하단 출처 줄
- **Composition tendency**: 그래프가 있는 장은 그래프를 페이지 폭의 55–65%로 크게 두고 옆이나 아래에 2–3줄 해석 카드; 개념 장은 둥근 카드 2–3개 또는 흐름 도식
- **Cross-page continuity**: 본문 장(P04–P13) 상단 레일은 같은 위치·크기를 유지하고 활성 노드만 바뀐다. 출처 줄 위치와 형식은 모든 본문 장에서 동일
- **Spacing posture**: variable by page rhythm — 그래프 장은 dense, 표지·결론은 open
- **Spacing anchors**: page margin 64 px · block gap 24 px · column gutter 32 px · corner radius 12 px · body leading 36 px

## VI. Icon Usage Specification

- **Primary bundled library**: tabler-filled

| Icon Path | Suitable Scenarios |
| --- | --- |
| icons/tabler-filled/database.svg | |
| icons/tabler-filled/search.svg | |
| icons/tabler-filled/filter.svg | |
| icons/tabler-filled/sort-descending-2.svg | |
| icons/tabler-filled/shield-check.svg | |
| icons/tabler-filled/message-chatbot.svg | |
| icons/tabler-filled/scale.svg | |
| icons/tabler-filled/chart-dots.svg | |
| icons/tabler-filled/check.svg | |
| icons/tabler-filled/x.svg | |
| icons/tabler-filled/alert-triangle.svg | |
| icons/tabler-filled/bulb.svg | |
| icons/tabler-filled/file-text.svg | |
| icons/tabler-filled/user.svg | |
| icons/tabler-filled/flask.svg | |
| icons/tabler-filled/gauge.svg | |
| icons/tabler-filled/circle-check.svg | |
| icons/tabler-filled/circle-x.svg | |
| icons/tabler-filled/medical-cross.svg | |
| icons/tabler-filled/list-check.svg | |
| icons/tabler-filled/stack-2.svg | |
| icons/tabler-filled/award.svg | |
| icons/tabler-filled/thumb-down.svg | |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| P05 | table | metric_table | 검색 방법별 Recall·MRR 수치 비교 |
| P08 | table | record_table | DPO 선호 쌍 3종의 좋은 답·나쁜 답·쌍 수 |
| P10 | table | record_table | 검색·생성 지표 정의 |
| P13 | table | record_table | 챗봇 테스트 질문별 결과와 응답 시간 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01_progress.png | 2000×1000 | 2.00 | 단계별 시험 정답률 | Chart | 페이지 주 증거로 크게, 옆에 해석 카드 | no-crop | user | Existing | 실험 단계별 시험 정답률 가로 막대, 최종만 파랑 | none | local |
| 02_retrieval.png | 2000×1000 | 2.00 | 검색 단계 Recall@10·MRR@10 | Chart | 왼쪽 큰 그래프 + 오른쪽 거절 기준 카드 | no-crop | user | Existing | BM25→dense→MiniLM→앙상블 묶음 막대 | none | local |
| 03_generator_ci.png | 2000×900 | 2.22 | 생성 모델 교체 효과와 95% CI | Chart | 페이지 폭 그래프 + 아래 해석 줄 | no-crop | user | Existing | 08 대비 정답률 차이 점과 신뢰구간 선 | none | local |
| 04_dpo.png | 2000×1000 | 2.00 | DPO 전후 4개 지표 | Chart | 두 그래프 나란히 중 왼쪽 | no-crop | user | Existing | 진짜 답 없음 거절률·근거 충실도·정답률·잘못 거절 묶음 막대 | none | local |
| 05_tradeoff.png | 2000×1100 | 1.82 | 안전성과 정답률 교환 | Chart | 두 그래프 나란히 중 오른쪽 | no-crop | user | Existing | 4가지 설정의 정답률 × 거절률 산점, 최종만 파랑 | none | local |
| 06_f1_vs_judge.png | 2000×840 | 2.38 | F1과 심판 정답률 순위 역전 | Chart | 아래쪽 넓은 증거 띠 | no-crop | user | Existing | 08 RAG vs 06 LoRA 두 패널 막대 | none | local |
| 07_cross_judge.png | 2000×1100 | 1.82 | 교차 심판 순위 동일 | Chart | 두 그래프 나란히 중 오른쪽 | no-crop | user | Existing | Qwen 심판 vs Phi-4 심판 검증 정답률 | none | local |
| 08_judge_flow.png | 2600×1040 | 2.50 | 심판 채점 과정 4단계 | Diagram | 페이지 폭 흐름도 | no-crop | user | Existing | 입력 → 심판 → 첫 토큰 확률 → 점수 판정 (예시 값 표기 포함) | none | local |
| 09_judge_vs_human.png | 1500×1200 | 1.25 | 심판 vs 사람 혼동 행렬 | Chart | 두 그래프 나란히 중 왼쪽 | no-crop | user | Existing | 사람 40개 판정과 심판 판정 3×3 히트맵 | none | local |

## IX. Content Outline

### Part 1: 개요와 데이터

#### Slide 01 - 표지

- **Audience move**: 무슨 발표인지 모름 → 의료 RAG 챗봇을 지표로 개선한 이야기이며 핵심 숫자가 무엇인지 앎
- **Relationships**: 제목 · 핵심 수치 2개(정답률 .618 → .770, 지어낸 답 35% → 20%) contrast(before → after)
- **Cover impact**: 훅 = "정답률 .618 → .770 · 지어낸 답 35% → 20%"; Composition Reference — 남색 면 위 큰 제목, 오른쪽에 before → after 수치 쌍
- **Title**: 근거 안에서만 답하는 의료 RAG 챗봇
- **Core message**: 지표를 먼저 세우고, 그 지표로 개선을 증명했다
- **Content**: 부제: MS MARCO v2.1 건강 분야 · 최종 파이프라인과 지표 / 수치 쌍: 시험 정답률 .618 → .770 · 지어낸 답 35% → 20% / 멋사 NLP 6기 · 프로젝트 02 지식 기반 QA · 2026-11-03
- **page_rhythm**: anchor

#### Slide 02 - 한 줄 요약과 개선 흐름

- **Audience move**: 결과를 모름 → 최종 결과와 그까지의 단계별 변화를 한눈에 봄
- **Relationships**: 실험 단계 order(B0 → 08 → 06·15 → 16 → 17), 06·15는 폐기로 contrast
- **Composition**: 왼쪽 큰 그래프, 오른쪽 한 줄 요약과 3개 해석 포인트
- **Title**: 검색과 DPO로 정답률 .618 → .770, 지어낸 답은 35% → 20%
- **Content**: 한 줄: 검색된 의료 문단 안에서만 답하고, 문장마다 출처 번호, 근거 없으면 거절 · 과제 핵심: 믿을 수 있는 지표를 먼저 세우고 그 지표로 개선 증명 · 검색 추가(08) +11.8점 / 06·15 학습은 원본 못 넘어 폐기 / 앙상블 Top-10 + Qwen3-8B +4.6점 / DPO로 정답률 유지하며 지어낸 답 35% → 20% · 이득 없어 뺀 것: Hybrid(RRF), 쿼리 재작성/HyDE, LLM 거절 판정, 도메인 판정, 프롬프트·거절 기준 조정
- **Images**: 01_progress.png
- **page_rhythm**: dense

#### Slide 03 - 데이터셋

- **Audience move**: 데이터 출처를 모름 → 무엇을 검색 대상으로, 무엇으로 평가했는지 앎
- **Relationships**: MS MARCO → 건강 질문 선별(규칙) → 검색 DB 3개 출처 membership; 평가셋 3묶음 membership; 검증 → 시험 order
- **Composition**: 왼쪽 데이터 선별 흐름, 가운데 DB 구성 카드, 오른쪽 평가셋 카드
- **Title**: 데이터 — MS MARCO 건강 질문 13.1%, 문단 46만 개, 평가 650문항
- **Content**: MS MARCO: Bing 실제 검색 질문 + 질문마다 웹 문단 10개 + 사람이 쓴 정답 · 왜 의료: dev 분야 중 의료 13.1%로 최다(2위 날씨·여행 3.9%) · 건강 질문 판정: 문단 10개 중 의료 사이트 33곳 출처 2개 이상 → train 119,659 / dev 13,494 · 검색 DB 459,067개(중복 25,666 제거): dev 건강 131,143(정답 문단) / train 건강 229,697(검색 난도) / dev 일반 98,227(방해 문단) · 평가셋 시험 650: 건강·답 있음 500 / 건강·답 없음 100 / 분야 밖 50 + 검증 300 · 검증으로 설정 고르고 시험은 마지막에 한 번만 보고
- **page_rhythm**: dense

#### Slide 04 - 최종 파이프라인

- **Audience move**: 전체 구조를 모름 → 검색 3단계와 생성 2단계, 두 번의 거절 관문을 앎
- **Relationships**: 질문 → (번역) → ①1차 검색 → ②재정렬 → ③검색 거절 → ④생성 → ⑤생성 단계 거절 → 답변 order; ①②③ membership 검색 단계, ④⑤ membership 생성 단계; ③과 ⑤는 각각 거절로 link; DPO만 직접 학습 contrast 나머지 사전학습
- **Composition**: 페이지 폭 가로 흐름도, 검색 구역(옅은 블루 면)과 생성 구역 구분, 아래 모델 표 한 줄씩
- **Title**: 최종 파이프라인 — 검색 3단계 + 생성 2단계, 거절 관문 2개
- **Content**: 질문(한국어면 영어로 번역) · ① 1차 검색: bge-base-en-v1.5 + FAISS, 후보 100 · ② 재정렬: bge-reranker-large + v2-m3 앙상블, 상위 10 · ③ 검색 단계 거절: MiniLM 최고점 < 4.92면 LLM 호출 없이 거절 · ④ 생성: Qwen3-8B + DPO LoRA, 문단 안의 내용만, 문장마다 [n] · ⑤ 생성 단계 거절: 정해진 거절 문장 · 답변(한국어 질문이면 한국어로) · 모델: 사전학습 = bge-base, MiniLM, bge-reranker 2종, Qwen3-8B / 직접 학습 = DPO LoRA(r16, 224쌍) / 평가 심판 Qwen2.5-14B(챗봇엔 미사용)
- **page_rhythm**: anchor

### Part 2: 검색 단계

#### Slide 05 - ① 1차 검색 — 임베딩 + FAISS

- **Audience move**: FAISS·dense 검색 선택 근거를 모름 → 왜 FAISS FlatIP과 dense만 쓰는지, RRF를 왜 뺐는지 앎
- **Relationships**: 임베딩 → 인덱스 저장 → 내적 검색 order; BM25 vs dense vs RRF contrast
- **Composition**: 왼쪽 FAISS 동작 3단계와 선택 이유, 오른쪽 BM25/dense/RRF 비교 표
- **Title**: dense 검색이 BM25의 약 2배 — RRF는 오히려 낮아 제외
- **Content**: FAISS: Meta의 벡터 유사도 검색 라이브러리 · 문단 459,067개 → bge-base 768차원 벡터(A100 166초) → 인덱스 1.4GB → 질문 벡터와 내적 최대 100개(정규화 → 내적 = 코사인) · IndexFlatIP(전부 비교): 46만 개는 근사 검색 없이도 빠르고 근사 오차 없어 실험 비교가 흔들리지 않음 · Vector DB 대신 인덱스 파일: DB 고정, Colab에서 서버 없이 파일 하나 · 표(시험 500): BM25 R@1 .120 R@10 .406 R@100 .710 MRR@10 .202 / bge-base R@1 .272 R@10 .688 R@100 .938 MRR@10 .401 / Hybrid RRF R@10 .608 · RRF = Σ 1/(60+순위), 약한 BM25가 순위를 희석 · R@100 .938 → 문제는 순위 → 재정렬로
- **Visualization**: retrieval-baseline (table, 방법 × R@1/R@10/R@100/MRR@10)
- **Native-ready**: retrieval-baseline=yes
- **page_rhythm**: dense

#### Slide 06 - ② 재정렬 + ③ 검색 단계 거절

- **Audience move**: 재정렬·거절 기준 근거를 모름 → 앙상블이 유의하게 낫고, 거절 기준 4.92가 어떻게 정해졌는지 앎
- **Relationships**: dense → MiniLM → 앙상블 order(개선); 재정렬 점수 → 거절 판단 link
- **Composition**: 왼쪽 큰 그래프, 오른쪽 위 재정렬 해석 카드, 오른쪽 아래 거절 기준 카드
- **Title**: 앙상블 재정렬로 MRR@10 +0.030(유의), 관련 문단 없으면 LLM 전에 거절
- **Content**: 크로스인코더: 질문과 문단을 함께 넣어 관련도 매김, 후보 100개에만 · 재정렬 6종 + 앙상블을 검증 MRR@10으로 선택 · MiniLM 대비 MRR@10 +0.030, 95% CI [+0.008, +0.050] · 의료 특화 MedCPT가 오히려 최하위(MRR@10 .234) · 문단 5 → 10개: 정답 문단 포함률 .654 → .776 · 거절: MiniLM 최고점 < 4.92면 거절(0.3~1.4초), 기준 = 검증셋 답 있는 질문 점수 하위 5% → 잘못 거절 약 5% · 거절 구분력 AUC: 답 있음 vs 답 없음 .804 / vs 분야 밖 .917
- **Images**: 02_retrieval.png
- **page_rhythm**: dense

### Part 3: 생성 단계

#### Slide 07 - ④ 생성 — Qwen3-8B

- **Audience move**: 생성 모델 선택 근거를 모름 → 세대 교체가 가장 큰 개선이었고 8B를 고른 규칙을 앎
- **Relationships**: 4개 모델 contrast(08 대비 차이), CI가 0을 넘는지 membership
- **Composition**: 위 프롬프트 규칙 4개 한 줄, 가운데 페이지 폭 CI 그래프, 아래 해석 2줄
- **Title**: 가장 큰 개선은 모델 세대 교체 — Qwen3-8B +4.6점, 유의
- **Content**: 프롬프트 규칙: 문서에 있는 사실로만 / 문장마다 [1] 출처 / 답 없거나 건강 질문 아니면 거절 문장 / 2~4문장 · 검색은 앙상블 Top-10 고정, 08 첫 RAG(.736) 대비 차이와 95% 부트스트랩 CI · Qwen2.5 → Qwen3 교체가 최대 개선, 같은 계열 크기 키우기는 +2점·유의하지 않음 · Qwen3-14B는 시험에서 조금 높지만 검증에서 동점(.795) → 미리 정한 규칙대로 가벼운 8B
- **Images**: 03_generator_ci.png
- **page_rhythm**: dense

#### Slide 08 - ⑤ 왜 DPO를 직접 학습했나

- **Audience move**: DPO가 왜 필요한지 모름 → 사전학습 모델만으로 남은 문제와 앞선 3가지 시도의 실패 이유, DPO를 고른 논리를 앎
- **Relationships**: 문제(지어낸 답 35%) → 시도 3개(06 LoRA, 15 SFT 재학습, 18 거절 기준 올리기) 각각 실패 → DPO order; SFT vs DPO contrast; 선호 쌍 3종 membership
- **Composition**: 위 문제 한 줄 강조, 가운데 실패한 시도 3카드, 아래 DPO 학습 방법(선호 쌍 표 + 설정)
- **Title**: 문단에 답이 없으면 지어낸다 — 그래서 DPO만 직접 학습했다
- **Content**: 다른 모델은 모두 사전학습 그대로, DPO만 직접 학습 · 남은 문제: 문단에 답이 없을 때 Qwen3-8B가 답을 지어냄(진짜 답 없는 질문의 35%) · 시도1 06 문장형 LoRA .450: 답할 질문까지 거절하도록 배움 · 시도2 15 SFT 재학습 .724: 좋은 답 따라 하기만 해서 원본(.736)에서 멈춤 · 시도3 18 거절 기준 4.92 → 6.80 .678: 답할 질문까지 거절 · SFT는 좋은 답 따라 하기, DPO는 좋은 답과 나쁜 답 비교해 나쁜 답 피하기 · 학습: train 건강 질문마다 Qwen3-8B 답 3개 → Qwen2.5-14B 심판 채점 → 좋은 답 vs 나쁜 답 짝 · 선호 쌍: 답 있는 질문(정답 vs 오답/근거 없음) 137 / 문단에 답 없음(거절 vs 지어낸 답) 67 / 라벨은 답 없음·문단엔 답 있음(근거 충실 vs 근거 없음) 20 = 224 · 거절 쌍 30% 이하로 제한 · LoRA r16, β 0.1, 1 epoch, TRL 없이 직접 구현
- **Visualization**: dpo-pairs (table, 경우 × 좋은 답/나쁜 답/쌍 수)
- **Native-ready**: dpo-pairs=yes
- **page_rhythm**: dense

#### Slide 09 - ⑤ DPO로 좋아진 성능

- **Audience move**: DPO 효과를 모름 → 무엇이 좋아지고 무엇을 지켰고 대가가 무엇인지, 다른 방법보다 나은 이유를 앎
- **Relationships**: DPO 전 vs 후 contrast(좋아짐/지킴/대가 membership); 3가지 안전성 확보 방법 contrast
- **Composition**: 두 그래프 나란히, 아래 좋아짐·지킴·대가 3칸 요약 띠
- **Title**: 정답률은 지키고 지어낸 답은 35% → 20%
- **Content**: 좋아짐: 진짜 답 없음 거절률 .652 → .804(+15.2점), 근거 충실도 .919 → .933 · 지킴: 정답률 .782 → .770(−1.2점, 95% CI −3.8 ~ +1.4, 유의하지 않음), 문단에 답 있는 질문 답변률 .830 그대로 · 대가: 잘못 거절 .046 → .078 · 같은 안전성을 검색 기준으로 얻으면 정답률 .678, DPO로 얻으면 .770 · 검색 단계는 명백히 관련 없는 질문을 빠르게, DPO는 문단은 있는데 답이 없는 경우를 거름
- **Images**: 04_dpo.png, 05_tradeoff.png (나란히, 왼쪽 전후 비교 → 오른쪽 교환 관계)
- **page_rhythm**: dense

### Part 4: 지표

#### Slide 10 - 지표 — 무엇을 재고, 왜 F1을 버렸나

- **Audience move**: 어떤 지표로 쟀는지 모름 → 검색·생성 지표 정의와 F1을 버린 이유를 앎
- **Relationships**: 지표 membership(검색 2 / 생성 3); F1 순위 vs 심판 순위 contrast(역전)
- **Composition**: 위 지표 정의 표, 아래 F1 vs 심판 그래프와 해석
- **Title**: F1로는 1등이던 LoRA가 실제론 꼴찌 — 그래서 LLM 심판으로 바꿨다
- **Content**: 검색: Recall@k = 상위 k개 안에 정답 문단이 있는 비율 / MRR@10 = 첫 정답 순위의 역수 평균(MS MARCO 공식) · 생성: 정답률 = 심판이 2점 준 답 비율(거절은 0점) / 근거 충실도 = 답한 것 중 모든 사실이 문단에 있는 비율 / 잘못 거절·진짜 답 없음 거절률 · F1은 단어 겹침만 봐서 짧게 답하는 LoRA가 최고점(.349 vs .282), 심판 정답률은 .450 vs .736 · 지표를 바꾸자 개선으로 보였던 실험이 폐기됨 → 이후 모든 실험을 심판 정답률로
- **Visualization**: metric-definitions (table, 구분 × 지표 × 정의)
- **Native-ready**: metric-definitions=yes
- **Images**: 06_f1_vs_judge.png
- **page_rhythm**: dense

#### Slide 11 - 지표 — 심판(LLM-as-a-Judge)이란

- **Audience move**: 심판이 무엇인지 모름 → 누가, 무엇을 받아, 어떤 기준으로, 어떻게 점수를 읽는지 앎
- **Relationships**: 입력 → 심판 → 첫 토큰 확률 → 점수 판정 order; 정답 점수 vs 근거 충실도 contrast
- **Composition**: 위 정의 한 줄과 두 점수 카드, 아래 페이지 폭 채점 과정 흐름도
- **Title**: 심판 = 답을 채점하는 별도의 LLM (Qwen2.5-14B)
- **Content**: 챗봇 생성 모델(Qwen3-8B)과 다른 더 큰 모델, 평가에만 쓰고 챗봇엔 넣지 않음 · 왜: 표현이 달라도 핵심 사실이 같으면 맞는 답 → F1로는 못 잼 · 정답 점수 0/1/2: 질문 + MS MARCO 참고 정답 + 챗봇 답 → 2 핵심 사실 맞음 / 1 일부만 / 0 틀림 · 근거 충실도 0/1: 문단 + 챗봇 답 → 1 모든 사실이 문단에 있음 / 0 지어냄 · 첫 토큰이 0·1·2일 확률만 읽음 → 같은 답은 언제나 같은 점수 · 정답 점수 = P(1) + 2·P(2), 1.5 이상이면 정답 · (질문, 답) 단위 캐시로 모든 실험이 같은 채점 공유 · 그림의 챗봇 답과 확률 값은 설명용 예시
- **Images**: 08_judge_flow.png
- **page_rhythm**: dense

#### Slide 12 - 지표 — 이 숫자를 믿을 수 있는 이유

- **Audience move**: 심판 숫자를 의심함 → 사람과의 비교, 교차 심판, 실험 설계 장치로 숫자를 신뢰함
- **Relationships**: 신뢰 장치 membership(심판 vs 사람, 교차 심판, 검증-시험 분리, CI, 같은 조건); 심판은 깐깐한 쪽으로만 틀림 → 정답률이 부풀려지지 않음 link
- **Composition**: 두 그래프 나란히(왼쪽 혼동 행렬, 오른쪽 교차 심판), 아래 그 밖의 장치와 한계 한 줄
- **Title**: 심판은 깐깐하게만 틀린다 — 정답률은 부풀려지지 않는다
- **Content**: 사람 판정 40개(F1 < 0.4로 낮게 나온 답)와 비교: 오답 vs 부분 이상 일치 .88 · 심판이 정답이라 한 12개는 사람도 모두 정답, 틀릴 때는 늘 깐깐한 쪽(사람 정답 24개 중 12개를 부분으로) · Phi-4로 다시 채점해도 검증 정답률 순위 동일 · 그 밖의 장치: 검증 → 시험 분리 / 부트스트랩 95% CI / 같은 질문·후보·심판 캐시 · 한계: 1점 vs 2점 세부 일치는 .57이라 맞음/틀림 수준으로만 신뢰, 사람 표본 40개 · 최종 DPO 선택은 18번 자동 선택의 시험 결과(.678)를 보고 바꾼 것
- **Images**: 09_judge_vs_human.png, 07_cross_judge.png (나란히, 왼쪽 사람 비교 → 오른쪽 다른 심판 비교)
- **page_rhythm**: dense

### Part 5: 테스트와 결론

#### Slide 13 - 챗봇 테스트와 한계

- **Audience move**: 실제 동작과 한계를 모름 → 일상 표현 질문 결과와 남은 과제를 앎
- **Relationships**: 테스트 질문 6개 membership(정답/거절/잘못 거절/분야 밖 통과); 한계 3개 membership(검색/DB/분야 밖)
- **Composition**: 왼쪽 테스트 결과 표, 오른쪽 한계와 다음 단계 카드 3개
- **Title**: 일상 표현 10개 중 8개 정답 — 남은 오답의 주원인은 검색
- **Content**: 테스트: blood sugar too high all the time → hyperglycemia 정답 3.7초 / ringing sound in ears → tinnitus 정답 5.8초 / 위궤양을 일으키는 세균 → 헬리코박터 파일로리 정답(번역 경유) 7.7초 / coke every day cause dementia → 거절(관련 문서 없음) 0.3초 / shot after rusty nail → 잘못 거절(검색 점수 3.9 < 4.92) 0.5초 / capital of australia → 답함(분야 밖 통과) 1.6초 · 영어 일상 표현 10개: 정답 8 · 부분 1 · 잘못 거절 1(A100 3~10초) · 한계: 검색 — Top-10 포함률 .776(상한 .890), 짧은 구어 질문 잘못 거절 → 쿼리 확장·구어체 평가셋 / DB — MS MARCO 문단뿐 → MedQuAD 등 확장 / 분야 밖 — 건강 외 문단 약 9.8만 개 → 호주 수도에 답함
- **Visualization**: chatbot-test (table, 질문 × 결과 × 초)
- **Native-ready**: chatbot-test=yes
- **page_rhythm**: dense

#### Slide 14 - 결론

- **Audience move**: 개별 결과를 들음 → 핵심 메시지 하나와 세 가지 근거 수치를 기억함
- **Relationships**: 지표 먼저 → 검색 개선 → DPO 안전성 order(원인 → 결과)
- **Closing impact**: 테이크어웨이 = "지표를 먼저 세웠기 때문에, 정답률을 지키면서 더 안전한 의료 챗봇을 만들 수 있었다"; Composition Reference — 남색 면 위 결론 문장과 세 개의 큰 수치(.88 심판-사람 일치, .618 → .770 정답률, 35% → 20% 지어낸 답)
- **Title**: 지표를 먼저 세웠기에, 더 안전한 챗봇을 증명할 수 있었다
- **Content**: 심판 ↔ 사람 일치 .88 · 시험 정답률 .618 → .770 · 지어낸 답 35% → 20% · 다음: 구어체 검색 개선 · DB 확장 · 사람 판정 표본 확대
- **page_rhythm**: anchor

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 각 장 화면의 내용과 source md의 수치만 사용; 결론부터 말하고 근거 수치를 이어 설명; 새 수치 추가 금지
- **Total duration**: 15분 (장당 약 1분, 지표·DPO 장은 조금 길게)
- **Notes style**: conversational
- **Presentation purpose**: 파이프라인을 검색·생성 단계로 설명하고, LLM 심판으로 세운 지표로 각 개선(특히 DPO)을 증명하며 한계를 밝힌다
