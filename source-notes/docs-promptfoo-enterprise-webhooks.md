---
source_url: https://www.promptfoo.dev/docs/enterprise/webhooks
source_type: docs
title: "Promptfoo Enterprise: Webhook Integration — The Five-Event Contract, the Update-Consolidation Rule, and the Undocumented Delivery Half"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-09
date_extracted: 2026-10-09
last_checked: 2026-10-09
status: current
confidence_overall: emerging
issue: "#1640"
---

# Promptfoo Enterprise: Webhook Integration

> The vendor's outbound webhook contract for the eval/red-team control plane:
> five `issue.*` event types over an org-scoped subscription
> (`POST /api/webhooks`, Bearer auth, secret issued at creation), a
> where-multiple-attributes-change-at-once **consolidation rule** that collapses
> a status+severity update into a single `issue.updated`, a JSON payload carrying
> the complete current issue state plus a human-readable `changes` string array,
> and HMAC SHA-256 signing delivered in `X-Promptfoo-Signature` — and, for the
> guide's purposes, the entire documented **absence** of the reliability half:
> no retry, no delivery guarantee, no ordering, no timeout, no backoff, no
> dead-letter queue, and no delivery log, so an integration built on this page is
> a best-effort notification channel until the operator supplies reconciliation.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Enterprise
  "Enterprise > Webhook Integration" page). The page opens with the gating
  notice "This feature requires [Promptfoo Enterprise](/docs/enterprise/)." Page
  footer: "Last updated on **Oct 9, 2026** by **mldangelo-oai**".
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own Enterprise control plane, so
  authoritative *as a specification* — the event-type identifiers, endpoint
  path, request-body fields, header name, and signing algorithm below are the
  vendor's own contract and are string-checkable by anyone with an Enterprise
  tenant. It is **not** measurement and it is **not** an operational contract:
  the page publishes no delivery guarantee, no retry schedule, no ordering
  promise, and no volume/latency figure, and the feature is Enterprise-gated so
  none of it is verifiable in the open-source repository (see Extraction Notes).
  The integration-scenario prose ("makes it easy to keep your SIEM system
  synchronized") is marketing-adjacent framing, not evidence.
- **Scope**: Covers what an "issue" is, the five webhook event types and the
  consolidation note, subscription creation via `POST /api/webhooks`, the payload
  structure plus the `issue.updated` `eventData`, HMAC signature verification
  with a Node.js sample, and three example integration recipes (SIEM, task
  tracking, custom notification). Does **not** cover delivery reliability of any
  kind (retry, backoff, ordering, timeout, dead-letter, delivery logging), secret
  rotation or retrieval, webhook update/delete/list endpoints, payload size
  bounds, rate limits, at-least-once vs at-most-once semantics, or any
  measurement of the surface.
- **Relationship to sibling pages**: this is the corpus's coverage of the
  Enterprise webhook *delivery* mechanism that
  `source-notes/docs-promptfoo-enterprise-audit-logging.md` explicitly recorded
  as absent ("no webhook delivery" of audit events; its Concrete Artifacts → "No
  audit sink" section lists the same five `issue.*` events this page specifies).
  Same Enterprise doc tree, same first-party-spec framing, same `emerging`
  confidence choice as the audit-logging (#1589), findings (#1610), and
  guardrails (#1611) notes.

## Extracted Claims

### Claim 1: The webhook surface is five event types over an "issue" object, where an issue is a red-team-detected security vulnerability — the control plane's finding record, not an operational or eval event
- **Evidence**: The "What is an Issue?" section defines the object, and the
  "Event Types" section enumerates exactly five identifiers. The word "issue"
  is the same object the findings note dispositions (status, severity, comments)
  and the same object the audit-logging note records are *not* covered by audit
  logging.
- **Confidence**: settled (the definition and the five-item list are the
  vendor's own contract; the "closed list" reading is supported by the
  enumeration but the page does not literally say "exhaustive")
- **Quote**: "An \"issue\" in Promptfoo Enterprise refers to a **security vulnerability** or weakness detected during AI security testing. Issues are created when red team plugins identify potential security risks such as prompt injections, data leaks, harmful content generation, or other AI-specific vulnerabilities."
- **Our assessment**: Buy it, and note the scope it implies: the webhook
  surface is a **finding-notification** channel, not a run/eval telemetry feed.
  Every event is a mutation of a red-team finding; there is no `scan.started`,
  `eval.completed`, `guardrail.tripped`, or audit event. So a team that wants
  real-time signal on *the act of scanning* or on *runtime guardrail
  interventions* gets nothing here — consistent with the audit-logging note's
  control-plane/data-plane boundary (its Claim 2) and the guardrails note's
  data-plane telemetry (its Claim 3), which are both "tracked separately" from
  this stream. For the guide: an eval platform's webhook fan-out is scoped to
  the product's *finding* object, and a subscriber should enumerate the event
  types before assuming the stream covers the operations that matter.

### Claim 2: The consolidation rule is a state-diff design decision — when multiple attributes change simultaneously, a single `issue.updated` is emitted *instead of* the specific `issue.status_changed` / `issue.severity_changed` events, so consumers cannot assume one event per attribute transition
- **Evidence**: The `>` Note block immediately after the five-item event list.
  It gives the exact motivating example (both status and severity changing) and
  the stated rationale (preventing multiple notifications for one logical
  operation).
- **Confidence**: settled (the rule is stated verbatim as a documented
  behavior; the consumer-side consequence below is our derivation)
- **Quote**: "Note: When multiple properties of a vulnerability are updated simultaneously (for example, both status and severity), a single issue.updated event will be sent rather than separate issue.status\_changed and issue.severity\_changed events. This helps prevent webhook consumers from receiving multiple notifications for what is logically a single update operation."
- **Our assessment**: This is the single most important design fact on the page,
  and it is a **fan-in** decision the consumer must design around: the specific
  event types (`issue.status_changed`, `issue.severity_changed`) are emitted only
  for *isolated* changes, so a subscriber that filters on
  `events: ["issue.severity_changed"]` silently misses every severity change
  that co-occurs with a status change (or with any other simultaneous
  attribute update), because that update arrives as `issue.updated` and not
  under its own type. The correct subscription for a complete picture is
  `issue.created` + `issue.updated` (+ optionally the others for convenience),
  and the consumer must then parse `eventData.changes` (Claim 9) rather than
  trust the event type to say what happened. Contrast this with the corpus's
  Langfuse alerting webhook, which fires one delivery per severity transition
  (`docs-langfuse-alerts.md` Claim 7) — the two vendors choose opposite
  fan-out/attle semantics, and neither is wrong, which is exactly why the guide
  must state the rule rather than assume a convention: **an event-type filter is
  not a complete filter when the producer reserves the right to fold events.**

### Claim 3: The event-type descriptions and the task-tracking recipe both suggest a status-only subscription, which the consolidation rule makes incomplete — an internal footgun the page states but does not reconcile
- **Evidence**: `issue.status_changed` is described as "Triggered when a
  vulnerability's status changes", and the "Task Tracking Integration" section
  recommends "Listen for `issue.status_changed` if you only care about
  vulnerability status transitions" — while the consolidation Note (Claim 2)
  says a status change bundled with any other attribute change arrives as
  `issue.updated` only.
- **Confidence**: settled (all three sentences are on the page verbatim; the
  tension between them is directly observable, not inferred)
- **Quote**: "`issue.status_changed`: Triggered when a vulnerability's status changes (e.g., from open to fixed)" / "Listen for `issue.status_changed` if you only care about vulnerability status transitions"
- **Our assessment**: This is the page's most actionable trap, and we record it
  as a **documented footgun rather than a contradiction** (see Cross-References →
  Contradicts for why no contradiction issue was filed). A literal reading of the
  bullet says a status transition fires `issue.status_changed`; the Note says a
  status transition bundled with a severity edit does not. The two statements are
  reconcilable — the bullet is true only for *isolated* transitions — but the
  page never attaches that qualifier to the bullet or to the recommendation, so a
  reader who wires `events: ["issue.status_changed"]` because the docs told them
  to "only care about status transitions" will miss transitions they explicitly
  asked for, with no error and no dead-letter to notice it. The guide-safe rule:
  **subscribe to the coarse event that carries all changes (`issue.updated`) and
  discriminate in the consumer, never the reverse** — a fine-grained event
  subscription is only complete when the producer guarantees one event per
  transition, and this producer explicitly does not.

### Claim 4: The payload carries the complete current issue state plus an event-specific `eventData` block, and for `issue.updated` that block adds a `changes` array and an optional `userId` — so a single delivery is both a notification and a full-state snapshot
- **Evidence**: The "Webhook Payload Structure" section's base JSON, the
  separate `issue.updated` JSON, and the three-item bullet list of what the
  structure lets you do.
- **Confidence**: settled (both payloads and the interpretive list are
  verbatim)
- **Quote**: "This structure allows you to: 1. See the complete current state of the issue 2. Understand what specific attributes changed 3. Track who made the change (if applicable)" / "\"userId\": \"user-123\" // If the update was performed by a user"
- **Our assessment**: Buy it, and note the two useful properties. (1)
  **Full-state deliverable**: the payload carries the whole `issue` object
  (`pluginId`, `status`, `severity`, `organizationId`, `targetId`, `providerId`,
  `weakness`, `history`, timestamps), so a consumer does not need a follow-up
  `GET` to reconcile the event — the delivery *is* the snapshot. That is a
  better design than thin change-events that force a read-back, and it is what
  the audit-logging note's Claim 6 found the audit record lacks (a before/after
  pair). (2) **Attribution exists on the change**: `userId` is present on
  `issue.updated` when a human made the update — the attribution the findings
  note observed is *not* documented on the disposition record itself (its
  Claim 2) is here supplied on the outbound event. The caveat: `userId` is
  optional ("if applicable"), so a system-initiated or unknown-actor change
  carries no attribution, and the page does not say what a missing `userId`
  means.

### Claim 5: Subscriptions are created with `POST /api/webhooks` under a Bearer token, are organization-scoped, and receive a signing secret at creation — with no documented update, delete, list, or secret-rotation operation
- **Evidence**: The "Managing Webhooks" and "Creating a Webhook" sections: one
  endpoint (`POST /api/webhooks`), one auth header, a five-field body
  (`url`, `name`, `events[]`, optional `teamId`, `enabled`), and the
  secret-issuance sentence. No other method or endpoint appears on the page.
- **Confidence**: settled (the endpoint, body, and secret note are verbatim; the
  management-operation absence is an absence on *this* page, recorded as
  undocumented rather than nonexistent per this corpus's convention)
- **Quote**: "Webhooks can be managed via the API. Each webhook is associated with an organization and can be configured to listen for specific event types." / "Upon creation, a secret is generated for the webhook. This secret is used to sign webhook payloads and should be stored securely."
- **Our assessment**: Buy the creation contract; flag the secret-handling gap,
  which is the operational part the page skips. The secret is issued once, at
  creation, and the page gives no retrieval path and no rotation path — so
  "store it securely" is the whole of the guidance, and an operator who loses
  the secret has no documented remedy short of deleting and recreating the
  webhook (which itself is not documented). This is the same class of gap the
  audit-logging note recorded for service-account keys (its Claim 3: no
  rotation event), here on the egress credential rather than the retrieval
  credential. Also note the scope: the webhook is org-wide with an optional
  `teamId`; the page does not document what `teamId` actually scopes (delivery
  filtering? payload fields? authorization?) beyond listing it as an optional
  field.

### Claim 6: Signatures are HMAC SHA-256 over `JSON.stringify(payload)` and delivered in `X-Promptfoo-Signature`; the Node sample verifies with `crypto.timingSafeEqual` and returns 401 on mismatch — but signing the *serialized* body means the receiver must verify the raw bytes, not a re-serialized parse
- **Evidence**: The "Verifying Webhook Signatures" section: one prose sentence
  naming the algorithm and header, plus the complete Node.js example
  (reproduced verbatim in Concrete Artifacts) showing
  `.createHmac('sha256', secret).update(JSON.stringify(payload)).digest('hex')`,
  `crypto.timingSafeEqual`, and `res.status(401).send('Invalid signature')`.
- **Confidence**: settled (algorithm, header name, and sample code are the
  vendor's own contract); the integration footgun below is our derivation from
  the documented signing input
- **Quote**: "To verify that a webhook is coming from Promptfoo Enterprise, the payload is signed using HMAC SHA-256. The signature is included in the `X-Promptfoo-Signature` header."
- **Our assessment**: Buy the scheme — HMAC SHA-256 is the right primitive and
  `timingSafeEqual` is the right comparison — and extract the **integration
  footgun**: the vendor signs `JSON.stringify(payload)`, i.e. the *serialized
  request body*, so the receiver must compute the HMAC over the exact raw bytes
  it received, **not** over a re-serialization of a parsed object. Parsing to
  JSON and re-stringifying can reorder keys, change whitespace, or alter
  unicode escapes, producing a signature mismatch on legitimate traffic — which
  the sample itself partially masks by spreading the check across an already-
  parsed `req.body`. The guide rule: *capture the raw body before any JSON
  middleware, verify the HMAC against those bytes, then parse.* Second-order
  note: the sample's `timingSafeEqual` will throw (not just return false) if the
  two buffers differ in length, so a malformed or absent signature header can
  crash the handler rather than 401 — worth a length guard in production.

### Claim 7: The page documents no delivery contract whatsoever — no retry, no backoff, no ordering guarantee, no timeout, no dead-letter queue, and no delivery log — so the webhook is a best-effort notification channel and the only documented failure path is the receiver's own 401
- **Evidence**: Full-page read of the fetched page (2026-10-09): the words
  *retry*, *backoff*, *ordering*, *timeout*, *dead-letter*, *at-least-once*,
  *at-most-once*, *delivery guarantee*, and *delivery log* do not appear
  anywhere; the only status code on the page is the receiver's `401`, and the
  only failure handling is the receiver rejecting a bad signature. The
  "Managing Webhooks" prose stops at "managed via the API".
- **Confidence**: settled as a description of what this page documents (full-text
  read); the *product-level* absence of retry is not established by its absence
  from one page, so this is recorded as undocumented, not nonexistent
- **Quote**: "Promptfoo Enterprise provides webhooks to notify external systems when security vulnerabilities (issues) are created or updated."
- **Our assessment**: This is the page's highest-value finding for the guide, and
  it is an **absence with operational teeth**. The vendor commits to emitting an
  event; it commits to nothing about *delivering* it. So an operator wiring
  promptfoo findings into a SIEM or ticket queue has no documented answer to the
  questions that decide whether the integration is trustworthy: if the endpoint
  is briefly down, is the event retried or lost; if it is retried, is it
  deduplicated; if events arrive out of order, does a stale `issue.updated`
  overwrite a newer one; is there a delivery log to detect a silent gap? The
  page instead routes all reliability to the consumer, who does not own the
  producer. This is the direct mirror of the corpus's Langfuse finding — that
  vendor documents a delivery-failure circuit breaker and a versioned webhook
  schema (`docs-langfuse-alerts.md` Claims 7, 8) — and it is the second instance,
  after the guardrails note's Claim 13, of the recurring promptfoo
  "vendor documents the contract and omits the failure semantics" pattern. The
  guide rule: **an outbound webhook is best-effort until the vendor documents
  retry, dedup, ordering, and a delivery log; absent those, build reconciliation
  that polls the source of truth and treats the webhook as an optimization, not
  the record.**

### Claim 8: The SIEM recipe asserts the stream "makes it easy to keep your SIEM system synchronized" while the page documents no delivery guarantee — a payload-completeness claim is presented as if it were a synchronization guarantee
- **Evidence**: The "SIEM Integration" paragraph's two sentences, read against
  Claim 7. The claim is about the *content* of each delivery ("The complete
  vulnerability state provided with each webhook"), not about *whether* each
  state change is delivered.
- **Confidence**: settled as a description of what the page asserts; the gap
  between content-completeness and delivery-completeness is our reading
- **Quote**: "When integrating with a SIEM system, you might want to listen for `issue.created` and `issue.updated` events. This allows your security team to be notified of new security vulnerabilities detected by Promptfoo Enterprise and track their resolution. The complete vulnerability state provided with each webhook makes it easy to keep your SIEM system synchronized."
- **Our assessment**: Do not buy the synchronization framing, and say why in the
  guide rather than dropping the citation. The recipe is correct on the two
  points it makes explicitly — subscribe to `issue.created` + `issue.updated`
  (i.e. the coarse carrier events, per Claims 2–3), and treat each delivery as a
  full-state snapshot (Claim 4). What it elides is the third requirement: a
  SIEM is "synchronized" only if every state change *arrives*, and this page
  documents no mechanism that makes arrival reliable (Claim 7). A dropped
  `issue.updated` is not self-healing — the SIEM will simply retain the
  previous state, and because each event carries the full current state rather
  than a delta, there is no *missing-delta* signal that a reconciler could
  detect without polling promptfoo. So the honest formulation is: **payload
  completeness makes each *received* event sufficient; it says nothing about
  event frequency, and a state-snapshot stream with no delivery guarantee yields
  a SIEM that is eventually-consistent-by-polling, not by webhook.** This is the
  cross-vendor caution the guide should carry wherever an AI platform advertises
  "push findings to your SIEM".

### Claim 9: The `issue.updated` diff is a human-readable string array (`eventData.changes`), not a structured field/from/to delta — consumers must parse free text to know what changed
- **Evidence**: The `issue.updated` payload sample, whose `eventData.changes`
  is `["status changed to fixed", "severity changed to low"]` and whose comment
  in the integration prose restates the same example as a customer-facing
  message ("Vulnerability status changed from open to fixed").
- **Confidence**: settled (the sample and the prose example are verbatim)
- **Quote**: "\"changes\": [\"status changed to fixed\", \"severity changed to low\"]" / "The `changes` array included with `issue.updated` events makes it easy to add appropriate comments to your task tracking system (e.g., \"Vulnerability status changed from open to fixed\")."
- **Our assessment**: Buy the field and flag its shape as the fragile part of the
  contract. `changes` is an array of *sentences*, not machine-enumerated
  transitions — there is no `{field, from, to}` object, no enumerated field
  vocabulary, and no stability promise on the sentence format. A consumer that
  needs to branch on "severity went up" or "status moved to fixed" must either
  string-match the human text (brittle against wording changes) or ignore
  `changes` and diff the full `issue` object against its own stored previous
  state (which requires the consumer to keep that state, since the payload
  carries only the current value — Claim 4). The guide rule worth stating:
  **when a vendor delivers a diff as prose, treat it as display text, not as an
  API — compute your own diff from the full-state payload, and pin the previous
  state yourself.** This is also why the consolidation rule (Claim 2) and this
  claim travel together: the fold hides *which* events fired, and the
  human-readable `changes` is the only window into what actually changed.

### Claim 10: The page is a contract specification with no operational or quantitative content of any kind, and the feature is Enterprise-gated — so the documented surface is the auditable surface and everything else is unknown rather than absent
- **Evidence**: Full-page read: no metric, threshold, volume, latency, retention,
  or cost figure; no schema beyond the two example payloads; the Enterprise gate
  in the first line. The "complete API documentation" pointer is not given here
  (unlike the audit-logging page, which deferred to an API Reference this corpus
  has repeatedly found unfetchable — its Claim 9).
- **Confidence**: settled as a description of what the page does and does not
  say (full-text read); the *product-level* absence of features is not
  established by their absence from one page
- **Quote**: "This feature requires [Promptfoo Enterprise](/docs/enterprise/)."
- **Our assessment**: This is the calibration claim that governs how every other
  claim above may be cited, and it mirrors the audit-logging and findings notes'
  conclusion for their sibling pages: **the documented surface is the auditable
  surface.** Record two explicit non-claims for the Assayer and Smith. (1)
  **No delivery semantics** — Claim 7's absences are absences *on this page*; the
  page does not say "no retry", it simply never mentions retry, so the guide must
  say *undocumented*, not *nonexistent*. (2) **No measurement** — nothing here
  may be turned into a metric, and there is no retention statement for any
  webhook secret or delivery history. Because the feature is Enterprise-gated,
  none of it is checkable against the open-source repository, which is why
  `confidence_overall` is `emerging`: the enumerated facts are a *specification*
  we trust because it is the vendor's contract, and the operational behavior
  behind them is unverified.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(https://www.promptfoo.dev/docs/enterprise/webhooks). Code blocks are
reproduced as the page renders them; the create-webhook block is a single
fenced block on the page whose HTTP header lines and JSON body are shown
consecutively, so it is split here for readability with no wording changes.

### Event types (verbatim, "Event Types")

- `issue.created`: Triggered when a new security vulnerability is detected and created
- `issue.updated`: Triggered when a vulnerability is updated (such as when multiple attributes change at once)
- `issue.status_changed`: Triggered when a vulnerability's status changes (e.g., from open to fixed)
- `issue.severity_changed`: Triggered when a vulnerability's severity level changes
- `issue.comment_added`: Triggered when a comment is added to a vulnerability

### Creating a webhook (verbatim, "Creating a Webhook")

```
POST /api/webhooks
Content-Type: application/json
Authorization: Bearer YOUR_API_TOKEN

{
  "url": "https://your-webhook-endpoint.com/callback",
  "name": "My SIEM Integration",
  "events": ["issue.created", "issue.status_changed"],
  "teamId": "optional-team-id",
  "enabled": true
}
```

### Base webhook payload (verbatim, "Webhook Payload Structure")

```json
{
  "event": "issue.created",
  "timestamp": "2025-03-14T12:34:56Z",
  "data": {
    "issue": {
      "id": "issue-uuid",
      "pluginId": "plugin-id",
      "status": "open",
      "severity": "high",
      "organizationId": "org-id",
      "targetId": "target-id",
      "providerId": "provider-id",
      "createdAt": "2025-03-14T12:30:00Z",
      "updatedAt": "2025-03-14T12:30:00Z",
      "weakness": "display-name-of-plugin",
      "history": [...]
    },
    "eventData": {
      // Additional data specific to the event type
    }
  }
}
```

### `issue.updated` payload (verbatim, "Webhook Payload Structure")

```json
{
  "event": "issue.updated",
  "timestamp": "2025-03-14T14:22:33Z",
  "data": {
    "issue": {
      // Complete issue data with the current state
    },
    "eventData": {
      "changes": ["status changed to fixed", "severity changed to low"]
    },
    "userId": "user-123" // If the update was performed by a user
  }
}
```

### Signature verification (verbatim, "Verifying Webhook Signatures")

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
}

// In your webhook handler:
app.post('/webhook-endpoint', (req, res) => {
  const payload = req.body;
  const signature = req.headers['x-promptfoo-signature'];
  const webhookSecret = 'your-webhook-secret';

  if (!verifyWebhookSignature(payload, signature, webhookSecret)) {
    return res.status(401).send('Invalid signature');
  }

  // Process the webhook
  console.log(`Received ${payload.event} event`);
  res.status(200).send('Webhook received');
});
```

### Integration recipes (verbatim, "Example Integration Scenarios")

- **SIEM Integration**: "When integrating with a SIEM system, you might want to listen for `issue.created` and `issue.updated` events. This allows your security team to be notified of new security vulnerabilities detected by Promptfoo Enterprise and track their resolution. The complete vulnerability state provided with each webhook makes it easy to keep your SIEM system synchronized."
- **Task Tracking Integration**: "Listen for `issue.created` to create new tickets for vulnerabilities" / "Listen for `issue.updated` to update tickets when any vulnerability properties change" / "Listen for `issue.status_changed` if you only care about vulnerability status transitions" / "Listen for `issue.comment_added` to sync comments between systems" / "The `changes` array included with `issue.updated` events makes it easy to add appropriate comments to your task tracking system (e.g., \"Vulnerability status changed from open to fixed\")."

## Cross-References

**Candidates from `miner-related-notes.md`** (read before writing this section;
every listed path is cited or dismissed by name):

- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **cited**
  (Extends — see below).
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  rate-limit accounting for `POST /v1/batches`; no webhook or event-delivery
  content.
- `source-notes/docs-promptfoo-deterministic-metrics.md` — **dismissed**:
  assertion-type inventory; no event or delivery surface.
- `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **cited**
  (Corroborates + Extends — see below).
- `source-notes/docs-promptfoo-enterprise-guardrails.md` — **cited**
  (Corroborates the "contract documented, failure semantics omitted" pattern —
  see below).
- `source-notes/blog-pagerduty-sre-agent-triage.md` — **dismissed**: AI
  *incident* triage by an SRE Agent; the shared word "triage" denotes alert
  routing there and finding disposition here, and that note makes no claim about
  webhook delivery.
- `source-notes/docs-promptfoo-pi-scorer.md` — **dismissed**: a model-graded
  grader's configuration; no event surface.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-MCP
  transport, unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: the toil
  taxonomy, unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch coordination, unrelated.

Additional cross-reference found by searching `source-notes/` (not in the
candidate list): `docs-langfuse-alerts.md` — **cited** (the vendor-documented
delivery contract this page lacks).

**Primary cross-references (verified per MINER §4b — cited claims re-read in
the source notes before writing):**

- **Corroborates**:
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **Concrete
    Artifacts → "No audit sink" section**, which records that the Enterprise
    webhook surface carries "`issue.created`, `issue.updated`,
    `issue.status_changed`, `issue.severity_changed`, `issue.comment_added` —
    five red-team finding events, no audit-log event". This page is the *primary
    source* for that second-hand list: the five identifiers match exactly, and
    the audit note's conclusion — that the webhook surface does not carry audit
    records — is now confirmed from the producing page's own event taxonomy
    (Claim 1). Where the audit note could only say "the webhook surface, which
    the page's sibling Enterprise overview advertises as 'External Integrations
    (SIEMs, Issue trackers, etc.)', does not carry audit records", this page
    establishes *what* it does carry. (Verified: the section heading, the
    five-event quote, and the surrounding sentence re-read.)
  - `source-notes/docs-promptfoo-enterprise-guardrails.md` **Claim 13** ("no
    failure semantics for the evaluate call itself and no measurement of any
    kind — no unreachable/error knobs, no timeout behavior, no status codes") —
    the same documented-absence shape as this page's Claim 7, on a different
    endpoint of the same Enterprise control plane. Together they establish the
    pattern as recurring for this vendor: a runtime/egress endpoint is specified
    as a *contract* (endpoint, enums, signing) while its *failure and delivery
    semantics* are left to the caller. Corroborates the pattern, not the
    mechanics — the guardrails endpoint's gap is about request-path failure, this
    page's is about event delivery. (Verified: Claim 13 heading, the
    "no failure semantics" paraphrase, and its assessment re-read.)
  - `source-notes/docs-langfuse-alerts.md` **Claim 7** ("Notifications route
    through automations that pair a trigger (an alert severity change) with an
    external action — Slack message, HMAC-signed webhook JSON POST, or a GitHub
    Actions `workflow_dispatch` event") — two vendors of LLM-ops tooling both
    ship HMAC-signed webhook delivery as a first-class integration channel,
    independently establishing the signed-webhook pattern in this corpus. The
    two contracts differ exactly where it matters (see **Contrast** under
    Extends). (Verified: Claim 7 heading and both verbatim quotes re-read.)

- **Contradicts**: **None filed, and this was checked rather than assumed.**
  - The one contradiction-shaped observation is *internal* to this source
    (Claim 3): the `issue.status_changed` description and the "listen for
    `issue.status_changed` if you only care about status transitions"
    recommendation versus the aggregation Note (Claim 2). Per MINER §4a this does
    **not** rise to a filed contradiction, for two reasons recorded here rather
    than left implicit: (a) the page *resolves* it — the Note explicitly states
    that a simultaneous change emits `issue.updated` "rather than separate
    `issue.status_changed` and `issue.severity_changed` events", so the bullet is
    true under the qualifier the Note supplies, and the two statements are not
    two opposed verdicts but one statement missing its condition; (b) the
    resolution is exactly the kind of conditioning variable §4a cites as "not a
    contradiction" (the event fires for isolated changes, not for bundled ones).
    The guide-facing treatment is the *footgun rule* in Claim 3, and no
    `C-NNN` entry applies.
  - No contradiction with an existing source note. Checked against
    `CONTRADICTIONS.md` and the open `contradiction`-labeled issues: none touch
    promptfoo webhooks or event delivery. The nearest adjacent material —
    `docs-langfuse-alerts.md` (Claims 7–8) — documents *more* delivery machinery
    than this page does; a richer contract does not oppose a thinner one, it
    exposes the gap, so the correct treatment is extension/contrast, recorded
    below.

- **Extends**:
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 2** ("The
    coverage boundary is drawn explicitly and in control-plane vocabulary:
    administrative actions are logged, while 'Evaluation runs, prompt testing,
    and other data plane operations are tracked separately' — with no named
    destination") — this page is the push side of the boundary. The audit log is
    a control-plane, pull-only, 100-record-capped poll (that note's Claims 7–8);
    webhooks are the only *push* path the Enterprise surface offers, and they
    push the *finding* plane, not the audit plane. Read together the corpus now
    holds both postures for the same product: **the audit trail must be polled,
    and the finding stream can be pushed but has no delivery guarantee.** The
    guide rule generalizes: *enumerate which plane each integration carries
    before assuming a vendor's "webhooks" cover the events you need audited.*
    (Verified: Claim 2 heading, its two verbatim quotes, and the assessment
    re-read.)
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` **Claim 2**
    ("Vulnerability disposition is a closed three-value status set — 'Marked as
    Fixed', 'False Positive', 'Ignore' — plus manual severity re-rating and
    free-text comments ... with no documented transition rules, auto-closure,
    SLA, or actor attribution") — the three mutable actions that note documents
    (status, severity, comment) are exactly the `issue.status_changed`,
    `issue.severity_changed`, and `issue.comment_added` events this page
    specifies, and this page supplies the attribution that note found missing
    (`userId` on `issue.updated`, Claim 4 here). It also resolves the disposition
    loop: a human edit in the UI becomes an outbound event in real time, so the
    finding's mutation surface is externally observable even though the audit
    log (per the audit note's Claim 3) records none of it. The two notes should
    be cited as a pair wherever the guide discusses finding disposition.
    (Verified: Claim 2 heading and quote, plus the "no actor attribution" clause
    re-read.)
  - `source-notes/docs-langfuse-alerts.md` **Claim 8** ("After 5 consecutive
    delivery failures, Langfuse automatically disables the automation's trigger;
    it must be manually re-enabled from the Automations page once the endpoint
    is restored") — **the contrast that gives this page its guide value.** Both
    vendors ship HMAC-signed webhooks; Langfuse documents a delivery-failure
    circuit breaker and a versioned payload schema, and promptfoo documents
    neither (Claims 6–7 here). The guide's Ch03 notification-plumbing rule
    ("give every notification channel a delivery-failure circuit breaker") was
    stated from the Langfuse instance alone; this source is the counterexample
    that shows the rule is *not* a vendor invariant — it must be demanded per
    integration, because a second vendor's webhook page omits it entirely.
    (Verified: Claim 8 heading and quote re-read.)
  - `source-notes/docs-promptfoo-enterprise-guardrails.md` **Claim 1** (the
    runtime enforcement contract is a caller-integrated HTTP endpoint) — not a
    webhook, but the same architectural posture the guide should name for this
    whole product family: promptfoo supplies contract endpoints and leaves the
    operational half (for guardrails, failure handling; for webhooks, delivery
    reliability) to the integrating caller. The webhook is the third instance in
    the corpus of "the vendor documents the schema and the endpoint, the operator
    supplies the semantics". (Verified: Claim 1 heading and its endpoint
    paraphrase re-read.)

- **Novel**: The following are net-new to the corpus:
  1. **The update-consolidation rule** (Claim 2) — the first documented
     event-fan-in design in the corpus: a producer that collapses simultaneous
     attribute changes into one coarse event and reserves the right to suppress
     the fine-grained ones. No prior note describes a vendor webhook whose
     specific event types are incomplete by design.
  2. **The event-type-filter footgun** (Claim 3) — a subscription filtered on a
     fine-grained event silently misses bundled changes, stated as a consumer
     rule.
  3. **The HMAC-over-serialized-body verification rule** (Claim 6) — the corpus's
     first concrete signature-verification integration footgun: verify the raw
     bytes, not a re-serialized parse.
  4. **The full promptfoo finding-event taxonomy and payload schema** (Claims
     1, 4, 9) — five event types, the full-state `issue` object, the
     human-readable `changes` string array, and optional `userId`; the audit note
     had only the bare event names.
  5. **The delivery-guarantee absence as a first-class finding** (Claims 7–8) —
     the corpus's first explicit record that an AI-platform webhook page
     documents no retry/ordering/DLQ/delivery-log at all, adjacent to the
     Langfuse counterexample that documents a circuit breaker.

## Guide Impact

- **Chapter 03 §"Alerts that dispatch runbooks" (`guide/03-runbooks-and-agents.md:238`)
  — generalize the delivery-failure circuit-breaker Rule from a Langfuse
  invariant to a per-integration demand.** The existing Rule ("give every
  notification channel a delivery-failure circuit breaker that stops retrying a
  dead endpoint and demands a human re-enable") cites `docs-langfuse-alerts`
  Claim 8. Add the counterexample: promptfoo's webhook page documents **no**
  retry, circuit breaker, ordering, or delivery log (Claim 7), so a channel
  built from this page has no delivery-failure handling at all. Proposed wording:
  *a notification channel's reliability is whatever the producing vendor
  documents, so verify the delivery contract before wiring a runbook — a webhook
  with no documented retry, ordering, or delivery log is best-effort, and the
  consumer must add polling reconciliation rather than assume the event is the
  record.*
- **Chapter 06 §"A guardrail is an egress boundary — configure what crosses it"
  (`guide/06-security-and-trust.md:547`) — extend the egress rule to webhook
  payloads and add the signature-verification step.** A delivered webhook
  payload carries the complete `issue` object (plugin, status, severity, target,
  provider, `weakness`, `history`) plus a `userId` (Claim 4) off-platform to a
  SIEM or ticket system — the same identity-bearing-egress shape the section
  already applies to guardrail payloads. Two specific additions: (a) enumerate
  the fields crossing the boundary and minimize them; (b) verify the signature
  over the **raw request bytes**, not a re-serialized parse, because the vendor
  signs `JSON.stringify(payload)` (Claim 6) — and guard the length before
  `timingSafeEqual`. Proposed rule text: *an outbound finding webhook is an
  egress path; verify its HMAC against the raw body and review the payload
  fields as you would a guardrail payload.*
- **Chapter 06 §"Red-teaming as a CI gate" (`guide/06-security-and-trust.md:120`)
  — one line on treating finding webhooks as an unreliable optimization.**
  The section already tells teams to run red-team tests before deploy and track
  a scorecard. Add that the real-time finding fan-out (webhooks) and the gate's
  source of truth are different paths: the webhook is best-effort (Claim 7), so
  a pipeline that *acts* on a finding must still poll the read API for the
  authoritative state rather than trust the push — the same read-via-API,
  react-via-webhook, actuate-outside pattern the findings note records (its
  Claim 10), here with the added caveat that the webhook has no delivery
  guarantee.
- **Chapter 02 (Observability) — event-delivery semantics as a design axis.**
  Add a short rule beside the notification material: **consumers cannot assume
  one event per state transition.** This page collapses simultaneous attribute
  changes into a single `issue.updated` (Claim 2) and delivers the diff as
  human-readable strings (Claim 9), so a correct subscriber listens to the
  coarse carrier event, keeps its own previous-state copy, and computes the
  diff itself. Cite the consolidation rule and the `changes`-is-prose caveat.
- **Do not** cite this page as evidence that promptfoo provides reliable
  finding delivery, ordering, deduplication, or replay. It documents a
  best-effort notification contract (Claim 7) and an Enterprise-gated
  specification with no measurement (Claim 10).

## Extraction Notes

- Source read in full via direct fetch of the rendered page
  (https://www.promptfoo.dev/docs/enterprise/webhooks, HTTP 200, no paywall).
  Every `Quote` above is character-for-character from the rendered text; the
  four code/JSON artifacts and the event/recipe lists are reproduced verbatim
  from the page's code blocks and bullet lists. Quote locations for
  re-verification: Claim 1's definition is the "What is an Issue?" paragraph;
  the five event-type bullets are "Event Types"; the consolidation Note is the
  `>` block immediately after them; the subscription/secret language is
  "Managing Webhooks" and "Creating a Webhook"; the `changes`/`userId` payload
  and the three-item "This structure allows you to" list are "Webhook Payload
  Structure"; the HMAC sentence and Node sample are "Verifying Webhook
  Signatures"; the SIEM and task-tracking quotes are "Example Integration
  Scenarios".
- **No metrics were manufactured.** The page contains no number of any kind
  except the example `2025-03-14` timestamps and `user-123`/`org-id`-style
  identifiers. `confidence_overall: emerging` rather than `settled` for the same
  reason the sibling promptfoo Enterprise notes made that choice: the enumerated
  facts are a specification string-checkable by an Enterprise tenant, while the
  behavior behind them is unverified and unverifiable from the open-source
  repository.
- **Enterprise gating / open-source verifiability.** The page is gated ("This
  feature requires Promptfoo Enterprise") and nothing on it is a config file or
  CLI flag checkable against `promptfoo/promptfoo`. I did not run a repository
  code search: the audit-logging note (same Enterprise doc tree) already
  recorded that its sibling feature returns a single doc-only markdown hit, and
  nothing on *this* page is an implementation claim.
- **Linked pages followed**: none. The page is self-contained — it links only to
  the Enterprise overview and does not defer to an API Reference, so there was
  no substantive sub-page to follow within the 5-page budget. This is itself a
  difference from the audit-logging and findings pages, which defer to an
  unfetchable client-rendered API spec; here the documented contract is exactly
  what is on the page, and Claim 10 is bounded accordingly.
- **Contradiction filing decision (MINER §4a)**: none filed. The one
  contradiction-shaped observation is the source's own internal tension (Claim
  3), assessed and declined with reasons recorded in Cross-References →
  Contradicts: the consolidation Note resolves the event-type bullet rather than
  opposing it, so it is a documented footgun, not two opposed verdicts. Checked
  against `CONTRADICTIONS.md` and the open `contradiction`-labeled issues — no
  existing entry covers promptfoo webhooks or event delivery.
- **Candidate handling** (`miner-related-notes.md`, 10 lexical candidates).
  Cited: **3** — `docs-promptfoo-enterprise-audit-logging.md` (Corroborates,
  Extends), `docs-promptfoo-enterprise-findings-reports.md` (Extends), and
  `docs-promptfoo-enterprise-guardrails.md` (Corroborates the documented-absence
  pattern). The other seven dismissed, one line each in Cross-References. One
  additional cross-reference (`docs-langfuse-alerts.md`) was found by searching
  `source-notes/` and is cited for the delivery-contract contrast.
- **Cross-references verified before writing** (MINER §4b): every `Claim N`
  cited from another note was located by re-reading that note's `### Claim:`
  headings and confirming content — `enterprise-audit-logging` Claim 2 and its
  Concrete Artifacts → "No audit sink" section; `enterprise-findings-reports`
  Claim 2, Claim 10; `enterprise-guardrails` Claims 1, 13;
  `docs-langfuse-alerts` Claims 7, 8. No quote was reconstructed from memory,
  and the audit-logging webhook list is cited by section name + quote, not
  invented as a claim number.
- `registry/sources.json` and `registry/claims-index.json` were **not** touched;
  both are derived indexes rebuilt by `registry-rebuild.yml` after merge.
  `miner-related-notes.md` was read but is not committed.
