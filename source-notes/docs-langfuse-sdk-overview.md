---
source_url: https://langfuse.com/docs/observability/sdk/overview
source_type: docs
title: "SDKs Overview — Langfuse"
author: "Langfuse (Langfuse GmbH / Finto Technologies Inc.; page contributors include Hassieb Pakzad, Jannik Maierhöfer, Milana Gurbanova)"
date_published: n.d. (living documentation; page footer © 2022–2026)
date_extracted: 2026-07-18
last_checked: 2026-07-18
status: current
confidence_overall: settled
issue: "#302"
---

# SDKs Overview — Langfuse

> An onboarding/overview page for the Langfuse Python and JS/TS SDKs covering
> installation, credential/region configuration, three instrumentation methods
> (context manager, decorator, manual observations), the OpenTelemetry-based
> architecture (OTel span processor for JS/TS, auto-setup for Python), the
> trace/span/generation/event data model in SDK terms, flush/shutdown behavior
> for short-lived applications, singleton client patterns, and attribute
> propagation. Fills the SDK-setup gap between existing Langfuse notes that
> assume tracing is already wired.

## Source Context

- **Type**: docs (vendor product documentation / SDK onboarding page)
- **Author credibility**: Langfuse is a production LLM-observability/evaluation
  platform; the page documents its own shipped SDK surface (Python v4, JS/TS v5).
  All claims about SDK behavior, API surface, and configuration are authoritative
  and factual (settled). The page lists three named contributors (Hassieb Pakzad,
  Jannik Maierhöfer, Milana Gurbanova). SDK documentation is first-party and
  maintained alongside the shipped code.
- **Scope**: Covers SDK installation, credential/region configuration, three
  instrumentation patterns (context manager, decorator, manual observations),
  the OTel-based architecture and the OTel→Langfuse data-model mapping (trace,
  span, generation, event, context/attribute propagation), the singleton client
  pattern, flush/shutdown behavior for short-lived/serverless apps, the modular
  JS/TS package ecosystem, self-hosted version requirements, and other-language
  support via the OTel endpoint + public API. Does NOT cover: evaluation, prompt
  management, datasets, or the MCP server (each has dedicated page) — the page
  cross-links to those. Does NOT contain practitioner failure reports, metrics,
  or benchmark comparisons.

## Extracted Claims

### Claim 1: Langfuse SDKs expose three instrumentation methods — context manager, decorator, and manual observations — following standard SDK design patterns for LLM observability
- **Evidence**: The Quickstart section names all three, then walks a worked example
  using the context manager with `start_as_current_observation()` for both Python
  and JS/TS SDKs.
- **Confidence**: settled
- **Quote**: "There are three main ways of instrumenting your code with the Python SDK. In this example we will use the context manager. You can also use the decorator or create manual observations."
- **Our assessment**: The three-method pattern (context manager → automatic
  lifecycle, decorator → method-level, manual → full control) is a standard SDK
  API design. The taxonomy itself is not novel — it mirrors patterns in OpenTelemetry
  and Datadog SDKs — but Langfuse's concrete API (`start_as_current_observation`,
  `startActiveObservation`) is the concrete reference the guide needs for Ch02
  instrumentation guidance. The same three choices appear for both Python and JS/TS,
  confirming it is a deliberate, cross-SDK design.

### Claim 2: The Langfuse SDK is designed as fully async with near-zero latency overhead; SDK errors are caught and logged so they cannot break the application
- **Evidence**: The "Key benefits" section lists both properties as named design
  goals. The "Fully async requests" bullet is paired with "Cannot break your
  application: SDK errors are caught and logged."
- **Confidence**: settled
- **Quote**: "Fully async requests, meaning Langfuse adds almost no latency."
- **Our assessment**: The "cannot break your application" design principle is the
  more notable of the two. It addresses a real concern in LLM-observability
  instrumentation: the tracing layer itself becoming a failure point. The async
  design (non-blocking send-and-forget) is the mechanism that makes this work —
  if the SDK fails to reach the backend, the error is swallowed and logged rather
  than raised to the caller. This is a transferable design principle for any
  observability SDK in production, not just Langfuse. Both claims are vendor
  assertions without independent latency benchmarks or error-rate data, but are
  plausible for a well-designed async SDK.

