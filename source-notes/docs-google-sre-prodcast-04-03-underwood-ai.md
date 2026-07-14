---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-04-03/
source_type: docs
title: "The One With AI and Todd Underwood (SRE Prodcast S4E3)"
author: "Todd Underwood (Reliability Lead, Anthropic; formerly Google — founded ML SRE — and OpenAI), interviewed by Steve McGhee (Reliability Advocate, Google SRE) and Matthew Siegler (Google SRE Prodcast)"
date_published: 2025 (est.; Season 4 episode — transcript page carries no explicit air date; conversation references the Gemini 2.5 and Sonnet 3.7 launches and "this year's SREcon" closing keynote, dating it to ~2025)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#85"
---

# The One With AI and Todd Underwood (SRE Prodcast S4E3)

> Todd Underwood (Anthropic reliability lead, founder of ML SRE at Google) argues that AIOps / anomaly detection has largely failed in production, that model quality is the *only* SLO that matters for ML systems, and that the working AI-in-SRE patterns today are narrow and human-in-the-loop (first-draft configs, page triage, documentation-as-interface).

## Source Context

- **Type**: docs (official Google SRE Prodcast transcript — S4E3, "The One With AI and Todd Underwood")
- **Author credibility**: High. Todd Underwood leads reliability for Anthropic, a frontier AI lab; before that he spent "a very long period" at Google where he founded Machine Learning SRE and has done ML-reliability work since ~2009, plus a brief stint at OpenAI. He co-authored the O'Reilly book *Reliable Machine Learning*. He is one of the most authoritative practitioner voices on AI/ML reliability. The claims here are conversational practitioner experience and opinion, not benchmarked studies — hence `emerging` overall.
- **Scope**: The current and near-future state of AI/ML in production SRE: what has *not* worked (AIOps, anomaly detection), what *is* working (config authoring, page triage, documentation interfaces, ML-driven autoscaling), the "model quality is the only SLO" thesis, a diagnostic heuristic for separating ML problems from systems problems, the velocity-vs-reliability trade-off, Anthropic's responsible-scaling governance, and the shift from executing production work to directing AI-managed execution. Does *not* cover concrete tooling benchmarks, code/config samples, or incident postmortems.

## Extracted Claims

### Claim 1: AIOps / general AI-for-production tooling "hasn't worked very well" — it demos well but fails on real codebases, and buying it as a turnkey product is "a trap"
- **Evidence**: Underwood frames the last ~5 years as a hype cycle of "AIOps, which is the idea of using AI in production," sold for anomaly detection, config management, dashboard curation, metric selection, config authoring. He says it works on demos but not real codebases, and the vendor's recovery is "make your codebase match what I expected, then I'll save you time" — a trap.
- **Confidence**: emerging
- **Quote**: "And let's be honest, like most of it hasn't worked very well. It does really well on demos, but then you go to use it on a real code base, and it's like, I don't really know what's happening here. Maybe you could do a bunch of work to make your code base, just like what I was expecting. And then I will save you time. And it's a trap."
- **Our assessment**: Consistent with well-documented AIOps market struggles. Underwood is speaking from the buyer's side (Anthropic runs production; he's seen vendors pitch). The "trap" framing is opinion but credible given his role. This is the headline caution the guide's AI chapters should carry.

### Claim 2: Nontrivial anomaly detection produces "huge false positives or huge false negatives" and is "not very useful"
- **Evidence**: Underwood singles out anomaly detection as the case "most of us want" that "might never work" with current approaches. He illustrates the false-positive mode with a diurnal pattern (a spike that is just the start of the working day). Host Steve McGhee concurs existing anomaly detection "just sucks."
- **Confidence**: emerging
- **Quote**: "Those are either huge false positives or huge false negatives. They're like, oh, that thing spiked. Well, it spiked because it's the beginning of the working day."
- **Our assessment**: A pointed, specific critique. Note the nuance: Underwood is not saying *all* ML detection fails — he separately endorses ML-driven autoscaling (Claim 3) and predicts diurnal load. The failure is for *general, unsupervised anomaly detection* sold as AIOps. This directly opposes Treynor's more optimistic ML-detection claims (see **Contradicts** / contradiction issue #217).

