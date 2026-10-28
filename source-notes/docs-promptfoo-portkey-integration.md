---
source_url: https://www.promptfoo.dev/docs/integrations/portkey
source_type: docs
title: "Promptfoo × Portkey Integration — Prompt-Only Retrieval, Two-Credential Splitting, and the Interactive-OAuth CI Trap"
author: "Promptfoo (vendor documentation; page last updated by renovate[bot])"
date_published: 2026-10-26
date_extracted: 2026-10-28
last_checked: 2026-10-28
status: current
confidence_overall: settled
issue: "#1905"
---

# Promptfoo × Portkey Integration

> Promptfoo's Portkey integration page documents two distinct surfaces — prompt
> management via `portkey://` (which fetches *only* the prompt, ignoring
> Portkey-side model/temperature settings) and the Portkey gateway via
> `portkey:` (which splits a Portkey key and an upstream provider key across
> different headers and forwards the provider key only for direct passthrough)
> — plus an MCP Gateway path whose base-URL env var deliberately does **not**
> configure the MCP connection and whose CI auth failure mode is a browser OAuth
> flow rather than a clean error.

## Source Context

- **Type**: docs (vendor integration page, promptfoo × Portkey AI)
- **Author credibility**: Promptfoo, maintainer of the eval harness, documenting
  its own Portkey integration code path. Authoritative for promptfoo's
  documented resolution and forwarding behavior, including the negative
  statements ("does not follow", "does not configure") that are the highest-value
  content on the page. The page is machine-maintained (footer: "Last updated on
  **Oct 26, 2026** by **renovate\[bot\]**"). It contains **no measured
  evidence** — no eval output, no failure trace, no latency/cost figure — so
  confidence here is in *documented behavior*, not observed operation.
- **Scope**: Covers `portkey://` prompt references and variable pass-through,
  the `portkey:` gateway provider, the two-credential model, arbitrary extra
  headers, the provider config option inventory, `PORTKEY_API_BASE_URL`, and the
  Portkey MCP Gateway connection (URL shape, CI API key, OAuth fallback, test
  payload). Does **not** cover Portkey's prompt-management lifecycle, gateway
  routing/policy internals, or eval metrics.
- **Linked page followed**: [Portkey MCP Gateway → Authentication](https://portkey.ai/docs/product/mcp-gateway/authentication)
  (linked from the integration page for the auth details). That page supplies
  the two-layer auth model, workspace-scoped API keys, and credential-isolation
  statement extracted as Claims 12–13; quotes from it are attributed inline.
- **Last updated**: Oct 26, 2026 (live footer). The Prospector triage comments
  cite Oct 25; the live page footer says Oct 26. Treated as current either way.

## Extracted Claims

### Claim 1: The integration exposes two separate surfaces — Portkey prompt management through `portkey://` and the Portkey AI gateway through the `portkey:` provider — and the page treats them as distinct configuration paths
- **Evidence**: The page opens by describing Portkey as a prompt-management-capable observability suite, then has a separate "Using Portkey gateway" section that states the gateway is directly supported.
- **Confidence**: settled (documented product surface)
- **Quote**: "The Portkey AI gateway is directly supported by promptfoo."
- **Our assessment**: Buy it, and treat the distinction as the first setup decision. A team can use Portkey solely as a prompt store (`portkey://<prompt-id>` + any provider) or as the request path (`portkey:<model>`), and the two surfaces have different credential and parameter semantics. Conflating them is how an operator ends up expecting gateway-side settings to apply to an eval that only fetched prompt text (Claim 2).

### Claim 2: `portkey://<prompt-id>` fetches and renders only the prompt — variables are injected from the test case, but promptfoo does **not** follow the temperature, model, or other parameters configured in Portkey; those must be set in the `providers` block
- **Evidence**: The "To reference prompts in Portkey" section describes variable plug-in and rendered-prompt return, then explicitly states the parameter limitation.
- **Confidence**: settled (documented product behavior; the page offers no mitigation)
- **Quote**: "Note that promptfoo does not follow the temperature, model, and other parameters set in Portkey. You must set them in the `providers` configuration yourself."
- **Our assessment**: This is the highest-value claim on the page and a genuine reproducibility trap. The `portkey://` prefix makes an eval look like it is testing "the Portkey prompt" while the model and decoding parameters come from promptfoo, not from the same Portkey object production reads. Unless the operator mirrors those settings in `providers`, a green eval can validate a prompt under a different model/temperature than production uses. The page documents the risk and gives no mechanism to detect or reconcile the drift — so the guide should require an explicit parameter mirror/review step, not assume prompt-store parity.

### Claim 3: A Portkey request can carry two credentials in two different places — the Portkey key as `x-portkey-api-key` (`PORTKEY_API_KEY` / `portkeyApiKey`) and the upstream provider key as `Authorization: Bearer` (`OPENAI_API_KEY` / `apiKey`)
- **Evidence**: The "Credentials" section's explicit two-row table naming each credential, header, and configuration source.
- **Confidence**: settled (documented credential contract)
- **Quote**: "A Portkey request can carry two credentials, and they are sent in different places:"
- **Our assessment**: The split is operationally useful but easy to misread: the `Authorization` header is *not* the Portkey credential. For Ch06 this is a concrete egress-boundary fact — two different secrets with two different destinations — and it means "we set PORTKEY_API_KEY" says nothing about whether an upstream provider key is also leaving the runner. The table should be reproduced in the guide rather than paraphrased.

### Claim 4: The upstream provider key is forwarded only for direct passthrough (e.g. `portkeyProvider: openai` with no slug); when Portkey holds the provider credential via a model-catalog provider slug or a virtual key, promptfoo sends no provider key
- **Evidence**: The paragraph immediately after the credential table, which states the condition and names the passthrough example.
- **Confidence**: settled (documented forwarding rule)
- **Quote**: "When Portkey holds the provider credential — a model catalog provider slug or a virtual key — the Portkey key is all you need, and promptfoo does not forward a provider key. A provider key is only sent for direct passthrough, such as `portkeyProvider: openai` with no slug."
- **Our assessment**: This is the security decision point on the page, and the decision is *implicit in configuration shape*: presence of a provider slug or virtual key flips provider-key forwarding off. There is no documented `forwardProviderKey: false` flag. Ch06's "declare, don't infer" rule therefore applies by analogy — operators must deliberately choose passthrough vs catalog/virtual key and verify the egress surface, because a config edit that adds a slug silently changes which secret leaves the process. The page does not state the reverse direction explicitly (whether adding a provider key while using a slug causes an error or is silently ignored), which is worth flagging as an undocumented edge.

### Claim 5: The `portkey:` provider exposes a fixed configuration inventory — `portkeyApiKey`, `portkeyVirtualKey`, `portkeyMetadata`, `portkeyConfig`, `portkeyProvider`, and `portkeyApiBaseUrl` — and the page's gateway example omits the YAML list marker that its own headers example includes
- **Evidence**: The "Other options" code block lists all six fields; the gateway example immediately above it starts `providers:` then `id:` with no `-`, while the headers example uses `- id:`. This is a documentation inconsistency, not a behavior claim.
- **Confidence**: settled for the option names; anecdotal for the YAML-shape defect (single-page observation, not run)
- **Quote**: "More complex portkey configurations are also supported."
- **Our assessment**: Treat the option list as the inventory and the missing dash as a docs defect to fix upstream. Copying the page's gateway/options block literally produces a `providers` value that is a mapping, not the list promptfoo expects elsewhere on the same page (`- openai:gpt-5.6`, `- id: portkey:gpt-5.6`). The note reproduces the block verbatim under Concrete Artifacts and flags the defect rather than silently "fixing" it. `portkeyMetadata` is worth a second look in any security review: it is an operator-controlled metadata surface sent through the gateway.

### Claim 6: Additional request headers are sent through `config.headers` and accept arbitrary header names/values
- **Evidence**: The "Credentials" section's `config.headers` example with a custom `x-my-header` entry.
- **Confidence**: settled (documented config surface)
- **Quote**: "To send additional headers, use `config.headers`:"
- **Our assessment**: A useful escape hatch, and another egress surface. In CI configs this is where teams are tempted to put auth or tenant-routing headers; the page gives no validation or allowlist guidance. Ch06 should treat arbitrary headers on a gateway provider as part of the declared request contract, not as inert metadata — especially because headers are a common place for secrets to be duplicated or logged.

### Claim 7: `PORTKEY_API_BASE_URL` configures only the OpenAI-compatible chat-completions endpoint (default `https://api.portkey.ai/v1`) and explicitly does **not** configure the MCP connection; the MCP Gateway URL must be set in `server.url`
- **Evidence**: The Portkey MCP Gateway section's explicit negative statement and the default value.
- **Confidence**: settled (documented non-behavior)
- **Quote**: "`PORTKEY_API_BASE_URL` does not configure the MCP connection. It sets the OpenAI-compatible chat-completions endpoint used by the `portkey:` provider and defaults to `https://api.portkey.ai/v1`. Put the MCP Gateway URL in `server.url` instead."
- **Our assessment**: A textbook configuration footgun and a good Ch05 rule: one env var named for the *gateway* does not redirect *all* Portkey traffic. A team pointing at a self-hosted/preview chat endpoint can believe MCP is also pointed there while the MCP client still uses the hard-coded/`server.url` target. The failure is silent in the sense that the two paths simply diverge; the page gives no preflight or warning that they disagree, so the guide should require an explicit `server.url` check whenever `PORTKEY_API_BASE_URL` is set.

### Claim 8: Portkey exposes each registered MCP server at `https://mcp.portkey.ai/<server-slug>/mcp`, where the slug comes from Portkey's MCP Registry
- **Evidence**: The MCP Gateway section states the URL pattern and the registry source of the slug.
- **Confidence**: settled (documented endpoint shape)
- **Quote**: "The gateway exposes each registered server at `https://mcp.portkey.ai/<server-slug>/mcp`, where `<server-slug>` is the slug from Portkey's MCP Registry."
- **Our assessment**: Concrete enough to configure and to review. Note the endpoint is provider-hosted (`mcp.portkey.ai`), not derived from the chat base URL — reinforcing Claim 7. The slug is an addressing identifier, not a credential; access is still determined by the gateway auth in Claim 9.

### Claim 9: Non-interactive CLI/CI MCP runs require a workspace user API key with `mcp invoke` permission in `x-portkey-api-key`; without an API key Portkey starts an interactive OAuth flow intended for browser clients
- **Evidence**: The MCP Gateway section's CI-specific instruction, plus the explicit statement of the no-key fallback behavior.
- **Confidence**: settled (documented auth behavior; the page does not show the resulting CI error/trace)
- **Quote**: "For non-interactive CLI and CI runs, send a workspace user API key with `mcp invoke` permission in the `x-portkey-api-key` header. Without an API key, Portkey starts an interactive OAuth flow intended for browser-based clients."
- **Our assessment**: This is the sharpest operational claim for Ch05/Ch06: the failure mode is not a 401, it is a wait on a browser consent flow in a headless job. That makes it a timeout/hang rather than a fast-fail, and it is exactly the kind of thing a CI gate must test for. The `mcp invoke` permission is also a least-privilege detail: the CI credential should be a scoped workspace key, not a broad admin key. The page states the behavior but provides no error string or observed trace, so the guide should describe it as documented behavior and add a preflight that asserts a non-interactive auth path.

### Claim 10: Promptfoo can reach Portkey's MCP Gateway in two modes — use the `mcp` provider to test/red-team the server directly, or attach the same server block to a model provider's `mcp` config to test an LLM application that uses the server
- **Evidence**: The opening paragraph of the Portkey MCP Gateway section names both modes and their different evaluation targets.
- **Confidence**: settled (documented configuration pattern)
- **Quote**: "Promptfoo can connect to Portkey's MCP Gateway in two ways. Use the `mcp` provider to test or red team the MCP server directly. To test an LLM application that uses the server, add the same server block to the model provider's `mcp` config."
- **Our assessment**: The distinction matters for what an eval result actually covers: direct `mcp` testing grades the server/tool contract, while the model-provider attachment grades the application's tool-use behavior. Both share the same `server.url` and auth block, so a broken/mis-scoped credential affects both modes. Ch05 should make the target explicit in the eval name so a green "MCP eval" is not read as end-to-end app coverage.

### Claim 11: Each functional MCP test sends one JSON tool call shaped `{"tool": "tool_name", "args": {...}}`; a red-team run reuses the same `id: mcp` target with the `mcp` plugin and converts generated attacks into valid tool calls
- **Evidence**: The paragraph after the `promptfooconfig.yaml` example describes the functional-test payload and the red-team reuse path.
- **Confidence**: settled (documented payload contract)
- **Quote**: "Each functional test sends one JSON tool call in the form `{"tool": "tool_name", "args": {...}}`. For a red-team run, use the same `id: mcp` target with the `mcp` plugin; Promptfoo converts generated attacks into valid calls to the server's tools."
- **Our assessment**: Useful concrete contract: the "prompt" for an MCP functional test is a JSON tool-call payload, not natural language, so assertions like `contains` operate on the tool result. The red-team path is the same target with a different plugin, which means the same auth/URL mistakes propagate into security testing — a good reason to validate the connection with one functional test before spending on a red-team run (consistent with `docs-promptfoo-mcp-server.md` Claim 10's validate → test → subset → full ordering).

### Claim 12 (linked auth page): Portkey MCP Gateway authentication is two independent layers — gateway auth (agent → Portkey: API key, Portkey OAuth, external IdP) and server auth (Portkey → MCP server: OAuth Auto, client credentials, custom headers) — with the agent never seeing upstream credentials
- **Evidence**: The linked authentication page's "Two-Layer Architecture" diagram and table, followed by the credential-isolation statement.
- **Confidence**: settled (documented auth architecture)
- **Quote**: "These layers are independent. An agent authenticates to Portkey with an API key. Portkey authenticates to Linear with OAuth. The agent never sees Linear's OAuth tokens."
- **Our assessment**: This is the architectural fact behind Claim 9 and a strong Ch06 pattern: gateway auth and upstream-server auth are separate trust decisions. It also explains why a CI job only needs the Portkey key (with `mcp invoke`) rather than each upstream MCP credential — provided the gateway already holds the server auth. The page explicitly says the layers are independent; the guide should not assume an upstream 401 implies the gateway key is wrong, or vice versa.

### Claim 13 (linked auth page): Portkey API keys are scoped to workspaces, and the key determines which MCP servers a request can access; keys must carry the `mcp invoke` permission
- **Evidence**: The linked page's "API Key" subsection names workspace scoping, the server-access consequence, and the required permission.
- **Confidence**: settled (documented auth behavior)
- **Quote**: "API keys are scoped to workspaces. The key determines which MCP servers the request can access."
- **Our assessment**: Buy it, and read it as a least-privilege lever: the smallest CI key is one scoped to the workspace and permissions needed for the eval's servers, not a shared operator key. Combined with Claim 9's interactive-OAuth fallback, the failure signature of a missing/insufficient key is a hang, so the permission must be verified in preflight rather than inferred from "the job started."

## Concrete Artifacts

### `portkey://` prompt reference with variable pass-through (integration page, opening example)
```yaml
prompts:
  - 'portkey://pp-test-promp-669f48'

providers:
  - openai:gpt-5.6

tests:
  - vars:
      topic: ...
```
*(Attribution: promptfoo docs "Portkey AI integration". Rendered lines reproduced verbatim; only the original blank lines/indentation are restored.)*

### Portkey gateway provider config — **verbatim, including the missing list marker** (integration page, "Using Portkey gateway")
```yaml
providers:
  id: portkey:gpt-5.6
  config:
    portkeyProvider: openai
```
> "When Portkey holds the provider credential — a model catalog provider slug or a virtual key — the Portkey key is all you need, and promptfoo does not forward a provider key. A provider key is only sent for direct passthrough, such as `portkeyProvider: openai` with no slug."
>
> **Docs defect**: the page's gateway and "Other options" blocks omit the `- ` list marker that its own headers example includes (`- id: portkey:gpt-5.6`). Reproduced as-is; the dash is required for a valid promptfoo `providers` array.

### Credential placement table (integration page, "Credentials")
| Credential | Sent as | Set with |
|---|---|---|
| Your Portkey key | `x-portkey-api-key` | `PORTKEY_API_KEY`, or `portkeyApiKey` in config |
| The upstream provider's key | `Authorization: Bearer` | `OPENAI_API_KEY`, or `apiKey` in config |

> "A Portkey request can carry two credentials, and they are sent in different places:"

### Additional headers (integration page, "Credentials")
```yaml
providers:
  - id: portkey:gpt-5.6
    config:
      portkeyProvider: openai
      headers:
        x-my-header: my-value
```
*(Attribution: promptfoo docs "Credentials". This is the block that *does* include the list marker.)*

### Full option inventory (integration page, "Other options") — **verbatim, missing list marker retained**
```yaml
providers:
  id: portkey:gpt-5.6
  config:
    # Can alternatively set environment variable, e.g. PORTKEY_API_KEY
    portkeyApiKey: xxx

    # Other configuration options
    portkeyVirtualKey: xxx
    portkeyMetadata:
      team: xxx
    portkeyConfig: xxx
    portkeyProvider: xxx
    portkeyApiBaseUrl: xxx
```
*(Attribution: promptfoo docs "Other options". Same missing-dash defect as the gateway block.)*

### Portkey MCP Gateway config (integration page, "Portkey MCP Gateway")
```yaml
prompts:
  - '{{prompt}}'

providers:
  - id: mcp
    config:
      enabled: true
      server:
        name: portkey-gateway
        url: https://mcp.portkey.ai/<your-server-slug>/mcp
        headers:
          x-portkey-api-key: '{{env.PORTKEY_API_KEY}}'

tests:
  # Each test calls one tool. The prompt is a JSON tool-call payload.
  - vars:
      prompt: '{"tool": "your_tool_name", "args": {"param1": "value1"}}'
    assert:
      - type: contains
        value: 'expected result'
```
*(Attribution: promptfoo docs "Portkey MCP Gateway". Verbatim rendered lines.)*

### MCP gateway key requirements (linked Portkey auth page, "API Key")
```json
{
  "headers": {
    "x-portkey-api-key": "your_api_key_here"
  }
}
```
> "API keys are scoped to workspaces. The key determines which MCP servers the request can access."
>
> "Create keys in **Settings > API Keys**. The key must have **`mcp invoke`** permissions."
>
> "These layers are independent. An agent authenticates to Portkey with an API key. Portkey authenticates to Linear with OAuth. The agent never sees Linear's OAuth tokens."

## Cross-References

- **Corroborates**:
  - `source-notes/docs-langfuse-mcp-server.md` **Claim 8** — a separate authenticated MCP server using request-header credentials (Langfuse: Basic Auth built from `pk-lf-...:sk-lf-...`, project-scoped; Portkey: workspace-scoped `x-portkey-api-key` with `mcp invoke`). Both sources show MCP auth carried in the request header, and both contrast with an unauthenticated docs MCP surface (**Claim 4**). This note adds a second vendor instance of the authenticated-MCP pattern.
  - `source-notes/docs-promptfoo-mcp-server.md` **Claim 5** — promptfoo's *own* MCP server documents no auth on `/mcp`/`/health`, the opposite of Portkey's gateway. Same harness, two MCP surfaces with inverted auth postures; the contrast is useful for Ch06 (see Contradicts note below — this is a product-boundary difference, not a contradiction).
  - `source-notes/docs-litellm-gateway-auth-reference.md` **Claim 2** — MCP outbound auth is declared per server via `auth_type` with `oauth2` (PKCE vs M2M) among the modes. Portkey's gateway auth likewise supports API key vs OAuth vs external IdP (linked auth page, Claim 12); this note is another data point that "MCP auth" is a mode family, not a single Bearer-token convention.
- **Contradicts**:
  - None filed. The closest tension is with Ch06's "declare, don't infer" rule (`source-notes/blog-litellm-july-stability-update.md` **Claim 1**: inferring auth from whichever fields are set produced ambiguity and silent fallback). Portkey's provider-key forwarding is likewise switched by *presence* of a catalog slug or virtual key (Claim 4), with no explicit forward/no-forward flag documented. This is **not** a contradiction: LiteLLM's postmortem is about a gateway with ambiguous precedence, while Portkey documents a deterministic condition on a different product. It is a guide-applicability gap — the declared-auth rule should be applied to Portkey config review — not opposing claims about the same system. No contradiction issue filed.
  - The promptfoo-own-MCP-server no-auth posture (`docs-promptfoo-mcp-server.md` Claim 5) vs Portkey's authenticated MCP gateway is also not a contradiction; they are different products/surfaces. Recorded here so the Assayer does not read the contrast as a disputed fact.
- **Extends**:
  - `source-notes/docs-promptfoo-configuration-prompts.md` **Claim 3** and **Claim 5** — own the `portkey://` grammar (version/label forms, external registry schemes), but do not cover the gateways, credentials, parameter non-inheritance, or MCP path. This note deliberately does not re-extract the URI grammar; it extends the same integration with the behavior that determines whether the referenced prompt is evaluated under production-equivalent parameters (Claim 2) and which secrets leave the runner (Claims 3–4).
  - `source-notes/docs-promptfoo-langfuse-integration.md` **Claim 4** — documents that `--env-file`/`config.env` beat shell exports in promptfoo. This Portkey page shows `portkeyApiKey` "Can alternatively set environment variable, e.g. PORTKEY_API_KEY" but documents **no precedence** when both are set. The Langfuse note's rule is the reason that omission matters: a CI job can believe it overrode the key in the shell while a checked-in config value wins. Flagged as a gap rather than asserted behavior.
  - `source-notes/docs-langfuse-mcp-server.md` **Claim 8** and `source-notes/docs-litellm-mcp-control.md` **Claim 7** — per-key/project scoping and tool-level MCP permissions. This note adds Portkey's workspace-scoped key + `mcp invoke` permission as another concrete least-privilege granularity.
- **Novel** (first Portkey note in the corpus):
  - The **two-credential split** (`x-portkey-api-key` vs `Authorization: Bearer`) and the **presence-based forwarding rule** (provider key sent only for passthrough with no catalog slug/virtual key) — Claims 3–4.
  - The **prompt-only retrieval trap**: `portkey://` does not honor Portkey-side model/temperature/parameters — Claim 2.
  - **`PORTKEY_API_BASE_URL` not configuring the MCP connection** and the `mcp.portkey.ai/<server-slug>/mcp` URL shape — Claims 7–8.
  - The **CI failure mode**: missing MCP key starts interactive OAuth instead of failing fast, and the required credential is a workspace key with `mcp invoke` — Claim 9 (plus linked-page Claims 12–13).
  - The **documentation defect** where two of the page's YAML blocks omit the `providers` list marker — Claim 5 / Concrete Artifacts.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — eval config drift / CI gating)**:
  - Add a "prompt-store settings do not travel with the prompt" rule: when promptfoo references a Portkey prompt via `portkey://`, only the prompt text is fetched; `temperature`, `model`, and other Portkey-side parameters must be mirrored in `providers` (Claim 2). The eval can therefore pass against the same prompt version while exercising a different model/decoding setup than production. Recommend recording both the prompt ID and the provider parameters in the gate definition, and reviewing them together.
  - Add a preflight for MCP evals: setting `PORTKEY_API_BASE_URL` does not redirect MCP; verify `server.url` explicitly (Claims 7–8). Require a workspace key with `mcp invoke` for headless runs, and treat the absence of a key as a hang risk, not a 401, because the fallback is an interactive OAuth flow (Claim 9). One functional tool-call test before a red-team run (Claim 11) is the cheap way to prove the credential path.
- **Chapter 06 (Security and Trust — gateway credential routing / egress boundaries)**:
  - Add Portkey as a worked example under "Gateway credential routing: declare, don't infer": the Portkey key and upstream provider key ride in different headers (Claim 3), and the provider key is forwarded **only** for direct passthrough with no catalog slug/virtual key (Claim 4). The actionable form: choose passthrough vs virtual key deliberately, verify which secret leaves the runner, and do not assume that adding a slug leaves the upstream key in place. `config.headers` is an additional declared egress surface, not inert metadata (Claim 6).
  - Add least-privilege MCP auth guidance: a CI credential should be a workspace-scoped key carrying `mcp invoke` (Claims 9, 13), and the gateway-vs-upstream auth layers are independent — an upstream server error does not mean the gateway key is wrong, and vice versa (Claim 12, linked auth page). This complements the corpus's authenticated-MCP patterns in `docs-langfuse-mcp-server.md` Claim 8 and `docs-litellm-gateway-auth-reference.md` Claim 2.

## Extraction Notes

- Source read in full from `https://www.promptfoo.dev/docs/integrations/portkey` (rendered page plus HTML code blocks fetched 2026-10-28), and one substantive linked page followed per MINER.md §1: `https://portkey.ai/docs/product/mcp-gateway/authentication` (linked for auth detail). Quotes were verified character-for-character against the fetched pages. The only reformatting is YAML indentation/blank lines in Concrete Artifacts; token content is verbatim, including the missing `- ` list markers flagged above.
- The page is short, as the Prospector noted, so the note is scoped to the incremental operational/security facts rather than padded with the generic quickstart. The `portkey://` URI grammar is owned by `docs-promptfoo-configuration-prompts.md` Claims 3 and 5 and is not re-extracted here.
- `confidence_overall: settled` reflects that these are documented behaviors of shipped tooling (credential placement, forwarding condition, env-var scope, MCP auth requirement), checkable against an installed promptfoo and a Portkey workspace. It does **not** imply measured validation: the page has no eval output, failure trace, or metrics, and the "interactive OAuth flow" consequence in CI is a vendor statement of behavior, not an observed hang. Claim 5's YAML-shape defect is a single-page observation and is graded anecdotal in its own field.
- `miner-related-notes.md` candidate dispositions (all reviewed):
  - `docs-promptfoo-enterprise-findings-reports.md` — dismissed: red-team findings/report export, no integration or credential surface.
  - `docs-litellm-evals-api.md` — dismissed: LiteLLM's server-side Evaluations API, unrelated gateway.
  - `docs-litellm-batches-api.md` — dismissed: batch rate limiting, unrelated.
  - `blog-pagerduty-sre-agent-triage.md` — dismissed: incident triage, unrelated.
  - `docs-promptfoo-pi-scorer.md` — dismissed: Pi model-graded scorer, unrelated to Portkey.
  - `docs-langfuse-mcp-server.md` — **cited** (Corroborates: authenticated MCP server, request-header credentials, per-key scoping).
  - `docs-google-sre-eliminating-toil.md` — dismissed: toil reduction, unrelated.
  - `docs-google-sre-reliable-product-launches.md` — dismissed: launch process, unrelated.
  - `docs-google-sre-team-lifecycles.md` — dismissed: SRE team org, unrelated.
  - `docs-promptfoo-deterministic-metrics.md` — dismissed: assertion-type reference, no Portkey/gateway content.
- Additional cross-references found by searching `source-notes/` directly: `docs-promptfoo-configuration-prompts.md`, `docs-promptfoo-langfuse-integration.md`, `docs-promptfoo-mcp-server.md`, `docs-litellm-gateway-auth-reference.md`, `docs-litellm-mcp-control.md`, and `blog-litellm-july-stability-update.md` (all cited above and claim-verified per §4b).
- Version/date note for the Assayer: the Prospector triage comments say the page was updated Oct 25, 2026; the live footer says Oct 26, 2026. Recorded as current either way. No paywall or access issue.
