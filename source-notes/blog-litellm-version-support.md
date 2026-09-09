---
source_url: https://docs.litellm.ai/blog/version-support
source_type: blog-post
title: "LiteLLM version support: focusing on the four most recent stable lines"
author: "Yuneng Jiang (Senior SWE @ LiteLLM)"
date_published: 2026-06-20
date_extracted: 2026-09-09
last_checked: 2026-09-09
status: current
confidence_overall: settled
issue: "#1250"
---

# LiteLLM version support: focusing on the four most recent stable lines

> LiteLLM's canonical statement of its rolling release-support window: effective
> June 29, 2026, only the four most recent stable minor lines are actively
> supported, each line covering every patch in it. At ~weekly minor releases that
> is roughly a month of coverage per line, with a provider-recommended operator
> discipline of pinning to a line, taking drop-in patches, and planning line
> moves (release-notes review required) before the line ages out.

## Source Context

- **Type**: blog-post (vendor engineering/operations policy announcement), tagged
  `release`, `support`.
- **Author credibility**: High for *what LiteLLM's support policy is* — the post
  is authored by Yuneng Jiang, Senior SWE at LiteLLM (BerriAI), describing the
  vendor's own release-support window. It is a companion post to the June
  townhall's one-line policy announcement (`blog-litellm-june-townhall-updates.md`
  Claim 11) and is dated the day before it (2026-06-20 vs 2026-06-26), making it
  the first published version of the policy with the operational mechanics.
- **Scope**: Covers (1) the effective date of the four-minor-line support window,
  (2) the definition of a "minor line," (3) the supported set at publish time and
  the EOL boundary, (4) the roll-forward mechanism and per-line coverage math, (5)
  operator guidance (pin/patch vs line-move), (6) exceptions (enterprise extended
  coverage, discretionary high-severity patching), and (7) how to track the moving
  window (release-notes page). Does NOT cover: change management procedure for
  upgrades, the rationale for the weekly minor cadence itself (that is in
  `blog-litellm-may-townhall-updates.md`), or operational runbook detail.

## Extracted Claims

### Claim 1: Starting Monday June 29, 2026, LiteLLM actively supports only the four most recent stable minor lines
- **Evidence**: The post's lede and the "How the rolling window works" section
  both state the policy and the effective date; the date had already passed at
  extraction time (2026-09-09), so the policy was in force.
- **Confidence**: settled
- **Quote**: "Starting Monday, June 29, 2026, LiteLLM will only actively support the four most recent stable minor lines. Here's what's changing and what it means for you."
- **Our assessment**: A concrete, dated vendor policy statement — not marketing.
  The effective date (June 29, 2026) predates extraction, so the claim is a
  retrospective fact about LiteLLM's support posture that an SRE can plan
  against. The June townhall announced the identical policy one week later
  (Claim 11 of that note), confirming this post is the canonical source.

### Claim 2: A "minor line" is a release series written as 1.89.x, covering every patch in it — the supported unit is the line, not individual patch releases
- **Evidence**: Explicit definition of the term with concrete patch examples.
- **Confidence**: settled
- **Quote**: "A minor line is a release series written as 1.89.x, covering every patch in it: 1.89.0, 1.89.1, 1.89.2, and any later ones. We support the four most recent lines and every patch inside each of them."
- **Our assessment**: The definition matters operationally: "support" is granted
  at the minor-line granularity, so staying within a supported line (1.89.0 →
  1.89.1 → 1.89.2) is always safe, and it is the decision variable for pinning
  (see Claim 7). This lines up with the May townhall's versioning scheme, where
  the MINOR bumps weekly and the PATCH carries hotfixes (`blog-litellm-may-townhall-updates.md`
  Claim 1).

