<!-- ppt-master-schema: design-spec/v1 -->
# 의료 특화 RAG 챗봇 최종 발표 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | medical_rag_final — MS MARCO v2.1 의료 특화 RAG 챗봇 최종 발표 |
| Canvas Format | ppt169 (1280×720) |
| Page Count | 16 |
| Primary Language | ko-KR |
| Target Audience | 멋사 NLP 6기 수강생·멘토·강사. RAG와 LLM 기초는 알지만 이 프로젝트의 세부 실험(01~19)은 처음 보는 사람들 |
| Communication Intent | 최종 결과를 먼저 보고하고, 어떤 판단과 실패를 거쳐 그 결과에 이르렀는지(평가 방식 교체, 검색 앙상블, 생성 모델 교체, DPO) 설명한 뒤, 남은 한계와 다음 단계를 공유한다 |
| Desired Audience Outcome | 청중이 최종 챗봇 구성과 성능(시험 정답률 .770, 진짜 답 없는 질문 거절률 .804)을 이해하고, F1 대신 LLM 심판을 쓴 이유와 DPO를 채택한 근거를 납득하며, 남은 병목이 검색이라는 점에 동의한다 |
| Core Message / Ask / Action | 근거로만 답하고 모르면 거절하는 의료 챗봇: 검색 앙상블 + Qwen3-8B + DPO로 정답률을 지키면서(.736 → .770) 지어낸 답을 35%에서 20%로 줄였다. 남은 오답의 주원인은 검색이다 |
| Delivery Context | 주: 발표자가 진행하는 최종 프로젝트 발표(약 15~20분)와 챗봇 데모. 부: 발표 후 팀 저장소·공유 자료로 따로 읽힘 |
| Artifact Afterlife | 팀 프로젝트 결과 기록과 개인 포트폴리오 자료 |
| Reading Mode | presentation |
| Content Strategy | balanced default (content_divergence blank) — 소스 사실을 유지하며 showcase 흐름으로 재구성; 2026-11-03 수정 요청: 쉬운 단어 + RAG 관행 용어(Retriever/Reranker/Generator, Recall@k, Threshold, 환각, LLM-as-a-Judge, OOD, Passage) |
| Design Style | showcase + soft-rounded, 청록 + 신호 주황 |
| AI Image Acquisition Path | not applicable (image usage: none) |
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
| Margins | 64 px left/right, 56 px top/bottom |
| Content Area | x 64–1216, y 56–664 |

## III. Visual Theme

### Theme Style

- **Mode**: showcase
- **Visual style**: soft-rounded
- **Theme**: 숫자가 주인공인 결과 발표. 큰 숫자·짧은 문구가 페이지 중심, 둥근 카드와 알약 태그가 보조
- **Tone**: 자신 있고 친근하며 정직함 (한계도 숨기지 않음)

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FFFFFF | 기본 바탕 |
| Secondary background | #F2F5F7 | 카드 뒷면, 띠 |
| Primary | #0B4F6C | 표지·장 페이지 색면, 제목, 주요 막대 |
| Accent | #E4572E | 최종 결과·핵심 숫자 한 곳 강조 |
| Secondary accent | #7B97AB | 비교 대상·보조 계열 |
| Body text | #1C2630 | 본문 |
| Secondary text | #5B6B78 | 캡션, 출처 줄, 주석 |
| Divider | #D5DEE4 | 구분선, 표 괘선 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 친근한 산세리프, 굵게 | Malgun Gothic | Arial | sans-serif |
| Body | 친근한 산세리프, 보통 | Malgun Gothic | Arial | sans-serif |

- **Title stack**: Malgun Gothic, Arial, sans-serif
- **Body stack**: Malgun Gothic, Arial, sans-serif

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 32 |
| Title | 56 |
| Subtitle | 44 |
| Annotation | 24 |
| Cover title | 88 |
| Display | 128 |
| Footnote | 18 |

