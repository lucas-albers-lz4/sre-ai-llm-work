---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-05-07/
source_type: docs
title: "The One with Carla Geisser and Crisis Engineering (SRE Prodcast S5E7)"
author: "Carla Geisser (ex-Google SRE 2004–2015, storage systems; founder, Layer Aleph — 'crisis engineering'); hosts Steve McGhee & Florian Rathgeber"
date_published: 2026 (est.; Season 5 episode — transcript page carries no explicit air date; Season 5 'More Friends, More Trends' aired in 2026, matching sibling S5 notes)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#188"
---

# The One with Carla Geisser and Crisis Engineering (SRE Prodcast S5E7)

> A practitioner's *framework* for distinguishing a **crisis** from a routine **incident**: a crisis is an event with no usable playbook, diagnosed by a five-criteria taxonomy (fundamental surprise, broken critical functions, high visibility, rigid deadline, perception breakdown) in which leadership will only "break rules" and enable substantive change once **three of the five** criteria are met. The novel contribution to the corpus is the *playbook-boundary / escalation* model — the condition under which the standard incident-management process (Walcer's IMAG) no longer applies and organizational override is required.

## Source Context

- **Type**: docs (official Google SRE published podcast transcript) — SRE Prodcast Season 5, Episode 7, hosted by Steve McGhee and Florian Rathgeber. Guest: Carla Geisser.
- **Author credibility**: Carla Geisser was a Google SRE from 2004 to ~2015, "mostly on storage systems," and notes "there's a quote from me in the SRE book" (the canonical Google SRE book). She now runs **Layer Aleph**, a company that does "crisis engineering" — technical crisis management / incident response sold mainly to state governments and occasionally to private companies facing a "planned crisis" (e.g., an acquisition). The five-criteria model is Layer Aleph's *own* taxonomy, which she says was "back computed" from real engagements (healthcare.gov, federal/state government systems) where leadership said "we definitely need to do something" and then "nothing changed." This is a primary-source practitioner framework, not a secondary summary, published on the official sre.google domain.
- **Scope**: A conceptual model for *recognizing and declaring* a crisis and for understanding why organizational behavior only shifts at a tipping point. Covers: the crisis-vs-incident boundary, the five named criteria, the three-of-five rule, who declares a crisis, manufactured crises, the organizational root causes (failure to admit computers control decisions; the "stack of complexity" migration anti-pattern), the SRE skills that make crisis work possible, and crises as part of the organizational change cycle. It does **not** contain AI/LLM content, code, configs, metrics, or quantitative failure data — it is a conversational episode about general SRE/organizational practice.
- **Note on AI relevance**: This source has zero AI/LLM content. Its value to an AI/SRE guide is *structural*: it supplies a concrete escalation framework (crisis = playbook exhausted) that the corpus's incident-management notes (Walcer S1E8, S3E6 tooling) assume but do not model, and a sensemaking-failure vocabulary ("perception breakdown") that maps onto the context-poisoning risks AI incident agents face (PagerDuty gaps). Every AI connection drawn below is the Miner's analytical synthesis, clearly marked, not a claim from the source.

## Extracted Claims

