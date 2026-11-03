# MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정

- Source: `MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정.pptx`
- Total slides: 12

## Slide 1

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-1-1.jpeg)

MS MARCO v2.1 · 의료 특화 RAG

근거로만 답하고,
모르면 거절하는 의료 챗봇

파이프라인보다 "어떻게 여기까지 왔는지"를 중심으로

[팀명]

·

[발표자]

·

2026.11.[__]

01

### Speaker Notes

파이프라인의 상세 구조보다는 우리가 어떤 의사결정을 거쳐 현재의 시스템을 구축했는지, 그 과정에서의 시도와 실패를 중심으로 공유하고자 합니다.

1

## Slide 2

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-2-1.jpeg)

Project Goal

의료 질문에는 근거 문서 안에서만 답하고, 근거가 약하면 답하지 않는다

근거로 답하기

모르면 거절

완전한 문장

검색한 문단 [1]~[5]의 내용만 쓰고, 문장마다 [번호]로 출처 표시

답 없는 건강 질문, 의료와 무관한 질문에는 "답할 수 없다"

짧은 단어 대신 사람이 읽기 좋은 문장형 답변

의료 분야 RAG의 핵심: 정확성과 안전성

02

### Speaker Notes

의료 분야 RAG의 가장 큰 목표는 안전입니다. 질문 분야 분포에서 의료가 13.1%로 가장 많았던 만큼, 틀린 답을 내놓기보다 모르면 거절하고 근거가 명확할 때만 답하는 것을 최우선으로 삼았습니다.

2

## Slide 3

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-3-1.jpeg)

Pipeline Overview

Retriever → Reranker → 거절 판단 → Generator

① 인덱싱 (사전 구축)

MS MARCO v2.1

코퍼스 구축
459,067개

임베딩
bge-base

벡터 인덱스
FAISS FlatIP

건강 질문 선별

② 검색·생성 (질문마다)

Retriever
Dense (Top-100)

Generator
Qwen2.5-7B + LoRA

Reranker
MiniLM (Top-5)

거절 판단
Score < 4.92

쿼리

답변 + 인용

Retriever는 Dense 기반. 쿼리와 문단을 같은 bge 모델로 임베딩해 FAISS에서 찾고, Reranker(cross-encoder)로 다시 정렬한다. 근거가 약하면 Generator를 부르지 않는다.

전체 파이프라인 구성 및 주요 모듈

03

### Speaker Notes

파이프라인은 크게 사전 구축 단계인 인덱싱과 실시간 검색·생성 단계로 나뉩니다. Retriever는 Dense 기반이며, Reranker를 거쳐 나온 점수가 4.92 미만이면 Generator를 호출하지 않고 즉시 거절하여 안전성을 확보합니다.

3

## Slide 4

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-4-1.jpeg)

Dataset: MS MARCO QnA v2.1

질문 하나 = 문단 10개 + 정답 + 문장형 정답

v2.1의 추가 필드 활용을 위해 v1.1 대신 v2.1 사용

// dev 질문 데이터 예시 (오타 포함)

필드

프로젝트 활용

query: "what kind of bacteria is in a kindey infection"

passages: 10개

query

쿼리 · 평가 질문

{ is_selected: 1, url: ...,

passage_text: "Causes of kidney infection. ... E. coli ..." }

passages

코퍼스 · 사이트 판별

is_selected: 0 인 문단 × 9

answers: ["E.coli bacteria"]

wellFormedAnswers: [일부 질문에만 있음]

is_selected

Recall·MRR 채점

answers

F1·정답 포함률

No Answer...

거절 평가

wellFormed...

문장형 LoRA 학습

실제 Bing 검색 질문 및 정답 구성 (train 808,731 / dev 101,093)

04

### Speaker Notes

v1.1 대신 v2.1을 선택한 결정적인 이유는 wellFormedAnswers와 같은 문장형 정답 데이터가 포함되어 있어, 사람이 읽기 좋은 답변을 생성하도록 학습시키기에 적합했기 때문입니다. 오타가 포함된 실제 검색어 환경을 그대로 반영했습니다.

4

## Slide 5

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-5-1.jpeg)

Data Processing

의료 사이트 33개로 질문을 고르고, 방해 문단을 일부러 섞었다

코퍼스 구성 (총 459,067개)

평가셋 650문항

출처

문단 수

역할

• 건강·답 있음: 500

dev 건강 질문

131,143

평가 정답지

• 건강·답 없음: 100

train 건강 질문

229,697

검색 난이도 상승

• 분야 밖 질문: 50

dev 일반 질문

98,227

분야 밖 방해 문단

• 검증용(방법 선택): 200

결정: 코퍼스를 의료 사이트 문단으로 제한하지 않음. 평가 정답 문단 중 의료 사이트 출처가 40%뿐이라 제한하면 평가가 무너짐

질문 선별 규칙: 문단 10개 중 2개 이상이 의료 사이트 출처인 경우

