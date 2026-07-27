---
source_url: https://docs.litellm.ai/blog/mcp-stdio-command-injection-april-2026
source_type: failure-report
platform: blog
title: "Security Update: CVE-2026-30623 — Command Injection via Anthropic's MCP SDK"
author: "Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-04-21
date_extracted: 2026-07-27
last_checked: 2026-07-27
status: current
confidence_overall: settled
issue: "#595"
---

# Failure Report: CVE-2026-30623 — MCP Stdio Command Injection in LiteLLM

> A critical authenticated RCE (CVE-2026-30623) in LiteLLM's MCP stdio transport allowed authenticated users with MCP server creation permissions to execute arbitrary OS commands on the proxy host because the `command` field flowed directly into `StdioServerParameters` without validation. The fix introduces a command allowlist (`MCP_STDIO_ALLOWED_COMMANDS`), Pydantic-level validation, runtime re-validation, and PROXY_ADMIN role gating — a defense-in-depth pattern applicable to any LLM gateway implementing MCP stdio support.

## Source Context

- **Type**: failure-report (CVE disclosure via vendor security blog post)
- **Platform**: Vendor blog post on `docs.litellm.ai/blog` (Docusaurus), published alongside OX Security's disclosure and referenced as CVE-2026-30623.
- **Author credibility**: High — authored by Krrish Dholakia (CEO) and Ishaan Jaffer (CTO) of LiteLLM/BerriAI, the maintainers of the vulnerable project. The disclosure describes the vulnerability mechanism, the four-part patch with code-level detail (the allowlist constant, Pydantic validation, runtime re-validation, PROXY_ADMIN gating), version table, and upgrade impact.
- **Scope**: A single CVE (CVE-2026-30623) covering command injection in LiteLLM's MCP stdio transport. Covers the vulnerability mechanism, the four-part fix, affected versions, and operator action items. Does NOT cover other MCP transport types (e.g., streamableHttp), the upstream MCP SDK vulnerability from Anthropic, or the broader OX Security cross-ecosystem writeup.
- **Discovery**: OX Security research team — Moshe Siman Tov Bustan, Mustafa Naamnih, and Nir Zadok.

## What Was Attempted

- **Goal**: Add an MCP server to the LiteLLM proxy via JSON configuration with `transport: stdio`, specifying a `command` and `args` value. This is a legitimate configuration path: users connect MCP stdio servers (e.g., `npx`, `uvx`, `python`-based MCP servers) to the LiteLLM proxy, which then exposes those MCP tools through the proxy's routing layer.
- **Tool/approach**: LiteLLM Proxy's MCP server creation API endpoints. The `command` field of `StdioServerParameters` was accepted and passed directly to a subprocess call through the MCP SDK.
- **Setup**: LLLM proxy deployment with MCP server creation enabled and an authenticated user who has permission to create MCP servers.

## What Went Wrong

- **Symptoms**: An authenticated user with permission to create MCP servers could specify an arbitrary `command` value (e.g., any OS command) in the MCP server creation request, and LiteLLM would execute it as a subprocess on the proxy host. The command was passed straight through to `StdioServerParameters` without validation.
- **Severity**: Critical (CVE-2026-30623). However, it required authentication — "not exploitable by unauthenticated users."
- **Reproducibility**: Deterministic — any request to create an MCP server with a crafted `command` to an affected version could trigger command execution.

### Vulnerability Detail A: `StdioServerParameters.command` passed through without validation
- **Evidence**: Blog post describes the data flow explicitly.
- **Quote**: "when adding an MCP server with `transport: stdio`, the `command` field was passed straight through to `StdioServerParameters` and executed as a subprocess on the proxy host. An authenticated user with permission to create MCP servers could run arbitrary commands as the LiteLLM process."
- **Confidence**: settled

### Vulnerability Detail B: This is an authenticated RCE, not unauthenticated
- **Evidence**: Blog post's TLDR explicitly scopes the auth requirement.
- **Quote**: "This was not exploitable by unauthenticated users. The affected endpoints (MCP server creation and the `/mcp-rest/test/*` preview endpoints) all sit behind LiteLLM's auth. An attacker needed a valid LiteLLM API key — and, with the patch, the `PROXY_ADMIN` role — before they could reach this code path."
- **Confidence**: settled

