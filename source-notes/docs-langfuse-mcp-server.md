---
source_url: https://langfuse.com/docs/docs-mcp
source_type: docs
title: "Langfuse Docs MCP Server"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.; page contributors Marc Klingen, Lotte Verheyden)
date_published: "unknown (Langfuse vendor docs; page footer © 2022–2026)"
date_extracted: 2026-07-15
last_checked: 2026-07-15
status: current
confidence_overall: settled
issue: "#131"
---

# Langfuse Docs MCP Server

> A setup/config docs page showing how an LLM-observability vendor ships two
> distinct MCP surfaces — an unauthenticated **docs** MCP server (so coding
> agents can self-serve tracing integration) and an authenticated **data
> platform** MCP server (so agents can read/write project data) — with the
> same `streamableHttp` transport, per-client config artifacts, and a REST
> fallback for the docs search tool.

## Source Context

- **Type**: docs (vendor product documentation / onboarding page)
- **Author credibility**: Langfuse is a production LLM-observability/evaluation
  vendor documenting its own shipped surface, so claims about endpoints,
  transport, and auth model are authoritative and factual (settled) rather
  than opinion. The page names two contributors (Marc Klingen — a Langfuse
  co-founder — and Lotte Verheyden).
- **Scope**: Covers the **public Docs MCP server** only — its endpoint, the
  `streamableHttp` transport, per-client install snippets (Cursor, Copilot in
  VSCode, Claude Code, Windsurf, generic clients), and the REST search-docs
  fallback. It does NOT cover tracing internals, pricing, or the MCP tool
  schemas themselves (those are deferred to an external "MCP Reference"). One
  substantive linked page — the **authenticated** data-platform MCP server
  (`/docs/api-and-data-platform/features/mcp-server`) — was followed and is
  extracted below for the dual-mode contrast the Prospector asked about.

## Extracted Claims

### Claim 1: Langfuse exposes its documentation to AI agents through a dedicated, public MCP server whose stated purpose is letting a coding agent auto-integrate Langfuse tracing into a user's codebase
- **Evidence**: The page's opening definition plus a "Core use case" line that
  frames the server as an onboarding accelerator (Cursor reads the docs, then
  writes the tracing integration).
- **Confidence**: settled
- **Quote**: "The Langfuse Docs MCP server exposes the Langfuse docs to AI agents."
- **Our assessment**: This is the load-bearing pattern of the page: docs-as-a-tool.
  Rather than a human reading integration docs, the vendor packages the docs
  behind MCP so the agent retrieves them on demand during a coding session. It
  is a concrete instance of "observability vendors are standardizing on MCP as
  a delivery mechanism for agentic tool use" (the Prospector's key question).

### Claim 2: The primary intended workflow is a coding agent (Cursor et al.) automatically wiring Langfuse tracing into the user's codebase, guided by an example prompt on the get-started page
- **Evidence**: The "Core use case" sentence links to a get-started page with
  "detailed instructions and an example prompt" for agentic onboarding.
- **Confidence**: settled
- **Quote**: "Core use case: Use Cursor (or other AI Coding Agent) to automatically integrate Langfuse Tracing into your codebase, see get started for detailed instructions and an example prompt."
- **Our assessment**: Names the concrete agentic-onboarding loop: the agent
  queries the docs MCP, then edits code to add tracing. This is the "why" behind
  Claim 1 and the reason the server is unauthenticated (see Claim 4) — an agent
  integrating your app shouldn't need Langfuse credentials just to read docs.

### Claim 3: The docs MCP server uses the `streamableHttp` transport, which the page says most clients support; clients that don't (named example: Windsurf) use the `mcp-remote` npx command as a local proxy
- **Evidence**: An explicit transport statement plus a fallback snippet using
  `npx mcp-remote` for non-`streamableHttp` clients, with Windsurf given as the
  concrete example.
- **Confidence**: settled
- **Quote**: "If you use a client that does not support streamableHttp (e.g. Windsurf), you can use the mcp-remote command as a local proxy."
- **Our assessment**: A precise interop detail. The `streamableHttp`-or-proxy
  split is the one non-trivial client-compatibility decision on the page: remote
  HTTP MCP is not yet universal, so the vendor documents a stdio-bridge fallback
  (`mcp-remote`) rather than assuming native support. Worth recording as a
  portability pattern for anyone shipping a remote MCP server.