- **Role rationale**: cover_title은 표지·마무리 큰 문구, display는 반복되는 핵심 숫자(.770, .804 등), footnote는 데이터 페이지 출처 줄. 모두 같은 글꼴 가족.

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 큰 숫자 또는 짧은 결론 → 한 줄 설명 → 작은 근거·출처
- **Composition tendency**: 페이지마다 초점 하나. 넓은 여백, 둥근 카드는 근거 묶음에만 사용, 표지·장 페이지는 청록 색면을 크게
- **Cross-page continuity**: 실험 번호 알약 태그(EXP 14 … EXP 19)와 상단 진행 표시가 실험 구간 페이지에 반복; 최종 결과 숫자 .770은 주황으로만 표기
- **Spacing posture**: open — 발표형이라 여백 넉넉, 데이터 페이지만 중간 밀도
- **Spacing anchors**: page margin 64 · block gap 32 · column gutter 32 · corner radius 20 · body leading 1.4

## VI. Icon Usage Specification

- **Primary bundled library**: tabler-outline
- **Stroke Width**: 2

| Icon Path | Suitable Scenarios |
| --- | --- |
| icons/tabler-outline/search.svg | |
| icons/tabler-outline/database.svg | |
| icons/tabler-outline/filter.svg | |
| icons/tabler-outline/message-chatbot.svg | |
| icons/tabler-outline/brain.svg | |
| icons/tabler-outline/shield-check.svg | |
| icons/tabler-outline/scale.svg | |
| icons/tabler-outline/alert-triangle.svg | |
| icons/tabler-outline/x.svg | |
| icons/tabler-outline/check.svg | |
| icons/tabler-outline/language.svg | |
| icons/tabler-outline/clock.svg | |
| icons/tabler-outline/file-text.svg | |
| icons/tabler-outline/target.svg | |
| icons/tabler-outline/flask.svg | |
| icons/tabler-outline/chart-bar.svg | |
| icons/tabler-outline/route.svg | |
| icons/tabler-outline/player-play.svg | |
| icons/tabler-outline/gavel.svg | |
| icons/tabler-outline/books.svg | |
| icons/tabler-outline/arrows-sort.svg | |
| icons/tabler-outline/ban.svg | |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| P10 | chart | horizontal_bar_chart | 시스템별 시험 정답률 비교, 생성 모델 교체 효과 강조 |
| P12 | table | metric_table | 안전성·정답률 교환: 설정별 정답률·잘못 거절·진짜 답 없음 거절 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## IX. Content Outline

### Part 1: 결과 먼저

#### Slide 01 - 표지

- **Audience move**: 무슨 발표인지 모름 → "환각을 줄인 의료 챗봇" 이야기임을 안다
- **Relationships**: none
- **Cover impact**: 훅 — "근거로만 답하고, 모르면 거절한다" + 작은 숫자 띠 "환각 35% → 20%"; 청록 큰 색면이 한쪽에서 번져 나오는 구성 (Reference)
- **Title**: 근거로만 답하고, 모르면 거절한다
- **Core message**: MS MARCO v2.1 기반 의료 특화 RAG 챗봇 최종 발표
- **Content**: 키커: MS MARCO v2.1 · 의료 특화 RAG / 부제: 환각 35% → 20% / 멋사 NLP 6기 · 프로젝트 02 지식 기반 QA · [팀명] · [발표자] · 2026.11

#### Slide 02 - 최종 결과

- **Audience move**: 결과를 모름 → 세 숫자로 최종 성능을 기억한다
- **Relationships**: 세 지표가 병렬(membership); 각 지표는 이전 값과 대비(contrast)
- **Composition**: 주황 .770이 가장 크고, .804와 35%→20%가 옆에 작게; 아래 한 줄 비교 (Reference)
- **Title**: 정답률은 지키고, 환각은 줄였다
- **Core message**: 최종 챗봇 시험 정답률 .770, 답 없는 질문 거절 .804
- **Content**: .770 시험 정답률 (첫 RAG .736, LLM만 .618) · .804 답 없는 질문 거절률 (DPO 전 .652) · 환각 35% → 20% / 출처: 시험셋 답 있는 건강 질문 500, LLM-as-a-Judge Qwen2.5-14B

#### Slide 03 - 목표와 데이터

- **Audience move**: 문제 설정을 모름 → 목표 세 가지와 평가 데이터 규모를 안다
- **Relationships**: 목표 세 가지 병렬(membership); 데이터 → 평가셋 구성(parent)
- **Title**: 목표: 근거로 답하고, 모르면 거절
- **Core message**: 정확성과 안전성이 의료 RAG의 핵심
- **Content**: 근거로 답하기 (문장마다 [번호] 출처) · 모르면 거절 · 완전한 문장 / MS MARCO v2.1 문단 459,067 · 평가 650 = 답 있음 500 + 답 없음 100 + OOD 50 · 검증 200으로 설정 선택, 시험은 한 번만

