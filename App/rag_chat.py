"""의료 정보 RAG 챗봇 (노트북 없이 실행).

저장된 DB(index/medical_db/, LabeledBaseline.ipynb 3-1에서 저장)를 불러와
질문 → BM25 + Dense 검색 → RRF → Rerank → 거절 게이트 → Qwen 답변(근거 번호 [n]) → 인용 검증
순서로 답합니다. 검색·프롬프트·검증 코드는 LabeledBaseline.ipynb와 같습니다.

생성 모델
- "ollama": Ollama의 qwen2.5:7b-instruct (원본 Qwen, 4bit). 먼저 `brew services start ollama`
- "mlx":    MLX의 Qwen2.5-7B-Instruct 4bit. adapter_path를 주면 GeneratorLoRA.ipynb에서 학습한 LoRA를 붙임
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import torch
import faiss
import bm25s
import Stemmer
from sentence_transformers import SentenceTransformer, CrossEncoder

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "index" / "medical_db"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b-instruct"
MLX_MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"
MAX_NEW_TOKENS = 128
SEED = 42

# Mac: torch와 faiss가 서로 다른 OpenMP를 불러와, faiss가 여러 스레드로 검색하면 프로세스가 죽음.
# 이 설정은 호출한 스레드에만 적용되므로 검색할 때마다 부름 (Gradio는 질문을 별도 작업 스레드에서 처리)
SINGLE_THREAD_FAISS = sys.platform == "darwin"

# ===== 프롬프트와 인용 검증 (LabeledBaseline.ipynb 6-3과 같음) =====
REFUSAL = "I cannot answer this question based on the provided documents."
SYSTEM_CITE = f"""You are a medical information assistant. Answer the question using ONLY the information in the provided passages.
Rules:
1. Do not use any knowledge that is not stated in the passages.
2. Answer in one or two complete sentences that restate the subject of the question.
3. End each sentence with the numbers of the passages that support it, like [1] or [2][3].
4. If the passages do not contain the answer, reply exactly: {REFUSAL}"""

CITE_RE = re.compile(r"\[(\d+)\]")
CITE_GROUP_RE = re.compile(r"((?:\s*\[\d+\])+)")
SUPPORT_MIN = 0.5   # 문장 단어 중 그 문장이 인용한 passage들에 있어야 하는 비율
CITE_MIN = 0.3      # 인용 하나가 근거로 인정되려면 문장 단어 중 이만큼이 그 passage에 있어야 함
STOPWORDS = set("""a an the and or but of to in on at for with by from as is are was were be been being it its this that
these those can may might will would should could do does did has have had not no than then so such which who what
when where why how also more most other some any each into about over after before your you they their them he she his her""".split())


def _tokens(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def is_refusal(pred):
    return "cannot answer" in pred.lower()


def content_words(text):
    return {t for t in _tokens(text) if t not in STOPWORDS}


def split_claims(answer):
    """답변을 (문장, 그 문장에 붙은 인용 번호) 묶음으로 나눔. '문장 [1][2].'와 '문장. [1]' 둘 다 처리"""
    parts = CITE_GROUP_RE.split(answer)
    claims = []
    for text, cites in zip(parts[0::2], parts[1::2] + [""]):
        if content_words(text):
            claims.append((text.strip(" ."), [int(n) for n in CITE_RE.findall(cites)]))
    return claims


def validate_answer(answer, texts):
    """인용 유효성과 근거 지원 여부 → (상태, 근거로 남긴 번호, 근거가 아니라 뺀 번호). texts: LLM에 넘긴 passage 문장들"""
    if is_refusal(answer):
        return "refused", [], []
    claims = split_claims(answer)
    cited = sorted({n for _, ns in claims for n in ns})
    if not cited:
        return "no_citation", [], []
    if any(n < 1 or n > len(texts) for n in cited):
        return "invalid_citation", [], cited
    status, kept = "supported", set()
    for claim, ns in claims:
        words = content_words(claim)
        cover = {n: words & set(_tokens(texts[n - 1])) for n in ns}
        union = set().union(*cover.values()) if cover else set()
        if len(union) / len(words) < SUPPORT_MIN:
            status = "unsupported"
        kept |= {n for n, c in cover.items() if len(c) / len(words) >= CITE_MIN}
    return status, sorted(kept), sorted(set(cited) - kept)


def build_messages(query, texts):
    ctx = "\n\n".join(f"[{i}] {t}" for i, t in enumerate(texts, 1))
    return [{"role": "system", "content": SYSTEM_CITE},
            {"role": "user", "content": f"Passages:\n{ctx}\n\nQuestion: {query}\nAnswer:"}]


class MedicalRAG:
    def __init__(self, db_dir=DB_DIR, generator="ollama", adapter_path=None):
        self.cfg = json.loads((db_dir / "config.json").read_text())
        self.corpus = pd.read_parquet(db_dir / "corpus.parquet")
        self.passages = self.corpus["text"].tolist()
        self.faiss_index = faiss.read_index(str(db_dir / "faiss.index"))
        self.bm25 = bm25s.BM25.load(str(db_dir / "bm25"))
        self.stemmer = Stemmer.Stemmer(self.cfg["bm25"]["stemmer"])
        assert len(self.passages) == self.faiss_index.ntotal == self.cfg["n_docs"]

        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.embedder = SentenceTransformer(self.cfg["embed_model"], device=device)
        self.reranker = CrossEncoder(self.cfg["rerank_model"], device=device, max_length=512)
        self.threshold = self.cfg["threshold"]

        self.generator = generator
        if generator == "ollama":
            self.session = requests.Session()
        elif generator == "mlx":
            from mlx_lm import load
            self.llm, self.tok = load(MLX_MODEL, adapter_path=adapter_path)
        else:
            raise ValueError(generator)
        self.model_name = f"{generator}" + (" + LoRA" if adapter_path else "")

    def retrieve(self, query):
        """BM25 + Dense → RRF → Rerank. (상위 pid 리스트, 점수 리스트)"""
        cfg = self.cfg
        tokens = bm25s.tokenize([query], stopwords=cfg["bm25"]["stopwords"], stemmer=self.stemmer, show_progress=False)
        bm25_ids, _ = self.bm25.retrieve(tokens, k=cfg["k_cand"], show_progress=False)
        q_emb = self.embedder.encode([cfg["query_prefix"] + query], normalize_embeddings=True,
                                     convert_to_numpy=True).astype("float32")
        if SINGLE_THREAD_FAISS:
            faiss.omp_set_num_threads(1)
        _, dense_ids = self.faiss_index.search(q_emb, cfg["k_cand"])

        score = defaultdict(float)
        for ids in (bm25_ids[0], dense_ids[0]):
            for rank, pid in enumerate(ids):
                score[int(pid)] += 1.0 / (cfg["rrf_k"] + rank + 1)
        cand = sorted(score, key=score.get, reverse=True)[:cfg["k_rerank"]]

        s = np.asarray(self.reranker.predict([(query, self.passages[p]) for p in cand], batch_size=256,
                                             show_progress_bar=False))
        order = np.argsort(-s)
        return [cand[i] for i in order], s[order].tolist()

    def generate(self, messages):
        if self.generator == "ollama":
            r = self.session.post(f"{OLLAMA_URL}/api/chat", json={
                "model": OLLAMA_MODEL, "messages": messages, "stream": False, "keep_alive": "30m",
                "options": {"temperature": 0, "seed": SEED, "num_predict": MAX_NEW_TOKENS, "num_ctx": 4096},
            }, timeout=600)
            r.raise_for_status()
            return r.json()["message"]["content"].strip()
        from mlx_lm import generate
        prompt = self.tok.apply_chat_template(messages, add_generation_prompt=True)
        return generate(self.llm, self.tok, prompt=prompt, max_tokens=MAX_NEW_TOKENS).strip()

    def ask(self, query):
        """→ {"answer", "status", "top_score", "threshold", "sources": [{"n", "url", "text", "score"}], "dropped"}"""
        ids, scores = self.retrieve(query)
        ids, scores = ids[:self.cfg["k_ctx"]], scores[:self.cfg["k_ctx"]]
        out = {"query": query, "top_score": scores[0], "threshold": self.threshold, "sources": [], "dropped": []}
        if scores[0] < self.threshold:   # 거절 게이트: 관련 의료 문서가 없음
            return {**out, "answer": REFUSAL, "status": "low_score"}
        texts = [self.passages[p] for p in ids]
        answer = self.generate(build_messages(query, texts))
        status, cited, dropped = validate_answer(answer, texts)
        # 근거로 확인된 인용만 표시. 하나도 없으면 넘긴 passage 전체를 참고로 표시
        show = cited or ([] if is_refusal(answer) else list(range(1, len(ids) + 1)))
        sources = [{"n": n, "url": self.corpus.at[ids[n - 1], "url"], "text": texts[n - 1], "score": scores[n - 1]}
                   for n in show]
        return {**out, "answer": answer, "status": status, "sources": sources, "dropped": dropped}


if __name__ == "__main__":
    rag = MedicalRAG()
    for q in sys.argv[1:] or ["What are the symptoms of iron deficiency anemia?", "Who won the 2010 FIFA World Cup?"]:
        r = rag.ask(q)
        print(f"Q: {q}\nA: {r['answer']}\n   ({r['status']}, top={r['top_score']:.2f}, thr={r['threshold']:.2f})")
        for s in r["sources"]:
            print(f"  [{s['n']}] {s['url']}\n      {s['text'][:150]}...")