### Claim 4: The docs MCP endpoint is `https://langfuse.com/api/mcp`, transport `streamableHttp`, with no authentication
- **Evidence**: An explicit "About" list giving endpoint, transport, and
  "Authentication: None".
- **Confidence**: settled
- **Quote**: "Authentication: None"
- **Our assessment**: The no-auth model is deliberate and consistent with the
  content being public documentation. It contrasts sharply with the
  authenticated data-platform MCP server (Claim 8), making Langfuse a clean
  worked example of the "public-read vs authenticated-write" split for MCP
  surfaces.

### Claim 5: The same server is reachable via per-client config artifacts — a URL-only `mcpServers` block for Cursor/generic clients, a `claude mcp add` CLI (or `add-json`) for Claude Code, and a UI flow for Copilot/Windsurf
- **Evidence**: Distinct install tabs each with a concrete artifact: Cursor
  one-click + `mcp.json` URL block; Copilot via Command Palette "MCP: Add
  Server..."; Claude Code via `claude mcp add --transport http ... --scope user`
  (plus a `~/.claude/settings.json` block and a `claude mcp add-json` one-liner);
  Windsurf via "MCP Configuration Panel" + `mcp-remote` config.
- **Confidence**: settled
- **Quote**: "Once added, start a Claude Code session (claude) and type /mcp to confirm the connection."
- **Our assessment**: These are the reusable configuration artifacts the
  Prospector asked the Miner to extract (captured verbatim in Concrete
  Artifacts). The Claude-Code-specific detail — `--scope user` and the
  `~/.claude/settings.json` / project / local scope options — is directly
  relevant to this repo's own Claude Code configuration conventions.

### Claim 6: The underlying docs search is exposed twice — as an MCP tool (`searchLangfuseDocs`) and, independently, as a plain REST endpoint at `https://langfuse.com/api/search-docs`
- **Evidence**: A "REST Endpoint" section states the `searchLangfuseDocs` tool
  is "also available independently as a REST API" with a `curl` example, and
  recommends it for lightweight semantic search "outside of MCP."
- **Confidence**: settled
- **Quote**: "The underlying docs search (searchLangfuseDocs tool) is also available independently as a REST API at https://langfuse.com/api/search-docs."
- **Our assessment**: This is the dual-mode / REST-fallback pattern the
  Prospector flagged, and the most architecturally interesting decision on the
  page. The MCP tool is a thin wrapper over a REST search primitive; the vendor
  ships both so consumers that can't (or won't) speak MCP still get the
  capability. It signals that MCP is a *packaging* layer over an existing REST
  API, not a replacement for one — a useful counter to MCP hype.

