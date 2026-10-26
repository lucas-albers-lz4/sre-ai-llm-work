---
source_url: https://www.promptfoo.dev/docs/integrations/langfuse
source_type: docs
title: "Promptfoo × Langfuse Integration — SDK/Server Coupling, Env-Var Precedence, and SDK-Free Trace Retrieval"
author: "Promptfoo (vendor documentation; page last updated by renovate[bot])"
date_published: 2026-10-25
date_extracted: 2026-10-26
last_checked: 2026-10-26
status: current
confidence_overall: settled
issue: "#1889"
---

# Promptfoo × Langfuse Integration

> The dependency and configuration surface behind promptfoo's Langfuse integration: an optional `@langfuse/client` package whose v6 line requires self-hosted Langfuse ≥ v4.59.0 (with v5.11.1 as the older-server fallback), a host-variable alias where `LANGFUSE_HOST` wins over `LANGFUSE_BASE_URL`, `--env-file`/`config.env` taking precedence over shell exports, and eval-time trace retrieval that uses Langfuse's public API without the client SDK but is scoped to Cloud or self-hosted v4.

## Source Context

- **Type**: docs (vendor integration page, promptfoo × Langfuse)
- **Author credibility**: Promptfoo, maintainer of the eval harness, documenting its own integration code path. Authoritative for promptfoo's resolution behavior and for the version constraint it enforces at install time. The page is machine-maintained (footer: "Last updated on **Oct 25, 2026** by **renovate\[bot\]**"). It contains no measured evidence — no eval run, no failure trace, no benchmark — so confidence here is in the *documented behavior*, not in observed operation.
- **Scope**: Covers promptfoo setup against Langfuse (installing the optional client SDK, credentials/host env vars), the `langfuse://` prompt reference, trace retrieval through the external `langfuse` trace provider, and generic label-based deployment advice. Does **not** cover the Langfuse prompt-management lifecycle, trace data model, or self-hosting upgrade matrix — those are separate Langfuse pages already in the corpus.
- **Linked page followed**: `/docs/tracing/` (the page the integration page links to for the external trace provider). Only the "Langfuse" subsection of that tracing page is used here, to resolve what "Trace retrieval uses Langfuse's public API directly" actually means operationally. All quotes sourced from it are attributed inline.
- **Deliberately out of scope**: the `langfuse://<prompt>@label:type` grammar, version/label forms, `:text`/`:chat` suffixes, and variable pass-through. `docs-promptfoo-configuration-prompts.md` Claims 3–4 already own that surface; this page is a restatement, not new evidence.

## Extracted Claims

### Claim 1: Langfuse prompt resolution goes through an optional `@langfuse/client` package that promptfoo does not install by default, and promptfoo must run from the project where that package is resolvable
- **Evidence**: The Setup section's first step shows a combined install (`npm install promptfoo @langfuse/client@^6.0.0`) and states the SDK is not installed by default; it instructs running `npx promptfoo eval` from that project so promptfoo can resolve it, and gives a global-install equivalent.
- **Confidence**: settled (documented install/resolution behavior)
- **Quote**: "The SDK is not installed by default. Run `npx promptfoo eval` from this project so promptfoo can resolve it."
- **Our assessment**: Buy it, and read it as a hidden runtime dependency rather than an install-time one. A promptfoo image that only installs promptfoo will pass config parsing and then fail when a `langfuse://` prompt is actually resolved, so the dependency has to be present in the CI image/workspace, not just in a developer's global npm prefix. The explicit `npx promptfoo eval` instruction also matters in CI: invoking a globally installed binary from a different working directory can leave the project-local `@langfuse/client` unresolved.

### Claim 2: `@langfuse/client` v6 requires Langfuse Cloud or self-hosted Langfuse v4.59.0 or later; older self-hosted servers must stay on `@langfuse/client@^5.11.1`, which remains supported
- **Evidence**: The sentence immediately following the install step states the server floor and names the fallback package version. The page links out to Langfuse's JS v5→v6 migration guide rather than restating the migration details.
- **Confidence**: settled (documented compatibility constraint)
- **Quote**: "SDK v6 requires Langfuse Cloud or self-hosted Langfuse v4.59.0 or later. For older self-hosted servers, install `@langfuse/client@^5.11.1`, which remains supported."
- **Our assessment**: This is the most operationally significant claim on the page: a *prompt-source* choice silently adds a *server-version floor* to the eval pipeline. Nothing in the prompt URI reveals the constraint. A team that pins `@langfuse/client` to the current major can therefore break a CI job against an older self-hosted Langfuse even though the prompt name/label did not change; the fix is either to pin the client to `^5.11.1` or to upgrade the Langfuse server to ≥ v4.59.0. The corpus's compatibility note (`docs-langfuse-compatibility.md`, extracted 2026-07-23) records JS/TS SDK v5 as the GA client and a much lower OSS floor (≥ 3.63.0), so this is a *newer SDK generation* with a stricter floor, not a contradiction — but the compatibility note is now behind and should be updated when Langfuse v6 is documented.

