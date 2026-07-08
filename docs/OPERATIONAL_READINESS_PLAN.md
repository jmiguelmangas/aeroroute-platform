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

Only after those gates exist should route filing, NOTAM, RAD, approved
performance and operator-specific dispatch workflows be implemented.
