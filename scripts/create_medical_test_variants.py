from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


SOURCE = Path("data/derived/medical_test_350.parquet")
OUTPUT = Path("data/derived/medical_test_350_expanded.parquet")

LABELS = ["원본", "구어체", "쉬운 말", "핵심 단어 회피"]

PLAIN_TERMS = [
    (r"\bmyocardial infarction\b", "heart attack"),
    (r"\bhypertension\b", "high blood pressure"),
    (r"\bhypotension\b", "low blood pressure"),
    (r"\bhypoglycemia\b", "low blood sugar"),
    (r"\bhyperglycemia\b", "high blood sugar"),
    (r"\bdyspnea\b", "trouble breathing"),
    (r"\bedema\b", "swelling"),
    (r"\bmyocardial\b", "heart muscle"),
    (r"\bcardiac\b", "heart"),
    (r"\bcardiovascular\b", "heart and blood vessel"),
    (r"\bcerebral\b", "brain"),
    (r"\brenal\b", "kidney"),
    (r"\bhepatic\b", "liver"),
    (r"\bpulmonary\b", "lung"),
    (r"\bneoplasm\b", "tumor"),
    (r"\bcarcinoma\b", "cancer"),
    (r"\bmalignancy\b", "cancer"),
    (r"\bbenign\b", "noncancerous"),
    (r"\bmalignant\b", "cancerous"),
    (r"\basymptomatic\b", "without symptoms"),
    (r"\bsymptomatic\b", "having symptoms"),
    (r"\bprognosis\b", "likely outcome"),
    (r"\betiology\b", "cause"),
    (r"\burinalysis\b", "urine test"),
    (r"\bmedication\b", "medicine"),
    (r"\bmedications\b", "medicines"),
    (r"\bdosage\b", "amount to take"),
    (r"\badministered\b", "given"),
    (r"\btransmitted\b", "spread"),
    (r"\bcontagious\b", "able to spread"),
    (r"\bincubation period\b", "time before symptoms start"),
    (r"\bprecancerous\b", "not cancer yet"),
    (r"\bhypertrophy\b", "growth or enlargement"),
    (r"\bdeficiency\b", "low level"),
]


