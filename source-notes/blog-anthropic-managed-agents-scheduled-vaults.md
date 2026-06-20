---
source_url: https://claude.com/blog/whats-new-in-claude-managed-agents
source_type: blog-post
title: "New in Claude Managed Agents: run agents on a schedule and store environment variables in vaults"
author: Anthropic (product announcement)
date_published: 2026-06-09
date_extracted: 2026-06-10
last_checked: 2026-06-10
status: current
confidence_overall: anecdotal
issue: "#1134"
---

# New in Claude Managed Agents: run agents on a schedule and store environment variables in vaults

> June 9, 2026 Anthropic product announcement introducing two new Claude Managed Agents features — scheduled deployments (agents running on cron-style schedules without external scheduler infrastructure) and environment variables in vaults (CLI-based credential injection enabling agents to authenticate with external tools without credentials entering the sandbox) — both now in public beta, corroborated by seven named customer implementations.

## Source Context

- **Type**: blog-post (official Anthropic product announcement, claude.com blog, June 9, 2026; incremental feature update to Claude Managed Agents, which launched April 8, 2026 — see blog-anthropic-claude-managed-agents.md)
- **Author credibility**: First-party Anthropic announcement — authoritative on what the platform provides and which access tier features occupy. Seven named customer quotes from individuals with titles, though the quotes are brief and provide limited technical depth. The Prospector's triage identified five customers; the actual post includes seven (Rakuten, Actively AI, Ando, Notion, Browserbase, KERNEL, Milana). No performance benchmarks appear in this post — unlike the April and May announcements, this one is entirely testimonial-based.
- **Scope**: Covers two new features: (1) scheduled deployments — agents running on a recurring schedule with pause/resume and on-demand triggering; (2) environment variables in vaults — credential injection for CLI-based tool integration. Does NOT cover: changes to existing features (outcomes, dreaming, multiagent, memory, MCP tunnels, self-hosted sandboxes), API or SDK details, pricing updates, or technical architecture of how scheduling is implemented internally.

## Extracted Claims

### Claim 1: Claude Managed Agents now supports scheduled deployments — agents that run on a cron-style schedule and complete routine work automatically without human-triggered initiation

- **Evidence**: First-party feature description. The opening statement is explicit: "Starting today, Claude Managed Agents can run on a schedule and securely access CLI tools and other authenticated services." Three customer testimonials specifically validate scheduled deployments (Rakuten, Actively AI, Ando).
- **Confidence**: emerging (vendor feature description; three named customer corroborations at time of launch; public beta means broadly accessible but not GA)
- **Quote**: "Agents can now run on a schedule, completing routine work automatically."
- **Our assessment**: Scheduled deployments are the Managed Agents platform layer's answer to the scheduling problem that Claude Code Routines (blog-anthropic-claude-code-routines.md) addresses at the Claude Code CLI layer. The distinction matters: Routines schedule Claude Code sessions (research preview, April 2026); Managed Agents scheduled deployments schedule Managed Agent sessions (public beta, June 2026). They operate at different abstraction levels and serve different audiences — developers building with the Claude Code CLI vs. developers building with the Managed Agents platform API. The Actively AI testimonial ("We replaced the scheduling infrastructure we'd built ourselves with scheduled deployments") is the most significant claim in the post: it confirms a team that had built their own scheduler found the managed option sufficient to replace it. This is the same category of evidence as the April 8 announcement's "weeks instead of months" testimonials — teams reaching for the managed service rather than maintaining DIY infrastructure.

### Claim 2: Scheduled deployments support cron-style recurring schedules (nightly data sync, weekly compliance scan, daily digest) and can be paused, resumed, or triggered on demand

- **Evidence**: First-party feature description with three explicit use case examples named in the announcement.
- **Confidence**: settled (explicit feature description from first-party source with named trigger patterns and named operational controls)
- **Quote**: "Use it for recurring work like a nightly data sync, a weekly compliance scan, or a daily digest."
- **Our assessment**: The three named patterns (nightly/weekly/daily) match the cadences documented in blog-anthropic-claude-code-routines.md (Claim 3: "hourly, nightly, weekly"). The pause/resume and on-demand triggering capabilities make the scheduling model more operationally flexible than pure cron: practitioners can halt a scheduled agent temporarily (e.g., during a deployment freeze) or trigger an additional run (e.g., a compliance scan ahead of an audit) without modifying the schedule configuration. This operational flexibility is not present in simple cron-based scheduling.

