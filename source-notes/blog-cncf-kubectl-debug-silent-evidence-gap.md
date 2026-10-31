---
source_url: https://www.cncf.io/blog/2026/05/18/what-kubectl-debug-doesnt-tell-you-the-silent-evidence-gap
source_type: blog-post
title: "What kubectl debug doesn’t tell you: The silent evidence gap"
author: "Shamsher Khan, CNCF Community Member"
date_published: 2026-05-18
date_extracted: 2026-10-31
last_checked: 2026-10-31
status: current
confidence_overall: emerging
issue: "#1964"
---

# What kubectl debug doesn’t tell you: The silent evidence gap

> A `kubectl debug` session can hold the only direct observation of a failing
> pod, but Kubernetes deliberately gives `EphemeralContainerStatus` no
> `lastState` and no `restartCount`, so the exit code, session duration, target
> container, and debug-container logs survive only until the next pod event —
> making the first responder’s notes the only durable incident record unless the
> findings are written out of band before exit. The API fact is reproducible and
> settled; the handoff and compliance consequences are reasoned rather than
> measured.

## Source Context

- **Type**: blog-post (CNCF community blog; practitioner write-up with
  runnable reproduction commands and a linked example repository).
- **Author credibility**: Shamsher Khan, CNCF Community Member. The post is
  grounded in the Kubernetes v1.32 API type definitions and a three-command
  reproduction on a stock 1.25+ cluster, not vendor marketing. The linked
  implementation (`github.com/opscart/k8s-causal-memory`) appears to be
  author-affiliated, so it is an example of a mitigation, not independent
  validation.
- **Scope**: Covers `kubectl debug` / ephemeral-container evidence retention:
  the API-field gap, a reproduction, the signal-loss table, incident-handoff
  impact, audit/compliance implications, ranked workarounds, and a proposed
  upstream `lastState` addition. Does **not** cover LLM-specific workloads,
  measured evidence-retention rates, or an accepted Kubernetes Enhancement
  Proposal (KEP). The AI/agent connection in this note is the Miner’s
  synthesis, clearly marked as such.

## Extracted Claims

### Claim 1: `EphemeralContainerStatus` in Kubernetes v1.32 has no `lastState` and no `restartCount`, unlike `ContainerStatus`; the omission is an explicit API design decision, not a kubectl bug
- **Evidence**: A side-by-side type listing drawn from the v1.32 API, plus the
  statement that ephemeral containers avoid restart semantics. The author then
  reproduces the observable consequence.
- **Confidence**: settled for the field absence (checkable against the API
  reference); emerging for the operational impact.
- **Quote**: "This is not a bug or missing feature — it is an explicit API design decision. The EphemeralContainerStatus type in the Kubernetes API (v1.32) does not include a lastState field:"
- **Our assessment**: Buy this. It is the load-bearing technical fact and it is
  independently checkable against the published API type. The guide should cite
  it as an upstream API limitation, not as a defect to file against `kubectl`.
  Because the field truly does not exist, no amount of post-hoc querying can
  recover the record — which is why the mitigation must happen at observation
  time.

### Claim 2: The evidence gap is reproducible in three commands on any Kubernetes 1.25+ cluster; immediately after exit, `{.status.ephemeralContainerStatuses[*]}` still shows the `exitCode` while `State.Terminated` is current
- **Evidence**: A deploy command, a `kubectl debug` command that sleeps 10
  seconds and exits 42, and a `jsonpath`/`jq` inspection command, followed by
  the actual JSON containing `"exitCode": 42`.
- **Confidence**: settled (self-verifiable reproduction).
- **Quote**: "You do not need a special cluster to see this. Any Kubernetes 1.25+ cluster works. Three commands confirm the gap."
- **Our assessment**: This is the strongest form of evidence in the post:
  anyone can run it. It also establishes the narrow observation window — the
  data is present right after exit and disappears later — which is the detail a
  guide or runbook must encode. A reader who only reads "exit codes are lost"
  will miss that capture is possible but time-bounded.

