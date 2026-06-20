---
source_url: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification
source_type: docs
title: "GitHub Agentic Workflows: Copilot SDK Driver Specification (v1.0.2)"
author: GitHub Agentic Workflows team (GitHub Next / Microsoft Research)
date_published: null
date_extracted: 2026-06-06
last_checked: 2026-06-06
status: current
confidence_overall: emerging
issue: "#1083"
---

# GitHub Agentic Workflows: Copilot SDK Driver Specification (v1.0.2)

> A formal W3C-style draft specification (v1.0.2) that defines normative behavior for
> Copilot SDK drivers executing agent sessions — covering standalone-mode environment
> variable contracts, token isolation policy, the mandatory 7-step session lifecycle,
> the permission-checking model with five tool-kind rules and shell rule semantics,
> logging requirements across three compliance levels, and tool-denial guardrail
> thresholds; the first specification-layer source in the corpus to document how the
> execution substrate enforces permission separation at the driver level.

## Source Context

- **Type**: docs (formal specification in the `specs/` section of the GitHub Agentic
  Workflows documentation — distinct from `reference/` (platform configuration syntax)
  and `patterns/` (practitioner patterns). This is the normative technical contract
  for SDK driver implementors; it uses RFC 2119 MUST/SHOULD/MAY language and is
  explicitly marked Draft v1.0.2.)
- **Author credibility**: First-party from GitHub Next / Microsoft Research — the
  same team behind the gh-aw platform. Specification-level claims (MUST/SHOULD
  statements) are authoritative for conforming SDK driver implementations. The spec
  includes formal compliance levels, test IDs, and design goals — markers of an
  intentionally testable specification rather than informal guidance.
- **Scope**: Covers standalone-mode execution contract (required and optional
  environment variables), token isolation policy (what platform secrets drivers MUST
  NOT receive), session lifecycle (7 required steps), the permission-checking model
  (`onPermissionRequest` handler, `allowAllTools`, scoped allowlists, five tool-kind
  rules, shell rule semantics), logging requirements (lifecycle logs, permission denial
  logs), compliance levels (L1/L2/L3), tool-denial guardrail (`GH_AW_MAX_TOOL_DENIALS`),
  and design goals. Does NOT cover: the full gh-aw compilation process (see
  `docs-ghaw-compilation-process.md`), Safe Outputs mechanism (see
  `docs-ghaw-how-they-work.md`), MCP Scripts (see `docs-ghaw-mcp-scripts-specification.md`),
  or the upstream permission configuration in workflow frontmatter (see
  `docs-ghaw-permissions-reference.md`).

## Extracted Claims

### Claim 1: Drivers MUST support standalone mode — an executable entry point that reads all runtime configuration from environment variables, with four required variables forming the minimal harness-to-driver contract

- **Evidence**: Section 4.1 defines standalone mode with an explicit required/optional
  variable table and MUST-level conformance requirements for each. The spec states
  drivers "MUST support **standalone mode** (executable entry point that reads
  configuration from environment variables)" and separately documents MUST-level
  requirements for each required variable.
- **Confidence**: settled (first-party specification with MUST-level requirements;
  specific variable names and behaviors are explicitly enumerated)
- **Quote**: "MUST enforce the following contract" (on the standalone mode environment
  variable table, Section 4.1)
- **Our assessment**: Standalone mode is the gh-aw integration point — the harness
  invokes the driver as a subprocess, passing all session parameters via environment
  variables. The four required variables (GH_AW_PROMPT, COPILOT_SDK_URI,
  COPILOT_CONNECTION_TOKEN, COPILOT_MODEL) form the minimal harness-to-driver
  contract. A driver missing any of these cannot execute. For Ch02 (Harness
  Engineering): document the standalone mode env vars as the harness-driver interface.
  Harness implementations that launch SDK drivers must ensure all four required
  variables are set before spawning the subprocess.

### Claim 2: The token isolation policy PROHIBITS the harness from passing platform authentication secrets into the SDK driver subprocess — COPILOT_CONNECTION_TOKEN is the driver's sole authentication mechanism