### Claim 3: The Python SDK auto-sets up OpenTelemetry; the JS/TS SDK requires manual OTel SDK setup with a LangfuseSpanProcessor registered in the span processor pipeline
- **Evidence**: The "Initialize OpenTelemetry (JS/TS only)" section states both
  behaviors. The Python tab says "The Python SDK automatically sets up
  OpenTelemetry when initializing the client." The JS/TS tab explains that
  "The JS/TS SDK's tracing is built on top of OpenTelemetry, so you need to set
  up the OpenTelemetry SDK" with a code example using `NodeSDK` and
  `LangfuseSpanProcessor`.
- **Confidence**: settled
- **Quote**: "The JS/TS SDK's tracing is built on top of OpenTelemetry, so you need to set up the OpenTelemetry SDK."
- **Our assessment**: This language-split is a practical consideration for any
  setup guide. Python is simpler (one `pip install` + `get_client()` and OTel is
  running), while JS/TS requires a separate `instrumentation.ts` module, three npm
  packages (`@langfuse/tracing`, `@langfuse/otel`, `@opentelemetry/sdk-node`),
  and importing the instrumentation module at the app entry point before any other
  code. The guide should call this out so readers don't expect the same zero-config
  experience across languages. A Next.js note is included: `@vercel/otel` v2+ is
  required if using the Vercel OTel integration (earlier versions lack OpenTelemetry
  JS SDK v2 support).

### Claim 4: The JS/TS LangfuseSpanProcessor exports Langfuse + GenAI/LLM spans by default, with a should_export_span callback for customization (masking, filtering)
- **Evidence**: The JS/TS OTel setup section: "By default, the processor exports
  Langfuse + GenAI/LLM spans" and references "For more options to configure the
  LangfuseSpanProcessor such as masking, filtering, and more, see advanced
  features."
- **Confidence**: settled
- **Quote**: "The LangfuseSpanProcessor is the key component that sends traces to Langfuse."
- **Our assessment**: The should_export_span pattern is the recommended customization
  hook. The page also notes that `blocked_instrumentation_scopes` "still works but is
  deprecated and planned for removal in a future version." This deprecation signal
  is worth recording so the guide recommends `should_export_span` over the deprecated
  mechanism.

### Claim 5: The Langfuse data model maps directly onto OpenTelemetry — an OTel Trace shares its ID with a Langfuse Trace; an OTel Span maps to a Langfuse Observation with typed sub-types (span, generation, event, tool, retrieval, etc.)
- **Evidence**: The "OpenTelemetry foundation" section defines the mapping: "It shares
  the same ID as the OTel trace," and names `Langfuse Span`, `Langfuse Generation`,
  `Langfuse Event`, and "other observation types such as tool calls, RAG retrieval
  steps, etc."
