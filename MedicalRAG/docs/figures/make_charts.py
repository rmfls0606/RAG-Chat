# 발표 자료(presentation_final_pipeline.md) 지표 그래프 생성. 숫자는 docs/·results/ 요약 문서에서 옮김.
# 실행: python3 MedicalRAG/docs/figures/make_charts.py  → 같은 폴더에 PNG 저장
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).parent
BLUE, ORANGE, GRAY = '#2a78d6', '#eb6834', '#c3c2b7'
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e8e7e3', '#fcfcfb'
plt.rcParams.update({
    'font.family': 'Apple SD Gothic Neo', 'font.size': 13, 'axes.unicode_minus': False,
    'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID,
    'axes.axisbelow': True, 'axes.titlesize': 16, 'axes.titleweight': 'bold', 'axes.titlecolor': INK,
    'axes.titlelocation': 'left', 'axes.titlepad': 14,
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)


def hbar(ax, labels, vals, colors, fmt='{:.3f}'):
    y = range(len(labels))[::-1]
    ax.barh(list(y), vals, color=colors, height=0.6)
    ax.set_yticks(list(y), labels)
    ax.grid(axis='y', visible=False)
    for yi, v in zip(y, vals):
        ax.text(v + 0.01, yi, fmt.format(v).lstrip('0'), va='center', color=INK, fontsize=12)


# 1. 개선 흐름 (시험 정답률, 답 있는 건강 500)
fig, ax = plt.subplots(figsize=(10, 5))
labels = ['B0 · LLM만', '08 · 첫 RAG', '06 · 문장형 LoRA', '15 · SFT 재학습', '16 · 앙상블 Top-10 + Qwen3-8B', '17 · + DPO (최종)']
vals = [.618, .736, .450, .724, .782, .770]
hbar(ax, labels, vals, [GRAY, GRAY, GRAY, GRAY, GRAY, BLUE])
ax.set_xlim(0, 1)
ax.set_xlabel('시험 정답률 (LLM 심판 2점 비율)')
ax.set_title('단계별 시험 정답률')
save(fig, '01_progress.png')

# 2. 검색 지표 (시험 500): R@10, MRR@10
fig, ax = plt.subplots(figsize=(10, 5))
methods = ['BM25', 'bge-base + FAISS', '+ MiniLM 재정렬', '+ bge 앙상블 재정렬 (최종)']
r10, mrr = [.406, .688, .758, .776], [.202, .401, .445, .474]
x = range(len(methods))
w = 0.36
b1 = ax.bar([i - w / 2 - 0.01 for i in x], r10, w, color=BLUE, label='Recall@10')
b2 = ax.bar([i + w / 2 + 0.01 for i in x], mrr, w, color=ORANGE, label='MRR@10')
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.015, f'{b.get_height():.3f}'.lstrip('0'),
                ha='center', color=INK, fontsize=11)
ax.set_xticks(list(x), methods)
ax.set_ylim(0, 1)
ax.grid(axis='x', visible=False)
ax.legend(frameon=False, loc='upper left')
ax.set_title('검색 단계 지표 (시험 500)')
save(fig, '02_retrieval.png')

# 3. 생성 모델: 08 대비 정답률 차이 + 95% 부트스트랩 CI
fig, ax = plt.subplots(figsize=(10, 4.5))
models = ['Qwen2.5-7B', 'Qwen2.5-14B', 'Qwen3-8B (채택)', 'Qwen3-14B']
diff = [.4, 2.4, 4.6, 5.4]
lo, hi = [-3.2, -1.2, .8, 1.8], [4.2, 6.0, 8.2, 8.8]
y = list(range(len(models)))[::-1]
for yi, d, l, h, m in zip(y, diff, lo, hi, models):
    c = BLUE if l > 0 else GRAY
    ax.plot([l, h], [yi, yi], color=c, lw=2, solid_capstyle='round')
    ax.plot(d, yi, 'o', ms=10, color=c, mec=SURF, mew=2)
    ax.text(h + 0.3, yi, f'{d:+.1f}점  [{l:+.1f}, {h:+.1f}]', va='center', color=INK, fontsize=12)
ax.axvline(0, color=INK2, lw=1)
ax.set_yticks(y, models)
ax.set_xlim(-5, 13)
ax.grid(axis='y', visible=False)
ax.set_xlabel('08 첫 RAG 대비 시험 정답률 차이 (점, 95% CI)')
ax.set_title('생성 모델 교체 효과 — CI가 0을 넘는 것만 유의')
save(fig, '03_generator_ci.png')