- **Evidence**: Section 4.2 (updated in v1.0.2): "The harness MUST NOT propagate
  platform authentication secrets such as `GITHUB_TOKEN`, `COPILOT_GITHUB_TOKEN`,
  or `GH_TOKEN` into the SDK driver subprocess environment." Drivers "SHOULD NOT
  attempt to read `GITHUB_TOKEN`, `COPILOT_GITHUB_TOKEN`, or `GH_TOKEN` from their
  environment" and "MUST NOT treat this as an error condition. The absence of these
  variables is expected and normal."
- **Confidence**: settled (first-party specification; three separate normative
  statements consistently returned across multiple fetches of the source)
- **Quote**: "The harness MUST NOT propagate platform authentication secrets such as
  `GITHUB_TOKEN`, `COPILOT_GITHUB_TOKEN`, or `GH_TOKEN` into the SDK driver
  subprocess environment."
- **Our assessment**: This is a security boundary, not just a convention. The per-run
  `COPILOT_CONNECTION_TOKEN` is scoped and temporary; the platform tokens
  (`GITHUB_TOKEN`, `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`) are long-lived and
  broadly-scoped platform credentials. Prohibiting platform token propagation means
  a compromised or malicious driver cannot use the session to exfiltrate or abuse
  platform credentials. The "absence expected and normal" requirement additionally
  means drivers must not have fallback logic that reaches for platform tokens when
  `COPILOT_CONNECTION_TOKEN` is absent — such fallback would undermine the isolation.
  For Ch03 (Safety): the harness-driver token isolation policy is the driver-level
  implementation of the platform-wide "no write access by default" principle — the
  driver is structurally prevented from using credentials it was never meant to have.

### Claim 3: The session lifecycle has a mandatory 7-step sequence that MUST be executed in order — deviation constitutes a conformance failure

- **Evidence**: Section 3.2 states conforming implementations "MUST execute the
  following sequence": (1) resolve runtime configuration, (2) start SDK client
  connection, (3) create session, (4) register event handlers, (5) send prompt and
  await completion, (6) return success/failure result, (7) perform cleanup.
- **Confidence**: settled (first-party specification; MUST-level requirement; the
  7-step sequence is explicitly enumerated in numbered form)
- **Quote**: "best-effort cleanup of stream/session/client resources" (step 7, Section 3.2)
- **Our assessment**: The ordered lifecycle is a testable conformance requirement, not
  a suggested pattern. Step 4 (register event handlers before step 5 send prompt) is
  architecturally important: handlers must be in place before the first message is
  dispatched to avoid missed events. The "best-effort" qualifier on step 7 acknowledges
  that cleanup may fail (connection already dropped, session already expired) without
  making cleanup failure a conformance defect. For Ch03: document the mandatory
  lifecycle sequence as the standard SDK driver test surface — an L1-compliant
  implementation can be verified by checking that all 7 steps execute in order and
  that non-zero exit codes are correctly returned on failure.

### Claim 4: Drivers MUST always configure an `onPermissionRequest` handler — the handler is the enforcer of the permission-checking model and its absence is a conformance violation

- **Evidence**: The permission checking model (Section 5) states implementations
  "MUST always configure an `onPermissionRequest` handler." Two handler modes:
  when `allowAllTools=true`, the handler "MUST approve all permission requests";
  when a scoped allowlist is present, the handler applies the five-kind evaluation
  rules. When config is absent or empty, the spec requires drivers to "MUST treat
  the session as unrestricted."
- **Confidence**: settled (first-party specification; MUST-level requirement;
  handler requirement is unambiguous with both primary code paths documented)
- **Quote**: "MUST always configure an `onPermissionRequest` handler"
- **Our assessment**: The mandatory handler is the mechanism that translates
  workflow-level tool allowlists into runtime-level permission decisions. Without
  the handler configured, no permission checking occurs — which would either allow
  all tools (unsafe) or block all tools (non-functional). For Ch04 (Tooling &
  Safety): document `onPermissionRequest` as the required driver extension point
  for permission enforcement. Any driver implementation that omits this handler
  is non-conformant at L2 and above.

