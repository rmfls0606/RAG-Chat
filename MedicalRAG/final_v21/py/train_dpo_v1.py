# DPO v1 학습 파이프라인 - 후보 생성 → 심판 → 선호 쌍 → DPO 학습 → 평가
# 자동 변환: 07_DPO_v1_17_dpo_v21.ipynb (Colab 노트북 셀 순서 그대로). "!pip" 줄은 주석 처리.
# 실행 전: pip install -U peft faiss-cpu sentence-transformers transformers gradio


# # 17. DPO (v2.1): 심판이 고른 "좋은 답 vs 나쁜 답"으로 선호 학습
# 
# 15 SFT v2는 원본 답 중 좋은 것만 따라 해서 **원본과 같은 수준**에서 멈췄습니다. DPO는 **나쁜 답(오답·근거 없는 답·잘못 거절)을 피하도록** 직접 학습해서 원본을 넘을 수 있습니다.
# 
# - 생성 모델·검색: **16에서 검증으로 고른 조합** (`gen_compare/best_config.json`)
# - 학습 질문: 15와 같은 train 질문 (시험·검증·검증 생성셋 제외), 문단은 15의 MiniLM 상위 5
# - 후보 답: 고른 모델로 질문당 3개 (7B면 15 결과 재사용) → 14B 심판 (14·15·16과 같은 캐시)
# - 쌍 만들기
# 
# | 경우 | 좋은 답 (chosen) | 나쁜 답 (rejected) |
# |---|---|---|
# | 답 있는 질문 | 정답 2점 + 근거 충실한 답 | 오답·근거 없는 답 / 문단에 답 있는데 **거절** |
# | 문단에 답 없음 (심판 < 0.2) | 거절 | 지어낸 답 |
# | MS MARCO 답 없음인데 문단에 답 있음 (≥ 0.8) | 근거 충실한 답 | 거절 |
# 
# - DPO는 TRL 없이 직접 구현 (버전 충돌 방지): LoRA r16, β 0.1, 참조 모델 = 같은 모델에서 LoRA 끈 상태
# - 평가: 16과 같은 시험 650 / 검증 200, 같은 심판 → 16 최고 조합과 차이 + 95% CI
# - 먼저 `QUICK = True`로 점검


# ## 1. 설치 + 경로

# !pip -q install -U peft faiss-cpu sentence-transformers
# !pip -q uninstall -y torchao   # 최신 peft가 Colab 기본 torchao(0.10)와 충돌해서 제거 (14·15에서 확인한 조합)

QUICK = False   # True: 질문 수십 개로 점검 (결과는 dpo/quick) / False: 본 실행

import os
from google.colab import drive
drive.mount('/content/drive')
SAVE_DIR   = '/content/drive/MyDrive/rag_msmarco/health'
RAG_DIR    = f'{SAVE_DIR}/rag'          # 08 시험 답변
R2_DIR     = f'{SAVE_DIR}/rerank2'      # 11 후보·재정렬 점수
JUDGE_DIR  = f'{SAVE_DIR}/judge_eval'   # 14 검증 답변 + 심판 캐시
GC_DIR     = f'{SAVE_DIR}/gen_compare'                              # 16 본 실행 결과 (QUICK도 이걸 씀)
SFT_DIR    = f'{SAVE_DIR}/sft_v2'                                   # 15 후보 질문·답
OUT_DIR    = f'{SAVE_DIR}/dpo' + ('/quick' if QUICK else '')
REPORT_DIR = '/content/drive/MyDrive/RAG/2_results/generation_v21'
os.makedirs(OUT_DIR, exist_ok=True); os.makedirs(REPORT_DIR, exist_ok=True)
print('QUICK =', QUICK, '→', OUT_DIR)


# ## 2. 설정 + 공통 함수 (16과 같음)

import re, json, gzip, time, random, string, hashlib, gc
from collections import Counter
from urllib.parse import urlparse
import numpy as np
import pandas as pd
import torch, transformers, peft

SEED      = 42
THRESH    = 4.921875
ENSEMBLE  = ['bge-reranker-large', 'bge-reranker-v2-m3']
BASE_RR   = 'ms-marco-MiniLM-L-6-v2'
BASE_GEN  = 'Qwen/Qwen2.5-7B-Instruct'
GENS      = ['Qwen/Qwen2.5-14B-Instruct', 'Qwen/Qwen3-8B', 'Qwen/Qwen3-14B']
JUDGE_LLM = 'Qwen/Qwen2.5-14B-Instruct'
JUDGE2    = 'microsoft/phi-4'
GEN_BS    = 16
N_TEST_A, N_TEST_N, N_TEST_O, N_VAL = (20, 5, 5, 12) if QUICK else (None, None, None, None)
DEMO = ['why does my face turn red and itchy after drinking alcohol',
        'what are the symptoms of low vitamin d',
        'can ibuprofen cause stomach bleeding',
        'how long does the flu last',
        'what is a normal resting heart rate for adults']

