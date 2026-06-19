---
source_url: https://github.blog/changelog/2026-06-17-auto-mode-in-copilot-chat-available-for-all-users
source_type: docs
title: "Auto mode in Copilot Chat available for all users"
author: GitHub (official changelog)
date_published: 2026-06-17
date_extracted: 2026-06-19
last_checked: 2026-06-19
status: current
confidence_overall: settled
issue: "#1218"
---

# Auto Mode in Copilot Chat Available for All Users

> GitHub's June 17, 2026 changelog announces auto model selection as generally available
> in Copilot Chat on github.com and the GitHub mobile app for all Copilot plans — the
> fourth GitHub Copilot surface to receive auto routing — with task-complexity-aware
> routing, an explicitly named model pool (Sonnet 4.6, GPT-5.4 mini, GPT-5.4, Haiku 4.5),
> per-response model switching, hover-based transparency, and a 10% billing discount for
> paid subscribers.

## Source Context

- **Type**: docs (GitHub official product changelog, June 17, 2026; approximately 200 words
  of primary announcement text, tagged "Release", organized into three named sections:
  "How it works," "Benefits of auto mode," and "Token use")
- **Author credibility**: GitHub engineering team announcing a production feature. Authoritative
  for: the existence and GA status of the feature, the named model pool, the routing heuristic
  description, the billing mechanic, and the stated benefits. Not a credible source for: how
  the routing algorithm weighs task complexity against model availability, which specific plan
  tiers receive which pool members, whether the task-complexity analysis covers the same four
  dimensions as VS Code auto (reasoning, code generation, bug diagnosis, tool orchestration),
  what "real-time system health" specifically monitors (latency, error rates, saturation), or
  whether the model pool differs between github.com and the GitHub mobile app.
- **Scope**: The Copilot Chat auto model selection feature on github.com and the GitHub mobile
  app. Covers the routing heuristic (complexity + availability), the model pool (four named
  models as of June 2026), billing (10% discount), transparency affordance (hover), and user
  control (per-response switching). Does NOT cover: plan-tier-specific pool membership, the
  routing algorithm's internal implementation, integration with IDE-based Copilot Chat (VS Code
  Copilot Chat uses its own auto mode documented in issue #844), JetBrains Copilot Chat auto
  routing, whether Chat auto interacts differently with sessions started via the contextual chat
  agent vs. standalone chat, or whether "Copilot Chat" here includes the CLI REPL.

## Extracted Claims

### Claim 1: Copilot Chat auto model selection is generally available on github.com and the GitHub mobile app for all Copilot plans as of June 17, 2026

- **Evidence**: Official GitHub product changelog announcing GA. Stated as available
  "for all Copilot plans" — the broadest plan availability of any GitHub Copilot auto
  feature documented to date.
- **Confidence**: settled (product fact — feature announced in official changelog)
- **Quote**: "GitHub Copilot auto model selection is now generally available in Copilot
  Chat on github.com and the GitHub mobile app for all Copilot plans."
