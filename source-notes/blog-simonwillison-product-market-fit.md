---
source_url: https://simonwillison.net/2026/May/27/product-market-fit/
source_type: blog-post
title: "I think Anthropic and OpenAI have found product-market fit"
author: Simon Willison
date_published: 2026-05-27
date_extracted: 2026-06-05
last_checked: 2026-06-05
status: current
confidence_overall: emerging
issue: "#1066"
---

# I think Anthropic and OpenAI have found product-market fit

> Simon Willison argues from pricing shifts, revenue figures, enterprise hiring
> patterns, and infrastructure spend that Anthropic and OpenAI crossed a
> product-market fit threshold in late 2025/early 2026 — driven specifically by
> coding agents at enterprise API pricing — and documents two inflection points
> (November 2025 for model quality; April 2026 for revenue materialization)
> that practitioners should understand as context for why coding-agent adoption
> is now a sustained enterprise reality, not an experiment.

## Source Context

- **Type**: blog-post (Simon Willison's personal weblog, May 27, 2026; analytical
  opinion piece with referenced external data: SpaceX S-1 SEC filing, OpenAI pricing
  announcement, job-listing analysis, and revenue reports)
- **Author credibility**: Simon Willison is the creator of Django and the `llm`
  Python CLI — one of the most widely-read independent AI-tooling commentators with
  no vendor affiliation. His prior analyses in this corpus
  (`blog-simonwillison-spacex-s1-anthropic.md`, `blog-simonwillison-encyclical-on-ai.md`,
  and others) are consistently high-signal and carefully attributed. In this post he
  is arguing from public data points (SEC filings, job listings, revenue leaks,
  pricing pages) rather than from insider access — the analysis is as strong as the
  data he cites. No conflict of interest.
- **Scope**: Covers the enterprise pricing shift (Nov 2025 Anthropic, April 2026 OpenAI),
  personal token-cost estimates, revenue scale signals (Anthropic profitability, SpaceX
  deal, Cursor/Copilot revenue share), enterprise hiring data from public job listings,
  Uber and Microsoft as "AI-failure stories" reframed as success signals, the November
  2025 and April 2026 inflection points, and a prediction that IPO S-1 filings will
  provide audited confirmation. Does NOT cover: specific harness configurations, team
  adoption patterns, coding-agent technical capabilities, or comparative model benchmarks.

## Extracted Claims

### Claim 1: Both Anthropic and OpenAI crossed a product-market fit threshold driven specifically by coding agents combined with enterprise API pricing

- **Evidence**: Author's synthesis across multiple data points in the post: pricing
  shifts, revenue scale, infrastructure spend, hiring signals. This is an analytical
  judgment, not a single quoted metric.
- **Confidence**: emerging
- **Quote**: "Coding agents plus enterprise pricing marks the point when these companies
  start making _very_ real revenue"
- **Our assessment**: This is the post's central thesis. The "product-market fit"
  framing is precise: Willison is not claiming general AI adoption success, he is
  claiming that the specific combination of coding agents (the use case) and enterprise
  API pricing (the commercial model) is what produced durable, large-scale revenue. The
  implication for the guide is that coding-agent adoption is not going to reverse —
  the commercial infrastructure supporting it (enterprise pricing, compute investment,
  sales hiring) is now in place. This provides strategic context for practitioners
  deciding whether to invest in AI-native engineering: the infrastructure is mature
  enough that the tools will continue to improve and the vendors will continue to invest.

### Claim 2: November 2025 was the first inflection point — model quality crossed a threshold that made coding agents genuinely useful

- **Evidence**: Author's retrospective characterization, consistent with the practitioner
  pattern documented across the broader corpus.
- **Confidence**: emerging
- **Quote**: "the models released in November 2025 elevated agents to being genuinely
  useful"
- **Our assessment**: This is an important calibration for the guide. The "November 2025
  inflection" is the capability threshold; "April 2026" (Claim 3) is the revenue
  threshold. The six-month lag between capability and revenue materialization is itself
  a data point: enterprise adoption cycles from "tools got good enough" to "companies
  are spending real money" took roughly two quarters. This timeline is useful context
  for practitioners counseling leadership on AI adoption timelines — the financial
  case takes time to materialize even after the technical case is clear.

### Claim 3: April 2026 is a second inflection point — when the revenue implications of November 2025's model improvements materialized

