# 08 틀린 사례 분석 (v2.1, RAG 개선 + 문장형 LoRA)

2026-11-02 · 08 `eval_answers.jsonl` (답 있는 건강 500) · '성공' = F1 ≥ 0.4

## 질의 유형별 (MS MARCO query_type)

| 유형 | n | 근거 R@5 | F1 | 성공 | 답 틀림 | 거절 |
|---|---|---|---|---|---|---|
| DESCRIPTION | 314 | 0.63 | 0.360 | 0.34 | 0.53 | 0.13 |
| ENTITY | 87 | 0.61 | 0.310 | 0.32 | 0.61 | 0.07 |
| NUMERIC | 86 | 0.63 | 0.339 | 0.36 | 0.59 | 0.05 |
| LOCATION | 7 | 0.71 | 0.372 | 0.43 | 0.43 | 0.14 |
| PERSON | 6 | 0.67 | 0.456 | 0.50 | 0.50 | 0.00 |

→ 유형별 차이는 작음.

## 질문-정답 문단 키워드 겹침 구간별 (09와 같은 기준: 하 ≤ 0.5 < 중 < 1.0 = 상)

| 구간 | n | 근거 R@5 | F1 | 성공 | 답 틀림 | 거절 |
|---|---|---|---|---|---|---|
| 하 | 165 | **0.46** | 0.276 | 0.25 | 0.61 | 0.13 |
| 중 | 187 | 0.64 | 0.342 | 0.33 | 0.57 | 0.10 |
| 상 | 148 | 0.80 | 0.439 | 0.46 | 0.47 | 0.07 |

→ 겹침이 낮을수록 검색이 크게 떨어짐 (0.80 → 0.46). 쿼리 재작성/HyDE(09)의 목표 구간.

## 검색 × 생성 (n)

| | 성공 | 답 틀림 | 거절 |
|---|---|---|---|
| 정답 문단 있음 (314) | 139 | 154 | 21 |
| 정답 문단 없음 (186) | 33 | 123 | 30 |

## '정답 문단 있음 + 답 틀림' 154개 중 40개 직접 판정

- 정답(뜻은 맞음) 24 / 부분(일부만·불완전) 9 / 오답 7
- F1이 낮은 이유 대부분은 **표현 차이** (예: 정답 '7 to 10 days' vs 답 'It takes 7 to 10 days ...') 또는 **정답 라벨 오류** (eustachian 정답이 밴드 이름, 'Yes'만 있는 정답)
- 진짜 문제: 목록형 질문에서 하나만 답함 (원인·부작용·효능), 문서 중 엉뚱한 것을 고름
- 추정: 154개 중 약 60%가 실제로 맞음 → 정답 문단 있을 때 실제 성공률 약 44% → 약 74%
- 결론: F1은 답변 품질을 과소평가 → 멘토 조언대로 LLM-as-a-Judge로 보완 필요. 생성 쪽 수정은 '목록은 빠짐없이' 프롬프트.