### Claim 5: The permission-checking model defines MUST-level approval rules for five tool kinds — read, write, url, custom-tool, and mcp — with read as the only explicitly default-denied kind

- **Evidence**: Section 5 defines the scoped allowlist evaluation rules:
  - `read`: "MUST be denied unless `allowedTools` contains `read`"
  - `write`: "MUST be approved only when `allowedTools` contains `write`"
  - `url`: "MUST be approved only when `allowedTools` includes `web_fetch`"
  - `custom-tool`: "MUST be approved only when `allowedTools` contains the request tool name"
  - `mcp`: approved when allowedTools contains `<serverName>` OR `<serverName>(<toolName>)`
  - unknown kinds: "Unknown kinds MUST be rejected"
- **Confidence**: settled (first-party specification; MUST-level rules for each
  kind are explicitly enumerated and confirmed across multiple fetch passes)
- **Quote**: "MUST be denied unless `allowedTools` contains `read`"
- **Our assessment**: The five-kind model creates an explicit, auditable permission
  surface. Every tool invocation has a named kind, and each kind has a deterministic
  approval rule. The `read` kind being "default denied" reflects the platform-wide
  "no read access by default" principle — even reading filesystem/repository content
  requires explicit allowlisting. The `mcp` kind's two-format allowlist
  (`<serverName>` for all tools on a server, `<serverName>(<toolName>)` for a
  single tool) enables fine-grained MCP server permission scoping. "Unknown kinds
  MUST be rejected" enforces a fail-closed security posture for future or novel
  tool types. For Ch05 (MCP & Integrations): the `<serverName>(<toolName>)` syntax
  is the recommended pattern for least-privilege MCP access — grant only the
  specific MCP tool needed, not the entire server.

### Claim 6: Shell permission rules follow three distinct matching semantics — prefix matching for `:*` rules, identifier matching for space-free rules, and exact full-command matching for rules with spaces

- **Evidence**: Section 5.4 shell rule semantics: "Rules ending with `:*` MUST
  perform prefix matching against command identifiers. Rules without spaces SHOULD
  be treated as identifier matches. Rules containing spaces MUST be treated as
  exact full-command matches."
- **Confidence**: settled (first-party specification; matching semantics are
  MUST/SHOULD-level with explicit rule syntax; confirmed verbatim across multiple
  fetches)
- **Quote**: "Rules ending with `:*` MUST perform prefix matching against command
  identifiers. Rules without spaces SHOULD be treated as identifier matches. Rules
  containing spaces MUST be treated as exact full-command matches."
- **Our assessment**: The three-tier shell rule syntax provides a hierarchy of
  specificity: prefix rules (e.g., `git:*` matching any git subcommand), identifier
  rules (e.g., `npm` matching the npm command), and exact-command rules (e.g.,
  `npm install --save-dev` matching only that specific invocation). The MUST on
  prefix and exact-command rules vs. SHOULD on identifier rules may signal that
  identifier matching has edge cases. For Ch03 (Safety): document the `:*` prefix
  syntax as the preferred pattern for tool families (e.g., `git:*` for all git
  operations) — it avoids maintaining a long list of exact commands while still
  enforcing a category-level boundary.

### Claim 7: The tool-denial guardrail uses `GH_AW_MAX_TOOL_DENIALS` (default 5) — drivers SHOULD count denials and MUST stop inference when the threshold is reached

- **Evidence**: "GH_AW_MAX_TOOL_DENIALS controls the catastrophic tool-denials
  guardrail in SDK mode. A conforming driver implementation SHOULD count repeated
  tool refusals (permission denials), and MUST stop inference once the configured
  threshold is reached." Default is 5.
- **Confidence**: settled (first-party specification; MUST-level stop-on-threshold
  requirement confirmed across multiple fetch passes)
