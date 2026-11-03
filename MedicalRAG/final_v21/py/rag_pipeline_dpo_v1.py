# 최종 RAG 파이프라인 (Qwen3-8B + DPO v1) - 추론
# 자동 변환: 10_최종챗봇_08f_final_chatbot_v21.ipynb (Colab 노트북 셀 순서 그대로). "!pip" 줄은 주석 처리.
# 실행 전: pip install -U peft faiss-cpu sentence-transformers transformers gradio


# # 08f. 최종 의료 QA 챗봇 (v2.1)
# 
# 16·17·18에서 검증셋으로 고른 **최종 설정**(`rag_msmarco/health/final/final_config.json`)을 그대로 읽어서 챗봇을 켭니다. **런타임 → 모두 실행** 한 번이면 됩니다 (A100, 약 10분).
# 
# - 검색: bge 후보 100개 → 재정렬 (설정에 따라 MiniLM 또는 bge-reranker-large + v2-m3 앙상블) → 상위 N개 (중복 제거)
# - 거절: 설정의 재정렬 점수 기준 (점수가 낮으면 LLM을 부르지 않고 거절)
# - 생성: 설정의 모델 (+ DPO LoRA가 고른 경우), 설정의 프롬프트
# - **한국어 질문**은 영어로 번역해 검색 → 답을 한국어로
# - 재정렬 점수 때문에 거절될 때만 **질문을 고쳐(철자·구어 → 의학 용어) 한 번 더 검색** (도메인 판정은 정답 손실이 커서 꺼 둠, 4번 셀에 근거)
# - 챗봇을 켜기 전에 **데모 질문을 자동으로 돌려** 결과를 `final/chatbot_test.jsonl`에 저장
# - 마지막 셀 출력의 `https://xxxx.gradio.live` 링크로 접속. **셀이 돌고 있는 동안만** 열려 있고, 끝내려면 ■(중지)


# ## 1. 설치 + 드라이브 + 최종 설정

# !pip -q install -U sentence-transformers faiss-cpu peft gradio
# !pip -q uninstall -y torchao   # 최신 peft가 Colab 기본 torchao(0.10)와 충돌해서 제거

import os, json
from google.colab import drive
drive.mount('/content/drive')
SAVE_DIR  = '/content/drive/MyDrive/rag_msmarco/health'
FINAL_DIR = f'{SAVE_DIR}/final'
CFG = json.load(open(f'{FINAL_DIR}/final_config.json'))
for k, v in CFG.items():
    if k != 'system_prompt':
        print(f'{k:18s} {v}')


# ## 2. 검색기

import re, time
from collections import Counter
from urllib.parse import urlparse
import numpy as np
import torch, faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
assert torch.cuda.is_available(), 'GPU 런타임이 아닙니다 (A100 권장).'

def load_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]

K, TOP_N = 100, CFG['top_n']
corpus = load_jsonl(f'{SAVE_DIR}/corpus.jsonl')
texts  = [c['text'] for c in corpus]
index  = faiss.read_index(f'{SAVE_DIR}/faiss_bge_flatip.index')
emb    = SentenceTransformer('BAAI/bge-base-en-v1.5', device='cuda').half()

def ce_load(name, max_len):
    # 11·18과 같이 원래 점수(활성화 함수 없음): 거절 기준 단위를 맞추기 위해
    try:
        m = CrossEncoder(name, max_length=max_len, device='cuda', activation_fn=torch.nn.Identity())
    except TypeError:
        m = CrossEncoder(name, max_length=max_len, device='cuda', default_activation_function=torch.nn.Identity())
    m.model.half()
    return m
RR = {n: ce_load(n, 256 if 'MiniLM' in n else 512)
      for n in dict.fromkeys(CFG['rerankers'] + ([CFG['refusal_signal']] if CFG['refusal_signal'] else []))}

