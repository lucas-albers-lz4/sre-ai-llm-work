---
source_url: https://lucumr.pocoo.org/2026/6/10/gaslighting/
source_type: blog-post
title: "Gaslighting Openness"
author: Armin Ronacher
date_published: 2026-06-10
date_extracted: 2026-06-11
last_checked: 2026-06-11
status: current
confidence_overall: anecdotal
issue: "#1143"
---

# Gaslighting Openness

> Armin Ronacher argues that large tech companies — Apple and Anthropic named
> specifically — use "safety" and "security" language as narrative cover for
> restricting user and developer access to technology and AI models, and that
> practitioners (especially Europeans) should resist accepting this narrative
> uncritically and prioritize keeping access gates open.

## Source Context

- **Type**: blog-post (lucumr.pocoo.org personal blog; ~350 words; four paragraphs;
  opinion/political commentary; published 2026-06-10)
- **Author credibility**: Armin Ronacher is the creator of Flask, Jinja2, Click, and
  Sentry, and the author of the Pi coding agent. His blog is a designated `trusted-feed`
  source in this repo. He is a long-time Open Source advocate who uses AI tools daily
  while critically analyzing their ecosystem effects. This post is political/normative
  commentary, not a practitioner implementation analysis. Claims carry anecdotal
  confidence; no controlled evidence, metrics, or failure-mode data are presented.
  Ronacher discloses no AI assistance in writing this post.
- **Scope**: Covers the narrative politics of AI access restrictions; Apple's EU DMA
  dispute; Anthropic's restrictions on Mythos and Fable; the ethical asymmetry of
  training on public works but blocking distillation; democratized access as a first
  principle; and the structural disadvantages European practitioners face. Does NOT
  cover: specific technical implementations of any safety system, operational
  patterns for teams, or evidence-based measurement of the harms described. This is
  an opinion post, not a practitioner methodology post.

## Extracted Claims

### Claim 1: Large tech companies frame access restrictions as safety or security — this is narrative manipulation, not a primary technical or ethical concern

- **Evidence**: Ronacher's practitioner observation of the discourse across social media
  and business circles. Examples named: Apple's DMA fight; Anthropic's restrictions on
  Mythos/Fable. The characterization is normative — he argues intent, not just effect.
- **Confidence**: anecdotal (single practitioner's reading of industry behavior; no
  internal documents or stated corporate motivations cited)
- **Quote**: "A lot of that battle today is manipulation of the narrative. Opinion makers
  on social media and in business circles increasingly frame access as irresponsibility."