- **Confidence**: settled
- **Quote**: "The Langfuse SDKs are built on top of OpenTelemetry."
- **Our assessment**: This is the architectural foundation claim of the page and the
  connective tissue between the glossary's observation-type taxonomy (#255) and the
  SDK code that produces those observations. The SDK does not define its own
  telemetry protocol — it wraps OTel spans with Langfuse semantic types. This
  directly corroborates the glossary note (Claim 7: "Langfuse is built on
  OpenTelemetry") and the Honeycomb OTel GenAI conventions note (Claim 7). The
  practical consequence: any OTel-instrumented library in your stack automatically
  generates Langfuse-compatible trace data.

### Claim 6: Langfuse SDKs provide wrapper objects (LangfuseSpan, LangfuseGeneration) around native OTel spans that offer convenience methods for Langfuse-specific features (scoring, media handling) while remaining native OTel spans under the hood
- **Evidence**: The SDK overview states this explicitly in the OTel foundation section.
- **Confidence**: settled
- **Quote**: "The Langfuse SDKs provide wrappers around OTel spans (LangfuseSpan, LangfuseGeneration) that offer convenient methods for interacting with Langfuse-specific features like scoring and media handling, while still being native OTel spans under the hood."
- **Our assessment**: This wrapper-preserving-identity pattern is notable as an API-design
  choice: the SDK extends OTel spans with Langfuse sugar (`.update_trace()`,
  `propagate_attributes()`, score attachment) but the underlying span remains
  OTel-native and is visible to any OTel consumer. This means a Langfuse-instrumented
  app can send the same spans to any OTel-compatible backend simultaneously — there is
  no vendor lock-in at the SDK level beyond the convenience API.

### Claim 7: The Langfuse Python SDK client is a singleton — get_client() returns one instance per public_key; creating multiple Langfuse instances with the same public_key reuses the singleton silently
- **Evidence**: The Client Setup section: "The Langfuse client is a singleton. It can be
  accessed anywhere in your application using the get_client() function." And: "If you
  create multiple Langfuse instances with the same public_key, the singleton instance is
  reused and new arguments are ignored."
- **Confidence**: settled
- **Quote**: "The Langfuse client is a singleton."
- **Our assessment**: This is an important initialization detail that the guide's Ch02
  instrumentation setup should call out. The singleton pattern means you can call
  `get_client()` from anywhere without coordinating initialization — useful for
  modular apps — but it also means explicit constructor arguments beyond the first call
  are silently ignored. Anyone switching from the `Langfuse()` constructor to
  `get_client()` (or vice versa) should understand this behavior. The page also
  documents `auth_check()` as a way to verify credentials: `langfuse.auth_check()`
  returns True/False.

### Claim 8: Short-lived applications (serverless functions, CLI tools) must call langfuse.flush() (Python) or sdk.shutdown() (JS/TS) to ensure all events are sent before the process terminates
- **Evidence**: Both language quickstarts end with a flush/shutdown call preceded by a
  "when should I call this?" prompt. The Python code reads `langfuse.flush()` after the
  context-manager block; the JS/TS code reads `main().then(() => sdk.shutdown())`.
- **Confidence**: settled
- **Quote**: "Flush events in short-lived applications" (Python SDK code comment) and
  "Shutdown flushes events and is required for short-lived applications" (JS/TS SDK code
  comment).
- **Our assessment**: This is a practical operational detail that matters for serverless
  and ephemeral environments where the process terminates as soon as the function
  returns. Without explicit flush/shutdown, pending telemetry batches would be lost. The
  page links to a detailed FAQ question ("When should I call langfuse.flush()?") but
  does not specify the flush() implementation (timeout, batch size, retry). The guide
  should reference this as a known gotcha for Lambda/Cloud Functions deployments.

### Claim 9: The JS/TS SDK is modular — 7 npm packages with distinct responsibilities (core, client, browser, tracing, otel, openai, langchain) and environment constraints
- **Evidence**: An explicit table lists each package, its description, and the runtime
  environment it supports (Universal JS, Browser, or Node.js ≥ 20).
- **Confidence**: settled
- **Quote**: "The Langfuse JS/TS SDK is designed to be modular."
- **Our assessment**: The modularity is notable because it means the guide must
  specify the right combination of packages for a given scenario. A basic tracing
  setup needs `@langfuse/tracing` + `@langfuse/otel` + `@opentelemetry/sdk-node` (3
  packages). Adding prompt management/datasets adds `@langfuse/client`. Adding OpenAI
  auto-instrumentation adds `@langfuse/openai`. The `@langfuse/browser` package is
  unique: it works in browser environments for public-key score ingestion only. A
  concrete reference table is extracted in Concrete Artifacts.

### Claim 10: Attribute propagation via propagate_attributes() automatically distributes user_id, session_id, metadata, version, tags, and environment (Python only) from a parent observation to all child observations
- **Evidence**: The OTel foundation section: "Certain trace attributes (user_id,
  session_id, metadata, version, tags, and request-scoped environment in the Python
  SDK) can be automatically propagated to all child observations using
  propagate_attributes()."
