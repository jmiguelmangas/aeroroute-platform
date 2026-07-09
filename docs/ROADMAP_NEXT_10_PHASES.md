# AeroRoute MLX — Roadmap: Next 10 Phases

**Status:** Proposed working roadmap, post `system-v1.0.0-rc1`
**Written:** 2026-07-09
**Audience:** Solo developer continuing implementation, coding agents (Claude Sonnet, low-cost tier)
**Baseline:** Version 6 HLD (`HLD.md`), `IMPLEMENTATION_CHECKPOINT_2026-06-27.md`, `RELEASE_CANDIDATE_1.md`, `OPERATIONAL_READINESS_PLAN.md`

---

## 0. Design principle

Each phase below is scoped to **one primary repository**, has an **exit criterion that can be checked mechanically** (a `make` target, a test, a diff), and requires **no open architectural decision** — the HLD has already made those decisions. This shape is intentional: it is meant to be executable by a low-cost/low-reasoning-effort Claude Sonnet session, one phase per session, without needing broad judgment calls. The only phases with real open-ended judgment (model bake-off, QLoRA promotion) are pushed to the end, after the rest of the system is reconciled and safe.

Context that motivated this roadmap: the MVP (HLD Phases 10–14) is complete and was frozen as `system-v1.0.0-rc1` on 2026-07-08. A post-MVP operational-readiness stream (HLD Phases 15–21) then landed across `contracts`/`api`/`web`/`platform`, culminating 2026-07-09 in an aircraft-capability slice. That work is currently **unpinned**: `aeroroute-platform/RELEASES.yaml` still points at `1.0.0-mvp` / `contracts 0.6.0` / `api 0.6.0`, while the real repos are already at `0.14.0`.

---

## Phase 1 — Re-pin and tag `system-v1.0.0-rc2`

**Repo:** `aeroroute-platform`

- Update `RELEASES.yaml` so every component pin matches the real `VERSION`/`pyproject.toml`/`package.json` in each repo (confirmed drift so far: `contracts` and `api` are at `0.14.0`, manifest says `0.6.0`; also re-check `optimizer`, `data`, `mlx`, `mlx_training`).
- Run `make check`, `make verify-live`, `make performance-live`.
- Tag all 8 repos coordinately as `system-v1.0.0-rc2` per HLD §21.7.

**Exit criterion:** `make release-verify` passes; identical tag exists on all 8 GitHub remotes.

---

## Phase 2 — Manifest integrity guardrail

**Repo:** `aeroroute-platform`

- Add a check to `release-verify` that fails if `RELEASES.yaml` pins disagree with the actual checked-out `VERSION`/`pyproject.toml`/`package.json` values.
- This directly reproduces (as a regression test) the drift found before Phase 1.

**Exit criterion:** the new check fails on the pre-Phase-1 state and passes after it; committed as a permanent CI gate.

---

## Phase 3 — Non-operational boundary audit

**Repos:** `aeroroute-api`, `aeroroute-web`, `aeroroute-platform`

- Grep every endpoint/screen touching `icao-fpl` or "validate" for `filing_enabled=false`, `active_mode=simulator`, and the mandatory disclaimer (HLD §2.2/§2.3).
- Add a contract or E2E regression test that fails if a future endpoint/screen omits these.

**Exit criterion:** new regression test passes today and would fail against a hypothetical endpoint that claims real ICAO filing.

---

## Phase 4 — Close Phase 0 governance items

**Repos:** all 8 (LICENSE files) + GitHub settings (no product code)

- Select an org license; add `LICENSE` to each repo (check the OpenAP LGPL-3.0 note from the checkpoint doc before choosing).
- Verify branch protection and required status checks on all 8 GitHub repos (`gh api repos/jmiguelmangas/<repo>/branches/main/protection`).

**Exit criterion:** checkpoint's "Required closure sequence" step 1 fully checked off.

---

## Phase 5 — `aeroroute-web` housekeeping

**Repo:** `aeroroute-web`

- Add code splitting to remove the large-chunk build warnings flagged in `RELEASE_CANDIDATE_1.md`.
- Bump `package.json` off `0.1.0` to reflect the real feature history.

**Exit criterion:** production build has no chunk-size warnings; version bumped with a changelog entry.

---

## Phase 6 — AIRAC progressive load / prefetch

**Repo:** `aeroroute-api`

- Implement the progressive cold-load/prefetch for large AIRAC graphs, deferred explicitly in the checkpoint doc.

**Exit criterion:** benchmark on a large graph meets the HLD §3.2 SLO targets.

---

## Phase 7 — Airport catalogue expansion

**Repo:** `aeroroute-data`

- Extend the catalogue beyond the current 45 airports; regenerate fixtures, checksums, and dataset manifest.
- Re-freeze the four reference routes (MAD-JFK, JFK-MAD, DXB-MAD, NRT-SFO) if their data changes.

**Exit criterion:** new `bundle_version` published with checksum and provenance recorded in the manifest.

---

## Phase 8 — Gemma 3 12B compatibility spike

**Repo:** `aeroroute-mlx-training`

- Run the HLD §48.1 / §13.5 acceptance checklist: pin checkpoint + revision, measure memory headroom on target Mac (gate ≥24 GB unified memory), JSON validity ≥99.5%, record Gemma terms acceptance (do **not** commit the acceptance record, per `OPERATIONS_RUNBOOK.md`).

**Exit criterion:** written compatibility report, pass/fail against every §48.1 gate.

---

## Phase 9 — 12B serving benchmark and model bake-off

**Repo:** `aeroroute-mlx`

- Benchmark 12B serving latency/memory against the already-validated 4B baseline.
- Run the Mistral/Qwen challenger bake-off on the quality corpus.

**Exit criterion:** documented, data-backed decision on default model (12B vs 4B fallback), not a preference call.

---

## Phase 10 — QLoRA smoke pipeline (conditional)

**Repo:** `aeroroute-mlx-training`

- Only if Phase 8/9 results justify it: build the missing `training/`/`publishing/` modules, run a 50–100 step smoke training run, verify adapter save/reload round trip.
- Promote the adapter only if it beats the prompt-only baseline on the HLD §13.9 gates; otherwise leave it documented as "not promoted" and keep prompt-only as the default.

**Exit criterion:** either a promoted, versioned adapter with an evaluation report, or an explicit "not promoted" record with the failing gate(s) named.

---

## Notes for execution with a low-cost model

- Do one phase per session; do not blend repos within a phase.
- Each phase's "Exit criterion" is the acceptance test — treat it as the definition of done, not a suggestion.
- Phases 1–7 are mechanical/checklist work against an already-frozen spec. Phases 8–10 involve real measurement and a judgment call (model selection, adapter promotion) and may warrant a higher-reasoning session or human review of the numbers before committing to a default.
- Any tag push or force-push to shared remotes should be confirmed explicitly before executing, regardless of which model is driving the session.