### Claim 3: At publish time (June 20, 2026) the supported lines were 1.89.x–1.86.x; everything 1.85.x and earlier had reached end of life and no longer receives active updates
- **Evidence**: Explicit enumeration of the supported set and the EOL boundary.
- **Confidence**: settled
- **Quote**: "Today the four supported lines are 1.89.x, 1.88.x, 1.87.x, and 1.86.x. Everything 1.85.x and earlier has reached end of life and will no longer actively receive updates."
- **Our assessment**: A publish-time snapshot that is operationally informative
  but ages quickly (the set rolls forward — see Claim 4). Its durable value is
  the *example* of how the set looks and the precision that "1.85.x and earlier"
  are EOL. Operators should read this as the shape of the policy, not as a
  long-lived fact; the current set is tracked on the release-notes page (Claim 9).

### Claim 4: The support window rolls forward on each new minor release — when 1.90.x ships, 1.86.x drops out of the supported set
- **Evidence**: Explicit roll-forward example.
- **Confidence**: settled
- **Quote**: "The window rolls forward: when 1.90.x ships, 1.86.x rolls out and the supported set becomes 1.90.x, 1.89.x, 1.88.x, and 1.87.x."
- **Our assessment**: This is the mechanical core of the policy — the supported
  set is a sliding window of four lines, not four fixed "blessed" versions. The
  practical consequence for an SRE running a self-hosted gateway: the oldest line
  you could be on is always the one a new release is about to evict, and there is
  no grace tier for "we're one line back." This is planning input for the upgrade
  cadence in Ch05.

### Claim 5: At ~one new line per week, the window works out to roughly a month of coverage per line
- **Evidence**: The window math stated directly, deriving per-line coverage from
  the ~weekly minor cadence.
- **Confidence**: settled
- **Quote**: "With a new line about every week, that works out to roughly a month of coverage per line."
- **Our assessment**: The key quantitative implication. A line pinned at release
  gets ~4 weeks before it vacates the window, so a self-hosted operator's
  line-move cadence is effectively monthly. The ~weekly cadence matches the May
  townhall's "Minor bumps weekly" release scheme (`blog-litellm-may-townhall-updates.md`
  Claim 1), so this is consistent, derived math rather than a separate promise.

### Claim 6: The maintenance-burden rationale — carrying fixes back to older lines scales with the number of lines kept alive, not the number of fixes made
- **Evidence**: Stated in the "Why we're doing this" section as the justification
  for the window.
- **Confidence**: settled
- **Quote**: "Maintaining older lines means carrying every fix back to keep them all in parity. That overhead grows with the number of lines we keep alive, not the number of fixes we make."
- **Our assessment**: The rationale is the reusable software-lifecycle principle:
  backport-parity cost is multiplicative in the number of maintained lines, so a
  vendor bounding support at N lines is trading coverage breadth for fix quality
  and velocity on the supported set. This matches the June townhall's framing of
  the 4-minor policy as a maintenance-burden management decision
  (`blog-litellm-june-townhall-updates.md` Claim 11). Operators should read this
  as a signal that out-of-window bug reports will not be backported by default.

### Claim 7: The recommended operator posture is to pin to a line and take its patches (drop-in within a line), and to move up a line only after checking the release notes — planning the move before the line ages out
- **Evidence**: Stated verbatim under "What this means for you."
- **Confidence**: settled
- **Quote**: "To stay supported, pin to a line and take its patches, then move up before it ages out. Patching within a line is a drop-in; moving up a line is where you'd check the release notes for changes."
- **Our assessment**: The highest-value operator guidance in the source. The
  drop-in-vs-check distinction is the operational rule: PATCH upgrades within a
  pinned minor line are safe (no release-note review required), while MINOR line
  moves are where behavior can change and need review. Given ~1 month of coverage
  per line (Claim 5), the sequence is: pin a line, take each patch as it lands
  (drop-in), and schedule a reviewed line move before the line exits the window.
  Security fixes land via patches/newer lines (see the host-header backport matrix
  in `failure-litellm-host-header-auth-bypass.md`), so the patch-taking habit is
  also the security-update habit.