- **Confidence**: settled
- **Quote**: "Ensure consistent attribute coverage across all observations in a trace."
- **Our assessment**: Attribute propagation is a practical convenience that solves a
  real problem: ensuring every span in a trace carries the same identifying metadata
  without repeating it at each instrumentation call site. The page also mentions OTel
  "context propagation" (automatic parent-child span hierarchy) as a separate mechanism
  — attribute propagation is Langfuse-specific and complements it. The Python-only note
  on request-scoped `environment` is a small but real cross-language difference.

### Claim 11: Self-hosted Langfuse deployments have minimum platform version requirements per SDK: Python SDK v3 requires ≥ 3.125.0, TypeScript SDK v4 requires ≥ 3.95.0
- **Evidence**: A collapsible "Requirements for self-hosted Langfuse" section.
- **Confidence**: settled
- **Quote**: "If you are self-hosting Langfuse, the Python SDK v3 requires Langfuse platform version ≥ 3.125.0 and the TypeScript SDK v4 requires Langfuse platform version ≥ 3.95.0 for all features to work correctly."
- **Our assessment**: A concrete dependency constraint for anyone running Langfuse
  self-hosted. The guide should reference this in any self-hosting section so readers
  know the SDK and platform versions are coupled. Note the page documents SDK v3/v4
  requirements alongside the current SDK v4 (Python) / v5 (JS/TS) — legacy versions
  have separate requirements.

### Claim 12: For languages other than Python and JS/TS, Langfuse supports instrumentation via the OpenTelemetry endpoint (sending OTel spans directly) and the public API (prompt management, evaluation, querying)
- **Evidence**: The "Other languages" section at the bottom of the page lists 10 OTel
  SDKs (Kotlin/Java via JetBrains Tracy, Java, .NET, Go, C++, Erlang/Elixir, Ruby,
  PHP, Rust, Swift) plus community-maintained SDKs.
- **Confidence**: settled
- **Quote**: "For other languages, you can use our OpenTelemetry endpoint to instrument your application and use the public API to use Langfuse prompt management, evaluation, and querying."
- **Our assessment**: This confirms Langfuse's architecture is OTel-native rather than
  language-forking: any language with an OTel SDK can send traces to Langfuse. The
  corollary is that Langfuse-specific features (prompt management, evaluation, datasets)
  require the public REST API in non-supported languages — there is no SDK convenience
  layer. Useful for the guide's "choosing an observability platform" section when the
  stack includes polyglot or non-Python/JS services.

## Concrete Artifacts

### Three instrumentation methods — Python SDK (context-manager pattern from Quickstart)
```python
from langfuse import get_client

langfuse = get_client()

# Create a span using a context manager
with langfuse.start_as_current_observation(
    as_type="span",
    name="process-request"
) as span:
    # Your processing logic here
    span.update(output="Processing complete")

    # Create a nested generation for an LLM call
    with langfuse.start_as_current_observation(
        as_type="generation",
        name="llm-response",
        model="gpt-3.5-turbo"
    ) as generation:
        # Your LLM call logic here
        generation.update(output="Generated response")

# All spans are automatically closed when exiting their context blocks
# Flush events in short-lived applications
langfuse.flush()
```
Source: langfuse.com/docs/observability/sdk/overview (Quickstart — Python tab, code
block verbatim with prose comments preserved).

### Three instrumentation methods — JS/TS SDK (startActiveObservation pattern from Quickstart)
```typescript
import { sdk } from "./instrumentation";
import { startActiveObservation } from "@langfuse/tracing";

async function main() {
    await startActiveObservation("my-first-trace", async (span) => {
        span.update({
            input: "Hello, Langfuse!",
            output: "This is my first trace!",
        });
    });
}

// Shutdown flushes events and is required for short-lived applications
main().then(() => sdk.shutdown());
```
Source: langfuse.com/docs/observability/sdk/overview (Quickstart — JS/TS tab, code
block verbatim with prose comments preserved).

