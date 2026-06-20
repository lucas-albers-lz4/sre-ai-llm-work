---
source_url: https://simonwillison.net/2026/Jun/4/ai-enthusiasts-ai-skeptics/
source_type: blog-post
title: "AI enthusiasts are in a race against time, AI skeptics are in a race against entropy"
author: Charity Majors (excerpted by Simon Willison)
date_published: 2026-06-04
date_extracted: 2026-06-13
last_checked: 2026-06-13
status: current
confidence_overall: emerging
issue: "#1167"
---

# AI Enthusiasts Are in a Race Against Time, AI Skeptics Are in a Race Against Entropy

> Charity Majors (excerpted by Simon Willison) names a structural organizational gap that
> explains why internal AI adoption debates often stalemate: both enthusiasts and skeptics
> face real, existential threats, but there is no natural feedback loop connecting them —
> and resolving the tension requires designing one.

## Source Context

- **Type**: blog-post (Simon Willison link-blog excerpt, June 4, 2026). Willison excerpts
  three blockquotes from Charity Majors' Substack post at
  https://charitydotwtf.substack.com/p/ai-enthusiasts-are-in-a-race-against and adds brief
  editorial framing. The Substack post returned HTTP 403 Forbidden when directly fetched —
  the Willison page is the only accessible version of this content. All quoted passages
  below are verified verbatim from the Willison page. Tags on the Willison post: ai,
  charity-majors, agentic-engineering.