### Claim 8: Exceptions exist — enterprise customers can buy longer coverage, and rare high-severity issues may be patched outside the window at LiteLLM's discretion
- **Evidence**: Stated in the same section as the operator guidance.
- **Confidence**: settled
- **Quote**: "Enterprise customers who need longer coverage can reach out, and for rare high-severity issues we'll use our judgment and may patch outside the window."
- **Our assessment**: Honest scoping of the policy's hard edges. For free/OSS
  self-hosted operators it means there is no default backport guarantee beyond the
  window — out-of-window remediation should be assumed unavailable unless it is a
  rare high-severity security issue (or the operator is an enterprise customer).
  This is a conditioning variable for the support cadence the guide recommends,
  not a contradiction of the window itself.

### Claim 9: The release-notes page is the canonical, always-current tracker of the rolling window — the latest stable line plus the three behind it
- **Evidence**: "How to stay current" section pointing to the release notes.
- **Confidence**: settled
- **Quote**: "We update it as new versions ship, so you can see the latest stable line and the three behind it that are still supported."
- **Our assessment**: The operational complement to Claim 3: because the window
  rolls, the publish-time supported-set snapshot goes stale, and the vendor's
  designated source of truth for the current set is the release-notes page. An SRE
  on a self-hosted gateway should treat that page (or an RSS/notification watch on
  it) as the aging-out early-warning signal rather than relying on static policy
  documents.

## Concrete Artifacts

