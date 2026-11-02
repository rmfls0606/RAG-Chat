# data/

MS MARCO 질문을 의료 / 비의료로 라벨링하고, 그 결과로 검색·학습·평가용 데이터를 만든 폴더입니다.

- 라벨러: `qwen2.5:7b-instruct`, 프롬프트 `v2`
- split: MS MARCO의 `train` / `validation`을 그대로 씀 (아래 파일명의 `tune` = train, `test` = validation)
- 라벨
  - `A` = core_medical (질병·증상·약·해부·검사 등 사람 건강 핵심)
  - `B` = health_adjacent (영양·운동·수면·의료비 등 건강 주변)
  - `C` = non_medical
- pool (질문을 뽑아 온 곳)
  - `med_url` = 정답 문단 URL이 의료 사이트인 질문
  - `no_med` = 그 밖의 질문

> 표시된 "추정"은 파일 내용을 보고 유추한 설명입니다. 만든 노트북 기준으로 확인이 필요합니다.

---

## labels/ — 라벨링 결과와 검수

| 파일 | 행 수 | 내용 |
|---|---|---|
| `raw_v2.jsonl` | 16,440 | 라벨러 원본 출력. `key`(`split:query_id`)와 `raw`(JSON 문자열: `about_human_health`, `label`, `high_risk`, `time_sensitive`)만 있고 질문 원문은 없음 |
| `query_labels.parquet` | 16,440 | 질문 원문 + 라벨 전체. 컬럼: `query_id`, `split`, `query`, `query_type`, `answers`, `pool`, `context`(정답 문단), `label`, `high_risk`, `time_sensitive`, `parse_ok`, `raw`, `prompt_version`, `gen_model`. 라벨 분포 A 6,129 / B 1,588 / C 8,723 |
| `review_disagreements.csv` | 26 | 라벨러(LLM)와 Codex 라벨이 엇갈린 질문과 사람 판단 메모. 컬럼: `query`, `pool`, `label_codex`, `label_llm`, `note` |
| `medical_final.parquet` | 7,559 | **최종 의료 데이터.** `query_labels`의 A+B(7,717행)에서 비의료 158행을 뺀 것. 컬럼은 `query_labels`와 같음. A 6,105 / B 1,454 |
| `medical_final.csv` | 7,559 | 위와 같은 내용, `context` 컬럼만 뺀 CSV (열어 보기용) |
| `excluded_all.csv` | 158 | 의료 데이터에서 뺀 행 전체 (`split`, `query_id`, `label`, `pool`, `query`, `번역`, `분류`, `제안`, `판단`, `추천`). 파이프라인에서 쓸 **제외 목록**은 이 파일 |
| `excluded_confirmed.csv` | 120 | 위 158행 중 1차 검토에서 바로 제외가 확정된 행. `excluded_all.csv`에 모두 포함됨 (중복) |
| `review_false_medical.csv` | 63 | 판단이 갈렸던 행과 최종 판단(유지 24 / 제외 38 / 해당없음 1). 학습에는 안 쓰는 검수 기록 |

### 2026-11-02 검수 요약
- 대상: A+B 7,717행. B는 전부, A는 `no_med` 풀 228행과 키워드 검색으로 걸린 행만 봄 → A에는 못 찾은 오분류가 남아 있을 수 있음
- 제외 기준: 반려동물·가축, 식물, 요리·식품 보관, 미용·생활, 일반 세포·분자생물학, 상식·인물·직업, 정답이 틀리거나 질문과 안 맞는 행
- 유지로 결정한 경계 사례: 사람 응급처치(개 물림), 임상 미생물 검사, 영양 정보, 의료 시술·검사 비용 11건, 독감 발견 시기, 자전거 헬멧
- 의료비 질문은 일부만 남김. B에는 검토하지 않은 비용 질문(무릎 인공관절, 허셉틴 등)이 더 있음
- 알려진 문제
  - `train:55795`(what is the center part of the layer called)는 raw JSON 키가 `high_rircular_risk`로 깨져 있음 → 제외함
  - C인데 `about_human_health=true`인 행 8개 (예: `what is amitiza for`, `define birth defect`) → 의료로 되살릴지 미검토

---

## processed/ — 학습·평가용 데이터

> ⚠️ 모두 **검수 전** `query_labels.parquet`로 만든 파일입니다. 아래 "제외 포함" 열의 행이 아직 들어 있으니, 다시 쓰려면 `labels/excluded_all.csv`로 걸러서 새로 만들어야 합니다.

### processed/labeled/ — 질문 세트

| 파일 | 행 수 | split | 라벨 | 제외 포함 | 내용 |
|---|---|---|---|---|---|
| `lab_med_tune.parquet` | 500 | train | A | 0 | 라벨 A 의료 질문 (튜닝용) |
| `lab_med_test.parquet` | 598 | validation | A | 2 | 라벨 A 의료 질문 (평가용) |
| `lab_med_ext_tune.parquet` | 18 | train | A | 1 | 확장 의료 질문 (추정: `med_url` 풀 밖에서 A로 라벨된 질문) |
| `lab_med_ext_test.parquet` | 210 | validation | A | 18 | 위와 같음, 평가용. 205행은 `gold_pids`가 비어 있음 |
| `lab_b_test.parquet` | 143 | validation | B | 6 | health_adjacent 질문 (평가용) |
| `lab_ood_tune.parquet` | 500 | train | C | 0 | 분야 밖 질문 (튜닝용). `gold_pids` 없음 |
| `lab_ood_test.parquet` | 1,000 | validation | C | 0 | 분야 밖 질문 (평가용). `gold_pids` 없음 |
| `url_med_tune.parquet` | 500 | train | – | 0 | URL 기준으로만 뽑은 의료 질문 (라벨 없음, 비교용 추정) |
| `url_med_test.parquet` | 840 | validation | – | 8 | 위와 같음, 평가용 |
| `url_ood_tune.parquet` | 500 | 대부분 split 매칭 안 됨 | – | 1 | URL 기준 분야 밖 질문 (추정: 라벨링 대상 밖에서 뽑음) |

공통 컬럼: `query_id`, `query`, `query_type`, `answers`, `gold_pids`(정답 문단 id), `lab_*`는 여기에 `label`, `high_risk`, `time_sensitive`가 더 있음.

### processed/finetune/

| 파일 | 행 수 | 제외 포함 | 내용 |
|---|---|---|---|
| `train_pairs.parquet` | 5,922 | 43 | 임베딩·리랭커 파인튜닝용 (질문, 정답 문단, 오답 문단) 쌍. train split, A 4,803 / B 1,119. 컬럼: `query_id`, `query`, `label`, `pool`, `gold_pids`, `neg_pids` |

### processed/lora/

| 파일 | 행 수 | 내용 |
|---|---|---|
| `train.jsonl` | 2,000 | RAG 답변 형식 LoRA 학습 데이터. 한 줄에 `{"messages": [system, user, assistant]}`. system 프롬프트는 "주어진 문단만 근거로 1~2문장으로 답하고 끝에 [번호] 출처를 단다" |
| `valid.jsonl` | 100 | 위와 같은 형식, 검증용 |