- **Author credibility**: Charity Majors is co-founder and CTO of Honeycomb (the
  observability platform for distributed systems) and co-author of *Database Reliability
  Engineering* (O'Reilly). Her entire career has been spent building systems that observe
  and maintain reliability at scale, and she has direct first-hand experience with on-call
  rotations and institutional knowledge degradation. The Prospector triage notes: "Charity
  Majors is a recognized expert in observability and engineering culture; her framing of
  the enthusiast/skeptic dynamic as a *leadership problem*, not a technical one, is
  substantive and grounded in real team experience." Simon Willison is the creator of
  Django and one of the highest-signal independent AI tooling commentators; his selection
  of this piece for his curated feed is itself a relevance signal.
- **Scope**: The accessible content (three blockquotes and Willison's brief framing)
  covers the conceptual diagnosis of the enthusiast/skeptic organizational tension and
  names the goal of feedback-loop design. The Majors Substack post almost certainly
  contains more detail on specific recommendations — this extraction is limited to what
  Willison chose to excerpt. Does NOT cover (from accessible content): specific
  organizational structures, concrete feedback loop designs, tool configurations, or
  empirical data from any specific team.

## Extracted Claims

### Claim 1: AI enthusiasts are not wrong — teams that lean in hard are seeing real, non-imaginary, discontinuous capability leaps

- **Evidence**: Charity Majors' own framing, excerpted by Willison. Majors explicitly
  rejects the framing that enthusiasts are mistaken or overselling. She grounds the
  enthusiast position in direct team observation, not hype.
- **Confidence**: emerging (Majors is an authority in engineering culture; the claim is
  consistent with multiple corpus sources reporting real productivity gains, but no
  controlled evidence is cited)
- **Quote**: "The enthusiasts are _not wrong_. We are starting to see real, non-imaginary,
  discontinuous leaps in capabilities from teams that lean in hard to working with AI."
- **Our assessment**: Majors' framing "real, non-imaginary, discontinuous" is carefully
  chosen — she is distinguishing this from hype-cycle exaggeration and from incremental
  improvements. "Discontinuous" is the key word: this is not a linear capability
  improvement where the skeptic strategy of "wait and see" is safe. This corroborates the
  corpus pattern of genuine velocity gains reported by Anthropic's org, Shopify, and
  others — but coming from an author whose skeptic credentials make the endorsement more
  valuable than from a pure enthusiast.

### Claim 2: The current AI adoption cycle is different from normal technology cycles — waiting while competitors adopt creates an existential competitive risk

- **Evidence**: Majors' explicit framing embedded in the enthusiast position, contrasting
  AI adoption with normal technology cycles.
- **Confidence**: emerging (single-author assertion; the "existential threat" framing is
  argued but not quantified; directionally consistent with competitive dynamics observed
  in corpus but not independently verified)
- **Quote**: "this does not feel like a normal technology cycle where you can wait for the
  dust to settle; teams that sit this out while competitors are hustling could be out of
  business before the dust settles. That's a real, existential threat."
- **Our assessment**: The "not a normal technology cycle" claim is the load-bearing premise
  for the enthusiast urgency position. If it were a normal cycle, the skeptics' "wait and
  see" strategy would be rational — let the early adopters bear the integration risk and
  adopt the proven patterns later. Majors argues this window does not exist here: the
  competitive disadvantage of waiting may compound faster than the technical risk of
  adopting. This is a contested empirical claim, not a settled one — but it directly
  motivates why enthusiasts experience their position as urgent rather than merely
  preferential.

### Claim 3: AI skeptics are also not wrong — shipping code faster than engineers can read it depletes institutional trust and creates systems nobody understands

- **Evidence**: Charity Majors' own framing, excerpted by Willison. Majors explicitly
  validates the skeptic position with the same "not wrong" framing she applied to
  enthusiasts. She uses a specific economic metaphor ("trust account") and names four
  concrete consequences.
- **Confidence**: emerging (Majors is an authority specifically in reliability and
  institutional knowledge dynamics; the "trust account" model is conceptually coherent;
  the named consequences are consistent with operational experience but not measured here)
- **Quote**: "The skeptics are also _not wrong_. When you ship code faster than engineers
  can read it, in domains where nobody has full context, you are making withdrawals from a
  trust account that took years to build. Reliability degrades, institutional knowledge
  evaporates. You end up with systems nobody understands, products burbling into
  incoherence, and on-call rotations that grind people up and spit them out. That is ALSO
  a real existential threat."
- **Our assessment**: This is the most substantive single passage in the accessible
  content. Majors names four specific skeptic concerns: (1) reliability degradation,
  (2) institutional knowledge evaporation, (3) incomprehensible systems, (4) on-call
  rotation burnout. The "trust account" metaphor is precise — institutional reliability is
  not a one-time property but an accumulated investment that can be depleted faster than
  it was built. Crucially, Majors frames this as "ALSO a real, existential threat" —
  placing it on equal ontological footing with the competitive threat enthusiasts face.
  No prior corpus source makes both threats explicit and equal in the same statement.

### Claim 4: Velocity without comprehension is the specific failure mode — the problem is code shipped faster than engineers can read it

- **Evidence**: Embedded in the Claim 3 quote. Majors identifies the precise mechanism:
  not AI code generation per se, but generation that outpaces human reading capacity.
- **Confidence**: emerging (logical framing from an expert in reliability; consistent with
  corpus evidence from Shore's maintenance cost analysis and the broader "verification
  bottleneck" finding)
- **Quote**: "When you ship code faster than engineers can read it, in domains where nobody
  has full context, you are making withdrawals from a trust account that took years to
  build."
- **Our assessment**: The operative phrase is "faster than engineers can read it" — this
  is a velocity-to-comprehension ratio, not an absolute velocity limit. The skeptic
  position is not "AI generation is bad" but "AI generation that outpaces comprehension is
  dangerous." This is a calibration-friendly framing: the acceptable velocity is
  determined by the team's comprehension bandwidth, not a fixed threshold. This connects
  directly to the bottleneck shift finding in the corpus (Fung, Osmani, Shopify) — the
  reason verification and code review have become the new bottleneck is precisely that
  generation has exceeded comprehension bandwidth. The skeptics' concern is validated by
  the enthusiast teams' own operational findings.

### Claim 5: There is no natural feedback loop connecting enthusiasts with skeptics

- **Evidence**: Majors' explicit structural diagnosis, excerpted by Willison as the
  "key issue."
- **Confidence**: emerging (a conceptual claim about organizational dynamics; not
  empirically measured but named by a practitioner with direct experience in engineering
  culture)
- **Quote**: "There is no natural feedback loop connecting enthusiasts with skeptics."
- **Our assessment**: This is the central claim of the piece. Majors is not arguing that
  either side is wrong or should defer to the other — she is arguing that the *structure
  of the situation* prevents the two sides from developing shared understanding. Without
  a feedback loop, enthusiasts cannot see the reliability degradation their velocity
  creates, and skeptics cannot see the competitive ground being lost by caution. Each
  group has access only to the costs of the other's failure mode, not its benefits. This
  is a novel structural diagnosis not present in any existing corpus note.

### Claim 6: Resolving the enthusiast/skeptic tension requires treating it as both a leadership challenge and an engineering challenge

- **Evidence**: Willison's summary of Majors' recommendation, with the phrase "mend the
  gap in shared reality" in quotes indicating verbatim attribution to Majors.
- **Confidence**: anecdotal (the recommendation is framed in the accessible content; the
  specific mechanisms are in the paywalled Substack body)
- **Quote** (Willison's framing of Majors' position): "Charity recommends treating this as
  both a leadership challenge and an engineering challenge."
  (Majors' phrase, as quoted in Willison's closing): "mend the gap in shared reality"
- **Our assessment**: The dual framing — leadership AND engineering — is significant. Many
  adoption debates treat this as purely a leadership problem (leadership should mandate
  or slow adoption) or purely a technical problem (build better tooling). Majors argues
  both are required: leadership must create structures for feedback exchange, and
  engineering must build the mechanisms that make the shared reality visible. The
  phrase "shared reality" is precise — the goal is not that both sides agree, but that
  both sides have access to the same operational data about what is actually happening.
  This implies specific engineering artifacts: reliability dashboards, comprehension
  audits, incident causation traces that connect AI-assisted changes to production
  failures.

## Concrete Artifacts

### Verbatim Blockquotes from Willison's Page

```
Source: Simon Willison, https://simonwillison.net/2026/Jun/4/ai-enthusiasts-ai-skeptics/
(excerpting Charity Majors, https://charitydotwtf.substack.com/p/ai-enthusiasts-are-in-a-race-against)
Published: June 4, 2026

[Blockquote 1 — The Enthusiasts:]
"The enthusiasts are _not wrong_. We are starting to see real, non-imaginary, discontinuous
leaps in capabilities from teams that lean in hard to working with AI. And this does not
feel like a normal technology cycle where you can wait for the dust to settle; teams that
sit this out while competitors are hustling could be out of business before the dust settles.
That's a real, existential threat."

[Blockquote 2 — The Skeptics:]
"The skeptics are also _not wrong_. When you ship code faster than engineers can read it,
in domains where nobody has full context, you are making withdrawals from a trust account
that took years to build. Reliability degrades, institutional knowledge evaporates. You end
up with systems nobody understands, products burbling into incoherence, and on-call
rotations that grind people up and spit them out. That is ALSO a real existential threat."

[Blockquote 3 — The Structural Gap:]
"There is no natural feedback loop connecting enthusiasts with skeptics."

[Willison's closing framing:]
"Charity recommends treating this as both a leadership challenge and an engineering
challenge. The key issue: [blockquote 3]. Designing feedback loops to help
'mend the gap in shared reality' between the two groups is a fascinating organizational
design problem."
```

### The Four Skeptic Consequences Named by Majors

```
Consequences of shipping code faster than engineers can read it
(Charity Majors, via Simon Willison, June 4, 2026):

1. Reliability degrades
2. Institutional knowledge evaporates
3. Systems nobody understands (including products "burbling into incoherence")
4. On-call rotations that "grind people up and spit them out"

Framed by Majors as: "withdrawals from a trust account that took years to build"
```

## Cross-References

- **Corroborates**: `blog-simonwillison-james-shore-maintenance-costs.md` (Claims 1–4):
  James Shore's maintenance cost framework is the mathematical articulation of exactly
  what Majors calls "withdrawals from a trust account." Shore's model shows that shipping
  faster without reducing per-unit maintenance costs compounds the total maintenance
  burden until it consumes team capacity — this is the mechanism by which "trust accounts"
  are depleted. Shore's Claim 3 ("productivity gain disappears within ~5 months") maps
  directly to the trajectory Majors describes: velocity that appears as a win until the
  reliability debt materializes. The two sources are complementary: Majors names the
  organizational dynamic; Shore provides the economic model for why it is correct.

- **Corroborates**: `blog-anthropic-ai-native-engineering-org.md` (Claims 1, 6, 10):
  Fung's three-way convergence finding (Anthropic, Osmani, Shopify all independently
  report that verification and code review are the post-adoption bottleneck) can now be
  read as the engineering expression of what Majors calls the skeptic concern: teams that
  adopted enthusiastically discovered their comprehension bandwidth was the new constraint.
  Fung's "trust but verify" code review bifurcation is an example of an engineering
  response to the skeptic concern — mechanisms that give skeptics their reliability
  assurance (human review on legal, security, product taste) while enabling enthusiast
  velocity (Claude handles mechanical). This is a concrete instance of "designing feedback
  loops to mend the gap in shared reality."

- **Corroborates**: `blog-thebatch-ng-aiteam-structure.md` (Claims 4–5): Ng's "bottleneck
  cascade" (marketing, legal, design all become slower than engineering when velocity
  increases 10×–100×) is the organizational-scale version of what Majors describes at the
  team level. Ng's cascade describes what happens when enthusiast velocity escapes into
  adjacent functions without skeptic friction; Majors describes what happens *inside* the
  engineering team before the cascade reaches adjacent functions. The two sources describe
  different stages of the same dynamic: Majors is the internal team-level version; Ng is
  the cross-org cascade version.

- **Extends**: `blog-anthropic-ai-native-engineering-org.md` (Claim 10 — three team
  principles): Fung's team principles ("relentlessly dogfood," "flat," "kill obsolete
  processes") represent the enthusiast-oriented organizational design for teams that have
  already resolved the tension toward adoption. Majors' source addresses the prior step —
  how to create the shared reality that makes adoption decisions possible without one side
  simply dominating the other. Fung's principles describe what a post-adoption org looks
  like; Majors describes the organizational prerequisite to get there without losing the
  skeptics.

- **Extends**: `blog-simonwillison-the-pressure.md` (the curl maintainer experience):
  Daniel Stenberg's account of AI-amplified security report volume creating unsustainable
  on-call burden is a concrete, real-world case study of exactly the fourth skeptic
  consequence Majors names: "on-call rotations that grind people up and spit them out."
  Stenberg experiences this as the *external* effect of AI adoption by other teams
  (security researchers using AI to flood his queue); Majors describes it as the
  *internal* effect on the team doing the adopting. Together they bracket the on-call
  reliability concern from both directions.

- **Novel** (not present in any existing corpus note):
  - **The explicit "both are not wrong" epistemological stance**: No existing corpus note
    represents both the enthusiast and skeptic positions as simultaneously valid and
    equally existential. All corpus sources are written from one position or the other.
    Majors' balanced framing provides the guide with vocabulary to present both positions
    without implying one is correct.
  - **"No natural feedback loop connecting enthusiasts with skeptics"**: This structural
    diagnosis of *why* the tension persists — not because one side is wrong, but because
    no information flows between them — is entirely new to the corpus. It names the
    missing organizational mechanism.
  - **"Trust account" as a metaphor for institutional reliability**: The framing of
    institutional knowledge and reliability as a depleting capital account — accumulated
    over years, withdrawable at velocity — is a novel addition to the corpus's vocabulary
    for discussing code quality risks.
  - **"Mend the gap in shared reality" as the design goal**: No other corpus source names
    the *goal* of the organizational intervention as achieving shared reality between the
    two groups. This is a more precise goal than "resolve conflict" or "align on
    adoption" — it implies specific engineering artifacts that make the same operational
    facts visible to both groups.
  - **Dual leadership-and-engineering framing for adoption friction**: No corpus source
    treats the enthusiast/skeptic tension as requiring both leadership structure and
    engineering mechanism. Most corpus coverage addresses either organizational policy
    (Shopify's mandate, Anthropic's principles) or technical tooling.

## Guide Impact

- **Chapter 05 (Team Adoption — Why Adoption Debates Stall)**: This is the most
  actionable addition this source makes to the guide. The corpus currently covers what
  teams that have adopted AI do (Fung, Thawar, Ng) but not the organizational dynamic
  that makes adoption decisions difficult. Majors' "no natural feedback loop" diagnosis
  explains why internal adoption debates often produce stalemate: each side is correct
  about its own existential threat and has no mechanism to see the other's. Recommend
  adding a section "Bridging Enthusiasts and Skeptics" that anchors on Majors' structural
  diagnosis and points to engineering-side feedback mechanisms (reliability dashboards
  connected to AI-assisted change rates, incident post-mortems that trace AI-generated
  code contributions, comprehension audits as periodic skeptic check-ins).

- **Chapter 05 (Team Adoption — The Dual Existential Threat)**: The "both are not wrong"
  framing should appear explicitly before any adoption guidance in Chapter 05. Guides that
  treat AI adoption skepticism as ignorance will fail to persuade the teams most at risk
  from reliability degradation — those are exactly the teams that most need good feedback
  loop design. The competitive threat (falling behind) and the reliability threat (systems
  nobody understands) are both real; teams need organizational design for both, not a
  choice between them.

- **Chapter 00 (Principles)**: The "trust account" metaphor and the "no natural feedback
  loop" diagnosis belong in the principles chapter as epistemic context. They establish
  that the tension is structural — inherent in the situation — rather than resulting from
  irrationality or stubbornness on either side. This frames the rest of the guide's
  team adoption content as organizational design work, not persuasion work.

- **Chapter 03 (Safety and Verification)**: Majors' four skeptic consequences — reliability
  degradation, institutional knowledge evaporation, systems nobody understands, on-call
  burnout — provide specific claims that verification practices should address. Current
  corpus coverage of verification focuses on catching bugs (correctness) and security
  issues. Majors' concerns extend to *comprehension* (can engineers still read and reason
  about the code?), *institutional knowledge* (does the team still understand *why* the
  code was written the way it was?), and *operational reliability* (is on-call sustainable
  given the new code volume?). These are distinct verification concerns that the guide
  should address separately from correctness-checking.

