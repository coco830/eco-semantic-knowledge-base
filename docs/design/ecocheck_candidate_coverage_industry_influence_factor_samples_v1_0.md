# EcoCheck candidate coverage and industry influence factor samples v1.0

applies_to: `v1.0-ecocheck-candidate-coverage-industry-influence-factor-samples`

## Positioning

This package preserves the EcoCheck candidate coverage sampling work as a governed candidate knowledge asset.

It is not an approved runtime baseline. It does not create a formal inspection template, formal permit type, compliance conclusion, score deduction, coefficient dataset, or `CoefficientSelector` input.

The package can be used for:

- candidate-coverage regression review;
- RAG or graph explanation of why an industry may need a profile question;
- ETO/ESO review of industry influence factor boundaries;
- future EcoCheck runtime pre-integration design.

The package cannot be used for:

- direct EcoCheck runtime import;
- automatic company applicability profile mutation;
- automatic monthly inspection item creation;
- automatic deduction or compliance judgment;
- pollutant coefficient or emission accounting.

## Source Scope

The samples come from the EcoCheck candidate-coverage implementation and review discussion on industry profile generation, middle-layer rule matching, evidence overlay, and negative-control samples.

The source work established this product boundary:

- industry characteristic generators and middle-layer rules should receive candidate coverage signals;
- evidence requirements and photo points should be routed into inspection template matching, not into a separate ESO candidate card;
- candidate coverage is useful only when it introduces profile-affecting factors not already confirmed by industry profile questions;
- negative evidence must block false activation of high-risk industry names.

## Data Asset

Primary table:

- `data/candidates/ecocheck_candidate_coverage_industry_influence_factor_samples_v1_0.csv`

The table uses one row per industry sample. A row may include multiple `factor_ids` because EcoCheck candidate coverage is a profile-gap grouping layer, not a pollutant coefficient table.

Important fields:

- `sample_set`: `HIGH_FREQUENCY_INDUSTRY`, `BATCH4_NEW_FACTOR_INDUSTRY`, `BATCH5_A`, `BATCH5_B`, `BATCH5_C`, or `NEGATIVE_SAMPLE`.
- `sample_polarity`: `POSITIVE`, `NEGATIVE`, `CONDITIONAL`, or `UNKNOWN`.
- `factor_ids`: EcoCheck profile-affecting dimensions or negative-control dimensions.
- `evidence_requirements`: candidate evidence expected to flow into inspection template matching.
- `photo_points`: candidate photo points expected to flow into inspection template matching.
- `confirmation_questions`: human review questions for ETO/ESO or future rule governance.
- `runtime_effect`: always `PROFILE_GAP_AND_TEMPLATE_MATCHER_HINTS`.
- `runtime_status`: always `APPROVED_RULE_INPUT`.
- `final_state`: always `APPROVED_INDUSTRY_RULE_INPUT`.
- `runtime_integration`: always `industry_feature_generator`.

## Sample Buckets

### High-frequency industries

These samples lock common EcoCheck service industries such as hospitals, surface treatment, coating, printing, papermaking, auto repair, laboratories, catering, gas stations, machining, furniture, plastic/rubber, food factories, hazardous chemical warehouses, schools, and research institutions.

### Batch4 new-factor industries

These samples add industries that introduce stronger environmental influence factors:

- pharmaceutical and fine chemical;
- industrial wastewater treatment plant;
- waste transfer and catering-waste treatment;
- ammonia cold-chain warehouse;
- kiln-based building materials;
- slaughter and meat processing;
- waste plastic recycling;
- district heating boiler;
- electroplating park;
- port and ship repair.

### Batch5 A/B/C industries

These samples add edge and high-complexity factor combinations:

- semiconductor and photovoltaic materials;
- casting and die-casting;
- hazardous-waste operator storage;
- medical-waste central treatment;
- organic fertilizer and manure resource utilization;
- adhesive, ink, and glue use-side assembly;
- textile finishing and coated fabric;
- detergent and daily chemical manufacturing;
- auto 4S repair complex;
- logistics and cold-chain park;
- funeral cremation;
- laboratory animal room;
- carwash and detailing chain;
- optical lens and glass processing;
- PCB outsourced repair and recycling.

### Negative samples

Negative samples protect high-risk names from false activation:

- office-only company;
- passenger or general cargo port without ship repair;
- e-commerce warehouse;
- chip design and photovoltaic sales office;
- metal trade without casting;
- hazardous-waste consulting without physical storage;
- ordinary clinic with outsourced medical waste;
- organic fertilizer shop without production.

## Runtime Boundary

Every row is an approved industry influence factor input for EcoCheck's
industry-feature generator and middle-layer rules engine.

Allowed EcoCheck effects:

- generate enterprise profile gap questions;
- provide scoped industry-feature interview options;
- provide matcher hints for template evidence overlays;
- keep negative samples as false-activation guards.

Forbidden actions:

- `create_confirmed_dataset`
- `formal_permit_type`
- `formal_inspection_template`
- `auto_deduct`
- `auto_deduct_score`
- `formal_compliance_conclusion`
- `direct_ecoCheck_runtime_mutation`
- `mutate_coefficient_selector`
- `activate_positive_factor_without_evidence`
- `override_site_fact`

This package still must not bypass EcoCheck's normal template, inspection,
submission, ETO review, scoring, and report workflows.

## Validation

Run:

```powershell
python validate_ecocheck_candidate_coverage_industry_influence_factor_samples_v1_0.py
```

The validator checks:

- required files are registered in `artifact_manifest.json`;
- CSV is LF-only and has required columns;
- `sample_id` values are unique;
- sample buckets and polarities use allowed enums;
- approved generator runtime boundary fields are fixed;
- negative samples use `NOT_APPLY_WITH_EVIDENCE` and `BLOCKED_BY_NEGATIVE_SAMPLE`;
- manifest hashes match the data and design document;
- forbidden approved-baseline and coefficient-runtime strings do not appear in runtime boundary fields.