### Claim 3: Actively AI replaced their self-built scheduling infrastructure with Managed Agents scheduled deployments

- **Evidence**: Named customer testimonial from Mihir Garimella, Co-founder, Actively AI.
- **Confidence**: anecdotal (single customer report; no technical details about what was replaced or the migration scope)
- **Quote**: "We replaced the scheduling infrastructure we'd built ourselves with scheduled deployments."
- **Our assessment**: This is structurally the most significant customer claim in the post because it confirms a replacement-not-supplement pattern: Actively AI had built scheduling infrastructure themselves and then removed it in favor of the managed service. In the April 8 announcement context (blog-anthropic-claude-managed-agents.md Claim 8), the "weeks instead of months" testimonials showed teams adopting the managed service instead of building from scratch; this June testimonial shows a team that had already built their own infrastructure deciding the managed option is better. This strengthens the build-vs-buy case for scheduling specifically, not just agent infrastructure generally.

### Claim 4: Environment variables in vaults enable agents to authenticate with CLI tools by injecting credentials from a secure vault rather than exposing them in the sandbox

- **Evidence**: First-party feature description with an explicit security guarantee about the agent-sandbox boundary.
- **Confidence**: settled (explicit feature description from first-party source; the mechanism aligns precisely with the credential security design documented in blog-anthropic-scaling-managed-agents.md Claim 7)
- **Quote**: "The agent never sees your key because the sandbox only holds a placeholder."
- **Our assessment**: The "sandbox only holds a placeholder" statement is the key security claim. The mechanism extends the vault+proxy credential pattern documented in blog-anthropic-scaling-managed-agents.md (Claim 7) into a first-class platform feature for CLI authentication specifically. Prior vault documentation described OAuth tokens and API keys via MCP proxies; this announcement explicitly targets CLI tool authentication — a distinct and common category of enterprise tooling. The security guarantee is the same architectural invariant (credentials never in sandbox) but the delivery mechanism is adapted for CLI execution contexts.

### Claim 5: CLIs are positioned as a fast, lightweight integration path for agents, enabling access to any service that provides a command-line interface

- **Evidence**: First-party feature framing with explicit positioning statement; four customer examples validate the pattern.
- **Confidence**: emerging (vendor positioning claim; the "fast, lightweight" characterization is relative to alternatives such as custom MCP servers or direct API integrations; customer examples validate the pattern is working in production)
- **Quote**: "CLIs let agents drive existing command-line tools directly through a shell, making them a fast, lightweight integration path."
- **Our assessment**: This claim frames CLIs as an alternative to MCP servers for service integration. Where blog-anthropic-mcp-production-agents.md recommends building remote MCP servers for production agent integrations, this announcement positions CLI integration (via environment variable vaults) as a lower-friction path for services that already have CLIs. The trade-off is implicit: CLIs are faster to integrate (no MCP server to build or host) but potentially less structured than MCP (command output is text, not typed tool responses). For services like Notion, Browserbase, or internal tools with existing CLIs, the vault integration pattern avoids building new MCP infrastructure. This is a meaningful complement (not replacement) to MCP-based integration.

### Claim 6: Notion uses environment variable vaults to deploy the Notion CLI to agents while meeting enterprise security team requirements

- **Evidence**: Named customer testimonial from Quan Nguyen, Public API Lead, Notion.
- **Confidence**: anecdotal (single customer; no technical detail on the security review process or CLI deployment architecture)
- **Quote**: "Environment variables in vaults let us securely roll out the Notion CLI, meeting our security team's strict guidelines."
- **Our assessment**: Notion as a customer is particularly significant because Notion also appeared in the April 8 launch announcement (blog-anthropic-claude-managed-agents.md — Eric Liu, Product Manager, cited long-running sessions). This June quote from a different Notion person (Quan Nguyen, Public API Lead) suggests broader adoption across teams within Notion: the platform/API team is deploying the Notion CLI as an agent integration in addition to the session management the product team uses. The "strict guidelines" qualifier confirms that enterprise security review is a real gate for this category of integration — the vault mechanism is specifically what allows the CLI deployment to pass that review.

