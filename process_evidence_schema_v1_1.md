# process_evidence_schema_v1_1

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

## Purpose

v1.1 introduces a process/evidence layer between industry-code recall and enterprise profile confirmation. It converts EIA, approval, permit, registration, ledger, and site facts into auditable predicates. It does not generate formal permit_type, inspection templates, or deduct values.

## State Model

- `CANDIDATE_RECALLED`: recalled by industry code, permit catalog, or scenario template.
- `PROCESS_EVIDENCE_CONFIRMED`: source document directly confirms a process or risk unit.
- `SCENARIO_EVIDENCE_CONFIRMED`: confirmed process activates a scenario template.
- `NOT_APPLY_WITH_EVIDENCE`: source document directly negates a process or risk unit.
- `SITE_VERIFICATION_REQUIRED`: document evidence exists but ESO/ETO must verify current site facts.
- `SITE_CONFLICT_NEEDS_REVIEW`: source document and site fact conflict.
- `RUNTIME_BLOCKED`: no runtime effect before approval gates.

## Core Fields

- `process_id`, `process_name`, `aliases`, `positive_keywords`, `negative_keywords`.
- `evidence_id`, `enterprise_id`, `industry_code`, `evidence_strength`, `source_document_type`, `source_excerpt`.
- `linked_scenario_ids`, `linked_permit_entry_nos`, `confirmation_questions`, `photo_points`.
- `overlay_scope`: `PROCESS_ONLY` means the evidence only includes/excludes one process trigger; `SCENARIO_WIDE` means the evidence supports a scenario-level candidate.
- `runtime_status`, `final_state`, `runtime_integration`.

## Evidence Rules

- DIRECT evidence can activate a scenario but still requires site verification.
- NEGATED evidence can support `NOT_APPLY_WITH_EVIDENCE` only when the source excerpt explicitly excludes the process.
- NEGATED process evidence must use `overlay_scope=PROCESS_ONLY` unless it explicitly excludes the entire scenario/risk unit.
- IMPLIED evidence cannot upgrade to `APPLIES` without ETO/ESO review.
- UNKNOWN remains a question, not a negative conclusion.