assert torch.cuda.is_available(), 'GPU 런타임이 아닙니다 (A100 권장).'
print('GPU:', torch.cuda.get_device_name(0), f'{torch.cuda.get_device_properties(0).total_memory / 1e9:.0f}GB')
print(f'torch {torch.__version__} / transformers {transformers.__version__} / peft {peft.__version__}')

def load_jsonl(path):
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def save_jsonl(rows, path):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

def toks(s):
    s = s.lower(); s = re.sub(r'\[\d+\]', ' ', s)
    s = ''.join(ch if ch not in string.punctuation else ' ' for ch in s)
    return [w for w in s.split() if w not in {'a', 'an', 'the'}]

def f1(pred, ref):
    p, r = toks(pred), toks(ref); c = sum((Counter(p) & Counter(r)).values())
    if not p or not r or c == 0:
        return 0.0
    pr, rc = c / len(p), c / len(r)
    return 2 * pr * rc / (pr + rc)

REFUSAL = "Sorry, I can't answer that from the medical documents I have."
def is_refusal(ans):
    a = ans.lower()
    return any(p in a for p in ["can't answer", 'cannot answer', 'unable to answer'])

SYS_RAG = f"""You are a careful medical information assistant.
Rules:
1. Answer ONLY with facts stated in the numbered documents. Do not add outside knowledge.
2. After each sentence, cite the supporting document numbers like [1] or [2][4].
3. If the question is not about health or medicine, or the documents do not contain the answer, reply with exactly this sentence: "{REFUSAL}"
4. Answer in 2-4 short sentences."""

def free_gpu():
    gc.collect(); torch.cuda.empty_cache()
    print(f'GPU 사용 {torch.cuda.memory_allocated() / 1e9:.1f}GB')

corpus = load_jsonl(f'{SAVE_DIR}/corpus.jsonl')
texts  = [c['text'] for c in corpus]
def site_of(url):
    h = urlparse(url).netloc.lower()
    return h[4:] if h.startswith('www.') else h
sites  = [site_of(c['url']) for c in corpus]
norm_text = lambda t: ' '.join(t.lower().split())
docs_text = lambda pids: '\n'.join(f'[{i}] ({sites[p]}) {texts[p]}' for i, p in enumerate(pids, 1))
def rag_messages(q, pids):
    return [{'role': 'system', 'content': SYS_RAG}, {'role': 'user', 'content': f'Documents:\n{docs_text(pids)}\n\nQuestion: {q}'}]
print(f'문단 {len(texts):,}')

N_POOL     = 40 if QUICK else None    # 15 후보 질문 중 사용 수 (None = 전부)
N_SAMPLES, TEMP = 3, 0.7
CHUNK      = 256
BETA, LR   = 0.1, 2e-5
EPOCHS     = 1
GRAD_ACC   = 8
LORA_R, LORA_ALPHA = 16, 32
MAX_LEN    = 1400


# ## 3. 시험·검증 질문 + 16 답변 + 고른 조합

eval_set = load_jsonl(f'{SAVE_DIR}/eval.jsonl')
val_set  = load_jsonl(f'{SAVE_DIR}/rerank/val.jsonl')
C  = np.load(f'{R2_DIR}/candidates.npz')
SC = {n: np.load(f'{R2_DIR}/scores_{n}.npz') for n in ENSEMBLE + [BASE_RR]}
zs = lambda m: (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)

def pick(order_scores, ids, n):
    docs, seen = [], set()
    for j in np.argsort(-order_scores):
        p = int(ids[j]); key = norm_text(texts[p])
        if key in seen:
            continue
        seen.add(key); docs.append(p)
        if len(docs) == n:
            break
    return docs

groups = {'test':  [q for q in eval_set if q['domain'] == 'health' and q.get('answerable', True) and q.get('gold_pids')],
          'noans': [q for q in eval_set if q['domain'] == 'health' and not q.get('answerable', True)],
          'other': [q for q in eval_set if q['domain'] != 'health'],
          'val':   val_set}