### Claim 3: `LANGFUSE_BASE_URL` is accepted as an alias for `LANGFUSE_HOST`, and when both are set `LANGFUSE_HOST` wins regardless of which one the integration page demonstrates
- **Evidence**: The env-var paragraph after the credential exports names the alias and states the tie-break explicitly. The page's own examples export `LANGFUSE_HOST`.
- **Confidence**: settled (documented precedence)
- **Quote**: "`LANGFUSE_BASE_URL`, the name the Langfuse SDK uses for the host, works in place of `LANGFUSE_HOST`. If both are set, `LANGFUSE_HOST` is used."
- **Our assessment**: Buy the precedence, and flag the trap. Langfuse's own SDK/CLI documentation uses `LANGFUSE_BASE_URL` (`docs-langfuse-cli.md` Claim 4; `docs-langfuse-sdk-overview.md` Concrete Artifacts), so an operator migrating an existing Langfuse job to promptfoo is likely to leave `LANGFUSE_BASE_URL` in place and add nothing else. That works — until a second, stale `LANGFUSE_HOST` is introduced (e.g. from a base image or a shared env file), at which point the *undocumented-in-the-older-docs* variable wins. The precedence is the reverse of "last definition wins" intuition and should be recorded explicitly in the CI env contract.

### Claim 4: `--env-file` and the config's top-level `env` block take precedence over variables exported in the shell — the opposite of the usual shell-overrides-file assumption
- **Evidence**: The same env-var paragraph states that either mechanism "take[s] precedence over variables exported in your shell." This sits alongside the sibling configuration-guide rule that `{{ env.* }}` is resolved at config load time (`docs-promptfoo-configuration-guide.md` Claim 7).
- **Confidence**: settled (documented precedence)
- **Quote**: "You can also set them in a file passed with `--env-file` or in your config's top-level `env` block. Both take precedence over variables exported in your shell."
- **Our assessment**: This is a Ch06-grade declaration-precedence hazard. Operators commonly assume `export LANGFUSE_HOST=...` in a CI `env:` block will override a checked-in `config.env` or an `--env-file`; here it does not. That inverts the normal blast-radius reasoning: a committed config file, not the job's shell, is the authoritative source for the host/credentials. It also means a config `env` block carrying a secret is worse than a shell export, because the config wins *and* (per the configuration-guide note) may end up in exported results. The safe pattern is to keep non-sensitive flags in config and credentials in the process environment, then verify which source actually won.

### Claim 5: Eval-time trace retrieval uses Langfuse's public API directly through the external `langfuse` trace provider and does not require installing the Langfuse client SDK
- **Evidence**: The integration page's "Using Langfuse prompts" section links to the `langfuse` external trace provider and states that trace retrieval uses the public API and does not require the client SDK.
- **Confidence**: settled (documented architecture)
- **Quote**: "Trace retrieval uses Langfuse's public API directly and does not require installing the Langfuse client SDK."
- **Our assessment**: This is a useful separation of concerns: prompt resolution and trace retrieval are two different Langfuse client surfaces in promptfoo. A team can run SDK-free trace fetch (the application already emits traces to Langfuse) while separately opting into the `@langfuse/client` package only if it also sources prompts from Langfuse. The distinction matters for air-gapped/self-hosted runners and for supply-chain minimisation: trace-only users can avoid adding a third-party SDK to the eval image. The page itself only states the negative (no SDK needed) and links out for the provider config, so the positive configuration must be taken from the tracing page (Claim 6).