| # | 판정 | 질문 | 정답 | 답변 |
|---|---|---|---|---|
| 0 | 정답 | what to eat before a workout for energy | A fresh fruit snack,carbohydrates. | Eat carbohydrates before a workout for energy [2]. |
| 1 | 부분 | causes of fingernail ridges & concave shape | It may be due to aging and iron deficiency. | Depression lines in fingernails, also known as beau lines, occur due to malnutrition or an injury to your nail [4]. |
| 2 | 정답 | when you feel tired all the time | It is when being a “carboholic”. | When you feel tired all the time, you are a carboholic, meaning someone who overeats grains, refined carbs and sugary foods [1]. |
| 3 | 부분 | iron foods benefits of function | It requires to perform daily activities and It helps to transport oxygen around the body. | Iron foods benefits of function is to help to maintain healthy cells, skin, hair and nails [2]. |
| 4 | 오답 | what is yoga flow class | A yoga in which is synchronized to the breath. | Yoga flow class is a term that covers a broad range of yoga classes [2]. |
| 5 | 오답 | which of the following is an effect of luteinizing hormone (lh) after ovulation? | The cells in the ovarian follicle become corpus luteum. | The effect of luteinizing hormone after ovulation is the release of eggs from the ovary [3]. |
| 6 | 정답 | lymes disease symptoms dogs | 1 A fever running between 103 and 105 degrees. 2 Lameness. Swelling in the joints, which appears suddenly 3 limping and intermittent, wander | The symptoms of Lyme disease in dogs are fever, lameness, swelling in the joints, which appears suddenly [1]. |
| 7 | 정답 | treatment of lymphadenitis | Treatment of lymphadenitis includes IV antibiotics, antifungals, and antiparasitics depending upon etiology or clinical suspicion. | Treatment of lymphadenitis is antibiotics, and medications to control pain and fever [2]. |
| 8 | 부분 | what would cause pain in the upper back | Improper lifting, bending, twisting motion, muscle strengthen, Bad posture, excessive weight and smoking. | Poor posture would cause pain in the upper back [2]. |
| 9 | 오답 | when does baby's eye color change | A child’s eyes might darken or change color during the first 3-6 months of his life. | Baby's eye color changes between 6 to 9 months of life [1]. |
| 10 | 오답 | what causes h-pylori stomach infection | Helicobacter pylori may be spread by consuming unclean food and water in which the bacteria thrive. | Helicobacter pylori is a bacteria that causes stomach infections leading to gastritis and ulcers [1]. |
| 11 | 정답 | what is the normal serum calcium' | 8.5-10.2 mg/dL | The normal serum calcium is 8.5 to 10.5 milligrams per deciliter [3]. |
| 12 | 부분 | what are examples of biofeedback | Picks up electrical signals in the muscles. | Biofeedback is a method that uses the mind to control a body function that the body normally regulates automatically, such as skin temperatu |
| 13 | 부분 | what is the minimum healthy calorie intake | Women eat at least 1,200 calories daily and men get a minimum of 1,500 calories a day. | The minimum healthy calorie intake is 1,200 calories per day [1]. |
| 14 | 정답 | what is vitamin b3 good for | To boost your HDL cholesterol – your good cholesterol. | Vitamin B3 is good for maintaining good blood circulation, healthy robust skin condition, help in normal functioning of the brain, boosting  |
| 15 | 오답 | how much minerals do you need each day | Men should have 8 milligrams of iron per day, but women need 18 milligrams of the mineral. | You need 1,000 milligrams of minerals each day [2]. |
| 16 | 정답 | how long does the stomach flu last in adults | Anywhere from 24 hours to 10 days. | The stomach flu lasts for 1 to 3 days in adults [5]. |
| 17 | 부분 | causes of aaa | 1 Infection. 2 Trauma. 3 Arteritis. 4 Cystic medial necrosis. 5 Connective tissuedisorders. 6 Marfan's syndrome. 7 Ehlers-Danlos syndrome. 8 | The cause of an AAA, or abdominal aortic aneurysm is unknown, but the most significant risk factor is smoking [1]. |
| 18 | 정답 | muscle relaxer tizanidine | A drug that is used as a muscle relaxant and a centrally acting α2 adrenergic agonist. | Tizanidine is a short acting muscle relaxer that's marketed under the brand name Zanaflex [1]. |
| 19 | 정답 | which pair of chromosomes would result in the birth of a male | Males have one Y chromosome and one X chromosome. | The pair of chromosomes XY would result in the birth of a male [1]. |
| 20 | 정답 | another name for doxycycline | Vibramycin, Oracea, Adoxa, Atridox, Acticlate, Acticlate Cap, Doryx, Doxteric, Doxy and Monodox. | Vibramycin is another name for doxycycline [1]. |
| 21 | 정답 | define gluteus | Any of the three muscles that form each of the buttocks and act to extend, abduct and rotate the thigh. | Gluteus is a large muscle with an origin in the ilium, the sacrum, and the sacrotuberous ligament and an insertion in the gluteal tuberosity |
| 22 | 정답 | what is a phobia of life | A phobia is defined as the persistent fear of a situation, activity, or thing that causes the sufferer to want to avoid it. | A phobia of life is an irrational fear, a kind of anxiety disorder in which the sufferer has a relentless dread of a situation, living creat |
| 23 | 정답 | pericardial fluid definition | An abnormal accumulation of fluid in the pericardial cavity. | Pericardial fluid is the serous fluid secreted by the serous layer of the pericardium into the pericardial cavity [1]. |
| 24 | 정답 | surfactant is a phospholipid that reduces quizlet | Yes | Surfactant is a phospholipid that reduces surface tension throughout the lung [1]. |
| 25 | 정답 | how long is recovery time from gallbladder surgery | The gallbladder removal surgery, or open cholecystectomy takes four to six weeks and the less invasive laparoscopic gallbladder surgery take | The recovery time from gallbladder surgery is four to six weeks [5]. |
| 26 | 부분 | saw palmetto berry benefits | The benefits of saw palmetto berry are that it tones the urethra and it may be used to uphold the healthy function of the thyroid gland and  | Saw palmetto berry benefits are urinary tract problems and increase sperm production [2]. |
| 27 | 오답 | diabetic service dogs cost | $8,000 to $20,000 | The cost of diabetic service dogs is $35,000 [1]. |
| 28 | 부분 | who sings fever | Little Willie John | Peggy Lee sings Fever [4]. |
| 29 | 정답 | pectoralis major definition | The pectoralis major muscle is a large muscle in the upper chest, fanning across the chest from the shoulder to the breastbone. | The pectoralis major is a thick, fan-shaped muscle, situated at the chest of the human body [3]. |
| 30 | 정답 | what exactly are pimples | A pimple is a small pustule or papule. It develop when sebaceous glands, or oil glands, become clogged and infected, leading to swollen, red | Pimples are small skin inflammations or lesions [5]. |
| 31 | 정답 | what is an emg test for nerve damage? | An electromyogram is a test that detects abnormal muscle electrical activity in conditions such as neuropathy, carpal tunnel syndrome, pinch | An electromyography, or EMG, test can detect various neuromuscular diseases, motor issues, nerve damage and degenerative conditions such as  |
| 32 | 정답 | side effects of mirapex er | Drowsiness, nausea, dizziness, headache, or dry mouth, stomach pain, vomiting, constipation, dizziness, spinning sensation; mild drowsiness, | The side effects of Mirapex ER are nausea, dizziness, sleepiness, constipation, hallucinations, insomnia, muscle weakness, confusion, and ab |
| 33 | 정답 | what is an example of ppe | Spectacles, goggles are the examples of PPE. | Respiratory protection is an example of personal protective equipment [1]. |
| 34 | 정답 | range for normal body temperature in general | 97.8 degrees F or 36.5 degrees C | The range for normal body temperature in general is 97°F to 99°F [2]. |
| 35 | 오답 | what does having hiccups mean | A hiccup is an automatic action that the body can't control. During a hiccup your diaphragm contracts. Immediately after this the top of you | Having hiccups means there are bubbles of air inside your stomach trying to get out [5]. |
| 36 | 정답 | what is a father's role in a child's life | To helping out in physical, emotional, social and spiritual needs, the sharing of time, activities, conversation and self, means a constant  | A father's role in a child's life is to be a central to the emotional well-being of their children; they are are capable caretakers and disc |
| 37 | 정답 | what does eustachian mean | Eustachian is a San Francisco based Neo colonial digital power violence / breakcore duo. | Eustachian means a tube leading from the middle ear to the pharynx, or to the rudimentary valve at the entrance of the inferior vena cava in |
| 38 | 부분 | what is the palpebral in the eye? | It refers to the area where the lower and upper eyelids meet. | The palpebral is the membrane that forms the underside of the eyelid [1]. |
| 39 | 정답 | what is the primary purpose of a medical record | To foster quality and continuity of care. | The primary purpose of a medical record is to provide a list of the patients medical history and treatment [1]. |