info = {}
for g, qs in groups.items():
    ids = C[f'{g}_ids']
    assert len(ids) == len(qs), f'{g}: 11 후보 수 {len(ids)} ≠ 질문 수 {len(qs)}'
    ens = (zs(SC[ENSEMBLE[0]][g]) + zs(SC[ENSEMBLE[1]][g])) / 2
    base = SC[BASE_RR][g]
    for i, q in enumerate(qs):
        info[(g == 'val', str(q['qid']))] = {'top_minilm': float(base[i].max()), 'M5': pick(base[i], ids[i], 5),
                                              'E5': pick(ens[i], ids[i], 5), 'E10': pick(ens[i], ids[i], 10)}

# 시험 650: 08 답변 (S0 = 'RAG 개선', 원본 7B + MiniLM 상위 5)
evq = {str(q['qid']): q for q in eval_set}
test_rows = []
for r in load_jsonl(f'{RAG_DIR}/eval_answers.jsonl'):
    q = evq[str(r['qid'])]; inf = info[(False, str(r['qid']))]
    g = 'A' if r['domain'] == 'health' and r['answerable'] else ('N' if r['domain'] == 'health' else 'O')
    test_rows.append({'qid': str(r['qid']), 'query': r['query'], 'answers': q['answers'], 'gold_pids': q.get('gold_pids') or [],
                      'group': g, 'refuse': r['rag_docs'][0]['score'] < THRESH,
                      'docs': {'S0': [d['pid'] for d in r['rag_docs']], 'E5': inf['E5'], 'E10': inf['E10']},
                      'ans': {'S0|7B': r['RAG 개선']}})
# 검증 200 (답 있음): 14 답변 (S0 = 'RAG 개선')
v14 = {str(r['qid']): r for r in load_jsonl(f'{JUDGE_DIR}/val_answers.jsonl') if r['group'] == 'A'}
val_rows = []
for q in val_set:
    r = v14.get(str(q['qid'])); inf = info[(True, str(q['qid']))]
    if r is None:
        continue
    val_rows.append({'qid': str(q['qid']), 'query': q['query'], 'answers': r['answers'], 'gold_pids': q.get('gold_pids') or [],
                     'group': 'A', 'refuse': r['rag_docs'][0]['score'] < THRESH,
                     'docs': {'S0': [d['pid'] for d in r['rag_docs']], 'E5': inf['E5'], 'E10': inf['E10']},
                     'ans': {'S0|7B': r['RAG 개선']}})
if QUICK:
    by = lambda g: [r for r in test_rows if r['group'] == g]
    test_rows = by('A')[:N_TEST_A] + by('N')[:N_TEST_N] + by('O')[:N_TEST_O]
    val_rows = val_rows[:N_VAL]
print(f'시험 {len(test_rows)} {Counter(r["group"] for r in test_rows)} / 검증 {len(val_rows)}')
for k in ('S0', 'E5', 'E10'):
    for name, rows in [('시험', test_rows), ('검증', val_rows)]:
        A = [r for r in rows if r['group'] == 'A']
        print(f'  {k} {name} 근거 R@N {np.mean([bool(set(r["gold_pids"]) & set(r["docs"][k])) for r in A]):.3f}', end='')
    print()

ANS_PATH = f'{OUT_DIR}/answers.jsonl'   # 이 노트북 답변 (DPO)
def save_answers():
    save_jsonl([{'set': s, 'qid': r['qid'], 'ans': r['ans']} for s, rows in [('test', test_rows), ('val', val_rows)] for r in rows], ANS_PATH)
if os.path.exists(ANS_PATH):
    saved = {(d['set'], d['qid']): d['ans'] for d in load_jsonl(ANS_PATH)}
    for s, rows in [('test', test_rows), ('val', val_rows)]:
        for r in rows:
            r['ans'].update(saved.get((s, r['qid']), {}))
    print('저장된 답변 불러옴:', sorted({k for r in test_rows for k in r['ans']}))

# 16 답변 (비교 기준) 불러오기
for d in load_jsonl(f'{GC_DIR}/answers.jsonl'):
    rows = test_rows if d['set'] == 'test' else val_rows
    for r in rows:
        if r['qid'] == d['qid']:
            for k, v in d['ans'].items():
                r['ans'].setdefault(k, v)