### Claim 3: The termination context is replaced by the next pod event — another container restart, a second debug session, or a reschedule — and there is no `lastState` fallback once that happens
- **Evidence**: The API semantics plus the reproduction: the `Terminated` block
  is present immediately after the session and then replaced on subsequent pod
  updates.
- **Confidence**: settled for the replacement behavior (API state is current
  state only); emerging for how often the window closes before an operator
  captures it.
- **Quote**: "The exit code is visible here — but only while this State.Terminated entry is still present."
- **Quote**: "There is no lastState to fall back on. Once the current state changes, the termination context is no longer accessible through the Kubernetes API."
- **Our assessment**: This is the actual failure mode: not "the API never
  exposes the data" but "the API exposes it transiently and silently stops."
  The silent transition matters more than the loss itself, because nothing
  signals that a previously observable record has become unavailable. The guide
  should treat the `Terminated` transition as the capture deadline.

### Claim 4: After the session terminates, `kubectl logs <pod> -c <debug-container>` returns NotFound, so the debug container’s stdout is not recoverable from the pod
- **Evidence**: A concrete `kubectl logs` invocation and the exact server error.
- **Confidence**: settled (reproduced command/error pair).
- **Quote**: "Error from server (NotFound): container \"debugger-xxxxx\" not found"
- **Our assessment**: Buy it. This closes the obvious escape hatch — "the exit
  code is gone, but I can just read the logs." Ephemeral containers have no
  retained log stream after termination, so the finding must be emitted to a
  durable sink *while the process is still running*, not collected afterward.
  The guide should not assume `kubectl logs` works for a completed debug
  container.

### Claim 5: `--target` is a kubectl CLI feature only and is not stored as an API field, so "which container was investigated" is a distinct loss from the exit code
- **Evidence**: The author’s explicit note after the reproduction command and
  the handoff example showing the missing target.
- **Confidence**: settled (CLI-flag vs API-field distinction).
- **Quote**: "Note: –target is a kubectl CLI feature that routes the debug container into the target container’s process namespace. The target container name is not stored as an API field on the pod object."
- **Our assessment**: Important because it is easy to conflate with the
  `lastState` gap. Even a future `lastState` field would not recover `--target`
  unless the proposal also persists it; the two losses have different fixes.
  For incident records, the target container is part of the finding’s meaning —
  an exit code without the container it came from is not actionable.

### Claim 6: Four investigation signals are lost on pod state change — exit code (only while `State.Terminated` is current), session duration (never available), target container (not an API field), and debug-container logs (inaccessible after termination)
- **Evidence**: The source’s signal-loss table.
- **Confidence**: settled for the signal inventory and API-field status;
  emerging for the practical impact on incident response.
- **Quote**: "These signals exist only transiently and are not preserved across pod state transitions."
- **Our assessment**: Adopt this as the checklist of what a capture mechanism
  must persist: `exit_code`, `duration_seconds`, `target_container`, and the
  debug log stream. A mitigation that saves only the exit code still leaves the
  handoff unable to answer "how long" or "what was targeted." The guide can
  reuse this four-field minimum as a concrete runbook requirement.

### Claim 7: SRE teams commonly encode findings in exit codes (e.g., 42 for connection-pool exhaustion, 1 for a missing config file), and those signals become unobservable after the pod state changes
- **Evidence**: The author’s stated convention, with two illustrative exit
  codes; no survey or measurement.
- **Confidence**: anecdotal (plausible convention, asserted from experience).
- **Quote**: "The exit code convention is particularly common in SRE workflows — exit 42 for “connection pool exhausted,” exit 1 for “config file missing.” Once the pod state changes, these signals are no longer observable through the Kubernetes API."
- **Our assessment**: Plausible and consistent with the corpus’s existing
  "exit code as machine-readable failure class" rule, but the prevalence claim
  is anecdotal. Use the mechanism, not the frequency. The guide-relevant point
  is that encoding a diagnosis in an exit code is only useful if the code is
  captured before the state transitions; otherwise the convention creates a
  false sense of a durable record.

