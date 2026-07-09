# AeroRoute Operational Readiness Plan

Status: planning baseline, not operational approval.

This document defines the work required to move AeroRoute MLX from an
educational pre-operational OFP simulator toward a product that an operator
could submit for operational approval. It does not make the current software
operationally approved, ICAO-fileable, dispatch-authorized, or suitable for
safety-critical decisions.

## Regulatory Baseline

The target must be selected per operator and jurisdiction before implementation
can be considered complete:

- **EASA Air OPS**: operator responsibilities, operational control,
  performance, fuel/energy, operational flight plan, records, manuals,
  compliance monitoring and safety management belong to the approved operator
  system, not just to the software supplier.
- **FAA EFB authorization**: FAA AC 120-76E describes operational use of EFBs
  for operators under 14 CFR part 91K, 121, 125 and 135. Operational use needs
  operator processes, application assessment, training, revision control,
  backup procedures and authorization where applicable.
- **FAA/ICAO flight-plan filing**: filed data must match current domestic,
  international and ICAO flight-plan guidance plus the operator's actual
  aircraft capabilities and operational approvals.

Authoritative references to review at the start of every operational release:

- EASA Easy Access Rules for Air Operations:
  https://www.easa.europa.eu/en/document-library/easy-access-rules/easy-access-rules-air-operations
- FAA AC 120-76E, Authorization for Use of Electronic Flight Bags:
  https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentID/1042829
- FAA Flight Planning Information:
  https://www.faa.gov/about/office_org/headquarters_offices/ato/service_units/air_traffic_services/flight_plan_filing

## Non-Negotiable Entry Gate

AeroRoute remains non-operational until all of these are true:

- a launch operator, aircraft fleet, operation type and jurisdiction are named;
- the applicable regulator or principal inspector path is identified;
- legal access and redistribution rights exist for navdata, weather, NOTAM,
  airport, obstacle, terrain, performance and filing data;
- a safety management process accepts the software's failure conditions and
  mitigations;
- a quality management process controls requirements, changes, verification,
  releases, defects, suppliers and records;
- operational manuals, dispatch procedures, training and backup procedures are
  approved by the operator;
- an independent operational validation demonstrates that generated outputs are
  correct for the intended aircraft, routes, airports and rules.

## Target Product Split

The current RC1 product remains educational, pre-operational,
non-ICAO-fileable and not dispatch-authorized.

The operational program creates a separate approval track:

| Track | Purpose |
| --- | --- |
| `simulator` | Existing demo, portfolio, training and development environment. |
| `ops-candidate` | Controlled operational candidate with licensed data, evidence, compliance gates and operator-specific configuration. |
| `approved-operator-build` | Immutable build approved inside one operator's manuals/procedures; not automatically reusable by another operator. |

## Phase 15 — Regulatory Scope And Safety Case

Goal: define the exact approval target and safety argument before adding
operational features.

Deliverables:

- named launch operator profile or representative target profile;
- jurisdiction matrix covering EASA, FAA or both;
- intended-function statement and explicit excluded functions;
- preliminary hazard analysis for wrong route, wrong fuel, stale navdata,
  incorrect weather, unavailable filing, display corruption, stale aircraft
  performance and AI explanation misuse;
- DAL/criticality assessment or equivalent software assurance classification;
- operational approval checklist mapped to operator manuals and procedures;
- traceability repository for requirements, risks, tests and evidence.

Exit gate:

- every safety-relevant feature has an owner, hazard, severity, mitigation,
  verification method and release evidence requirement.

## Phase 16 — Certified Data Supply Chain

Goal: replace demo/open fixture data with licensed, versioned, auditable
operational sources.

Required data domains:

- ARINC 424/AIRAC navdata with legal operational use rights;
- airport/runway/procedure/airway/fix restrictions;
- weather including METAR, TAF, winds aloft, SIGMET/AIRMET and provider
  quality indicators;
- NOTAM and operational airport status;
- airspace restrictions, RAD/route availability where applicable, flow
  constraints and conditional routes;
- terrain/obstacle data where route validation requires it;
- aircraft performance database per tail/fleet and approved configuration;
- fuel policy, MEL/CDL effects, tankering rules and company policy.

Exit gate:

- every OFP field cites its source, cycle, timestamp, license, validation state
  and fallback behavior; stale or missing operational data blocks operational
  release rather than silently degrading.