05

### Speaker Notes

평가 결과의 왜곡을 막기 위해 코퍼스를 의료 사이트 문단으로만 제한하지 않았습니다. 대신 건강 질문을 선별하고 방해 문단을 적절히 섞어 실제 검색 환경과 유사한 46만 개의 코퍼스와 650개의 평가셋을 구축했습니다.

5

## Slide 6

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-6-1.jpeg)

Step ① Retriever & Reranker

Dense 검색이 BM25의 두 배, Reranker로 한 번 더

방법 (시험 500문항)

Recall@10

Recall@100

MRR@10

BM25

0.406

0.710

0.202

Dense (bge-base)

0.688

0.938

0.401

Hybrid (Dense + BM25, RRF)

0.608

-

-

Dense → MiniLM-L-6 Reranker (채택)

0.760

-

0.445

Dense → bge-reranker-base

0.758

-

0.448

뺌 · HYBRID

채택 · MINILM-L-6

참고 · 정답 문장으로 검색

BM25가 섞이며 오히려 Dense 단독보다 낮아짐

bge-reranker와 점수는 거의 같고, 더 작고 빠름

Recall@10 0.890 — 표현 차이가 큰 원인

방법은 검증 200으로 선택, 시험 500은 마지막에 한 번만 채점 (치팅 방지)

06

### Speaker Notes

Dense 검색이 BM25 대비 두 배 이상의 Recall 성능을 보였으며, MiniLM 기반의 Reranker를 추가하여 최종 성능을 확보했습니다. 치팅 방지를 위해 검증셋으로 방법론을 확정한 뒤 시험셋은 단 한 번만 채점했습니다.

6

## Slide 7

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-7-1.jpeg)

Step ② Rejection & Comparison

점수로 먼저 거르고, RAG의 정확도와 안전을 함께 본다

4.92

Reranker 최고 점수 기준선

검증 200문항의 최고 점수 하위 5% 기준. 이보다 낮으면 Generator를 부르지 않고 바로 거절. 잘못 거절 비율을 5% 내외로 통제.

지표 (650문항)

LLM 단독

RAG 기본

RAG 개선

F1 (짧은 정답)

0.226

0.286

0.282

ROUGE-L 문장형

0.286

0.337

0.330

정답 포함률

0.370

0.506

0.495

잘못 거절 (낮을수록 좋음)

0.012

0.028

0.056

답 없음 거절률

0.02

0.17

0.44

분야 밖 거절률

0.50

0.58

0.82

RAG 개선: 기본 + 중복 제거 + 거절 기준 적용 (생성 모델: Qwen 원본)

07

### Speaker Notes

단순히 프롬프트로 거절을 유도했을 때보다 점수 기반의 필터링이 분야 밖 질문 거절률을 58%에서 82%까지 획기적으로 높였습니다. 다만 이 과정에서 정답이 있는 질문을 오거절하는 비율이 2.8%에서 5.6%로 늘어나는 비용이 발생했습니다.

7

## Slide 8

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-8-1.jpeg)

Step ③ Generator Prompt

문서 안에서만 답하고, 문장마다 출처를 단다

SYSTEM PROMPT

USER PROMPT

You are a careful medical information assistant.

Documents:

Rules:

[1] (사이트) 문단

1. Answer ONLY with facts stated in the numbered documents. Do not

...

add outside knowledge.

[5] (사이트) 문단

2. After each sentence, cite the supporting document numbers like

[1] or [2][4].

Question: 질문

3. If the question is not about health or medicine, or the

documents do not contain the answer, reply with exactly this

sentence: "Sorry, I can't answer that from the medical documents I

have."

• Reranker Top-5 문단에 번호와 사이트 등급 부여

4. Answer in 2-4 short sentences.

• 거절 문장 고정으로 자동 채점 신뢰도 확보

• LoRA 학습도 동일 프롬프트 형식 적용

의료 RAG 가드레일: 외부 지식 배제 및 출처 표기 강제

08

### Speaker Notes

프롬프트는 '문서 내 사실로만 답할 것'과 '출처 표기'를 엄격히 강제합니다. 특히 거절 문장을 고정하여 자동 채점의 정확도를 높였으며, 이 형식을 LoRA 학습 데이터에도 동일하게 적용했습니다.

8

## Slide 9

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-9-1.jpeg)

Step ③ Generator fine-tuning

짧은 답에서 문장형 답으로, 학습 데이터부터 바꿨다

이전 모델 (V1.1 LORA)

이번 모델 (V2.1 문장형 LORA)

짧은 정답 구절 중심 학습

wellFormedAnswers 기반 학습

짧은 정답(answers) 구절로 학습하여 답변이 약 14단어로 매우 간결하게 출력됨

건강 질문의 문장형 정답 + 검색 문단 5개를 활용. "문장 [번호]" 형식 강조, 15% 거절 예시 포함

출력 예시:
"E.coli bacteria [1]"