### Claim 6: The `langfuse` trace provider queries Langfuse's v2 Observations API using the OTel trace ID propagated in `traceparent`, is scoped to Langfuse Cloud or self-hosted v4, and imports normalised spans/attributes plus parent-child, I/O, model, token, and cost data
- **Evidence**: The tracing page's Langfuse subsection gives the provider config (`id: langfuse`, endpoint, public/secret key auth) and describes the query path and imported data. It also scopes the provider to "Langfuse Cloud or a self-hosted Langfuse v4 instance."
- **Confidence**: settled (documented provider behavior and version scope)
- **Quote**: "Promptfoo queries Langfuse's v2 Observations API using the OpenTelemetry trace ID propagated in `traceparent`. It preserves original OpenTelemetry span and resource attributes, normalizes generation, embedding, tool, agent, workflow, and retrieval observations to GenAI semantic conventions, and imports parent-child relationships, inputs, outputs, models, token usage, and costs."
- **Our assessment**: This answers the triage's "does trace retrieval need the SDK at all?" with a documented no — but it also adds a version constraint the integration page omits: the provider is explicitly Cloud-or-self-hosted-v4, because the v2 Observations API does not exist on older servers (`docs-langfuse-compatibility.md` Claims 11 and 14: v2 resources require server v4; on OSS v3 the defaults fail). So "SDK-free" is not "dependency-free" — the eval runner now depends on the Langfuse server being v4 and on the application carrying the W3C `traceparent` into its spans. The normalised import is the value proposition: assertions can see tool calls, retrieval steps, token usage, and parent-child structure rather than only the final response.

### Claim 7: Real-time trace availability requires Langfuse Python SDK ≥ 4.7.0, JS SDK ≥ 5.4.0, or the `x-langfuse-ingestion-version: 4` header on an OTel exporter; older ingestion paths can delay visibility by up to ten minutes, which the tracing page states makes earlier versions unusable for eval-time trace fetching
- **Evidence**: The tracing page's Langfuse subsection states the three real-time paths and the ten-minute delay, then draws the eval-specific conclusion. This independently corroborates the Langfuse compatibility/metrics documentation already in the corpus.
- **Confidence**: settled (same constraint documented by two independent vendors)
- **Quote**: "Langfuse Python SDK 4.7.0+, JavaScript SDK 5.4.0+, or an OpenTelemetry exporter configured with the `x-langfuse-ingestion-version: 4` header makes new observations available in real time; older ingestion paths can delay visibility by up to ten minutes. This delay makes earlier versions of Langfuse unusable for fetching traces during an evaluation."
- **Our assessment**: Strong, because promptfoo is not Langfuse and has no incentive to overstate Langfuse's ingestion delay; it is describing a constraint its own trace provider has to live with. The practical consequence is a *preflight* requirement for any CI job that asserts on traces: the application's ingestion path must be real-time before the eval starts, or the trace fetch races the trace write and returns an incomplete/empty trace. `docs-langfuse-compatibility.md` Claims 6–7 and `docs-langfuse-metrics-overview.md` Claim 10 document the same delay from the Langfuse side, making this a three-source, cross-vendor fact. Note the threshold here is stated as "Python SDK 4.7.0+ / JavaScript SDK 5.4.0+", while the integration page separately requires `@langfuse/client` v6 for prompt reads — these are different packages/majors and should not be conflated in the guide.

## Concrete Artifacts

### Optional Langfuse client install and the v6 server floor (integration page, "Setup")
```bash
npm install promptfoo @langfuse/client@^6.0.0
```
> "The SDK is not installed by default. Run `npx promptfoo eval` from this project so promptfoo can resolve it. For a global installation, use `npm install -g promptfoo @langfuse/client@^6.0.0`."
>
> "SDK v6 requires Langfuse Cloud or self-hosted Langfuse v4.59.0 or later. For older self-hosted servers, install `@langfuse/client@^5.11.1`, which remains supported."

### Credentials, host alias, and precedence (integration page, "Setup")
```bash
export LANGFUSE_PUBLIC_KEY="your-public-key"
export LANGFUSE_SECRET_KEY="your-secret-key"
export LANGFUSE_HOST="https://cloud.langfuse.com"  # or your self-hosted URL
```
> "You can also set them in a file passed with `--env-file` or in your config's top-level `env` block. Both take precedence over variables exported in your shell."
>
> "`LANGFUSE_BASE_URL`, the name the Langfuse SDK uses for the host, works in place of `LANGFUSE_HOST`. If both are set, `LANGFUSE_HOST` is used."

### External `langfuse` trace provider (tracing page, "Pulling Traces From Another Service → Langfuse")
```yaml
tracing:
  enabled: true
  provider:
    id: langfuse
    endpoint: 'https://cloud.langfuse.com'
    auth:
      username: '{{ env.LANGFUSE_PUBLIC_KEY }}'
      password: '{{ env.LANGFUSE_SECRET_KEY }}'
```
> "Use the `langfuse` trace provider to pull observations from Langfuse Cloud or a self-hosted Langfuse v4 instance:"
>
> "Promptfoo includes a `traceparent` header when it calls your application."

