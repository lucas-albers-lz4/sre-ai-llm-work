---
source_url: https://langfuse.com/docs/observability/features/alerts
source_type: docs
title: "Alerts — Langfuse"
author: "Langfuse (Langfuse GmbH / Finto Technologies Inc.)"
date_published: n.d. (living documentation; current as of 2026-08-29)
date_extracted: 2026-08-29
last_checked: 2026-08-29
status: current
confidence_overall: settled
issue: "#1069"
---

# Alerts — Langfuse

> Vendor-reference documentation for Langfuse's **shipped** Alerts feature —
> the concrete LLM-ops instantiation of SRE alerting: metric/score-driven alert
> conditions, an explicit severity state machine with named notification
> semantics, first-class no-data handling, and automation delivery channels
> (Slack, HMAC-signed webhook JSON, GitHub Actions `workflow_dispatch`) with a
> delivery-failure circuit breaker. Fills the "alerting on eval/guardrail
> score rates" gap the roadmap note (#320) listed as planned.

## Source Context

- **Type**: documentation (vendor product docs — Langfuse Alerts feature)
- **Author credibility**: Langfuse is a widely-used open-source LLM observability
  platform. This page is first-party, Markdown-first documentation of the
  shipped Alerts feature. Claims about what the feature does (states, conditions,
  no-data modes, automation contract, webhook schema) are authoritative for the
  product's intended behavior; they are vendor-authored and not independently
  benchmarked, but they describe a concrete shipped capability.