### JS/TS OTel setup — LangfuseSpanProcessor registration
```typescript
import { NodeSDK } from "@opentelemetry/sdk-node";
import { LangfuseSpanProcessor } from "@langfuse/otel";

const sdk = new NodeSDK({
    spanProcessors: [new LangfuseSpanProcessor()],
});

sdk.start();
```
Source: langfuse.com/docs/observability/sdk/overview (Initialize OpenTelemetry (JS/TS
only) section, code block verbatim).

### Python client — singleton pattern with auth check
```python
from langfuse import get_client

langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")
```
Source: langfuse.com/docs/observability/sdk/overview (Client Setup — Python SDK tab,
code block verbatim).

### JS/TS modular packages table
```
Package              | Description                                                | Environment
---------------------|------------------------------------------------------------|----------------
@langfuse/core       | Core utilities, types, and logger shared across packages.  | Universal JS
@langfuse/client     | Client for features like prompts, datasets, and scores.    | Universal JS
@langfuse/browser    | Browser-safe client for public-key score ingestion.        | Browser
@langfuse/tracing    | Core OpenTelemetry-based tracing functions.                | Universal JS
@langfuse/otel       | The LangfuseSpanProcessor to export traces to Langfuse.    | Node.js ≥ 20
@langfuse/openai     | Automatic tracing integration for the OpenAI SDK.          | Universal JS
@langfuse/langchain  | CallbackHandler for tracing LangChain applications.        | Universal JS
```
Source: langfuse.com/docs/observability/sdk/overview (Install the SDK — JS/TS tab,
packages table verbatim).

### Credentials / data regions configuration
```
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_BASE_URL = "https://cloud.langfuse.com"  # 🇪🇺 EU region
# Other Langfuse data regions include 🇺🇸 US: https://us.cloud.langfuse.com,
# 🇯🇵 Japan: https://jp.cloud.langfuse.com and ⚕️ HIPAA: https://hipaa.cloud.langfuse.com
```
Source: langfuse.com/docs/observability/sdk/overview (Configure credentials section,
.env example verbatim).