> Formatting note: the YAML above is reproduced from the rendered page with normal indentation; the prose quotes are verbatim.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-langfuse-compatibility.md` **Claim 6** and **Claim 7** (real-time OTel tracing requires Python SDK ≥ 4.7.0 / JS/TS SDK ≥ 5.4.0, or the `x-langfuse-ingestion-version: 4` header; otherwise up to a 10-minute delay). This note's Claim 7 is the same constraint stated by promptfoo's tracing page, from the consumer side of the integration — a second, independent vendor confirming the delay and the header threshold.
  - `source-notes/docs-langfuse-metrics-overview.md` **Claim 10** (older SDKs or OTel exporters without the `x-langfuse-ingestion-version: 4` header can be delayed up to 10 minutes on v2 endpoints). Same ingestion constraint, now reached through promptfoo's trace provider rather than Langfuse's metrics API.
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 7** (`{{ env.* }}` is resolved at config load time and `config.env` may leak into exported results). This note adds the *ordering* the guide's note leaves implicit: config/`--env-file` beat shell exports, so the config file is the authoritative declaration surface — which strengthens the case for keeping secrets out of `config.env`.
- **Extends**:
  - `source-notes/docs-promptfoo-configuration-prompts.md` **Claims 3–4** (`langfuse://` external prompt references; version pinning vs labels; `@`/colon label forms; `:text`/`:chat` suffixes). This note deliberately does **not** re-extract that grammar; it extends the same integration with the dependency floor and env-var precedence that determine whether the URI resolves at all in CI.
  - `source-notes/docs-langfuse-sdk-overview.md` **Claim 9** (`@langfuse/client` is the modular JS/TS package for prompts/datasets/scores) and **Claim 11** (self-hosted Langfuse version coupling per SDK). This note supplies the exact client-v6 → server-v4.59.0 boundary, and the `@langfuse/client@^5.11.1` fallback for older servers, that the SDK overview does not state.
  - `source-notes/docs-langfuse-compatibility.md` **Claim 5** and **Claim 14** (self-hosted SDK-major minimum server versions; current JS/TS v5 ≥ OSS 3.63.0). This note adds a *newer* client major (v6) with a stricter floor (self-hosted v4.59.0+). Recorded as version drift, not a contradiction: the compatibility note predates the v6 requirement and can be updated rather than disputed.
  - `source-notes/docs-langfuse-cli.md` **Claim 4** (CLI/SDK/public-API credential surface is `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL`). This note extends the credential surface with promptfoo's alias and precedence rules, where the Langfuse-native `LANGFUSE_BASE_URL` can be silently overridden by `LANGFUSE_HOST`.