# 4. DPO 전후 (시험 650)
fig, ax = plt.subplots(figsize=(10, 5))
metrics = ['진짜 답 없음\n거절률', '근거 충실도', '정답률', '잘못 거절']
before, after = [.652, .919, .782, .046], [.804, .933, .770, .078]
x = range(len(metrics))
b1 = ax.bar([i - w / 2 - 0.01 for i in x], before, w, color=GRAY, label='Qwen3-8B')
b2 = ax.bar([i + w / 2 + 0.01 for i in x], after, w, color=BLUE, label='+ DPO')
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.015, f'{b.get_height():.3f}'.lstrip('0'),
                ha='center', color=INK, fontsize=11)
ax.set_xticks(list(x), metrics)
ax.set_ylim(0, 1.08)
ax.grid(axis='x', visible=False)
ax.legend(frameon=False, loc='upper right', ncol=2)
ax.set_title('DPO 전후 (시험 650) — 거절률↑, 정답률 유지(차이 유의하지 않음)')
save(fig, '04_dpo.png')

# 5. 안전성 vs 정답률 교환
fig, ax = plt.subplots(figsize=(10, 5.5))
pts = [('Qwen3-8B (기준 4.92)', .782, .652, GRAY, (10, -18)),
       ('검색 기준만 올림 (6.80)', .678, .826, GRAY, (10, -4)),
       ('DPO만 (검색 거절 없음)', .782, .587, GRAY, (10, -4)),
       ('검색 4.92 + DPO (최종)', .770, .804, BLUE, (-12, 10))]
for name, acc, ref, c, off in pts:
    ax.plot(acc, ref, 'o', ms=13, color=c, mec=SURF, mew=2)
    ax.annotate(f'{name}\n정답 {acc:.3f}'.replace('0.', '.') + f' · 거절 {ref:.3f}'.replace('0.', '.'),
                (acc, ref), xytext=off, textcoords='offset points', color=INK, fontsize=11,
                ha='right' if off[0] < 0 else 'left')
ax.set_xlim(.65, .82)
ax.set_ylim(.55, .87)
ax.set_xlabel('정답률 (답 있는 500) →')
ax.set_ylabel('진짜 답 없음 거절률 →')
ax.set_title('안전성과 정답률 — 오른쪽 위가 좋음')
save(fig, '05_tradeoff.png')

# 6. F1 vs 심판 정답률: 같은 두 시스템, 지표에 따라 순위가 뒤집힘 (지표별 패널, 축 따로)
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
systems = ['08 RAG', '06 RAG + LoRA']
for ax, (title, vals) in zip(axes, [('F1 (단어 겹침)', [.282, .349]), ('심판 정답률', [.736, .450])]):
    best = max(vals)
    ax.bar(systems, vals, width=0.55, color=[BLUE if v == best else GRAY for v in vals])
    for i, v in enumerate(vals):
        ax.text(i, v + 0.015, f'{v:.3f}'.lstrip('0'), ha='center', color=INK, fontsize=12)
    ax.set_ylim(0, 0.85)
    ax.grid(axis='x', visible=False)
    ax.set_title(title, fontsize=14)
fig.suptitle('F1로는 LoRA가 1등, 심판으로는 꼴찌', x=0.02, ha='left', fontsize=16, fontweight='bold', color=INK)
save(fig, '06_f1_vs_judge.png')

# 7. 교차 심판: Qwen 심판 vs Phi-4 심판 (검증 정답률) — 순위가 같음 (16번은 검증 순위로 고름)
fig, ax = plt.subplots(figsize=(10, 5.5))
sys5 = ['08 · MiniLM Top-5 + Qwen2.5-7B', 'Top-10 + Qwen2.5-7B', 'Top-10 + Qwen2.5-14B', 'Top-10 + Qwen3-8B', 'Top-10 + Qwen3-14B']
qwen = [.690, .725, .735, .795, .795]
phi = [.765, .785, .825, .840, .840]
y = list(range(len(sys5)))[::-1]
h = 0.36
ax.barh([yi + h / 2 + 0.01 for yi in y], qwen, h, color=BLUE, label='Qwen2.5-14B 심판')
ax.barh([yi - h / 2 - 0.01 for yi in y], phi, h, color=ORANGE, label='Phi-4 심판')
for yi, a, b in zip(y, qwen, phi):
    ax.text(a + 0.005, yi + h / 2 + 0.01, f'{a:.3f}'.lstrip('0'), va='center', color=INK, fontsize=11)
    ax.text(b + 0.005, yi - h / 2 - 0.01, f'{b:.3f}'.lstrip('0'), va='center', color=INK, fontsize=11)