Implementation update, 9 July 2026:

- `aeroroute-contracts` publishes the `operational-data-source/v1` schema.
- `aeroroute-api` exposes `GET /api/v1/operational-data-sources`, which lists
  all required data domains and keeps `operational_use_enabled=false`.
- `reference/operational-data-sources-2026-07-09.json` records the current
  non-operational data-source baseline.
- `make operational-data-sources` verifies that required data domains exist,
  missing operational providers fail closed, and no source is mislabeled as
  operational.

Phase 16 completes the source-contract and blocking-gate foundation. It does
not mean AeroRoute has licensed operational data; the readiness gate
`licensed_operational_data` remains blocking until approved suppliers and
operator rights are configured.

## Phase 17 — Operational Route And Filing Engine

Goal: generate routes and flight-plan messages that are valid for the intended
operation, not merely plausible.

Deliverables:

- route validation against airways, DCT allowances, altitude/level constraints,
  procedure restrictions and route availability;
- ICAO FPL generation and validation for items 7, 8, 9, 10, 13, 15, 16, 18 and
  19;
- aircraft capability and approval model so filed codes cannot exceed operator
  approvals;
- NOTAM/RAD/ATC restriction integration;
- route amendment workflow, dispatcher review and approval state machine;
- filing gateway integration only after operator approval.

Exit gate:

- invalid, incomplete, unapproved or stale inputs block filing and produce a
  controlled operational error; no route is promoted as filed until accepted by
  the relevant filing path.

Implementation update, 9 July 2026:

- `aeroroute-contracts` publishes the `icao-fpl-validation/v1` schema.
- `aeroroute-api` exposes `POST /api/v1/icao-fpl/validate` for a
  non-transmitted ICAO FPL validation preview covering items 7, 8, 9, 10, 13,
  15, 16, 18 and 19.
- Filing remains disabled. The validator always returns `filing_enabled=false`
  and includes blockers for missing filing gateway, missing NOTAM/RAD/ATC data
  and absent operator aircraft-capability approval.
- `reference/icao-fpl-validation-2026-07-09.json` and
  `make icao-fpl-baseline` keep the filing baseline blocked.

Phase 17 completes validation scaffolding only. It does not enable ICAO FPL
submission, route filing, dispatcher release or ATC-facing output.

## Phase 18 — Operational Fuel, Performance And Dispatch

Goal: replace simplified educational fuel with approved dispatch calculations.

Deliverables:

- aircraft-specific performance model validated against the operator's approved
  data;
- takeoff, climb, cruise, descent, approach, alternate and contingency policies
  per applicable rules and company policy;
- runway performance, limitations, weights, balance interface and payload/fuel
  reconciliation;
- weather minima, alternate minima, destination suitability and airport status;
- ETOPS/EDTO support only if separately approved;
- dispatcher/pilot signoff, revision history and immutable release records.

Exit gate:

- OFP totals reconcile mathematically and match independent benchmark cases for
  every supported fleet/route class.

Implementation update, 9 July 2026:

- `aeroroute-contracts` publishes the `dispatch-readiness/v1` schema.
- `aeroroute-api` exposes `GET /api/v1/dispatch-readiness`, which keeps
  `dispatch_release_enabled=false`.
- `reference/dispatch-readiness-2026-07-09.json` and
  `make dispatch-readiness` verify that dispatch release remains blocked until
  approved aircraft performance data, fuel policy, runway/weight/balance
  limits, minima/alternate suitability and dispatcher/pilot signoff exist.

Phase 18 completes the dispatch-readiness gate only. The current fuel plan
remains educational and non-operational.

## Phase 19 — Assurance, Security And Operations

Goal: make the system operable under controlled change, audit and incident
processes.

Deliverables:

- requirements-to-test traceability;
- independent verification and validation for safety-critical calculations;
- release control, rollback, data-cycle promotion and supplier change review;
- production observability with alerting, SLOs, audit logs and data-retention
  policy;
- cybersecurity threat model, access control, secrets management, penetration
  testing and incident response;
- backup procedures, alternate dispatch procedure and degraded-mode manuals;
- operator training material and competency checks.

Exit gate:

- a failed dependency, stale cycle, bad calculation, unavailable filing path or
  AI service outage cannot produce an approved dispatch artifact.

Implementation update, 9 July 2026:

