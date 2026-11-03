# 15 SFT v2 (v2.1) (2026-11-02 21:10 KST)

- 학습 데이터: 원본 Qwen 답 3개/질문 → 14B 심판으로 선택. 학습 예시 1994 = 답변 1835 + 거절 159
- 거절 라벨은 심판 P(문단에 답 있음) < 0.2일 때만. 06에서 거절로 학습했던 경우(정답 문단 top5 밖) 714개 → {'answer': 500, 'drop': 151, 'refuse': 63}
- LoRA r16, lr 0.0001, 1 epoch. 어댑터 `health/sft_v2/adapter`
- 시험 정답률 차이 (SFT v2 - 원본): -0.012 (95% CI -0.034 ~ +0.010)

## 라벨 분포 (A=답 있음, N=MS MARCO 답 없음)

| group   |   answer |   answer_noref |   drop |   refuse |   All |
|:--------|---------:|---------------:|-------:|---------:|------:|
| A       |     1574 |              0 |    304 |      122 |  2000 |
| N       |        0 |            261 |     44 |      160 |   465 |
| All     |     1574 |            261 |    348 |      282 |  2465 |

## 시험 650 (08 문단)

|                 |   정답률 (심판 2점) |   정답+부분 (심판 ≥ 1점) |   평균 점수 (0~2) |   F1 (참고) |   근거 충실도 |   잘못 거절 |   답 없음 거절률 |   분야 밖 거절률 |
|:----------------|--------------------:|-------------------------:|------------------:|------------:|--------------:|------------:|-----------------:|-----------------:|
| RAG 개선        |               0.736 |                    0.89  |             1.617 |       0.282 |         0.87  |       0.056 |             0.44 |             0.82 |
| RAG 개선 + LoRA |               0.45  |                    0.744 |             1.183 |       0.349 |         0.794 |       0.102 |             0.54 |             0.82 |
| SFT v2          |               0.724 |                    0.874 |             1.596 |       0.276 |         0.896 |       0.072 |             0.46 |             0.82 |

## 검증 300

|                 |   정답률 (심판 2점) |   정답+부분 (심판 ≥ 1점) |   평균 점수 (0~2) |   F1 (참고) |   근거 충실도 |   잘못 거절 |   답 없음 거절률 |   분야 밖 거절률 |
|:----------------|--------------------:|-------------------------:|------------------:|------------:|--------------:|------------:|-----------------:|-----------------:|
| RAG 개선        |               0.69  |                    0.89  |             1.584 |       0.283 |         0.866 |       0.05  |             0.43 |              nan |
| RAG 개선 + LoRA |               0.415 |                    0.685 |             1.092 |       0.328 |         0.808 |       0.155 |             0.55 |              nan |
| SFT v2          |               0.695 |                    0.875 |             1.566 |       0.277 |         0.862 |       0.065 |             0.47 |              nan |

## 데모

- **why does my face turn red and itchy after drinking alcohol**
  - 원본: Your face turning red and itchy after drinking alcohol could be due to alcohol intolerance, which is often caused by a genetic condition where the body cannot break down alcohol efficiently [4][5]. This can lead to immediate unpleasant reactions including skin flushing [4].
  - SFT v2: Your face turning red and itchy after drinking alcohol could be due to alcohol intolerance, which is often caused by a genetic condition where the body struggles to break down alcohol efficiently [4][5]. This can lead to immediate unpleasant reactions including skin flushing [4].
- **what are the symptoms of low vitamin d**
  - 원본: Some symptoms of low vitamin D include difficulty thinking clearly, bone pain, frequent bone fractures, muscle weakness, soft bones that may result in deformities, and unexplained fatigue [1][2]. Additionally, muscle weakness, joint aches and discomfort, high blood pressure, inability to concentrate or focus, urinary incontinence, bladder issues, constipation, headaches, colds or flu, and mood disorders are also specific symptoms of vitamin D deficiency [3][4].
  - SFT v2: Symptoms of low vitamin D may include difficulty thinking clearly, bone pain, frequent bone fractures, muscle weakness, soft bones that may result in deformities, and unexplained fatigue [1][2]. Additionally, specific symptoms can include muscle weakness, joint aches and discomfort, high blood pressure, inability to concentrate or focus, urinary incontinence or bladder issues, constipation, headaches, colds or flu, and mood disorders [3][4].
- **can ibuprofen cause stomach bleeding**
  - 원본: Yes, ibuprofen can cause stomach bleeding [1][4][5].
  - SFT v2: Yes, ibuprofen can cause stomach bleeding [1][4][5].
- **how long does the flu last**
  - 원본: Most individuals experience the main flu symptoms for about 3 to 10 days, with a full recovery taking around one to two weeks [1][2][3][4][5].
  - SFT v2: Most individuals experience the main flu symptoms for about 3-10 days, with the entire infection lasting around one to two weeks [1][2][3][4][5].
- **what is a normal resting heart rate for adults**
  - 원본: A normal resting heart rate for adults ranges from 60 to 100 beats per minute. [1][2][3][4][5]
  - SFT v2: A normal resting heart rate for adults ranges from 60 to 100 beats per minute. [1][2][3][4][5]