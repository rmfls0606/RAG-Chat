from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pandas as pd


SOURCE = Path("data/medical_train.parquet")
OUTPUT_DIR = Path("data/derived")
TEST_PATH = OUTPUT_DIR / "medical_test_350.parquet"
REMAINING_PATH = OUTPUT_DIR / "medical_train_without_test.parquet"
AUDIT_PATH = OUTPUT_DIR / "medical_test_350_distribution.csv"
MANIFEST_PATH = OUTPUT_DIR / "medical_test_350_manifest.json"
SEED = 20261102
TARGET_SIZE = 350


SOURCE_COUNTS = {
    "정의·의미": 1525,
    "원인": 863,
    "해부·생리": 627,
    "검사·정상수치": 559,
    "기타": 509,
    "기간·시기": 348,
    "효능·용도": 305,
    "약물": 272,
    "영양·식이": 263,
    "증상": 257,
    "예/아니오 확인": 247,
    "치료·관리": 162,
    "종류·분류": 157,
    "감염·전파": 149,
    "질환 특성·예후": 92,
    "비용·보험": 37,
    "예방": 25,
}


# The first matching expression is stored for auditability. Selection uses only
# the query field; answers/context never influence the assigned question type.
PATTERNS = {
    "비용·보험": [
        r"\b(cost|price|expensive|cheap|insurance|insured|coverage|cover(ed|age)?|copay|co-pay|medicare|medicaid|pay for)\b",
    ],
    "예방": [
        r"\b(prevent|prevention|preventing|avoid|protect against|prophylaxis|reduce (the )?risk)\b",
    ],
    "감염·전파": [
        r"\b(contagious|infectious|infection|infected|transmit|transmission|spread|catch|contract|communicable)\b",
    ],
    "검사·정상수치": [
        r"\b(normal (range|level|value|count)|reference range|test result|blood test|urine test|urinalysis|screening|diagnos(e|is|tic)|detect|measure|level(s)?|count|positive test|negative test)\b",
    ],
    "약물": [
        r"\b(drug|medication|medicine|tablet|pill|capsule|dose|dosage|prescription|antibiotic|antidepressant|painkiller|insulin|vaccine)\b",
    ],
    "영양·식이": [
        r"\b(food|diet|eat|eating|nutrition|nutrient|vitamin|mineral|calorie|protein|carbohydrate|fat intake|supplement|fiber|fibre)\b",
    ],
    "치료·관리": [
        r"\b(treat|treatment|therapy|manage|management|cure|remedy|surgery|operation|rehabilitation|care for|relieve)\b",
    ],
    "증상": [
        r"\b(symptom|signs? of|feel like|look like|present with|manifestation|warning sign)\b",
    ],
    "원인": [
        r"\b(cause|causes|caused by|causing|why (do|does|is|are|can)|reason for|risk factor|lead to|trigger)\b",
    ],
    "기간·시기": [
        r"\b(how long|duration|when (do|does|is|are|can|should)|what age|at what age|age range|onset|start|begin|last for|incubation period|recovery time|gestation)\b",
    ],
    "종류·분류": [
        r"\b(types? of|kinds? of|categories of|classification|classify|stages? of|grades? of|forms? of|different types)\b",
    ],
    "질환 특성·예후": [
        r"\b(prognosis|outlook|survival|life expectancy|fatal|deadly|serious|chronic|acute|progress|progression|complication|recurrence|recur|curable)\b",
    ],
    "효능·용도": [
        r"\b(used for|use of|purpose of|benefit|benefits|effective|effectiveness|efficacy|help with|good for|role of)\b",
    ],
    "해부·생리": [
        r"\b(function of|functions? of|where (is|are)|located|location of|part of the body|which (organ|muscle|bone|nerve|artery|vein|gland)|what (organ|muscle|bone|nerve|artery|vein|gland)|body produce|physiology|anatomy|how (does|do) .+ (work|function))\b",
    ],
    "정의·의미": [
        r"^(what is|what are|what does .+ mean|define|definition of|meaning of|who is)\b",
        r"\b(stands for|known as|refers to)\b",
    ],
    "예/아니오 확인": [
        r"^(is|are|can|could|do|does|did|should|will|would|has|have|was|were)\b",
    ],
}


def allocate_largest_remainder(counts: dict[str, int], target: int) -> dict[str, int]:
    total = sum(counts.values())
    exact = {name: count * target / total for name, count in counts.items()}
    result = {name: math.floor(value) for name, value in exact.items()}
    remainder = target - sum(result.values())
    order = sorted(counts, key=lambda name: exact[name] - result[name], reverse=True)
    for name in order[:remainder]:
        result[name] += 1
    return result