- **Our assessment**: This is the fourth GitHub Copilot surface to receive auto model
  selection, following CLI (issue #203, April 17, 2026), Copilot Cloud Agent / CCA
  (issue #745, May 14, 2026), and VS Code (issue #844, May 20, 2026). The rollout is
  now complete across all major GitHub Copilot surfaces. The "all Copilot plans" scope
  matches the CLI auto availability (issue #203, Claim 1: "generally available across
  all Copilot plans") and is broader than the VS Code note which did not specify plan
  gating. For Ch02: update the auto model selection surface inventory — the feature is
  now available on four surfaces: CLI, CCA, VS Code, and Copilot Chat (github.com + mobile).

### Claim 2: Copilot Chat auto routing selects models based on both task complexity and real-time model availability

- **Evidence**: The "How it works" section of the changelog describes dual-input routing.
  The named routing inputs are "the complexity of your request and current model availability."
  The benefits section separately confirms "complexity and real-time system health" as inputs.
- **Confidence**: settled (routing heuristic stated in official changelog)
- **Quote**: "With auto, Copilot chooses a model on your behalf based on the complexity of
  your request and current model availability."
- **Our assessment**: Copilot Chat auto is both task-complexity-aware and availability-aware
  — the same dual-input pattern as VS Code auto (issue #844, Claim 1: "evaluates your task
  across several dimensions like reasoning, code generation complexity, bug diagnosis
  difficulty, and tool orchestration needs"). This distinguishes Chat auto from CLI auto
  (issue #203, Claim 2), which routes on "plan and policies" and explicitly NOT on task type.
  The specific task-complexity dimensions evaluated by Chat auto are not named in the
  changelog (unlike VS Code auto's four dimensions: reasoning, code generation complexity,
  bug diagnosis difficulty, tool orchestration needs). This is an underdocumented detail —
  whether Chat auto uses the same taxonomy as VS Code auto is not confirmed. For Ch02:
  document Chat auto as task-aware, but note that the routing dimensions are not as
  specifically documented as the VS Code surface.

### Claim 3: The Copilot Chat auto model pool (as of June 2026) explicitly includes Claude Sonnet 4.6, GPT-5.4 mini, GPT-5.4, and Haiku 4.5

- **Evidence**: The model pool is named explicitly in the "How it works" section.
  The pool is described as evolving over time.
- **Confidence**: settled (model pool enumerated in official changelog as of June 17, 2026;
  noted as subject to change)
- **Quote**: "Auto routes to models like Claude Sonnet 4.6, GPT-5.4 mini, GPT-5.4, and
  Haiku 4.5 based on your plan and policies."
- **Our assessment**: The Chat auto pool is the most completely documented auto pool in the
  corpus. The word "like" suggests the list is illustrative rather than exhaustive — the
  actual pool may include additional models. Notably, GPT-5.4 mini appears in this pool but
  was not in the CLI auto pool (issue #203, Claim 3: GPT-5.4, GPT-5.3-Codex, Sonnet 4.6,
  Haiku 4.5). GPT-5.3-Codex was in the CLI pool but is not listed here. These differences
  reflect per-surface pool membership, not a contradiction — GitHub adjusts the auto pool
  per surface. The GitHub documentation on supported auto models (linked from the changelog)
  confirms a broader pool for Chat including MAI-Code-1-Flash and Raptor mini alongside the
  named models. The phrase "based on your plan and policies" confirms pool membership varies
  by plan and admin policy configuration. For Ch04: document Chat auto as cost-bounded to
  non-Opus models (Haiku at low cost, Sonnet at mid cost, GPT-5.4 mini at low cost) — same
  ceiling pattern as CLI and VS Code auto where Opus-tier models are absent from the auto pool.

### Claim 4: Task-based routing evaluates the task and selects the optimal model based on both complexity and real-time system health

- **Evidence**: Named explicitly as a benefit in the changelog's "Benefits of auto mode"
  section.
- **Confidence**: settled (stated in official changelog)
- **Quote**: "Auto evaluates your task and chooses the optimal model based on complexity
  and real-time system health."
- **Our assessment**: The pairing of "complexity" (task input) and "real-time system health"
  (availability input) in a single routing criterion closely mirrors VS Code auto's dual
  routing architecture (issue #844, Claim 2: "real-time model availability and reliability
  signals" + task analysis). This is also consistent with CCA auto's "system health and
  model performance" framing (issue #745, Claim 2), though CCA auto did not confirm
  task-complexity analysis. Chat auto is the first changelog besides VS Code to explicitly
  name task complexity as a routing input alongside system health. For Ch04: Chat auto
  can be characterized as a task-aware routing surface (like VS Code auto), contrasted with
  CLI auto (availability-only routing) and CCA auto (system health + model performance,
  task complexity not confirmed).

### Claim 5: Copilot Chat auto provides transparency by surfacing the model used via hover on the model response

- **Evidence**: Stated as the first benefit in the "Benefits of auto mode" section.
- **Confidence**: settled (stated in official changelog)
- **Quote**: "You can see which model was used by hovering over the model response."
- **Our assessment**: This is the identical transparency mechanism as VS Code auto
  (issue #844, Claim 6: "You can see which model was used by hovering over the model
  response"). Both are hover-based, in-UI disclosure — a passive transparency affordance
  that does not interrupt the interaction flow. This is in contrast to CLI auto (issue #203,
  Claim 5: "you can see which model was used directly in the Copilot CLI"), where the model
  name is surfaced in terminal output, making it capturable for logging. For harness
  engineering: the hover-based transparency in Chat auto is not directly capturable
  programmatically — teams building observability over Chat model selection cannot pipe
  chat hover metadata into logs the way CLI output can be captured.

### Claim 6: Users can switch between auto and any specific model on a per-response basis in Copilot Chat

- **Evidence**: Stated as a benefit in the "Benefits of auto mode" section. The "per-response
  basis" granularity is more specific than the CLI and VS Code descriptions of user control.
- **Confidence**: settled (stated in official changelog)
- **Quote**: "You can switch between auto and any specific model of choice on a per-response
  basis."
- **Our assessment**: The per-response switching granularity is explicitly finer than what
  other auto surfaces specify. CLI auto (issue #203, Claim 8) and VS Code auto (issue #844,
  Claim 7) both state users can switch "at any time," but neither specifies per-response
  granularity. Chat auto's per-response framing means the routing delegation is not sticky
  — each response can use a different model selection strategy. This is the appropriate
  granularity for a chat interface, where individual turns may have very different task
  demands (one turn may be a quick factual question, the next a complex code review). For
  Ch02: document per-response model control as a Copilot Chat-specific capability that
  enables mixed-strategy conversations (auto for simple turns, explicit model for demanding
  turns within the same session).

### Claim 7: Copilot Chat auto honors all user and administrator model settings

- **Evidence**: Stated as a benefit in the "Benefits of auto mode" section.
- **Confidence**: settled (stated in official changelog)
- **Quote**: "Auto honors all user and administrator model settings."
- **Our assessment**: Consistent with the pattern across all GitHub Copilot auto surfaces:
  CLI auto (issue #203, Claim 7: "honors all administrator model settings"), VS Code auto
  (issue #844, Claim 8: "Auto honors all model policies set by admins"), CCA auto (policy
  compliance not confirmed in issue #745, Extraction Note 3, but highly likely by analogy).
  Chat auto is also unique in mentioning "user" settings alongside "administrator" settings —
  the other auto surface notes only name administrator settings. Whether "user settings"
  refers to personal model preferences (e.g., a user's own model exclusions or favorites)
  or plan-level access is not specified. For Ch05: Chat auto is enterprise-safe to enable —
  admin model exclusion policies are enforced and auto will not route to administrator-
  excluded models. The mention of "user settings" may offer a per-user customization layer
  not documented in other surfaces.

### Claim 8: Use of Copilot Chat auto is billed at a 10% discount for all paid subscribers

- **Evidence**: Stated in the "Token use" section of the changelog.
- **Confidence**: settled (billing mechanic stated in official changelog)
- **Quote**: "Use of auto is billed at a 10% discount for all paid subscribers."
- **Our assessment**: The 10% discount for auto mode is now confirmed across all four
  GitHub Copilot auto surfaces: CLI (issue #203, Claim 6), VS Code (issue #844, Claim 4),
  CCA (issue #745, Claim 3), and now Chat. The consistent discount across all four surfaces
  confirms this is a platform-wide GitHub billing policy incentivizing auto adoption — not
  a surface-specific experiment. For Ch04: the 10% auto discount applies to all Copilot
  Chat paid subscribers using auto mode on github.com and mobile. Teams that have adopted
  auto across CLI, CCA, and VS Code can now extend this cost pattern to their Chat usage
  as well, compounding savings across all surfaces.

### Claim 9: Copilot Chat auto is designed to optimize for token use while maintaining high quality results

- **Evidence**: Stated in the introductory paragraph of the changelog.
- **Confidence**: settled (stated in official changelog; no empirical evidence provided)
- **Quote**: "Using auto allows you to better optimize for token use while maintaining
  high quality results."
- **Our assessment**: This is a marketing-adjacent claim — "high quality results" is
  unquantified and no comparison data is provided. The "optimize for token use" framing
  is the most explicit statement anywhere in the GitHub Copilot auto corpus that the routing
  is intended to reduce token consumption, not just financial cost. This framing appears
  alongside "cost and response quality" in the "How it works" section: "It provides you
  with the same access to your favorite models while optimizing for cost and response
  quality." The dual objective (token efficiency + quality) is consistent with the general
  auto mode rationale across surfaces but is phrased more explicitly here than in the CLI
  (issue #203) or CCA (issue #745) announcements. Take "high quality" at face value as
  intent, not as a measured outcome. For Ch04: use the "token optimization + quality"
  framing when explaining Chat auto to practitioners — this is GitHub's stated value
  proposition, not just cost reduction.

## Concrete Artifacts

### Copilot Chat Auto Model Selection — Full Announcement Content (June 17, 2026)

```
Source: https://github.blog/changelog/2026-06-17-auto-mode-in-copilot-chat-available-for-all-users
Published: June 17, 2026

--- INTRO ---

GitHub Copilot auto model selection is now generally available in Copilot Chat on
github.com and the GitHub mobile app for all Copilot plans. With auto, Copilot
chooses a model on your behalf based on the complexity of your request and current
model availability. Using auto allows you to better optimize for token use while
maintaining high quality results.

--- HOW IT WORKS ---

Auto model selection is dynamic, routing to models based on real-time availability
and the complexity of your request. It provides you with the same access to your
favorite models while optimizing for cost and response quality. Auto routes to models
like Claude Sonnet 4.6, GPT-5.4 mini, GPT-5.4, and Haiku 4.5 based on your plan and
policies. The models auto will route to will change over time.

--- BENEFITS OF AUTO MODE ---

• Transparency: You can see which model was used by hovering over the model response.
• Task-based routing: Auto evaluates your task and chooses the optimal model based on
  complexity and real-time system health.
• Stay in control: You can switch between auto and any specific model of choice on a
  per-response basis.
• Respects your policies: Auto honors all user and administrator model settings.

--- TOKEN USE ---

Use of auto is billed at a 10% discount for all paid subscribers.
```

### GitHub Copilot Auto Model Selection — Four-Surface Comparison (as of June 2026)

```
Surface        | Announced  | Routing Heuristic                    | Pool (named)               | Discount | Plan Scope
───────────────┼────────────┼──────────────────────────────────────┼────────────────────────────┼──────────┼────────────
CLI            | Apr 17     | Plan + policies + rate-limit         | GPT-5.4, GPT-5.3-Codex,    | 10%      | All plans
               | (#203)     | pressure — NOT task-type-aware       | Sonnet 4.6, Haiku 4.5      |          |
───────────────┼────────────┼──────────────────────────────────────┼────────────────────────────┼──────────┼────────────
CCA            | May 14     | System health + model performance    | Not enumerated              | 10%      | Not stated
               | (#745)     | — task-complexity NOT confirmed      |                             |          |
───────────────┼────────────┼──────────────────────────────────────┼────────────────────────────┼──────────┼────────────
VS Code        | May 20     | Task dimensions (reasoning, code gen,| Multiple families (not      | 10%      | Not stated
               | (#844)     | bug diagnosis, tool orchestration)   | named; 0x–1x only)          |          |
               |            | + utilization + model health metrics |                             |          |
───────────────┼────────────┼──────────────────────────────────────┼────────────────────────────┼──────────┼────────────
Chat           | Jun 17     | Task complexity + real-time          | Sonnet 4.6, GPT-5.4 mini,  | 10%      | All plans
(github.com    | (#1218)    | model availability / system health   | GPT-5.4, Haiku 4.5 (named; |          |
+ mobile)      |            | — task-complexity-aware (confirmed)  | "like" = not exhaustive)    |          |

Notes:
- All four surfaces: 0x–1x multiplier models only (Opus-tier excluded)
- All four surfaces: admin policy-compliant; user retains override control
- CCA auto is the only surface where weekly rate limits are explicitly eliminated (not "mitigated")
- Chat auto is the only surface to specify "per-response" switching granularity
```

### Copilot Chat Auto Model Pool — Documentation Reference (as of June 2026)

```
Source: GitHub Docs — Supported AI Models (auto model selection section)
URL: https://docs.github.com/copilot/reference/ai-models/supported-models#supported-ai-models-in-auto-model-selection

Models listed for Copilot Chat auto (as of June 2026 fetch):
  - GPT-5 mini
  - GPT-5.3-Codex
  - GPT-5.4
  - GPT-5.4 mini
  - Claude Haiku 4.5
  - Claude Sonnet 4.6
  - MAI-Code-1-Flash
  - Raptor mini

Note: Changelog names four models ("like Claude Sonnet 4.6, GPT-5.4 mini, GPT-5.4, and
Haiku 4.5"). The docs page lists a broader set. Availability varies by plan and policies.
```

## Cross-References

- **Corroborates**:
  - `docs-github-copilot-cli-auto-model-selection.md` (issue #203, Claims 6, 7, 8): The
    10% billing discount, admin policy enforcement, and user switching control are all
    confirmed for CLI auto and match Chat auto exactly. The consistent billing mechanic
    across all four surfaces (confirmed for CLI, VS Code, CCA, and now Chat) establishes
    this as a platform-wide GitHub billing policy, not a surface-specific feature.
  - `docs-github-copilot-vscode-auto-model-selection.md` (issue #844, Claims 1, 4, 6, 7, 8):
    VS Code auto is the closest analogue to Chat auto — both are task-complexity-aware,
    both use hover-based transparency (VS Code Claim 6 quote: "You can see which model was
    used by hovering over the model response" — identical wording to Chat auto), both offer
    10% discount and admin policy compliance. Chat auto's task-aware routing extends the VS
    Code pattern to the github.com and mobile surfaces.
  - `docs-github-copilot-cca-auto-model-selection.md` (issue #745, Claim 3): The 10%
    discount for CCA auto matches Chat auto's 10% discount, corroborating the platform-wide
    billing incentive conclusion.
  - `docs-github-copilot-chat-agent-sessions.md` (issue #1145, Claim 1): That source
    documented GitHub expanding Chat as a session management surface (June 10, 2026). This
    source adds model routing intelligence to Chat one week later (June 17, 2026). The two
    sources together show GitHub making Copilot Chat a fully-featured autonomous surface:
    session visibility + intelligent model routing.

- **Extends**:
  - `docs-github-copilot-cli-auto-model-selection.md` (issue #203, Claim 2): That source's
    assessment stated "For practitioners who want task-aware routing, explicit model selection
    remains the only option" when discussing CLI auto. VS Code auto (issue #844) first
    disproved this for the VS Code surface. Chat auto further extends task-aware auto routing
    to github.com and mobile. The general guide statement about auto mode needing task-aware
    routing must now note that three surfaces (VS Code, Chat, and partially CCA via "model
    performance") offer some form of task-consideration in routing; only CLI auto remains
    purely availability-driven.
  - `docs-github-copilot-vscode-auto-model-selection.md` (issue #844, Claim 3): The VS Code
    note established that the auto pool is bounded to 0x–1x multiplier models (no Opus).
    The Chat auto changelog does not state this constraint explicitly, but the named pool
    (Sonnet 4.6, GPT-5.4 mini, GPT-5.4, Haiku 4.5) contains no Opus-tier models, consistent
    with the 0x–1x ceiling pattern across all auto surfaces.
  - `docs-github-copilot-agent-model-selection.md` (issue #171): That source documented
    explicit model selection for cloud agents on github.com (Claude Sonnet, Opus tiers).
    Chat auto now provides a complementary delegated-routing option on the same github.com
    surface. Together the two sources define the full model selection spectrum on github.com:
    explicit tier selection for cloud agent tasks (issue #171) vs. auto routing for Chat
    interactions (this source).

- **Contradicts**: None identified. The four auto surfaces use different routing inputs and
  pool compositions, but this reflects per-surface implementation diversity, not contradictory
  claims about the same surface or feature. The CLI auto note's assessment (issue #203, Claim 2)
  that task-aware routing requires explicit model selection is now incomplete as a general
  statement, but accurate for the CLI surface specifically — this is a corpus synthesis gap
  for the guide, not a factual contradiction between source notes. No contradiction issue filed.

- **Novel**:
  - **Copilot Chat as the fourth and final auto model selection surface**: This is the first
    corpus source to document auto routing on the github.com Chat surface and the GitHub mobile
    app. It completes the rollout of auto model selection across all major GitHub Copilot
    surfaces (CLI, CCA, VS Code, Chat). No prior source documented Chat auto; prior corpus
    sources treated Chat as a session management and agent escalation surface, not a routing
    surface.
  - **Per-response switching granularity**: No prior auto model selection source in the corpus
    specifies "per-response" switching. CLI auto (issue #203, Claim 8) and VS Code auto (issue
    #844, Claim 7) say "at any time" — a less specific granularity. Chat auto's per-response
    framing is a distinctive UX property of the chat-turn model.
  - **"Token use" optimization framing**: No prior auto source frames the benefit as "optimize
    for token use." CLI auto, CCA auto, and VS Code auto frame benefits around cost (multiplier
    discount) and availability (rate-limit mitigation). Chat auto adds explicit token
    optimization language ("better optimize for token use") — a nuance that matters when Chat
    can process long multi-turn conversations with substantial context.
  - **"User settings" as a distinct policy layer**: Chat auto (Claim 7) is the only auto
    surface source to name "user and administrator model settings" — all other surfaces only
    name administrator settings. Whether "user settings" is a meaningful new capability or
    just broader phrasing is unclear from the changelog alone.
  - **Model pool inclusion of GPT-5.4 mini**: The Chat auto pool explicitly names GPT-5.4
    mini, which was not enumerated in the CLI auto pool (issue #203, Claim 3 named GPT-5.3-
    Codex instead). First corpus confirmation of GPT-5.4 mini in any auto routing pool.

## Guide Impact

- **Chapter 02 (Harness Engineering — Auto Model Selection Surface Map)**:
  - The auto model selection surface inventory is now complete across all four major
    GitHub Copilot surfaces (CLI, CCA, VS Code, Chat). Update the guide to reflect
    this completion. The four-surface comparison table in Concrete Artifacts is suitable
    for direct inclusion or adaptation. Practitioners should understand the routing
    heuristic differences: CLI = availability-only; CCA = system health + model performance;
    VS Code = task-aware + availability; Chat = task-complexity + system health.
  - Add Copilot Chat to the default recommendation for auto mode: practitioners using
    github.com or the mobile app can now benefit from auto model selection without
    configuring anything. Recommend Chat auto as the default Chat model configuration
    for practitioners who haven't formed an explicit model selection policy — it provides
    task-aware routing and a 10% billing discount with no setup required.

- **Chapter 04 (Model Selection and Cost Management)**:
  - The 10% auto-mode discount is now confirmed across all four Copilot surfaces. Update
    the guide's cost-management recommendations to include Copilot Chat as a fourth surface
    where auto adoption produces billing savings. Teams with comprehensive Copilot adoption
    (CLI scripts + CCA workflows + VS Code + Chat) can compound auto-mode savings by
    defaulting to auto on all four surfaces.
  - Document the per-response model switching capability as a Chat-specific pattern for
    mixed-complexity conversations: use auto for routine turns (factual questions, short
    code snippets), switch to an explicit high-capability model for turns requiring complex
    reasoning (multi-file refactoring discussions, cross-codebase analysis). This mixed
    strategy is enabled by per-response rather than per-session granularity.

- **Chapter 01 (Daily Workflows — Chat-First Patterns)**:
  - Combine with `docs-github-copilot-chat-agent-sessions.md` (issue #1145) to document
    Chat as a fully autonomous surface: auto model routing for intelligence (this source)
    + session management tools for workflow continuity (June 10 source). Practitioners
    who prefer a browser-first or mobile-first workflow now have both routing intelligence
    and session visibility in Chat — a complete daily workflow surface.

## Extraction Notes

1. **Source is short by design (~200 words of primary text)**: All substantive claims are
   exhausted in the nine claims above. The source covers one narrow feature GA announcement.

2. **"Like" qualifier on model pool**: The changelog uses "like Claude Sonnet 4.6, GPT-5.4
   mini, GPT-5.4, and Haiku 4.5" — the word "like" signals the list is illustrative, not
   exhaustive. The GitHub documentation page linked from the changelog confirms a broader pool
   (including MAI-Code-1-Flash and Raptor mini). Claims citing specific pool members should
   note this qualifier.

3. **Mobile app scope**: The changelog explicitly includes "the GitHub mobile app" alongside
   github.com. No prior auto model selection source documented mobile app coverage. The mobile
   app may have a different model pool or UI presentation (the hover transparency mechanism,
   for example, is a desktop-native affordance — how it manifests on mobile is not documented).

4. **Task complexity dimensions not enumerated**: Unlike VS Code auto (issue #844, Claim 1),
   which named four specific task dimensions (reasoning, code generation complexity, bug
   diagnosis difficulty, tool orchestration needs), Chat auto uses only "complexity" and
   "real-time system health" without naming specific dimensions. Whether Chat auto uses the
   same taxonomy internally is unknown from this source.

5. **No rate-limit language**: Unlike CLI auto ("mitigating rate limits," issue #203, Claim 4)
   and CCA auto ("won't be impacted by weekly rate limits," issue #745, Claim 4), Chat auto
   makes no mention of rate-limit behavior. Whether Chat auto provides the same rate-limit
   mitigation benefit as other surfaces is unconfirmed by this source.

6. **No contradictions to file**: Reviewed all corpus auto model selection notes (issues #203,
   #745, #844) and the Chat session management note (issue #1145). All claims are additive
   across surfaces — no source makes a contradictory claim about the Chat surface. The
   routing-heuristic differences across surfaces are per-surface implementation choices, not
   contradictions. No contradiction issue filed.