- **Quote**: "GH_AW_MAX_TOOL_DENIALS controls the catastrophic tool-denials guardrail
  in SDK mode. A conforming driver implementation SHOULD count repeated tool refusals
  (permission denials), and MUST stop inference once the configured threshold is
  reached."
- **Our assessment**: The guardrail addresses a failure mode where the AI engine
  repeatedly requests a denied tool in a retry loop, consuming tokens without
  progress. Stopping inference at 5 denials caps the waste and surfaces the failure
  explicitly (non-zero exit). The SHOULD on counting (vs. MUST) leaves room for
  implementations that track denials at a coarser granularity. For Ch02: document
  `GH_AW_MAX_TOOL_DENIALS` as a configurable safety knob — workflows where repeated
  denials indicate a configuration error may need a lower threshold; supervised
  development workflows may need a higher threshold to observe denial patterns before
  tightening.

### Claim 8: Logging requirements are tiered across three compliance levels — L1 for basic execution, L2 for permission diagnostics, L3 for full lifecycle event serialization

- **Evidence**: Section 2.3 compliance levels: L1 (required): environment variables,
  session startup, prompt dispatch, exit behavior; L2 (standard): permission checking
  and denial diagnostics; L3 (complete): full lifecycle logging and event
  serialization. Section 6 logging requirements include lifecycle logs (connection
  attempt, client start, session creation with session identifier, prompt dispatch,
  completion summary including output presence and duration, runtime error summary on
  failure) and permission denial logs (denial entry with compact request summary,
  secondary logger diagnostics when configured).
- **Confidence**: settled (first-party specification; compliance levels and log
  categories are explicitly defined with section references)
- **Quote**: (no single direct quote covers all three levels; see Concrete Artifacts
  for the full compliance level definitions)
- **Our assessment**: The three-tier compliance model is a practical maturity ladder:
  a minimal driver hits L1 (can execute sessions), a production driver hits L2
  (permission decisions are observable for debugging and audit), and a
  full-observability driver hits L3 (complete event stream for replay and forensics).
  For Ch08 (Observability): the L2 denial logging requirement is the minimum for
  meaningful observability of permission-based failures. A driver logging only at L1
  provides no visibility into why tool requests are being denied — a critical gap for
  debugging misconfigured workflows. Recommend L2 as the baseline for any production
  deployment.

### Claim 9: Optional environment variables let operators tune timeout, log level, and tool-denial threshold — with MUST-level fallback requirements that ensure predictable behavior when values are invalid

- **Evidence**: Section 4.1 documents optional variables:
  - `COPILOT_SDK_SEND_TIMEOUT_MS`: default 600000ms; "MUST apply the default value
    when unset, non-numeric, or non-positive"
  - `GH_AW_MAX_TOOL_DENIALS`: default 5 (covered in Claim 7)
  - `COPILOT_SDK_LOG_LEVEL`: valid values none/error/warning/info/debug/all;
    "MUST fall back to `warning`" on invalid input
  - `GITHUB_WORKSPACE`: "SHOULD be used when present"
- **Confidence**: settled (first-party specification; MUST-level fallback requirements
  are explicitly stated for each optional variable)
- **Quote**: "MUST apply the default value when unset, non-numeric, or non-positive"
  (COPILOT_SDK_SEND_TIMEOUT_MS, Section 4.1)
- **Our assessment**: The MUST-level fallback requirements mean optional variables are
  "safe by default" — a misconfigured value (e.g., `COPILOT_SDK_LOG_LEVEL=verbose`
  which is not in the valid set) falls back to a known safe default rather than
  causing a driver crash or silent undefined behavior. The 600-second (10-minute)
  default timeout is generous for most prompt workflows. For Ch02: document these
  variables as tuning knobs with their defaults; the MUST-level fallbacks mean
  practitioners can rely on predictable behavior even when these variables are unset.

### Claim 10: The design goals articulate four architectural properties that distinguish SDK drivers from informal implementations — language-agnostic behavior, testable permissions, audit-friendly logs, and fail-fast configuration

