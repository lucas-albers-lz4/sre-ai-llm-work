---
source_url: https://github.blog/changelog/2026-05-26-target-copilot-models-to-organizations-with-model-rules
source_type: docs
title: "Target Copilot models to organizations with model rules"
author: GitHub (official changelog)
date_published: 2026-05-26
date_extracted: 2026-05-27
last_checked: 2026-05-27
status: current
confidence_overall: settled
issue: "#957"
---

# Target Copilot Models to Organizations with Model Rules

> GitHub's May 26, 2026 changelog introducing targeted model rules — a new public-preview
> enterprise governance capability that lets enterprise owners assign specific Copilot models
> to individual organizations, moving beyond a single enterprise-wide default to per-org
> model policy control.

## Source Context

- **Type**: docs (GitHub official product changelog, May 26, 2026; approximately 150 words
  of primary announcement text, plus two linked documentation pages followed per MINER.md §1:
  "Managing availability of default models" and "Managing default models for your organization")
- **Author credibility**: GitHub engineering team announcing a production feature change (public
  preview). Authoritative for the feature's existence, its plan requirements, and the available
  model availability modes. Not a credible source for: how targeted model rules interact with
  auto-routing within the permitted model set, whether rules apply retroactively to active tasks,
  or any performance or cost implications of restricting model availability.
- **Scope**: Enterprise-level governance for Copilot model availability, targeted at enterprise
  owners managing multiple organizations. Covers: the targeted model rules mechanism, the
  Enabled/Optional availability modes, the refreshed default model availability UI, and plan
  requirements. Does NOT cover: which specific models can be targeted, what happens when an
  organization has active sessions with a model that gets restricted, how targeted rules interact
  with BYOK configurations, or how individual Copilot Pro/Pro+/Free users are affected.

## Extracted Claims

### Claim 1: Enterprise owners can now target specific Copilot models to individual organizations via targeted model rules (public preview as of May 26, 2026)

- **Evidence**: Official GitHub product changelog announcing the feature as in public preview.
  Stated directly as the headline capability of the changelog entry.
- **Confidence**: settled (product fact — the feature exists and is documented in official changelog)
- **Quote**: "Enterprise owners now have granular control over which GitHub Copilot models are
  available to each organization. With targeted model rules, you can allow specific models for
  specific organizations instead of relying on a single enterprise-wide setting. This capability
  is now in public preview."
- **Our assessment**: Prior to this feature, enterprise Copilot model availability was binary:
  a model is either available across the entire enterprise or it is not. Targeted model rules
  introduce a per-organization targeting dimension. For Ch05: document this as a new governance
  primitive enabling differentiated model access across the enterprise. Example use cases:
  enabling GPT-5.4 only for engineering orgs with verified AI tooling maturity, restricting
  Opus-tier models to orgs with approved budget headroom, or running a pilot with a subset of
  organizations before rolling out enterprise-wide.

### Claim 2: The feature gives "fine-grained control beyond enterprise-wide defaults" by creating per-org model access rules

- **Evidence**: Both the changelog "What's new" section and the linked enterprise documentation
  characterize the feature explicitly as extending beyond enterprise-wide defaults.
- **Confidence**: settled (stated in official changelog and documentation)
- **Quote**: "Targeted model rules let you create rules that allow specific Copilot models for
  selected organizations, giving you fine-grained control beyond enterprise-wide defaults."
- **Our assessment**: The framing "beyond enterprise-wide defaults" positions targeted model
  rules as an additive governance capability, not a replacement. Enterprise-wide defaults still
  exist; targeted rules provide exceptions at the organizational level. For Ch05: document the
  layered model — set an enterprise default, then create per-org exceptions where different
  model access is warranted. This maps to a "central guardrails, local exceptions" governance
  pattern.

### Claim 3: Enterprise-wide model availability has two modes — "Enabled" (forced on for all orgs) and "Optional" (each org decides)

- **Evidence**: The "What's improved" section of the changelog enumerates the two modes
  explicitly. The linked enterprise documentation confirms the definitions: "Enabled" = "The
  model is enabled for all organizations in your enterprise." "Optional" = "Organizations can
  choose whether to enable the model."