### Claim 8: A live incident handoff can fail because the first responder’s notes are the only record; the next engineer cannot re-derive session duration, target container, or logs and has to start from scratch
- **Evidence**: A concrete 12-minute handoff narrative followed by the exact
  verification commands the second engineer would run and the "not available /
  not stored / container not found" results.
- **Confidence**: emerging (realistic scenario, not a measured incident study).
- **Quote**: "The handoff depends entirely on the first engineer’s notes. If those notes are incomplete — which happens during a live incident — the diagnostic context may no longer be observable through the Kubernetes API. The second engineer starts from scratch."
- **Our assessment**: This is the transferable operational lesson, and it maps
  to LLM-ops directly: an agent that attaches a debug container and reports
  back in prose has exactly the same problem — its report is the only record,
  and nothing in the cluster can validate it. The guide should require the
  first responder (human or agent) to externalise the observation before exit,
  because the handoff cannot reconstruct it later.

### Claim 9: PCI-DSS 10.3 audit-logging and SOC 2 access-activity requirements cannot be satisfied for ephemeral sessions through the Kubernetes API alone, because neither the `--target` container nor session duration is recorded
- **Evidence**: The author names the two frameworks and states the missing
  fields; no control-by-control mapping or auditor assessment is provided.
- **Confidence**: emerging (the field absence is settled; the compliance
  conclusion is the author’s reasoning, not an audit finding).
- **Quote**: "Because the Kubernetes API does not record the –target container name or session duration as API fields, it is currently impossible to answer “who looked at what container, and for how long” using standard Kubernetes audit logs alone for ephemeral container sessions."
- **Our assessment**: Buy the logical link — you cannot evidence an access
  activity you never recorded — but treat the framework conclusion as an
  engineering inference to confirm with compliance, not as legal advice. The
  guide should say "standard Kubernetes audit logs alone are insufficient for
  ephemeral debug sessions" rather than "non-compliant," because the
  organisation may have a separate access-logging path (bastion, SIEM, PAM)
  that satisfies the control.

### Claim 10: There are three practical mitigations with real trade-offs — write findings to a shared volume/external system before exit, run `kubectl logs -f` in a parallel terminal, or watch the pod API and snapshot the `Terminated` block before another controller mutates the pod
- **Evidence**: The enumerated workaround section, including the conditions
  under which each fails; plus the recommendation to route findings to an
  external audit log or SIEM.
- **Confidence**: emerging (mechanisms are concrete; reliability is not
  measured).
- **Quote**: "Note that kubectl logs -f requires the session to be actively writing to stdout and the user to be capturing before exit — not always possible during a live incident."
- **Quote**: "This requires a watch on pod modifications and assumes no other controller updates the pod before capture."
- **Our assessment**: The ranking is the useful part: the in-session write is
  the most reliable because it happens before the API loses the state, the
  parallel-log capture depends on pre-capture discipline, and the watch-based
  capture races any controller that touches the pod. The guide should prefer
  "write it out while you still have it" and present the watch API as a
  best-effort backstop, not a guarantee. Note that the author does not quantify
  failure rates for any option.

### Claim 11: Ephemeral containers were designed to avoid restart semantics — the specification defines them as "not restarted on failure" — so restart tracking and last-state preservation are excluded by design, an exclusion that dates to the v1.16 alpha
- **Evidence**: The Kubernetes specification language quoted by the author,
  plus the design-history paragraph.
- **Confidence**: settled for the specification and the v1.16 alpha history;
  emerging for the judgment that the original trade-off no longer fits current
  `kubectl debug` usage.