- **Evidence**: Section 1.3 design goals state a conforming implementation must:
  "Remain language agnostic in externally visible behavior"; "Provide explicit and
  testable permission decisions"; "Produce consistent, audit-friendly logs for
  runtime and policy events"; "Fail fast on missing required configuration in
  standalone mode."
- **Confidence**: settled (first-party specification; design goals are explicitly
  stated and directly correspond to the testable compliance requirements in the
  spec body)
- **Quote**: "Provide explicit and testable permission decisions"
- **Our assessment**: The four design goals map to concrete requirements: language-
  agnostic behavior is enforced by the MUST-level environment-variable contract
  (any language can read env vars); testable permissions are enforced by the five-kind
  MUST rules and compliance tests T-CSD-101 through T-CSD-111; audit-friendly logs
  are the L2/L3 logging requirements; fail-fast on missing config is the "MUST fail
  fast when unset" requirement for `COPILOT_MODEL` and the "MUST exist and be
  readable" requirement for `GH_AW_PROMPT`. For Ch02: these goals function as a
  checklist for evaluating whether a custom driver implementation is production-ready
  — not as aspirational principles, but as testable criteria with corresponding
  compliance tests.

## Concrete Artifacts

### Required Environment Variables (Section 4.1)

```
Variable                  | Required | Conformance Requirement
--------------------------|----------|---------------------------------------------
GH_AW_PROMPT              | Yes      | Path to prompt file; MUST exist and be readable
COPILOT_SDK_URI           | Yes      | SDK endpoint URI; MUST be non-empty
COPILOT_CONNECTION_TOKEN  | Yes      | Per-run shared token generated by the harness
                          |          |   in SDK mode; MUST be non-empty
COPILOT_MODEL             | Yes      | Model to use (e.g. gpt-4o, claude-sonnet-4);
                          |          |   MUST be non-empty; MUST fail fast when unset
```

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 4.1*

### Optional Environment Variables (Section 4.1)

```
Variable                    | Default  | Conformance Requirement
----------------------------|----------|---------------------------------------------
COPILOT_SDK_SEND_TIMEOUT_MS | 600000   | MUST apply default when unset, non-numeric,
                            |          |   or non-positive (10-minute default)
GH_AW_MAX_TOOL_DENIALS      | 5        | Tool-denial guardrail; driver MUST stop
                            |          |   inference when threshold is reached
COPILOT_SDK_LOG_LEVEL       | warning  | Valid: none/error/warning/info/debug/all;
                            |          |   MUST fall back to warning on invalid value
GITHUB_WORKSPACE            | (unset)  | SHOULD be used when present
```

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 4.1*

### Session Lifecycle — 7-Step Mandatory Sequence (Section 3.2)

```
Conforming implementations MUST execute the following sequence:

1. Resolve runtime configuration
2. Start SDK client connection
3. Create a session
4. Register event handlers
5. Send prompt and await completion
6. Return success/failure result
7. Perform best-effort cleanup of stream/session/client resources
```

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 3.2*

### Permission Checking Model — Tool-Kind Rules (Section 5)

```
Kind         | Approval Rule (MUST-level)
-------------|---------------------------------------------------------------
read         | MUST be denied unless allowedTools contains "read"
write        | MUST be approved only when allowedTools contains "write"
url          | MUST be approved only when allowedTools includes "web_fetch"
custom-tool  | MUST be approved only when allowedTools contains the
             |   request tool name
mcp          | MUST be approved when allowedTools contains <serverName>
             |   OR <serverName>(<toolName>)
shell        | Approved via "shell", "shell(<rule>)", or per shell rule
             |   semantics (Section 5.4)
unknown      | MUST be rejected

Special case: allowAllTools=true → MUST approve all permission requests
Special case: config absent/empty → MUST treat session as unrestricted
```

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 5*

### Shell Rule Semantics (Section 5.4)

```
Rule format         | Matching behavior                              | Level
--------------------|------------------------------------------------|-------
<cmd>:*             | Prefix matching against command identifiers    | MUST
<cmd>               | Identifier match (no spaces in rule)           | SHOULD
"<cmd> arg1 arg2"   | Exact full-command match (rule contains spaces) | MUST
```