- **Our assessment**: This is a strong claim about corporate intent — framing the
  safety narrative as a rhetorical strategy rather than a genuine concern. Ronacher
  does not argue that all safety restrictions are fake ("Some restrictions may be
  defensible"), but that the narrative framing systematically overstates the safety
  rationale to mask commercial motivations. The claim is impossible to verify from
  public sources, but as a practitioner reading of industry messaging, it is consistent
  with the observable pattern: safety language tends to appear most prominently when
  access restrictions have obvious commercial benefits for the restricting party. For
  teams evaluating vendor safety documentation: this is a prompt to ask which
  restrictions serve the vendor and which serve the user.

### Claim 2: Apple's fight over delayed AI features in Europe is about user device/data access control, not European regulatory overreach

- **Evidence**: Ronacher's characterization of the Apple DMA dispute as a control battle
  rather than a technical/regulatory problem.
- **Confidence**: anecdotal (practitioner framing of a public dispute; no access to
  internal Apple documentation)
- **Quote**: "Apple's fight over delayed AI features in Europe is not about Brussels
  being annoying: it is about whether users can access their own devices and data.
  The phone is yours, the data is yours, yet Apple decides who may reach it and takes
  the agency away from you and then tries to make that sound like it is in your
  interest (supposedly it's for your safety and security)."
- **Our assessment**: Ronacher's framing reframes what is often discussed as a
  regulatory-compliance complaint into a user-agency complaint. The argument: Apple is
  not complying with the DMA because compliance would give users (and competitors) access
  that Apple currently controls. The safety/security framing is the cover story. For
  practitioners building on Apple's platform or advising on platform choices: the DMA
  dispute is partly about whether Apple intelligence features can be competed with or
  audited. Whether you buy Ronacher's full characterization, the underlying tension —
  platform owner control vs. user/developer access — is a genuine dynamic in the AI
  tooling ecosystem.

### Claim 3: Anthropic has financial incentives to restrict Mythos and Fable access and wraps those restrictions in safety and national security language

- **Evidence**: Ronacher's practitioner assessment of Anthropic's behavior. Mythos and
  Fable are Anthropic's most capable models; Anthropic has restricted access to them
  through selective preview programs (corroborated by the Firefox/Mythos source note's
  description of restricted access). The "national security" characterization references
  Anthropic's public positioning around export controls and dual-use risks.
- **Confidence**: anecdotal (practitioner characterization of corporate motivation;
  Anthropic has not publicly stated that safety/security framing is rhetorical cover)
- **Quote**: "Anthropic has every financial incentive to restrict what people can do
  with Mythos and Fable, and they wrap those restrictions in safety and (national)
  security language. Some restrictions may be defensible, but not all of them are."
- **Our assessment**: The concession "some restrictions may be defensible" is important —
  Ronacher is not arguing all safety restrictions are illegitimate. He is arguing that
  the framing systematically overstates safety concerns to normalize commercial access
  control. This is directly relevant to teams making vendor selection decisions: a model
  available only to vetted preview partners or enterprise contracts represents a
  different risk profile (vendor lock-in, discontinuation risk, pricing leverage) than
  a model available through standard API access. The safety framing should not obscure
  the access dynamics.

### Claim 4: Training AI models on public works while blocking open-source distillation is ethically inconsistent

- **Evidence**: Ronacher's normative argument about the asymmetry between what AI
  companies take from the commons (training data from public works) and what they
  give back (blocking distillation and open-source learning from those models).
- **Confidence**: anecdotal (normative argument; accurate as a description of current
  industry practice — most frontier labs do train on public web data and most do not
  release weights or allow distillation)
- **Quote**: "They trained their models on public works, then block Open Source
  attempts to learn from and distill these systems."
- **Our assessment**: This is the most specific and verifiable claim in the post.
  Anthropic (like other frontier labs) has trained on large web corpora including
  open-source code and public writing; Anthropic has not released model weights for
  any of its frontier models; and Anthropic's terms of service restrict using model
  output to train competing models (the distillation restriction). Ronacher frames
  this as an asymmetry: the company benefits from the commons and then closes the
  commons behind it. Whether one agrees with Ronacher's normative conclusion, the
  asymmetry itself is accurate. For practitioners evaluating vendor ethics alongside
  capability: the training-data/distillation asymmetry is a real and unresolved
  question in AI licensing, not a fringe concern.

### Claim 5: Democratized access to technology, including AI, is in everyone's interest — including practitioners who dislike the EU or other regulatory actors

- **Evidence**: Ronacher's principled argument separating the messenger (EU regulation,
  which he says many including himself reflexively dislike) from the substance (user
  access rights).
- **Confidence**: anecdotal (normative argument; widely contested in business and policy
  circles; stated without empirical support)
- **Quote**: "Disliking the EU, China, or any other large government should not make us
  forget that true democratized access to technology including AI is in all our interest."
- **Our assessment**: This is the post's core normative claim. The argument: access
  restrictions harm practitioners even when the restrictions come from actors whose
  safety/security motivations might otherwise seem credible. The DMA framing is the
  vehicle — even those who dislike EU regulation should support the underlying access
  principle. For teams: this is a values-level claim, not a technical recommendation.
  Its guide relevance is in framing how teams evaluate vendor messaging about access
  restrictions — asking "who benefits from this restriction?" is a legitimate question
  regardless of whether the stated rationale sounds reasonable.

### Claim 6: European practitioners face structural disadvantages that make open AI access particularly important

- **Evidence**: Ronacher's characterization of the European technology ecosystem. The
  "brain drain" and capital markets claims are well-documented in European tech policy
  discourse; the "internal fighting" characterization is more editorial.
- **Confidence**: anecdotal (accurate characterization of structural disadvantages
  commonly cited in European tech policy; stated without sources)
- **Quote**: "We should not let companies own the narrative that preventing access is
  in our interest, particularly not as Europeans where the odds are already stacked
  against us by our underdeveloped capital markets, brain drain and internal fighting."
- **Our assessment**: The "particularly as Europeans" framing adds a practitioner-specific
  angle that is relevant for European teams evaluating US-headquartered AI vendor lock-in.
  The structural disadvantages Ronacher names are real: European venture capital is less
  developed than US/Asian equivalents; senior ML talent does migrate to US labs; EU member
  state policy fragmentation creates inconsistency. In this context, restrictions on AI
  access compound existing disadvantages — European practitioners who cannot access frontier
  models cannot build competitive products, train competing teams, or contribute to the
  open ecosystem. This is a real asymmetry, not just rhetorical framing.

### Claim 7: Some temporary product pain from keeping AI access gates open is worth accepting if it preserves long-term access

- **Evidence**: Ronacher's normative argument applied to the Apple AI feature delay in Europe.
  He explicitly says "I am willing" to accept this pain (inferred; he says "will be worth
  paying").
- **Confidence**: anecdotal (normative/values judgment)
- **Quote**: "Some temporary product pain, including delayed Apple AI features, will be
  worth paying if it keeps gates open."
- **Our assessment**: This is a direct trade-off claim: short-term product capability
  loss (delayed features) vs. long-term access rights (DMA enforcement). Ronacher comes
  down on the long-term access side. For teams: this maps to the vendor lock-in trade-off
  discussion in tool adoption decisions. Choosing a more open (but possibly less capable)
  AI tool today may preserve flexibility and negotiating leverage in ways that a locked-in
  frontier tool does not. Ronacher doesn't develop this into a team practice, but the
  trade-off framing is directly applicable to enterprise vendor selection.

## Concrete Artifacts

No code examples, configuration files, metrics, or operational procedures appear in this
post. The source is pure opinion commentary.

```
Source: Armin Ronacher, https://lucumr.pocoo.org/2026/6/10/gaslighting/ (2026-06-10)

The post's argument structure (four paragraphs):
  Para 1: Open source under stress — AI slop, contributor dynamics, cost of code,
          companies closing doors behind them.
  Para 2: Battle is about narrative — EU DMA as access rights mechanism; Apple's DMA
          fight is about device/data control rebranded as safety.
  Para 3: Anthropic named specifically — financial incentives + safety/security framing;
          training on public works while blocking distillation.
  Para 4: Normative conclusion — democratized access is in everyone's interest; accept
          temporary product pain; Europeans especially should resist the narrative.

No appendices, linked sub-pages, or substantive external links in the post.
```

## Cross-References

- **Corroborates**: `blog-ronacher-local-models-focus-polish.md` Claim 14 — "The local
  model vision is explicitly framed as an alternative to hyperscaler lock-in, where tools
  'locked behind a subscription in a data center in another country' do not qualify as
  truly local." Quote from that note: "a hammer that's locked behind a subscription in a
  data center in another country does not qualify." Ronacher's "Gaslighting Openness" post
  is the political theory behind the local-models engineering practice: the reason he cares
  about fully-local inference is the same reason he criticizes Anthropic's access
  restrictions — subscription-gated, vendor-controlled access is not genuine access.
  The current post makes the values claim explicit; the local-models post implements it.

- **Extends**: `blog-ronacher-communities-of-not.md` Claim 4 — "LLMs appear in developer
  work environments (editors, issue trackers, hiring, management pressure, code reviews)
  whether individual developers opted in or not." Quote from that note: "For us developers,
  LLMs show up in editors, issue trackers, hiring conversations, management pressure and
  code reviews whether we asked for them or not." The communities-of-not post describes
  AI as imposed on individual developers from below (organizational and environmental
  pressure). The current post describes AI access being restricted from above (corporate
  and regulatory gatekeeping). Together they frame practitioners as squeezed from both
  directions: imposed exposure without choice on one side, restricted access without
  recourse on the other.

- **Extends**: `blog-ronacher-pi-oss.md` Claim 12 — "AI makes local workarounds cheap,
  discouraging the upstream collaboration that improves shared infrastructure for everyone."
  Quote from that note: "Instead of humans talking to humans about where a fix belongs,
  one human and one machine work around the problem in isolation." The pi-oss post
  documents the micro-level dynamics where AI makes open-source collaboration less
  economically rational. The current post argues the same asymmetry at the macro level:
  AI companies benefit commercially from the open-source commons (public training data)
  while their restrictions reduce what flows back to that commons (no distillation, no
  weight releases). Both document the same basic extraction dynamic — the AI ecosystem
  takes from shared resources without equivalent contribution back.

- **Extends**: `blog-ronacher-content-for-contents-sake.md` — Same author; this post is
  Ronacher's most explicitly political piece in the corpus. His prior posts addressed
  internal AI ecosystem dynamics (vocabulary inflation, content flooding, OSS maintenance
  pressure). This post addresses the external governance dynamics (who controls access,
  who benefits from restrictions). Together they trace a coherent practitioner critique:
  AI adoption degrades internal collaboration norms (content-for-contents-sake,
  communities-of-not, pi-oss) while corporate actors capture the economic upside and
  restrict access back to practitioners (gaslighting-openness, local-models).

- **Contextualizes**: `blog-simonwillison-firefox-claude-mythos.md` — The Firefox/Mythos
  post documents Claude Mythos Preview being used for Firefox security hardening through
  a selective preview program — exactly the kind of restricted, vetted access Ronacher
  critiques. The Firefox note shows Mythos access as high-value (271 security fixes) and
  restricted (preview program, not general availability). These two posts are not
  contradictory; they describe the same access-restriction pattern from different vantage
  points: Ronacher criticizes the restriction pattern; the Firefox note shows what that
  restricted access enables. The tension is real — preview access can produce genuine
  value while still representing a restriction on broader access. No contradiction filed;
  these are two angles on the same dynamic.

- **Contradicts**: None identified. No existing corpus note makes claims that would lead
  to directly opposing guide advice on vendor access narratives or democratized AI access.
  Anthropic-authored source notes document their own safety and containment practices but
  do not make claims about whether those practices are rhetorically motivated — the
  Anthropic notes and Ronacher's critique operate at different levels. No contradiction
  issue filed.

- **Novel**:
  - **Corporate "safety as narrative cover" critique from a trusted practitioner**:
    No other corpus source presents a critical analysis of how safety language functions
    as a commercial access-restriction strategy. Other corpus notes accept safety framing
    at face value or focus on technical safety implementations. This is the first corpus
    source to argue that the safety framing itself warrants skepticism.
  - **Distillation asymmetry as ethical/licensing concern**: No other corpus source names
    the training-on-public-works/blocking-distillation asymmetry as a practitioner concern
    relevant to vendor evaluation. The claim exists in AI policy debates but has not
    appeared in the guide corpus as a practitioner-level consideration.
  - **EU DMA as user-access mechanism (not just compliance burden)**: Other corpus sources
    treat EU regulation as compliance context. Ronacher's framing — DMA as a mechanism
    for users to access their own devices and data — is a novel frame for the regulatory
    context.
  - **European structural disadvantage in AI access**: No other corpus source discusses
    the asymmetric consequences of AI access restrictions for European practitioners
    specifically, given capital market, talent, and fragmentation disadvantages.

## Guide Impact

- **Chapter 00 (Principles — Vendor Evaluation)**: Add a lens for evaluating vendor safety
  and security claims: ask whether the restriction primarily benefits the user or the
  vendor. Ronacher's Claim 1 and Claim 3 together justify adding this question to any
  vendor evaluation framework. A safety claim that coincides with a commercial benefit
  (protecting model access, preventing competitive distillation) warrants more scrutiny than
  one that does not.

- **Chapter 03 (Models & Licensing — Evaluating Model Access)**: The access-restriction
  pattern Ronacher describes is directly relevant to model selection guidance. If the guide
  advises on frontier model evaluation, it should include: (a) what access restrictions
  exist (preview programs, rate limits, distillation prohibitions), (b) what commercial
  interests those restrictions serve, and (c) what the practitioner's exit options are if
  access changes. Claim 4 (training/distillation asymmetry) is worth documenting as a
  known unresolved tension in AI vendor licensing.

- **Chapter 03 (Models & Licensing — Open vs. Closed Models)**: Claim 5 (democratized
  access is in everyone's interest) and the local-models cross-reference together support
  a framing where open model access is not just an ideological preference but a
  practitioner risk management strategy. The trade-off in Claim 7 (temporary pain for
  long-term access) maps to the concrete decision between a more capable but access-
  restricted frontier model and a less capable but openly accessible alternative.

- **Chapter 04 (Organizations — European Teams)**: If the guide has regional coverage,
  Claim 6 is specifically relevant to European practitioners. The structural disadvantages
  named (capital markets, brain drain, fragmentation) compound the access-restriction risk
  Ronacher describes. European teams should weight vendor lock-in and access restrictions
  more heavily in their vendor selection criteria than US-based counterparts who face
  fewer structural disadvantages.

## Extraction Notes

- Full post text fetched from https://lucumr.pocoo.org/2026/6/10/gaslighting/ via
  WebFetch. The post is approximately 350 words and four paragraphs with no sub-pages,
  linked resources, or embedded artifacts. All quotes verified character-for-character
  against the fetched content.
- The source is pure political opinion commentary. There are no code examples, metrics,
  configuration artifacts, or failure-mode data to extract. This is consistent with the
  Prospector's second triage assessment: "primarily opinion/critique rather than
  evidence-based analysis" and "does not provide concrete patterns or artifacts for teams
  to adopt."
- Confidence rated anecdotal overall: every claim is normative or based on Ronacher's
  practitioner reading of corporate behavior. No quantitative data, failure reports, or
  independent verifications are present.
- The Prospector's first triage comment rates novelty as "high" and names Ch02 and Ch03
  as primary targets. The second triage comment rates novelty as "medium" and names Ch00
  and Ch03. This extraction adopts the more conservative novelty rating from the second
  triage and aligns the guide impact with Ch00/Ch03 rather than Ch02.
- No sub-pages followed (the post contains no links to related pages; it has one external
  reference implicit in the Apple/EU DMA context but no linked supporting sources).
- Cross-references verified: all Claim N citations were confirmed against the referenced
  source notes character-for-character before writing this note.
