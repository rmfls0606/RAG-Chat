"""pgvector 검색 결과가 T2(FAISS)와 같은지 확인합니다.

    python check_dense.py [DATA_DIR]

eval.jsonl의 건강 질문 500개로 Recall/MRR을 재고, T2가 저장한 retrieval_results.json의 bge-base 값과 비교합니다.
"""
import json, os, sys, time
from pathlib import Path

import psycopg
from pgvector.psycopg import HalfVector, register_vector
from sentence_transformers import SentenceTransformer

DSN = os.environ.get('PG_DSN', 'postgresql://rag:rag@127.0.0.1:5432/rag')
DATA_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'data' / 'v11_test')
EMB_MODEL = 'BAAI/bge-base-en-v1.5'
QUERY_PREFIX = 'Represent this sentence for searching relevant passages: '


def retrieval_metrics(ranked, qs, ks=(1, 5, 10, 100)):   # T2와 같은 함수
    res = {f'Recall@{k}': 0.0 for k in ks}
    res['MRR@10'] = 0.0
    for pids, q in zip(ranked, qs):
        gold = set(q['gold_pids'])
        for k in ks:
            res[f'Recall@{k}'] += bool(gold & set(pids[:k]))
        for r, p in enumerate(pids[:10]):
            if p in gold:
                res['MRR@10'] += 1 / (r + 1)
                break
    return {k: round(v / len(qs), 4) for k, v in res.items()}


def main():
    with open(DATA_DIR / 'eval.jsonl', encoding='utf-8') as f:
        eval_ans = [q for q in map(json.loads, f) if q['answerable']]

    model = SentenceTransformer(EMB_MODEL)
    model.max_seq_length = 256
    q_emb = model.encode([QUERY_PREFIX + q['query'] for q in eval_ans], batch_size=64,
                         normalize_embeddings=True, show_progress_bar=True).astype('float16')

    t = time.time()
    with psycopg.connect(DSN) as conn:
        register_vector(conn)
        ranked = [[r[0] for r in conn.execute('SELECT pid FROM passages ORDER BY embedding <#> %s LIMIT 100',
                                              (HalfVector(v),))]
                  for v in q_emb]
    ms = (time.time() - t) / len(eval_ans) * 1000
    scores = retrieval_metrics(ranked, eval_ans)
    print(f'pgvector ({len(eval_ans)}문항, 질문당 {ms:.0f}ms):', scores)

    ref_path = DATA_DIR / 'retrieval_results.json'
    if ref_path.exists():
        ref = json.load(open(ref_path))['bge-base']
        print('T2 FAISS                    :', ref)
        # T2는 GPU fp16으로 질문을 임베딩해서 소수점 끝자리가 조금 다를 수 있음
        diff = max(abs(scores[k] - ref[k]) for k in ref)
        print('최대 차이', round(diff, 4), '→', '일치' if diff <= 0.01 else '⛔ 차이가 큼: pid와 벡터 짝을 확인하세요')


if __name__ == '__main__':
    main()