cfg = json.load(open(f'{GC_DIR}/best_config.json'))
BEST, BEST_RETR = cfg['best'], cfg['best'].split('|')[0]
MODEL_OF = {'7B': BASE_GEN, 'Qwen2.5-14B': 'Qwen/Qwen2.5-14B-Instruct', 'Qwen3-8B': 'Qwen/Qwen3-8B', 'Qwen3-14B': 'Qwen/Qwen3-14B'}
GEN_NAME = MODEL_OF[BEST.split('|')[1]]
DPO_KEY = f'{BEST}+DPO'
print(f'16 최고 조합: {BEST} → 생성 모델 {GEN_NAME}, 검색 {BEST_RETR}')


# ## 4. 생성·심판 함수 (16과 같음)

from transformers import AutoTokenizer, AutoModelForCausalLM

def load_gen(name):
    tok = AutoTokenizer.from_pretrained(name, padding_side='left')
    llm = AutoModelForCausalLM.from_pretrained(name, dtype=torch.bfloat16, device_map='cuda').eval()
    return tok, llm

@torch.inference_mode()
def generate(tok, llm, msgs_list, bs=GEN_BS, max_new=256):
    outs = []
    for i in range(0, len(msgs_list), bs):
        prompts = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True, enable_thinking=False)
                   for m in msgs_list[i:i + bs]]
        enc = tok(prompts, return_tensors='pt', padding=True).to(llm.device)
        gen = llm.generate(**enc, max_new_tokens=max_new, do_sample=False, temperature=None, top_p=None, top_k=None,
                           pad_token_id=tok.pad_token_id or tok.eos_token_id)
        dec = tok.batch_decode(gen[:, enc['input_ids'].shape[1]:], skip_special_tokens=True)
        outs += [re.sub(r'<think>.*?</think>', '', o, flags=re.S).strip() for o in dec]
    return outs

def run_system(tok, llm, key, docs_key):
    # key = '검색|모델' 시스템 답변을 시험·검증 모두 생성 (거절 규칙 08과 같음)
    for rows in (test_rows, val_rows):
        todo = [r for r in rows if not r['refuse'] and key not in r['ans']]
        t = time.time()
        outs = generate(tok, llm, [rag_messages(r['query'], r['docs'][docs_key]) for r in todo])
        for r, a in zip(todo, outs):
            r['ans'][key] = a
        for r in rows:
            if r['refuse']:
                r['ans'][key] = REFUSAL
        if todo:
            print(f'  {key}: {len(todo)}개 생성 {time.time() - t:.0f}초')
    save_answers()

SYS_CORRECT = ('You grade answers to health questions. Compare the candidate answer with the reference answer(s). '
               'Reply with one digit only.\n'
               '2 = correct: states the key facts of a reference answer (different wording or extra correct detail is fine)\n'
               '1 = partially correct: some key facts, but incomplete or partly wrong\n'
               '0 = wrong, unrelated, or does not answer the question')
SYS_FAITH = ('You check whether an answer is supported by the given documents. Reply with one digit only.\n'
             '1 = every factual statement in the answer is stated in the documents\n'
             '0 = the answer contains a fact that is not in the documents, or contradicts them')
SYS_EVID = ('You check whether the given documents contain the information needed to answer a health question. '
            'Reply with one digit only.\n'
            '1 = at least one document directly answers the question\n'
            '0 = the documents do not answer the question (related topic only, or missing information)')
def correct_msgs(q, refs, ans):
    ref = '\n'.join(f'- {x}' for x in refs[:3])
    return [{'role': 'system', 'content': SYS_CORRECT},
            {'role': 'user', 'content': f'Question: {q}\nReference answer(s):\n{ref}\nCandidate answer: {ans}\n\nGrade (0, 1 or 2):'}]
def faith_msgs(dt, ans):
    return [{'role': 'system', 'content': SYS_FAITH},
            {'role': 'user', 'content': f'Documents:\n{dt}\n\nAnswer: {ans}\n\nSupported (0 or 1)?'}]
def evid_msgs(q, dt):
    return [{'role': 'system', 'content': SYS_EVID},
            {'role': 'user', 'content': f'Documents:\n{dt}\n\nQuestion: {q}\n\nDo the documents answer it (0 or 1)?'}]