- **Quote**: "Ephemeral containers were introduced to support debugging without affecting pod lifecycle guarantees. Their design explicitly avoids restart semantics, which influences how their state is exposed in the Kubernetes API."
- **Quote**: "“not restarted on failure.” As a result, the restart tracking and last-state preservation mechanisms that apply to regular containers are excluded by design."
- **Quote**: "The design decision to exclude lastState made sense when ephemeral containers were introduced in alpha (Kubernetes v1.16). As kubectl debug becomes a standard incident response tool across the ecosystem, the absence of a termination record has real operational consequences."
- **Our assessment**: Buy the specification and history. The second sentence is
  the author’s argument from changed usage, which is reasonable but not proven;
  the guide should present it as the rationale for a proposed upstream change,
  not as evidence that the change will land. This is also why "just add
  `lastState`" is not a workaround teams can rely on today.

### Claim 12: The proposed fix is a minimal `lastState` on `EphemeralContainerStatus` storing only the most recent termination record, argued to be low-risk because ephemeral containers never restart; the natural owners are SIG Node or SIG Instrumentation, and no KEP is accepted
- **Evidence**: The author’s proposal section; no KEP number, PR, or accepted
  design is cited.
- **Confidence**: anecdotal (an idea, not an implemented or accepted change).
- **Quote**: "The lastState field could be added to EphemeralContainerStatus with minimal breaking changes, since ephemeral containers are never restarted. It would store only the most recent termination record."
- **Quote**: "The natural owners of such a proposal would be SIG Node — which owns the kubelet and container lifecycle — or SIG Instrumentation — which owns observability primitives."
- **Our assessment**: Mark this `[proposed]`, not `[settled]`. The risk
  argument is plausible — a non-restarting container needs at most one prior
  termination record — but the guide must not present it as available
  behaviour. Its value is as a "known upstream limitation" with a named owner,
  so teams know to capture externally rather than wait for the API.

### Claim 13: An author-affiliated example implementation (`opscart/k8s-causal-memory`, scenario `05-ephemeral-exit`) captures `container_name`, `target_container`, `exit_code`, `exit_class`, `duration_seconds`, and `node_name` at the moment of exit
- **Evidence**: A linked repository and scenario path, plus the captured
  record for a 10-second session exiting 42.
- **Confidence**: anecdotal (example implementation; no independent validation
  or adoption evidence).
- **Quote**: "An example implementation demonstrating this approach is available at github.com/opscart/k8s-causal-memory, with a reproducible scenario under scenarios/05-ephemeral-exit/."
- **Our assessment**: Treat as a pointer and a schema example, not as proof
  that the approach is reliable at scale. The six-field schema is useful: it is
  the four lost signals (`container_name`, `target_container`, `exit_code`,
  `duration_seconds`) plus classification (`exit_class`) and placement
  (`node_name`). The guide can recommend the schema without endorsing the
  implementation.

## Concrete Artifacts

**Three-command reproduction (verbatim from source):**

```bash
# Step 1 — Deploy a stable target pod:
kubectl run debug-target --image=nginx:alpine -n default
kubectl wait --for=condition=Ready pod/debug-target -n default

# Step 2 — Attach a debug session, run for 10 seconds, exit with a distinctive code:
kubectl debug debug-target -n default \
--image=busybox:1.36 \
--target=nginx \
-it -- sh -c "echo 'finding: connection pool exhausted'; sleep 10; exit 42"

# Step 3 — Immediately after exit, inspect the ephemeral container status:
kubectl get pod debug-target -n default \
-o jsonpath='{.status.ephemeralContainerStatuses[*]}' | jq .
```

**Observed ephemeral-container status immediately after exit (verbatim from
source):**

```json
{
"containerID": "containerd://...",
"image": "busybox:1.36",
"name": "debugger-xxxxx",
"ready": false,
"state": {
"terminated": {
"exitCode": 42,
"finishedAt": "2026-04-17T16:43:56Z"
}
}
}
```

**Post-termination log lookup failure (verbatim from source):**

