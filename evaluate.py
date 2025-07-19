import json
import time
from datetime import datetime, timezone
now = datetime.now(timezone.utc).isoformat()
from app.retrieval.retrieval_service import hybrid_retrieve
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def load_benchmark():
    with open("benchmark/sample_questions.json", "r") as f:
        return json.load(f)

def semantic_similarity(answer: str, expected: str) -> float:
    from sentence_transformers import util, SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return util.cos_sim(model.encode(answer), model.encode(expected)).item()

def hallucination_check(answer: str) -> bool:
    # simple heuristic: flag if answer contains random-looking numbers or future years
    import re
    suspicious = re.findall(r"\b(202[6-9]|[A-Z]{3,}[0-9]{3,})\b", answer)
    return bool(suspicious)

def evaluate():
    test_cases = load_benchmark()
    rows = []
    for case in test_cases:
        start = time.time()
        results = hybrid_retrieve(case["question"], k=1)
        end = time.time()

        answer = results[0][0] if results else ""
        latency = int((end - start) * 1000)
        similarity = semantic_similarity(answer, case["expected"])
        hallucinated = hallucination_check(answer)

        rows.append({
            "question": case["question"],
            "expected": case["expected"],
            "answer": answer,
            "similarity": round(similarity, 3),
            "latency_ms": latency,
            "hallucination": hallucinated
        })

    write_markdown_report(rows)

def write_markdown_report(rows):
    now = datetime.utcnow().isoformat()
    with open("evaluation_report.md", "w") as f:
        f.write(f"# Evaluation Report ({now})\n\n")
        f.write("| Question | Similarity | Latency (ms) | Hallucination |\n")
        f.write("|----------|------------|--------------|----------------|\n")
        for r in rows:
            f.write(f"| {r['question']} | {r['similarity']} | {r['latency_ms']} | {'⚠️' if r['hallucination'] else '✅'} |\n")
        f.write("\n---\n")
        f.write(f"Test cases: {len(rows)}\n")
        avg_sim = sum([r['similarity'] for r in rows]) / len(rows)
        avg_lat = sum([r['latency_ms'] for r in rows]) / len(rows)
        f.write(f"Avg similarity: {round(avg_sim, 3)}\n")
        f.write(f"Avg latency: {round(avg_lat)}ms\n")

if __name__ == "__main__":
    evaluate()