TIERS = {
    '공공기관':   ['medlineplus.gov', 'cdc.gov', 'nih.gov', 'nhs.uk', 'who.int', 'fda.gov', 'cancer.gov'],
    '병원·학회':  ['mayoclinic.org', 'clevelandclinic.org', 'hopkinsmedicine.org', 'aafp.org', 'merckmanuals.com',
                  'kidshealth.org', 'health.harvard.edu', 'heart.org', 'cancer.org', 'familydoctor.org', 'uptodate.com'],
    '상업 매체':  ['webmd.com', 'healthline.com', 'verywell.com', 'medicinenet.com', 'everydayhealth.com', 'drugs.com',
                  'rxlist.com', 'emedicinehealth.com', 'medscape.com', 'medicalnewstoday.com', 'rightdiagnosis.com',
                  'patient.info', 'labtestsonline.org'],
    '커뮤니티·생활': ['healthtap.com', 'sharecare.com', 'livestrong.com', 'babycenter.com', 'psychologytoday.com'],
    '사전':       ['thefreedictionary.com'],
}
def site_of(url):
    h = urlparse(url).netloc.lower()
    return h[4:] if h.startswith('www.') else h
def tier_of(site):
    for tier, ss in TIERS.items():
        if any(site == s or site.endswith('.' + s) for s in ss):
            return tier
    return '기타'
sites = [site_of(c['url']) for c in corpus]
norm_text = lambda t: ' '.join(t.lower().split())
zs = lambda m: (m - m.mean()) / (m.std() + 1e-6)

def retrieve(q):
    qe = emb.encode(['Represent this sentence for searching relevant passages: ' + q], normalize_embeddings=True,
                    convert_to_numpy=True).astype('float32')
    _, ids = index.search(qe, K); cands = ids[0].tolist()
    pairs = [(q, texts[p]) for p in cands]
    raw = {n: m.predict(pairs, batch_size=128) for n, m in RR.items()}
    order = sum(zs(raw[n]) for n in CFG['rerankers']) / len(CFG['rerankers'])
    signal = float(raw[CFG['refusal_signal']].max()) if CFG['refusal_signal'] else None
    docs, seen = [], set()
    for i in np.argsort(-order):
        p = cands[i]; key = norm_text(texts[p])
        if key in seen:
            continue
        seen.add(key)
        docs.append({'pid': p, 'site': sites[p], 'tier': tier_of(sites[p]), 'url': corpus[p]['url'], 'text': texts[p],
                     'score': float(order[i])})
        if len(docs) == TOP_N:
            break
    return docs, signal
print(f'문단 {len(texts):,} / 재정렬 {list(RR)} / 상위 {TOP_N}')


# ## 3. LLM

from transformers import AutoTokenizer, AutoModelForCausalLM
tok = AutoTokenizer.from_pretrained(CFG['generator'], padding_side='left')
llm = AutoModelForCausalLM.from_pretrained(CFG['generator'], dtype=torch.bfloat16, device_map='cuda')
if CFG['adapter']:
    from peft import PeftModel
    llm = PeftModel.from_pretrained(llm, '/content/drive/MyDrive/' + CFG['adapter'])
llm.eval()
REFUSAL = "Sorry, I can't answer that from the medical documents I have."
SYS = CFG['system_prompt']
def is_refusal(a):
    a = a.lower()
    return any(p in a for p in ["can't answer", 'cannot answer', 'unable to answer'])