### Vulnerability Detail C: Three affected surfaces — server creation, preview endpoints, and rehydrated servers
- **Evidence**: Blog post's enumerated affected surfaces.
- **Quote**: "MCP server creation/update (`NewMCPServerRequest`, `UpdateMCPServerRequest`); `/mcp-rest/test/connection` and `/mcp-rest/test/tools/list` preview endpoints; Servers rehydrated from config or the DB at runtime"
- **Confidence**: settled

### Vulnerability Detail D: The upstream root cause is Anthropic's MCP SDK passing `command` to subprocess without restriction
- **Evidence**: Blog post explicitly names the SDK-level issue.
- **Quote**: "command-injection in Anthropic's MCP SDK's stdio transport (`StdioServerParameters` runs whatever `command` it's handed)"
- **Confidence**: settled
- **Our assessment**: LiteLLM correctly identifies the upstream SDK behavior as the root enabler. However, LiteLLM's fix is ultimately downstream (app-level validation), not an SDK patch. This is a realistic division of responsibility: the gateway layer should validate inputs before forwarding to the SDK, even if the SDK itself is permissive. The LiteLLM patch is defense-in-depth at the application layer, which is exactly where an LLM gateway operator has control.

## Root Cause (if identified)

- **Author's diagnosis**: The `command` field in `StdioServerParameters` was accepted without any validation. The LiteLLM proxy passed the user-supplied command straight through to the MCP SDK's subprocess invocation. No allowlist, no basename check, no validation at any layer from request parsing to runtime instantiation.

- **Our assessment**: Agree. The root cause is a missing-input-validation (CWE-20) at the application layer, combined with the MCP SDK's design which does not constrain which commands it will execute over stdio. The vulnerability is straightforward in mechanism but significant in context: the MCP stdio transport is designed for running local MCP server processes, and the `command` field is inherently executable. An allowlist-based approach is the correct fix because the set of legitimate MCP launcher commands is small and well-defined.

### Root-cause detail: The upstream MCP SDK allows any command
- **Evidence**: Blog post references OX Security's advisory describing the SDK's behavior.
- **Quote**: "StdioServerParameters runs whatever command it's handed"
- **Confidence**: settled

### Root-cause detail: The attack path via preview endpoints was the easiest trigger
- **Evidence**: Blog post's fix section explains the preview endpoint gating rationale.
- **Quote**: "Locked down the preview endpoints. `/mcp-rest/test/connection` and `/mcp-rest/test/tools/list` now require the `PROXY_ADMIN` role. These 'try before you add' endpoints were the easiest way to trigger command execution without persisting anything."
- **Confidence**: settled

## Recovery Path