### Claim 7: The MCP tool schemas are not documented on this page; an external "MCP Reference" is named as the canonical source for tools, input schemas, and request examples
- **Evidence**: Two pointers ("The MCP Reference is the canonical source for
  current Docs MCP tools, input schemas, and generated request examples") to
  `mcp.reference.langfuse.com`, plus links to the implementation (`route.ts`),
  `llms.txt`, and an "Ask AI" RAG chat.
- **Confidence**: settled
- **Quote**: "The MCP Reference is the canonical source for current Docs MCP tools, input schemas, and generated request examples."
- **Our assessment**: Confirms the Prospector's "thin evidence" read: the page
  is setup-only and pushes tool-schema detail elsewhere. We followed the
  implementation link — `route.ts` is a 29-line Next.js handler that delegates
  GET/POST to an internal `mcpHandler` with `maxDuration = 60` — so the public
  repo exposes no additional architectural detail beyond "stateless HTTP route."

### Claim 8 (linked page): Langfuse also ships a *separate, authenticated* MCP server for the data platform, using a stateless architecture where each API key is project-scoped, with Basic-Auth credentials
- **Evidence**: The authenticated MCP docs page: it is explicitly "the
  authenticated MCP server for the Langfuse data platform," distinct from the
  public docs server; it lists region-specific endpoints
  (`.../api/public/mcp`), `streamableHttp` transport, and Basic-Auth via an
  `Authorization` header built from base64(`pk-lf-...:sk-lf-...`).
- **Confidence**: settled
- **Quote**: "The Langfuse MCP server uses a stateless architecture where each API key is scoped to a specific project."
- **Our assessment**: This is the other half of the dual-mode pattern and the
  most transferable design decision in the whole source: **stateless, per-key,
  project-scoped auth carried in the request header** — no server-side session,
  so the same endpoint safely multiplexes many projects. It is the authenticated
  mirror of Claim 4's no-auth docs server. Strong Ch06 (security) material.

### Claim 9 (linked page): The authenticated server ships both read and write tools by default, and the documented way to get read-only safety is a client-side allowlist, not a server-side role
- **Evidence**: The auth page states both tool classes are enabled by default
  and that restricting to read-only is done by configuring the MCP client with
  an allowlist.
- **Confidence**: settled
- **Quote**: "Both read and write tools are available by default. If you only want to use read-only tools, configure your MCP client with an allowlist to restrict access to write operations."
- **Our assessment**: A notable and slightly risky default: write access is on
  unless the *client* opts out. For SRE/agent use this is exactly the kind of
  blast-radius default that belongs in a security review — an agent with the
  default config can mutate project data. Directly reinforces the corpus's
  MCP-auth-hardening thread (see Cross-References).

### Claim 10 (linked page): For agents that can run CLI tools, Langfuse recommends its "Agent Skill" over the MCP server; reverse-proxy deployments must preserve the public Host header or set `LANGFUSE_MCP_ALLOWED_HOSTS` to avoid a 403
- **Evidence**: The auth page recommends the Agent Skill when the environment
  permits installing CLI tools and running bash, and documents a host-header /
  `LANGFUSE_MCP_ALLOWED_HOSTS` requirement for reverse-proxy setups.
- **Confidence**: settled
- **Quote**: "If you are running AI agents in an environment where you can install CLI tools and run bash commands, we recommend using the Langfuse Agent Skill instead of the MCP server."
- **Our assessment**: Two concrete operational details. The Skill-over-MCP
  recommendation is a small but real signal that MCP is not always the right
  delivery mechanism even for its own vendor — CLI/skill delivery can be
  preferable when the agent has a shell. The `LANGFUSE_MCP_ALLOWED_HOSTS` /
  Host-header note is a real self-hosting footgun worth citing in any MCP
  deployment runbook.

## Concrete Artifacts

### Docs MCP — Cursor / generic client (`mcp.json`) — public, URL-only, no auth
```json
{
  "mcpServers": {
    "langfuse-docs": {
      "url": "https://langfuse.com/api/mcp"
    }
  }
}
```

### Docs MCP — Claude Code CLI registration (user scope)
```bash
claude mcp add \
  --transport http \
  langfuse-docs \
  https://langfuse.com/api/mcp \
  --scope user
```

### Docs MCP — Claude Code manual config (`~/.claude/settings.json`; also project `.claude/settings.json` or local `.claude/settings.local.json`)
```json
{
  "mcpServers": {
    "langfuse-docs": {
      "transportType": "http",
      "url": "https://langfuse.com/api/mcp",
      "verifySsl": true
    }
  }
}
```

### Docs MCP — Claude Code one-liner JSON import
```bash
claude mcp add-json langfuse-docs \
  '{"type":"http","url":"https://langfuse.com/api/mcp"}'
```
Source note: "Once added, start a Claude Code session (claude) and type /mcp to
confirm the connection."

### Docs MCP — Windsurf / non-`streamableHttp` client via `mcp-remote` proxy
```json
{
  "mcpServers": {
    "langfuse-docs": {
      "command": "npx",
      "args": ["mcp-remote", "https://langfuse.com/api/mcp"]
    }
  }
}
```

### Docs MCP — About (verbatim)
```
Endpoint:       https://langfuse.com/api/mcp
Transport:      streamableHttp
Authentication: None
```

### Docs search — REST fallback (independent of MCP)
```bash
curl "https://langfuse.com/api/search-docs?query=Langfuse+Docs+MCP+Server"
```
Source note: "Use this endpoint directly when you need lightweight semantic
search outside of MCP." The MCP tool wrapping this is named `searchLangfuseDocs`.

### Server implementation — `app/api/mcp/route.ts` (from the linked GitHub source)
```typescript
import { NextRequest } from "next/server";
import { mcpHandler } from "@/lib/mcp-handler";

export const maxDuration = 60;

export async function GET(request: NextRequest) { /* delegates to mcpHandler */ }
export async function POST(request: NextRequest) { /* delegates to mcpHandler */ }
```
Both GET and POST delegate to an internal `mcpHandler`; the public route adds
only error handling and a 60s max duration. No transport/tool logic is exposed
in the public repo file.

### Authenticated data-platform MCP — Basic-Auth token construction (linked page)
```bash
echo -n "pk-lf-your-public-key:sk-lf-your-secret-key" | base64
```

### Authenticated data-platform MCP — Claude Code registration (linked page; EU region)
```bash
claude mcp add --transport http langfuse https://cloud.langfuse.com/api/public/mcp \
  --header "Authorization: Basic {your-base64-token}"
```
Region endpoints (all `streamableHttp`, Basic Auth): EU
`cloud.langfuse.com`, US `us.cloud.langfuse.com`, Japan `jp.cloud.langfuse.com`,
HIPAA `hipaa.cloud.langfuse.com`, self-hosted `your-domain.com`, all at
`/api/public/mcp`.

## Cross-References

- **Corroborates**:
  - `blog-litellm-april-townhall-updates.md` **Claim 13** ("Polish MCP
    authentication. Better understand how teams are using agents through
    LiteLLM.") — LiteLLM names MCP auth as an active hardening target; this
    Langfuse source is a concrete instance of the auth surface that thread is
    about (Claim 8's Basic-Auth/project-scoped keys, Claim 9's write-by-default
    tools). Same "MCP auth is a live reliability/security concern" theme.
  - `blog-litellm-april-townhall-updates.md` **Claim 11** ("agent auditability
    (how decisions were made across LLM + MCP + sub-agent inputs/outputs)") —
    the authenticated Langfuse MCP is exactly an "MCP input/output" surface that
    such auditability would have to cover.
  - `blog-incidentio-ai-sre-incident-run.md` **Claim 5** (Claude Code, via the
    incident.io MCP, opens a PR and posts a channel update) — that note's "MCP
    integration point (described but not configured)" gap is filled in the
    abstract here: this source shows what a concrete, documented MCP server
    config looks like (endpoint, transport, auth, per-client snippet), the very
    detail the incident.io article omitted.
  - `docs-datadog-llm-observability.md` (Concrete Artifacts framework list; and
    **Claim 11** on zero-code auto-instrumentation) — Datadog lists `MCP` among
    auto-instrumented frameworks for both `ddtrace` and `dd-trace`. Datadog
    *observes* MCP traffic; Langfuse *ships* MCP servers. Two vendors, opposite
    ends of the same MCP-as-first-class-surface trend.

- **Contradicts**: None. This is vendor setup documentation; it adds
  tool-specific mechanism, not advice that opposes any existing note. No
  contradiction issue filed.

- **Extends**:
  - `docs-langfuse-datasets.md` and `docs-langfuse-evaluation-core-concepts.md`
    — sibling pages from the same vendor docs. Those notes cover *what* Langfuse
    does (datasets, evals); this one covers *how agents reach Langfuse* (the MCP
    delivery layer). Together they sketch the vendor's full agent-facing surface.

- **Novel** (not in the corpus before this note):
  - The **dual-mode MCP pattern**: one vendor shipping a public, no-auth *docs*
    MCP server (Claim 4) alongside an authenticated, project-scoped *data*
    MCP server (Claim 8) — the public-read/authenticated-write split for MCP.
  - **MCP-as-a-wrapper-over-REST**: the same search capability exposed as both
    an MCP tool (`searchLangfuseDocs`) and a plain REST endpoint (Claim 6),
    showing MCP as a packaging layer, not a replacement for the underlying API.
  - **`streamableHttp`-or-`mcp-remote`-proxy** portability handling for clients
    without native remote-MCP support (Claim 3).
  - **Stateless, header-carried, project-scoped auth** for a multi-tenant MCP
    endpoint, with read/write-by-default tools gated only by a client-side
    allowlist (Claims 8–9) — a concrete MCP blast-radius default.
  - The **Agent-Skill-over-MCP** vendor recommendation for shell-capable agents
    and the `LANGFUSE_MCP_ALLOWED_HOSTS` reverse-proxy requirement (Claim 10).

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Add the docs-MCP config artifacts as a
  worked example of registering a remote MCP server with a coding agent —
  specifically the Claude Code `claude mcp add --transport http ... --scope user`
  CLI and the `~/.claude/settings.json` scope options (user/project/local),
  which mirror this repo's own Claude Code conventions. Also record the
  `streamableHttp`-vs-`mcp-remote` portability fallback (Claim 3) as a gotcha
  when a target client lacks native remote-MCP support. Evidence: Claims 3, 5,
  and the Concrete Artifacts.
- **Chapter 06 (Security and Trust)**: This is the highest-value target. Use the
  dual-mode contrast (Claim 4 no-auth docs vs Claim 8 authenticated data plane)
  and Claim 9's *write-tools-on-by-default, restrict-via-client-allowlist* model
  as a concrete MCP blast-radius example: an SRE connecting an agent to a data
  MCP inherits write access unless they explicitly allowlist read-only tools.
  Pair with the `LANGFUSE_MCP_ALLOWED_HOSTS` / Host-header 403 note (Claim 10)
  as a self-hosting hardening item. Ties directly to the LiteLLM "polish MCP
  authentication" thread (Cross-References). Evidence: Claims 8, 9, 10.
- **Chapter 02 (Observability)**: Add a short note that observability vendors
  are shipping MCP as a first-class agent-facing surface (Langfuse ships servers;
  Datadog auto-instruments MCP traffic — `docs-datadog-llm-observability.md`),
  so "MCP" is now both something you *expose* and something you *trace*. Keep it
  brief — this page is setup docs, not an experience report. Evidence: Claims 1,
  6, and the Datadog cross-reference.
- **Not recommended**: Do not over-read this page. It is onboarding/config
  documentation with no metrics, no failure cases, and no practitioner
  experience. Cite it for the concrete config artifacts and the dual-mode/auth
  patterns, not as evidence that MCP-based docs delivery is effective in
  practice (that claim is untested here).

## Extraction Notes

- Source fetched 2026-07-15. WebFetch returned empty for `langfuse.com/docs/*`
  (JS-heavy Next.js render, same as the sibling `docs-langfuse-datasets.md`),
  so the page was retrieved with `curl` and readable text extracted from the
  HTML (`<script>`/`<style>`/`<svg>` stripped, entities decoded, shiki code
  blocks reassembled). All quotes are taken from the rendered prose (the "About"
  list, the transport paragraph, the REST-endpoint paragraph), not from
  extraction artifacts, and are verbatim.
- Per MINER.md §1, substantive linked pages were followed:
  1. `/docs/api-and-data-platform/features/mcp-server` (the **authenticated**
     data-platform MCP server) — substantive; contributed Claims 8–10 and the
     Basic-Auth / regional-endpoint artifacts. This is the source of the
     dual-mode contrast the Prospector's triage asked for.
  2. `app/api/mcp/route.ts` on GitHub (the docs-MCP implementation) — a 29-line
     Next.js route delegating to an internal `mcpHandler`; extracted as a
     Concrete Artifact but exposes no further architecture (Claim 7).
  Not followed: the external `mcp.reference.langfuse.com` tool-schema reference
  (out of scope for this note — it documents individual tool input schemas, not
  patterns) and the `llms.txt` family (link indexes, not prose).
- `confidence_overall: settled` because these are factual claims about a shipped
  vendor surface (endpoints, transport, auth model, config syntax) — they are
  authoritative, not opinion. This does NOT mean the *pattern's value* is proven;
  the page offers no evidence that docs-MCP onboarding works well in practice
  (noted under Guide Impact). The Prospector's "novelty: low / thin evidence"
  read is respected: the note foregrounds the genuinely novel bits (dual-mode
  MCP, MCP-over-REST, stateless per-key auth, write-by-default tools) and frames
  the rest as reusable config artifacts.
- No part of the source was paywalled; both the docs page and the authenticated
  MCP page are publicly readable. No contradiction with existing notes surfaced,
  so no contradiction issue was filed.