#### Slide 04 - FAISS DB 구축 과정

- **Audience move**: DB를 어떻게 만들었는지 모름 → 데이터 받기부터 FAISS 인덱스까지 5단계를 안다
- **Relationships**: 데이터 받기 → 건강 질문 고르기 → Passage 모으기 → 임베딩 → FAISS 인덱스 순서(order)
- **Composition**: 왼쪽 번호 단계 목록, 오른쪽 IndexFlatIP 선택 이유와 Dense Recall@10 (Reference)
- **Title**: FAISS DB는 이렇게 만들었다
- **Core message**: MS MARCO v2.1에서 건강 질문의 Passage를 모아 bge-base로 임베딩하고 FAISS IndexFlatIP에 저장
- **Content**: 데이터 받기 (MS MARCO v2.1, train 808,731 / dev 101,093) · 건강 질문 고르기 (Passage 10개 중 2개 이상이 의료 사이트 33곳) · Passage 모으기 (중복 제거, pid 0부터, 459,067개) · 임베딩 (bge-base-en-v1.5, 768차원, float16, 정규화) · FAISS IndexFlatIP (질문 접두어, Top-100) / 왜 IndexFlatIP: 근사 검색 없이 전부 비교, 46만 개면 빠르고 정확 / Dense Recall@10 .688 vs BM25 .406 (Test 500) / 출처: 02_health_embedding.ipynb

#### Slide 05 - 데이터 구조

- **Audience move**: 파일 구조를 모름 → corpus·eval 필드와 pid 연결을 안다
- **Relationships**: corpus.jsonl 필드 묶음(membership), eval.jsonl 필드 묶음(membership), gold_pids → pid 연결(link), src 세 종류(membership), pid = 줄 번호 = 임베딩 행 = FAISS id(link)
- **Composition**: 두 레코드 카드를 나란히, gold_pids에서 pid로 화살표, 아래 src 세 종류와 id 연결 줄 (Reference)
- **Title**: 데이터는 pid 하나로 이어진다
- **Core message**: Passage, 임베딩, FAISS id가 모두 같은 pid로 이어지고, 평가 질문은 gold_pids로 정답 Passage를 가리킨다
- **Content**: corpus.jsonl 459,067줄 {pid, text, url, src} / eval.jsonl 650줄 {qid, query, gold_pids, answers, well_formed, answerable, query_type, domain} / src: dev_health 131,143 · train_health 229,697 · dev_other 98,227 / pid i = corpus i번째 줄 = 임베딩 i번째 행 = FAISS id i / corpus_emb_bge.npy 459,067 × 768 float16 · faiss_bge_flatip.index · 평가 qid가 학습 데이터와 겹치지 않음을 검사

#### Slide 06 - 최종 파이프라인

- **Audience move**: 시스템 모양을 모름 → 질문이 답이 되기까지 단계를 따라간다
- **Relationships**: 질문 → 번역(한국어일 때) → 검색 → 재정렬 → 거절 판단 → 생성 → 답변 순서(order); 거절 판단에서 거절로 갈라짐(link)
- **Composition**: 왼쪽에서 오른쪽 한 줄 흐름, 거절 판단에서 아래로 분기 (Reference)
- **Title**: 넓게 찾고, 먼저 거르고, 마지막에 답한다
- **Core message**: 앙상블 재정렬 상위 10 + Qwen3-8B + DPO, 재정렬 점수가 낮으면 LLM 전에 거절
- **Content**: 질문 (한국어면 영어로 번역) · bge-base 검색 100 · 앙상블 재정렬 bge-reranker-large + v2-m3 → 상위 10 · Threshold: MiniLM 최고점 < 4.92 · Qwen3-8B + DPO LoRA · 답변 + [번호] 출처

### Part 2: 어떻게 여기까지 왔나

#### Slide 07 - 실험 지도