- **Contradicts**: None. No contradiction issue filed. The only near-miss is the SDK-generation difference with `docs-langfuse-compatibility.md` (v5/OSS ≥ 3.63.0 vs promptfoo's v6/self-hosted ≥ 4.59.0). Both are vendor-documented and can be simultaneously true — v6 is a later SDK major with a later server floor — so it is a conditioning/version variable, not opposing claims. The compatibility note should be refreshed for v6; see Extraction Notes.
- **Novel** (not present in the corpus before this note):
  - The optional `@langfuse/client` dependency and the **v6 ↔ self-hosted Langfuse v4.59.0** coupling, with **`@langfuse/client@^5.11.1`** as the older-server fallback (Claim 2). `docs-langfuse-compatibility.md` documents JS/TS v5 and OSS ≥ 3.63.0, not this boundary.
  - **`LANGFUSE_HOST` beating `LANGFUSE_BASE_URL`** when both are set (Claim 3) — the corpus documents both variable names but not their tie-break.
  - **`--env-file` / `config.env` precedence over shell exports** (Claim 4) — the reverse of the usual assumption; not in the promptfoo configuration notes.
  - **SDK-free trace retrieval** via Langfuse's public API (Claim 5) and the concrete `langfuse` trace-provider requirement for **Cloud or self-hosted v4**, keyed on the OTel `traceparent` and the v2 Observations API (Claim 6) — a new observability-path fact.
  - The consumer-side confirmation that **10-minute ingestion delay makes earlier Langfuse versions unusable for eval-time trace fetching** (Claim 7), independent of Langfuse's own docs.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — eval harness / CI gating)**: Add a "prompt-source dependencies are eval dependencies" item. Concrete change: wherever Ch05 says promptfoo can source prompts from Langfuse, state that this requires an optional `@langfuse/client` package in the same workspace (`npx promptfoo eval` from that project), and that the client major is coupled to a Langfuse server floor — v6 requires Cloud or self-hosted ≥ v4.59.0, older self-hosted servers must pin `@langfuse/client@^5.11.1` (Claims 1–2). Recommend pinning the client and recording the Langfuse server version in the CI image/lockfile, because a client bump can turn a green eval red without any prompt or config change. Cite `docs-promptfoo-configuration-prompts.md` Claims 3–4 for the URI syntax rather than restating it.
- **Chapter 05 / Chapter 02 (Observability — traces as eval input)**: Add a preflight check for trace-based assertions: retrieval uses Langfuse's public API and does **not** need the client SDK (Claim 5), but it queries the **v2 Observations API** and is scoped to **Cloud or self-hosted v4** (Claim 6; cf. `docs-langfuse-compatibility.md` Claims 11/14). The application must propagate the OTel `traceparent` into its spans, and the ingestion path must be real-time (Python SDK ≥ 4.7.0, JS SDK ≥ 5.4.0, or the `x-langfuse-ingestion-version: 4` header) or traces can lag by ten minutes and the eval can fetch an incomplete trace (Claim 7). Recommend a preflight assertion or a `queryDelay`/retry note for the guide's eval-runbook rather than silently trusting an empty trace result.
- **Chapter 06 (Security and Trust — credential/env declaration)**: Add the precedence rule to the "declare, don't infer" guidance: `LANGFUSE_HOST` wins over `LANGFUSE_BASE_URL` (Claim 3), and `--env-file` / config `env` block win over shell exports (Claim 4). The actionable form: audit the *declaration order* in CI, not just which variable names are present, and keep secrets in the process environment rather than `config.env` — the config wins, and per `docs-promptfoo-configuration-guide.md` Claim 7 a config-embedded secret may appear in exported results.

## Extraction Notes

- Source read in full from `https://www.promptfoo.dev/docs/integrations/langfuse` (rendered page fetched 2026-10-26) and from the linked `/docs/tracing/` page's Langfuse subsection (the integration page links there for the external trace provider). Quotes were verified character-for-character against the fetched HTML; the only reformatting is the YAML indentation in Concrete Artifacts, flagged above.
- Scope was set by the Prospector triage: extract the delta (SDK/server coupling, env-var precedence, and whether trace retrieval needs the SDK), not the `langfuse://` grammar. The grammar is owned by `docs-promptfoo-configuration-prompts.md` Claims 3–4; this note does not restate it as novel. The label-based deployment advice and the `@`-in-prompt-ID limitation were deliberately not extracted — generic practice and a parsing footnote, as the triage assessed.
- `confidence_overall: settled` reflects that these are documented behaviors of shipped tooling (install/resolution, env precedence, provider API/version scope), checkable against an installed promptfoo and a Langfuse instance. It does **not** imply measured validation: the page has no eval traces, metrics, or failure data, and the "unusable for trace fetching" conclusion is a vendor assertion that follows from the documented 10-minute delay rather than from a demonstrated incident.
- `miner-related-notes.md` candidates — disposition (all dismissed as non-overlapping; listed for completeness): `docs-promptfoo-enterprise-findings-reports.md` (red-team findings export, not integration deps); `docs-langfuse-mcp-server.md` (docs MCP server, not trace retrieval); `docs-litellm-evals-api.md` and `docs-litellm-batches-api.md` (LiteLLM eval/batch APIs, unrelated); `blog-pagerduty-sre-agent-triage.md` (incident triage, unrelated); `docs-promptfoo-pi-scorer.md` (Pi scorer, unrelated); `docs-google-sre-eliminating-toil.md`, `docs-google-sre-reliable-product-launches.md`, and `docs-google-sre-team-lifecycles.md` (SRE org/practice, unrelated); `docs-promptfoo-deterministic-metrics.md` (assertion types, unrelated to integration dependencies). Additional cross-references were found by searching `source-notes/` directly and are cited above.
- Version-drift note for the Assayer: `docs-langfuse-compatibility.md` (extracted 2026-07-23) records JS/TS SDK v5 as the current GA client with self-hosted OSS ≥ 3.63.0. This page (last updated 2026-10-25) requires `@langfuse/client` v6 for Cloud/self-hosted ≥ 4.59.0, with v5.11.1 as the supported fallback for older servers. No contradiction issue was filed because the two statements are compatible across SDK generations; the older note is simply behind the current client major and should be refreshed.
- No paywall or access issue; the page is short (~4.8 KB body) as the triage noted, so the note is deliberately scoped to the three incremental facts rather than padded with the generic deployment advice.
