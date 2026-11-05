# 구글 드라이브 폴더 구조 (`MyDrive/rag_msmarco/`)

```
rag_msmarco/
├── v11_test/                 v1.1 (지금 기준)
│   ├── corpus.jsonl          문단 142,605
│   ├── eval.jsonl            평가 550 (건강 500 + 분야 밖 50)
│   ├── faiss_bge_flatip.index
│   ├── rerank/               03 결과 (val.jsonl, results_summary.md, 상위 20 문단 파일)
│   ├── rag/                  04 결과 (results_summary.md, eval_answers.jsonl, 챗봇 대화 기록)
│   └── lora/                 05 결과 (train_examples.jsonl, ckpt/, adapter/, results_summary.md)
└── health/                   v2.1
    ├── corpus.jsonl          문단 459,067
    ├── eval.jsonl            평가 650
    ├── train_health_qa.jsonl.gz   파인튜닝용 train 건강 질문
    └── rerank/               03 결과
```

`lora/`는 05를 실행하면 생깁니다. 파일 이름은 노트북 코드 기준이며 일부는 실제 드라이브와 다를 수 있습니다.