- **Audience move**: 실험 순서를 모름 → 08 이후 다섯 단계 흐름을 지도로 본다
- **Relationships**: 08 → 14 → 15 → 16 → 17 → 18·19 순서(order)
- **Composition**: 알약 체인 타임라인, 각 단계에 한 단어 (Reference)
- **Title**: 첫 RAG .736에서 출발한 다섯 번의 실험
- **Core message**: 평가를 고치고, 모델을 바꾸고, 안전성을 학습시켰다
- **Content**: 08 첫 RAG .736 · 14 평가 교체 · 15 SFT v2 · 16 검색×생성 · 17 DPO · 18·19 거절 기준
- **Motion suggestion**: 알약 체인이 이후 실험 페이지의 진행 표시로 이어짐 (Morph 후보)

#### Slide 08 - EXP 14 평가 교체

- **Audience move**: F1을 믿음 → F1이 짧은 답을 과대평가했음을 안다
- **Relationships**: F1 순위와 Judge 순위의 대비(contrast)
- **Composition**: 좌우 대비 — F1 기준 vs Judge 기준 (Reference)
- **Title**: F1 점수가 실제 성능과 달랐다
- **Core message**: 단어 겹침만 보는 F1에서 LLM-as-a-Judge 정답률로 바꿨다
- **Content**: F1: 06 문장형 LoRA가 최고 (.349) / Judge: 원본 .736 vs LoRA .450 / Judge-사람 일치 .88 → 이후 모든 비교는 Judge 정답률

#### Slide 09 - EXP 15 SFT v2

- **Audience move**: 06 실패 원인을 모름 → 잘못된 거절 학습이 원인임을 안다
- **Relationships**: 원인 → 수정 → 결과(order); 결과와 원본 대비(contrast)
- **Title**: 거절을 잘못 가르쳤다
- **Core message**: 답 가능한 질문을 거절로 학습한 것이 원인, 고치니 .724로 복구
- **Content**: 정답 문단이 상위 5 밖이라 거절로 학습한 714개 중 500개(70%)는 실제로 답 가능 / .450 → .724 · 원본 .736은 못 넘음 (모델이 만든 답으로 다시 학습한 한계)

#### Slide 10 - EXP 16 검색 × 생성 모델

- **Audience move**: 무엇이 가장 효과적이었는지 모름 → 생성 모델 교체가 가장 컸음을 본다
- **Relationships**: 여덟 시스템의 정답률 순위 비교(contrast)
- **Composition**: 가로 막대 차트가 주인공, 최종 두 막대만 강조 (Reference)
- **Title**: 가장 큰 개선은 LLM 교체
- **Core message**: 앙상블 + Qwen3-8B .782, 첫 RAG 대비 +4.6점 (95% CI +0.8 ~ +8.2)
- **Content**: 막대: LLM만 .618 · 06 문장형 LoRA .450 · 15 SFT v2 .724 · 08 첫 RAG .736 · 앙상블+Qwen2.5-14B .760 · 최종 챗봇(+DPO) .770 · 앙상블+Qwen3-8B .782 · 앙상블+Qwen3-14B .790 / 메모: Recall@5 .628→.654, Recall@10 .776 · 14B는 검증 동점이라 가벼운 8B 선택
- **Visualization**: system-accuracy — chart/horizontal_bar_chart
- **Native-ready**: system-accuracy=yes

#### Slide 11 - EXP 17 DPO

- **Audience move**: DPO의 효과를 모름 → 거절은 크게 늘고 정답률은 거의 그대로임을 안다
- **Relationships**: DPO 전후 두 지표 대비(contrast)
- **Composition**: 전→후 숫자 쌍 두 개, 거절률 쪽이 주인공 (Reference)
- **Title**: DPO로 환각을 줄였다
- **Core message**: 답 없음 거절 .652 → .804, 정답률 .782 → .770 (유의하지 않음)
- **Content**: Judge가 고른 좋은 답 vs 오답·환각·오거절 224쌍 · LoRA r16 직접 구현 / 거절 .652 → .804 / 정답률 .782 → .770 (-1.2점, 유의하지 않음)

#### Slide 12 - EXP 18·19 안전성과 정답률 교환

- **Audience move**: 같은 안전성을 다른 방법으로 얻을 수 있다고 생각 → DPO가 정답 손실이 가장 적음을 본다
- **Relationships**: 네 설정의 세 지표 비교(contrast)
- **Title**: 안전성은 Threshold보다 DPO가 낫다
- **Core message**: 거절 기준을 올리면 정답률 .678, DPO로 얻으면 .770
- **Content**: 표 행: Qwen3-8B + 기준 4.92 (.786 / .046 / .652, 환각 35%) · 기준 올림 6.80 (.678 / .184 / .826) · DPO + 기준 4.92 최종 (.770 / .078 / .804, 채택) · + Domain Filter (.626, 정답 72개 손실 → 제거) / 메모: 프롬프트 3종 차이 없음 · DPO 모델 기준 4.72 ≈ 4.92 / 출처: 시험 650
- **Visualization**: safety-tradeoff — table/metric_table
- **Native-ready**: safety-tradeoff=yes