@torch.inference_mode()
def generate(q, docs):
    ctx = '\n'.join(f'[{i}] ({d["site"]}) {d["text"]}' for i, d in enumerate(docs, 1))
    msgs = [{'role': 'system', 'content': SYS}, {'role': 'user', 'content': f'Documents:\n{ctx}\n\nQuestion: {q}'}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    enc = tok(prompt, return_tensors='pt').to(llm.device)
    out = llm.generate(**enc, max_new_tokens=256, do_sample=False, temperature=None, top_p=None, top_k=None,
                       pad_token_id=tok.pad_token_id or tok.eos_token_id)
    a = tok.decode(out[0, enc['input_ids'].shape[1]:], skip_special_tokens=True)
    return re.sub(r'<think>.*?</think>', '', a, flags=re.S).strip()

from contextlib import nullcontext
DOMAIN_GATE = False   # True면 답하기 전에 "건강·의학 질문인가?" 판정. 시험에서 정답 72개(.770→.626)를 잃어서 끔 (4번 셀 참고)
GATE_TH     = 0.5
KO_REFUSAL  = '죄송해요, 가지고 있는 의료 문서로는 답할 수 없어요.'
YES_ID = tok.encode('Yes', add_special_tokens=False)[0]
NO_ID  = tok.encode('No', add_special_tokens=False)[0]
SYS_GATE = ('You decide whether a user question is about health or medicine: diseases, symptoms, treatments, drugs, '
            'vaccines, the human body, nutrition, fitness, mental health, pregnancy, or medical tests. '
            'Answer with Yes or No only.')

def base_ctx():
    return llm.disable_adapter() if CFG['adapter'] else nullcontext()

@torch.inference_mode()
def p_health(questions, bs=32):
    out = []
    with base_ctx():
        for i in range(0, len(questions), bs):
            prompts = [tok.apply_chat_template([{'role': 'system', 'content': SYS_GATE}, {'role': 'user', 'content': q}],
                                               tokenize=False, add_generation_prompt=True, enable_thinking=False)
                       for q in questions[i:i + bs]]
            enc = tok(prompts, return_tensors='pt', padding=True).to(llm.device)
            lg = llm(**enc).logits[:, -1, [YES_ID, NO_ID]].float()
            out += torch.softmax(lg, -1)[:, 0].tolist()
    return out

@torch.inference_mode()
def translate(text, lang):
    msgs = [{'role': 'system', 'content': f'Translate the user text into {lang}. Keep citation markers like [1] or [2][4] unchanged. '
                                          'Output only the translation.'},
            {'role': 'user', 'content': text}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    enc = tok(prompt, return_tensors='pt').to(llm.device)
    with base_ctx():
        out = llm.generate(**enc, max_new_tokens=300, do_sample=False, temperature=None, top_p=None, top_k=None,
                           pad_token_id=tok.pad_token_id or tok.eos_token_id)
    a = tok.decode(out[0, enc['input_ids'].shape[1]:], skip_special_tokens=True)
    return re.sub(r'<think>.*?</think>', '', a, flags=re.S).strip()

RETRY_FIX = False  # B안(11/03 결정): 발표 기준 = 재검색 없음(오전 챗봇 DPO v1·A). True로 바꾸면 점수 때문에 거절될 때 질문을 고쳐 한 번 더 검색(오타 대응)
SYS_FIX = ('Rewrite the user question as a clear English health search query. Fix spelling mistakes and replace casual '
           'phrases with standard medical terms when obvious (e.g. "sympton" -> "symptoms", "shot after rusty nail" -> '
           '"tetanus shot after stepping on a rusty nail"). Do not answer it. Output only the rewritten question.')

@torch.inference_mode()
def rewrite_query(q):
    msgs = [{'role': 'system', 'content': SYS_FIX}, {'role': 'user', 'content': q}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    enc = tok(prompt, return_tensors='pt').to(llm.device)
    with base_ctx():
        out = llm.generate(**enc, max_new_tokens=60, do_sample=False, temperature=None, top_p=None, top_k=None,
                           pad_token_id=tok.pad_token_id or tok.eos_token_id)
    a = tok.decode(out[0, enc['input_ids'].shape[1]:], skip_special_tokens=True)
    return re.sub(r'<think>.*?</think>', '', a, flags=re.S).strip().split('\n')[0].strip('" ')

def answer_one(q):
    # 반환: (답, 문단, LLM 답변 여부, 거절 점수, 걸린 초, 부가 정보)
    t = time.time()
    ko = bool(re.search('[가-힣]', q))
    q_en = translate(q, 'English') if ko else q
    info = {'ko': ko, 'q_en': q_en, 'gate': None, 'why': None, 'ans_en': None}
    docs, signal = retrieve(q_en)
    if DOMAIN_GATE:
        info['gate'] = p_health([q_en])[0]
        if info['gate'] < GATE_TH:
            info['why'] = 'domain'
    if info['why'] is None and CFG['refusal_threshold'] is not None and signal < CFG['refusal_threshold'] and RETRY_FIX:
        # 점수 때문에 거절될 때만: 철자·구어 표현을 고친 질문으로 한 번 더 검색 (예: 'sympton' → 'symptoms')
        fixed = rewrite_query(q_en)
        if fixed.lower().strip(' ?.') != q_en.lower().strip(' ?.'):
            docs2, signal2 = retrieve(fixed)
            info['q_fixed'] = fixed
            # 20번 결과: 고친 질문은 더 높은 기준(6.0)을 넘어야 씀 → 오타 질문 정답률 .148 → .622, 답 없는 질문 안전성 손실 작게
            if signal2 >= CFG.get('retry_threshold', CFG['refusal_threshold']):
                docs, signal, q_en = docs2, signal2, fixed
                info['q_en'] = fixed
                info['retry_ok'] = True
    if info['why'] is None and CFG['refusal_threshold'] is not None and signal < CFG['refusal_threshold'] and not info.get('retry_ok'):
        info['why'] = 'score'
    if info['why']:
        return (KO_REFUSAL if ko else REFUSAL), docs, False, signal, time.time() - t, info
    a = generate(q_en, docs)
    info['ans_en'] = a
    if ko:
        a = KO_REFUSAL if is_refusal(a) else translate(a, 'Korean')
    return a, docs, not is_refusal(info['ans_en']), signal, time.time() - t, info
print('LLM:', CFG['generator'], '+ DPO LoRA' if CFG['adapter'] else '', f'/ GPU {torch.cuda.memory_allocated() / 1e9:.1f}GB')


# ## 4. 도메인 판정 점검 (시험 650: 건강 600 + 분야 밖 50) — 결과: 정답 손실이 커서 챗봇에서는 끔

ev = load_jsonl(f'{SAVE_DIR}/eval.jsonl')
ph = p_health([q['query'] for q in ev])
health = [p for q, p in zip(ev, ph) if q['domain'] == 'health']; other = [p for q, p in zip(ev, ph) if q['domain'] != 'health']
for th in (0.3, 0.5, 0.7):
    print(f'기준 {th}: 건강 질문 잘못 거절 {np.mean([p < th for p in health]):.3f} / 분야 밖 거절 {np.mean([p < th for p in other]):.3f}')
miss = sorted([(p, q['query']) for q, p in zip(ev, ph) if q['domain'] == 'health' and p < GATE_TH])[:10]
print('건강인데 분야 밖으로 판정된 예:', *miss, sep='\\n  ')

# MS MARCO '건강' 라벨은 문단 출처 사이트로 붙인 것이라 의료가 아닌 질문도 섞여 있음 → 실제 손해는 '정답을 맞혔던 질문을 몇 개 잃나'로 봄
import hashlib
jc = {j['key']: j['v'] for j in load_jsonl(f'{SAVE_DIR}/judge_eval/judgments.jsonl')}
dpo = {d['qid']: d['ans'] for d in load_jsonl(f'{SAVE_DIR}/dpo/answers.jsonl') if d['set'] == 'test'}
KEY = 'E10|Qwen3-8B+DPO'
A = [(q, p) for q, p in zip(ev, ph) if q['domain'] == 'health' and q.get('answerable', True) and q.get('gold_pids')]
def correct(q):
    a = dpo.get(str(q['qid']), {}).get(KEY)
    return a is not None and not is_refusal(a) and jc.get(hashlib.md5(f"c|{q['query']}|{a}".encode()).hexdigest(), 0) >= 1.5
acc0 = np.mean([correct(q) for q, _ in A])
gate_rows = {}
for th in (0.1, 0.3, 0.5):
    acc = np.mean([correct(q) and p >= th for q, p in A])
    gate_rows[th] = {'정답률 (판정 없음)': acc0, '정답률 (판정 있음)': acc, '잃은 정답 (개)': int(round((acc0 - acc) * len(A))),
                     '분야 밖 거절률': np.mean([p < th for p in other])}
import pandas as pd
gtab = pd.DataFrame(gate_rows).T.round(3); display(gtab)
lost = [q['query'] for q, p in A if p < GATE_TH and correct(q)]
print(f'판정 때문에 잃는 정답 질문 {len(lost)}개:', *lost[:15], sep='\n  ')
json.dump({'gate_th': GATE_TH, 'health_label_refusal': float(np.mean([p < GATE_TH for p in health])),
           'other_refusal': float(np.mean([p < GATE_TH for p in other])), 'acc_no_gate': float(acc0),
           'acc_gate': float(gate_rows[GATE_TH]['정답률 (판정 있음)']), 'lost_correct': lost,
           'table': {str(k): v for k, v in gate_rows.items()}}, open(f'{FINAL_DIR}/domain_gate_eval.json', 'w'), ensure_ascii=False, indent=1)


# ## 5. 데모 질문 자동 테스트 (결과 `final/chatbot_test.jsonl`)

DEMO = [  # 일상 표현 → 병명 (팀 데모 질문)
    ('why does my face turn red and itchy after drinking alcohol', 'alcohol intolerance / flush'),
    ('what is it called when your blood sugar is too high all the time', 'diabetes / hyperglycemia'),
    ('the pill doctors give to thin your blood after a heart attack', 'aspirin / antiplatelet'),
    ('condition where you stop breathing for a few seconds while sleeping', 'sleep apnea'),
    ('when the butterfly shaped gland in your neck is too slow', 'hypothyroidism'),
    ('the bacteria that causes stomach ulcers', 'H. pylori'),
    ("ringing sound in ears that won't go away", 'tinnitus'),
    ('bone disease where bones become weak and break easily in old women', 'osteoporosis'),
    ('virus that causes cold sores around the mouth', 'herpes simplex (HSV-1)'),
    ('shot you get after stepping on a rusty nail', 'tetanus'),
    # 거절해야 하는 질문 (분야 밖)
    ('what is the capital of australia', '(거절)'),
    ('how do i make kimchi', '(거절)'),
    # 한국어 (DB가 영어라 한계 확인용)
    ('술 마시면 얼굴이 빨개지는 이유가 뭐야?', '알코올 불내증'),
    ('위궤양을 일으키는 세균이 뭐야?', '헬리코박터 파일로리'),
    # 오타 (점수 거절 → 질문 고쳐서 재검색)
    ('what are the sympton of influenza', 'fever, cough, aches'),
    ('녹슨 못을 밟으면 무슨 주사를 맞아야 해?', '파상풍 주사'),
]
rows = []
for q, expect in DEMO:
    a, docs, used, sig, sec, info = answer_one(q)
    rows.append({'question': q, 'expect': expect, 'answer': a, 'answered': used, 'why': info['why'], 'gate': info['gate'],
                 'q_en': info['q_en'], 'q_fixed': info.get('q_fixed'), 'signal': sig, 'sec': round(sec, 1), 'sources': [f"{d['site']}" for d in docs[:3]]})
    print(f"Q: {q}{'  → ' + info['q_en'] if info['ko'] else ''}\n   기대: {expect} | {'답변' if used else '거절(' + str(info['why'] or 'LLM') + ')'} | "
          f"{sec:.1f}초 | 건강 판정 {info['gate'] and round(info['gate'], 2)} | 점수 {sig if sig is None else round(sig, 2)}\n   A: {a[:300]}\n")
with open(f'{FINAL_DIR}/chatbot_test.jsonl', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('저장:', f'{FINAL_DIR}/chatbot_test.jsonl')


# ## 6. 챗봇 실행 (링크가 나오면 접속)

import gradio as gr
def sources_md(docs, used, sig, sec, info):
    head = f'**근거 문단 상위 {len(docs)}개** · {sec:.1f}초'
    if info.get('q_fixed'):
        head += f'\n\n🔧 질문을 고쳐서 다시 검색: *{info["q_fixed"]}*'
    if info['ko']:
        head += f'\n\n🔤 영어로 검색: *{info["q_en"]}*'
        if info['ans_en']:
            head += f'\n\n영어 원문 답변: {info["ans_en"]}'
    if info['why'] == 'domain':
        head += f'\n\n⚠️ 건강·의학 질문이 아니라고 판정 (P={info["gate"]:.2f}) → 답하지 않았어요.'
    elif info['why'] == 'score':
        head += f'\n\n⚠️ 재정렬 점수 {sig:.2f} < 기준 {CFG["refusal_threshold"]:.2f} → 관련 문서가 없다고 보고 답하지 않았어요.'
    parts = [head] + [f'**[{i}] {d["tier"]}** · `{d["site"]}`\n\n> {d["text"]}\n\n[{d["url"]}]({d["url"]})'
                      for i, d in enumerate(docs, 1)]
    return '\n\n---\n\n'.join(parts)

def chat(message, history):
    message = (message or '').strip()
    if not message:
        return '', history, ''
    a, docs, used, sig, sec, info = answer_one(message)
    with open(f'{FINAL_DIR}/chat_log.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps({'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 9 * 3600)),
                            'question': message, 'answer': a, 'answered': used, 'signal': sig, 'why': info['why'], 'q_en': info['q_en'],
                            'docs': [{k: d[k] for k in ('pid', 'site', 'tier')} for d in docs]}, ensure_ascii=False) + '\n')
    history = history + [{'role': 'user', 'content': message}, {'role': 'assistant', 'content': a}]
    return '', history, sources_md(docs, used, sig, sec, info)

