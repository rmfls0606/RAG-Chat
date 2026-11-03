# 16 검색 × 생성 모델 비교 (v2.1) (2026-11-03 01:16 KST)

- S0 = MiniLM 상위 5 (08), E5/E10 = 앙상블(bge-reranker-large + v2-m3) 상위 5/10. 거절은 08과 같음 (MiniLM 최고점 < 4.92)
- 심판: Qwen/Qwen2.5-14B-Instruct (14와 같음), 교차 심판 microsoft/phi-4. 고르기는 검증 200, 시험 650은 보고용
- **고른 검색: E10 / 검증 기준 최고 조합: E10|Qwen3-8B** / Phi-4 검증 순위 일치: True

## ① 검색 비교 (생성 7B)

검증

|        |   정답률 (심판 2점) |   정답+부분 |   평균 점수 (0~2) |   F1 (참고) |   잘못 거절 |   근거 충실도 |
|:-------|--------------------:|------------:|------------------:|------------:|------------:|--------------:|
| S0|7B  |               0.69  |       0.89  |             1.584 |       0.283 |       0.05  |         0.874 |
| E5|7B  |               0.71  |       0.89  |             1.601 |       0.283 |       0.065 |         0.856 |
| E10|7B |               0.725 |       0.915 |             1.638 |       0.278 |       0.055 |         0.91  |

시험

|        |   정답률 (심판 2점) |   정답+부분 |   평균 점수 (0~2) |   F1 (참고) |   잘못 거절 |   근거 충실도 |   답 없음 거절률 (MS MARCO 기준) |   분야 밖 거절률 |
|:-------|--------------------:|------------:|------------------:|------------:|------------:|--------------:|---------------------------------:|-----------------:|
| S0|7B  |               0.736 |       0.89  |             1.617 |       0.282 |       0.056 |         0.87  |                             0.44 |             0.82 |
| E5|7B  |               0.762 |       0.896 |             1.647 |       0.295 |       0.054 |         0.876 |                             0.43 |             0.82 |
| E10|7B |               0.74  |       0.896 |             1.636 |       0.283 |       0.05  |         0.899 |                             0.41 |             0.82 |

## ② 생성 모델 비교

검증

|                 |   정답률 (심판 2점) |   정답+부분 |   평균 점수 (0~2) |   F1 (참고) |   잘못 거절 |   근거 충실도 |
|:----------------|--------------------:|------------:|------------------:|------------:|------------:|--------------:|
| S0|7B           |               0.69  |       0.89  |             1.584 |       0.283 |       0.05  |         0.874 |
| E10|7B          |               0.725 |       0.915 |             1.638 |       0.278 |       0.055 |         0.91  |
| E10|Qwen2.5-14B |               0.735 |       0.9   |             1.645 |       0.273 |       0.055 |         0.963 |
| E10|Qwen3-8B    |               0.795 |       0.925 |             1.711 |       0.267 |       0.045 |         0.859 |
| E10|Qwen3-14B   |               0.795 |       0.91  |             1.694 |       0.241 |       0.06  |         0.91  |

시험

|                 |   정답률 (심판 2점) |   정답+부분 |   평균 점수 (0~2) |   F1 (참고) |   잘못 거절 |   근거 충실도 |   답 없음 거절률 (MS MARCO 기준) |   분야 밖 거절률 |
|:----------------|--------------------:|------------:|------------------:|------------:|------------:|--------------:|---------------------------------:|-----------------:|
| S0|7B           |               0.736 |       0.89  |             1.617 |       0.282 |       0.056 |         0.87  |                             0.44 |             0.82 |
| E10|7B          |               0.74  |       0.896 |             1.636 |       0.283 |       0.05  |         0.899 |                             0.41 |             0.82 |
| E10|Qwen2.5-14B |               0.76  |       0.91  |             1.664 |       0.281 |       0.054 |         0.926 |                             0.42 |             0.82 |
| E10|Qwen3-8B    |               0.782 |       0.904 |             1.687 |       0.268 |       0.046 |         0.919 |                             0.4  |             0.82 |
| E10|Qwen3-14B   |               0.79  |       0.902 |             1.687 |       0.241 |       0.066 |         0.925 |                             0.43 |             0.84 |

시험 정답률 차이 (vs 08 S0|7B, 95% 부트스트랩)

|                 |   차이 |   95% CI 하한 |   95% CI 상한 |
|:----------------|-------:|--------------:|--------------:|
| E10|7B          |  0.004 |        -0.032 |         0.042 |
| E10|Qwen2.5-14B |  0.024 |        -0.012 |         0.06  |
| E10|Qwen3-8B    |  0.046 |         0.008 |         0.082 |
| E10|Qwen3-14B   |  0.054 |         0.018 |         0.088 |

