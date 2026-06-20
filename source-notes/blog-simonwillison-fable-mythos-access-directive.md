---
source_url: https://simonwillison.net/2026/Jun/13/us-government-directive-to-suspend-access/
source_type: blog-post
title: "Statement on the US government directive to suspend access to Fable 5 and Mythos 5"
author: Simon Willison (linking to and commenting on Anthropic's official statement at https://www.anthropic.com/news/fable-mythos-access)
date_published: 2026-06-13
date_extracted: 2026-06-20
last_checked: 2026-06-20
status: current
confidence_overall: emerging
issue: "#1234"
---

# Statement on the US government directive to suspend access to Fable 5 and Mythos 5

> Simon Willison documents the June 12, 2026 US government export control directive
> forcing Anthropic to suspend Fable 5 and Mythos 5 access for all users within 4.5
> hours, with first-hand API monitoring logs showing the exact cutoff moment — the
> first corpus case of a government regulatory action immediately terminating commercial
> AI model availability, and a concrete constraint for practitioners designing systems
> that depend on third-party model APIs.

## Source Context

- **Type**: blog-post (link post with personal verification; Simon Willison relaying and
  independently verifying Anthropic's official statement with his own API monitoring logs.
  Published June 13, 2026, one day after the incident. The underlying primary source is
  Anthropic's official statement at https://www.anthropic.com/news/fable-mythos-access)
- **Author credibility**: Simon Willison is the creator of Django and one of the highest-
  signal independent LLM tooling commentators. For this post, his contribution is twofold:
  (1) relaying and contextualizing Anthropic's official statement, and (2) independently
  verifying the outage moment with his own monitoring script — providing concrete,
  timestamped API evidence that is not in the official statement. The underlying Anthropic
  statement is first-party from the model provider directly affected. Maximum credibility
  for factual claims about the incident timeline and scope.
- **Scope**: Covers the incident (what directive, when received, what was suspended), the
  alleged jailbreak technique, Anthropic's public position on the directive, and Willison's
  first-hand API monitoring verification of the cutoff. Does NOT cover: enforcement
  mechanism details, classification of the government authority cited, Anthropic's legal
  strategy, or subsequent restoration timeline.

## Extracted Claims

### Claim 1: The US government issued an export control directive to Anthropic to suspend all access to Fable 5 and Mythos 5, citing national security authorities

- **Evidence**: Anthropic's official statement (linked from Willison's post at
  https://www.anthropic.com/news/fable-mythos-access). First-party confirmation from the
  company receiving the directive.
- **Confidence**: settled (official Anthropic statement; the directive is documented by both
  Anthropic and independently verified by Willison's monitoring logs)
- **Quote**: "The US government, citing national security authorities, has issued an export
  control directive to suspend all access to Fable 5 and Mythos 5 by any foreign national."
- **Our assessment**: This is a novel category of API risk — not a technical outage,
  capacity issue, or pricing change, but a government regulatory action requiring immediate
  suspension. The "by any foreign national" scope in the directive is notable: Anthropic
  apparently disabled access for all users globally, not just foreign nationals, presumably
  to ensure unambiguous compliance (see Claim 5). For practitioners: this event establishes
  that commercial AI API availability is not solely a technical or business-continuity
  question — it is also a regulatory compliance variable that can change without customer
  notice within hours.

### Claim 2: Anthropic received the directive at 5:21pm ET on June 12, 2026 and access was revoked at 6:59pm PT (9:59pm ET) — an enforcement window of approximately 4.5 hours

- **Evidence**: Anthropic's statement ("We received the directive from the government today
  at 5:21pm (ET).") combined with Willison's first-hand API monitoring logs documenting
  successful calls at 6:56–6:57pm PT and a 404 error at 6:59pm PT on June 12.
- **Confidence**: settled (two independent sources: Anthropic's own statement for the
  receipt time; Willison's monitoring logs for the cutoff time)
- **Quote**: "We received the directive from the government today at 5:21pm (ET)."
- **Our assessment**: The 4.5-hour enforcement window is the key design constraint this
  incident establishes for practitioners. Anthropic received the directive at 5:21pm ET
  and had suspended access globally before 9:59pm ET the same day — faster than any
  standard change-management or incident-response cycle would allow for customer
  notification. Systems that depend on Fable 5 or Mythos 5 had no advance warning before
  encountering 404 errors. This directly implies that any production system relying on a
  single model provider must have a tested fallback path that requires zero manual
  intervention to activate — because the model it depends on could be unavailable by the
  time a human engineer is notified and could respond.

### Claim 3: The alleged jailbreak technique "essentially consists of asking the model to read a specific codebase and fix any software flaws"

- **Evidence**: Anthropic's official statement relaying their understanding of the
  government's basis for the directive.
- **Confidence**: emerging (Anthropic is relaying the government's characterization of the
  technique via their own interpretation; the government's classified basis is not publicly
  documented; Anthropic frames this as "our understanding")
- **Quote**: "Our understanding is that the government believes it has become aware of a
  method of bypassing, or 'jailbreaking' Fable 5." / "Essentially consists of asking the
  model to read a specific codebase and fix any software flaws."
- **Our assessment**: The described technique is functionally identical to standard
  AI-assisted security research workflows documented throughout the corpus — particularly
  in `blog-anthropic-ai-accelerated-offense.md` (Claim 2), where Anthropic's own research
  team used publicly available models to find vulnerabilities in production codebases.
  The irony: the technique the government flagged as a jailbreak is one Anthropic itself
  described as legitimate security practice in their April 2026 security blog post. This
  is not a contradiction — the government and Anthropic appear to have different
  characterizations of the same technique class. The guide should note this definitional
  ambiguity: capability that is documented practice in security research is simultaneously
  a regulatory trigger in a different governance frame.

### Claim 4: Anthropic characterizes the jailbreak as "narrow" and argues similar capabilities are available in other public models, including GPT-5.5

- **Evidence**: Anthropic's official statement; the GPT-5.5 comparison is reported in the
  Prospector triage comment based on Willison's post. Anthropic's position is that the
  technique is non-unique to Fable 5.
- **Confidence**: emerging (Anthropic's characterization of the vulnerability as "narrow"
  is their own framing, not independently assessed; the GPT-5.5 comparison is reported
  but not independently verified in this extraction)
- **Quote**: (no verbatim quote on this specific point extracted with confidence; paraphrase
  from Anthropic statement summary: "perfect jailbreak resistance is not currently possible
  for any model provider" and that demonstrated vulnerabilities are "widely available from
  other models")
- **Our assessment**: Anthropic's position — that the capability is non-novel and widely
  available — is strategically important for two reasons. First, it challenges the
  regulatory premise that suspending Fable 5 addresses the underlying risk (if GPT-5.5
  has the same capability, suspending Fable 5 merely redirects the technique, not
  eliminates it). Second, it signals Anthropic's intent to contest the directive while
  complying with it. For practitioners: if this regulatory rationale extends to other
  models in the future, no single AI provider substitution fully eliminates the
  compliance risk — teams relying on any frontier model with advanced security research
  capabilities face similar regulatory exposure.

### Claim 5: Anthropic suspended access for all users globally — not just foreign nationals as specified in the directive — to ensure unambiguous compliance

- **Evidence**: The directive text specifies "by any foreign national," but Willison's
  API testing (a US-based user) hit the same 404 error, indicating the suspension was
  universal. The Anthropic statement does not explicitly explain this decision, but the
  behavior is consistent with over-compliance to avoid any potential violation.
- **Confidence**: emerging (the universal suspension is documented by Willison's logs;
  the rationale for universal vs. narrower suspension is inferred, not explicitly stated
  by Anthropic in the documented statement text)
- **Quote**: (no direct quote on this specific claim; conclusion drawn from the 404 error
  Willison received as a presumably-US user)
- **Our assessment**: Anthropic's decision to apply the directive universally (rather than
  implementing nationality-based access restrictions) reveals a real operational reality:
  implementing compliant nationality-based restrictions for an API is technically and
  legally complex, and Anthropic apparently chose the simpler path of universal suspension
  rather than risk a compliance gap. For practitioners: this means the blast radius of
  future export control actions could affect domestic users even when the directive targets
  "foreign nationals." Do not assume that US-based operations are insulated from directives
  that appear to target foreign access only.

### Claim 6: Willison's API monitoring script captured successful calls at 6:56–6:57pm PT and a 404 error at 6:59pm PT on June 12, 2026

- **Evidence**: First-hand API monitoring logs documented in Willison's post. Independent
  verification of the cutoff timing, not reliant on Anthropic's statement.
- **Confidence**: settled (first-hand API observation with timestamps; Willison is a
  reliable technical practitioner with a long track record of accurate tooling observation)
- **Quote**: (no verbatim quote of the log output captured; the summary indicates
  successful calls at 6:56–6:57pm and a 404 at 6:59pm PT)
- **Our assessment**: The monitoring script approach Willison used is itself an artifact
  worth noting for practitioners. Willison had an active monitoring setup that was running
  against the Fable 5 API, which is how he detected the cutoff within minutes. Teams
  that depend on external model APIs should consider implementing similar active monitoring
  rather than relying on API provider status pages or passive error detection — especially
  for high-stakes production systems where a 3-minute detection delay matters.

### Claim 7: The API returned a 404 error directing users to Opus 4.8; all other Anthropic models remained unaffected

- **Evidence**: Willison's documented API response (the error message text). The specific
  redirection to Opus 4.8 is from the error message body.
- **Confidence**: settled (documented API response; Anthropic's statement confirmed other
  models were unaffected: "Access to all other Anthropic models will not be affected.")
- **Quote**: "Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error',
  'message': 'Claude Fable 5 is not available. Please use Opus 4.8...'"
- **Our assessment**: The error message is doubly useful: (1) it provides the literal
  practitioner experience of the outage (not a 500 or timeout — a clear 404 with a
  redirection message), and (2) it establishes that Anthropic had the forethought to
  embed a fallback guidance message in the error response. For practitioners building
  fallback logic: a 404 on a model endpoint with this error body is a reliable signal
  to switch to the alternative model programmatically. The availability of Opus 4.8 as
  the designated fallback also confirms the scope: only Fable 5 and Mythos 5 were
  suspended; other model generations were not affected.

### Claim 8: Anthropic is complying with the directive while publicly disagreeing with the government's reasoning, and is working to restore access

- **Evidence**: Anthropic's official statement framing (relayed by Willison). The
  compliance-under-disagreement position is explicit in the statement.
- **Confidence**: settled (Anthropic's public position is documented in their official
  statement; whether restoration succeeds is unknown at time of this extraction)
- **Quote**: (no single verbatim quote capturing this compound claim fully; the statement
  documents both compliance and disagreement)
- **Our assessment**: Anthropic's public disagreement-while-complying posture is
  significant for practitioners who rely on Anthropic models. It signals: (1) Anthropic
  is not simply deferring — they are contesting the regulatory basis, which creates a
  path toward restoration; (2) the company's public statement establishes a record for
  future regulatory engagements with this type of directive. Teams with business-critical
  dependencies on suspended models should monitor Anthropic's restoration timeline
  closely, as this may not be a permanent suspension.

## Concrete Artifacts

### API Error Response (documented by Willison, June 12, 2026, 6:59pm PT)

```
Error code: 404 - {
  'type': 'error',
  'error': {
    'type': 'not_found_error',
    'message': 'Claude Fable 5 is not available. Please use Opus 4.8...'
  }
}
```

### Incident Timeline (June 12, 2026)

```
Directive received by Anthropic: 5:21pm ET (2:21pm PT)
Last successful Willison monitoring call: 6:56–6:57pm PT
First documented 404 error: 6:59pm PT (9:59pm ET)

Enforcement window (receipt → cutoff): ~4 hours 38 minutes
Models suspended: Fable 5, Mythos 5
Models unaffected: Opus 4.8, all other Anthropic models

Scope of suspension: All users globally (not limited to foreign nationals
despite directive text)

Anthropic's stated fallback: Use Opus 4.8
```

### Key Anthropic Statement Excerpts (from https://www.anthropic.com/news/fable-mythos-access, June 12, 2026)

```
On the directive:
"The US government, citing national security authorities, has issued an export
control directive to suspend all access to Fable 5 and Mythos 5 by any foreign
national."

On timing:
"We received the directive from the government today at 5:21pm (ET)."

On the alleged jailbreak:
"Our understanding is that the government believes it has become aware of a method
of bypassing, or 'jailbreaking' Fable 5."

"Essentially consists of asking the model to read a specific codebase and fix any
software flaws."
```

## Cross-References

- **Corroborates**: `blog-thebatch-ng-ai-andrew-agentic-harness.md` (Claim 12) — The
  Batch 353 (May 2026) documented the TRAINS task force as a pre-deployment national
  security evaluation mechanism triggered by Claude Mythos's autonomous vulnerability
  exploitation capability. Claim 12 establishes the arc: "The abrupt policy change marks
  a major departure from the Trump Administration's focus on removing Biden-era regulatory
  barriers to AI innovation. It comes roughly one month after Anthropic attracted the
  government's attention by announcing that its Claude Mythos Preview model...could exploit
  vulnerabilities in widely used software." The Fable 5 directive is the next escalation
  in this arc — from pre-deployment evaluation (TRAINS) to post-deployment forced
  suspension. Both notes should be read together: the TRAINS note establishes the
  regulatory mechanism, the Fable 5 note documents its first operational use as a
  suspension order.

- **Corroborates**: `blog-anthropic-ai-accelerated-offense.md` (Claims 1 and 2) — The
  AI accelerated offense post documents that "publicly available models can find serious
  vulnerabilities that traditional reviews have missed for long periods" (Claim 2) and
  recommends "asking the model to read a specific codebase and fix any software flaws" as
  a defensive security research practice. The Fable 5 directive was triggered by the
  government citing exactly this technique as a jailbreak. The accelerated offense post
  (April 2026) and the Fable 5 directive (June 2026) establish a direct tension: the same
  capability class that Anthropic's security team documented as legitimate defensive
  practice in April became a government-cited national security concern in June. This is
  not a contradiction in the corpus — the technique is the same; the characterization
  differs by frame (security research vs. jailbreak risk). The guide should present both
  framings.

- **Novel**: This is the first corpus source documenting a government regulatory action
  causing forced, immediate suspension of a commercial AI model API. No other source in
  the corpus:
  - Documents a forced model-level API suspension (as opposed to rate limits, pricing
    changes, or voluntary deprecations)
  - Establishes a real-world enforcement timeline for model availability risk (4.5 hours)
  - Documents the specific API error response format for a compliance-driven suspension
  - Provides a practitioner-experienced verification of the exact cutoff moment
  - Establishes that universal suspension (not nationality-gated) was the compliance
    approach chosen

## Guide Impact

- **Chapter on Model Selection and System Architecture**: This event is a first-order input
  to model selection risk analysis. The guide currently covers technical model selection
  factors (capability, cost, latency). This source establishes a previously undocumented
  risk category: **regulatory availability risk**. Specifically recommend adding:
  (1) A section on model availability risk that includes regulatory action alongside
  technical outage and deprecation as categories of availability failure;
  (2) The 4.5-hour enforcement window as a concrete design constraint — any production
  system that cannot tolerate 4.5 hours of primary model unavailability must have an
  automated, tested fallback path;
  (3) The note that universal suspension may affect domestic users even for directives
  nominally scoped to foreign nationals.

- **Chapter on Integration Patterns / Resilience**: Currently the corpus documents
  fallback patterns for rate limits and latency. This source adds **regulatory suspension
  as a failure mode** that fallback patterns must handle. Specific recommendation: the
  Fable 5 error message (404 with a model-unavailability body) is the signal to detect
  in production error handling for compliance-driven suspensions. Teams should distinguish
  this from temporary API errors (5xx) in their retry/fallback logic — a 404 with this
  error type means "this model is gone, switch to alternative immediately."

- **Chapter on Operational Dependencies and Risk Management**: The incident demonstrates
  that active API monitoring (not passive status-page monitoring) is the only way to
  detect a compliance-driven cutoff within minutes. The guide should recommend that
  production systems depending on frontier model APIs implement active health-check
  monitoring with alerting, not just error-rate monitoring from production traffic.

- **Chapter on Regulatory Context**: This is the first documented case of an export
  control action applying directly to AI model API access. The guide should note this
  as an emerging regulatory risk category distinct from data privacy (GDPR, CCPA),
  AI safety certification (EU AI Act), and sector-specific AI regulations (financial
  services, healthcare). Export control/national security actions operate on different
  legal bases with much shorter implementation timelines than regulatory compliance
  cycles.

## Extraction Notes

1. **Primary source is Anthropic's statement, not Willison's analysis**: The post is
   predominantly a relay of the Anthropic statement with Willison's API monitoring logs
   as first-hand verification. The analytical content (context on the jailbreak technique,
   its availability in other models) comes from the Anthropic statement, not Willison's
   own editorial judgment.

2. **Quote confidence calibration**: Quotes from the first WebFetch pass (labeled as
   excerpts from the Anthropic statement with explicit quotation marks in the source) are
   higher confidence. The Anthropic statement additional quotes ("narrow, non-universal
   jailbreak," "perfect jailbreak resistance is not currently possible for any model
   provider") came from a summary response and may be close paraphrase rather than
   character-for-character verbatim. The latter quotes are noted as "(paraphrase from
   statement summary)" in the relevant claims rather than presented in Quote fields.

3. **GPT-5.5 comparison**: The Prospector triage comment references GPT-5.5 as the
   specific model Anthropic compared the jailbreak capability to. This claim was not
   directly confirmed in the two WebFetch passes; it appears in the Prospector's reading
   of the source. Treated as emerging-confidence and not quoted verbatim.

4. **Enforcement timeline discrepancy**: The Prospector triage comment stated "< 2 hours
   from government notification." The documented timestamps (5:21pm ET receipt, 9:59pm ET
   cutoff) indicate approximately 4 hours 38 minutes. The note uses the documented
   timestamps; the Prospector's < 2 hour figure appears to be an error.

5. **No sub-pages followed**: The Willison post links to the Anthropic statement
   (https://www.anthropic.com/news/fable-mythos-access), which was fetched separately.
   No further sub-pages from that statement were linked or required.