### Self-hosted version requirements
```
Python SDK v3   requires Langfuse platform version ≥ 3.125.0
TypeScript SDK v4 requires Langfuse platform version ≥ 3.95.0
```
Source: langfuse.com/docs/observability/sdk/overview ("Requirements for self-hosted
Langfuse" collapsible section, verbatim).

## Cross-References

- **Corroborates**:
  - `docs-langfuse-glossary.md` (#255) **Claim 1** (Session ⊃ Trace ⊃ Observation
    hierarchy) and **Claim 2** (observation-type taxonomy). The SDK overview's OTel
    foundation section (this note, Claim 5) confirms the same containment model in
    SDK terms: "A Langfuse trace collects observations and holds trace attributes"
    and observations are typed (span, generation, event, tool, retrieval, etc.).
  - `docs-langfuse-glossary.md` (#255) **Claim 7** ("Langfuse is built on
    OpenTelemetry"). The SDK overview's "The Langfuse SDKs are built on top of
    OpenTelemetry" (this note, Claim 5) restates this verbatim and adds the
    architectural detail — OTel Trace ID is shared with Langfuse Trace, OTel spans
    become Langfuse Observations.
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 2** (Scores are
    Langfuse's universal data object for evaluation). This SDK page references
    evaluation as a downstream consumer of SDK instrumentation — "With the SDK set
    up, you can: ... Run Experiments and create Scores" — confirming that the
    evaluation features in #195 depend on SDK tracing being wired first.
  - `docs-datadog-llm-observability.md` (#91) **Claim 4** (SDK auto-instrumentation
    for frameworks). The Langfuse SDK's `@langfuse/openai` and `@langfuse/langchain`
    packages fill the same role — framework-specific auto-instrumentation — for
    Langfuse as Datadog's SDK auto-instrumentation fills for Datadog. Both vendors
    offer both auto-instrumentation and manual trace API.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (#2) **Claim 7**
    (OTel GenAI semantic conventions standardize attribute naming). Langfuse's
    `gen_ai.*` span output and OTel foundation (Claim 5) confirm the same
    ecosystem standardization pressure: both Honeycomb and Langfuse build on OTel
    GenAI conventions.

- **Contradicts**: None. This is vendor SDK documentation with factual claims about
  the shipped API surface. All overlapping claims in the cross-referenced notes are
  consistent. No contradiction issue filed.

- **Extends**:
  - `docs-langfuse-glossary.md` (#255). The glossary defines the observation-type
    taxonomy *what* observations are; this SDK page documents *how to create them in
    code* — `start_as_current_observation(as_type="generation", ...)` gives the
    glossary's abstract types concrete SDK API surface. Together they form the
    prerequisite knowledge for Ch02 instrumentation guidance.
  - `docs-langfuse-evaluation-core-concepts.md` (#195). The eval note describes
    the evaluation loop and Score model but says "this section documents tracing
    related features" then immediately points to this page. This SDK overview is
    the assumed prerequisite — you cannot run evaluations (#195) without SDK
    instrumentation (#302) being wired first.
  - `docs-langfuse-datasets.md` (#196). The datasets note shows `create_dataset`,
    `create_dataset_item`, etc. as SDK calls, but never documents how the SDK client
    is initialized or configured. This SDK overview provides the initialization
    layer (credentials, client singleton, OTel setup) that the datasets code
    snippets assume. The `@langfuse/client` package (Claim 9) is the specific
    package datasets code requires.
  - `docs-langfuse-mcp-server.md` (#131). The MCP server is an alternative data
    ingestion channel; this SDK page documents the primary (direct SDK) ingestion
    path. Together they cover the two ways telemetry reaches Langfuse.

- **Novel** (not present in the corpus before this note):
  - The **three-instrumentation-method taxonomy** (context manager, decorator,
    manual observations) as SDK API design — a concrete reference for the guide's
    Ch02 SDK setup guidance (Claim 1).
  - The **"cannot break your application" / fail-safe instrumentation** design
    principle — SDK errors are caught and logged rather than propagated (Claim 2).
  - The **async-first, near-zero-latency latency design** assertion (Claim 2).
  - The **Python OTel auto-setup vs JS/TS manual OTel setup** split — a critical
    cross-language difference with practical setup implications (Claim 3).
  - The **`should_export_span` customization hook** and the deprecation of
    `blocked_instrumentation_scopes` (Claim 4).
  - The **LangfuseSpan / LangfuseGeneration wrapper objects** — the API-preserving
    wrapper-around-native-OTel pattern (Claim 6).
  - The **singleton client pattern** in the Python SDK and its `auth_check()`
    verification method (Claim 7).
  - The **flush() / shutdown() requirement** for short-lived/serverless
    applications — a concrete operational gotcha (Claim 8).
  - The **JS/TS modular package design** — 7 packages with environment constraints
    (Claim 9, full table in Concrete Artifacts).
  - **Attribute propagation** via `propagate_attributes()` for automatic metadata
    distribution across child observations (Claim 10).
  - **Self-hosted version coupling** — SDK and platform versions are linked
    (Claim 11).
  - The **"other languages via OTel endpoint"** architecture (Claim 12) — OTel
    SDKs for 10+ languages can target Langfuse directly.

## Guide Impact

- **Chapter 02 (Observability / Instrumentation)**: This is the highest-value target.
  The page provides the concrete SDK setup and instrumentation guidance that Ch02
  needs. Specific additions:
  1. **SDK initialization** — Add the credential/env-var setup pattern (Claim 7, the
     singleton client and `get_client()` vs `Langfuse()` constructor) and the `auth_check()`
     verification step. Evidence: Claims 7 and the Concrete Artifacts (Python client
     code block).
  2. **Python vs JS/TS split** — Document that Python auto-sets up OTel while JS/TS
     requires a separate `instrumentation.ts` boot module with `NodeSDK` +
     `LangfuseSpanProcessor` (Claim 3). Include the Next.js `@vercel/otel` v2+
     compatibility note.
  3. **Three instrumentation methods** — Add the context-manager pattern (most common),
     decorator pattern, and manual-observation pattern as a taxonomy, with the context
     manager as the recommended default. Evidence: Claim 1 and the code-block artifacts.
  4. **OTel architecture and data model** — Add the OTel-to-Langfuse mapping (Claim 5)
     with the shared Trace ID, Span→Observation mapping, and typed subtypes. This is
     the architectural foundation any Ch02 section needs before it can explain Langfuse
     traces. Evidence: Claims 5–6.
  5. **Attribute propagation** — Add `propagate_attributes()` as the recommended way
     to ensure consistent user_id/session_id/metadata across all spans in a trace
     (Claim 10). Evidence: Claim 10.
  6. **Serverless flush** — Add the `flush()`/`shutdown()` requirement for Lambda and
     ephemeral environments (Claim 8). Evidence: Claim 8 and code-block comments.
  7. **Fail-safe design** — Mention the catch-and-log error isolation (Claim 2) as a
     rationale for trusting the SDK in production. Evidence: Claim 2.

- **Chapter 04 (Tooling — SDK-based tracing setup)**: Reference this SDK overview as
  the prerequisite for the Langfuse tooling section:
  1. **JS/TS package selection** — Cite the modular packages table (Claim 9, Concrete
     Artifacts) so readers can choose the right packages for their use case (tracing
     only vs adding datasets/eval/prompt management/OpenAI auto-instrumentation).
  2. **Self-hosted version constraints** — Reference Claim 11 for version-coupling
     requirements when self-hosting.
  3. **Polyglot support** — Reference Claim 12 for non-Python/JS setups via the OTel
     endpoint.

- **Chapter 05 (LLM Ops Reliability — eval harness)**: Add one sentence noting that
  "the Langfuse SDK must be initialized and tracing wired (see Ch02 SDK guidance,
  citing this note) before evaluation features (#195) or datasets (#196) can be used"
  — the eval and dataset notes assume SDK wiring but never document it.

## Extraction Notes

- Source fetched 2026-07-18. The page renders server-side and was fully readable
  via `curl` + HTML text extraction (scripts and styles stripped, remaining text
  decoded). All quotes are character-for-character from the rendered prose.
- The page's collapsible "Requirements for self-hosted Langfuse" and "Legacy
  documentation" sections were expanded and read in full. The advanced features,
  troubleshooting, Python/JS reference, and upgrade path links at the bottom
  ("Learn more") were noted but not followed — they link to sub-pages (instrumentation
  detail, API references) that document individual method signatures rather than
  architectural patterns, and the Prospector triage scope asked for the SDK overview
  patterns only.
- This is vendor onboarding documentation with no failure cases, no benchmarks, and
  no practitioner experience. `confidence_overall` is **settled** because the claims
  are factual about a shipped SDK surface (API signatures, configuration, data model).
  The underlying pattern value (e.g., "is the fail-safe design effective in practice?")
  is untested here — that belongs in a practitioner source.
- A significant amount of the page's content (the DataDog-like claims that OTel
  standardization reduces vendor lock-in, the general tracing model) is incremental
  — well-covered by the existing Honeycomb OTel conventions note, the Datadog note,
  and the Langfuse glossary note. The extraction focuses on what is genuinely novel
  to the corpus (see Novel section above) and on the concrete code/config artifacts
  the guide needs for Ch02 instrumentation setup.
- No contradiction with existing notes was found. The SDK overview's OTel mapping
  (Claim 5) corroborates the glossary's Claim 7 exactly; the flush/shutdown behavior
  (Claim 8) is new but not contradictory to anything in the eval or dataset notes.
  No contradiction issue filed.