class Judge:
    def __init__(self, name, cache_path, tag=''):
        self.tok = AutoTokenizer.from_pretrained(name, padding_side='left')
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        self.llm = AutoModelForCausalLM.from_pretrained(name, dtype=torch.bfloat16, device_map='cuda').eval()
        self.digits = [self.tok.encode(d, add_special_tokens=False)[-1] for d in '012']
        self.path, self.tag = cache_path, tag
        self.cache = {j['key']: j for j in load_jsonl(cache_path)} if os.path.exists(cache_path) else {}
    def key(self, kind, q, a):
        return hashlib.md5(f'{self.tag}{kind}|{q}|{a}'.encode()).hexdigest()
    @torch.inference_mode()
    def probs(self, msgs_list, n, bs=8):
        prompts = [self.tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs_list]
        order = np.argsort([len(p) for p in prompts]); out = [None] * len(prompts)
        for s in range(0, len(order), bs):
            idx = order[s:s + bs]
            enc = self.tok([prompts[i] for i in idx], return_tensors='pt', padding=True, add_special_tokens=False).to(self.llm.device)
            logits = self.llm(**enc).logits[:, -1, self.digits[:n]].float()
            for i, p in zip(idx, torch.softmax(logits, -1).cpu().numpy()):
                out[i] = p
        return out
    def score(self, kind, items):
        # 'c' (q, refs, ans) → 0~2 / 'f' (q, docs_text, ans) → 0~1 / 'e' (q, docs_text) → 0~1
        keyed = [(self.key(kind, it[0], it[-1]), it) for it in items]
        need = list({k: it for k, it in keyed if k not in self.cache}.items())
        t = time.time()
        for s in range(0, len(need), 2000):
            part = need[s:s + 2000]
            if kind == 'c':
                vals = [float(p[1] + 2 * p[2]) for p in self.probs([correct_msgs(*it) for _, it in part], 3)]
            elif kind == 'f':
                vals = [float(p[1]) for p in self.probs([faith_msgs(it[1], it[2]) for _, it in part], 2)]
            else:
                vals = [float(p[1]) for p in self.probs([evid_msgs(it[0], it[1]) for _, it in part], 2)]
            for (k, _), v in zip(part, vals):
                self.cache[k] = {'key': k, 'v': v}
            save_jsonl(list(self.cache.values()), self.path)
        if need:
            print(f'  심판{self.tag} {kind}: {len(need)}개 새로 채점 ({time.time() - t:.0f}초)')
        return [self.cache[k]['v'] for k, _ in keyed]
    def close(self):
        del self.llm; free_gpu()

def evaluate(J, rows, systems, faith=True):
    table = {}
    for key in systems:
        dk = key.split('|')[0]
        A = [r for r in rows if r['group'] == 'A']
        ansA = [r for r in A if not is_refusal(r['ans'][key])]
        cs = dict(zip([id(r) for r in ansA], J.score('c', [(r['query'], r['answers'], r['ans'][key]) for r in ansA])))
        c_all = [cs.get(id(r), 0.0) for r in A]
        g = lambda k: [r for r in rows if r['group'] == k]
        row = {'정답률 (심판 2점)': np.mean([c >= 1.5 for c in c_all]),
               '정답+부분': np.mean([c >= 0.5 for c in c_all]),
               '평균 점수 (0~2)': np.mean(c_all),
               'F1 (참고)': np.mean([max(f1(r['ans'][key], x) for x in r['answers']) for r in A]),
               '잘못 거절': np.mean([is_refusal(r['ans'][key]) for r in A])}
        if faith:
            answered = [r for r in rows if not is_refusal(r['ans'][key])]
            fs = J.score('f', [(r['query'], docs_text(r['docs'][dk]), r['ans'][key]) for r in answered])
            row['근거 충실도'] = np.mean([f >= 0.5 for f in fs]) if fs else np.nan
        if g('N'):
            row['답 없음 거절률 (MS MARCO 기준)'] = np.mean([is_refusal(r['ans'][key]) for r in g('N')])
        if g('O'):
            row['분야 밖 거절률'] = np.mean([is_refusal(r['ans'][key]) for r in g('O')])
        table[key] = row
    return pd.DataFrame(table).T.round(3)

JUDGE_PATH = f'{JUDGE_DIR}/judgments.jsonl'


# ## 5. 학습 후보 답 (고른 모델로 질문당 3개, 7B면 15 결과 재사용)