- **Scope**: Covers (1) alert creation (data source, metric, filters, condition
  operators, warning/alert threshold ladder, evaluation window, no-data modes,
  renotify), (2) all alert severity states and exactly which transitions notify,
  (3) pause/resume semantics, (4) automations and their three delivery channels,
  (5) the 5-consecutive-delivery-failure auto-disable guardrail, and (6) the
  full webhook payload JSON schema with HMAC verification. Does NOT cover:
  eval/experiment-specific alert wiring beyond score data sources, pricing
  (beyond the alert-count tiering note), telemetry ingestion, or security
  guardrails (see #321).
- **Sub-pages followed**: The page is self-contained. It links to the prompt-webhook
  page for the HMAC verification code ("Signature verification works identically
  to prompt webhooks"), which is already documented in the security-and-guardrails
  note (#321) — no additional fetch needed. The Automations page referenced by
  navigation was not a separate substantive sub-source for the claims here.

## Extracted Claims

### Claim 1: Alerts in Langfuse are driven by either observation-level operational metrics (e.g. `avg latency`, `count`, `p95 cost`) or by score metrics — including aggregating boolean scores where the average equals the share of scores that are `true` — with filters (model, tags, user ID, environment, Boolean value)
- **Evidence**: The "Configure the metric" step enumerates four data sources
  (`Observations`, `Scores (numeric)`, `Scores (categorical)`, `Scores (boolean)`)
  and the metric/filter model. The prose explicitly explains the boolean-average
  trick.
- **Confidence**: settled
- **Quote**: "For Boolean scores, the average value is the share of scores that are `true`. Use it to alert on rates such as policy-check passes or detected hallucinations."
- **Our assessment**: This is the core LLM-specific alerting contribution. An
  alert can target the *operation-level* signals (latency, cost, count) an SRE
  already understands, or the *quality* signals (scores) that are unique to LLM
  ops. The boolean-score-average trick converts a rate (policy-check pass rate,
  hallucination rate) into a single numeric threshold — directly operationalizing
  the "alert on curated LLM SLIs, not raw anomalies" guidance from
  `docs-google-sre-prodcast-01-03-alerting.md` (Claim 13) and the eval-score
  monitoring thesis of #195. The metric/measure pairs (avg latency, count, p95
  cost) map onto the Metrics API v2 aggregation primitives documented in #284.

### Claim 2: Alerts use a two-threshold ladder — an optional warning threshold plus a required alert threshold, compared via operators (`>`, `≥`, `<`, `≤`, `=`, `≠`) over a time window (e.g. 1 hour, 1 day, 1 week)
- **Evidence**: The "Set alert conditions" step table enumerates the operators,
  the alert threshold (required, "sets severity to ALERT"), the warning threshold
  (optional, "sets severity to WARNING"), and the window.
- **Confidence**: settled
- **Quote**: "Crossing this value sets severity to **ALERT**." / "Crossing this value (before the alert threshold) sets severity to **WARNING**." / "How far back each evaluation looks (e.g. `1 hour`, `1 day`, `1 week`)"
- **Our assessment**: The warning-then-alert threshold ladder is the classic
  two-stage severity model (heads-up before paging). For LLM ops the thresholds
  can be defined over score rates (Claim 1) as well as infra metrics, giving a
  "quality first degrades to WARNING, then crosses ALERT" escalation path. This
  corroborates and instantiates the general page-vs-ticket philosophy from
  #36 (the warning tier being the non-paging precursor).

### Claim 3: Langfuse maintains an explicit severity state machine — `UNKNOWN / OK / WARNING / ALERT / NO_DATA / PAUSED` — with defined notification semantics: breach always notifies, recovery always notifies, no-data notifies only under the notify-after-sustained-NO_DATA mode, and sustained severity notifies only when Renotify is enabled
- **Evidence**: The "Alert states" section defines each state and then lists the
  four notification rules ("When notifications fire:").
- **Confidence**: settled
- **Quote**: "Breach (`UNKNOWN | OK → WARNING | ALERT`): always notifies." / "Recovery (`WARNING | ALERT → OK`): always notifies." / "No data (`NO_DATA ↔ WARNING | ALERT | OK | UNKNOWN`): only notifies when no-data mode is **Notify after sustained `NO_DATA`**." / "Sustained severity (`WARNING → WARNING`, `ALERT → ALERT`): notifies only when **Renotify** is enabled."
- **Our assessment**: This is the most generalizable claim on the page — a clean,
  vendor-documented alert-lifecycle state machine with *explicit* notify semantics
  per transition. It distinguishes three things SREs conflate: breach (entering a
  bad state), recovery (leaving it), and sustained/persistence (staying bad).
  Recovery-always-notifies is the page-fatigue tradeoff (avoid infinite alerts on
  a healed condition) made concrete. This is exactly the "alert on curated SLIs"
  lifecycle model the alerting note #36 and Ch04/Ch05 material need as a
  reference.

### Claim 4: No-data is a handled first-class state with four modes — treat-missing-as-0 (default), keep-previous-severity, show-NO_DATA (record, no notify), and notify-after-sustained-NO_DATA (record + notify after configurable delay) — addressing the alert-storm-vs-page-fatigue tradeoff under sparse sampling
- **Evidence**: The "Advanced settings" no-data-handling table enumerates all
  four modes and their behavior.
- **Confidence**: settled
- **Quote**: "**Treat missing data as 0** (default) / Treat null as `0` and compare against thresholds" / "**Notify after sustained NO_DATA** / Record `NO_DATA` severity; send a notification after a configurable delay"
- **Our assessment**: Sparse or bursty LLM traffic makes "no data" a real
  operational state (an eval that stops being emitted, a generation that stops
  being called), not just an incidental gap. Treat-missing-as-0 is the
  lowest-signal default (a silent gap reads as "fine"); sustained-NO_DATA is the
  high-signal option that pages when the *absence* of data is itself alarming —
  directly relevant where sampling makes missing data meaningful. This instantiates
  the alert-storm-vs-page-fatigue balance the Ch04 on-call material discusses.

### Claim 5: Renotify is an explicit, opt-in mechanism — off by default (notify once per severity transition); when enabled, re-notifies every N minutes (1–10,080) while an elevated severity persists
- **Evidence**: The "Renotify" table enumerates the two modes.
- **Confidence**: settled
- **Quote**: "`Off` (default) / Notifies once on each severity transition" / "`Every N minutes` / Re-notifies every N minutes while severity persists (1–10,080 min)"
- **Our assessment**: Renotify-off-by-default is the healthy default (no alert
  spam); renotify-on is a deliberate choice for sustained/critical conditions
  where one notification could be missed. The 1–10,080 min range is a wide knob.
  Small but concrete design detail worth capturing for Ch04's alert-design
  guidance.

### Claim 6: Alert evaluability is bounded by a pause/resume mechanism — a paused alert skips all evaluations and freezes its severity at `PAUSED`; resuming sets it back to `ACTIVE` and schedules the next evaluation
- **Evidence**: The "Pause and resume" section.
- **Confidence**: settled
- **Quote**: "A paused alert skips all evaluations; its severity is frozen at `PAUSED`. Resuming sets it back to `ACTIVE` and schedules the next evaluation."
- **Our assessment**: Pause/resume is the operational handle for a noisy or
  temporarily-irrelevant alert without deleting it — the day-one response to an
  alert storm. The fact that severity freezes at PAUSED (rather than decaying)
  means resuming gives an immediate, clean next evaluation. Minor but completes
  the lifecycle picture.

### Claim 7: Notifications route through automations that pair a trigger (an alert severity change) with an external action — Slack message, HMAC-signed webhook JSON POST, or a GitHub Actions `workflow_dispatch` event
- **Evidence**: The "Automations" section describes the three action channels and
  the trigger/action pairing.
- **Confidence**: settled
- **Quote**: "Each automation pairs a **trigger** (an alert severity change) with an **action** (a notification sent to an external system)." / "**Slack** / Posts a formatted alert message to a Slack channel" / "**Webhook** / HTTP POST to your endpoint with an HMAC-signed JSON payload" / "**GitHub Actions** / Fires a `workflow_dispatch` event on a GitHub repository"
- **Our assessment**: The GitHub Actions `workflow_dispatch` channel is the most
  interesting for this corpus: an alert severity change can directly trigger a
  CI/CD runbook (self-healing, dataset refresh, experiment re-run) — closing the
  eval-loop automation gap the roadmap note (#320, Claim 6) flagged and matching
  the Ch03 runbook-and-agents theme. The HMAC webhook is a generic, auditable
  delivery contract.

### Claim 8: After 5 consecutive delivery failures, Langfuse automatically disables the automation's trigger; it must be manually re-enabled from the Automations page once the endpoint is restored
- **Evidence**: The note directly beneath the automation-linking instructions.
- **Confidence**: settled
- **Quote**: "After **5 consecutive delivery failures**, Langfuse automatically disables the automation's trigger. Re-enable it from the Automations page once the endpoint is restored."
- **Our assessment**: A concrete, extractable resilience pattern for alert
  notification plumbing: a circuit breaker that stops retrying a dead endpoint and
  requires human re-enablement. This prevents an unreachable webhook/Slack from
  silently accumulating failed deliveries while also forcing an explicit operator
  acknowledgement (avoiding silent re-enable loops). Directly relevant to Ch03/Ch04
  notification-infrastructure reliability and to the #321 delivery/HMAC discussion.

### Claim 9: The webhook delivers a versioned, HMAC-signed JSON payload that preserves the legacy `monitor` naming (`type`, `monitorId`, `permalink`) for backward compatibility, so existing integrations continue to work unchanged
- **Evidence**: The "Webhook payload" section shows the full schema and the
  compatibility note.
- **Confidence**: settled
- **Quote**: "The payload keeps the legacy `monitor` naming (`type`, `monitorId`, `permalink`) so existing integrations continue to work unchanged."
- **Our assessment**: Backward-compatible payload evolution (adding the new
  alert/model while keeping the old key names) is exactly the kind of change
  management that prevents pager outages on vendor updates. The payload includes
  the message title/body, severity, the evaluation timestamp window
  (fromTimestamp/toTimestamp), the view, filters, and window — enough for an
  external system to reason about the alert without another API call.

### Claim 10: On Langfuse Cloud, the number of alerts per organization is tiered by plan — 2 (Hobby), 20 (Core), 50 (Pro), 100 (Enterprise)
- **Evidence**: The opening note on the page.
- **Confidence**: settled
- **Quote**: "On Langfuse Cloud, the number of alerts per organization depends on your plan: **2** (Hobby), **20** (Core), **50** (Pro), and **100** (Enterprise)."
- **Our assessment**: A concrete capacity-planning constraint: an organization's
  total alert count is bounded by plan tier. Teams on lower tiers must consolidate
  alert definitions or use score-based single alerts that cover many conditions.
  Minor but a real operational limit.

## Concrete Artifacts

### Webhook payload JSON schema (verbatim from the "Webhook payload" section)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-07-10T10:30:00Z",
  "type": "monitor-alert",
  "apiVersion": "v1",
  "payload": {
    "monitorId": "monitor_abc123",
    "projectId": "proj_xyz789",
    "permalink": "https://cloud.langfuse.com/project/proj_xyz789/monitors/monitor_abc123",
    "message": {
      "title": "avg latency crossed alert threshold",
      "body": "avg latency is 1234 ms (threshold: 1000 ms) over the last 1 hour"
    },
    "severity": "ALERT",
    "timestamp": "2024-07-10T10:30:00Z",
    "fromTimestamp": "2024-07-10T09:30:00Z",
    "toTimestamp": "2024-07-10T10:30:00Z",
    "view": "observations",
    "filters": [],
    "window": "1h"
  }
}
```
Source: langfuse.com/docs/observability/features/alerts — "Webhook payload" JSON
code block, verbatim.

### Alert configuration model (from the alert-setup steps)
```
Data source : Observations | Scores (numeric) | Scores (categorical) | Scores (boolean)
Metric      : Aggregation + measure — e.g. avg latency, count, p95 cost
Filters     : model name, tags, user ID, environment, Boolean value, etc.
Operator    : >  ≥  <  ≤  =  ≠
Alert thr.  : required; crossing sets severity to ALERT
Warning thr.: optional; crossing (before alert) sets severity to WARNING
Window      : how far back each evaluation looks (e.g. 1 hour, 1 day, 1 week)

No-data modes:
  Treat missing data as 0            (default) — treat null as 0, compare against thresholds
  Keep the previous severity         — hold previous severity; send no notification
  Show severity NO_DATA              — record NO_DATA; send no notification
  Notify after sustained NO_DATA     — record NO_DATA; notify after a configurable delay

Renotify:
  Off (default)   — notifies once on each severity transition
  Every N minutes — re-notifies every N minutes while severity persists (1–10,080 min)
```
Source: langfuse.com/docs/observability/features/alerts — "Configure the metric",
"Set alert conditions", and "Configure advanced settings" step tables, verbatim.

### Severity state machine and notification rules
```
Severity  Meaning
UNKNOWN   Initial state — not yet evaluated
OK        Metric is within bounds
WARNING   Metric crossed the warning threshold
ALERT     Metric crossed the alert threshold
NO_DATA   Query returned no data and no-data mode is Show severity NO_DATA
          or Notify after sustained NO_DATA
PAUSED    Alert is paused; no evaluations run

When notifications fire:
  Breach       (UNKNOWN | OK → WARNING | ALERT):  always notifies
  Recovery     (WARNING | ALERT → OK):            always notifies
  No data      (NO_DATA ↔ WARNING|ALERT|OK|UNKNOWN): only when mode is
                Notify after sustained NO_DATA
  Sustained    (WARNING → WARNING, ALERT → ALERT): only when Renotify enabled
```
Source: langfuse.com/docs/observability/features/alerts — "Alert states" section,
verbatim.

## Cross-References

- **Corroborates**:
  - `docs-langfuse-metrics-overview.md` (#284) **Claim 5** (Metrics API v2 views:
    observations, scores-numeric, scores-categorical). The Alerts feature's data
    sources (Observations, numeric/categorical/boolean scores — this note, Claim 1)
    are the alerting-layer consumers of exactly those `observations` and score
    views, and the alert metric aggregations (avg latency, count, p95 cost) use the
    same aggregation primitives (#284, Concrete Artifacts -> "v2 Observations
    metrics"). Complementary layers: #284 covers the data/query side, this note the
    alert/threshold/notify side. No contradiction.
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 3** (Score data
    model — numeric/categorical/boolean/text) and **Claim 11** (online evaluation
    auto-scores production traces; evals are monitorable signals). Alerts consume
    those score types as alertable signals — the boolean-score-average rate alert
    (this note, Claim 1) is the concrete operationalization of #195's
    scores-are-monitorable thesis. Directionally aligned.
  - `docs-langfuse-glossary.md` (#255) **Claim 5** (Score is an annotation/eval
    output, typed numeric/categorical/boolean/text, attachable to
    traces/observations/sessions/dataset runs). The Alerts page's score data
    sources corroborate the same four-type score model used as alert inputs. No
    contradiction.
  - `docs-google-sre-prodcast-01-03-alerting.md` (#36) **Claim 13** (generalized
    anomaly detection does not work for alerting; alert on curated SLIs) and
    **Claim 1** (monitoring is async/pull, alerting is sync/push). Langfuse Alerts
    is a concrete, vendor-documented instantiation: it alerts on curated,
    operator-chosen metrics/thresholds, not anomalies, and treats the alert as a
    synchronous, actionable push. The two-threshold ladder (this note, Claim 2)
    and recovery-always-notifies (Claim 3) also mirror #36's page-vs-ticket and
    alert-fatigue philosophy. Confirms generic SRE alerting philosophy against a
    specific LLM-ops product.

- **Contradicts**: None requiring a contradiction issue.
  - The only apparent tension is with `docs-langfuse-roadmap.md` (#320) **Claim 6**,
    which listed alerting as *planned* ("Ship alerting for evals, metrics, and
    operational thresholds across delivery channels such as Slack, PagerDuty,
    webhooks, and email"). This page documents the Alerts feature as *shipped*. This
    is a **status/progress update within the same vendor** (planned → shipped), not
    an opposition in advice: the roadmap said alerting *will* be shipped, and this
    page confirms it *is*. Both claims are true at different points in time and do
    not lead to different guide guidance. Per MINER.md §4a (source disagrees on
    nothing material / claims differ only by status), no contradiction issue is
    filed; this note instead **extends/updates** #320's claim with the shipped spec.
    Note: this page routes alerting via Slack/webhook/GitHub Actions, whereas the
    roadmap also named PagerDuty and email as planned channels — a roadmap-vs-shipped
    channel-scope difference, not a correction of a shipped claim.

- **Extends**:
  - `docs-langfuse-roadmap.md` (#320) **Claim 6** (multi-channel alerting as
    planned). This page is the shipped realization of that roadmap item, adding the
    full operational spec (state machine, no-data modes, renotify, webhook schema,
    auto-disable guardrail) that the roadmap only previewed as intent.
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 11** (online eval →
    monitorable signals). This note supplies the alerting layer that turns online
    eval scores into threshold-based notifications, completing the monitoring half
    of the closed eval loop.
  - `docs-langfuse-security-and-guardrails.md` (#321) (HMAC-signed webhook /
    prompt-webhook verification). The Alerts webhook uses the same HMAC signature
    verification as prompt webhooks (this note, Claim 9 and its "Signature
    verification works identically to prompt webhooks" note); #321 documents the
    HMAC verification mechanics. This note does not re-extract the HMAC code — it
    extends the delivery-automation contract to the alerting feature.

- **Novel** (first appearances in the corpus):
  - **Boolean-score-average = share-of-true rate alerting** (Claim 1) — alerting on
    policy-check pass rate or detected-hallucination rate via a boolean score
    average. No prior note describes eval/guardrail *rate* alerting as an alert
    signal.
  - **The explicit severity state machine with per-transition notify semantics**
    (Claim 3) — the concrete `UNKNOWN/OK/WARNING/ALERT/NO_DATA/PAUSED` lifecycle with
    breach/recovery/no-data/sustained notify rules. No prior note documents a full
    vendor alert-lifecycle model.
  - **First-class no-data handling modes** (Claim 4) — treat-as-0 vs hold-previous
    vs NO_DATA vs notify-after-sustained-NO_DATA, plus renotify intervals (Claim 5).
  - **Delivery-failure circuit breaker** (Claim 8) — auto-disable after 5
    consecutive delivery failures with manual re-enable. No prior note covers
    notification-plumbing resilience.
  - **GitHub Actions `workflow_dispatch` as an alert channel** (Claim 7) — alert
    severity change triggering a CI/CD event; the alert→runbook bridge.
  - **The full webhook payload schema** (Concrete Artifacts) — the JSON contract
    with legacy `monitor` naming preserved for backward compat (Claim 9).

## Guide Impact

- **Chapter 02 (Observability)**: This is the alerting sink for the observability
  pillar. Specific additions:
  1. Alert on LLM quality signals, not just infra — the boolean-score-average rate
     alert (Claim 1) as the recommended way to alert on policy-check pass rate and
     detected-hallucination rate. Pair with the eval-score monitoring from #195.
  2. The score data sources (numeric/categorical/boolean, Claim 1) as the
     alertable surface, directly consuming the Metrics API v2 score views from #284.
  3. The severity state machine (Claim 3) as a reference lifecycle model for
     depicting alert states in the observability chapter.

- **Chapter 03 (Runbooks and Agents)**: Add the GitHub Actions `workflow_dispatch`
  alert channel (Claim 7) as a concrete alert→CI/CD runbook trigger — an alert
  severity change can dispatch a workflow (self-healing action, dataset refresh,
  experiment re-run), closing the automation loop flagged in #320. Also add the
  delivery-failure circuit breaker (Claim 8) as a pattern for runbook/notification
  plumbing reliability (after 5 consecutive delivery failures, disable and require
  human re-enable).

- **Chapter 04 (Oncall and Toil)**: Add the full alert-lifecycle model as the
  concrete severity/no-data/renotify design:
  1. The two-threshold warning/alert ladder (Claim 2) as the escalation pattern for
     LLM alerts.
  2. No-data handling modes (Claim 4) as the alert-storm-vs-page-fatigue tradeoff —
     treat-missing-as-0 is the silent default, notify-after-sustained-NO_DATA is the
     high-signal option for sparse/bursty LLM traffic where missing data is itself
     meaningful.
  3. Renotify-off-by-default and recovery-always-notifies (Claims 3, 5) as
     page-fatigue controls. Pause/resume (Claim 6) as the alert-storm handling
     tool. This directly extends and concretizes the Google SRE alerting philosophy
     from #36 with a shipped vendor implementation.

- **Chapter 05 (LLM Ops Reliability — monitoring and alerting)**: This is the
  primary destination. Add:
  1. Alert on eval/guardrail score *rates* (Claim 1) as the LLM-specific alert
     signal complementing latency/cost — e.g., alert when the detected-hallucination
     rate or policy-check failure rate crosses a threshold.
  2. The data-source/metric/filter model for building alert definitions (Claim 1,
     and the configuration table in Concrete Artifacts) as the reference for
     authoring alerts against observability and score data.
  3. The webhook automation contract (Claim 9, full schema in Concrete Artifacts)
     as the integration point for routing LLM alerts into external systems.

## Extraction Notes

- Source fetched 2026-08-29 via WebFetch from
  https://langfuse.com/docs/observability/features/alerts (the page serves plain
  Markdown to AI agents per its stated convention; fully readable, not paywalled).
  Quotes in Claims are copied character-for-character from the extracted page text;
  the JSON schema and table artifacts are reproduced verbatim from the page's
  code/step blocks. The Assayer should spot-check quotes against the live URL.
- **Do-not-treat-as-evidence**: the triage comment explicitly warned not to treat
  any "165× faster v4" banner as evidence. That marketing banner did not appear in
  the extracted Markdown body, but I deliberately extracted no performance claim
  from any banner/marketing copy; all claims here are from the substantive feature
  documentation.
- **Contradiction reconciliation**: The roadmap note (#320, Claim 6) listed
  alerting as *planned*; this page documents it as *shipped*. I treat this as a
  vendor status update (planned → shipped) rather than a genuine contradiction —
  it does not change guide advice and is fully consistent (the roadmap said it
  would ship; this confirms it did). Per MINER.md §4a I did **not** file a
  contradiction issue; I documented the reconciliation in Cross-References and the
  shipped spec here extends/updates #320's Claim 6.
- Candidate notes from `miner-related-notes.md` were each reviewed: the ones with
  substance for cross-references were `docs-langfuse-metrics-overview.md` (#284,
  metric/score query backend), `docs-langfuse-roadmap.md` (#320, alerting planned →
  shipped), `docs-langfuse-security-and-guardrails.md` (#321, HMAC webhook
  parallels), `docs-langfuse-glossary.md` (#255, score types), and the generic
  `docs-google-sre-prodcast-01-03-alerting.md` (#36, alerting philosophy). The
  remaining candidates were dismissed for this note: `docs-langfuse-mcp-server.md`
  (MCP surface, unrelated to alerts), `docs-langfuse-agent-skill.md` (agent
  conditioning skill, unrelated), `docs-langfuse-sdk-overview.md` (SDK
  instrumentation, no alerting claims), `docs-google-sre-data-processing-pipelines.md`,
  `docs-google-sre-eliminating-toil.md`, and `docs-google-sre-reliable-product-launches.md`
  (classic SRE chapters; no alerting/LLM overlap not already covered by #36).
  `blog-pagerduty-sre-agent-triage.md` (LLM-as-judge triage alerts) is
  thematically adjacent — it describes an agent *triaging* LLM-judge alerts rather
  than the alert-authoring/config contract here — noted but not cited as
  corroboration to avoid inventing a parallel.
- `confidence_overall` is set to **settled** (higher than the sibling Langfuse notes)
  because this page documents a **shipped** feature with concrete, verifiable
  protocol detail (state machine, JSON schema, delivery-failure threshold) — these
  are factual vendor specifications, not aspirational roadmap items or untested
  pattern claims. The alerting *patterns'* long-term value to practitioners remains
  a separate judgment, but the product behavior described is settled.
- No part of the source was paywalled; the page is fully public. No contradiction
  issue was filed (see reconciliation note above).