## ③ 교차 심판 (정답률)

|                 |   Qwen 심판 검증 |   Phi-4 심판 검증 |   Qwen 심판 시험 |   Phi-4 심판 시험 |
|:----------------|-----------------:|------------------:|-----------------:|------------------:|
| S0|7B           |            0.69  |             0.765 |            0.736 |             0.774 |
| E10|7B          |            0.725 |             0.785 |            0.74  |             0.78  |
| E10|Qwen2.5-14B |            0.735 |             0.825 |            0.76  |             0.798 |
| E10|Qwen3-8B    |            0.795 |             0.84  |            0.782 |             0.802 |
| E10|Qwen3-14B   |            0.795 |             0.84  |            0.79  |             0.794 |

## ④ 시험 답 없음 100: 심판 기준 거절

|                 |   진짜 답 없음 (개) |   → 거절률 |   사실 답 있음 (개) |   → 답변률 |   → 근거 충실도 |
|:----------------|--------------------:|-----------:|--------------------:|-----------:|----------------:|
| S0|7B           |                  50 |      0.72  |                  48 |      0.854 |           0.78  |
| E10|7B          |                  46 |      0.674 |                  53 |      0.83  |           0.818 |
| E10|Qwen2.5-14B |                  46 |      0.696 |                  53 |      0.83  |           0.886 |
| E10|Qwen3-8B    |                  46 |      0.652 |                  53 |      0.83  |           0.909 |
| E10|Qwen3-14B   |                  46 |      0.717 |                  53 |      0.83  |           0.886 |

## 데모

- **why does my face turn red and itchy after drinking alcohol**
  - 08 (S0|7B): Your face turning red and itchy after drinking alcohol could be due to alcohol intolerance, which is often caused by a genetic condition where the body cannot break down alcohol efficiently [4][5]. This can lead to immediate unpleasant reactions including skin flushing [4].
  - E10|Qwen3-8B: Your face may turn red and itchy after drinking alcohol due to facial flushing, which occurs when alcohol causes blood vessels to expand, leading to increased blood flow to the face [6]. This reaction can also be triggered by sensitivity to ingredients in alcohol, leading to skin flushing and itching [9]. Additionally, alcohol can exacerbate conditions like hives, which are characterized by itchy, red welts on the skin [5].
- **what are the symptoms of low vitamin d**
  - 08 (S0|7B): Some symptoms of low vitamin D include difficulty thinking clearly, bone pain, frequent bone fractures, muscle weakness, soft bones that may result in deformities, and unexplained fatigue [1][2]. Additionally, muscle weakness, joint aches and discomfort, high blood pressure, inability to concentrate or focus, urinary incontinence, bladder issues, constipation, headaches, colds or flu, and mood disorders are also specific symptoms of vitamin D deficiency [3][4].
  - E10|Qwen3-8B: Symptoms of low vitamin D include muscle weakness, joint aches, high blood pressure, inability to concentrate, urinary incontinence, constipation, headaches, and mood disorders [1]. It can also lead to fatigue, bone pain, and a weakened immune system [3][4]. Some people may not experience any symptoms at all [5].
- **can ibuprofen cause stomach bleeding**
  - 08 (S0|7B): Yes, ibuprofen can cause stomach bleeding [1][4][5].
  - E10|Qwen3-8B: Yes, ibuprofen can cause stomach bleeding. This is because it decreases the number of protective prostaglandins in the stomach [2]. The risk of stomach bleeding from ibuprofen increases with long-term use, being elderly, or having a history of stomach ulcers [3].
- **how long does the flu last**
  - 08 (S0|7B): Most individuals experience the main flu symptoms for about 3 to 10 days, with a full recovery taking around one to two weeks [1][2][3][4][5].
  - E10|Qwen3-8B: The flu typically lasts from three days to two weeks [1][4][6]. For most healthy individuals, symptoms last about one to two weeks, with the main symptoms subsiding in about one week [2][3][7].
- **what is a normal resting heart rate for adults**
  - 08 (S0|7B): A normal resting heart rate for adults ranges from 60 to 100 beats per minute. [1][2][3][4][5]
  - E10|Qwen3-8B: A normal resting heart rate for adults ranges from 60 to 100 beats a minute [1][2][3][4][5][6][7][8][10]. A well-trained athlete might have a normal resting heart rate closer to 40 beats a minute [1][2][3][4][5][6][7][8][10].