<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: ko-KR
- audience: 멋사 NLP 6기 강사·멘토와 동료 수강생 (RAG 기본 개념은 알지만 이 프로젝트 세부는 처음 봄)
- objective: 의료 RAG 챗봇의 최종 파이프라인을 검색·생성 단계로 설명하고 LLM 심판 지표로 각 개선(특히 DPO)을 증명해, 청중이 정답률 .618 → .770과 지어낸 답 35% → 20%를 믿을 만한 숫자로 납득하게 한다
- core_message: 믿을 수 있는 지표를 먼저 세웠기 때문에, 근거 안에서만 답하는 의료 챗봇을 정답률을 지키면서 더 안전하게(DPO) 만들 수 있었다
- consumption_mode: balanced

## mode
- mode: custom
- mode_references: instructional, pyramid
- mode_behavior: 파이프라인을 앞에서 뒤로 걸어가며 설명하는 교육형 흐름에 결론형 제목을 붙인다. 검색 단계(①1차 검색 ②재정렬 ③검색 거절)와 생성 단계(④생성 ⑤DPO)를 순서대로 다루고, 지표 파트는 심판을 먼저 정의한 뒤 신뢰성 근거를 보인다. 단계마다 무엇을 했나 → 어떤 지표로 쟀나 → 얼마나 좋아졌나를 같은 순서로 반복한다.

## visual_style
- visual_style: soft-rounded

## colors
- background: #FCFCFB
- secondary_bg: #EEF4FC
- primary: #12355B
- accent: #2A78D6
- secondary_accent: #EB6834
- body_text: #1F2328
- secondary_text: #52514E
- divider: #E2E1DC
- muted: #C3C2B7

## typography
- font_family: Pretendard, sans-serif
- title_family: Pretendard, sans-serif
- body_family: Pretendard, sans-serif
- body: 24
- title: 42
- subtitle: 32
- annotation: 18
- lead: 28
- cover_title: 64
- hero_number: 72
- footnote: 15

## icons
- library: tabler-filled
- inventory: tabler-filled/database, tabler-filled/search, tabler-filled/filter, tabler-filled/sort-descending-2, tabler-filled/shield-check, tabler-filled/message-chatbot, tabler-filled/scale, tabler-filled/chart-dots, tabler-filled/check, tabler-filled/x, tabler-filled/alert-triangle, tabler-filled/bulb, tabler-filled/file-text, tabler-filled/user, tabler-filled/flask, tabler-filled/gauge, tabler-filled/circle-check, tabler-filled/circle-x, tabler-filled/medical-cross, tabler-filled/list-check, tabler-filled/stack-2, tabler-filled/award, tabler-filled/thumb-down

## images
- p02: images/01_progress.png | source=user | crop=no-crop
- p06: images/02_retrieval.png | source=user | crop=no-crop
- p07: images/03_generator_ci.png | source=user | crop=no-crop
- p09: images/04_dpo.png | source=user | crop=no-crop
- p10: images/05_tradeoff.png | source=user | crop=no-crop
- p11: images/06_f1_vs_judge.png | source=user | crop=no-crop
- p13b: images/07_cross_judge.png | source=user | crop=no-crop
- p12: images/08_judge_flow.png | source=user | crop=no-crop
- p13a: images/09_judge_vs_human.png | source=user | crop=no-crop

## page_rhythm
- P01: anchor
- P02: dense
- P03: dense
- P04: anchor
- P05: dense
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: dense
- P11: dense
- P12: dense
- P13: dense
- P14: dense
- P15: anchor

## page_visualizations
- P05: table/metric_table
- P08: table/record_table
- P10: table/comparison_matrix
- P11: table/record_table
- P14: table/record_table

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