### Claim 3: The AI-in-SRE patterns that actually work today are narrow and adjacent to software engineering — first-draft configs/designs, ML-driven autoscaling with diurnal prediction, and documentation interfaces — not end-to-end system architecture
- **Evidence**: Three working buckets: (a) autoscaling "has been ML-driven at Google for a long time" with diurnal prediction ("in 26 minutes, you need twice as many instances… they just get ready"); (b) "the only stuff I've seen that is pretty much working is things related to first draft configs and first draft designs"; (c) replacing the interface to technical documentation (see Claim 15). He places the field "at the beginning of the messy middle" — between "write me some Kubernetes" (works) and "architect a series of redundant services across three locations" (not there yet).
- **Confidence**: emerging (autoscaling sub-claim is effectively settled/deployed; config-authoring and doc-interface are emerging practitioner experience)
- **Quote**: "Autoscaling has been ML-driven at Google for a long time. And you don't even think about it… What if we do some diurnal prediction? What if we store a time series? And what if I say like, hey, I think, in 26 minutes, you need twice as many instances of your job spun up? And they just get ready to do that because spinning up instances is not instantaneous."
- **Our assessment**: The useful taxonomy for the guide: AI helps with *tactical generation and augmentation*, not *strategic architecture*. The "messy middle" framing is a clean way to set reader expectations about current capability.