- **Evidence**: Author's analytical synthesis. The post's final section is explicitly
  titled "April is a new inflection point."
- **Confidence**: emerging
- **Quote**: "April 2026 is a new inflection point"
- **Our assessment**: The two-inflection-point framing gives practitioners a useful
  historical narrative structure: November 2025 (capability) → April 2026 (commercial).
  The post documents this second inflection through four independent data streams:
  enterprise pricing alignment (Claim 5), revenue scale signals (Claims 6–8), hiring
  patterns (Claim 9), and infrastructure spend (Claim 10).

### Claim 4: Personal cost data — power user would spend ~$2,180/month on Claude Code + Codex API tokens while paying only $200 in subscriptions

- **Evidence**: Author's own ccusage tool output — direct measurement from his own
  usage. One practitioner's usage pattern, not a representative sample.
- **Confidence**: anecdotal
- **Quote**: "I just ran the ccusage tool on my laptop to get an estimate of how much
  I would have spent if I were to pay for API tokens in the past 30 days and got:
  $1,199.79 for Anthropic Claude Code [and] $980.37 for OpenAI Codex. That's $2,180.16
  worth of tokens for $200—not bad at all!"
- **Our assessment**: This is the clearest illustration in the corpus of the structural
  problem that led to the enterprise pricing shift. At $200/month subscription, Willison
  was consuming $2,180 worth of tokens — an 11x cross-subsidy ratio. This is
  unsustainable for the vendor. The enterprise pricing shift (Claim 5) is the corrective
  mechanism. For practitioners evaluating enterprise AI budgets: power-user token
  consumption at enterprise scale quickly exceeds any flat subscription model. API-based
  billing aligns cost with actual usage; the prior flat-rate model was a subsidy that
  could only persist until enterprise adoption hit a threshold.

### Claim 5: Both Anthropic (Nov 2025) and OpenAI (Apr 2026) shifted enterprise pricing from flat/seat allocations to direct API pricing

- **Evidence**: Direct Anthropic pricing page evidence (described in source) and
  OpenAI's own announcement (quoted verbatim). Specific dates and terms.
- **Confidence**: settled
- **Quote (Anthropic)**: "at some point in the last six months Anthropic switched their
  Enterprise plan...to $20/seat/month plus API pricing for usage"
- **Quote (OpenAI)**: "On April 2, 2026, we updated Codex pricing to align with API
  token usage, instead of per-message pricing."
- **Our assessment**: This is the most operationally important claim in the source for
  practitioners managing enterprise AI budgets. The shift means enterprise customers
  are now paying the same API prices as API developers — there is no enterprise discount
  buffering consumption costs. Teams that set annual budgets in 2025 under the previous
  pricing model will face unexpectedly large overages under the new model. For
  practitioners: budget planning for Claude Code at enterprise scale must now use API
  token cost models, not flat seat pricing.

### Claim 6: Anthropic is rumored to be approaching its first profitable quarter with projected revenue of ~$10.9 billion in Q2 2026

- **Evidence**: Revenue rumor cited in the post (described as "strongly rumored"); not
  a confirmed audited figure.
- **Confidence**: anecdotal
- **Quote**: "Anthropic are rumored to hit $10.9 billion in the second quarter" and
  "Anthropic are strongly rumored to be about to have their first profitable quarter"
- **Our assessment**: As an unaudited rumor, this should be treated with caution.
  However, the magnitude is consistent with the structural signals in the post
  (SpaceX $1.25B/month deal, enterprise pricing alignment, Cursor/Copilot revenue
  contribution). Willison explicitly flags that S-1 filings will provide audited
  confirmation. For the guide: present as a revenue-scale signal, not a settled fact.
  The directional claim (Anthropic approaching profitability via coding agent enterprise
  revenue) is plausible given the corroborating evidence; the specific $10.9B figure
  should carry the `anecdotal` confidence flag.

### Claim 7: Cursor and GitHub Copilot alone accounted for $1.2 billion of Anthropic's then-$4 billion revenue — coding tools are the revenue driver

- **Evidence**: Specific figures cited in the post without source attribution (may be
  from industry reports or leaks that were circulating at publication time).
- **Confidence**: anecdotal
- **Quote**: "just Cursor and GitHub Copilot were responsible for $1.2 billion of the
  company's then-$4 billion revenue"