- **What they switched to**: A four-part defense-in-depth patch in commit `7b7f304` (PR #25343): (1) command allowlist, (2) Pydantic-level validation on request models, (3) runtime re-validation in client instantiation, (4) PROXY_ADMIN role gating on preview endpoints.
- **First release with fix**: `v1.83.6-nightly`
- **First stable release with fix**: `v1.83.7-stable`
- **Action**: Upgrade to `v1.83.7-stable` or later. If tracking nightlies, `>= v1.83.6-nightly`.
- **Post-upgrade audit required**: "If you have stdio MCP servers configured from before the upgrade, any row whose `command` basename isn't in the allowlist will now fail to start. Either update the config to use an allowed launcher (e.g. `npx`, `uvx`, `python`) or add the binary to `LITELLM_MCP_STDIO_EXTRA_COMMANDS`."
- **Role review needed**: "Review who has `PROXY_ADMIN`. The stdio test endpoints are now admin-only. If you'd previously delegated MCP testing to non-admin users, they'll now hit a 403."

### Fix Layer 1: `MCP_STDIO_ALLOWED_COMMANDS` frozenset allowlist
- **Evidence**: Blog post shows the constant definition.
- **Quote**: "A new constant `MCP_STDIO_ALLOWED_COMMANDS` restricts stdio `command` values to a small set of known MCP launchers"
- **Confidence**: settled
- **The allowlist** (verbatim from the code block on the page): `{"npx", "uvx", "python", "python3", "node", "docker", "deno"}`
- **Extensibility**: The blog post states "The list is extensible at deploy time via the `LITELLM_MCP_STDIO_EXTRA_COMMANDS` env var (comma-separated) if you need to allow additional binaries."

### Fix Layer 2: Pydantic-level validation on request models
- **Evidence**: Blog post describes the validation layer.
- **Quote**: "Both `NewMCPServerRequest` and `UpdateMCPServerRequest` now reject configs whose `command` basename is not in the allowlist — so the bad input never makes it past request parsing."
- **Confidence**: settled

### Fix Layer 3: Runtime re-validation in `_create_mcp_client`
- **Evidence**: Blog post describes the defense-in-depth at instantiation time.
- **Quote**: "`_create_mcp_client` re-validates the command when instantiating the stdio client, so any `MCPServer` reconstructed from an older DB row or config file (predating the allowlist) is also blocked at spawn time."
- **Confidence**: settled

### Fix Layer 4: PROXY_ADMIN role required for test endpoints
- **Evidence**: Blog post describes the role gating.
- **Quote**: "`/mcp-rest/test/connection` and `/mcp-rest/test/tools/list` now require the `PROXY_ADMIN` role."
- **Confidence**: settled

### Fix detail: Version table
- **Evidence**: Blog post's version table enumerates patched releases.
- **Quote**: "The patch is present in every LiteLLM release tagged from `v1.83.6-nightly` onward."
- **Versions with the fix** (verbatim from source table):
  - `v1.83.6-nightly` — First release with the fix
  - `v1.83.7.rc.1` — Release candidate
  - `v1.83.7-stable` — Stable
  - `v1.83.8-nightly` — Nightly
  - `v1.83.9-nightly` — Nightly
  - `v1.83.10-nightly` — Nightly

## Concrete Artifacts

**The `MCP_STDIO_ALLOWED_COMMANDS` allowlist constant (verbatim from the blog post's code block):**
```python
MCP_STDIO_ALLOWED_COMMANDS = frozenset(
    {"npx", "uvx", "python", "python3", "node", "docker", "deno"}
)
```

**CVE and advisory references (verbatim from source):**
```
CVE: https://www.ox.security/blog/mcp-supply-chain-advisory-rce-vulnerabilities-across-the-ai-ecosystem/
Commit: https://github.com/BerriAI/litellm/commit/7b7f304675
PR: https://github.com/BerriAI/litellm/pull/25343
```

**Affected surfaces (verbatim from source):**
```
- MCP server creation/update (NewMCPServerRequest, UpdateMCPServerRequest)
- /mcp-rest/test/connection and /mcp-rest/test/tools/list preview endpoints
- Servers rehydrated from config or the DB at runtime
```

**Operator action items (verbatim from source):**
```
- Upgrade. Move to v1.83.7-stable or later. If you track nightlies,
  anything >= v1.83.6-nightly is patched.
- Audit existing MCP servers. If you have stdio MCP servers configured
  from before the upgrade, any row whose command basename isn't in the
  allowlist will now fail to start. Either update the config to use an
  allowed launcher (e.g. npx, uvx, python) or add the binary to
  LITELLM_MCP_STDIO_EXTRA_COMMANDS.
- Review who has PROXY_ADMIN. The stdio test endpoints are now admin-only.
  If you'd previously delegated MCP testing to non-admin users, they'll
  now hit a 403.
```

**Version table (verbatim from source):**
| Version | Type |
|---|---|
| `v1.83.6-nightly` | First release with the fix |
| `v1.83.7.rc.1` | Release candidate |
| `v1.83.7-stable` | Stable |
| `v1.83.8-nightly` | Nightly |
| `v1.83.9-nightly` | Nightly |
| `v1.83.10-nightly` | Nightly |

**OX Security advisory description (verbatim from the blog post's block quote):**
> LiteLLM contains an authenticated remote command execution vulnerability in its MCP server creation functionality. The application allows users to add MCP servers via a JSON configuration specifying arbitrary command and args values. LiteLLM executes these values on the host without validation, enabling attackers to run arbitrary operating system commands.

## Cross-References

- **Corroborates**:
  - `blog-litellm-may-townhall-updates.md` **Claim 2** (89 vulnerabilities patched in 4 weeks, 78 reported by Veria scanner) — the MCP command injection fix was part of this security hardening wave (the CVE was disclosed April 21, and the May townhall reports 89 vulns patched in the subsequent 4 weeks).
  - `blog-litellm-may-townhall-updates.md` **Claim 6** (on-behalf-of MCP OAuth vaults tokens at the proxy) — both this note and that source address MCP security hardening at the proxy layer, though from different angles (this note covers MCP transport-level input validation; the May townhall covers MCP OAuth token delegation).
  - `failure-litellm-proxy-sql-injection-cve-2026-42208.md` **Lesson 1** (auth paths must use parameterized queries) — both this note and that one document CVE-level security vulnerabilities in LiteLLM with the same disclosure pattern (vendor blog post + GHSA), same authors, and similar architectural lessons about input validation at the API gateway. That note covers SQL injection; this one covers command injection — two different injection classes in the same product.
  - `failure-litellm-host-header-auth-bypass.md` — same vendor (LiteLLM), same disclosure pattern, same authors. Both are security advisories with clear fix descriptions. That note covers route-resolution auth bypass; this one covers MCP stdio command injection. Together they establish LiteLLM's security advisory disclosure format and pattern of recurring security engagement.
  - `docs-langfuse-mcp-server.md` **Claim 3** (Windsurf uses `npx mcp-remote` as a local proxy) — the `npx` launcher appears in the Langfuse MCP setup documentation and is also on the LiteLLM allowlist. This confirms `npx` as the lowest-common-denominator MCP launcher command across vendors.
  - `docs-langfuse-mcp-server.md` **Claim 4** (the docs MCP server uses `streamableHttp` with no auth) — the Langfuse docs MCP avoids stdio entirely by using `streamableHttp` (remote HTTP transport), which inherently avoids the stdio command injection surface. This is the alternative deployment pattern: if a gateway supports remote MCP transport, stdio injection risks are moot.

- **Contradicts**: None. No existing source note claims that passing `command` to stdio subprocess without validation is safe, or that allowlists are unnecessary for MCP stdio servers. No contradiction issue filed.

- **Extends / thematically adjacent**:
  - `failure-litellm-proxy-sql-injection-cve-2026-42208.md` — same vendor (LiteLLM), same vulnerability pattern (unvalidated input → OS-level impact through a trusted library), same disclosure format. That note documents how non-parameterized SQL queries in the API key verification path enabled SQL injection. This note documents how unvalidated MCP stdio `command` values enable command injection. Together they establish LiteLLM's input-validation gap as a recurring vulnerability class.
  - `failure-litellm-wildcard-model-access-desync.md` — same vendor (LiteLLM), different failure class (stale in-memory state in access control). That note covers a caching/reload desync affecting wildcard access rules; this note covers input validation in MCP server creation. Both involve LiteLLM's access-control layer, but through completely different mechanisms.
  - `failure-litellm-guardrail-logging-secret-exposure.md` — same vendor (LiteLLM), different failure class (credential leak through observability plumbing). This is the fifth distinct LiteLLM failure pattern in the corpus, covering MCP transport security — an attack surface none of the other LiteLLM failure notes addresses.
  - `failure-litellm-httpx-cache-eviction.md` — same vendor (LiteLLM), different failure class (shared-reference cleanup in caching). That note covers infrastructure reliability, not security; this note covers a CVE-level security vulnerability.
  - `docs-langfuse-security-and-guardrails.md` **Claim 1** (two-pronged Langfuse security: runtime blocking + post-hoc observability) — the LiteLLM MCP stdio fix is an instance of the "runtime blocking" prong (allowlist validation occurs before execution). Observability of which commands were blocked would be the "post-hoc observability" complement, which LiteLLM could implement via its tracing/logging.

- **Novel**: This is the first source note in the corpus covering:
  1. **MCP stdio command injection** (CVE-2026-30623) — a vulnerability class specific to the MCP protocol's stdio transport, where the `command` field is inherently executable content.
  2. **The allowlist pattern for MCP stdio**: `MCP_STDIO_ALLOWED_COMMANDS` as a deploy-time-configurable frozen set — a transferable security control for any LLM gateway implementing MCP stdio.
  3. **The three-layer defense concept**: Pydantic (request parsing) → runtime re-validation (client instantiation) → rehydration protection (DB/config recovery) — a defense-in-depth architecture for MCP gateway input validation.
  4. **PROXY_ADMIN role gating on MCP test endpoints** — the principle that MCP server testing/preview endpoints should be higher-privilege than regular MCP usage.
  5. **The authenticated-scope dimension**: this CVE was authenticated RCE (not unauthenticated), which is an important nuance — the auth boundary prevented remote unauthenticated exploitation, but post-authentication authorization was insufficient (any authenticated user with MCP creation permission, not only admins, could trigger it).

## Guide Impact

- **Chapter 06 (Security and Trust) — MCP Transport Security**: Add a specific security requirement for LLM gateways and proxies that implement MCP stdio transport: "MUST validate the `command` field of MCP stdio server configurations against an allowlist of known MCP launcher binaries (e.g., `npx`, `uvx`, `python`, `python3`, `node`, `docker`, `deno`). The allowlist MUST be enforced at request-parsing time, at runtime client-instantiation time, and when rehydrating server configurations from persistent storage." Reference CVE-2026-30623 as a real-world case study.

- **Chapter 06 (Security and Trust) — Defense-in-depth for MCP input validation**: Add a three-layer defense pattern (derived from this fix): Layer 1 — schema/Pydantic validation on API request models; Layer 2 — runtime re-validation when instantiating MCP clients; Layer 3 — validation on config rehydration from DB or config files. Reference the LiteLLM commit `7b7f304` and PR #25343.

- **Chapter 06 (Security and Trust) — MCP test/preview endpoint authorization**: Recommend that MCP server testing or preview endpoints carry stricter authorization than production MCP usage. The `/mcp-rest/test/*` endpoints are the easiest way to trigger command execution without persisting anything — they should require an admin role. Reference the PROXY_ADMIN gating in this fix.

- **Chapter 06 (Security and Trust) — Auth is not authorization**: Use this CVE to illustrate the principle that authentication (you have a valid API key) does not equal authorization (you should be allowed to create MCP servers). The vulnerability was authenticated RCE — meaning the attacker had valid credentials but was able to perform actions beyond their intended authorization scope. Reference the distinction between "not exploitable by unauthenticated users" (the auth gate) and "any authenticated user with MCP creation permission" (the insufficient authorization gate).

- **Chapter 05 (LLM Ops Reliability) — Extensible allowlist pattern**: Document the `MCP_STDIO_ALLOWED_COMMANDS` + `LITELLM_MCP_STDIO_EXTRA_COMMANDS` pattern as a deploy-time configurability mechanism: a locked-down safe default that operators can extend for site-specific needs without modifying code. The env-var extension point means the default is restrictive but not rigid.

- **Chapter 03 (Infrastructure — LLM Gateway Ops) — Upgrade impact for MCP servers**: Note that security fixes that introduce allowlists can break pre-existing configurations. Operators upgrading LiteLLM (or any MCP gateway) to a version with this fix need to audit their existing MCP server configs and may need to update launcher commands or add custom binaries to the extension allowlist. Reference the post-upgrade audit requirement from this source.

## Extraction Notes

- Primary source read in full: LiteLLM blog post (2026-04-21). All quoted passages copied character-for-character from the rendered HTML page. The code block for `MCP_STDIO_ALLOWED_COMMANDS` was extracted from the syntax-highlighted HTML and reproduced verbatim.
- The OX Security advisory is linked but was not followed as a sub-page — the blog post's block quote of the advisory description was sufficient for this source note's scope. The upstream Anthropic MCP SDK behavior is referenced as context but is not the primary subject.
- No sub-pages beyond the blog post itself were followed. The blog post is self-contained with the version table, code block, and action items all present.
- No contradiction issue filed: verified against all existing source notes. MCP stdio command injection is genuinely uncovered in the corpus. No existing source note makes a claim that would contradict the findings in this note.
- The five existing LiteLLM failure notes cover SQL injection, auth bypass, wildcard desync, guardrail secret exposure, and httpx cache eviction — orthogonal failure surfaces to this MCP stdio command injection vulnerability.