- `aeroroute-contracts` publishes the `assurance-readiness/v1` schema.
- `aeroroute-api` exposes `GET /api/v1/assurance-readiness`, which keeps
  `assurance_enabled=false`.
- `reference/assurance-readiness-2026-07-09.json` and
  `make assurance-readiness` verify that operational assurance remains blocked
  until requirements traceability, IV&V, release/data-cycle control, audit/SLO
  observability, security/incident response and fallback procedures are
  accepted.

Phase 19 completes the assurance-readiness gate only. It does not establish an
operator-approved quality management or safety assurance process.

## Phase 20 — Operator Approval And Controlled Rollout

Goal: deploy only through an operator-approved operational procedure.

Deliverables:

- regulator/principal-inspector submission pack where applicable;
- operator manuals/procedures updates;
- EFB or dispatch-system authorization package if used operationally;
- parallel-run campaign against the incumbent dispatch process;
- acceptance report, open limitation list and go/no-go decision;
- production release tag tied to operator, fleet, data cycle and manuals
  revision.

Exit gate:

- the operator formally accepts the system for its intended use and records the
  approval path. Until then, UI, API and exports continue to show
  non-operational limitations.

Implementation update, 9 July 2026:

- `aeroroute-contracts` publishes the `operator-approval-readiness/v1` schema.
- `aeroroute-api` exposes `GET /api/v1/operator-approval-readiness`, which
  keeps `ops_mode=simulator` and `operator_approval_enabled=false`.
- `reference/operator-approval-readiness-2026-07-09.json` and
  `make operator-approval-readiness` verify that controlled rollout remains
  blocked until operator acceptance, regulator submission, manuals/training,
  parallel-run evidence and go/no-go evidence are accepted.

Phase 20 adds an operator-approval gate only. It does not record acceptance,
authorize production dispatch use or remove any non-operational limitation.

## Architecture Changes Required

- Add an `ops_mode` boundary: `simulator`, `ops_candidate`,
  `approved_operator_build`.
- Move all operational outputs behind an approval-state machine.
- Add data-source contracts with license, cycle, timestamp, quality and expiry.
- Replace direct fallback-to-still-air behavior with operational blocking rules
  when weather is mandatory.
- Add aircraft capability and operator-approval models before ICAO filing.
- Add NOTAM/RAD/ATC and airspace restriction services before route filing.
- Add requirements traceability and evidence manifests to every release.
- Separate explanatory AI from dispatch authority; AI text may explain approved
  facts but must never authorize, alter or invent operational decisions.

## First Implementation Slice

The next safe engineering slice is not ICAO filing. It is the operational
readiness foundation:

1. Add a requirements/evidence schema in `aeroroute-contracts`.
2. Add an operational data-source model in `aeroroute-api`.
3. Add `ops_mode=simulator` as the only enabled mode.
4. Add tests proving operational modes cannot be enabled without required data,
   operator profile and approval evidence.
5. Add an operational gap dashboard in `aeroroute-web`.

## Versioned Evidence Baseline

Implementation update, 8 July 2026:

- `aeroroute-contracts` publishes JSON schemas for operational readiness
  evidence and the operational hazard log.
- `reference/operational-readiness-evidence-2026-07-08.json` is the current
  baseline for requirements, evidence gates and the simulator-only guardrail.
- `reference/operational-hazard-log-2026-07-08.json` is the current preliminary
  hazard log baseline.
- `make operational-readiness` validates that operational use remains disabled,
  required gates still block operations, and no baseline hazard is accepted
  without safety evidence.

These files are release evidence for the non-operational boundary. They are not
approval evidence for dispatch use.

Only after those gates exist should route filing, NOTAM, RAD, approved
performance and operator-specific dispatch workflows be implemented.

Implementation update, 8 July 2026:

- `aeroroute-api` exposes `GET /api/v1/operational-readiness`.
- `OPS_MODE=simulator` is the only active mode; requested operational modes are
  reported as blocked and never activate dispatch authority.
- The response publishes blocking gaps for missing operator profile, licensed
  operational data, safety case, requirements traceability and manual/procedure
  acceptance.
- `aeroroute-contracts` publishes the additive OpenAPI 0.9.0 schema.
- `aeroroute-web` displays the simulator-only operational readiness state and
  top blocking gaps in the main dashboard.