pool = load_jsonl(f'{SFT_DIR}/candidates.jsonl')
if N_POOL:   # QUICK: 답 있음·답 없음 섞어서
    pool = [q for q in pool if q['group'] == 'A'][:N_POOL * 3 // 4] + [q for q in pool if q['group'] == 'N'][:N_POOL // 4]
print(f'학습 질문 {len(pool)} {Counter(q["group"] for q in pool)}')
if GEN_NAME != BASE_GEN:
    CAND_PATH = f'{OUT_DIR}/candidates.jsonl'
    done = {r['qid']: r for r in load_jsonl(CAND_PATH)} if os.path.exists(CAND_PATH) else {}
    todo = [q for q in pool if q['qid'] not in done]
    print(f'{GEN_NAME} 후보 생성: 완료 {len(done)} / 남음 {len(todo)}')
    if todo:
        tok, llm = load_gen(GEN_NAME)
        @torch.inference_mode()
        def sample(msgs_list, n, bs=GEN_BS):
            outs = []
            for i in range(0, len(msgs_list), bs):
                prompts = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True, enable_thinking=False)
                           for m in msgs_list[i:i + bs]]
                enc = tok(prompts, return_tensors='pt', padding=True).to(llm.device)
                gen = llm.generate(**enc, max_new_tokens=256, do_sample=True, temperature=TEMP, top_p=0.9, top_k=None,
                                   num_return_sequences=n, pad_token_id=tok.pad_token_id or tok.eos_token_id)
                dec = [re.sub(r'<think>.*?</think>', '', o, flags=re.S).strip()
                       for o in tok.batch_decode(gen[:, enc['input_ids'].shape[1]:], skip_special_tokens=True)]
                outs += [dec[j * n:(j + 1) * n] for j in range(len(prompts))]
            return outs
        torch.manual_seed(SEED); t = time.time()
        for s in range(0, len(todo), CHUNK):
            part = todo[s:s + CHUNK]
            msgs = [rag_messages(q['query'], [d['pid'] for d in q['rag_docs']]) for q in part]
            greedy = generate(tok, llm, msgs)
            sampled = sample(msgs, N_SAMPLES - 1)
            for q, g, sm in zip(part, greedy, sampled):
                done[q['qid']] = {**q, 'samples': [g] + sm}
            save_jsonl(list(done.values()), CAND_PATH)
            print(f'  {s + len(part)}/{len(todo)} ({(time.time() - t) / 60:.0f}분)')
        del llm; free_gpu()
    pool = [done[q['qid']] for q in pool]
print('예:', pool[0]['query'], '→', pool[0]['samples'][0][:150])


# ## 6. 심판 → 선호 쌍 만들기

J = Judge(JUDGE_LLM, JUDGE_PATH)
for r in pool:
    r['pids'] = [d['pid'] for d in r['rag_docs']]
    r['dt'] = docs_text(r['pids'])
    r['uniq'] = [a for a in dict.fromkeys(r['samples']) if not is_refusal(a)]
    r['any_refusal'] = any(is_refusal(a) for a in r['samples'])
c_it = iter(J.score('c', [(r['query'], r['refs'], a) for r in pool if r['group'] == 'A' for a in r['uniq']]))
f_it = iter(J.score('f', [(r['query'], r['dt'], a) for r in pool for a in r['uniq']]))
ev_all = J.score('e', [(r['query'], r['dt']) for r in pool])
J.close(); del J

pairs = []
for r, ev in zip(pool, ev_all):
    sc = [(a, next(c_it) if r['group'] == 'A' else None, next(f_it)) for a in r['uniq']]
    mk = lambda ch, rj, kind: pairs.append({'qid': r['qid'], 'query': r['query'], 'pids': r['pids'], 'chosen': ch, 'rejected': rj, 'kind': kind})
    if r['group'] == 'A':
        good = sorted([(c + f, a) for a, c, f in sc if c >= 1.5 and f >= 0.5], reverse=True)
        bad  = sorted([(c + f, a) for a, c, f in sc if c < 0.5 or f < 0.5])
        if good:
            if bad:
                mk(good[0][1], bad[0][1], '정답 vs 오답/근거 없음')
            if r['any_refusal'] and ev >= 0.8:
                mk(good[0][1], REFUSAL, '정답 vs 잘못 거절')
        elif ev < 0.2 and sc:
            mk(REFUSAL, min(sc, key=lambda x: x[2])[0], '거절 vs 지어낸 답')
    else:
        if ev < 0.2 and sc:
            mk(REFUSAL, min(sc, key=lambda x: x[2])[0], '거절 vs 지어낸 답')
        elif ev >= 0.8:
            good = sorted([(f, a) for a, _, f in sc if f >= 0.8], reverse=True)
            if good and r['any_refusal']:
                mk(good[0][1], REFUSAL, '근거 답 vs 잘못 거절')
            elif good:
                low = [(f, a) for a, _, f in sc if f < 0.5]
                if low:
                    mk(good[0][1], min(low)[1], '근거 답 vs 근거 없음')
