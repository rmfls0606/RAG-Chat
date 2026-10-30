"""corpus.jsonl + corpus_emb_bge.npy → pgvector passages 테이블.

    python load.py [DATA_DIR]      # 기본: 저장소/data/v11_test (Drive의 rag_msmarco/v11_test를 받아 둔 곳)

여러 번 실행해도 됩니다 (테이블을 비우고 다시 넣음).
"""
import json, os, sys, time
from pathlib import Path

import numpy as np
import psycopg
from pgvector.psycopg import HalfVector, register_vector

DSN = os.environ.get('PG_DSN', 'postgresql://rag:rag@127.0.0.1:5432/rag')
DATA_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'data' / 'v11_test')


def main():
    with open(DATA_DIR / 'corpus.jsonl', encoding='utf-8') as f:
        corpus = [json.loads(line) for line in f]
    emb = np.load(DATA_DIR / 'corpus_emb_bge.npy', mmap_mode='r')
    # pid = 줄 번호 = 임베딩 행 번호. 이게 어긋나면 검색 결과가 전부 틀림
    assert len(emb) == len(corpus), f'임베딩 {len(emb)}개 ≠ 문단 {len(corpus)}개 (T2를 다시 돌리세요)'
    assert all(c['pid'] == i for i, c in enumerate(corpus)), 'pid가 줄 번호와 다름'

    t = time.time()
    with psycopg.connect(DSN) as conn:
        register_vector(conn)
        conn.execute('TRUNCATE passages')
        with conn.cursor().copy('COPY passages (pid, text, url, src, embedding) FROM STDIN WITH (FORMAT BINARY)') as copy:
            copy.set_types(['int4', 'text', 'text', 'text', 'halfvec'])
            for c, v in zip(corpus, emb):
                copy.write_row((c['pid'], c['text'], c['url'], c['src'], HalfVector(v)))
        conn.commit()

        n = conn.execute('SELECT count(*) FROM passages').fetchone()[0]
        assert n == len(corpus), f'DB {n}개 ≠ 문단 {len(corpus)}개'
        # 확인: 문단 자기 벡터로 검색하면 1위가 자기 자신이어야 함
        for pid in (0, len(corpus) // 2, len(corpus) - 1):
            top = conn.execute('SELECT pid FROM passages ORDER BY embedding <#> %s LIMIT 1',
                               (HalfVector(emb[pid]),)).fetchone()[0]
            assert top == pid, f'pid {pid}로 검색했는데 1위가 {top}'
    print(f'적재 완료: {n:,}개, {time.time() - t:.0f}초 → 검사 통과')


if __name__ == '__main__':
    main()