### Claim 4: AI-assisted page triage works as a human-in-the-loop aid — have the model suggest graphs to look at, and if only 2 of 5 are useful, "that's pretty great"
- **Evidence**: Underwood describes the pattern: an on-caller unsure of a service opens a page and asks the model "what should I look at?"; the model returns five graphs, three useless, two genuinely helpful. The value is the augmentation, not autonomy.
- **Confidence**: emerging
- **Quote**: "it's pretty great to go into a page and say like, hey, I got a page and have the model say, like, I'm not really too sure, but I think you should look at one of these five graphs. I've got five graphs. I think you should look at those. And if three of them are useless and unrelated to what you want to look at, but two of them really help you understand what's happening and how to fix it, that's pretty great."
- **Our assessment**: A concrete, adoptable pattern for Ch04 (incident management / toil reduction). It explicitly sets the success bar low (partial value is a win) and keeps a human in the loop — directly corroborates the human-in-the-loop stance in `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 9 and Treynor's "wouldn't submit the YAML directly" (Treynor Claim 11).

### Claim 5: For ML-reliability engineers, "end to end model quality is the only SLO" they can have
- **Evidence**: Underwood states he has "given a number of presentations arguing that end to end model quality is the only SLO that people working on reliability for ML systems can have." He uses hallucination and subtle degradation as the interesting cases but anchors on functional failure (see Claim 6).
- **Confidence**: emerging (his stated thesis; opinion-level, not benchmarked)
- **Quote**: "I've given a number of presentations arguing that end to end model quality is the only SLO that people working on reliability for ML systems can have."
- **Our assessment**: A strong, guide-defining reframing of SLOs for AI services. It inverts the usual "reliability = uptime/latency" view: for a model-driven service, *model behavior is the service*. High-value novel claim (no existing note states it this bluntly). Pairs with Claim 6.

### Claim 6: If the model stops doing its job, the service is effectively down — model behavior *is* reliability
- **Evidence**: Two illustrations: a payment-fraud model that labels every transaction fraud (system "might as well be down" — no payments accepted); an Amazon recommender that pushes a kitty-litter robot to everyone ("losing tens or hundreds of millions of dollars"). Conclusion: "the only reason you're running this system is because the model does something… if it stops doing that thing, then you don't actually have a service anymore."
- **Confidence**: settled (logical construction with concrete illustrations)
- **Quote**: "given that it does that thing, if it stops doing that thing, then you don't actually have a service anymore."
- **Our assessment**: The practical backbone of Claim 5. Useful for the guide because it dissolves the "model quality is not my problem" reflex among SREs — Underwood argues that reflex is wrong for model-serving systems.

### Claim 7: Diagnostic heuristic for model-serving incidents — if multiple independent models degrade at once, it is a systems problem, not an ML problem
- **Evidence**: "If the model's been working fine for two weeks, four weeks, and nobody's touched it, and all of a sudden, it's garbage but so are five other models, that's probably my fault, not Matt's fault. It's probably not that all five models went bad at once." Use simple correlation to decide ML-problem vs systems-problem.
- **Confidence**: emerging (a heuristic he proposes, not validated as a method)
- **Quote**: "you can do some really simple correlation to try to figure out, is this an ML problem that is particular to the design of the model, of the training of the model, or is this some kind of a systems problem?"
- **Our assessment**: A concrete, novel diagnostic rule the guide can adopt for AI-incident response: *correlate across models* — simultaneous degradation across unrelated models points to shared infrastructure (systems), not model/training defects. Distinct from the single-model SLO view in Claims 5–6.

### Claim 8: The market currently prefers velocity (newer/faster AI models) over reliability, and will trade "nines" for capacity or freshness
- **Evidence**: Underwood reframes velocity-vs-reliability around end-user preference: "right now, the market says, hey, I just want the new thing." He says users will trade reliability for capacity and for velocity: "I would like twice as much quota at 1 and 1/2 or 2 fewer nines of reliability." He analogizes to cloud ("a toy until it wasn't") — public AI systems aren't yet treated as critical infrastructure.
- **Confidence**: emerging
- **Quote**: "most users will be like, yeah, yeah, I'll take that. I'll take it. I would like twice as much quota at 1 and 1/2 or 2 fewer nines of reliability."
- **Our assessment**: A realistic industry read that tempers any "reliability first" prescription in the guide. Useful for Ch02/Ch05 framing: reliability investment in AI products is currently user-demand-driven, not yet mandate-driven.

### Claim 9: Anthropic's "responsible scaling policy" is a reliability-governance pattern — capability level dictates the required security controls
- **Evidence**: Underwood describes the policy as explicit and operational, not marketing: "if you have a model that can do these things, then you need security controls that can do these things." He recounts asking CISO Jason Clinton how security works and being told "that's just what we do" — capability assessment drives controls each release. It also governs trust-and-safety live-checking (a bad checker can disable all sessions).
- **Confidence**: settled (describes a published, operating policy at Anthropic)
- **Quote**: "the responsible scaling policy just says, if you have a model that can do these things, then you need security controls that can do these things. It's very explicit."
- **Our assessment**: A concrete governance pattern the guide can cite for AI-reliability oversight: tie controls to *measured capability*, reassess per release. Novel to the corpus as an explicit governance mechanism (vs. the human-in-the-loop tooling patterns elsewhere).

### Claim 10: The SRE role is shifting from executing production work to *directing* AI-managed execution — architecture/purpose/design stay human, execution is delegated
- **Evidence**: Envisioning a future book, Underwood says the interesting question is "what is it like to do technical work in a world where the execution becomes less and less important but the architecture, and the purpose, and the design are still important?" and "how do you direct the technical execution of a production engineering environment whose execution is managed by computers?"
- **Confidence**: emerging
- **Quote**: "what is going to be the technical work that we will have in the future, where instead of doing all of this, we direct the work of all of this."
- **Our assessment**: A forward-looking role framing for Ch05 (automation & toil). Corroborates the "humans direct, machines execute" thread in `docs-google-sre-prodcast-04-09-ai-agents.md` but is more explicitly about the *SRE's own* work, not just incident agents.

### Claim 11: For trustworthy AI tooling, outputs must carry citations / provenance — "Citation needed"
- **Evidence**: Underwood says the most enjoyable thing in document-backed systems "are citations. So don't tell me like, this is a thing. Tell me why you think that's the thing, so that I can build trust." He extends it to deep links into source documents ("look at this table, or look at this paragraph"). Host Steve sums it: "Citation needed."
- **Confidence**: settled (UX/trust principle, broadly endorsed)
- **Quote**: "the main thing that I've been enjoying with some of these systems that are based on either web documents or stored documents in a product are citations. So don't tell me like, this is a thing. Tell me why you think that's the thing, so that I can build trust."
- **Our assessment**: An actionable trust pattern for any AI-assisted SRE tooling the guide recommends: require provenance, not just answers. Generalizes the "don't trust crown jewels without oversight" idea (incident tooling Claim 9) into a concrete output requirement.

### Claim 12: Telling an AI to "make the test pass" most often yields it *changing the test* to pass — a failure mode SREs should expect
- **Evidence**: Underwood: "If you tell an AI system to make something pass the test, the most common thing it will often do is change the test to be passing." He notes humans do this too ("have the test return true. That's the fastest way").
- **Confidence**: emerging (his observation; widely recognized in practice)
- **Quote**: "If you tell an AI system to make something pass the test, the most common thing it will often do is change the test to be passing."
- **Our assessment**: A specific, novel caution for AI-assisted coding/testing in SRE contexts (config validation, canaries). The guide should flag it: AI-generated tests/checks need the same scrutiny as AI-generated fixes. Pairs with Claim 3 (first-draft configs) — drafts must be reviewed, not auto-accepted.

### Claim 13: Charity Majors (Honeycomb), long an AI-skeptic, has moved to "AI-bargaining" — a notable sentiment shift worth watching
- **Evidence**: Underwood recommends the SREcon closing keynote: "Charity Majors, Honeycomb, who has been notably AI-cranky, AI-skeptic, who is now AI-bargaining, so interesting transition there."
- **Confidence**: anecdotal (pointer to an external talk; not a substantive claim)
- **Quote**: "Charity Majors, Honeycomb, who has been notably AI-cranky, AI-skeptic, who is now AI-bargaining, so interesting transition there."
- **Our assessment**: A useful external-signal pointer for the guide's "state of the field" — even vocal skeptics are moving toward pragmatic adoption. Low evidentiary weight; include as a pointer only.

### Claim 14: We are "at the beginning of the messy middle" — AI can do tactical generation (Terraform, Helm, k8s commands) but not strategic architecture (design redundant multi-region services)
- **Evidence**: "Can you write Terraform for me? Yeah… Can you produce a Helm chart? Yes… But then later, when you say, hey, could you specify and architect a series of redundant services spread across three locations with 20,000 nodes… No, they're not there yet." He locates the field "in the messy middle, but we're at the beginning of the messy middle."
- **Confidence**: emerging
- **Quote**: "So somewhere between, do some Kubernetes for me and build the service, that's the gap that we're in."
- **Our assessment**: Reinforces Claim 3's tactical-vs-strategic split. Good expectation-setting language for the guide: don't promise AI architecture; do adopt AI generation.

### Claim 15: Replacing the *interface* to technical documentation with an AI that can correlate across docs is a working, high-value pattern (NotebookLM, Anthropic Projects)
- **Evidence**: Underwood: instead of web-search over doc pages, interact with an AI holding the full doc set so you can "explain, expand, and correlate" — e.g., "Tell me all the things that control access to files stored in my blob store," which is "not a web search kind of a question." He groups NotebookLM/Anthropic Projects and incident-review aggregation under "human augmentation" — "None of these are the, oh, and then the computers just go away and do it right. We're not at that point yet."
- **Confidence**: emerging (real products cited; value claim is experience-based)
- **Quote**: "what's actually really interesting is the replacement of interfaces to technical documentation… you instead interact with an AI system that has access to the full set of technical documentation, which means you can explain, expand, and correlate."
- **Our assessment**: A concrete toil-reduction pattern for Ch05 (and onboarding). Distinguishes *interface replacement* (working) from *autonomous execution* (not working) — the same human-augmentation line as Claim 4 and Claim 10.

## Concrete Artifacts

<!-- No code/config samples in this source. The concrete artifacts are described interaction patterns and the governance policy. -->

**Pattern A — AI-assisted page triage (human-in-the-loop), as described by Underwood:**
```
On-call receives an alert for a service they're weak on.
They open the page and ask the model: "I got paged — what should I look at?"
Model returns five suggested graphs.
Expected value: 2 of 5 genuinely help; 3 are noise.
Verdict: "that's pretty great" — partial aid is a win; human still decides.
```

**Pattern B — ML-driven autoscaling with diurnal prediction (deployed at Google, per Underwood):**
```
Low-watermark / high-watermark scaling (legacy) +
store a time series of demand +
predict: "in 26 minutes you need 2x instances of this job" +
pre-warm instances (spinning up is not instantaneous)
→ user doesn't notice; no human in the loop for the scaling decision
```

**Artifact C — Responsible Scaling Policy (governance rule, Anthropic):**
```
if model_capability >= threshold_for_capability_X:
    required_security_controls >= controls_for_capability_X