### Claim 7: Browserbase uses environment variable vaults to combine browser automation with agent execution, generating their public catalog of browser skills

- **Evidence**: Named customer testimonial from Ziray Hao, Product Lead, Browserbase.
- **Confidence**: anecdotal (single customer; no metrics or timeline for the skill catalog)
- **Quote**: "Environment variables in vaults enabled our engineering team to combine two major compute primitives: the agent and the browser."
- **Our assessment**: Browserbase provides the browse CLI that other teams use as a tool within agents. The "combine two major compute primitives" framing suggests Browserbase is using Managed Agents to build and evaluate browser agent capabilities from the inside — running Claude agents that drive their own browser infrastructure. This is a recursive pattern: a browser-infrastructure provider using agent infrastructure to develop browser skills for other agents. The implication for the corpus is significant: browser automation as a tool for agents is now both supported (via Managed Agents' CLIs+vaults) and being actively developed by a specialist provider who uses the same platform.

### Claim 8: KERNEL uses environment variable vaults to give agents direct database access for usage monitoring and customer conversation tracking

- **Evidence**: Named customer testimonial from Catherine Jue, Co-founder & CEO, KERNEL.
- **Confidence**: anecdotal (single customer; no detail on database type, query patterns, or access frequency)
- **Quote**: "Our agent now connects directly to the databases where we track usage and customer conversations."
- **Our assessment**: This use case (database access via CLI authentication) validates the vault mechanism for a data-access pattern distinct from API or browser integration. The "directly to databases" claim implies a CLI-based database client (e.g., psql, a cloud database CLI, or a custom wrapper) authenticated via vault credentials. This pattern addresses the monitoring and analytics use case where an agent needs to query operational databases without storing database credentials in the agent's execution environment. The combination of agent + vault credentials + database CLI is a complete pattern for database-read workflows.

### Claim 9: Milana uses environment variable vaults to invoke private APIs through a CLI without exposing credentials

- **Evidence**: Named customer testimonial from Raghav Sethi, Co-founder & CTO, Milana.
- **Confidence**: anecdotal (single customer; "private APIs" is generic — no detail on API type or authentication mechanism)
- **Quote**: "Environment variables in vaults let our agent invoke private APIs through a CLI without exposing credentials."
- **Our assessment**: The "private APIs through a CLI" pattern is the most generic of the vault use cases in this announcement: it suggests a custom CLI wrapper around private API calls, with the CLI's credentials stored in the vault. This pattern extends vault credential injection beyond public services (Notion CLI, Browserbase browse CLI) to arbitrary private APIs. Any service that can be wrapped in a CLI becomes a potential vault-based agent integration. The "without exposing credentials" emphasis (echoing the security framing from the platform description) confirms that credential exposure is the primary concern being addressed, not just CLI integration convenience.

### Claim 10: Both scheduled deployments and environment variables in vaults are in public beta on the Claude Platform as of June 9, 2026

- **Evidence**: Explicit availability statement from the announcement.
- **Confidence**: settled (explicit announcement; public beta is a formal Anthropic access tier)
- **Quote**: "Both features are now available in public beta on the Claude Platform."
- **Our assessment**: Public beta means broadly accessible without a separate access request, unlike research preview (which requires separate approval for dreaming and MCP tunnels). This is a meaningful access tier: practitioners can evaluate and deploy these features immediately. The public beta designation also means the features are subject to change before GA.

## Concrete Artifacts

### Feature Capability Matrix — Claude Managed Agents as of June 9, 2026

```
Claude Managed Agents — Feature Status (as of 2026-06-09):

NEW (this announcement — public beta):
  Scheduled deployments:           public beta
  Environment variables in vaults: public beta

PREVIOUSLY ANNOUNCED (status unchanged):
  Dreaming:                        research preview (since May 6, 2026)
  Webhooks:                        available (since May 6, 2026)
  Outcomes:                        public beta (since May 6, 2026)
  Multiagent orchestration:        public beta (since May 6, 2026)
  Memory:                          public beta (since April 23, 2026)
  Self-hosted sandboxes:           public beta (since May 19, 2026)
  MCP tunnels:                     research preview (since May 19, 2026)

GA SINCE LAUNCH (April 8, 2026, unchanged):
  Prompt-and-response mode
  Long-running sessions
  Sandboxed code execution
  Session tracing / Claude Console
  Scoped permissions
  Pricing: $0.08/session-hour

Source: Anthropic product announcements (2026-04-08 through 2026-06-09)
```

### Scheduled Deployments: Use Cases and Operational Controls

```
Managed Agents Scheduled Deployments (public beta, June 9, 2026)

NAMED USE CASES (from announcement):
  - Nightly data sync
  - Weekly compliance scan
  - Daily digest
  - Spreadsheet analysis → reports on weekly/monthly schedule (Rakuten)
  - Replacing self-built scheduling infrastructure (Actively AI)

OPERATIONAL CONTROLS:
  - Set cron schedule for recurring runs
  - Pause / resume deployment
  - Trigger additional on-demand runs

DISTINCT FROM Claude Code Routines (blog-anthropic-claude-code-routines.md):
  Claude Code Routines: scheduling for Claude Code sessions
                        (CLI layer; research preview, April 2026)
                        Plan-gated: 5/15/25 runs per day
  Managed Agents:       scheduling for Managed Agent sessions
                        (platform API layer; public beta, June 2026)
                        No documented per-day quota

Source: Anthropic product announcement (2026-06-09)
```

### Environment Variable Vaults: Credential Injection Pattern for CLIs

```
Managed Agents — Environment Variables in Vaults (public beta, June 9, 2026)

MECHANISM:
  - Credentials stored in vault (outside the sandbox)
  - Sandbox receives a placeholder (not the actual credential)
  - Agent invokes CLI; vault injects actual credential at execution time
  - "The agent never sees your key because the sandbox only holds a placeholder."

EXTENDS credential security patterns from blog-anthropic-scaling-managed-agents.md:
  Pattern 1 (April 8):   bundle auth with resource at provision() time
  Pattern 2 (April 8):   vault + MCP proxy (OAuth tokens → MCP tool → harness)
  Pattern 3 (June 9):    vault + CLI env var → agent executes CLI command

CUSTOMER IMPLEMENTATIONS:
  Notion      | Notion CLI          | Meets security team guidelines
  Browserbase | browse CLI          | Browser + agent compute integration
  KERNEL      | Database CLI        | Usage and conversation tracking
  Milana      | Custom CLI wrappers | Private API invocation

Source: Anthropic product announcement (2026-06-09)
```

### Customer Evidence by Feature

```
SCHEDULED DEPLOYMENTS:
  Rakuten     | Yusuke Kaji (GM of AI for Business):
    "Teams across Rakuten use scheduled deployments to analyze data
     in a spreadsheet and produce reports on schedules."
  Actively AI | Mihir Garimella (Co-founder):
    "We replaced the scheduling infrastructure we'd built ourselves
     with scheduled deployments."
  Ando        | Sara Du (Founder):
    "With scheduled deployments, they can bundle more capabilities
     into one autonomous agent."

ENVIRONMENT VARIABLES IN VAULTS:
  Notion      | Quan Nguyen (Public API Lead):
    "Environment variables in vaults let us securely roll out the
     Notion CLI, meeting our security team's strict guidelines."
  Browserbase | Ziray Hao (Product Lead):
    "Environment variables in vaults enabled our engineering team
     to combine two major compute primitives: the agent and the browser."
  KERNEL      | Catherine Jue (Co-founder & CEO):
    "Our agent now connects directly to databases where we track
     usage and customer conversations."
  Milana      | Raghav Sethi (Co-founder & CTO):
    "Environment variables in vaults let our agent invoke private
     APIs through a CLI without exposing credentials."

Source: Anthropic product announcement (2026-06-09)
All testimonials: customer-reported, no independent audit
```

## Cross-References

- **Corroborates**:
  - **blog-anthropic-claude-managed-agents.md** (Claim 8): "Multiple enterprise teams built initial integrations in weeks rather than months." The Actively AI testimonial (Claim 3 here) extends the evidence base: Actively AI replaced self-built infrastructure, not just avoided building it from scratch. This is a stronger form of the same build-vs-buy evidence.
  - **blog-anthropic-scaling-managed-agents.md** (Claim 7): The security boundary design — credentials never accessible from the sandbox — is confirmed here. "The agent never sees your key because the sandbox only holds a placeholder" is the user-facing expression of the architectural invariant documented in that engineering post.
  - **blog-anthropic-claude-managed-agents-selfhosted.md** (Claim 8): Vercel's "Sandbox firewall injects credentials at the network boundary so they never enter the sandbox" and this announcement's vault env-var placeholder mechanism are both implementations of the same invariant. Two separate announced mechanisms for achieving credential isolation in different execution contexts.
  - **blog-anthropic-claude-code-routines.md** (Claim 1): "Routines eliminate the local-machine infrastructure requirement for scheduled AI automation." The Actively AI testimonial in this note (replaced self-built scheduling infrastructure) corroborates the same dynamic at the Managed Agents platform layer: teams reach for managed scheduling rather than maintaining DIY schedulers.

- **Contradicts**: None identified. Managed Agents scheduled deployments and Claude Code Routines address the same underlying need (scheduled AI automation) at different product abstraction levels. This is a conditioning variable (what product layer you're building on) — Claude Code CLI layer vs. Managed Agents platform API — not a factual contradiction. Both are valid solutions for their respective audiences.

- **Extends**:
  - **blog-anthropic-scaling-managed-agents.md** (Claim 7, "Credential Security Patterns" Concrete Artifact): That note documented two credential isolation patterns (bundle-with-resource; vault+proxy). This announcement adds a third: vault + CLI env var → agent executes CLI command. All three achieve the same invariant (credentials never in sandbox) via different mechanisms suited to different integration types.
  - **blog-anthropic-claude-managed-agents.md** (platform capability matrix in Concrete Artifacts): Adds two new public beta features (scheduled deployments; environment variable vaults) to the April 8 capability list.
  - **blog-anthropic-managed-agents-dreaming-outcomes.md** (Feature Availability Matrix Concrete Artifact): Updates the May 6 feature matrix with two additional public beta features, completing the current platform feature status.
  - **blog-anthropic-mcp-production-agents.md**: That note recommends building remote MCP servers as the production integration layer for agents. This announcement positions CLI + vault as a complementary integration path — faster to set up for services with existing CLIs, avoiding MCP server build/host overhead. Both achieve agent-to-service integration; they differ in mechanism, effort, and output structure.

- **Novel**:
  - **Scheduled deployments as a first-class Managed Agents feature**: Prior corpus notes for the Managed Agents platform (April 8 launch, April 23 memory, May 6 dreaming/outcomes/multiagent, May 19 self-hosted sandboxes/MCP tunnels) document no scheduling capability. Scheduling at the Claude Code layer was documented in April. This is the first corpus note to document platform-level scheduled agent deployment.
  - **CLI + vault env var = agent integration pattern**: No prior corpus source documents the three-step pattern: vault holds credentials → sandbox holds placeholder → CLI executes with injected credentials. This is a new integration pathway alongside custom MCP servers and direct API integration.
  - **Actively AI replacing self-built scheduling infrastructure**: Prior build-vs-buy evidence showed teams adopting managed services instead of building from scratch. The Actively AI case (built something → replaced it with the managed option) is a stronger form of the same evidence and is new to the corpus.
  - **Browserbase as an agent-native browser-skills factory**: The recursive pattern (browser infrastructure provider using Managed Agents to build and curate browser skills for other agents) is not documented anywhere else in the corpus. A service provider using AI agents to develop its own capability catalog is a new category of agent-powered service development.

## Guide Impact

- **Chapter 02 (Harness Engineering) — Scheduling infrastructure**: Update the scheduling comparison to add Managed Agents scheduled deployments as a third option alongside Claude Code Routines (blog-anthropic-claude-code-routines.md Claim 1) and GHAW self-hosted scheduling. Current framing is binary (Routines vs. GHAW self-hosted). The updated taxonomy:
  - Self-hosted (GHAW model): GitHub Actions cron, unlimited scale, full control, maintenance overhead
  - Claude Code Routines: Anthropic-managed cloud, 5–25/day quota, Claude Code session layer, research preview (April 2026)
  - Managed Agents scheduled deployments: Anthropic-managed cloud, Managed Agents platform layer, public beta (June 2026), no documented per-day quota
  The Actively AI testimonial is the key evidence for the third option meeting production requirements: a team that built their own scheduler replaced it with the managed service.

- **Chapter 02 (Harness Engineering) — Credential security**: Add the CLI + vault env var pattern (Claim 4 here) as a third credential isolation mechanism alongside the two in blog-anthropic-scaling-managed-agents.md Claim 7 (bundle-with-resource; vault+proxy). The three patterns now form a complete taxonomy of vault-based credential isolation for agent sandboxes:
  - Bundle-with-resource: for repository/filesystem access at provision time
  - Vault + MCP proxy: for OAuth-based service access via MCP tools
  - Vault + CLI env var: for CLI-based service access via shell command execution
  All three share the invariant: credentials never accessible from Claude-generated code.

- **Chapter 03 (Tool Use / Integrations)** or wherever integration patterns are documented: Add CLI-as-integration-path alongside MCP servers as a production-viable mechanism. Document the trade-off: CLI integration is faster to set up for services with existing CLIs; MCP servers provide more structured, typed tool interfaces. Decision axis: does the service have a mature CLI? If yes, vault + CLI env var is a valid lower-friction path. If not (or if typed responses matter), build the MCP server.

- **Chapter 06 (Production Deployment) — Deployment trigger model taxonomy**: Add scheduled deployments as a time-based trigger model for Managed Agents. The deployment taxonomy currently covers session-initiated (prompt-and-response) and event-driven (webhooks) patterns documented in blog-anthropic-managed-agents-dreaming-outcomes.md (Claim 10). Scheduled deployments complete a three-way taxonomy: time-based (scheduled), event-based (webhooks), and request-based (prompt-and-response).

- **Chapter 04 (Authentication & Secrets)** or wherever credential security is documented: The vault mechanism (sandbox holds placeholder; actual credentials injected at execution) should be documented as the security primitive enabling CLI tool authentication at enterprise scale. The Notion quote ("meeting our security team's strict guidelines") is concrete evidence this pattern passes enterprise security reviews that direct credential injection would not.

## Extraction Notes

- The blog post is a JavaScript-rendered SPA on claude.com. Multiple WebFetch passes were made; the second targeted pass captured verbatim the opening statement, feature descriptions, all seven customer testimonials, and the availability statement. These quotes are treated as accurate per the fetch.
- The blog post title from the issue ("New in Claude Managed Agents: run agents on a schedule and store environment variables in vaults") matches the entry title in the RSS feed. The source URL is https://claude.com/blog/whats-new-in-claude-managed-agents.
- Seven customer testimonials were extracted (Rakuten, Actively AI, Ando, Notion, Browserbase, KERNEL, Milana). The Prospector's triage comments identified five customers (Rakuten, Actively AI, Ando, Browserbase, KERNEL) and did not mention Notion or Milana. Both Notion and Milana are present in the actual announcement and are documented here.
- Ando's Sara Du quote ("With scheduled deployments, they can bundle more capabilities into one autonomous agent") uses "they" rather than "we" — this may refer to scheduled deployments as the capability subject ("scheduled deployments enable bundling more capabilities") rather than the Ando team. The quote is reproduced verbatim as extracted.
- No performance benchmarks appear in this announcement, unlike the April 8 and May 6 announcements. The evidence is entirely testimonial.
- The blog post likely links to Claude Platform documentation and the Claude Console, but linked pages were not fetched. Technical implementation details — how scheduling is configured, what the vault API looks like, what CLI authentication mechanisms are supported — would require a documentation extraction to surface.
- No pricing changes are mentioned. The $0.08/session-hour rate from the April 8 announcement is assumed unchanged. Scheduled deployments may have different pricing implications (e.g., per-run charges vs. session-hour billing), but this is not stated in the announcement.
- Confidence is set to `anecdotal` overall because the evidence is entirely from customer testimonials at launch, with no performance benchmarks, no technical architecture details, and no independent corroboration.