- **Confidence**: settled (modes stated directly in official changelog and confirmed in documentation)
- **Quote**: "Set each model's availability to Enabled (automatically on for all organizations)
  or Optional (organizations decide whether to enable it)."
- **Our assessment**: The Enabled/Optional distinction is the foundational enterprise governance
  toggle. "Enabled" removes org discretion — all organizations in the enterprise have the model,
  regardless of preference. "Optional" delegates the activation decision to each organization.
  This creates a three-tier model availability taxonomy: (1) model excluded from the enterprise
  pool, (2) model Optional (org chooses), (3) model Enabled (all orgs have it, no opt-out).
  Targeted model rules operate within this framework to create org-specific exceptions. For Ch05:
  teams designing Copilot governance policies should categorize each model in their enterprise
  roster against one of these three states and document the rationale.

### Claim 4: The default model availability management experience has been refreshed to a single-page interface

- **Evidence**: The "What's improved" section of the official changelog describes the UI refresh.
- **Confidence**: settled (UI change stated in official changelog)
- **Quote**: "The default model availability experience has a refreshed interface. From a single
  page, you can: Choose which default Copilot models are available to organizations in your
  enterprise."
- **Our assessment**: This is a UX improvement accompanying the governance capability launch.
  Consolidation to a single page reduces the operational burden for enterprise admins managing
  large numbers of organizations. Not a high-signal claim for guide recommendations, but context
  for the governance workflow. The UI refresh suggests the enterprise model governance surface is
  maturing as a first-class admin concern.

### Claim 5: Targeted model rules are available only for Copilot Business and Copilot Enterprise plans

- **Evidence**: "Who can use this" section of the changelog.
- **Confidence**: settled (plan scope stated directly in official changelog)
- **Quote**: "Customers on Copilot Business and Copilot Enterprise plans can use targeted
  model rules."
- **Our assessment**: Individual plan users (Copilot Free, Pro, Pro+) cannot use targeted
  model rules. This is an enterprise governance feature requiring the paid enterprise tier.
  For Ch05: the guide's enterprise governance content on targeted model rules applies only to
  teams on Business or Enterprise plans. Teams on individual plans have no equivalent
  organizational-level model targeting capability and must rely on the enterprise's default
  availability settings or BYOK for model access variation.

### Claim 6: Organizations under enterprise governance see "Enforced Settings" (locked by enterprise, shield icon) or "Optional Settings" (enterprise permits org-level control)

- **Evidence**: The linked organization-level documentation page describes two status types
  that organization admins see when viewing model settings in a governed enterprise.
- **Confidence**: settled (stated in official GitHub documentation)
- **Quote**: (no direct verbatim quote captured; the documentation described "Enforced Settings"
  with a shield icon for enterprise-locked settings, and "Optional Settings" for enterprise-
  permitted organizational control — see Extraction Notes)
- **Our assessment**: The visibility of enforcement state at the organization level is an
  important governance UX signal. Organization admins can immediately see which model settings
  are locked by enterprise policy (shield icon = cannot change) vs. which they control locally.
  For Ch05: this makes the governance hierarchy transparent to organization admins — they do not
  need to escalate to the enterprise admin to learn which models are available; the UI signals
  it directly. This reduces governance friction while maintaining clear lines of control.

### Claim 7: For "Optional" models, organization admins can set availability to Enabled, Disabled, or leave it Unconfigured (inheriting enterprise default)

- **Evidence**: The linked organization-level documentation describes three choices for
  organization admins when managing "Optional" models.
- **Confidence**: settled (stated in official GitHub documentation)
- **Quote**: (no direct verbatim quote captured; the documentation described three options
  for Optional models: Enabled, Disabled, and Unconfigured — see Extraction Notes)
- **Our assessment**: The three-state option for "Optional" models means org admins have a
  genuine choice: enable, disable, or inherit. The Unconfigured state acts as passive inheritance
  from the enterprise default — if an org does not configure an Optional model, behavior follows
  the enterprise's default treatment. For Ch05: distinguish "Disabled" (explicit org decision to
  exclude a model) from "Unconfigured" (org has not decided — may change if enterprise default
  changes). Governance audits should flag Unconfigured models as requiring a documented decision.