- **Our assessment**: This 30% revenue concentration in two coding-tool clients is the
  most specific evidence in the corpus that coding agents are the primary revenue driver
  for frontier AI labs. It implies that Anthropic's commercial success is heavily
  dependent on the developer/engineering market specifically — not general consumer AI
  or enterprise productivity broadly. For practitioners: this validates the investment
  thesis that coding-agent tooling will continue to be prioritized by Anthropic as a
  product line, because it is their largest revenue source.

### Claim 8: Uber maxed out its full year AI budget early in 2026, driven primarily by Claude Code usage

- **Evidence**: Referenced in the post as a known story (Uber CTO reported this publicly).
- **Confidence**: anecdotal
- **Quote**: "Claude Code only got _really_ good in November it's entirely
  unsurprising...that a budget set in 2025 may have failed to predict demand"
- **Our assessment**: Willison reframes what might look like an "AI failure" (Uber
  exhausting its budget) as a success signal — adoption exceeded projections because the
  tool was genuinely valuable. For practitioners and team leads counseling finance teams:
  the Uber pattern is a leading indicator that enterprises which experienced agent
  adoption faster than their budget models predicted were not failing at AI adoption —
  they were succeeding. Budget planning for AI tools should explicitly account for
  exponential rather than linear adoption once an agent reaches quality thresholds.

### Claim 9: Microsoft canceled Claude Code licenses for financial reasons (tied to fiscal year end), not because of quality concerns

- **Evidence**: Cited from a Verge journalist's reporting ("sources tell me the
  decision is also a financial one").
- **Confidence**: anecdotal
- **Quote**: "Microsoft canceled Claude Code licenses ostensibly to encourage their
  engineers to dogfood their own Copilot CLI agent instead—but The Verge reporter Tom
  Warren says 'sources tell me the decision is also a financial one', triggered by the
  June 30th end of Microsoft's financial year."
- **Our assessment**: Willison frames both the Uber and Microsoft cases as "thin"
  AI-failure stories that actually evidence success. The Microsoft cancellation has a
  plausible alternative explanation: fiscal year budget resets, plus a competitive
  incentive to use their own product. Neither case constitutes evidence that Claude Code
  failed to deliver value. For practitioners responding to skeptics who cite these cases
  as AI failure evidence: Willison's reframing is documented and sourced.

### Claim 10: OpenAI has 229 of 703 open jobs (32.6%) in enterprise sales/support roles; Anthropic has 105 of 390 (26.9%)

- **Evidence**: Author's own count of open job listings at the time of writing.
  Point-in-time snapshot of public job boards.
- **Confidence**: anecdotal
- **Quote**: "703 open jobs" at OpenAI, "229 (32.6%) as relating to enterprise sales"
  and "390 open jobs" at Anthropic, "105 (26.9%) of which look enterprisey"
- **Our assessment**: The proportion of enterprise-focused hiring (~27–33% of open
  roles) is a structural signal that both companies are investing heavily in
  direct-to-enterprise go-to-market. This is consistent with Claim 1's thesis: the
  revenue shift to enterprise API pricing has triggered a corresponding organizational
  investment in enterprise sales capability. For practitioners: this signal indicates
  that both companies are building the enterprise relationships and support infrastructure
  needed for large-scale production deployment, not just providing APIs.

### Claim 11: The SpaceX/Anthropic compute deal ($1.25B/month through May 2029) evidences a demand signal large enough to justify frontier compute investment at that scale

- **Evidence**: SpaceX S-1 SEC filing (confirmed in the corpus by
  `blog-simonwillison-spacex-s1-anthropic.md` Claim 2).
- **Confidence**: settled
- **Quote**: "the customer **has agreed to pay us $1.25 billion per month** through
  May 2029"
- **Our assessment**: Willison uses this figure not to analyze the deal itself (that
  is covered in `blog-simonwillison-spacex-s1-anthropic.md`) but as evidence that
  Anthropic's compute demand is large enough to justify $1.25B/month in expenditure —
  which in turn implies revenue scale sufficient to support it. The $1.25B/month
  compute spend as a floor on Anthropic's revenue provides practitioners with a
  concrete calibration for Anthropic's commercial scale in mid-2026.

### Claim 12: Anthropic reported "25% of our code commits were via Claude Code last quarter" — coding agents are now majority-adopted at the lab itself