### Claim 1: A crisis is distinguished from an incident by the absence of a usable playbook — incidents have "page 37 in the manual," crises do not
- **Evidence**: Geisser draws the boundary explicitly; Florian Rathgeber restates it as "an incident is something you either have a playbook or you could reasonably have a playbook. And for a crisis, you couldn't."
- **Confidence**: settled (stated as a definitional boundary by the source)
- **Quote**: "The place that I draw the boundary is that an incident is a thing where there is probably some set of instructions you can pull off the shelf that is maybe a similar thing that has happened before, or even a full on playbook, because it happens often enough. And you can turn to page 37 in the manual and say, now I'm going to follow these steps, obviously with modifications, because it's not going to be quite the same. But there is a playbook that exists typically for a thing that is an incident but not yet a crisis." — and — "So an incident is something you either have a playbook or you could reasonably have a playbook. And for a crisis, you couldn't."
- **Our assessment**: This is the spine of the episode and the most useful boundary definition in the corpus for incident-vs-crisis. It directly extends `docs-google-sre-prodcast-01-08-incident-management.md` (Walcer's playbook-driven IMAG process): Geisser specifies the *condition under which that process no longer applies*. Settled as a definition, even though the taxonomy built on it is her firm's own.

### Claim 2: Criterion 1 — Fundamental surprise: the event is a truly novel experience for everyone involved
- **Evidence**: Geisser names and defines the first criterion; illustrates with a science-fiction framing ("Your cat wakes you up one morning… and tells you that the Earth is about to be invaded").
- **Confidence**: settled (stated definition)
- **Quote**: "The first one is fundamental surprise, which is, this is a thing that is a novel experience for everyone, and it has to be truly novel."
- **Our assessment**: Clear, if vividly illustrated. The "has to be truly novel" qualifier matters — it is what excludes predictable, recurring events (see Claim 8 / Claim 15 on planned crises). For an AI guide, this is the "we have never seen this failure mode" signal that should trigger crisis-level escalation rather than routine runbook handling.

### Claim 3: Criterion 2 — Broken critical functions: something core to the business is not happening right now
- **Evidence**: Geisser: "Something that is core to your business is not happening right now. That one's easy." She notes it is "the one we typically have in any crisis and in most incidents."
- **Confidence**: settled (stated definition)
- **Quote**: "Broken critical functions is another one. That one's the one we typically have in any crisis and in most incidents. Something that is core to your business is not happening right now. That one's easy."
- **Our assessment**: The most routine of the five — Geisser herself says it appears in most incidents too, so on its own it is not a crisis signal; it is a necessary-but-not-sufficient criterion. Useful as the baseline "is core function impaired?" check in a crisis checklist.

### Claim 4: Criterion 3 — High visibility: people (internal or external, especially news media) are watching the outcome
- **Evidence**: Geisser: "people are watching the outcome of this thing… If the news media is involved, obviously that is definite high visibility." Florian summarizes the internal flavor as "every meeting becomes about this incident."
- **Confidence**: settled (stated definition)
- **Quote**: "The other one is high visibility. So people are watching the outcome of this thing. And that can be either an internal thing or an external thing, particularly inside a large organization. The thing you might start to experience is that every meeting becomes about this incident, even if it originally was not meant to be about this incident. If the news media is involved, obviously that is definite high visibility."
- **Our assessment**: The "external attention / exec attention" criterion. For AI-production incidents this is the "customer-visible or regulator-visible" signal. Note Geisser treats internal visibility (meetings hijacked) and external (media) as both counting — relevant to how an org decides a near-miss has become a crisis.

### Claim 5: Criterion 4 — A rigid deadline: a *real* external deadline counts; internal tech-company deadlines "don't count" (they "move all the time")
- **Evidence**: Geisser: "Holiday shopping season, streaming for the Super Bowl, launching a satellite. Those are real deadlines. Internal tech company deadlines don't count." Steve: "They don't count. OK, good to know." Geisser: "those are fake and made up, and they move all the time."
- **Confidence**: settled (stated definition) — though the "internal deadlines don't count" stance is a strong normative claim worth flagging
- **Quote**: "A rigid deadline, like a real, actual deadline. Holiday shopping season, streaming for the Super Bowl, launching a satellite. Those are real deadlines. Internal tech company deadlines don't count." — and — "Yeah, those are fake and made up, and they move all the time, as we know."
- **Our assessment**: The most opinionated of the five. The criterion correctly distinguishes *externally-imposed, immovable* deadlines (regulatory filings, seasonal peaks, launch events, satellite windows) from internal roadmap dates that slip. The flat "internal deadlines don't count" is a useful shock to org behavior, but is a normative stance, not an empirical law — an internal deadline (e.g., a contractual SLA with a major customer) can absolutely function as a rigid deadline in practice. Flag as the source's strong phrasing rather than universal truth.

### Claim 6: Criterion 5 — Perception breakdown / failure of sensemaking: the org cannot produce a useful picture because information is late, noisy, overwhelming, or contradictory across parts of the org
- **Evidence**: Geisser defines the fifth criterion and gives the canonical micro-example "it works on my machine. That's the beginning of perception breakdown." Florian likens it to "headless chicken syndrome."
- **Confidence**: settled (stated definition)
- **Quote**: "And then the final one is hard to talk about. It's what we call perception breakdown or a failure of sense making. This is when the people are unable to produce a useful picture of what is going on, because either the information they're getting is late, or it's noisy, or it's overwhelming, or different parts of the organization are seeing different things happening. The simplest version is it works on my machine. That's the beginning of perception breakdown."
- **Our assessment**: The richest criterion and the one with the clearest AI mapping. "Different parts of the organization are seeing different things" is the organizational-scale version of the context-poisoning failure mode AI agents exhibit (`blog-pagerduty-production-ai-agent-gaps.md` Claim 6). For the guide, perception breakdown is the sensemaking-failure that an AI incident agent must be guarded against (shared correct context, invalidation-aware memory). See Cross-References.

### Claim 7: The "three-of-five" tipping point — leadership will only "break rules," move faster, and approve exceptions once at least three of the five criteria are met; below that, "nobody's behavior is going to change"
- **Evidence**: Geisser ties the criteria directly to leadership action; states the threshold twice ("using those criteria I described earlier" → break rules; and "until you hit three of those five criteria, nobody's behavior is going to change").
- **Confidence**: settled (stated thesis of the episode)
- **Quote**: "if a crisis is happening, you can do interesting and novel things, because leadership is going to be willing to do-- they're going to be willing to break rules. They're going to be willing to move faster. They're going to be willing to approve exceptions if you're in a real crisis using those criteria I described earlier. If you're not in a real crisis." — and — "You can absolutely take notes and start to learn how the system works and build up your allies who will help you when the crisis actually happens. But until you hit three of those five criteria, nobody's behavior is going to change."
- **Our assessment**: The single most actionable output of the episode: a concrete escalation trigger (≥3/5) for when to expect — and demand — organizational override (cross-team authority, rule exceptions, exec air-cover). This is exactly the gap in the corpus's incident-management notes: Walcer (S1E8) describes the playbook process but not the condition for escaping it. High-value for Ch04.

### Claim 8: Not all five criteria are required — "You only need most of them, not all of them"
- **Evidence**: Florian asks whether a predictable (non-novel) event still fits; Geisser: "Doesn't have to. You only need most of them, not all of them." She illustrates with the holiday-shopping example: "It's definitely not novel, but it's high visibility, definitely deadline, and probably going to cause a breakdown in understanding… And risk of broken core functions also always there. So you got most of them."
- **Confidence**: settled (stated refinement of the rule)
- **Quote**: "Doesn't have to. You only need most of them, not all of them." — and — "It's definitely not novel, but it's high visibility, definitely deadline, and probably going to cause a breakdown in understanding of how your system works. Pretty likely. And risk of broken core functions also always there. So you got most of them."
- **Our assessment**: An important qualifier to Claim 7 — the threshold is *majority of five*, not all five, and novelty (Criterion 1) can be absent for a *predictable* crisis (see Claim 15). Prevents the framework from being too rigid to apply to recurring, known events.

### Claim 9: The pragmatic "don't-waste-your-time" advice — until the tipping point you just do your normal job; quietly prepare (take notes, learn the system, build allies) but expect no behavior change
- **Evidence**: Geisser: "If you're not in a real crisis… You just have to do your job like a normal person. And you can be mad at everything that's going on that is definitely going to be a crisis someday. But nothing special is going to happen until you hit that tipping point."
- **Confidence**: settled (stated advice)
- **Quote**: "If you're not in a real crisis. You just have to do your job like a normal person. And you can be mad at everything that's going on that is definitely going to be a crisis someday. But nothing special is going to happen until you hit that tipping point. And so I think that is the both useful and also pragmatic and depressing advice… You can absolutely take notes and start to learn how the system works and build up your allies who will help you when the crisis actually happens. But until you hit three of those five criteria, nobody's behavior is going to change."
- **Our assessment**: A de-escalation heuristic that is genuinely useful for incident programs: don't burn political capital elevating every near-miss to "crisis." Prepare quietly until 3/5. Counterbalances alarm-fatigue and premature exec escalation. Strong candidate content for Ch04.

### Claim 10: Who declares the crisis — within an org there must be someone with power who is "scared enough to be willing to break rules"; the criteria were reverse-engineered from engagements where nothing changed
- **Evidence**: Geisser (as external consultant, their signal is "somebody has decided to pay the four of us to come help them"). Internally: "there has to be someone who is, frankly, scared enough to be willing to break rules… someone who has the levers on power needs to be willing to do something new." The taxonomy was "back computed… from the experience of places where someone said, this is really important, we definitely need to do something. And we were like, OK, we will definitely help you do something. And then nothing changed."
- **Confidence**: settled (stated model of declaration)
- **Quote**: "Within an organization, there has to be someone who is, frankly, scared enough to be willing to break rules. And so you can nudge them using the information you have. But ultimately, someone who has the levers on power needs to be willing to do something new." — and — "we kind of back computed the crisis criteria from the experience of places where someone said, this is really important, we definitely need to do something. And we were like, OK, we will definitely help you do something. And then nothing changed."
- **Our assessment**: Frames crisis *declaration* as a power/authority act, not a mechanical severity label. This complements `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 10–11 (severity as an organizational construct / a lever that unlocks authority) — Geisser says the *crisis* label is the stronger lever that unlocks rule-breaking, and it requires a frightened power-holder, not just a process.

### Claim 11: Manufactured crises — senior leaders invent a hard deadline (e.g., canceling a data-center contract) to force a slow migration faster; it "can become a manufactured crisis" but is a trust-burning "dark art" Geisser dislikes
- **Evidence**: Example: "we're moving everything to the cloud. We have ended our contract with our data center provider two years from now." Geisser: "Congratulations. You have a hard deadline." She calls manufacturing crises "a management technique that senior leaders definitely try to get the migration to move faster" and warns "it might work once and then it burns any trust with the people in leadership after that." She: "I personally do not like that approach. I consider it to be kind of a dark art."
- **Confidence**: emerging (practitioner observation; single illustrative example)
- **Quote**: "it is a management technique that senior leaders definitely try to get the migration to move faster, and it can become a manufactured crisis. I think the risk there is that everybody saw you do it. And so it might work once and then it burns any trust with the people in leadership after that." — and — "I personally do not like that approach. I consider it to be kind of a dark art."
- **Our assessment**: A candid, useful caution about weaponizing the crisis framework. Note the tension with Claim 5 (internal deadlines "don't count"): a *manufactured* hard deadline is precisely an internal deadline the leader insists counts. Geisser resolves this implicitly — the manufactured deadline only "works" (creates real crisis pressure) if the org believes it; the trust cost is the catch. Conditioning variable, not a contradiction: Claim 5 describes which deadlines *naturally* qualify; Claim 11 describes *forcing* one.

### Claim 12: Organizational root cause — many orgs (esp. government) "have not yet admitted that the computer is actually controlling all the decisions," producing perception breakdown; the telltale sign is holding "the controller from five iterations ago"
- **Evidence**: Geisser: "a lot of organizations have not yet admitted that to themselves… they haven't yet gotten to the place where they understand that the computer is actually controlling all the decisions. They still think there is a policy working group that can control what is happening." On perception breakdown: "one of the kinds of perception breakdown you see is information that is out of date or stale… the people who think they have their hands on the controls are holding the controller from five iterations ago. And so it's not actually connected to anything that drives anymore."
- **Confidence**: emerging (practitioner generalization from government work; anecdotal)
- **Quote**: "a lot of organizations have not yet admitted that to themselves… they haven't yet gotten to the place where they understand that the computer is actually controlling all the decisions." — and — "the people who think they have their hands on the controls are holding the controller from five iterations ago. And so it's not actually connected to anything that drives anymore."
- **Our assessment**: A pithy organizational-dysfunction diagnosis. "Holding the controller from five iterations ago" is a memorable artifact for the *stale mental model* failure mode — the human analog of context-poisoning (PagerDuty gaps Claim 6). Useful for the guide as the organizational origin of perception breakdown (Criterion 5). Emerging because it is a generalization from Geisser's government engagements, not a studied claim.

### Claim 13: The "stack of complexity" anti-pattern — decade-long migrations never finish, leaving "basically one of each kind of technology that has ever been popular over the last 20 years" glued onto the side of the original system
- **Evidence**: Geisser: "what instead they have built is a stack of complexity where about every five years, they take whatever is the hot new technology, build a few new things in that, and then get distracted and never complete that migration. So now they have basically one of each kind of technology that has ever been popular over the last 20 years." Mechanism: "they have a grand modernization scheme… they start with the grand modernisation plan and get about 60% of the way through. And then you just have a hodgepodge of stuff that's glued onto the side. And you still have the original system, and now you have this other stuff."
- **Confidence**: emerging (practitioner observation; recurring anecdote)
- **Quote**: "what instead they have built is a stack of complexity where about every five years, they take whatever is the hot new technology, build a few new things in that, and then get distracted and never complete that migration. So now they have basically one of each kind of technology that has ever been popular over the last 20 years." — and — "they start with the grand modernisation plan and get about 60% of the way through. And then you just have a hodgepodge of stuff that's glued onto the side. And you still have the original system, and now you have this other stuff."
- **Our assessment**: A vivid, concrete anti-pattern that corroborates the complexity-is-a-reliability-hazard thesis in `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 8 ("obtuse tooling that only half the team can use becomes a detriment") and `blog-pagerduty-production-ai-agent-gaps.md` Claim 8 (earn complexity) and `blog-pagerduty-sre-agent-architecture.md` Claim 16 (build hard, ship simple). Geisser supplies the *organizational origin* of that complexity — migration debt that is never retired. Strong Ch03 content (architecture/runbook sprawl caution).

### Claim 14: SRE-adjacent skills are central to crisis work — "connect the dots with no information," expose the full system end-to-end, "it always includes the people," and SREs are "encouraged to look in other lanes" (not "stay in your lane")
- **Evidence**: Geisser: "the ability to look at a very big system and start to connect the dots with no information. And the system includes the people often." The value: "building them a very clear map of what is going on right now from the beginning to the end of whatever their process is." On SREs: Steve "please do not tell an SRE to stay in their lane… we're actually encouraged to look in other lanes." Geisser: "that is a unique skill, especially in larger companies." Also: "we don't care what kind of computer is in there, as long as we can follow a chain of events. Anyone can run tcpdump. Anyone can look at a log file."
- **Confidence**: settled (stated practitioner view; consistent with SRE identity)
- **Quote**: "the ability to look at a very big system and start to connect the dots with no information. And the system includes the people often." — and — "a lot of the technical work we do is about exposing the full system to the people who can then make better decisions" / "building them a very clear map of what is going on right now from the beginning to the end of whatever their process is." — and — "please do not tell an SRE to stay in their lane. This doesn't work in our brains… we're actually encouraged to look in other lanes."
- **Our assessment**: Articulates the *human sensemaking* skill that is the complement to — and current limit of — AI incident agents. "Connect the dots with no information" and "expose the full system end-to-end" are exactly the capabilities AI agents lack when the playbook is gone (perception breakdown / context poisoning, PagerDuty gaps Claim 6). Useful framing for Ch01: automation fills the *playbook* regime; human-led sensemaking owns the *crisis* regime.

### Claim 15: Crises are part of the organizational change cycle — "you have to go through these moments periodically for anything substantive to change" — and predictable crises warrant advance "tickets" that suspend the normal rules
- **Evidence**: Geisser: "this is actually part of the cycle of change inside of an organization. You have to go through these moments periodically for anything substantive to change." On predictable crises (e.g., holiday shopping): "there's a bunch of crises that are going to happen that you can predict, and you should just assume that you will have a brief suspension of the rules of engagement during that moment… your leadership will write you a ticket in advance that says, you are allowed to enforce and break the following rules in order to hit this special time of the year."
- **Confidence**: emerging (practitioner thesis about organizational change)
- **Quote**: "this is actually part of the cycle of change inside of an organization. You have to go through these moments periodically for anything substantive to change." — and — "there's a bunch of crises that are going to happen that you can predict, and you should just assume that you will have a brief suspension of the rules of engagement during that moment… your leadership will write you a ticket in advance that says, you are allowed to enforce and break the following rules in order to hit this special time of the year."
- **Our assessment**: Two distinct, useful ideas. (a) The change-cycle thesis: crises are *necessary and periodic*, not purely avoidable — a counterweight to pure prevention-only messaging (see Cross-References re: S1E8 Claim 10; conditioning variable, not contradiction). (b) The predictable-crisis "rule-suspension ticket" is concrete, actionable Ch04 content for known high-visibility windows (major launches, seasonal peaks, regulatory deadlines): pre-authorize the overrides so the crisis, when it arrives, is already armed.

## Concrete Artifacts

### The five-criteria crisis taxonomy (verbatim from Carla Geisser, SRE Prodcast S5E7)

```
A crisis requires a taxonomy of five elements (you need MOST of them, not all):

1. Fundamental surprise  — a truly novel experience for everyone involved.
2. Broken critical functions — something core to your business is not
                             happening right now.
3. High visibility       — people are watching the outcome (internal meetings
                             hijacked, or news media involved = definite).
4. Rigid deadline        — a REAL, external deadline (holiday shopping,
                             Super Bowl stream, satellite launch).
                             Internal tech-company deadlines "don't count"
                             — "those are fake and made up, and they move
                             all the time."
5. Perception breakdown / failure of sensemaking — the org cannot produce a
                             useful picture: info is late, noisy, overwhelming,
                             or different parts see different things.
                             "The simplest version is it works on my machine.
                              That's the beginning of perception breakdown."
```
*Source: Carla Geisser, SRE Prodcast S5E7 transcript (the five named criteria).*

### The three-of-five tipping-point rule (verbatim from Carla Geisser)

```
Leadership will only "break rules," move faster, and approve exceptions
ONCE at least THREE of the five criteria are met.

  "if you're in a real crisis using those criteria I described earlier...
   they're going to be willing to break rules. They're going to be willing
   to move faster. They're going to be willing to approve exceptions."

  "But until you hit three of those five criteria, nobody's behavior
   is going to change."

You only need MOST of them, not all of them. (A predictable, non-novel
event like holiday shopping can still qualify on visibility + deadline +
likely perception breakdown + broken-function risk.)
```
*Source: Carla Geisser, SRE Prodcast S5E7 transcript (the escalation / tipping-point thesis).*

### The "stack of complexity" anti-pattern (verbatim from Carla Geisser)

```
Orgs blame the oldest system (often a mainframe) and launch a "grand
modernization scheme," but get ~60% of the way through, then:

  "you just have a hodgepodge of stuff that's glued onto the side.
   And you still have the original system, and now you have this other stuff."

Repeat every ~5 years with "whatever is the hot new technology" and:

  "now they have basically one of each kind of technology that has ever
   been popular over the last 20 years."
```
*Source: Carla Geisser, SRE Prodcast S5E7 transcript (government / large-corporation migration anti-pattern).*

### The "controller from five iterations ago" perception-breakdown tell (verbatim from Carla Geisser)

```
On orgs that haven't admitted "the computer is actually controlling all
the decisions":

  "the people who think they have their hands on the controls are holding
   the controller from five iterations ago. And so it's not actually
   connected to anything that drives anymore."
```
*Source: Carla Geisser, SRE Prodcast S5E7 transcript.*

## Cross-References

- **Extends**:
  - `docs-google-sre-prodcast-01-08-incident-management.md` — Walcer's note defines the *incident* process that assumes a playbook and a functioning IC structure exist: Claim 5 (IMAG — "incidents are an issue that have been escalated and require immediate, continuous, organized response"), Claim 8 ("by using a shared and clearly defined process, we build really positive emergency response habits… a clear chain of command"), and Claim 13 (responders "internalize best practices as habits so responders don't rely on looking up a playbook"). Geisser's framework (this note, Claims 1 & 7) is the **escape boundary** for that process: when ≥3/5 criteria hold, *there is no playbook* (Claim 1) and organizational override — leadership "breaking rules" — is required (Claim 7). Walcer describes the normal-incident regime; Geisser specifies the condition under which it no longer applies. This is precisely the gap the Prospector flagged: the corpus had playbook-driven response but not the *transition out* of the playbook into crisis. The mapping is direct: Walcer's "three C's" (Command/Control/Communications) are the playbook-era roles; Geisser's "someone with power scared enough to break rules" (Claim 10) is the crisis-era override authority.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 8 — "tools can't give you a working process… a tool becomes a detriment to the incident response process" if obtuse. Geisser's "stack of complexity" (Claim 13 here) is the *organizational origin* of that obtuseness: migration debt glued onto the original system makes the whole estate "a detriment." Same complexity-is-a-reliability-hazard thesis, supplied from the negative (human-systems) direction.

- **Corroborates**:
  - `blog-pagerduty-production-ai-agent-gaps.md` Claim 8 ("Agent architecture should evolve from single-agent → supervisor → hierarchical, **earning complexity rather than starting with it**") and `blog-pagerduty-sre-agent-architecture.md` Claim 16 ("Building the complex distributed version first was a deliberate methodology to understand which primitives were essential before simplifying for production"). Geisser's "one of each kind of technology… glued onto the side" (Claim 13) is the human-systems mirror image: complexity that was *never earned* and never simplified. The two notes reinforce the same "earn complexity / avoid glued-on sprawl" principle — PagerDuty from the AI-architecture positive, Geisser from the enterprise-negative.
  - `blog-pagerduty-production-ai-agent-gaps.md` Claim 6 — "Context poisoning — stale, corrupted, or contradictory data filling an agent's working memory — propagates errors across agents and systems." Geisser's perception breakdown (Claim 6 here; "different parts of the organization are seeing different things happening") and the "controller from five iterations ago" (Claim 12) are the *organizational sensemaking failure* that, at system scale, is exactly the context-poisoning risk. This note supplies the human-origin vocabulary the guide can use to motivate shared-correct-context guardrails (PagerDuty gaps Claim 14).
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 10–11 — severity as an organizational construct / a lever that unlocks authority and can be reclassified mid-incident. Geisser's crisis declaration (Claim 10 here) is the *stronger* lever: where severity unlocks teams/legal, the *crisis* label unlocks rule-breaking, and requires a frightened power-holder, not just a process. Consistent, not opposed.

- **Novel**: Material genuinely new to the corpus:
  - **The crisis-vs-incident playbook boundary** (Claim 1) — no existing note models the *condition under which the playbook runs out*.
  - **The five-criteria crisis taxonomy** (Claims 2–6) — a named, enumerable recognition checklist absent from all prior notes.
  - **The three-of-five tipping-point rule** (Claim 7) and the "you only need most, not all" qualifier (Claim 8) — a concrete escalation trigger for organizational override.
  - **The "don't-waste-your-time" de-escalation heuristic** (Claim 9) — don't elevate every near-miss to crisis; prepare quietly until 3/5.
  - **Manufactured crises as a trust-burning "dark art"** (Claim 11) — a caution about weaponizing the framework.
  - **The "stack of complexity" migration anti-pattern** (Claim 13) and the **"controller from five iterations ago" perception-breakdown tell** (Claim 12) — concrete organizational-dysfunction artifacts.
  - **Predictable-crisis "rule-suspension tickets"** (Claim 15) — pre-authorizing overrides for known high-visibility windows.

- **Contradicts**: None identified. No claim in this source opposes any existing source note. The one apparent tension — Geisser's change-cycle thesis ("you have to go through these moments periodically for anything substantive to change," Claim 15) vs. `docs-google-sre-prodcast-01-08-incident-management.md` Claim 10 ("do as little incident response as possible… focus on great engineering… avoid burning out your team") and Claim 11 (Treynor "only wants new incidents") — is a **conditioning variable, not a contradiction**: S1E8's prevention thesis operates at the *operational* layer (don't cause repeat outages), while Geisser's "necessary periodic crises" operates at the *organizational-transformation* layer (substantive change requires a suspension of normal behavior). Both can be true; Geisser's "you can't prevent the sky from falling" refers to organizational crises, not operational reliability. The AI-forward "manufactured deadline" tension with Claim 5 (internal deadlines don't count) is likewise resolved as a conditioning variable (Claim 11 describes *forcing* a deadline; Claim 5 describes which deadlines *naturally* qualify). No contradiction issue was filed.

## Guide Impact

- **Chapter 04 (Incident Management / Crisis Response)** — Primary target (per Prospector triage). Add a "crisis vs incident" subsection built on this note: (a) the playbook-boundary definition (Claim 1) — a crisis is an incident with no usable playbook; (b) the five-criteria recognition checklist (Claims 2–6), with the explicit note that internal roadmap deadlines "don't count" as rigid deadlines (Claim 5); (c) the **three-of-five tipping-point rule** (Claim 7) as the concrete escalation trigger for *organizational override* (cross-team authority, rule exceptions, exec air-cover) — the missing escalation layer in Walcer's IMAG note; (d) the "don't-waste-your-time" de-escalation heuristic (Claim 9) to curb premature crisis declaration; (e) the predictable-crisis "rule-suspension ticket" pattern (Claim 15) for known high-visibility windows (major launches, seasonal peaks, regulatory deadlines). This lets Ch04 distinguish a routine AI incident (playbook exists → Walcer's process) from a genuine AI production crisis (novel + no playbook → needs leadership override per 3/5).
- **Chapter 03 (Runbooks and Architecture)** — Use the "stack of complexity" anti-pattern (Claim 13) and the org-perception-breakdown root (Claim 12) to motivate the "earn complexity / avoid glued-on sprawl" principle already in `blog-pagerduty-production-ai-agent-gaps.md` Claim 8 and `blog-pagerduty-sre-agent-architecture.md` Claim 16. A relevant caution against runbook and AI-agent-system sprawl: every half-finished migration layer is future crisis fuel (perception breakdown).
- **Chapter 01 (Incident Response)** — Use the SRE-skill claim (Claim 14: "connect the dots with no information," "expose the full system end-to-end," don't "stay in your lane") to articulate the *human sensemaking* capability that AI incident agents currently lack when the playbook is exhausted (cf. `blog-pagerduty-production-ai-agent-gaps.md` Claim 6 context poisoning). Frames the automation boundary: agents fill the playbook regime; humans own the crisis/sensemaking regime. Also use perception breakdown (Claim 6) as the organizational vocabulary for why shared-correct-context guardrails matter.

## Extraction Notes

- The source is a single public transcript page on sre.google
  (https://sre.google/prodcast/transcripts/sre-prodcast-05-07/). `WebFetch` returned
  no model response for this URL, so it was fetched via `curl -A "Mozilla/5.0"`
  (HTTP 200, 77,546 bytes HTML) and stripped of scripts/styles; the full ~999-line
  HTML / 447-line text was read end-to-end. No sub-pages were followed — the episode
  is self-contained. No part was paywalled.
- The episode is Season 5, Episode 7 ("The One with Carla Geisser and Crisis
  Engineering"), hosted by Steve McGhee and Florian Rathgeber. Guest Carla Geisser
  (ex-Google SRE 2004–2015, storage systems; founder of Layer Aleph, a
  "crisis engineering" firm). The framework is Layer Aleph's own taxonomy, which
  Geisser says was "back computed" from real engagements (healthcare.gov launch
  failure; federal/state government systems).
- `confidence_overall` is **emerging**, not settled, deliberately: unlike the
  sibling S1E8 (Walcer describes Google's *actual, established* incident-management
  process she owns) and S3E6 (guests describe *established* IR tooling practice),
  this episode presents a **single practitioner's proprietary conceptual model** she
  invented ("we made up this term"). The individual *definitions* (the five criteria,
  the three-of-five rule) are stated crisply and are rated `settled` per-claim as
  definitions, but the framework as a whole lacks external validation, empirical
  backing, or industry-standard status — hence `emerging` overall. The
  org-change-cyclicity (Claim 15) and manufactured-crisis (Claim 11) claims are
  `emerging` even by the source's own telling (practitioner generalizations).
- `date_published` is estimated at **2026**, matching the sibling Season-5 notes
  (`docs-google-sre-prodcast-05-01-hippo-observability.md`, `-05-04-del-cid-ai-sre.md`,
  `-05-08-damion-yates-ai-systems.md`), all of which record Season 5 as airing in
  2026. The transcript page itself carries no structured publication date; only the
  series-index date (2022-03-31) and footer year links appear in the HTML.
- `source_type` is `docs` (official Google SRE published transcript), matching the
  sibling S5 prodcast notes and the Prospector's "docs" triage. The filename keeps
  the `docs-google-sre-prodcast-` prefix used for all Google SRE Prodcast notes.
- The source has **zero AI/LLM content** (consistent with the Prospector's second
  triage: "no AI/LLM-specific angle, no code, config, metrics, or failure data").
  All AI/LLM connections in Cross-References and Guide Impact are the Miner's
  analytical synthesis, clearly marked as such, not claims from the source.
- Quotes were copied character-for-character from the extracted transcript text
  (verified against the saved HTML via targeted grep for each key fragment, e.g.,
  "three of those five criteria," "don't count," "controller from five iterations
  ago," "hodgepodge of stuff that's glued onto the side"). Multi-fragment
  attributions are joined with "— and —"; each fragment is a contiguous passage
  from the source. Small bracketed/ellipsis omissions within a fragment are
  contiguous-context trims, not splices of non-adjacent sentences.
- No contradiction surfaces against existing notes; the operational-vs-organizational
  tension with S1E8 Claim 10/11 is a conditioning variable (different layer of
  analysis), not opposition. No contradiction issue was filed.