All artifacts verbatim from the source page
(https://docs.litellm.ai/blog/version-support); markdown emphasis markers
stripped, tokens unchanged.

**Supported set and EOL boundary at publish time (verbatim):**
```
Today the four supported lines are 1.89.x, 1.88.x, 1.87.x, and 1.86.x.
Everything 1.85.x and earlier has reached end of life and will no longer
actively receive updates.
```
Attribution: "How the rolling window works" section.

**Roll-forward mechanism and coverage math (verbatim):**
```
The window rolls forward: when 1.90.x ships, 1.86.x rolls out and the
supported set becomes 1.90.x, 1.89.x, 1.88.x, and 1.87.x. With a new line
about every week, that works out to roughly a month of coverage per line.
```
Attribution: "How the rolling window works" section.

**Operator guidance (verbatim):**
```
To stay supported, pin to a line and take its patches, then move up
before it ages out. Patching within a line is a drop-in; moving up a
line is where you'd check the release notes for changes.
```
Attribution: "What this means for you" section.

## Cross-References

- **Corroborates**:
  - `blog-litellm-june-townhall-updates.md` **Claim 11** (LiteLLM will maintain
    only the four most recent stable minor releases, effective June 29) — the
    townhall announced the identical policy with the same effective date; this
    post (dated four days earlier) is the canonical statement the townhall
    summarized. No conflict — this note supplies the mechanics the townhall
    one-liner lacked.
  - `blog-litellm-may-townhall-updates.md` **Claim 11** (security roadmap
    includes defining a support window for prior releases, quoted "Define support
    window for prior releases.") — this post is the delivery of that stated
    roadmap item. The May note flagged the support window as planned; this June
    post makes it concrete and dated.
  - `blog-litellm-may-townhall-updates.md` **Claim 1** (PEP-440/SemVer 2.0
    versioning with "Minor bumps weekly — each scheduled stable release bumps the
    MINOR version, not PATCH") — the support window's ~weekly-cadence math
    (Claim 5 here) operates on exactly that release scheme; the two sources agree
    on the cadence.

- **Contradicts**: None. No material contradiction with the existing corpus, and
  no contradiction issue filed. The one candidate tension is temporal, not
  substantive: the host-header security fix was backported across `v1.84.3`,
  `v1.85.2`, `v1.86.2`, and `v1.83.10-stable.patch.3`
  (`failure-litellm-host-header-auth-bypass.md`, Concrete Artifacts → Version
  ranges) — i.e., across more than four concurrent lines — but that advisory
  predates the June 29 policy effective date, so it describes the pre-policy
  backport posture, not a contradiction of the window. There is also no existing
  source note claiming LiteLLM guarantees out-of-window backports for OSS
  self-hosted operators; Claim 8's scoping (enterprise only; rare high-severity by
  judgment) fills a gap rather than opposing anything.

- **Extends**:
  - `blog-litellm-june-townhall-updates.md` — adds the concrete rolling-window
    mechanics (minor-line definition, supported-set enumeration, roll-forward
    rule, ~1-month per-line coverage, pin/patch vs line-move guidance) that the
    townhall's policy announcement lacked. Together the two notes form
    announcement (townhall) + operational reference (this post), which is exactly
    the split the Prospector flagged.
  - `failure-litellm-host-header-auth-bypass.md` (Concrete Artifacts → Version
    ranges, plus Fix detail A) — that advisory's backport matrix (`v1.84.3`,
    `v1.85.2`, `v1.86.2`, `v1.83.10-stable.patch.3`) is concrete evidence of the
    "carrying every fix back" cost this post says the policy exists to bound, and
    of the security-fix route operators rely on: fixes land in newer lines that
    in-window operators are expected to move up to.
  - `failure-litellm-server-root-path-regression.md` **Claim 7** (users remediate
    by upgrading; fix ships in `v1.81.3.rc.6` or higher) — shows the operator's
    remediation path is riding the vendor's line/ship cadence, which the ~monthly
    support window formalizes: the version-support post explains *how long* an
    operator has to complete that ride per line.
  - `blog-litellm-july-stability-update.md` **Claim 9** (vendor goal to reduce
    "reported regressions from users on an upgrade") — on a ~monthly line-move
    cadence (Claim 5 here), an operator is in the upgrade-regression exposure
    window every move; this motivates the "check the release notes before a line
    move" step and exercising upgrades in staging before aging out.
  - `docs-google-sre-eliminating-toil.md` **Claim 5** (toil taxonomy includes
    "Release Shepherding" — release requests/rollbacks/emergency patches) — the
    ~monthly minor-bump + patch-taking cadence this post implies for self-hosted
    operators is a recurring Release-Shepherding workload; the pin-to-a-line
    discipline is a toil-reduction posture in that category.

- **Novel**: First source note in the corpus to introduce:
  1. **A concrete, vendor-stated rolling release-support window for an OSS LLM
     gateway** — 4 stable minor lines ≈ 1 month of coverage per line at the
     ~weekly cadence, with the roll-forward eviction rule (newest minor ships →
     oldest supported minor drops).
  2. **The drop-in-vs-release-notes rule for gateway upgrades** — PATCH moves
     within a pinned minor line require no review; MINOR line moves do. This is
     the operational upgrade-hygiene distinction the guide's Ch05 upgrade rules
     were missing.
  3. **The vendor-stated maintenance-burden rationale as a cost model** — backport
     parity cost scales with the number of maintained lines, not the number of
     fixes (multiplicative carry-back), which is the justification for bounding
     support at N lines.
  4. **The "pin to a line, take patches, plan line moves before aging out"
     operator posture** for riding a fast-cadence LLM gateway dependency, with the
     release-notes page as the canonical tracker of the moving window.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — gateway dependency lifecycle / upgrade
  cadence)**: This source gives the concrete support-window numbers the June
  townhall note's Ch05 guidance ("version support policy (4 latest stable minors)
  as maintenance-burden management pattern") lacked. Recommend adding: for a
  self-hosted LiteLLM gateway, treat the support window as 4 stable minor lines ≈
  1 month of coverage per line; **pin to a line and take every PATCH within it
  (drop-in, no release-note review); budget a MINOR line bump roughly monthly,
  with release-notes review, scheduled before the pinned line exits the window**.
  Because security fixes land in newer lines/patches (see host-header backport
  matrix and the server-root-path upgrade remediation), the patch-taking and
  line-move cadence doubles as the security-update cadence — flag upgrade urgency
  rather than waiting for the aging-out deadline. This pairs with the existing
  Ch05 guidance that rollback must be exercised: a monthly line-move cadence makes
  the rollback path a routine, exercised operation rather than a rare one.