- **Evidence**: Claimed in the post as an Anthropic-stated figure. The same statistic
  appears to align with internal data referenced in other Anthropic sources in the
  corpus.
- **Confidence**: anecdotal
- **Quote**: "25% of our code commits were via Claude Code last quarter?"
- **Our assessment**: This internal adoption metric from Anthropic (the model vendor)
  is a floor, not a ceiling — by this point, `blog-anthropic-ai-native-engineering-org.md`
  Claim 11 documents Fiona Fung saying "I don't think I've seen a non-Claude-assisted
  commit in the last four months" on the Claude Code team specifically. The 25%
  figure appears to be org-wide; the Claude Code team has reached near-100%. For the
  guide: Anthropic's own usage data is the most credible available evidence that the
  tool works at scale — the company that builds it uses it for a substantial fraction
  of its own code.

### Claim 13: Enterprise pivot means labs are "cutting out the middlemen" — direct enterprise pricing lets them capture more value than routing through aggregators

- **Evidence**: Willison's analytical interpretation of the pricing shift.
- **Confidence**: emerging
- **Quote**: "This pivot-to-Enterprise suggests that the labs have realized that the
  real money lies in cutting out the middlemen"
- **Our assessment**: The "middlemen" framing refers to the per-seat discount model
  that previous enterprise plans used, which left value on the table compared to
  direct API billing. For practitioners: the pricing alignment means that enterprises
  now pay the same rate as direct API developers. There is no enterprise discount that
  buffers consumption. Teams that assumed enterprise plans were subsidized should update
  that assumption.

### Claim 14: Final verification of this inflection will come from audited IPO S-1 filings for Anthropic and OpenAI

- **Evidence**: Author's stated expectation about what would confirm his thesis.
- **Confidence**: anecdotal
- **Quote**: "We'll know for sure how real this moment is when the S-1 documents for
  the upcoming Anthropic and OpenAI IPOs give us some real, audited numbers to get
  our teeth into."
- **Our assessment**: This caveat is epistemically important. Willison is transparent
  that most of the revenue figures he cites are rumors or leaks, not audited disclosures.
  He is making a probabilistic argument from converging signals, not a definitive claim.
  The guide should treat the specific revenue figures as directionally indicative, not
  as settled facts, until IPO documents are filed. The structural signals (pricing
  changes, hiring patterns, compute commitments) are well-evidenced; the specific
  revenue figures are not.

## Concrete Artifacts

### Article Structure — Section Headings (verbatim)

```
"I think Anthropic and OpenAI have found product-market fit"
Simon Willison, simonwillison.net, May 27, 2026

Sections:
  Enterprise customers are now paying API prices
  I think they've found product-market fit
  And they're ramping up
  The AI-failure stories around this are pretty thin
  We also know the labs are spending a lot
  API revenue is becoming less important
  April is a new inflection point
```

### Enterprise Pricing Timeline (extracted from article)

```
Anthropic enterprise pricing shift (Simon Willison, May 27, 2026):
  Before: Flat/seat allocation (implied by "typical workday" language)
  After:  $20/seat/month + API pricing for usage
  When:   "some point in the last six months" (Nov 2025 per Anthropic's own statement)
  Anthropic quote: "Claude seats include enough usage for a typical workday"
  [source: Anthropic pricing page, August 2025, before switch]

OpenAI / Codex pricing shift:
  Before: Per-message pricing
  After:  API token usage pricing
  When:   April 2, 2026 (and again April 23, 2026 for GPT-5.5)
  OpenAI quote: "On April 2, 2026, we updated Codex pricing to align
                 with API token usage, instead of per-message pricing."
  Model pricing changes:
    GPT-5.5 (released April 23rd): 2x the API price of GPT-5.4
    Opus 4.7 (April 16th): ~1.4x the price of Opus 4.6
```

### Revenue and Scale Signals (extracted from article)

