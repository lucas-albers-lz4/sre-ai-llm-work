---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-04-07/
source_type: docs
title: "The One with STPA, Jeffrey Snover, and Theo Klein (SRE Prodcast S4E7)"
author: "Theo Klein (SRE, Google Maps) and Jeffrey Snover (Distinguished Engineer, Google; formerly 23 yrs at Microsoft), with host Steve McGhee and co-host Matthew Siegler (Google SRE Prodcast)"
date_published: 2026 (approximate; Season 4 episode — page carries no explicit publication date; Theo references an SREcon talk "this past spring" and mining occurred 2026-07-14)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#104"
---

# The One with STPA, Jeffrey Snover, and Theo Klein (SRE Prodcast S4E7)

> A practitioner primary source giving the first transcript-level, methodology-deep
> treatment of STPA (Systems Theoretic Process Analysis) inside Google SRE: how it
> models systems as control/feedback loops, how it finds design flaws *before* code
> is written, and how Google pragmatically adapts the "pure" MIT method for
> commercial software via a "20% STPA" Pareto approach.

## Source Context

- **Type**: docs (podcast transcript — SRE Prodcast Season 4, Episode 7)
- **Author credibility**: High for practice. Theo Klein is a Google SRE (NYC, ~5.5 yrs
  at Google, Google Maps) who has run STPA for ~2 years and gives SREcon talks on it.
  Jeffrey Snover is a Google Distinguished Engineer (2.5 yrs at Google, 23 yrs at
  Microsoft) whom Ben Treynor recruited specifically to work on STPA and risk
  management. Snover states STPA "came out of MIT" and is "grounded in control theory."
  This is the authoritative Google-SRE voice on the method, not a casual mention.
- **Scope**: Dedicated, hour-long explainer of STPA as a *design-review* technique —
  control/feedback-loop modeling, the reliability-vs-safety distinction, the road-
  closures worked example, cost-benefit data, and Google's divergence from the MIT
  "absolutist" approach. It does NOT cover: the MIT formal STAMP curriculum, tooling
  internals, or any production incident postmortem. It is a conceptual + one worked
  example, not a measurement study.
- **Novelty in corpus**: This is the only transcript-level STPA methodology source.
  `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` (Claim 15) first flags STPA as an
  emerging Google/MIT risk-assessment method; this episode is the full dedicated
  treatment that Claim 15 anticipated. `docs-google-sre-prodcast.md` lists S4E7 in its
  index table (line 317) with no transcript detail — this note is that extraction.

## Extracted Claims