```bash
kubectl logs debug-target -c debugger-xxxxx -n default
Error from server (NotFound): container "debugger-xxxxx" not found
```

**API field comparison (verbatim from source):**

```text
EphemeralContainerStatus:
containerID    string
image          string
name           string
ready          boolean
state          ContainerState
# lastState:   absent by design
# restartCount: absent by design

ContainerStatus:
containerID    string
image          string
lastState      ContainerState    ← preserves prior termination
name           string
ready          boolean
restartCount   integer           ← counts restarts
state          ContainerState
```

**Signal-loss table (verbatim cell text from source; the page renders it as an
HTML table, reproduced here in Markdown):**

| Investigation Signal | Visible After Pod State Changes? |
|---|---|
| Exit code | Only while current State.Terminated is present |
| Session duration | Not available |
| Target container (–target) | Not recorded as an API field |
| Debug container logs | Not accessible after termination |

**Handoff verification commands and results (verbatim from source):**

```bash
# How long was the debug session?
kubectl get pod my-pod -o jsonpath='{.status.ephemeralContainerStatuses[*]}' | jq .
# Duration: not available
# What container did they target?
# --target is a kubectl CLI flag — not stored in the API
# Can I see what they ran?
kubectl logs my-pod -c debugger-xxxxx
# Error: container not found
```

**Captured record from the example implementation (verbatim from source):**

```yaml
container_name:     debugger-1776446626
target_container:   nginx
exit_code:          42
exit_class:         ERROR
duration_seconds:   10.0
node_name:          opscart-m02
```

## Cross-References

- **Corroborates**: `source-notes/blog-cncf-inspektor-gadget-security-audit.md`
  — that note’s **Claim 7** describes a fixed-size eBPF ring buffer that
  "silently drop[s] events from other containers" and draws the lesson that the
  dangerous property is the *silence*, not the overflow; **Claim 11** adds that
  kernel-level tracing is coverage of the hooks a gadget implements, not a
  completeness guarantee. This source is the same failure class at the
  Kubernetes API layer: the record is not absent from the start, it is
  **silently replaced**, and nothing emits a drop counter for it. The shared
  rule for Ch02 is that evidence loss must be detectable — an empty observation
  window is not evidence of a quiet system. (Verified: Claim 7 and Claim 11
  headings and content re-read before citing.)

- **Extends**: `source-notes/blog-cncf-telemetry-that-matters-observability-pipelines.md`
  — that note’s **Claim 14** supplies the audit heuristic: "If this specific
  data stream stopped flowing tomorrow, what would we actually lose?" This
  source answers that question concretely for debug-session telemetry: you lose
  exit code, duration, target, and logs at the moment the pod state changes.
  The ephemeral-container stream is therefore a stream that *always* stops, by
  design, which makes it a useful worked example of why retention must be a
  design decision rather than a post-hoc query. Ch02 can pair the heuristic
  with this concrete loss inventory.

- **Extends**: `source-notes/docs-google-sre-incident-response.md` — that
  note’s **Claim 11** documents PagerDuty’s scribe-led information ledger that
  "captures actions, owners, and timestamps." This source identifies a
  precondition the ledger pattern assumes: the facts must exist to be recorded.
  For ephemeral-container investigations, the first responder’s ledger is the
  only durable record because the API does not retain the source data
  (**Claim 8** here). The guide’s incident-tooling section should therefore add
  a capture step to the scribe role for transient diagnostic sessions, not
  assume the cluster will answer follow-up questions.

- **Extends**: `source-notes/docs-google-sre-prodcast-01-09-postmortems.md` —
  that note’s **Claim 1** requires postmortems to include the stages and root
  causes, not just symptoms, and **Claim 6** identifies the timeline/stages as
  the most-missed mandatory element. This source shows a technical mechanism
  that makes the timeline unrecoverable: session duration and target are never
  recorded, and the exit code expires on the next pod event (**Claims 3, 6, 8**
  here). The practical implication for Ch01 is that a postmortem cannot be
  reconstructed later from the cluster; the evidence-capture step belongs in
  the live runbook, before the postmortem is written.

