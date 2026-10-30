-- 컨테이너를 처음 만들 때(볼륨이 비어 있을 때) 한 번만 실행됨
CREATE EXTENSION IF NOT EXISTS vector;

-- corpus.jsonl 한 줄 = 한 행. embedding은 corpus_emb_bge.npy의 같은 줄 번호(= pid)
CREATE TABLE IF NOT EXISTS passages (
    pid       int PRIMARY KEY,
    text      text NOT NULL,
    url       text,
    src       text,              -- dev_health / train_health / dev_other
    embedding halfvec(768) NOT NULL   -- bge-base-en-v1.5, 정규화됨. npy가 fp16이라 halfvec
);
-- 인덱스 없음: 14만 개는 전체 비교(FAISS IndexFlatIP와 같은 정확 검색)로 충분
-- ponytail: 문단이 수백만 개(v2.1)가 되면 CREATE INDEX ON passages USING hnsw (embedding halfvec_ip_ops);