- **Chapter 04 (Oncall / Toil)**: Add the ~monthly minor-line bump + continuous
  patch-taking on a ~weekly-release gateway as a concrete instance of Release
  Shepherding toil (`docs-google-sre-eliminating-toil.md` Claim 5). Recommend
  treating release-note review as a scheduled, rubric-able activity
  (applies to multi-gateway fleets where each gateway must ride the same window).

- **Chapter 03 (Runbooks and Agents)**: Add the "line move" procedure as a
  runbook step distinct from "patch": patch = drop-in apply within the pinned
  line; line move = release-notes review + staged rollout + exercise rollback
  before the window evicts the old line. The release-notes page is the canonical
  tracker to watch for the aging-out signal.

## Extraction Notes

- Source read in full via WebFetch of `https://docs.litellm.ai/blog/version-support`
  (Docusaurus blog post, published June 20, 2026, by Yuneng Jiang, Senior SWE @
  LiteLLM). The post is short and self-contained (four short sections); no
  substantive sub-pages were linked from the main content — the release-notes
  link is the tracker named by the post itself, not additional content to extract.
- All quoted passages copied character-for-character from the rendered page text.
  Markdown bold markers (`**1.89.x**`) were removed from two quoted passages
  (Claims 3 and 4 / the Concrete Artifacts block, which contain them in the
  source) without altering text tokens — the same formatting-normalization
  convention used in sibling LiteLLM notes.
- `confidence_overall` set to `settled`: the policy effective date (June 29,
  2026) had already passed at extraction time (2026-09-09), so the core claims
  (window in effect, supported-set mechanics, operator guidance) are retrospective
  vendor facts rather than forward-looking promises. The only aging component is
  the publish-time supported-set snapshot (Claim 3), which is explicitly treated
  as a dated example in the note and in the claim's assessment; the rolling
  mechanics themselves are the durable content.
- `miner-related-notes.md` candidates read before writing Cross-References; all 10
  evaluated — cited 1, dismissed 9:
  - `docs-google-sre-eliminating-toil.md` — cited (Extends, Claim 5, Release
    Shepherding toil).
  - `blog-litellm-auto-router-v2.md` — routing-configuration post, no release/
    support-window overlap. Dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server, unrelated to gateway
    version support. Dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent spectrum/guardrails,
    unrelated. Dismissed.
  - `docs-google-sre-data-processing-pipelines.md` — pipeline SLOs, unrelated.
    Dismissed.
  - `docs-google-sre-reliable-product-launches.md` — launch-coordination
    engineering, unrelated to a release-support window. Dismissed.
  - `docs-langfuse-evaluation-core-concepts.md` — evaluation concepts, unrelated.
    Dismissed.
  - `docs-langfuse-security-and-guardrails.md` — guardrail stacks, unrelated.
    Dismissed.
  - `blog-litellm-save-claude-code-costs.md` — cost-cutting features, unrelated.
    Dismissed.
  - `blog-litellm-valkey-semantic-caching.md` — semantic caching, unrelated.
    Dismissed.
  Additional cross-references (June/May townhall notes, July stability note, the
  two LiteLLM failure notes) were discovered from the Prospector's overlap list
  and by reading `source-notes/` directly; every cited claim number was verified
  against the cited note per §4b before writing.
- No contradiction issue filed: verified against CONTRADICTIONS.md (no open
  entries) and all existing source notes per §4a. The host-header backport matrix
  predates the policy's effective date (a before-state, not an opposition), and no
  source claims default out-of-window backports for OSS self-hosted operators — so
  this source fills a gap rather than opposing any existing claim.