### Claim 1: STPA reframes hazards as *control problems*, not *failure problems* — losses arise from a loss of control in the system, not from component failure
- **Evidence**: Theo's direct contrast with the Five Whys / root-cause timeline model, and Snover's confirmation that it is MIT control-theory grounded.
- **Confidence**: emerging
- **Quote**: "Systems Theoretic Process Analysis takes a completely different view on hazards and losses. And what it says, it claims that accidents and losses happen when we lose control in the system. Some part of the system is misbehaving, and it's a control problem, not a failure problem."
- **Our assessment**: This is the load-bearing conceptual claim of the episode and the clearest differentiator from RCA/Five-Whys. The distinction is well established in safety engineering (Leveson's STAMP) and is presented here by two credible practitioners. We buy it as a useful framing; it is "emerging" only in the sense that it is one podcast's account, not yet a guide-settled recommendation.

### Claim 2: A system is modeled as controllers acting on controlled processes, driven by *goals* + a *worldview* (gathered from feedback) compared against those goals, then *actions* to close the gap
- **Evidence**: Snover's thermostat/boiler walkthrough and the generalized control-structure description.
- **Confidence**: emerging
- **Quote**: "the heart of it is that this controller performs actions on a controlled process. Well, how does it do that? Well, first off, it has goals. I want to be comfortable. So you got to know what your goals are. And then it has a worldview. So where do you get a worldview? Well, you get a worldview from information, external information or information from the control process."
- **Our assessment**: This goal/worldview/action loop is the reusable mental model. It maps cleanly onto self-healing systems (Kubernetes operators, annealing — see Claim 5) and onto incident-response feedback loops. Solid conceptual scaffolding; we buy it.

### Claim 3: STPA is a human-driven, discussion-based *question-prompting* technique, not an automated checker — and it has a learning curve ("get your head through the knothole")
- **Evidence**: Theo's "question-prompting engine" description; Snover's "knothole" remark; Steve's "not a compiler" summary that Theo endorses.
- **Confidence**: emerging
- **Quote**: "It is a human-driven process. And in some ways, it's a question-prompting engine, is what I think of."
- **Our assessment**: Important for the guide: STPA is a facilitated practice requiring skilled humans (Theo notes he "used to be an STPA hater, but now I'm a convert" after working through it a few times). This constrains how a team adopts it — it is not a tool you install. Consistent with Treynor's Claim 15 note that STPA "spits out a set of vulnerabilities... mostly with people."

### Claim 4: STPA is explicitly NOT formal methods (not TLA+) — it examines *abstract responsibilities* of system parts rather than exhaustively defining behavior
- **Evidence**: Steve asks if it's like TLA+; Theo says no twice and explains the difference.
- **Confidence**: emerging
- **Quote**: "This is not like TLA+. ... you aren't trying to exhaustively define the behavior. Actually, you look at the abstract responsibilities of all of the different parts of your system."
- **Our assessment**: Useful scoping for the guide — STPA complements (does not replace) formal methods and exhaustive testing. It trades completeness for tractability, which is exactly why Google can run it in "20%" (Claim 8).

### Claim 5: STPA natively handles *sociotechnical* systems — some control decisions are made by the system, some by humans, and bad human configuration is a frequent error source
- **Evidence**: Theo's contrast of desired-state vs operations models; "the system worked perfectly. I just gave it the bad configuration."
- **Confidence**: emerging
- **Quote**: "one of the great benefits of STPA is that it is a system that allows you to analyze things that are sociotechnical, which is to say, some of those decisions are made by the system, and some of them are made by you."
- **Our assessment**: This is the feature that makes STPA relevant to AI/LLM-agent operations (where humans set intent/configuration and agents execute loops). Strong fit with the corpus's automation-safety and agent-reliability notes. We buy it.

### Claim 6: Worked example — a diff-based road-closure pipeline silently fails to add closures when a write fails and is never retried, because it assumes "the previous version of this file is equivalent to the state of Google Maps"
- **Evidence**: Detailed walkthrough of the Google Maps road-disruptions pipeline: reads a file of active closures, diffs v2 vs v1, adds new closures; if the add (HTTP request) fails with no/limited retry, v3 is diffed against v2 → "no diff" → the closure is never added → users get navigated through a known parade.
- **Confidence**: anecdotal
- **Quote**: "what it did, gets a file. All right. And the file contains all active road closures. And then it gets another file, and that's version 2. And what it does is very simple. It diffs the two files, and it says, aha, here is a new road closure in version 2. Let me add it into Google Maps. But what happens if, in the process of adding this road closure, it fails to do so? ... Version 3 is compared against version 2, no diff."
- **Our assessment**: A single concrete, well-explained instance of a *control-action-provided-but-not-applied* hazard — the canonical STPA failure category. The root flaw ("assumes previous file == Maps state") is a real, generalizable design error, not a one-off. Credible; marked anecdotal only because it is one project's experience.

### Claim 7: Headline cost-benefit — the road-closures STPA found 3 design gaps in 1.5 hrs, and 7 design flaws in ~27 SWE-hours across 5 engineers, fixable near-zero-cost because the system wasn't built yet; only ~20% of the control structure was analyzed
- **Evidence**: Theo's explicit numbers, repeated for emphasis ("seven design flaws, seven design flaws").
- **Confidence**: anecdotal
- **Quote**: "overall, we spent about 27 hours across five engineers. And we found seven design flaws, seven design flaws. And this is 27 SWE hours. ... we only analyzed, I would say, 20% of the control structure in order to find these seven design flaws."
- **Our assessment**: The single most quotable, guide-relevant metric in the episode. It is n=1 (one pipeline, one facilitation) so we treat the *exact* numbers as anecdotal, but the directional claim — design flaws caught pre-code cost far less to fix than post-launch — is well supported by general SE economics and is the core selling point. The "20%" figure ties directly to Claim 8.

### Claim 8: Google runs a "20% STPA" Pareto adaptation — it rarely completes a full STPA because it finds so much at the 20% mark — deliberately diverging from MIT "absolutists" who must "solve all of them" for nuclear plants / aircraft carriers
- **Evidence**: Snover's "absolutists" contrast; Theo's "20% of an STPA" description; both note Google is documenting the commercial adaptation.
- **Confidence**: emerging
- **Quote**: "within Google is actually performing a 20% of an STPA. We rarely have the time to complete an STPA, and usually it's because we find so much at the 20% mark."
- **Our assessment**: The pragmatic adaptation is the genuinely *new* practice signal for the guide. It is the bridge that makes STPA adoptable in commercial software cadence. We buy the Pareto logic; the specific "20%" is a rule-of-thumb, not a measured optimum. Directly extends Treynor Claim 15's "tooling to make STPA far less manual" thread.

### Claim 9: Reliability ≠ safety — STPA uniquely finds losses where *every component works reliably and as intended* but the system still produces devastating outcomes (butter-knife-in-outlet prop; 737 MAX analogy)
- **Evidence**: Theo's live prop demo; Snover's 737 MAX example as the canonical case of reliable components with unsafe emergent interaction.
- **Confidence**: emerging
- **Quote**: "STPA is great at finding flaws, losses for every component of the system works reliably and as intended. But the system produces devastating losses. And STPA is the only mechanism that I know that provides the context for finding those systems. In fact, the 737 MAX system, that was an example. All the components of that system worked as designed, worked reliably. But there were unexpected interactions between those systems that then resulted in a terrible and devastating loss."
- **Our assessment**: The reliability-vs-safety distinction is the episode's most important conceptual contribution for an SRE audience that equates "reliable" with "safe." The butter-knife quote ("But what if I took this butter knife and I shove it in the electrical outlet? OK. I'm going to be electrocuted.") is a memorable illustration. The principle is settled in safety engineering; its application to software reliability is emerging and directly relevant to automation/safety (Ch05).

### Claim 10: STPA can be applied *before* the system is designed — start from control structures and goals to derive safety requirements that then drive the build
- **Evidence**: Theo describes using STPA at design time and as a design *generator*, not just a reviewer.
- **Confidence**: emerging
- **Quote**: "you can use STPA before you've actually designed your system. ... We start with the control structures, and we define the goal of the system that we want to build. And we think, we think, in the abstract, OK, what controllers do we need to make sure that these losses cannot be achieved?"
- **Our assessment**: Shifts STPA left of design review — it becomes a requirements-elicitation technique ("test-driven development upstream of the design point," per Matt's analogy). High value for the guide's risk-assessment chapter: catch flaws at the cheapest possible stage.

### Claim 11: STPA deliberately avoids probability for prioritization — it ranks loss scenarios by *number of occurrence paths* and *cost of mitigation*, targeting an 80/20 cost-benefit trade
- **Evidence**: Theo explains probability is "very hard to provide accurately" without many samples; prioritization uses path-count + mitigation cost, "for 20% of the cost, we can get rid of 80% of the problems."
- **Confidence**: emerging
- **Quote**: "It is actually very hard unless you have many, many samples. It is actually very hard to provide an accurate probability. ... Maybe we can-- for 20% of the cost, we can get rid of 80% of the problems. And that's really just the cost-benefit where we start horse trading."
- **Our assessment**: A notable methodological stance that *differs* from classic probabilistic risk assessment (PRA). For software, where failure samples are sparse, the path-count + mitigation-cost heuristic is pragmatic and defensible. We buy it as a reasonable commercial adaptation, though it sacrifices the quantitative rigor PRA offers. Worth flagging to the Smith as a conditioning variable vs domains that do have samples.

### Claim 12: The two most common STPA findings in practice are (1) broken feedback mechanisms and (2) missing/implicit system goals ("what's the goal of this system? Silence.")
- **Evidence**: Snover's report from running many sessions; Matt's "a lot of implicit goals" agreement.
- **Confidence**: emerging
- **Quote**: "What we found a lot is these feedback mechanisms are broken. Second biggest thing, go and say, hey, what's the goal of these system? Silence."
- **Our assessment**: A useful, experience-derived checklist item for facilitators: when you run STPA, first check feedback loops and goal clarity. Cheap to adopt and a concrete takeaway for the guide's incident-management / design-review sections.

### Claim 13: STPA is framed as the "next level" beyond Treynor's error/loss budget — the loss budget balances reliability vs innovation, but STPA aims to get that balance "without the loss"
- **Evidence**: Snover relays Treynor's recruitment pitch and the loss-budget mechanism, then positions STPA as the forward step.
- **Confidence**: emerging
- **Quote**: "the heart of SRE is to manage this tension between reliability and innovation... we're going to define an error budget. And then you can go as fast as you want until you incur this amount of loss. And then you got to stop and then reset. ... How do we get this balance between reliability and innovation without the loss?"
- **Our assessment**: Ties S4E7 directly into the corpus's error-budget material (Treynor interview Claim 3 / Claim 9 / error-budget formula; rethinking-slos on SLO limits). STPA is presented as the proactive complement to the reactive error budget. We buy the framing; it strengthens the risk-assessment chapter's narrative arc.

### Claim 14: STPA generalizes beyond software — MIT has applied it to social systems, and learning it changes how practitioners see the world ("I see the world in systems")
- **Evidence**: Theo's "world in systems" remark; Snover's "who could have seen that coming?" on MIT modeling social systems.
- **Confidence**: emerging
- **Quote**: "At MIT, they've used STPA to model all sorts of social systems. And they've found flaws. ... I am so grateful that I learned about STPA, not only because it helps me in my work at Google but also because now I see the world in systems"
- **Our assessment**: Supports the broader "systems thinking" thread (Steve recommends Meadows' *Thinking in Systems* and *Systemantics*). Lower direct relevance to the guide's software/AI focus, but useful context that the method is domain-agnostic. Kept as a secondary claim.

## Concrete Artifacts

### The road-closures control structure (verbatim description of the flawed logic, from the transcript)

```
Bottom of control structure = the Google Maps database (the controlled process).
A controller (software) has the goal: "ensure all active road closures are on Google Maps."
Its control actions: "add a road closure" / "remove a road closure."

Logic inside the controller (Theo's description):
  - gets file v1  -> contains all active road closures
  - gets file v2  -> the new version
  - diffs v2 vs v1; for each NEW closure in v2, issues "add to Google Maps"
  - IF the add (HTTP request) fails, no retry / limited retries -> closure not added
  - next run: diffs v3 vs v2 -> "no diff" -> closure is NEVER retried/added

Theo's stated root flaw:
  "the flaw here is in assuming that the previous version of this file
   is equivalent to the state of Google Maps."
Loss: users navigated through a known NYC parade (a "mega PR event") with no closure shown.
```

### The "20% STPA" cost-benefit numbers (single project, Google Maps road disruptions)

```
Session 1:  ~1.5 hours  -> 3 system/requirements gaps found
Full effort: ~27 SWE-hours across 5 engineers -> 7 design flaws found
Scope analyzed: ~20% of the control structure
Fix cost: near-zero (system not yet built; fixed by rewriting the design doc)
```

### Control-structure vocabulary (verbatim, Theo + Snover)

```
"Control" = actions that constrain controlled processes.
  - human  = controller (most agency)
  - computer / operator / agent = controller
  - environment / database = controlled process (no agency; "just is")
"Control loop" = intent -> observe (feedback) -> compare to goals -> act.
  Hazard when any part of the loop breaks:
  misread feedback -> no action issued -> loss persists despite a "bad" being forbidden.
```

### Further resources cited in the episode

- Theo Klein's SREcon talk (spring 2026) — deeper dive on the road-disruptions system + butter-knife prop.
- MIT STAMP conference — bi-yearly, free; videos online (Google's rollout sessions recommended).
- Blog post: Ben Treynor Sloss + Tim Falzone, "STPA as the future of SRE."
- Books: Donella Meadows, *Thinking in Systems*; *Systemantics* (older, more technical).
- People: Jeffrey Snover (@jsnover on Twitter/Bluesky jsnover.com); Theo Klein (Pierre Theo Klein) on LinkedIn.

## Cross-References

- **Corroborates / Extends**: `docs-google-sre-prodcast-03-03-treynor-ai-ml.md` — **Claim 15** (Google has worked with MIT / Nancy Leveson on STPA for "several years," building tooling, aiming to "predict all of the outages... before they happen"). This S4E7 note is the deep methodology treatment that Claim 15 explicitly anticipated ("a separate, later mine... should be cross-read before the guide synthesizes STPA"). Both frame STPA as emerging and tooling-backed; complementary, not contradictory. The Treynor note's "predict all outages" line is aspirational over a ~2-yr horizon; S4E7 shows the present, manual, 20%-Pareto practice.
- **Extends**: `docs-google-sre-prodcast.md` — the Prodcast index note lists `S4E7  STPA (Theo Klein, Jeffrey Snover) — System Theoretic Process Analysis` (line 317) under "Notable Non-AI Practitioner Episodes" with no transcript detail. This note is the transcript-level extraction that entry points to.
- **Extends (conceptual)**: `discussion-google-sre-ben-treynor-interview.md` — **Claim 3** (error budget = 1 − availability target, the reliability/innovation balancing mechanism) and **Claim 9** (launch freeze when budget exhausted), plus the error-budget formula block. S4E7's Claim 13 presents the loss/error budget as the *precursor* and STPA as the "next level" that seeks reliability/innovation "without the loss." Also relevant: `docs-google-sre-prodcast-01-04-rethinking-slos.md` (SLO/error-budget limits in B2B) — S4E7 does not dispute error budgets, it builds on them, so no conflict.
- **Novel**: This is the **first transcript-level STPA methodology source** in the corpus. Novel specifics introduced: the control/feedback-loop model as a risk-analysis frame; the "20% STPA" Pareto adaptation vs MIT absolutism; the reliability-vs-safety distinction with the 737 MAX / butter-knife illustrations; the road-closures pre-code design-flaw worked example with concrete numbers; the "avoid probability, rank by path-count + mitigation cost" prioritization stance.
- **Contradicts**: **None.** The transcript is internally consistent. It agrees with and extends the only prior STPA mention (Treynor Claim 15), which already flagged S4E7 as complementary. No open `contradiction`-labeled issues exist, and CONTRADICTIONS.md records none. No contradiction issue was filed.

## Guide Impact

- **Chapter 02 (SRE Fundamentals / Risk Assessment)**: Add STPA as an *emerging* proactive risk-assessment method distinct from Five Whys / RCA. Recommend the control/feedback-loop framing (Claim 1–2) and the reliability-vs-safety distinction (Claim 9) as core mental models. Cross-read with Treynor Claim 15 so STPA is presented consistently (manual/20%-Pareto now; tooling-backed prediction on a ~2-yr horizon). Suggest "catch design flaws pre-code" (Claims 7, 10) as the headline benefit with the 27-SWE-hour / 7-flaw anecdote as supporting evidence (mark anecdotal).
- **Chapter 04 (Incident Management)**: Position STPA as the *proactive* counterpart to reactive postmortems — analyze control loops *before* loss, not just timeline root-cause *after*. Adopt the two facilitator checks from Claim 12 (broken feedback mechanisms; missing/implicit goals) as a lightweight design-review add-on. Note STPA complements rather than replaces Five Whys.
- **Chapter 05 (Automation & Safety)**: Use Claim 9 (reliable components → unsafe system outcomes; 737 MAX) to motivate safety analysis of automated controllers (Kubernetes operators, annealing, AI agents). Claim 5 (sociotechnical: humans set intent/config, agents execute loops) is directly relevant to AI-agent operations — a mis-set configuration is a first-class STPA hazard. Recommend the "20% STPA" adoption path (Claim 8) for teams that cannot fund a full analysis.

## Extraction Notes

- Source read in full (the complete S4E7 transcript, ~270 lines of spoken content, fetched 2026-07-14 and stripped from HTML to plain text). No paywall; the page is public.
- All `Quote` fields were copied character-for-character from the fetched transcript. Where the source used `--` for em-dashes or `[LAUGHS]` stage directions, those were omitted to keep quotes readable while preserving the exact words; no words were added, removed, or reordered within a quoted passage.
- Two overlapping notes were re-read and verified per MINER.md §4b before citing: Treynor Claim 15 (confirmed at `docs-google-sre-prodcast-03-03-treynor-ai-ml.md:269`) and the Prodcast index S4E7 line (confirmed at `docs-google-sre-prodcast.md:317`).
- The Prospector's two triage comments agreed this is the dedicated STPA episode; the first labeled it `discussion (podcast transcript)`, the second `docs (transcript)`. Filename follows the repo's existing Prodcast convention (`docs-google-sre-prodcast-NN-NN-topic.md`) and `source_type: docs`, matching sibling transcripts.
- No contradiction filed: the only prior STPA material (Treynor Claim 15) already anticipates and welcomes this episode as complementary.