### Part 3: 써 보고, 남은 것

#### Slide 13 - 챗봇 테스트

- **Audience move**: 실제 질문에서 어떤지 모름 → 일상 표현에도 대부분 맞히고 실패 유형을 안다
- **Relationships**: 결과 유형별 묶음(membership): 정답 / 부분 / 오거절
- **Composition**: 큰 8/10 숫자와 대표 질문 카드 3~4개 (Reference)
- **Title**: 일상 표현 10개 중 8개 정답
- **Core message**: 정답 8, 부분 1, 오거절 1; 한국어는 번역을 거쳐 답함
- **Content**: 정답 예: "ringing sound in ears that won't go away" → tinnitus · "butterfly shaped gland … too slow" → hypothyroidism / 오거절: "shot you get after stepping on a rusty nail" (재정렬 점수 3.9 < 4.92) / 한국어: "위궤양을 일으키는 세균이 뭐야?" → 헬리코박터 파일로리 (번역 경유) / 응답 약 5초 (A100)

#### Slide 14 - 데모

- **Audience move**: 숫자로만 봄 → 직접 동작을 본다
- **Relationships**: none
- **Composition**: 넓은 여백, 시연 안내 한 줄과 질문 세 개 (Reference)
- **Title**: 직접 물어보기
- **Core message**: Gradio 챗봇으로 답변, 근거 문단, 출처 등급을 확인
- **Content**: 답하는 질문: "the bacteria that causes stomach ulcers" / 거절하는 질문: "can drinking coke every day cause dementia" / 한국어: "술 마시면 얼굴이 빨개지는 이유가 뭐야?" / 정보 제공용, 의료 조언 아님

#### Slide 15 - 남은 과제

- **Audience move**: 시스템이 완성됐다고 봄 → 남은 병목이 검색임에 동의한다
- **Relationships**: 네 가지 한계 병렬(membership); 검색 병목이 가장 큼(parent)
- **Composition**: 검색 병목 카드가 크고 나머지 셋이 작게 (Reference)
- **Title**: 남은 오답의 주원인은 Retriever
- **Core message**: Recall@10 .776 — 검색 개선이 다음 단계
- **Content**: 검색: 상위 10 포함 .776, 구어체·multi-hop 평가셋으로 개선 · 짧은 구어 질문 오거절 ("녹슨 못 주사"): Query Expansion 필요 · OOD: DB에 건강 외 문단 약 9.8만 개, "호주 수도"에 답함 (OOD 거절률 .84) · DB 범위: MS MARCO 문단뿐 → MedQuAD 등 확장

#### Slide 16 - 마무리

- **Audience move**: 개별 실험을 들음 → 네 가지 배운 점을 가져간다
- **Relationships**: 네 가지 교훈 병렬(membership)
- **Closing impact**: 핵심 문구 "평가를 바로잡자, 진짜 개선이 보였다" + 네 교훈; 청록 색면 위 큰 문구 (Reference)
- **Title**: 평가를 바로잡자, 진짜 개선이 보였다
- **Core message**: 측정 → 모델 → 안전성 → 검색 순서로 배운 것
- **Content**: 지표가 틀리면 개선도 틀린다 (F1 → Judge) · 가장 큰 개선은 생성 모델 교체 (+4.6) · 안전성은 점수 기준보다 DPO로 (.770 vs .678) · 다음 병목은 검색 (.776) / 감사합니다 · Q&A

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 페이지에 없는 설명(실험 배경, 수치 해석, 전환 문장)을 노트에 담는다. 수치는 소스 문서(v21_final_results.md 등)에 있는 값만 사용
- **Total duration**: 약 15~20분 (데모 포함)
- **Notes style**: 결론 먼저, 짧고 힘 있는 구어체
- **Presentation purpose**: 최종 결과 보고 → 판단과 실패 과정 설명 → 남은 한계와 다음 단계 공유