### Claim 8: The targeted model rules configuration path is: AI controls > Copilot > Configure allowed models > Targeted model rules

- **Evidence**: The linked enterprise management documentation describes the navigation path
  and creation workflow steps.
- **Confidence**: settled (stated in official GitHub documentation, subject to preview-phase UI
  changes)
- **Quote**: (no direct verbatim path quote captured; the documentation described navigation
  to "AI controls > Copilot > Configure allowed models" and then the "Targeted model rules"
  section — see Extraction Notes)
- **Our assessment**: The navigation path is the operationally critical claim for enterprise
  admins implementing this feature. For Ch05: include this as the specific configuration
  reference when documenting enterprise Copilot governance setup. Note that the path is
  subject to change as the feature moves from public preview to GA.

## Concrete Artifacts

### Primary Changelog Text (verbatim from May 26, 2026 announcement)

```
Title: Target Copilot models to organizations with model rules
Published: May 26, 2026 (type: Improvement, ~1 minute read)
Source: https://github.blog/changelog/2026-05-26-target-copilot-models-to-organizations-with-model-rules

Opening paragraph:
"Enterprise owners now have granular control over which GitHub Copilot models are
available to each organization. With targeted model rules, you can allow specific
models for specific organizations instead of relying on a single enterprise-wide
setting. This capability is now in public preview."

Second paragraph:
"We've also refreshed the experience for managing default model availability across
your enterprise, making it easier to see and configure which models are available to
your organizations."

What's new:
"Targeted model rules let you create rules that allow specific Copilot models for
selected organizations, giving you fine-grained control beyond enterprise-wide defaults."

What's improved:
"The default model availability experience has a refreshed interface. From a single page,
you can: Choose which default Copilot models are available to organizations in your
enterprise. Set each model's availability to Enabled (automatically on for all
organizations) or Optional (organizations decide whether to enable it)."

Who can use this:
"Customers on Copilot Business and Copilot Enterprise plans can use targeted model rules."

Documentation links:
  "Managing availability of default models"
  → https://docs.github.com/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models
  "Managing default models for your organization"
  → https://docs.github.com/copilot/how-tos/administer-copilot/manage-for-organization/manage-default-models
```

### Enterprise Model Governance Hierarchy (synthesized from changelog + documentation)

```
GitHub Copilot Enterprise Model Governance — Layered Structure (as of May 26, 2026)

LAYER 1 — Enterprise Default Model Pool (enterprise owner)
  For each model in the enterprise pool, set availability mode:
    Enabled  → model is active for ALL organizations (no org action required)
    Optional → each organization individually decides to Enabled/Disabled/Unconfigured

LAYER 2 — Targeted Model Rules (NEW — public preview as of May 26, 2026)
  Enterprise owner creates per-org targeting rules:
    Select target organization(s)
    Select specific models those organizations can access
  Purpose: Fine-grained exceptions beyond enterprise-wide defaults
  Navigation: AI controls > Copilot > Configure allowed models > Targeted model rules

LAYER 3 — Organization-Level Model Control (for "Optional" models)
  Organization admin sees:
    "Enforced Settings" (shield icon) → enterprise-locked, cannot change
    "Optional Settings" → three choices:
      Enabled      → model available to org members
      Disabled     → model unavailable to org members
      Unconfigured → inherit from enterprise default (passive state)
  Configuration path: Profile → Organizations → org Settings →
    Code, planning, and automation → Copilot → Models

LAYER 4 — Admin Policy Enablement (pre-existing)
  Per docs-github-copilot-agent-model-selection.md (issue #171, Claim 5):
    Third-party agent access (Claude, Codex) requires separate admin policy enablement

LAYER 5 — Repository-Level Opt-In (pre-existing)
  Per docs-github-copilot-agent-model-selection.md (issue #171, Claim 6):
    Repo owner must enable agents at repo Settings > Copilot > Cloud agent

LAYER 6 — User Model Selection
  At task initiation, user selects a model from the options permitted by Layers 1-5

Applies to: Copilot Business and Copilot Enterprise only
Status (Layers 2-3): In public preview as of May 26, 2026; subject to change
```

### Targeted Model Rules Creation Workflow (synthesized from documentation)

