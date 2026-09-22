---
source_url: https://docs.litellm.ai/docs/apply_guardrail
source_type: docs
title: "Direct Guardrail Invocation — POST /guardrails/apply_guardrail (LiteLLM Docs)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-09-22)
date_extracted: 2026-09-22
last_checked: 2026-09-22
status: current
confidence_overall: emerging
issue: "#1392"
---

# Direct Guardrail Invocation — POST /guardrails/apply_guardrail (LiteLLM Docs)

> LiteLLM documents an authenticated out-of-band endpoint,
> `POST /guardrails/apply_guardrail`, that runs any guardrail configured on the
> proxy against caller-supplied text without a model request — turning PII
> masking (Presidio), content moderation (Bedrock), and custom policy checks
> into standalone API-callable functions on the gateway's port and virtual-key
> auth, with success returning the processed text as `response_text` and a
> block surfacing as an error body carrying a free-text `detail` string rather
> than a structured verdict, while optional client-supplied `metadata` is
> forwarded to the guardrail as per-request configuration.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway endpoint
  reference under "Supported Endpoints" in the docs nav; the nav label is
  `/guardrails/apply_guardrail` while the page URL is
  `https://docs.litellm.ai/docs/apply_guardrail` — both resolve to the same
  page, and `/guardrails/apply_guardrail` is the endpoint path itself).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *documented surface* — request/response schema, config
  keys, curl examples, supported guardrail types. The page carries no measured
  data: no latency, throughput, rate-limit interaction, false-positive figures,
  or HTTP status codes anywhere, and no failure report or practitioner
  validation. Everything here stays at "the gateway documents this contract,"
  never "this holds at scale."
- **Scope**: The direct-call contract only — purpose, supported guardrail
  types, Bedrock config shape, curl usage (Presidio / Bedrock / parameterized
  custom), the Admin UI Test Playground metadata field, the
  `ApplyGuardrailRequest` field list, the `response_text` success shape, and
  the block-as-error response. Does **not** cover in-path interception
  semantics (covered by the generic-guardrail note), other guardrail provider
  pages, auth/scoping policy for this endpoint, or failure-mode knobs — the
  page is silent on those (recorded as documented gaps in Claims 10-11).
- **Artifacts followed**: The page's three usage tabs (Presidio, Bedrock,
  Custom Guardrail with metadata) are all on-page and were read in full. No
  substantive linked sub-pages; the Enterprise upsell footer and the
  marketing guardrail-vendor list beyond the type enumeration were skipped per
  Prospector triage guidance.

## Extracted Claims

### Claim 1: The page documents a distinct out-of-band invocation surface — `POST /guardrails/apply_guardrail` calls a guardrail already configured on the LiteLLM instance directly, decoupled from `/v1/chat/completions` traffic, so a guardrail becomes a standalone service callable by arbitrary services
- **Evidence**: The page's opening purpose statement, the Supported Endpoints
  nav entry listing `/guardrails/apply_guardrail` alongside model endpoints,
  and every curl example posting to `http://localhost:4000/guardrails/apply_guardrail`
  with no model request in the payload.