*Verbatim from source: "Rules ending with :* MUST perform prefix matching against
command identifiers. Rules without spaces SHOULD be treated as identifier matches.
Rules containing spaces MUST be treated as exact full-command matches."*

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 5.4*

### Compliance Levels and Test IDs (Section 2.3)

```
Level 1 (Required):  Environment variables, session startup, prompt dispatch,
                     exit behavior
Level 2 (Standard):  Permission checking and denial diagnostics
Level 3 (Complete):  Full lifecycle logging and event serialization

Test suite:
  T-CSD-001 – T-CSD-008:  Configuration tests (8 tests)
  T-CSD-101 – T-CSD-111:  Permission tests (11 tests)
  T-CSD-201 – T-CSD-202:  Logging tests (2 tests)
```

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 2.3*
*Note: one fetch returned 11 configuration tests; another returned 8 with explicit IDs T-CSD-001–008.
The count with explicit IDs is used here — verify against live source.*

### Required Lifecycle Logs (Section 6.2)

```
Log entry              | Description
-----------------------|---------------------------------------------
Connection attempt     | Logged before starting SDK client
Client confirmation    | Logged after successful client start
Session creation       | Logged with session identifier
Prompt dispatch        | Logged at prompt send start
Completion summary     | Includes output presence and duration
Error summary          | Logged on runtime failure before exit
```

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 6.2*

### Design Goals (Section 1.3)

```
A conforming implementation MUST:
1. Remain language agnostic in externally visible behavior
2. Provide explicit and testable permission decisions
3. Produce consistent, audit-friendly logs for runtime and policy events
4. Fail fast on missing required configuration in standalone mode
```

*Source: https://github.github.com/gh-aw/specs/copilot-sdk-driver-specification — Section 1.3*

## Cross-References