출력 예시:
"신장 감염은 대개 E. coli라고 불리는 박테리아에 의해 발생합니다 [1]. 이 박테리아는 주로 하부 요로를 통해 체내로 유입됩니다 [2]."

Qwen2.5-7B-Instruct · bf16 LoRA r=16 · 1 epoch · 답변 부분만 손실 계산 · 정답 문단이 Top-5에 있는 질문만 학습

LoRA 학습 구성 및 데이터 전략

09

### Speaker Notes

짧은 단답형으로 출력되던 v1.1 모델의 한계를 극복하기 위해, v2.1의 문장형 정답 데이터를 학습에 활용했습니다. 15%의 거절 예시를 포함하여 모델이 스스로 답할 수 없는 상황을 인지하도록 유도했습니다.

9

## Slide 10

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-10-1.jpeg)

Analysis: Trade-off

문장은 좋아졌지만, 정답 내용은 덜 담겼다

ROUGE-L 문장형

정답 포함률

0.56

0.40

↑ 0.33에서 상승

↓ 0.50에서 하락

• 원인: 한 문장에 문서 하나의 사실만 담으며, 정답 문서를 인용한 답은 39% (28/71)에 불과

• 잘못 거절: 5.6% → 10.2%로 증가

• 결정: 팀 목표인 '사람이 읽기 좋은 문장형 답변'을 위해 정답 포함률 일부 포기

• 데이터: 학습용 문장형 정답 중 짧은 정답 내용이 누락된 "엉터리 정답" 혼입

지표의 이면: 문장 품질과 정보 충실도 간의 균형점 확인

10

### Speaker Notes

학습 결과 문장의 품질을 나타내는 ROUGE-L은 0.33에서 0.56으로 크게 개선되었으나, 정답을 누락하는 트레이드오프가 발생했습니다. 이는 학습 데이터 자체의 품질 문제와 한 문장에 하나의 사실만 담으려는 모델의 성향 때문으로 분석됩니다.

10

## Slide 11

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-11-1.jpeg)

Next Steps: Limitations & Planning

정답 문단을 못 찾으면, Generator가 좋아도 소용없다

미실행 개선안 07

CURRENT BOTTLENECK

Reranker 파인튜닝

정답 문단 Top-5 포함 시 F1

건강 질문 8,000개로 MiniLM 추가 학습. 정답 문단 1개 + 오답 7개 구성. 검증 MRR 향상 시 교체.

0.415

미실행 개선안 07

학습 데이터 필터링

정답 문단 Top-5 미포함 시 F1

0.237

짧은 정답 포함률 50% 미만 데이터 제외. 새 Reranker로 추출한 문단으로 실제 환경 재구축.

그 밖의 단계: 입력 문단 확대 (5→10), 틀린 사례 분석, LLM-as-a-judge 평가 도입

근거 Recall@5는 0.628. 질문 10개 중 4개는 Generator가 정답을 보지도 못함. Retriever 개선이 최우선 과제.

08 RAG 개선 + LoRA 기준 (정답 문단 있음 314/500)

11

### Speaker Notes

현재 시스템의 가장 큰 병목은 Retriever입니다. 정답 문단이 Top-5 안에 없을 경우 성능이 급격히 하락하므로, 향후 Reranker 파인튜닝과 학습 데이터 정제(07 계획)를 통해 이 구간의 성능을 개선할 예정입니다.

11

## Slide 12

![preencoded.png](MS MARCO v2.1 의료 특화 RAG 챗봇 프로젝트 진행 과정_files/image-12-1.jpeg)

Closing: Key Takeaways

직접 비교해 보기 전에는 알 수 없었던 것들

데이터를 좁히면 평가가 무너진다

알려진 좋은 방법도 예외가 있다

의료 사이트 문단만 남기면 정답 문단 대부분이 사라져 정상적인 평가가 불가능했습니다.

일반적으로 성능 향상을 기대하는 Hybrid 방식이 Dense 단독보다 낮은 성능을 보였습니다.

거절은 점수 기준이 확실하다

지표 하나만 보면 속기 쉽다

프롬프트 제어보다 임계치 기반 거절이 효과적이었으나, 잘못된 거절의 증가라는 대가가 따랐습니다.

문장의 유창성(ROUGE-L)이 개선될 때 정보 포함률은 오히려 감소하는 트레이드오프를 확인했습니다.

데모: Gradio 챗봇

Thank You

대화 흐름, 근거 문단, 출처 등급 확인 가능 · 정보 제공용

MS MARCO v2.1 기반 의료 특화 RAG 프로젝트 프로젝트 종료 및 제언

12

### Speaker Notes

이번 프로젝트를 통해 이론적으로 알고 있던 Hybrid 방식이 실제 데이터에서는 오히려 손해를 볼 수도 있다는 점, 그리고 지표 하나에 매몰되기보다 전체적인 트레이드오프를 살피는 것이 얼마나 중요한지 배울 수 있었습니다.

12