random.Random(SEED).shuffle(pairs)
# 거절이 '좋은 답'인 쌍은 30% 이하로 (너무 많으면 모델이 거절을 과하게 배움)
ref_p = [p for p in pairs if p['chosen'] == REFUSAL]; ans_p = [p for p in pairs if p['chosen'] != REFUSAL]
cap = int(len(ans_p) * 0.3 / 0.7)
if len(ref_p) > cap:
    print(f'거절 쌍 {len(ref_p)} → {cap}개로 제한')
    pairs = ans_p + ref_p[:cap]; random.Random(SEED).shuffle(pairs)
save_jsonl(pairs, f'{OUT_DIR}/pairs.jsonl')
print(f'선호 쌍 {len(pairs)}개:', dict(Counter(p['kind'] for p in pairs)))
for p in pairs[:2]:
    print(f"- Q: {p['query']}\n  좋음: {p['chosen'][:150]}\n  나쁨: {p['rejected'][:150]}")


# ## 7. DPO 학습 (LoRA, 참조 = LoRA 끈 같은 모델)
# 
# 손실 = −log σ(β · [(log π(좋음) − log π_ref(좋음)) − (log π(나쁨) − log π_ref(나쁨))])

from peft import LoraConfig, get_peft_model, PeftModel
ADAPTER_DIR = f'{OUT_DIR}/adapter'
tok = AutoTokenizer.from_pretrained(GEN_NAME)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
llm = AutoModelForCausalLM.from_pretrained(GEN_NAME, dtype=torch.bfloat16, device_map='cuda')