- **Corroborates**:
  - `docs-ghaw-how-they-work.md` Claim 3 (five-layer defense-in-depth security
    pipeline: compilation-time validation → runtime isolation → permission separation
    → network controls → output sanitization): This spec is the driver-level
    implementation of Layer 3 (permission separation). The permission-checking model
    with its five MUST-level tool-kind rules and mandatory `onPermissionRequest`
    handler is the runtime mechanism by which permission separation is enforced at the
    driver level, downstream of the workflow-level configuration.
  - `docs-ghaw-how-they-work.md` Claim 4 ("Workflows run with minimal permissions
    (no write access by default), use tool allowlists"): The `read` kind being
    "MUST be denied unless `allowedTools` contains `read`" in the permission checking
    model (Claim 5 here) is the driver-level enforcement of the platform-wide
    zero-capability-by-default principle. Both notes agree that read access requires
    explicit permission — this spec shows how that principle is enforced at the
    driver's permission handler level.
  - `docs-ghaw-permissions-reference.md` Claim 1 ("GitHub Agentic Workflows uses
    read-only permissions by default for security, with write operations handled
    through safe outputs"): The `permissions:` frontmatter section (workflow level)
    and the driver's `read: MUST be denied unless allowedTools contains read`
    (driver level) are complementary enforcement layers for the same principle.
    The permissions reference documents the harness-configuration side; this spec
    documents the driver-runtime enforcement side.

- **Extends**:
  - `docs-ghaw-mcp-scripts-specification.md` Claim 1 (inline MCP tool definitions
    in workflow frontmatter): The SDK driver's `mcp` tool-kind rule (with
    `<serverName>(<toolName>)` syntax for fine-grained access) is the driver-level
    mechanism by which MCP server permissions are enforced at runtime. Where
    `docs-ghaw-mcp-scripts-specification.md` documents the MCP Script authoring model
    and inline tool definitions, this spec documents how the driver gate-keeps MCP
    tool invocations via the permission handler.
  - `docs-ghaw-staged-mode-reference.md` (staged execution configuration): That
    note documents the harness-side configuration for how outputs are staged. This
    spec documents the driver-side runtime model (session lifecycle, permission
    checking) that executes within the same agent session that staged mode governs.
    The two together cover the full execution pipeline: the harness configures output
    staging; the driver manages the execution session.

- **Contradicts**: None identified. The token isolation policy (driver MUST NOT receive
  platform tokens) is consistent with and extends the permissions model in
  `docs-ghaw-permissions-reference.md`. The session lifecycle and permission model
  complement rather than contradict existing corpus sources. No existing note documents
  the `onPermissionRequest` handler, the five-kind rules, or the shell rule semantics —
  this is additive, not contradictory.

- **Novel**:
  - **Formal standalone mode env-var contract** (Claim 1): The specific four required
    variables (GH_AW_PROMPT, COPILOT_SDK_URI, COPILOT_CONNECTION_TOKEN, COPILOT_MODEL)
    with MUST-level requirements are not documented in any existing corpus source note.
  - **Token isolation policy — harness MUST NOT propagate platform tokens** (Claim 2):
    The prohibition on harness-to-driver platform token propagation (`GITHUB_TOKEN`,
    `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`) is entirely new to the corpus. No existing
    note documents this security boundary at the subprocess environment level.
  - **7-step mandatory session lifecycle** (Claim 3): The specific ordered sequence
    (resolve config → start client → create session → register handlers → send prompt
    → return result → cleanup) is new. Existing notes mention sessions conceptually
    but none documents the mandatory lifecycle sequence.
  - **`onPermissionRequest` handler as a required SDK extension point** (Claim 4):
    The requirement for drivers to always configure this handler is new to the corpus.
  - **Five tool-kind permission rules with MUST-level approval logic** (Claim 5):
    The named kinds (read/write/url/custom-tool/mcp/shell) and their deterministic
    approval rules are new to the corpus. The `mcp` kind's `<serverName>(<toolName>)`
    fine-grained syntax is new.
  - **Shell rule syntax and matching semantics** (Claim 6): The three-tier shell rule
    matching (`:*` prefix / identifier / exact-command) is new to the corpus.
  - **Tool-denial guardrail `GH_AW_MAX_TOOL_DENIALS`** (Claim 7): The specific
    guardrail mechanism (count denials, MUST stop at threshold, default 5) is new.
  - **Three-tier compliance level model with test IDs** (Claim 8): L1/L2/L3
    compliance levels with T-CSD-* test identifiers are new to the corpus.
  - **MUST-level fallback for invalid optional variables** (Claim 9): The fallback-
    to-default requirement when optional variables are invalid or non-numeric is a
    subtle safety property not documented in any other source.

## Guide Impact

### Chapter 02: Harness Engineering

- **Document the standalone mode env-var contract as the harness-driver interface**
  (Claim 1): Ch02 should treat the four required variables (GH_AW_PROMPT,
  COPILOT_SDK_URI, COPILOT_CONNECTION_TOKEN, COPILOT_MODEL) as the standard
  harness-driver interface specification. Any harness that spawns SDK drivers must
  configure all four before subprocess invocation. Add a reference table from the
  Concrete Artifacts section.

- **Add the four optional tuning variables with their defaults** (Claim 9): Document
  `COPILOT_SDK_SEND_TIMEOUT_MS` (10-min default), `GH_AW_MAX_TOOL_DENIALS` (5 default),
  `COPILOT_SDK_LOG_LEVEL`, and `GITHUB_WORKSPACE` as operator-adjustable knobs. The
  MUST-level fallback behavior means practitioners can omit these without destabilizing
  the driver — but note that the defaults may be too permissive for production
  workflows.

- **Add the 7-step session lifecycle as a driver evaluation checklist** (Claim 3):
  Practitioners building or evaluating custom SDK drivers can use the 7-step sequence
  as a structural test. The L1 compliance tests T-CSD-001–008 are the formal test suite.

- **Document `GH_AW_MAX_TOOL_DENIALS` as a configurable safety knob** (Claim 7):
  Workflows where repeated denials indicate a configuration error may need a lower
  threshold than the default 5. Document the trade-off between sensitivity (low
  threshold) and investigation overhead (high threshold).

### Chapter 03: Safety and Verification

- **Add token isolation policy as a harness security requirement** (Claim 2): Ch03
  should name the token isolation boundary explicitly: harness code MUST NOT pass
  `GITHUB_TOKEN`, `COPILOT_GITHUB_TOKEN`, or `GH_TOKEN` into the SDK driver subprocess
  environment. This is a concrete, actionable rule that any harness engineer can
  verify by inspecting subprocess launch code.

- **Add the permission checking model** (Claims 4, 5, 6): The mandatory
  `onPermissionRequest` handler, the five tool-kind rules, and the shell rule semantics
  are the driver-level security mechanism. Ch03 should document:
  - `read` as the most restricted kind (denied unless explicitly listed in `allowedTools`)
  - The `<serverName>(<toolName>)` pattern for least-privilege MCP access
  - Shell prefix rules (`:*` suffix) as the idiomatic way to allow tool families
    without listing every exact command
  - "Unknown kinds MUST be rejected" as a fail-closed security posture

- **Add the tool-denial guardrail** (Claim 7): `GH_AW_MAX_TOOL_DENIALS` is a safety
  valve for infinite denial loops. Ch03 should recommend configuring this variable
  explicitly rather than relying on the default 5, particularly for workflows where a
  denial indicates a misconfiguration that should fail fast.

### Chapter 05: MCP and Integrations

- **Document the `mcp` kind permission rule and `<serverName>(<toolName>)` syntax**
  (Claim 5): The two-format allowlist (`<serverName>` for all tools on a server,
  `<serverName>(<toolName>)` for a single tool) is the mechanism for fine-grained MCP
  permission scoping. Ch05 should recommend `<serverName>(<toolName>)` as the default
  pattern — grant the minimum MCP surface needed, not the entire server.

### Chapter 08: Observability

- **Add the three-tier compliance model and logging requirements** (Claim 8): Ch08
  should recommend L2 as the minimum production baseline — L2 is where permission
  denial logging becomes available, which is required for meaningful observability of
  why agent actions are being blocked. Document the six required lifecycle log events
  and the two denial log categories as the observable output of a conformant driver.
  Reference T-CSD-201/T-CSD-202 as the logging validation tests.

## Extraction Notes

1. **Version is v1.0.2 Draft**: The spec is explicitly marked as a draft. The token
   isolation policy (Section 4.2) was specifically updated in v1.0.2 according to the
   source. MUST/SHOULD requirements are authoritative for conforming implementations
   but may change before a final release.

2. **WebFetch returns AI-summarized content**: The gh-aw docs site is a single-page
   application. Two targeted fetches were used to confirm key quotes. All quotes are
   used only when consistent across both fetch passes. Claims with no reliable verbatim
   passage are marked "(no direct quote; see paraphrase in Our assessment)" per
   MINER.md §2a.

3. **Configuration test count discrepancy**: Fetch 1 reported 11 configuration tests;
   fetch 2 reported 8 tests (T-CSD-001 through T-CSD-008). The Concrete Artifacts
   section uses the more specific result from the second fetch, which included test IDs.
   The Assayer should verify the actual count against the live source.

4. **TypeScript example referenced but not extracted**: The spec includes a working
   TypeScript example demonstrating SDK client initialization with the
   `@github/copilot-sdk` package. The WebFetch model described it but did not return
   the full code verbatim. The example was not included in Concrete Artifacts to avoid
   fabricating code — the source should be consulted directly for the code artifact.

5. **No publication date**: The documentation does not carry an explicit publication
   date. `date_published` is left null. Version 1.0.2 Draft is the stated version.

6. **No contradictions filed**: Reviewed all existing source notes. No claims in this
   spec materially oppose any existing note at the MINER.md §4a filing threshold. The
   token isolation policy (driver MUST NOT receive platform tokens) is consistent with
   and extends the permissions reference and how-they-work notes.