- **Confidence**: settled (documented purpose and endpoint)
- **Quote**: "Use this endpoint to directly call a guardrail configured on your LiteLLM instance. This is useful when you have services that need to directly call a guardrail."
- **Our assessment**: The trust-boundary fact the Prospector flagged. A
  guardrail is normally an in-path interceptor; this endpoint makes the same
  configured control independently callable over the same port and
  `Authorization: Bearer` virtual-key auth as the rest of the proxy. Whatever
  the guardrail can do to text — PII masking, content moderation, topic
  blocking — any holder of a valid key can now invoke as a function, including
  on text that never came from an LLM call (scanning user uploads, cron
  output, another service's queue). This is the client-side invocation
  counterpart to the provider-side webhook contract in
  `docs-litellm-generic-guardrail-api.md` (that note's Claim 1): same
  guardrail config, opposite call direction.

### Claim 2: The request contract is `ApplyGuardrailRequest` — required `guardrail_name` + `text`, optional `language` / `entities` / `metadata`
- **Evidence**: The "Required Fields" and "Optional Fields" sections plus the
  example request body.
- **Confidence**: settled (documented schema)
- **Quote**: "The identifier for the guardrail to apply (e.g., \"mask_pii\")." / "The input text to process through the guardrail."
- **Quote**: "The language of the input text (e.g., \"en\" for English)." / "Specific entities to process or filter (e.g., [\"NAME\", \"EMAIL\"])."
- **Quote**: "Per-request configuration forwarded to the guardrail as `request_data[\"metadata\"]`. Custom guardrails that override `apply_guardrail` are responsible for reading it. Forwarded only when present, so omitting it preserves existing behavior."
- **Our assessment**: A minimal required surface (`guardrail_name` selects
  the control, `text` is the payload) with three optionals. `language` and
  `entities` tune detection (entity selection is Presidio-shaped);
  `metadata` is the load-bearing optional — it is not a hint but the channel
  for per-request guardrail configuration (Claim 5). The field description's
  "forwarded only when present, so omitting it preserves existing behavior"
  sentence is the backward-compat caveat the triage asked to capture, stated
  by the vendor itself.

### Claim 3: Success returns the processed text as a payload — `{"response_text": ...}` is the redacted/filtered output, meaning the PII-bearing input and its redaction both transit this endpoint
- **Evidence**: The "Response Format" section, both example responses
  (Presidio redaction, Bedrock echo of what-would-be-blocked content), and
  the `response_text` field description.
- **Confidence**: settled (documented response shape)
- **Quote**: "The response will contain the processed text after applying the guardrail."
- **Quote**: "The text after applying the guardrail."
- **Our assessment**: The endpoint is a bidirectional data path for exactly
  the class of content security controls exist to handle: raw PII goes in,
  masked text comes back (Presidio example: `My name is [REDACTED] and my
  email is [REDACTED]`). A service that takes raw PII and returns masked text
  is precisely the component whose request/response logging must be audited —
  tie directly to
  `failure-litellm-guardrail-logging-secret-exposure.md` (guardrail-adjacent
  data transiting logging/telemetry paths unsanitized). The Bedrock example
  response also shows the *unblocked* content returned verbatim on success,
  so the same endpoint carries both clean and (pre-moderation) harmful text
  through its responses.

### Claim 4: A block is signalled as an error body with a free-text `detail` string, not a structured verdict — and the page states no HTTP status code for it, so a caller must parse prose to distinguish "blocked by policy" from "guardrail broke" or "bad guardrail_name"
- **Evidence**: The "Error Responses" section and the Bedrock block note;
  a full-page scan confirms no HTTP status code appears anywhere on the page
  (neither for success nor for the block error).
- **Confidence**: settled (documented error shape; status absence verified on
  the 2026-09-22 fetch — no status inferred)
- **Quote**: "If a guardrail blocks content (e.g., Bedrock guardrail), the endpoint will return an error:"
- **Quote**: "If Bedrock guardrail blocks the content, the endpoint will return an error with the blocking reason."
- **Quote**: "{\"detail\": \"Content blocked by Bedrock guardrail: Content violates policy\"}"
- **Our assessment**: The operational weak point of the direct-call path. The
  counterpart contract — the provider-side generic guardrail webhook
  (`docs-litellm-generic-guardrail-api.md`, Claim 3) — returns an explicit
  three-verdict body (`BLOCKED` / `NONE` / `GUARDRAIL_INTERVENED`) plus a
  documented two-knob fail-open/fail-closed spectrum (that note's Claims 8-9).
  Here the caller gets one error object whose `detail` is free text whose
  wording is provider-specific ("Content blocked by Bedrock guardrail: ..."),
  with no verdict enum, no `blocked_reason` field, and no documented status
  code — a caller wiring this endpoint into a service cannot programmatically
  separate a policy block from a transport/provider failure without
  string-matching the message, and the page does not say which status
  distinguishes them. That is a Ch05 availability/observability claim: an
  SRE must observe this endpoint's error rate but cannot classify errors by
  status alone. We do not infer a status; we record that the page does not
  state one.

### Claim 5: Client-supplied `metadata` is forwarded to the guardrail as `request_data["metadata"]`, and the worked example is a custom guardrail that blocks text mentioning `forbidden_topics` passed in by the caller — i.e., the entity invoking the control supplies part of the policy it enforces
- **Evidence**: The parameterized-custom-guardrails paragraph, the metadata
  field description, the worked curl example, and the explicit
  forwarded-only-when-present caveat.
- **Confidence**: settled for the forwarding mechanics (documented contract);
  the security reading below is our synthesis, not the page's claim
- **Quote**: "Parameterized custom guardrails read per-request configuration from `request_data[\"metadata\"]`. Send optional `metadata` in the request body and it is forwarded to your guardrail's `apply_guardrail` method. In this example `my-topic-guardrail` is a custom guardrail that blocks text mentioning any of the `forbidden_topics` passed in `metadata`."
- **Quote**: "`metadata` is only forwarded when the client sends it, so guardrails that do not depend on per-request configuration keep working unchanged when it is omitted."
- **Our assessment**: The highest-value claim on the page, and the one the
  Prospector's key question targeted. The vendor presents `metadata` as a
  parameterization feature — per-request tuning of a custom guardrail without
  a config reload, exercised the same way from the Admin UI (Claim 6). The
  security reading is synthesis: on a *shared* guardrail, the caller chooses
  the `forbidden_topics` list the control enforces, so the entity that is
  supposed to be constrained supplies the constraint. The docs are silent on
  who is authorized to set `metadata` for a given `guardrail_name` beyond
  holding a valid virtual key (Claim 10) — the honest framing is that this is
  a documented feature with an under-documented authorization question, not a
  documented vulnerability. Marking the trust-boundary concern explicitly as
  Miner synthesis per the triage instruction.

### Claim 6: The same metadata mechanism is exposed in the Admin UI — the Guardrail Testing Playground has an optional Metadata field with inline JSON validation, so a human can drive parameterized guardrails from the dashboard
- **Evidence**: The "Testing from the Admin UI" section.
- **Confidence**: settled (documented UI surface)
- **Quote**: "Enter a JSON object and it is sent as the `metadata` field of the request, letting you exercise parameterized custom guardrails without leaving the dashboard. Invalid JSON is rejected inline before the request is sent."
- **Our assessment**: The dashboard twin of Claim 5's curl example — same
  request field, different caller (a browser session on a virtual key rather
  than a script). Operationally useful for pre-deployment conformance testing
  of a parameterized guardrail; security-wise it widens the set of parties
  who can supply per-request policy to anyone with Admin UI access. The
  inline JSON validation is a client-side ergonomics detail, not an
  authorization control.

### Claim 7: The endpoint enumerates five supported guardrail types — Presidio (PII detection and masking), Bedrock (content moderation), Lakera (AI safety), PANW Prisma AIRS (threat detection, DLP, policy enforcement), and custom — so each becomes an API-callable function on the gateway
- **Evidence**: The "Supported Guardrail Types" bullet list.
- **Confidence**: settled (explicit documented enumeration)
- **Quote**: "- **Presidio** - PII detection and masking / - **Bedrock** - AWS Bedrock guardrails for content moderation / - **Lakera** - AI safety guardrails / - **PANW Prisma AIRS** - Threat detection, DLP, and policy enforcement / - **Custom guardrails** - User-defined guardrails"
- **Our assessment**: A coverage map for what the direct-call surface exposes:
  masking, moderation, safety classification, DLP/threat policy, and whatever
  an operator wrote. Each of these, normally an invisible in-path hop, is now
  reachable with `guardrail_name` + `text`. The page records no latency,
  throughput, or false-positive data for any type (Claim 11), so this is a
  config/capability shape, not efficacy evidence. Cross-provider behavioral
  asymmetries are already visible on-page (Claim 8).

### Claim 8: Cross-provider contract asymmetry — Bedrock ignores the `entities` parameter and applies its own configured policy instead, so the same request field means different things depending on `guardrail_name`
- **Evidence**: The Bedrock `entities` note under Usage, plus the Presidio
  curl example (which does pass `entities`) versus the Bedrock one (which
  does not).
- **Confidence**: settled (explicit vendor note)
- **Quote**: "For Bedrock guardrails, the `entities` parameter is not used as Bedrock handles content moderation based on its own policies."
- **Our assessment**: A real contract detail for callers: entity selection is
  a Presidio-shaped knob, not a gateway-level one. A caller that uniformly
  sends `entities` gets no error and no effect on Bedrock guardrails —
  silent parameter degradation rather than a rejection. Worth stating in any
  client library or conformance test built on this endpoint: request-field
  semantics are per-guardrail-type, and the gateway does not validate the
  mismatch.

### Claim 9: Bedrock guardrails require a specific config shape plus AWS-side setup — `guardrailIdentifier` / `guardrailVersion` / `aws_region_name` / `aws_role_name` / `default_on` in `config.yaml`, and four AWS Console prerequisites including Bedrock permissions on the role
- **Evidence**: The "Bedrock Guardrail Configuration" config block and the
  "Required AWS Setup" numbered list.
- **Confidence**: settled (documented config and prerequisites)
- **Quote**: "Create a Bedrock guardrail in AWS Console" / "Get the guardrail ID and version" / "Ensure your AWS credentials have Bedrock permissions" / "Configure the guardrail in your LiteLLM config"
- **Our assessment**: The concrete artifact an operator needs to make Claim
  1's direct-call path work with Bedrock: the guardrail is *defined in AWS*
  and referenced from LiteLLM, so the enforcement policy lives outside the
  gateway's config and a policy change is an AWS-side change. `default_on: true`
  and `mode: "pre_call"` in the block also confirm the same guardrail object
  still participates in in-path interception — the direct-call endpoint is an
  *additional* surface on top of the configured guardrail, not a replacement
  for in-path mode. The required AWS permissions item is the one operational
  dependency the gateway cannot satisfy for itself.

### Claim 10: The page's auth surface is only `Authorization: Bearer your-api-key` — it shows no key-scoping, permission, or rate-limit discussion for who may invoke guardrails via this endpoint
- **Evidence**: Every curl example carries exactly `-H 'Authorization: Bearer your-api-key'`;
  a full-page scan finds no mention of key scopes, RBAC, per-endpoint
  permissions, team restrictions, or quotas for `/guardrails/apply_guardrail`
  (verified absence on the 2026-09-22 fetch).
- **Quote**: "Authorization: Bearer your-api-key"
- **Our assessment**: The Prospector explicitly asked whether the docs say
  which keys are authorized to call this endpoint; they do not — the page
  treats it like any other proxy route authenticated by a virtual key. What
  the page *not* saying means in practice: whether a low-privilege key can
  invoke a high-sensitivity guardrail (e.g., run Presidio over arbitrary
  text, or read back `response_text` derived from PII someone else supplies)
  is determined by LiteLLM's general key/auth machinery, not by anything
  documented here. Operators deploying this endpoint should check the
  gateway's key-scoping configuration themselves; we record the documentation
  gap rather than asserting a vulnerability.

### Claim 11: The direct-call path documents no failure-semantics knobs, no HTTP status codes, and no measured performance — no fail-open/fail-closed equivalent of the provider-side contract, no status for the block error, no latency/throughput/rate-limit figures anywhere on the page
- **Evidence**: Full-page scan of the 2026-09-22 fetch: zero HTTP status
  codes appear; no `unreachable_fallback` / `fail_on_error` (or any
  equivalent) is mentioned; no timing, quota, or volume data appears. This is
  a verified documented gap, not an inference about runtime behavior.
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: the gap is real and operational. An operator wiring this
  endpoint into a service needs three answers before trusting it as a
  control — what status does a block return, what happens when the
  underlying guardrail provider is unreachable (fail open or closed), and
  what latency/capacity should be budgeted — and the page answers none.
  The provider-side generic-guardrail note answers the second question
  explicitly (two-knob spectrum, both defaults closed; its Claims 8-9), but
  that contract governs the proxy→provider webhook, *not* this
  caller→gateway route; nothing on this page states whether the same knobs
  apply when the guardrail is invoked directly, so we record it as an
  undocumented surface rather than assuming the provider-side defaults carry
  over. This is a genuine divergence-by-omission for Ch05: a caller must
  string-match `detail` (Claim 4) and cannot rely on a status taxonomy the
  docs never provide.

## Concrete Artifacts

All artifacts verbatim from the fetched page
(https://docs.litellm.ai/docs/apply_guardrail).

### Bedrock guardrail configuration (from "Bedrock Guardrail Configuration", verbatim)

```yaml
guardrails:
  - guardrail_name: "bedrock-content-guard"
    litellm_params:
      guardrail: bedrock
      mode: "pre_call"
      guardrailIdentifier: "your-guardrail-id"  # Your actual Bedrock guardrail ID
      guardrailVersion: "DRAFT"  # or your version number
      aws_region_name: "us-east-1"  # Your AWS region
      aws_role_name: "your-role-arn"  # Your AWS role with Bedrock permissions
      default_on: true
```

### Required AWS Setup (verbatim numbered list from "Bedrock Guardrail Configuration")

```
1. Create a Bedrock guardrail in AWS Console
2. Get the guardrail ID and version
3. Ensure your AWS credentials have Bedrock permissions
4. Configure the guardrail in your LiteLLM config
```

### Presidio direct-call example (from "Usage" tab, verbatim)

```
curl -X POST 'http://localhost:4000/guardrails/apply_guardrail' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "guardrail_name": "mask_pii",
    "text": "My name is John Doe and my email is john@example.com",
    "language": "en",
    "entities": ["NAME", "EMAIL"]
  }'
```

### Bedrock direct-call example (from "Usage" tab, verbatim)

```
curl -X POST 'http://localhost:4000/guardrails/apply_guardrail' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "guardrail_name": "bedrock-content-guard",
    "text": "This is potentially harmful content that should be blocked",
    "language": "en"
  }'
```

### Parameterized custom guardrail example — caller-supplied `forbidden_topics` (from "Usage" tab, verbatim)

```
curl -X POST 'http://localhost:4000/guardrails/apply_guardrail' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-api-key' \
  -d '{
    "guardrail_name": "my-topic-guardrail",
    "text": "What are tax loopholes?",
    "metadata": {
      "forbidden_topics": ["tax", "finance"]
    }
  }'
```

### Request field reference (from "Request Format", verbatim field list)

```
Required Fields:
- guardrail_name (string): The identifier for the guardrail to apply (e.g., "mask_pii").
- text (string): The input text to process through the guardrail.

Optional Fields:
- language (string): The language of the input text (e.g., "en" for English).
- entities (array of strings): Specific entities to process or filter (e.g., ["NAME", "EMAIL"]).
- metadata (object): Per-request configuration forwarded to the guardrail as
  request_data["metadata"]. Custom guardrails that override apply_guardrail
  are responsible for reading it. Forwarded only when present, so omitting it
  preserves existing behavior.
```

### Example request body (verbatim)

```json
{
  "guardrail_name": "mask_pii",
  "text": "My name is John Doe and my email is john@example.com",
  "language": "en",
  "entities": ["NAME", "EMAIL"]
}
```

### Example success responses (from "Response Format", verbatim)

```json
{"response_text": "My name is [REDACTED] and my email is [REDACTED]"}
```

```json
{"response_text": "This is potentially harmful content that should be blocked"}
```

### Error response on block (from "Error Responses", verbatim)

```json
{"detail": "Content blocked by Bedrock guardrail: Content violates policy"}
```

## Cross-References

**Candidates from `miner-related-notes.md`** (read before writing
Cross-References; every listed path is cited or explicitly dismissed):

- `source-notes/docs-litellm-generic-guardrail-api.md` — **cited** (Extends —
  primary; see below).
- `source-notes/docs-langfuse-security-and-guardrails.md` — **cited**
  (Corroborates / Extends — see below).
- `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` — **dismissed**:
  its guardrail material (Claim 3, deny-by-default for world-mutating agent
  actions, sandboxing) is agent write-governance, not a gateway guardrail
  invocation contract; no overlap with this endpoint's surface.
- `source-notes/blog-litellm-auto-router-v2.md` — **dismissed**: model-path
  routing flavors and debuggability rationale; no guardrail contract.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **dismissed**: A2A
  per-session iteration/budget caps (429 budget-exceeded semantics); no
  guardrail mechanism.
- `source-notes/docs-litellm-a2a-cost-tracking.md` — **dismissed**: per-agent
  declared-charge accounting on the A2A path; no guardrail contract.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: docs-as-MCP
  coding-agent intake; unrelated to guardrail enforcement.
- `source-notes/docs-litellm-helicone-integration.md` — **dismissed**:
  Helicone observability/telemetry integration paths; no guardrail contract.
- `source-notes/docs-google-sre-data-processing-pipelines.md` — **dismissed**:
  pipeline SLO formats and freshness/correctness targets; unrelated.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization/measurement; unrelated.

Additional cross-references from the Prospector's overlap list and ad-hoc
search of `source-notes/` (verified below): `failure-litellm-guardrail-logging-secret-exposure.md`
and `docs-promptfoo-guardrails-assertions.md` are cited; no other note
covers `apply_guardrail` or this URL (grep confirmed before extraction).

**Primary cross-references (verified per MINER §4b — claims re-read in the
cited notes before writing):**

- **Corroborates**:
  - `source-notes/docs-langfuse-security-and-guardrails.md` **Claim 1**
    (security architecture is two-pronged: runtime blocking via guardrail
    libraries + post-hoc observability) and **Claim 10** (guardrails are
    application-layer controls that "intercept and filter inputs and outputs
    of LLM applications", complementary to model-level safety training) —
    this page supplies the *gateway-side runtime enforcement* surface for
    exactly that blocking half, with the concrete property that the
    interception can also be invoked out-of-band. That note's runtime half is
    an app-layer `llm_guard` pipeline; this is the same role instantiated as
    a gateway endpoint. (Verified: Claim 1 heading + two-pronged quote;
    Claim 10 heading + FAQ definition quote.)
  - `source-notes/docs-promptfoo-guardrails-assertions.md` **Claim 11**
    ("An intervention is not always a transport error... Return expected
    interventions as a scorable `output` plus `guardrails`; a provider
    `error` skips assertions") — corroborates the general corpus point that
    guardrail blocks are frequently *not* cleanly separable via HTTP status
    alone: that note documents it for provider→eval normalization (AWS
    `ApplyGuardrail` returns HTTP 200 with an action); this page documents
    the LiteLLM direct-call flavour (block arrives as an error-shaped body
    with free-text `detail`, status unstated). Two vendors, two layers, the
    same caller-side parsing problem. (Verified: Claim 11 heading + quote.)
- **Contradicts**: None, and no contradiction issue filed. The nearest
  surface — this page's block-as-free-text-error (Claim 4) versus
  `docs-litellm-generic-guardrail-api.md` **Claim 3**'s explicit
  `BLOCKED`/`NONE`/`GUARDRAIL_INTERVENED` three-verdict body — is a
  *different contract for a different call direction* (caller→gateway
  direct invocation vs gateway→provider webhook), not two opposing claims
  about the same behavior; likewise that note's fail-open/fail-closed knobs
  (Claims 8-9) govern the provider-side path while this page is simply
  silent about the direct path (Claim 11 records the omission, not a
  conflicting default). Complementary, as the triage predicted — both are
  extracted as-is. Verified against `CONTRADICTIONS.md` (no relevant `C-NNN`
  entries) and open `contradiction`-labeled issues (#1150 / #1307 / #1322 /
  #1338 / #1352 / #1408 — none touch this page).
- **Extends**:
  - `source-notes/docs-litellm-generic-guardrail-api.md` — the primary
    relationship. That note is the *provider-side integration contract* (a
    guardrail provider implements `POST /beta/litellm_basic_guardrail_api`
    so the proxy can call *it*); this page is the *client-side invocation
    contract* (a service calls a configured guardrail through the proxy).
    Same `guardrail_name` config objects, opposite traffic direction. It
    extends that note's coverage from "guardrails as in-path interceptors of
    model traffic" to "guardrails as independently callable functions," and
    its Claim 4 (block-as-error with no status) is the direct-call
    counterpart to that note's Claim 3 (structured three-verdict) and Claims
    8-9 (documented failure knobs this page lacks).
  - `source-notes/failure-litellm-guardrail-logging-secret-exposure.md` —
    that failure note's **Lesson 2** asks for a strict guardrail return
    contract (minimal structured results, not full request dicts) precisely
    because guardrail-adjacent data transits logging paths; this page's
    success contract (`response_text` = masked output derived from raw PII
    input, Claim 3) is a new instance of the same class: an endpoint whose
    request *and* response bodies are sensitive by construction, so its
    access logging, spend logs, and tracing must be treated under that
    lesson's sanitize-before-emission rule. (Verified: Lesson 2 heading +
    "minimal structured results" guidance.)
- **Novel**: First corpus coverage of a **guardrail as a standalone,
  independently callable API surface** — out-of-band invocation decoupled
  from the model path; the block-as-free-text-`detail`-without-status error
  shape for a direct-call security endpoint; the client-supplied `metadata` →
  `request_data["metadata"]` per-request policy channel (with the
  caller-supplies-the-constraint synthesis and its Admin UI twin); the
  documented auth-scoping and failure-knob *gaps* for this path; and the
  five-type supported enumeration (Presidio / Bedrock / Lakera / PANW Prisma
  AIRS / custom) with the Bedrock `entities` asymmetry. The corpus covered
  guardrails at three other layers before this — provider-side webhook
  contract (generic-guardrail note), app-layer scanner observability
  (Langfuse), eval-time verdict reading (promptfoo) — none covered the
  gateway's direct client-facing invocation route.

## Guide Impact

- **Chapter 06 (Security and Trust)**: The guide's guardrail coverage
  currently comes from `docs-litellm-generic-guardrail-api` (in-path
  interception, tool-authorization surface, egress minimization — see
  `guide/06-security-and-trust.md:282`ff). This source adds two things that
  section does not have: (a) the **out-of-band trust boundary** — state
  plainly that `/guardrails/apply_guardrail` makes a configured security
  control callable by any virtual-key holder on the gateway's port
  (Claim 1), and pair it with the documented auth-scoping silence (Claim 10)
  as an operator checklist item (verify key scoping before enabling the
  endpoint for broad audiences); (b) the **client-controlled policy
  channel** — `metadata` forwarded as `request_data["metadata"]` with the
  worked caller-supplied `forbidden_topics` example (Claim 5), marked as
  Miner synthesis that this is the same config-as-attack-surface class the
  corpus already tracks (the constrained entity supplies the constraint),
  with the honest framing that the vendor documents it as a feature. Both
  belong beside the existing gateway-guardrail material and the "Data
  governance for AI workloads" section: `response_text`'s PII-in/masked-out
  payload (Claim 3) is a concrete reason to audit logging on this endpoint
  per `failure-litellm-guardrail-logging-secret-exposure.md`'s lessons.
- **Chapter 05 (LLM Ops Reliability)**: Extend the
  "A guardrail in the request path is an availability dependency" section
  (`guide/05-llm-ops-reliability.md:1307`) with the direct-call path's
  observability gap: a block arrives as an error body with a provider-shaped
  free-text `detail` and **no documented HTTP status** (Claim 4), and the
  page defines no fail-open/fail-closed or reachability knobs for this route
  (Claim 11) — so an operator cannot classify this endpoint's errors by
  status code and must not assume the provider-side `unreachable_fallback` /
  `fail_on_error` defaults carry over. Recommend treating
  `/guardrails/apply_guardrail` error rate as a monitored dependency with
  `detail`-string classification (or a synthetic canary that exercises block
  and pass) until the vendor documents status/failure semantics. Claim 8's
  silent `entities` degradation on Bedrock is a conformance-test item for
  any client built on the endpoint.
- **Chapter 02 (Observability)**: The block-as-error shape (Claim 4) is a
  concrete instance of "classify errors by body, not status" — worth a line
  alongside the existing free-text/verdict discussion, and a reminder that
  the same free-text-parsing problem appears at the eval layer too
  (`docs-promptfoo-guardrails-assertions.md` Claim 11).

## Extraction Notes

- Source read in full via WebFetch on
  `https://docs.litellm.ai/docs/apply_guardrail` (HTTP 200, single
  self-contained endpoint-reference page) on 2026-09-22, then quotes and
  code blocks verified against that fetch character-for-character. All
  `Quote` fields are contiguous verbatim strings from the page's prose or
  its fenced examples (markdown emphasis markers retained per the sibling
  LiteLLM notes' convention; code-block line breaks restored at statement
  boundaries only). No paywall, no truncation. The page's three usage tabs
  (Presidio / Bedrock / Custom) are all present in the fetch and were read;
  no substantive sub-pages were linked, so none were followed (per triage:
  Enterprise footer and marketing vendor list skipped).
- The submitted URL (`/docs/apply_guardrail`) and the endpoint/page path
  (`/guardrails/apply_guardrail`, the nav label and `<h1>`) are recorded:
  `source_url` is the URL that was actually fetched; the canonical endpoint
  path appears in the title and Claim 1, per the Prospector's URL note.
- Prospector triage (three concurrent comments, all `triaged:text`,
  reconciled guidance) honored: request/response contract verbatim
  (Claim 2), block-as-error failure mode with explicit record that **no
  status code is stated** (Claim 4, no status inferred), `metadata`
  forwarding rule with the client-controlled-policy reading marked as
  synthesis (Claim 5), Admin UI metadata field (Claim 6), success
  `response_text` PII-transit tie to the logging-failure note (Claim 3),
  supported types + Bedrock config/AWS setup as config shape (Claims 7-9),
  auth-scoping silence (Claim 10), and the documented-gap scan for
  failure-semantics knobs (Claim 11). Enterprise upsell skipped as
  instructed.
- **Contradiction scan (MINER §4a)**: no contradiction issue filed. The
  block-as-error vs three-verdict difference is a cross-direction contract
  difference (client-side invocation vs provider-side webhook), not opposing
  claims; the failure-knob absence on this page is an omission, not a
  conflicting default. Verified against `CONTRADICTIONS.md` (no relevant
  entries) and all open `contradiction`-labeled issues (#1150, #1307, #1322,
  #1338, #1352, #1408 — none cover this page or the apply_guardrail
  surface).
- **Cross-ref verification (§4b)**: before citing, re-read
  `docs-litellm-generic-guardrail-api.md` (Claims 1, 3, 8-9),
  `docs-langfuse-security-and-guardrails.md` (Claims 1, 10),
  `docs-promptfoo-guardrails-assertions.md` (Claim 11), and
  `failure-litellm-guardrail-logging-secret-exposure.md` (Lesson 2). Every
  `Claim N` cited resolves to a real numbered claim in the cited note; no
  quotes were reconstructed. All ten `miner-related-notes.md` candidates
  are cited or dismissed by path above.
- **Guide-state correction**: the first triage comment (2026-09-20) said the
  guide contained only a metaphorical `guardrail` in `00-principles.md`.
  Since then `docs-litellm-generic-guardrail-api` was merged and the guide
  now carries concrete guardrail material in Ch05
  (`guide/05-llm-ops-reliability.md:1307`ff, "A guardrail in the request
  path is an availability dependency") and Ch06
  (`guide/06-security-and-trust.md:282`ff, tool-aware gateway guardrail).
  Verified by grep on 2026-09-22. Guide Impact above is written against the
  *current* guide state: this source extends, rather than fills, the
  guardrail coverage.
- `confidence_overall` is `emerging`, matching the sibling LiteLLM docs
  notes: the claims are documented vendor *contract* (schema, config,
  examples — settled-as-documented, with verified absences recorded as
  such), but the page carries no measured data, no status codes, no
  failure-report evidence, and the security reading in Claim 5 is Miner
  synthesis from the documented surface rather than a vendor assertion.