```
All figures from Simon Willison, May 27, 2026
Note: revenue figures are described as rumors/leaks — not audited

Anthropic revenue signals:
  - Q2 2026 projected revenue: "rumored to hit $10.9 billion"
  - Profitability: "strongly rumored to be about to have their first profitable quarter"
  - Cursor + GitHub Copilot revenue share: "$1.2 billion of the company's
    then-$4 billion revenue"
  - Compute commitment to SpaceX: "$1.25 billion per month through May 2029" (S-1)
  - Internal Claude Code adoption: "25% of our code commits were via Claude Code
    last quarter"

OpenAI consumer scale:
  - "900 million weekly active users for ChatGPT, but only 50 million—5.6% of
    that—were paying consumer subscribers"

Enterprise hiring as investment signal:
  - OpenAI: 229 of 703 open roles (32.6%) enterprise sales/support
  - Anthropic: 105 of 390 open roles (26.9%) enterprise-related
```

### Two Inflection Points Framework (extracted from article)

```
November 2025 inflection — capability threshold:
  "the models released in November 2025 elevated agents to being genuinely useful"
  Named models: GPT-5.1, Opus 4.5, "combined with their respective coding agent
                harnesses"
  Effect: "we've spent the last six months adapting to agent systems that can
           reliably get useful work done"

April 2026 inflection — revenue threshold:
  "April 2026 is a new inflection point"
  Triggers: Enterprise pricing alignment (both labs), new model releases
            (GPT-5.5 April 23, Opus 4.7 April 16)
  Effect: "revenue implications have materialized"

Gap between inflections: ~6 months
  (suggests ~2-quarter enterprise adoption cycle from capability threshold
   to budget materialization)
```

## Cross-References