def match_keyword(query: str, category: str) -> str | None:
    text = query.strip().lower()
    for pattern in PATTERNS.get(category, []):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def select_rows(train: pd.DataFrame, quotas: dict[str, int]) -> pd.DataFrame:
    rng = pd.Series(range(len(train))).sample(frac=1, random_state=SEED).tolist()
    shuffled = train.iloc[rng].copy()
    selected_ids: set[int] = set()
    selected_parts: list[pd.DataFrame] = []

    # Specific categories are selected before broad definitions/yes-no questions.
    selection_order = [
        "비용·보험", "예방", "감염·전파", "검사·정상수치", "약물", "영양·식이",
        "치료·관리", "증상", "원인", "기간·시기", "종류·분류", "질환 특성·예후",
        "효능·용도", "해부·생리", "정의·의미", "예/아니오 확인",
    ]

    for category in selection_order:
        needed = quotas[category]
        candidates = shuffled.loc[~shuffled["query_id"].isin(selected_ids)].copy()
        candidates["matched_keyword"] = candidates["query"].map(
            lambda value: match_keyword(value, category)
        )
        candidates = candidates[candidates["matched_keyword"].notna()].head(needed)
        if len(candidates) < needed:
            raise RuntimeError(
                f"Insufficient keyword matches for {category}: {len(candidates)} < {needed}"
            )
        candidates["question_category"] = category
        selected_ids.update(candidates["query_id"].astype(int).tolist())
        selected_parts.append(candidates)

    # 기타 is deliberately made from remaining questions with no category keyword.
    needed_other = quotas["기타"]
    remaining = shuffled.loc[~shuffled["query_id"].isin(selected_ids)].copy()
    remaining["_has_any_keyword"] = remaining["query"].map(
        lambda query: any(
            match_keyword(query, category) is not None
            for category in PATTERNS
        )
    )
    other = remaining.loc[~remaining["_has_any_keyword"]].head(needed_other).copy()
    if len(other) < needed_other:
        other = remaining.head(needed_other).copy()
    other["matched_keyword"] = "other/no listed keyword"
    other["question_category"] = "기타"
    other = other.drop(columns=["_has_any_keyword"], errors="ignore")
    selected_parts.append(other)

    selected = pd.concat(selected_parts, ignore_index=True)
    selected["split"] = "test"
    selected = selected.sample(frac=1, random_state=SEED).reset_index(drop=True)
    return selected


def main() -> None:
    frame = pd.read_parquet(SOURCE)
    train = frame.loc[frame["split"].eq("train")].copy()
    if len(train) != sum(SOURCE_COUNTS.values()):
        raise RuntimeError(
            f"Expected {sum(SOURCE_COUNTS.values())} train rows, found {len(train)}"
        )

    quotas = allocate_largest_remainder(SOURCE_COUNTS, TARGET_SIZE)
    test = select_rows(train, quotas)
    selected_ids = set(test["query_id"].astype(int))
    remaining = frame.loc[~frame["query_id"].isin(selected_ids)].copy()

    source_columns = frame.columns.tolist()
    test = test[source_columns + ["question_category", "matched_keyword"]]

    actual = test["question_category"].value_counts().to_dict()
    if len(test) != TARGET_SIZE or actual != quotas:
        raise RuntimeError(f"Distribution mismatch: {actual} != {quotas}")
    if test["query_id"].duplicated().any() or test["query"].duplicated().any():
        raise RuntimeError("Duplicate query_id or query in test set")
    if set(test["query_id"]) & set(remaining.loc[remaining["split"].eq("train"), "query_id"]):
        raise RuntimeError("Train/test query_id leakage detected")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    test.to_parquet(TEST_PATH, index=False)
    remaining.to_parquet(REMAINING_PATH, index=False)

    audit = pd.DataFrame(
        {
            "유형": list(SOURCE_COUNTS),
            "원본_개수": [SOURCE_COUNTS[name] for name in SOURCE_COUNTS],
            "원본_비율": [SOURCE_COUNTS[name] / sum(SOURCE_COUNTS.values()) for name in SOURCE_COUNTS],
            "테스트_개수": [quotas[name] for name in SOURCE_COUNTS],
            "테스트_비율": [quotas[name] / TARGET_SIZE for name in SOURCE_COUNTS],
        }
    )
    audit.to_csv(AUDIT_PATH, index=False, encoding="utf-8-sig")

    manifest = {
        "source": str(SOURCE),
        "seed": SEED,
        "method": "deterministic keyword-stratified holdout from split=train",
        "test_rows": len(test),
        "remaining_rows_total": len(remaining),
        "remaining_train_rows": int(remaining["split"].eq("train").sum()),
        "preserved_validation_rows": int(remaining["split"].eq("validation").sum()),
        "distribution": quotas,
        "checks": {
            "unique_query_id": bool(test["query_id"].is_unique),
            "unique_query": bool(test["query"].is_unique),
            "train_test_id_overlap": 0,
            "null_count": int(test.isna().sum().sum()),
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