- **Contradicts**: None. No existing source note claims that
  `EphemeralContainerStatus` preserves termination history or that debug logs
  survive termination. The nearest audit/observability notes (cited above)
  agree on the broader principle. Checked `CONTRADICTIONS.md` (no `C-NNN`
  entries on Kubernetes debug evidence) and open `contradiction`-labeled issues
  (none on `kubectl debug` / ephemeral containers). No contradiction issue
  filed.

- **Novel**: First source note in the corpus on `kubectl debug`, ephemeral
  containers, or `lastState`. Specifically new: (1) the
  `EphemeralContainerStatus` vs `ContainerStatus` field gap and its design
  rationale; (2) the three-command reproduction and the transient observation
  window; (3) the four-signal loss inventory; (4) the incident-handoff failure
  narrative; (5) the PCI-DSS 10.3 / SOC 2 auditability gap for ephemeral
  sessions; (6) the ranked workarounds and their race conditions; (7) the
  `[proposed]` upstream `lastState` change with named SIG owners; (8) the
  six-field capture schema from the example implementation.

## Guide Impact

- **Chapter 01 (Incident Response → Postmortems, `guide/01-incident-response.md:107`)**:
  Add an evidence-capture requirement to the live-incident procedure: any
  finding observed through an ephemeral container must be written to a durable,
  external record **before** the session exits, including exit code, session
  duration, target container, and the relevant log excerpt [Claims 3, 6, 8].
  State that the Kubernetes API cannot reconstruct this later, so a postmortem
  timeline that omits it is not recoverable [Claims 1, 8; cross-ref
  `docs-google-sre-prodcast-01-09-postmortems.md` Claim 6]. This is a
  precondition for the existing "root causes, not just symptoms" rule, not a
  replacement for it.

- **Chapter 02 (Observability → Observability as a spectrum, `guide/02-observability.md:121`)**:
  Add "transient diagnostic observations are not telemetry" as a named
  limitation. The chapter currently frames observability as monitoring →
  on-demand analysis; this source shows a case where the on-demand query target
  is deleted by the next pod event [Claims 2, 3, 6]. Recommend capturing the
  `State.Terminated` block at the transition and piping debug-container output
  to a shared volume or SIEM before exit [Claim 10], and require the capture
  path to emit a visible failure signal rather than silently missing the
  window [Claim 3; cross-ref inspektor note Claim 7 on denial-of-visibility].
  Add the audit heuristic pairing from `blog-cncf-telemetry-that-matters-
  observability-pipelines.md` Claim 14.

- **Chapter 03 (Runbooks and Agents → The human incident-tooling baseline an agent populates, `guide/03-runbooks-and-agents.md:247`)**:
  Add a rule for agent-driven debugging: an agent that runs `kubectl debug`
  must persist the session record (target, exit code, duration, log capture)
  before the container exits, because the cluster will not retain it and the
  agent's prose report is otherwise the only record [Claims 6, 8, 10]. The
  existing section already makes the agent the scribe/timeline reconstructor;
  this source supplies the concrete failure mode when the scribe is the sole
  source of truth. Also update the pre-on-caller pattern
  (`guide/03-runbooks-and-agents.md:195`): agent findings must cite captured
  evidence, not only narrative, so the human can verify the diagnosis.

- **Chapter 04 (On-call and Toil → Follow-up rigor and data quality, `guide/04-oncall-and-toil.md:231`)**:
  Add a handoff checklist item for investigations that use ephemeral
  containers: record what container was targeted, how long the session ran,
  what the exit code meant, and where the logs were written [Claims 6, 8].
  Without it, the next on-caller starts from scratch and the follow-up root
  cause depends on incomplete notes [Claim 8]. This is a low-cost toil
  reduction: one capture step prevents repeated investigation.