def feats(p):
    prompt = tok.apply_chat_template(rag_messages(p['query'], p['pids']), tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    p_ids = tok(prompt, add_special_tokens=False)['input_ids']
    out = []
    for ans in (p['chosen'], p['rejected']):
        a_ids = tok(ans + '<|im_end|>', add_special_tokens=False)['input_ids']
        out.append((p_ids + a_ids, [-100] * len(p_ids) + a_ids))
    return out

def seq_logps(model, items):
    n = max(len(i) for i, _ in items)
    ids = torch.tensor([i + [tok.pad_token_id] * (n - len(i)) for i, _ in items], device='cuda')
    att = torch.tensor([[1] * len(i) + [0] * (n - len(i)) for i, _ in items], device='cuda')
    lab = torch.tensor([l + [-100] * (n - len(l)) for _, l in items], device='cuda')
    logits = model(input_ids=ids, attention_mask=att).logits[:, :-1].float()
    lab = lab[:, 1:]; mask = lab != -100
    lp = torch.gather(logits.log_softmax(-1), 2, lab.clamp(min=0).unsqueeze(-1)).squeeze(-1)
    return (lp * mask).sum(-1)

if os.path.exists(f'{ADAPTER_DIR}/adapter_config.json'):
    llm = PeftModel.from_pretrained(llm, ADAPTER_DIR)
    print('저장된 DPO LoRA 불러옴 (학습 건너뜀)')
else:
    llm.config.use_cache = False
    llm.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    llm.enable_input_require_grads()
    llm = get_peft_model(llm, LoraConfig(r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0.05, task_type='CAUSAL_LM',
                                         target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']))
    data = [f for f in map(feats, pairs) if max(len(x[0]) for x in f) <= MAX_LEN]
    print(f'학습 쌍 {len(data)} (길이 초과 {len(pairs) - len(data)} 제외)')
    opt = torch.optim.AdamW([p for p in llm.parameters() if p.requires_grad], lr=LR, weight_decay=0.0)
    total = max(1, len(data) * EPOCHS // GRAD_ACC); warm = max(1, int(total * 0.05))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warm if s < warm else max(0.0, (total - s) / max(1, total - warm)))
    llm.train(); log, acc_hist, step, t = [], [], 0, time.time()
    for ep in range(EPOCHS):
        for i, f in enumerate(data):
            with torch.no_grad(), llm.disable_adapter():
                ref = seq_logps(llm, f)
            pol = seq_logps(llm, f)
            margin = BETA * ((pol[0] - ref[0]) - (pol[1] - ref[1]))
            loss = -torch.nn.functional.logsigmoid(margin)
            (loss / GRAD_ACC).backward()
            acc_hist.append(float(margin > 0)); log.append(float(loss))
            if (i + 1) % GRAD_ACC == 0 or i == len(data) - 1:
                torch.nn.utils.clip_grad_norm_([p for p in llm.parameters() if p.requires_grad], 1.0)
                opt.step(); sched.step(); opt.zero_grad(); step += 1
                if step % 10 == 0 or step == total:
                    print(f'  step {step}/{total}  loss {np.mean(log[-80:]):.3f}  보상 정확도 {np.mean(acc_hist[-80:]):.2f}  ({(time.time() - t) / 60:.0f}분)')
    llm.save_pretrained(ADAPTER_DIR)
    pd.DataFrame({'loss': log, 'acc': acc_hist}).to_csv(f'{OUT_DIR}/train_log.csv', index=False)
    print(f'DPO 끝: {(time.time() - t) / 60:.0f}분, 마지막 보상 정확도 {np.mean(acc_hist[-80:]):.2f}')
llm.eval(); llm.config.use_cache = True; tok.padding_side = 'left'


# ## 8. DPO 모델 답변 (시험 650·검증 200, 16에서 고른 검색)

run_system(tok, llm, DPO_KEY, BEST_RETR)
del llm; free_gpu()


# ## 9. 같은 심판으로 비교

J = Judge(JUDGE_LLM, JUDGE_PATH)
SYSTEMS = list(dict.fromkeys(['S0|7B', BEST, DPO_KEY]))
d_val  = evaluate(J, val_rows, SYSTEMS)
d_test = evaluate(J, test_rows, SYSTEMS)
print('[검증 200]'); display(d_val)
print(f'[시험 {len(test_rows)}]'); display(d_test)

A = [r for r in test_rows if r['group'] == 'A']
def corr(r, key):
    return 0.0 if is_refusal(r['ans'][key]) else J.cache[J.key('c', r['query'], r['ans'][key])]['v']
def boot(key, base):
    d = np.array([(corr(r, key) >= 1.5) - (corr(r, base) >= 1.5) for r in A], dtype=float)
    bs = np.random.default_rng(SEED).choice(d, (2000, len(d))).mean(1)
    return d.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5)
ci_tab = pd.DataFrame({f'{DPO_KEY} − {b}': dict(zip(['차이', '95% CI 하한', '95% CI 상한'], boot(DPO_KEY, b)))
                       for b in dict.fromkeys([BEST, 'S0|7B'])}).T.round(3)
print('[시험 정답률 차이]'); display(ci_tab)

N = [r for r in test_rows if r['group'] == 'N']
ref_rows = {}
for key in SYSTEMS:
    dk = key.split('|')[0]
    ev = J.score('e', [(r['query'], docs_text(r['docs'][dk])) for r in N])
    no = [r for r, e in zip(N, ev) if e < 0.2]; yes = [r for r, e in zip(N, ev) if e >= 0.8]
    ref_rows[key] = {'진짜 답 없음 → 거절률': np.mean([is_refusal(r['ans'][key]) for r in no]) if no else np.nan,
                     '사실 답 있음 → 답변률': np.mean([not is_refusal(r['ans'][key]) for r in yes]) if yes else np.nan}
ref_tab = pd.DataFrame(ref_rows).T.round(3)
print('[시험 답 없음 100: 심판 기준 거절]'); display(ref_tab)
J.close(); del J


# ## 10. 저장

stamp = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() + 9 * 3600))
summary = '\n'.join([
    f'# 17 DPO (v2.1){" [QUICK 점검]" if QUICK else ""} ({stamp} KST)', '',
    f'- 기준 조합 (16 검증 최고): {BEST} → 생성 {GEN_NAME}, 검색 {BEST_RETR}',
    f'- 선호 쌍 {len(pairs)}개: {dict(Counter(p["kind"] for p in pairs))}',
    f'- DPO: LoRA r{LORA_R}, β {BETA}, lr {LR}, {EPOCHS} epoch, 어댑터 `{ADAPTER_DIR.replace(SAVE_DIR, "health")}`', '',
    '## 검증 200', '', d_val.to_markdown(), '', f'## 시험 {len(test_rows)}', '', d_test.to_markdown(), '',
    '## 시험 정답률 차이 (95% 부트스트랩)', '', ci_tab.to_markdown(), '',
    '## 시험 답 없음 100: 심판 기준 거절', '', ref_tab.to_markdown(),
])
paths = [f'{OUT_DIR}/results_summary.md'] + ([] if QUICK else [f'{REPORT_DIR}/17_dpo_summary.md'])
for path in paths:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(summary)
print(summary)


# ## 11. 드라이브 저장 마무리 + 런타임 종료 (QUICK 점검일 땐 런타임 유지)

from google.colab import drive, runtime
drive.flush_and_unmount()
if not QUICK:
    runtime.unassign()