def tidy(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    text = text.rstrip(" ?.!")
    if text:
        text = text[0].upper() + text[1:]
    return text + "?"


def colloquial(query: str, index: int) -> str:
    q = query.strip().rstrip(" ?.!")
    openers = ["Quick question:", "I was wondering:", "Just curious,"]
    return f"{openers[index % len(openers)]} {q[0].lower() + q[1:]}?"


def plain_language(query: str) -> str:
    q = query.strip()
    for pattern, replacement in PLAIN_TERMS:
        q = re.sub(pattern, replacement, q, flags=re.IGNORECASE)
    return tidy("In simple words, " + q.rstrip(" ?.!").lower())


def keyword_avoid(query: str, category: str, index: int) -> str:
    q = query.strip().rstrip(" ?.!")
    low = q.lower()
    # Remove the named condition, medicine, test, or body structure while
    # retaining the question's task. These forms rely on the paired context.
    rules: dict[str, list[tuple[str, str]]] = {
        "원인": [
            (r"^what causes .+$", "What can cause this problem"),
            (r"^causes of .+$", "What can lead to this condition"),
            (r"^what is .+ caused by$", "What can this condition be caused by"),
            (r"^why (.+)$", r"Why does \1"),
        ],
        "해부·생리": [
            (r"^where is .+$", "Where is this body part located"),
            (r"^where are .+$", "Where are these body parts located"),
            (r"^(?:what is the )?function of .+$", "What does this body part do"),
            (r"^what are the functions of .+$", "What roles do these body parts have"),
        ],
        "검사·정상수치": [
            (r"^(.+) normal range$", "What is the normal range for this test"),
            (r"^normal range (?:for|of) .+$", "What values are considered normal"),
            (r"^what does .+ test for$", "What can this test detect"),
            (r"^what can .+ detect$", "What can this test detect"),
        ],
        "기간·시기": [
            (r"^how long (?:does )?it take for .+$", "How long does recovery usually take"),
            (r"^how long .+$", "How long does this usually last"),
            (r"^when (.+)$", r"When does \1"),
            (r"^at what age (.+)$", r"At what age does \1"),
        ],
        "약물": [
            (r"^what does .+ do$", "What does this medicine do"),
            (r"^what dose .+$", "What amount should someone take"),
            (r"^.+ dosage for .+$", "What amount is usually taken for this condition"),
        ],
        "영양·식이": [
            (r"^foods? .+ is found in$", "Which foods contain this nutrient"),
            (r"^can (.+) food (.+)$", r"Can food \2 cause this"),
            (r"^what is .+ vitamin$", "What is this nutrient"),
        ],
        "증상": [
            (r"^symptoms? of .+$", "What signs might someone notice"),
            (r"^what does .+ feel like$", "What might this feel like"),
            (r"^what (?:does|do) .+ look like$", "What might this look like"),
        ],
        "치료·관리": [
            (r"^(?:what is )?treatment for .+$", "How is this condition treated"),
            (r"^how (?:do|does|can) (?:you )?treat .+$", "How can this condition be treated"),
            (r"^what to expect after .+$", "What should someone expect after treatment"),
        ],
        "종류·분류": [
            (r"^(?:what are the )?types of .+$", "What different types are there"),
            (r"^different types of .+$", "What different types are there"),
            (r"^what kind of .+$", "Which type is being described"),
        ],
        "감염·전파": [
            (r"^how long is .+ contagious$", "How long can someone spread this infection"),
            (r"^how long are you contagious with .+$", "How long can someone spread it"),
            (r"^are .+ communicable$", "Can this be passed between people"),
            (r"^how (?:is|does) .+ (?:spread|transmitted)$", "How does this spread"),
        ],
        "질환 특성·예후": [
            (r"^is .+ curable$", "Can this condition be cured"),
            (r"^.+ survival rate$", "What is the likely outcome"),
            (r"^prognosis of .+$", "What is the likely outlook"),
        ],
        "비용·보험": [
            (r"^how much does it cost for .+$", "How much does this care usually cost"),
            (r"^how much does .+ cost$", "What is the usual cost"),
            (r"^cost (?:of )?.+$", "What is the usual cost"),
            (r"^does insurance cover .+$", "Can insurance help pay for this"),
        ],
        "예방": [
            (r"^how can you prevent .+$", "What can help prevent this condition"),
            (r"^how (?:do|does) (?:you )?prevent .+$", "What can help lower the risk"),
        ],
        "효능·용도": [
            (r"^what is .+ used for$", "What is this used for"),
            (r"^what are .+ used for$", "What are these used for"),
            (r"^is .+ good for .+$", "Can this help with the problem"),
        ],
        "예/아니오 확인": [
            (r"^is (.+) curable$", "Can this condition be cured"),
            (r"^is .+$", "Is this true"),
            (r"^are .+$", "Is this true"),
            (r"^can .+$", "Can this happen"),
            (r"^does .+$", "Does this happen"),
            (r"^do .+$", "Does this happen"),
        ],
        "정의·의미": [
            (r"^what is .+$", "What does this medical term mean"),
            (r"^what are .+$", "What does this term refer to"),
            (r"^what does .+ mean$", "What does this term mean"),
            (r"^definition of .+$", "What is the meaning of this term"),
        ],
    }
    for pattern, replacement in rules.get(category, []):
        if re.match(pattern, low, flags=re.IGNORECASE):
            return tidy(replacement)

    generic_by_category = {
        "정의·의미": ["What does this term mean", "What is being described here"],
        "원인": ["What can cause this problem", "What factors may lead to this"],
        "해부·생리": ["Where is the relevant body part", "What does this body part do"],
        "검사·정상수치": ["What can this test show", "Which values are considered normal"],
        "기타": ["What does the passage say about this", "Can you explain this using the passage"],
        "기간·시기": ["How long does this usually take", "When does this usually happen"],
        "효능·용도": ["What is this used for", "How can this help"],
        "약물": ["What does this medicine do", "How is this medicine used"],
        "영양·식이": ["Which food or nutrient is relevant here", "What should someone eat or know"],
        "증상": ["What signs might someone notice", "How might this appear"],
        "예/아니오 확인": ["Is this true", "Can this happen"],
        "치료·관리": ["How is this treated", "What can someone do to manage this"],
        "종류·분류": ["What different types are there", "How can these be grouped"],
        "감염·전파": ["Can this spread to someone else", "How can this be passed along"],
        "질환 특성·예후": ["What is likely to happen over time", "What is the expected outlook"],
        "비용·보험": ["What might this care cost", "Can insurance help pay for this"],
        "예방": ["What can help prevent this", "How can the risk be lowered"],
    }
    options = generic_by_category[category]
    return tidy(options[index % len(options)])


def main() -> None:
    base = pd.read_parquet(SOURCE)
    if len(base) != 350:
        raise RuntimeError(f"Expected 350 source rows, found {len(base)}")
    if "question_category" not in base.columns:
        raise RuntimeError("Source must contain question_category")

    max_id = int(base["query_id"].max())
    outputs = []
    for index, row in base.reset_index(drop=True).iterrows():
        original_id = int(row["query_id"])
        original_query = str(row["query"])
        avoided = keyword_avoid(original_query, row["question_category"], index)
        context_openers = [
            "From the passage,",
            "Based on the context,",
            "Using the information here,",
            "According to the passage,",
        ]
        avoided = f"{context_openers[index % len(context_openers)]} {avoided[0].lower() + avoided[1:]}"
        variants = [
            ("원본", original_query),
            ("구어체", colloquial(original_query, index)),
            ("쉬운 말", plain_language(original_query)),
            ("핵심 단어 회피", avoided),
        ]
        for variant_type, query in variants:
            record = row.to_dict()
            record["source_query_id"] = original_id
            record["comparison_group_id"] = original_id
            record["source_query"] = original_query
            record["query_variant_type"] = variant_type
            record["requires_paired_context"] = variant_type == "핵심 단어 회피"
            record["query"] = query
            if variant_type != "원본":
                max_id += 1
                record["query_id"] = max_id
            record["split"] = "test"
            outputs.append(record)

    result = pd.DataFrame(outputs)
    # A count check is explicit, while duplicate text is allowed across groups
    # because some broad keyword-avoid questions can naturally converge.
    if len(result) != 1400:
        raise RuntimeError(f"Expected 1,400 rows, found {len(result)}")
    if result["query_id"].duplicated().any():
        raise RuntimeError("Duplicate query_id values")
    if result.groupby("comparison_group_id")["query_variant_type"].nunique().ne(4).any():
        raise RuntimeError("Each comparison group must have all four variant labels")
    if result.isna().sum().sum():
        raise RuntimeError("Unexpected null values in expanded dataset")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(OUTPUT, index=False)
    summary = {
        "source": str(SOURCE),
        "output": str(OUTPUT),
        "rows": int(len(result)),
        "base_questions": int(result["comparison_group_id"].nunique()),
        "labels": {str(k): int(v) for k, v in result["query_variant_type"].value_counts().items()},
        "rows_per_group": 4,
        "unique_query_ids": bool(result["query_id"].is_unique),
        "null_count": int(result.isna().sum().sum()),
        "note": "Keyword-avoid variants depend on their paired context because explicit topic terms are intentionally removed.",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\nSAMPLE GROUP")
    sample = result[result["comparison_group_id"].eq(int(result.iloc[0]["comparison_group_id"]))]
    print(sample[["query_variant_type", "query"]].to_string(index=False))


if __name__ == "__main__":
    main()
