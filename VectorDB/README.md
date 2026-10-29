# VectorDB (pgvector)

각자 내 컴퓨터에서 Docker로 같은 DB를 띄웁니다. 데이터는 모두 Drive의 같은 파일에서 넣으므로 누가 넣어도 내용이 같습니다.

```
Preprocess/T1 (Colab) → corpus.jsonl, eval.jsonl ─┐
Embedding/T2  (Colab) → corpus_emb_bge.npy ───────┴→ Drive → load.py → passages 테이블
```

## Docker가 뭔가요?

DB 프로그램(PostgreSQL + pgvector)을 내 컴퓨터에 직접 설치하지 않고, 미리 만들어진 상자(컨테이너)째로 받아서 실행하는 도구입니다. 설정은 [docker-compose.yml](docker-compose.yml)에 이미 다 적혀 있으므로, 아래 명령만 그대로 따라 치면 모두 같은 DB가 뜹니다. 데이터는 컨테이너를 꺼도 남습니다.

## 처음 한 번

### 1. Docker Desktop 설치

1. https://www.docker.com/products/docker-desktop/ 에서 내 OS용을 받아 설치합니다 (Mac은 Apple 칩/Intel 칩 구분).
2. **Docker Desktop 앱을 실행**합니다. 상단 메뉴바(Windows는 작업 표시줄)에 고래 아이콘이 뜨고 "Engine running"이 되면 준비 끝입니다. 로그인은 안 해도 됩니다(Skip).
3. 터미널에서 확인:
   ```bash
   docker --version
   docker compose version
   ```

> 앞으로도 DB를 쓰려면 **Docker Desktop 앱이 켜져 있어야** 합니다. 꺼져 있으면 `Cannot connect to the Docker daemon` 오류가 납니다.

### 2. 데이터 파일 받기

Drive의 `rag_msmarco/v11_test/`에서 아래 4개를 받아 저장소의 `data/v11_test/`에 넣습니다 (`data/`는 git에 안 올라감).

`corpus.jsonl`, `eval.jsonl`, `corpus_emb_bge.npy`, `retrieval_results.json`

```
RAG-Chat/
├── data/v11_test/   ← 여기에 4개
└── VectorDB/        ← 아래 명령은 이 폴더에서 실행
```

### 3. DB 켜고 데이터 넣기

터미널에서 이 폴더로 이동한 뒤:

```bash
cd VectorDB
docker compose up -d                 # DB 켜기 (처음엔 이미지 다운로드로 1~2분)
docker ps                            # rag-pgvector 가 Up 이면 성공
pip install -r requirements.txt      # 가상환경 권장
python load.py                       # 적재 + 검사 (몇 초)
python check_dense.py                # 검색 결과 확인 (처음엔 모델 440MB 다운로드, 1~2분)
```

이렇게 나오면 끝입니다.

- `load.py` → `적재 완료: 142,605개 … → 검사 통과`
- `check_dense.py` → Recall@10 ≈ 0.754, 마지막 줄 `→ 일치`

`check_dense.py`는 `eval.jsonl`의 질문 약 500개로 pgvector를 검색해, Colab T2에서 FAISS로 잰 점수와 같은지 비교합니다. 행 수만 맞고 문단·벡터 짝이 어긋난 경우를 잡아냅니다.

### 4. (선택) DBeaver로 들여다보기

New Database Connection → PostgreSQL → 아래 값 입력 → Test Connection → Finish.

| Host | Port | Database | Username | Password |
|---|---|---|---|---|
| `127.0.0.1` | `5432` | `rag` | `rag` | `rag` |

테이블은 `rag → Schemas → public → Tables → passages`. `embedding` 열은 DBeaver가 타입을 몰라 이상하게 보일 수 있는데 정상입니다.

```sql
SELECT count(*) FROM passages;                       -- 142605
SELECT pid, text, url, src FROM passages LIMIT 20;
```

## 안 될 때

| 증상 | 해결 |
|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop 앱을 켜고 고래 아이콘이 Running 될 때까지 기다림 |
| `port is already allocated` / 5432 사용 중 | 로컬 Postgres 등이 5432를 쓰는 중. `PG_PORT=5434 docker compose up -d`로 켜고, 스크립트 전에 `export PG_DSN=postgresql://rag:rag@127.0.0.1:5434/rag` (DBeaver도 포트 5434) |
| `load.py`에서 `No such file` | `data/v11_test/`에 파일 4개가 있는지, 폴더 이름이 맞는지 확인 |
| `count`가 0 | `python load.py`를 아직 안 돌린 것 |
| `check_dense.py`가 `⛔ 차이가 큼` | Drive 파일이 최신인지 확인 후 `docker compose down -v` → 3단계 다시 |
| 컴퓨터 재부팅 후 접속 안 됨 | Docker Desktop 켜고 `docker compose up -d` (데이터는 그대로 있음, `load.py` 다시 안 해도 됨) |

## 테이블

| 열 | 내용 |
|---|---|
| `pid` | 문단 번호 (= `corpus.jsonl` 줄 번호 = 임베딩 행 번호, `eval.jsonl`의 `gold_pids`와 같은 번호) |
| `text`, `url`, `src` | `corpus.jsonl` 그대로 |
| `embedding` | `halfvec(768)`, bge-base-en-v1.5, 정규화됨 |

## 검색

```sql
-- <#> 는 (-내적). 벡터가 정규화돼 있어서 작을수록 가깝다 = 코사인 유사도 큰 순
SELECT pid, text, url, -(embedding <#> %s) AS score
FROM passages ORDER BY embedding <#> %s LIMIT 10;
```

질문 벡터는 반드시 `'Represent this sentence for searching relevant passages: ' + 질문`을 `normalize_embeddings=True`로 임베딩합니다 (`check_dense.py` 참고).

## 자주 쓰는 명령

```bash
docker compose down        # 끄기 (데이터는 남음)
docker compose down -v     # 끄고 데이터까지 삭제 → 다음 up 때 init.sql부터 다시
docker exec -it rag-pgvector psql -U rag   # SQL 직접 치기
```
