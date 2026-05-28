import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
LABELS = {
    "CONFIRM_APPLIES",
    "CONFIRM_MAY_APPLY",
    "CONFIRM_NOT_APPLY",
    "NEED_EIA_CONFIRM",
    "NEED_PERMIT_CONFIRM",
    "NEED_SITE_CONFIRM",
    "REJECT_CANDIDATE",
    "MERGE_DUPLICATE",
    "NEED_RULE_FIX",
}
CONFIRM_LABELS = {"CONFIRM_APPLIES", "CONFIRM_MAY_APPLY", "CONFIRM_NOT_APPLY"}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def main():
    failures = []
    required = [
        "simulated_human_review_input_v0_8.csv",
        "simulated_human_review_input_v0_8.json",
        "human_review_overlay_v0_8.csv",
        "human_review_overlay_v0_8.json",
        "human_review_diff_report_v0_8.md",
        "human_review_diff_report_v0_8.json",
        "human_review_backfill_validation_v0_8.json",
        "formalization_candidate_queue_v0_8.csv",
        "still_blocked_queue_v0_8.csv",
        "rag_prototype_queries_v0_8.jsonl",
        "rag_prototype_results_v0_8.jsonl",
        "rag_prototype_eval_report_v0_8.md",
        "rag_prototype_eval_report_v0_8.json",
        "knowledge_base_manifest_v0_8.json",
        "FINAL_COMPLETION_REPORT_v0_8.md",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(failures, name, "missing_required_output")

    v07_worksheet = read_csv(ROOT / "human_review_worksheet_v0_7.csv")
    if any(r.get("human_review_label") or r.get("human_reviewer") or r.get("reviewed_at") for r in v07_worksheet):
        fail(failures, "human_review_worksheet_v0_7.csv", "source_worksheet_was_modified")

    simulated = read_csv(ROOT / "simulated_human_review_input_v0_8.csv")
    overlay = read_csv(ROOT / "human_review_overlay_v0_8.csv")
    formalization = read_csv(ROOT / "formalization_candidate_queue_v0_8.csv")
    blocked = read_csv(ROOT / "still_blocked_queue_v0_8.csv")
    rag_queries = read_jsonl(ROOT / "rag_prototype_queries_v0_8.jsonl")
    rag_results = read_jsonl(ROOT / "rag_prototype_results_v0_8.jsonl")
    rag_eval = read_json(ROOT / "rag_prototype_eval_report_v0_8.json")
    backfill_validation = read_json(ROOT / "human_review_backfill_validation_v0_8.json")
    manifest = read_json(ROOT / "knowledge_base_manifest_v0_8.json")

    if len(simulated) < 6 or len(overlay) != len(simulated):
        fail(failures, "human_review_overlay_v0_8.csv", "bad_overlay_count")
    if {r["human_review_label"] for r in simulated} != LABELS:
        fail(failures, "simulated_human_review_input_v0_8.csv", "label_coverage_not_complete")
    if len(formalization) + len(blocked) != len(overlay):
        fail(failures, "formalization_candidate_queue_v0_8.csv", "partition_count_mismatch")
    if len(rag_queries) != len(rag_results) or len(rag_results) < 8:
        fail(failures, "rag_prototype_results_v0_8.jsonl", "bad_rag_query_count")

    for row in simulated:
        rid = row["review_item_id"]
        label = row["human_review_label"]
        if label not in LABELS:
            fail(failures, "simulated_human_review_input_v0_8.csv", "invalid_label", rid)
        for field in ["human_reviewer", "human_reviewer_role", "reviewed_at", "review_basis", "decision_confidence"]:
            if not row.get(field):
                fail(failures, "simulated_human_review_input_v0_8.csv", f"missing_{field}", rid)
        if label in CONFIRM_LABELS:
            for field in ["human_reviewer_role", "reviewed_at", "human_review_notes", "evidence_refs", "decision_confidence"]:
                if not row.get(field):
                    fail(failures, "simulated_human_review_input_v0_8.csv", f"confirm_missing_{field}", rid)

    overlay_ids = [r["overlay_id"] for r in overlay]
    if len(overlay_ids) != len(set(overlay_ids)):
        fail(failures, "human_review_overlay_v0_8.csv", "duplicate_overlay_id")
    for row in overlay:
        oid = row["overlay_id"]
        if (
            row.get("final_state") != FINAL_STATE
            or row.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME"
            or row.get("runtime_integration") != RUNTIME_INTEGRATION
        ):
            fail(failures, "human_review_overlay_v0_8.csv", "bad_boundary", oid)
        if row.get("runtime_effect") != "NO_RUNTIME_EFFECT" or row.get("requires_second_approval") != "true":
            fail(failures, "human_review_overlay_v0_8.csv", "bad_runtime_effect", oid)
        if row["human_review_label"] in CONFIRM_LABELS and row["overlay_status"] != "FORMALIZATION_CANDIDATE":
            fail(failures, "human_review_overlay_v0_8.csv", "confirm_not_formalization_candidate", oid)
        if row["human_review_label"] not in CONFIRM_LABELS and row["overlay_status"] != "BLOCKS_RUNTIME":
            fail(failures, "human_review_overlay_v0_8.csv", "non_confirm_not_blocked", oid)

    for row in formalization:
        oid = row["overlay_id"]
        if row.get("runtime_integration") != RUNTIME_INTEGRATION or row.get("runtime_effect") != "NO_RUNTIME_EFFECT":
            fail(failures, "formalization_candidate_queue_v0_8.csv", "bad_formalization_runtime_boundary", oid)
        if row.get("requires_second_approval") != "true":
            fail(failures, "formalization_candidate_queue_v0_8.csv", "missing_second_approval", oid)

    chunk_ids = {c["chunk_id"] for c in read_jsonl(ROOT / "rag_chunks_v0_5.jsonl")}
    forbidden = ["已接入运行时", "自动扣分", "正式模板已生成", "正式适用"]
    for row in rag_results:
        qid = row["query_id"]
        if row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "rag_prototype_results_v0_8.jsonl", "bad_boundary", qid)
        if "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY" not in row.get("answer", "") or "不是运行时批准" not in row.get("answer", ""):
            fail(failures, "rag_prototype_results_v0_8.jsonl", "missing_boundary_notice", qid)
        if not row.get("source_chunk_ids"):
            fail(failures, "rag_prototype_results_v0_8.jsonl", "missing_source_chunks", qid)
        for cid in row.get("source_chunk_ids", []):
            if cid not in chunk_ids:
                fail(failures, "rag_prototype_results_v0_8.jsonl", "orphan_source_chunk", f"{qid}:{cid}")
        if any(token in row.get("answer", "") for token in forbidden):
            fail(failures, "rag_prototype_results_v0_8.jsonl", "forbidden_runtime_claim", qid)

    if rag_eval.get("validation_status") != "PASS" or rag_eval.get("failed_query_count") != 0:
        fail(failures, "rag_prototype_eval_report_v0_8.json", "rag_eval_failed")
    if backfill_validation.get("runtime_effect") != "NONE" or backfill_validation.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "human_review_backfill_validation_v0_8.json", "bad_backfill_boundary")
    if manifest.get("final_state") != FINAL_STATE or manifest.get("runtime_integration") != RUNTIME_INTEGRATION or manifest.get("runtime_effect") != "NONE":
        fail(failures, "knowledge_base_manifest_v0_8.json", "bad_manifest_boundary")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "simulated_review_rows": len(simulated),
        "overlay_rows": len(overlay),
        "formalization_candidate_rows": len(formalization),
        "still_blocked_rows": len(blocked),
        "rag_query_count": len(rag_results),
        "failure_samples": failures[:50],
    }
    (ROOT / "review_backfill_rag_prototype_v0_8_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    backfill_validation["validation_status"] = report["validation_status"]
    backfill_validation["failure_count"] = len(failures)
    backfill_validation["validator"] = "validate_review_backfill_rag_prototype_v0_8.py"
    (ROOT / "human_review_backfill_validation_v0_8.json").write_text(
        json.dumps(backfill_validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "review_backfill_rag_prototype_v0_8_failure_list.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
