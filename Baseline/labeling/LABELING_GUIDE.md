# 질문 의료 관련성 라벨링 가이드 (검수용)

`review_sample.csv`에 있는 질문 200개에 A/B/C/U 라벨을 다는 작업입니다.
LLM 분류기(`QueryClassification.ipynb`)가 낸 라벨이 얼마나 정확한지 확인하는 **기준 라벨**로 쓰입니다.
기준은 `baseline.ipynb`의 "의료 데이터 범위 설정"과 같고, LLM 분류기 프롬프트도 같은 기준을 씁니다.

## 작업 방법

1. `review_sample.csv`를 열어 행마다 `query`와 `passage`를 읽습니다.
2. 아래 기준에 따라 `label`, `high_risk`, `time_sensitive`를 채웁니다. 판단이 애매했던 행은 `note`에 이유를 짧게 적습니다.
3. 결과를 같은 폴더에 `review_sample_labeled.csv`로 저장합니다. 원본 `review_sample.csv`는 수정하지 않습니다.
   - 열 이름과 순서, `review_id`, `query_id`, `query`, `passage`는 바꾸지 않습니다.
   - 인코딩은 UTF-8, 행 수는 200개 그대로 유지합니다.
4. **LLM 분류 결과를 보지 않고** 독립적으로 판단합니다. 결과를 참고하면 검증의 의미가 없어집니다.

## 채울 열

| 열 | 값 | 설명 |
|---|---|---|
| `label` | `A` / `B` / `C` / `U` | 한 글자 대문자 |
| `high_risk` | `true` / `false` | 개인 의료 판단(약 중단이나 변경, 본인 복용량 결정 등)을 요구하는 질문 |
| `time_sensitive` | `true` / `false` | 답이 바뀔 수 있는 가이드라인(치료 권고, 약물 용량, 백신 일정)에 의존하는 질문 |
| `note` | 자유 기술 | 애매한 경우의 판단 근거 (선택) |

`high_risk`와 `time_sensitive`는 A나 B일 때만 `true`가 될 수 있습니다. C와 U는 항상 `false`입니다.

## 라벨 정의

| 라벨 | 정의 | 예시 |
|---|---|---|
| **A** 핵심 의료 | 사람의 질병, 증상, 진단, 의학 검사, 약물, 치료와 시술, 해부와 생리, 예방과 감염, 정신질환에 대한 의학 지식이 필요한 질문 | what causes pneumonia / side effects of metformin / what does the pancreas do / symptoms of depression |
| **B** 의료 인접 | 영양, 식단, 운동, 건강 습관, 일반 웰니스, 식품 안전, 건강보험, 의료비, 병원 운영, 동물과 수의학 건강 | how much water should a person drink daily / how much does an MRI cost / what age do you give puppies parvo shots |
| **C** 비의료 | 의료 지식이 목적이 아닌 질문. 의료 단어가 들어 있어도 해당 | who invented the MRI machine / where was this doctor born / 의료직 연봉이나 직업 / 단어의 비의료적 의미 |
| **U** 불확실 | passage를 읽어도 의미를 정할 수 없을 만큼 모호한 질문 | 약어 하나만 있고 passage도 판단에 도움이 안 되는 경우 |

## 판단 규칙

1. **키워드가 아니라 질문의 목적**으로 판단합니다.
   - "what causes your hands to shake": 의료 용어는 없지만 증상의 원인을 묻습니다 → **A**
   - "who invented the MRI machine": 의료 용어가 있지만 역사를 묻습니다 → **C**
2. **여러 뜻을 가진 단어**는 passage로 판단합니다.
   - "what is a stroke"에 뇌졸중 passage가 붙었으면 **A**, 수영 영법 passage면 **C**, passage로도 정할 수 없으면 **U**
3. 일반 건강 상식과 임상 지식을 구분합니다.
   - "how much water should a person drink daily" → **B**
   - "what are the signs of severe dehydration" → **A**
4. **passage에 정답이 있는지는 라벨에 영향을 주지 않습니다.** 질문 자체의 성격만 봅니다.
5. 플래그 예시:
   - "should I stop taking my blood pressure medication" → **A**, `high_risk=true`
   - "what is the recommended treatment for hepatitis C" → **A**, `time_sensitive=true`
