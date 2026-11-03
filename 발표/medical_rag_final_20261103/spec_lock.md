<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: ppt169

## communication
- primary_language: ko-KR
- audience: 멋사 NLP 6기 수강생·멘토·강사 (RAG 기초는 알지만 이 프로젝트 실험은 처음 봄)
- objective: 최종 결과를 먼저 보고하고 평가 교체·검색 앙상블·생성 모델 교체·DPO의 판단 과정과 남은 한계를 설명해, 청중이 .770 / .804 성능과 LLM 심판·DPO의 근거를 납득하고 남은 병목이 검색임에 동의하게 한다
- core_message: 검색 앙상블 + Qwen3-8B + DPO로 정답률을 지키면서(.736 → .770) 지어낸 답을 35%에서 20%로 줄였고, 남은 오답의 주원인은 검색이다
- consumption_mode: presentation

## mode
- mode: showcase

## visual_style
- visual_style: soft-rounded

## colors
- background: #FFFFFF
- secondary_bg: #F2F5F7
- primary: #0B4F6C
- accent: #E4572E
- secondary_accent: #7B97AB
- body_text: #1C2630
- secondary_text: #5B6B78
- divider: #D5DEE4

## typography
- font_family: Malgun Gothic, Arial, sans-serif
- title_family: Malgun Gothic, Arial, sans-serif
- body_family: Malgun Gothic, Arial, sans-serif
- body: 32
- title: 56
- subtitle: 44
- annotation: 24
- cover_title: 88
- display: 128
- footnote: 18

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: search, database, filter, message-chatbot, brain, shield-check, scale, alert-triangle, x, check, language, clock, file-text, target, flask, chart-bar, route, player-play, gavel, books, arrows-sort, ban

## page_rhythm
- P01: anchor
- P02: anchor
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: anchor
- P08: dense
- P09: breathing
- P10: dense
- P11: breathing
- P12: dense
- P13: dense
- P14: breathing
- P15: dense
- P16: anchor

## page_visualizations
- P10: chart/horizontal_bar_chart
- P12: table/metric_table

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
