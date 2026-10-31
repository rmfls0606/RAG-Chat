"""의료 정보 RAG 챗봇 웹 화면 (Gradio).

실행 (RAG-Chat 폴더에서):
    .venv/bin/python App/app.py                      # 원본 Qwen (Ollama)
    .venv/bin/python App/app.py --generator mlx \
        --adapter models/qwen2.5-7b-instruct-rag-lora   # LoRA Qwen (MLX)
브라우저에서 http://127.0.0.1:7860 접속. --share를 붙이면 외부 공유 링크도 만듦.
"""
import argparse

import gradio as gr

from rag_chat import MedicalRAG

STATUS_TEXT = {
    "supported": "✅ 답변 내용이 인용한 문서에서 확인됨",
    "unsupported": "⚠️ 답변 일부가 인용한 문서에서 확인되지 않음",
    "invalid_citation": "⚠️ 잘못된 근거 번호가 있음",
    "no_citation": "⚠️ 근거 번호 없음",
    "refused": "문서에 답이 없어 답하지 않음",
    "low_score": "관련 의료 문서를 찾지 못해 답하지 않음",
}

parser = argparse.ArgumentParser()
parser.add_argument("--generator", choices=["ollama", "mlx"], default="ollama")
parser.add_argument("--adapter", default=None, help="MLX LoRA 어댑터 폴더")
parser.add_argument("--share", action="store_true")
args = parser.parse_args()

rag = MedicalRAG(generator=args.generator, adapter_path=args.adapter)


def respond(message, history):
    r = rag.ask(message)
    lines = [r["answer"], "", f"_{STATUS_TEXT[r['status']]}_ (관련도 {r['top_score']:.2f} / 기준 {r['threshold']:.2f})"]
    if r["sources"]:
        # MS MARCO는 2016~2017년 수집이라 원문 페이지가 지금은 없을 수 있음 → Internet Archive의 사본도 함께 표시 (원문 사이트와 무관한 비공식 사본)
        lines += ["", "**근거 문서** (원문 링크는 수집 당시 주소라 지금은 없을 수 있습니다. "
                      "웹 아카이브 사본은 Internet Archive가 저장한 비공식 사본입니다)"]
        for s in r["sources"]:
            lines.append(f"- **[{s['n']}]** [원문]({s['url']}) · [웹 아카이브 사본(2017, 비공식)](https://web.archive.org/web/2017/{s['url']})\n"
                         f"  > {s['text'][:300]}{'...' if len(s['text']) > 300 else ''}")
    return "\n".join(lines)


gr.ChatInterface(
    respond,
    title="의료 정보 RAG 챗봇",
    description=(f"MS MARCO 의료 사이트 문서 {len(rag.passages):,}개에서 근거를 찾아 답합니다 (생성: {rag.model_name}). "
                 "영어로 질문하세요. 의료 정보 참고용이며 진단·치료를 대신하지 않습니다. "
                 "문서는 2016~2017년 자료입니다. 최신 의료 정보는 해당 기관 사이트나 의료진에게 확인하세요."),
    examples=["What are the symptoms of iron deficiency anemia?", "What causes your hands to shake?",
              "what is treatment for jaundice", "Who won the 2010 FIFA World Cup?"],
).launch(share=args.share)