ax.set_yticks(y, sys5)
ax.set_xlim(0, 1)
ax.grid(axis='y', visible=False)
ax.legend(frameon=False, loc='lower left', bbox_to_anchor=(0, 1.0), ncol=2)
ax.set_xlabel('검증 정답률')
ax.set_title('다른 계열 심판으로 다시 채점해도 순위 동일', pad=40)
save(fig, '07_cross_judge.png')
# 8. 심판이 점수를 매기는 과정 (흐름도, 질문·참고 정답은 실제 데이터, 챗봇 답·확률 값은 설명용 예시)
from matplotlib.patches import FancyBboxPatch
LIGHT = '#eef4fc'
fig, ax = plt.subplots(figsize=(13, 5.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 5.2)
ax.axis('off')


def box(x, y, w, h, title, body, fill=SURF, edge=GRID):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=fill, ec=edge, lw=2))
    ax.text(x + 0.2, y + h - 0.3, title, fontsize=19, fontweight='bold', color=INK, va='top')
    ax.text(x + 0.2, y + h - 1.0, body, fontsize=17, color=INK2, va='top', linespacing=1.5)


def arrow(x1, x2, y):
    ax.annotate('', (x2, y), (x1, y), arrowprops=dict(arrowstyle='-|>', color=INK2, lw=2, mutation_scale=22))


box(0.05, 0.55, 3.0, 4.0, '① 입력', '질문\n  bacteria in kidney\n  infection?\n참고 정답\n  E.coli bacteria\n챗봇 답\n  usually E. coli [1]')
arrow(3.1, 3.5, 2.55)
box(3.55, 0.55, 2.95, 4.0, '② 심판 14B', '기준표\n2 = 핵심 사실 맞음\n1 = 일부만 맞음\n0 = 틀림 / 무관\n\n숫자 하나로만 답하게', fill=LIGHT, edge=BLUE)
arrow(6.55, 6.95, 2.55)
box(7.0, 0.55, 2.75, 4.0, '③ 첫 토큰 확률', '0·1·2가 나올\n확률만 읽음')
for i, pv in enumerate([.03, .12, .85]):
    yy = 2.45 - i * 0.62
    ax.text(7.25, yy, f'{i}', fontsize=18, color=INK, va='center')
    ax.add_patch(FancyBboxPatch((7.6, yy - 0.18), 1.45 * pv + 0.02, 0.36, boxstyle='round,pad=0,rounding_size=0.05',
                                fc=BLUE if i == 2 else GRAY, ec='none'))
    ax.text(7.66 + 1.45 * pv + 0.08, yy, f'{pv:.2f}'.lstrip('0'), fontsize=16, color=INK, va='center')
arrow(9.8, 10.2, 2.55)
box(10.25, 0.55, 2.7, 4.0, '④ 판정', 'P(1) + 2×P(2)\n= .12 + 2×.85\n= 1.82\n\n1.5 이상 → 정답')
ax.text(0.05, 4.85, '심판이 정답 점수를 매기는 과정', fontsize=21, fontweight='bold', color=INK)
ax.text(0.05, 0.12, '근거 충실도도 같은 방식 (문단 + 챗봇 답 → P(1)) · 챗봇 답과 확률 값은 설명용 예시', fontsize=15, color=INK2)
save(fig, '08_judge_flow.png')

# 9. 심판 vs 사람 (40개) 혼동 행렬
from matplotlib.colors import LinearSegmentedColormap
conf = [[4, 3, 0], [2, 7, 0], [0, 12, 12]]   # 행 = 사람 0/1/2, 열 = 심판 0/1/2
cmap = LinearSegmentedColormap.from_list('seq', ['#f4f8fd', '#86b6ef', '#1c5cab'])
fig, ax = plt.subplots(figsize=(7.5, 6))
ax.imshow(conf, cmap=cmap, vmin=0, vmax=12)
names = ['0 오답', '1 부분', '2 정답']
ax.set_xticks(range(3), names)
ax.set_yticks(range(3), names)
ax.xaxis.set_ticks_position('top')
ax.xaxis.set_label_position('top')
ax.set_xlabel('심판 판정', fontsize=13, labelpad=10)
ax.set_ylabel('사람 판정', fontsize=13)
ax.grid(False)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.set_xticks([0.5, 1.5], minor=True)
ax.set_yticks([0.5, 1.5], minor=True)
ax.grid(which='minor', color=SURF, lw=3)
ax.tick_params(which='both', length=0)
for r in range(3):
    for c in range(3):
        v = conf[r][c]
        ax.text(c, r, v, ha='center', va='center', fontsize=20, fontweight='bold', color=SURF if v >= 7 else INK)
ax.set_title('심판 vs 사람 40개 — 심판이 정답이라 한 12개는 모두 사람도 정답', fontsize=14, pad=50)
save(fig, '09_judge_vs_human.png')
print('saved to', OUT)