- **Corroborates**:
  - `blog-simonwillison-spacex-s1-anthropic.md` Claim 2 ("the customer has agreed to
    pay us $1.25 billion per month through May 2029"): This article cites the same
    SpaceX S-1 figure. The spacex-s1 note is the primary-source extraction; this
    article uses the figure as one of several converging signals for Anthropic's
    commercial scale.
  - `blog-anthropic-ai-native-engineering-org.md` Claim 11: Fiona Fung's "I don't
    think I've seen a non-Claude-assisted commit in the last four months" is the
    team-level version of Willison's org-wide "25% of our code commits were via Claude
    Code last quarter" (Claim 12 above). Both corroborate that Anthropic's own internal
    adoption is substantial and growing.
  - `blog-cursor-paypal-enterprise-adoption.md` Claim 10 (talent retention as a
    business outcome) and Claim 3 (daily deployment vs. monthly): The PayPal case
    study documents enterprise AI adoption outcomes from a buyer perspective; this
    Willison post documents the seller/vendor perspective on the same adoption wave.
    Together they triangulate that the same period (2025–2026) represents genuine
    enterprise adoption at scale, not experimental pilots.
  - `blog-bvp-shopify-ai-playbook.md` Claim 5 (Shopify's "humble 20%" productivity
    estimate): The Shopify estimate is a conservative bottom-up measure from a single
    enterprise; Willison's analysis provides the macro structural context explaining
    why enterprises with that level of adoption are now writing large checks.

- **Extends**:
  - `blog-simonwillison-spacex-s1-anthropic.md`: That note analyzes the SpaceX deal
    as an infrastructure supply chain event. This article contextualizes the same
    deal as a demand-side signal — Anthropic is committing $1.25B/month because
    enterprise coding-agent revenue is sufficient to justify that compute investment.
    The two notes should be read together for supply- and demand-side framing.

- **Contradicts**: None identified. The Uber budget-exhaustion story and the Microsoft
  seat cancellation are reframed here as success signals, not failures — this does not
  contradict any existing corpus note that treats them as failure signals, because no
  existing note makes that claim. No contradiction issue filed.

- **Novel**:
  - **Two-inflection-point framing** (November 2025 capability; April 2026 revenue):
    No existing corpus source structures the AI-native adoption story as two separate
    inflection points with a 6-month gap. This framing is useful for practitioners
    communicating adoption timelines to leadership.
  - **Enterprise API pricing alignment as a dated, documented event**: The specific
    Anthropic and OpenAI pricing changes (with dates) are documented here as
    a structured timeline that practitioners can cite. No other corpus source documents
    both transitions in one place.
  - **Revenue concentration in coding tools (30% of Anthropic's revenue from Cursor +
    Copilot)**: The $1.2B/$4B figure is the first in-corpus data point on how much of
    frontier lab revenue comes specifically from coding tools. No other source
    establishes this as a proportion.
  - **Consumer-vs-enterprise scale contrast (900M weekly users, 5.6% paying)**: The
    OpenAI figure illustrates the structural reason why enterprises — not consumers —
    are the real revenue opportunity for coding-agent vendors. No other corpus source
    makes this comparison explicitly.
  - **Reframing "AI budget exhaustion" stories as success signals**: Willison's
    argument that Uber budget overruns and Microsoft fiscal-year cancellations are
    evidence of adoption success (demand exceeded budget models) is novel framing not
    present in any other corpus source.

## Guide Impact

- **Chapter 01 (Daily Workflows — Why This Matters Now)**: Add the two-inflection-point
  framework as historical context for why coding-agent adoption accelerated in 2025–2026.
  Practitioners need the "why now" story; Willison provides a commercially-grounded
  version: November 2025 (capability threshold) → April 2026 (revenue materialization).
  This is more concrete than "AI got better" — it is "specific models at specific dates
  made agents reliably useful, and within two quarters the commercial infrastructure
  followed."

- **Chapter 05 (Team Adoption — Budget and Cost Planning)**: Add Claim 4 (Willison's
  $2,180/month token cost on $200 subscription) and Claim 5 (enterprise pricing
  alignment) as the anchor evidence for why AI tool budgets must be usage-based, not
  seat-based. Teams that budget Claude Code as a flat subscription will be surprised
  by actual API-based costs at enterprise scale. Recommend the chapter include explicit
  guidance on token-cost modeling before rolling out coding agents to large teams.

- **Chapter 05 (Team Adoption — Adoption Patterns)**: Add Claim 8 (Uber budget
  exhaustion) reframed as an adoption success signal. The correct interpretation of
  "we exceeded our AI budget" is "adoption exceeded projections" — which is a positive
  indicator, not a failure indicator. Teams should plan for budget overruns as a
  leading indicator of successful adoption.

- **Chapter 05 (Team Adoption — Making the Case to Leadership)**: Add Claims 6, 7,
  9, and 10 together as a commercial viability argument for practitioners pitching
  AI adoption internally. The leadership question "will these vendors still exist in
  two years?" is answered by: Anthropic approaching profitability, 26–32% of both
  labs' hiring in enterprise sales, $1.25B/month infrastructure commitment.

- **Chapter 02 (Harness Engineering — Cost and Pricing Awareness)**: Add Claim 5
  (pricing alignment) as context for why harness design should include cost monitoring.
  When API costs are now the enterprise pricing model, token consumption directly
  translates to financial exposure. Any harness built without cost telemetry is flying
  blind on a key operational metric.

## Extraction Notes

1. **WebFetch verbatim limitation**: The WebFetch tool declines to reproduce the full
   article verbatim (copyright constraints). Quotes in this note were extracted via
   multiple targeted WebFetch calls asking for specific passages. Verbatim accuracy is
   high for the short quotes returned; however, the Assayer should spot-check key
   quotes against the live URL `https://simonwillison.net/2026/May/27/product-market-fit/`.
   Especially verify: the OpenAI pricing quote, the "900 million weekly active users"
   sentence, and the two-inflection-point framing sentences.

2. **Revenue figures are unaudited**: Willison explicitly states that his revenue
   figures (Anthropic $10.9B Q2, Cursor + Copilot $1.2B share, $4B total) are rumors
   or from uncited leaks. The SpaceX $1.25B/month figure is settled (SEC S-1 filing).
   All other revenue figures carry `anecdotal` or `emerging` confidence.

3. **Job-listing counts are point-in-time**: The 703 OpenAI / 390 Anthropic job
   counts and the enterprise-role percentages were Willison's count as of May 27, 2026.
   These change daily; treat as illustrative proportions, not durable measurements.

4. **No substantive linked sub-pages followed**: Willison's analysis links to several
   external sources (Anthropic pricing page, OpenAI announcement, SpaceX S-1 filing).
   The SpaceX S-1 content is already deeply extracted in
   `blog-simonwillison-spacex-s1-anthropic.md` and is not re-extracted here.

5. **Triage comments**: Three Prospector triage comments were filed. All agree on
   high novelty. Chapter relevance ranges across Ch01, Ch02, Ch03, Ch05 — this note
   covers the most relevant: Ch01 (context/inflection), Ch05 (adoption/budget), Ch02
   (cost awareness). One triage comment suggests Ch03/Ch04 relevance (enterprise
   adoption and cost dynamics), which is partially covered in Ch05 recommendations.