```
Creating a Targeted Model Rule (enterprise owner):

Navigation path: AI controls > Copilot > Configure allowed models > Targeted model rules

Steps:
1. Access the "Targeted model rules" section
2. Create a new rule
3. Add target organizations (one or more)
4. Add specific models those organizations can access
5. Confirm to create the rule

Effect:
  Selected organizations gain access to the specified models
  (may differ from or extend enterprise-wide defaults)

Source: GitHub documentation — Managing availability of default models
  https://docs.github.com/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models

Status: Public preview — configuration steps may change before GA
```

## Cross-References

- **Corroborates** `docs-github-copilot-agent-model-selection.md` (issue #171, Claims 5–6):
  That April 14, 2026 source documented a two-layer governance model — Copilot subscription
  requirement + admin policy enablement + repo-level opt-in — for accessing third-party cloud
  agents on GitHub. This source (May 26, 2026) adds a new governance layer above those: enterprise-
  level targeted model rules that control which models are available to each organization before
  any admin policy or repo enablement decisions are made. The full governance stack for a
  practitioner accessing a specific model in a GitHub cloud agent is now: (1) enterprise
  model availability via targeted rules (this source), (2) org-level admin policy enablement
  (#171 Claim 5), (3) repository-level opt-in (#171 Claim 6), (4) user model selection at
  task initiation. This extends #171's two-layer governance model to a four-layer stack.

- **Extends** `docs-github-copilot-gpt53codex-base-model.md` (issue #797, Claim 1): That
  May 17, 2026 source established GPT-5.3-Codex as the default base model for all Copilot
  Business/Enterprise organizations. This source (nine days later) adds the mechanism by which
  enterprise owners can differentiate which organizations access GPT-5.3-Codex (or any other
  model) via targeted rules. The two together describe the governance state: GPT-5.3-Codex is
  the B/E enterprise default, but that default can now be modified per organization through
  targeted rules. The LTS guarantee in #797 Claim 2 (GPT-5.3-Codex available through
  February 2027) remains the forward planning horizon for any targeted rule that pins this model.

- **Complements** `docs-github-copilot-byok-vscode.md` (issue #346, Claim 5): That April 22,
  2026 source documented BYOK as a default-on governance gap — Business/Enterprise org members
  can add external provider models to VS Code Chat without admin action unless explicitly
  disabled. This source introduces a parallel governance surface (targeted model rules) that
  governs GitHub-managed Copilot model availability per organization. The contrast: BYOK
  controls external model access (requires opt-out governance — enabled by default, admin must
  disable), while targeted model rules control GitHub-managed model availability (opt-in
  governance — enterprise must explicitly create rules to restrict or target). Enterprise AI
  policies must address both surfaces separately; neither surface governs the other.

- **Complements** `docs-github-copilot-cca-auto-model-selection.md` (issue #745, Claim 2):
  That May 14, 2026 source documented CCA auto routing selecting models based on "system health
  and model performance" signals. This source adds an upstream governance constraint: auto
  routing can only select from models that are available within the organization's targeted model
  rules and enterprise availability settings. The full model selection pipeline for a CCA auto
  task is now: enterprise targeted rules (this source) → org availability settings (this source)
  → CCA auto routing algorithm (#745 Claim 2) → specific model selected. This fills the
  governance layer that was absent from the CCA auto routing analysis.

- **Complements** `docs-github-copilot-cca-cost-efficient-models.md` (issue #818, Claim 2):
  That May 18, 2026 source documented budget-tier models (Claude Haiku 4.5 at 0.33x, GPT-5.4-mini
  at 0.33x) as cost-optimization options for CCA. Targeted model rules determine whether those
  budget-tier models are available to a given organization at all. Enterprise cost management
  strategies that rely on steering teams toward budget-tier models now have a policy lever: make
  only budget-tier models Enabled or Available in targeted rules for cost-sensitive organizations.

- **Contradicts**: None. No existing corpus source claims that enterprise Copilot model
  governance is limited to enterprise-wide settings only, or that per-organization model
  targeting is not possible. No contradiction issue required.

- **Novel**:
  - First source in this corpus to document per-organization model targeting as an enterprise
    Copilot governance primitive. Prior corpus governance sources (agent model selection, BYOK,
    base model defaults) operate at the enterprise-wide or individual-org level; none document
    a mechanism for differentiating model access across organizations within the same enterprise.
  - First documentation of the Enabled/Optional model availability taxonomy as an explicit
    enterprise governance choice with defined semantics.
  - First corpus source to document the three-state org-level model control (Enabled / Disabled
    / Unconfigured) and the "Enforced Settings" / "Optional Settings" visibility indicators that
    organization admins see when governed by an enterprise.

## Guide Impact

### Chapter 05: Team Adoption / Enterprise Governance

- **Targeted model rules as a new governance primitive**: Add coverage of this feature as the
  mechanism for differentiating Copilot model access across organizations within an enterprise.
  The guide should document the six-layer governance stack (enterprise pool → targeted rules →
  org availability settings → admin policies → repo opt-in → user selection) and explain when
  each layer is the appropriate control point. Targeted rules are the right tool when different
  organizational units have different model access requirements — e.g., an experimental org gets
  GPT-5.4 access, a production org stays on GPT-5.3-Codex LTS, a cost-constrained org is
  restricted to budget-tier models only.
- **Enabled vs. Optional as a governance design decision**: Enterprise admins should establish
  a documented policy for which model availability mode they use by default. Recommend mapping
  each model in the enterprise pool to one of three states: (1) Enabled enterprise-wide for
  stable/approved models (e.g., the LTS base model), (2) Optional for experimental or specialty
  models (allows org-level discretion), (3) excluded from the pool for deprecated or non-compliant
  models. This policy should be recorded in governance documentation and reviewed at each major
  model deprecation or launch event.
- **Public preview caution**: Both the changelog and documentation indicate targeted model rules
  and org-level model management are in public preview and subject to change. Teams building
  governance policies around this feature should treat configuration paths and feature semantics
  as potentially evolving. Document which aspects of governance depend on public-preview features
  and schedule re-verification before major deployment milestones.

### Chapter 04: Model Selection and Cost Management

- **Governance-constrained cost optimization**: The budget-tier cost strategies from
  `docs-github-copilot-cca-cost-efficient-models.md` (#818) operate within the bounds set by
  targeted model rules. If enterprise governance restricts organizations to specific models,
  cost optimization must work within that constrained roster. Enterprises that want to enable
  cost optimization patterns should ensure budget-tier models (Haiku 4.5, GPT-5.4-mini) are
  included as Optional or Enabled within targeted rules for cost-conscious organizations.

### Chapter 02: Harness Engineering / Tooling Landscape

- **Model availability as an upstream variable in harness design**: Teams designing harness
  configurations (CLAUDE.md files, CI integrations, model selection policies in scripts) should
  verify that their target models are permitted under the organization's governance settings
  before finalizing configurations. A harness that references a specific model may fail silently
  or explicitly if that model is not permitted by targeted model rules or the enterprise
  availability settings.

## Extraction Notes

1. **Source is short by design**: The changelog is approximately 150 words of primary
   announcement text. The two linked documentation pages were followed per MINER.md §1 and
   provide the depth for Claims 6–8 and the Concrete Artifacts workflow sections.
2. **WebFetch verbatim limitation**: The AI model used by WebFetch declined to reproduce the
   full documentation pages verbatim, providing structured summaries instead. Claims 6, 7,
   and 8 rely on documentation summaries and lack direct character-for-character quotes —
   flagged explicitly in each claim. The Assayer should verify Claims 6–8 against the live
   documentation pages at the URLs in Concrete Artifacts.
3. **Feature is in public preview**: Both the changelog and the linked documentation pages
   note that targeted model rules and org-level default model management are in public preview
   and subject to change. Configuration paths and feature semantics should be verified against
   current documentation before citing.
4. **No specific models named**: The changelog does not enumerate which specific Copilot
   models can be targeted by these rules. The feature appears to work with any model in the
   enterprise's allowed pool, but no specific model list was confirmed in the source.
5. **No contradictions to file**: No existing corpus source claims that per-org model
   targeting is not possible or that enterprise Copilot governance is limited to enterprise-wide
   settings only. No contradiction issue required.