- **Chapter 06 (Security and Trust → Agent auditability is becoming a compliance expectation, `guide/06-security-and-trust.md:587`)**:
  Add that standard Kubernetes audit logs alone cannot answer "who looked at
  what container, and for how long" for ephemeral debug sessions, because
  `--target` and duration are not API fields [Claim 9]. Recommend routing debug
  session records to an external SIEM/audit log at the application level
  [Claim 10] and mark the upstream `lastState` proposal as `[proposed]`, not
  available [Claim 12]. Note that the PCI-DSS/SOC 2 conclusion is an
  engineering inference to validate with compliance, not a legal determination.

## Extraction Notes

- Read the full article (single page, ~2.4k words). The linked
  `github.com/opscart/k8s-causal-memory` repository and the Kubernetes
  ephemeral-containers/kubectl-debug docs were **not** deep-read; the note’s
  claims are scoped to what this post states. The repository is treated as a
  pointer/schema example only, per the Prospector’s author-affiliation caveat.
- No paywall; the page was fully readable via direct fetch.
- Quotes were copied character-for-character from the rendered page, including
  curly quotes/apostrophes and the source’s en dash in “–target” where it
  appears in prose. Code blocks reproduce the source’s line breaks. The
  signal-loss table and API comparison are reproduced as shown, with the table
  converted from HTML to Markdown and the API listing kept as a `text` block.
  No quote splices non-adjacent sentences.
- The page has an image caption rendered as "MAGE: ContainerStatus vs
  EphemeralContainerStatus side-by-side comparison showing lastState
  present/absent" (apparently a missing "I" in "IMAGE"). It is not used as
  evidence; the field comparison above is from the page’s code listing.
- `confidence_overall: emerging` — the API field absence and the reproduction
  are settled, but the handoff narrative is illustrative, the compliance
  conclusion is not an audit finding, the workaround reliability is not
  measured, the single example implementation is author-affiliated, and the
  `lastState` fix is an unaccepted proposal. Do not promote the KEP or the
  PCI-DSS/SOC 2 conclusion to settled.
- `miner-related-notes.md` candidates (10), each cited or explicitly dismissed
  per MINER.md §4:
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed; retail/gaming
    SLO granularity and user-experience alignment, no evidence-capture or
    Kubernetes debugging content.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — dismissed;
    multi-agent security platform architecture, not runtime diagnostic evidence
    retention.
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` — dismissed;
    sociotechnical complexity and incident mental models, no API evidence loss.
  - `docs-google-sre-eliminating-toil.md` — dismissed; toil taxonomy and
    measurement, no debug-session evidence.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — dismissed;
    imperative vs declarative change workflows, unrelated.
  - `docs-google-sre-reliable-product-launches.md` — dismissed; launch
    coordination checklists, unrelated.
  - `docs-google-sre-on-call.md` — dismissed; pager-load anatomy and alerting
    hygiene, not incident-handoff evidence capture.
  - `docs-google-sre-prodcast-03-01.md` — dismissed; SRE methodology and
    feedback cycles, unrelated.
  - `docs-litellm-anthropic-advisor-tool.md` — dismissed; within-request advisor
    model composition, unrelated.
  - `docs-litellm-completion-function-call.md` — dismissed; function-calling
    capability predicates, unrelated.
- Additional notes found by searching `source-notes/` (beyond the candidates):
  `blog-cncf-inspektor-gadget-security-audit.md`,
  `blog-cncf-telemetry-that-matters-observability-pipelines.md`,
  `docs-google-sre-incident-response.md`,
  `docs-google-sre-prodcast-01-09-postmortems.md`.
- Cross-reference claim numbers were re-read and verified against each cited
  note before writing (MINER.md §4b). No contradiction found; no contradiction
  issue filed. The candidates file `miner-related-notes.md` was read but not
  committed.