label = CFG['generator'].split('/')[-1] + (' + DPO' if CFG['adapter'] else '')
with gr.Blocks(title='의료 QA 챗봇 (최종, v2.1)') as demo:
    gr.Markdown(f'## 의료 QA 챗봇 · 최종 (v2.1)\nMS MARCO 건강 문단 46만 개에서 근거를 찾아 답합니다 ({label}, 검색 {CFG["retrieval"]}). '
                '영어 질문을 권장하지만 **한국어도 됩니다** (영어로 번역해서 검색 → 답을 한국어로 번역).')
    with gr.Row():
        with gr.Column(scale=3):
            try:
                bot = gr.Chatbot(type='messages', height=480, label='대화')
            except TypeError:
                bot = gr.Chatbot(height=480, label='대화')
            box = gr.Textbox(placeholder='e.g. the bacteria that causes stomach ulcers', label='질문', autofocus=True)
            gr.Examples([q for q, _ in DEMO[:10]], inputs=box)
            clear = gr.Button('대화 지우기')
        with gr.Column(scale=2):
            src = gr.Markdown('질문하면 근거 문단이 여기에 나옵니다.')
    gr.Markdown('<small>⚠️ 데모용입니다. 의료 조언이 아니며, 문서는 2016년 무렵 자료라 최신 정보와 다를 수 있습니다.</small>')
    box.submit(chat, [box, bot], [box, bot, src])
    clear.click(lambda: ([], '질문하면 근거 문단이 여기에 나옵니다.'), None, [bot, src])

demo.queue().launch(share=True, prevent_thread_lock=True)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    demo.close()
    print('챗봇을 닫았습니다. 대화 기록:', f'{FINAL_DIR}/chat_log.jsonl')


# ## 7. 끝내기 (■ 중지 후 실행)

from google.colab import drive, runtime
drive.flush_and_unmount()
runtime.unassign()