## Extraction Notes

- The primary source (Charity Majors' Substack at charitydotwtf.substack.com) returned
  HTTP 403 Forbidden on direct fetch. The Simon Willison link-blog post is therefore the
  sole accessible version of this content. All claims are grounded only in the three
  blockquotes and Willison's brief framing visible on the Willison page. The Substack post
  almost certainly contains more specific recommendations and additional context that is
  not captured here.
- All three blockquotes were verified verbatim from two separate WebFetch requests to the
  Willison page. The closing phrase "mend the gap in shared reality" appears in quotes in
  Willison's own prose, indicating verbatim attribution to Majors.
- No Lobsters comment thread (https://lobste.rs/s/ri4flr/) provided substantive
  additional content — commenter discussion largely debated the article's lack of
  empirical evidence, which is a useful signal about the claim confidence level but did
  not add extractable claims.
- Confidence is rated `emerging` (not `anecdotal`) because Charity Majors is one of the
  highest-credibility authorities on the skeptic position — her expertise in observability
  and reliability makes her assertion that these are real consequences especially credible.
  The enthusiasm position is corroborated by multiple corpus sources. The structural
  diagnosis (no natural feedback loop) is conceptual rather than empirical, but it comes
  from a highly credible source and maps directly to organizational dynamics described
  elsewhere in the corpus.
- The Prospector's two triage comments assigned different chapter relevance: the first
  triage (Ch02/Ch03) and the second (Ch05/Ch03/Ch00). This extraction follows the second
  triage's chapter framing, which better reflects the organizational-design content of the
  source.