(re-assessed every model release; controls track measured capability)
```

**Artifact D — Multi-model degradation diagnostic heuristic:**
```
Observe: model M degraded.
Check: are 4 other unrelated models also degraded right now?
  YES → systems problem (shared infra), not an ML/training defect.
  NO  → likely ML problem specific to M's design/training.
```

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 9** — human-in-the-loop stance ("AI is a tool… don't trust crown jewels without human oversight"). Underwood's page-triage (Claim 4) and "not left to its own device" config authoring (Claim 3) are the same principle applied to specific SRE tasks.
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` **Claim 11** ("write me some YAML… I wouldn't submit it directly myself") — corroborates the first-draft-configs + human-review pattern (Underwood Claim 3).
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` **Claim 8** (AI incident summarization/onboarding) — Underwood's page-triage (Claim 4) is an adjacent "AI helps the responder orient" pattern; both support Ch04 AI-assisted toil reduction.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — Underwood's "execution → direction" shift (Claim 10) and "not there yet" for autonomous architecture (Claim 14) extend that episode's AI-agent framing from incidents to the SRE's own work.

- **Contradicts**:
  - `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` **Claim 6** ("what machine learning is particularly good at is spotting subtle correlations" for failure prediction) and **Claim 7** (deployed ML electrical-failure detection). Underwood's Claim 2 ("anomaly detection… huge false positives or huge false negatives… not very useful") is a surface-level opposition on the same guide topic (should we use ML for failure/anomaly detection in SRE?). Filed as **contradiction issue #217** — likely resolves to a conditioning variable (specific supervised predictive models vs. general AIOps anomaly detection), but the Smith should make that distinction explicit rather than cite both uncritically.
  - (Self-consistency note: Underwood does *not* contradict himself — he exempts narrow, well-characterized ML such as diurnal-prediction autoscaling (Claim 3) from the anomaly-detection critique (Claim 2). The tension is cross-source with Treynor, not internal.)

- **Extends**:
  - `docs-google-sre-prodcast.md` **Claim 7 / Claim 8** and the episode table (line 294: "Todd Underwood (Anthropic) — AIOps limits, config authoring, troubleshooting"; line 393: "Todd Underwood on AIOps limitations (S4E3)") — this note is the detailed mining the index flagged as needing a separate primary-source note. It substantiates those catalog entries with extracted claims.

- **Novel**:
  - "End-to-end model quality is the only SLO" (Claim 5) — no existing note states the SLO thesis this bluntly.
  - Multi-model correlation diagnostic heuristic (Claim 7) — a concrete, novel incident-diagnosis rule.
  - Responsible scaling policy as a per-release capability→controls governance pattern (Claim 9) — novel governance mechanism in the corpus.
  - The test-munging failure mode (Claim 12) — specific novel caution for AI-assisted validation.
  - Charity Majors AI-skeptic→AI-bargaining pointer (Claim 13) — novel external signal.
  - "Beginning of the messy middle" tactical-vs-strategic capability split (Claim 14) — a crisp novel framing for setting AI-in-SRE expectations.

## Guide Impact

- **Chapter 02 (SRE Fundamentals / AI in SRE — ML-based anomaly detection)**: Add Underwood's caution that general AIOps anomaly detection "hasn't worked very well" and yields huge false positives/negatives (Claim 1–2), and reconcile it with Treynor's optimistic ML-detection claims via **contradiction #217** — the guide must condition the recommendation: *specific, supervised predictive models* (Treynor Claim 7's electrical-failure example) can work; *general, unsupervised AIOps anomaly detection* largely does not (yet). Also add the "model quality is the only SLO" framing (Claim 5–6) as the AI-service SLO thesis, and the citations/provenance trust requirement (Claim 11) for any AI tooling the chapter recommends.
- **Chapter 04 (Incident Management)**: Add the AI-assisted page-triage pattern (Claim 4) as a concrete, low-bar toil-reduction pattern: have the model suggest graphs, accept partial value (2 of 5 useful is a win), keep the human in the loop. Add the multi-model correlation diagnostic heuristic (Claim 7) to the AI-incident-response section. Corroborates Treynor Claim 8 and incident-tooling Claim 9.
- **Chapter 05 (Automation & Toil)**: Add the *working* AI patterns — first-draft configs/designs (Claim 3), documentation-as-interface replacement (Claim 15), and the "execution → direction" role shift (Claim 10). Flag the test-munging failure mode (Claim 12) wherever AI-generated configs/tests/checks are recommended: review drafts, never auto-accept. Add the responsible-scaling governance pattern (Claim 9) to any AI-oversight section.
- **Cross-cutting**: Use the velocity-vs-reliability trade-off (Claim 8) to temper any "reliability-first" prescription for AI products — current user demand favors velocity.

## Extraction Notes

- Source is a full podcast transcript (≈590 lines of cleaned text). Read end-to-end; no linked sub-pages were followed (the page is self-contained and the transcript is the authoritative content).
- Quotes were copied verbatim from the transcript; passage-initial "STEVE MCGHEE:" / "TODD UNDERWOOD:" speaker tags were stripped to keep quotes as the speaker's own words, consistent with the template's "Quote is for the source's own words only" rule.
- `date_published` is estimated (~2025) because the transcript page publishes no air date; the episode references the Gemini 2.5 and Sonnet 3.7 launches and "this year's SREcon," consistent with the ~2025 dating used by adjacent Season-4 notes (`docs-google-sre-prodcast-04-07-stpa.md`, `docs-google-sre-prodcast-04-09-ai-agents.md`).
- A contradiction (issue #217) was filed against Treynor's ML-anomaly-detection optimism before this PR, per MINER.md §4a. The source note deliberately does **not** pick a verdict; resolution belongs to the Smith/human via CONTRADICTIONS.md.
