---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-02-08/
source_type: docs
title: "Life of an SRE: Life Beyond Google (SRE Prodcast S2E08)"
author: "Google SRE Prodcast — hosts MP English & Steve McGhee; panelists Cody Smith (Camus Energy), Carla Geisser (Layer Aleph), Laura Nolan (Stanza)"
date_published: 2022 (estimated; SRE Prodcast Season 2, Episode 8 — transcript page has no structured per-episode publish date; Season 2 aired 2022)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#58"
---

# Life of an SRE: Life Beyond Google (SRE Prodcast S2E08)

> Three former Google SREs ("Xooglers") argue which SRE concepts transfer
> outside Google versus which don't, why "SRE in a box" can't work, and what
> anti-patterns kill SRE teams in smaller orgs — practitioner oral history that
> extends the corpus's SRE-philosophy material with non-Google-scale accounts
> and a direct critique of the "start with SLOs" SRE narrative.

## Source Context

- **Type**: docs (official Google SRE Prodcast transcript — Season 2, Episode 8,
  "Life Beyond Google," the Season 2 finale)
- **Author credibility**: High. Panelists are three former Google SREs with
  4–14 year tenures across Search, large-scale storage, ads/pipelines/databases
  (Mesa, Photon), and the network edge — now CTO/founders or engineers at
  small companies and SRE consultancies (Camus Energy, Layer Aleph, Stanza).
  Host Steve McGhee is a Google reliability advocate; MP English is a Google SRE
  host. This is primary-source practitioner testimony, not analyst reporting.
- **Scope**: SRE practice *transfer* — what survives leaving Google-scale
  infrastructure, the "scale shock" of smaller orgs, tooling/control-surface
  differences (Kubernetes), operational differences (replication, on-call,
  incident response), SRE team-design anti-patterns (checkbox SRE, embedded-SRE,
  sprinkled SREs), and the conditions under which "SRE" emerges at all.
- **Does NOT cover**: Any AI/LLM operations content (pre-dates the AI pivot the
  corpus tracks in Seasons 4–6). No code/config/dashboards. It is career/culture
  oral history, not a technical how-to.

## Extracted Claims

### Claim 1: The transferable part of SRE is the *concepts*; only the "proper nouns" (tool names) change when you leave Google
- **Evidence**: Carla Geisser's framing, echoed by Laura Nolan and Cody Smith. A load balancer, rate limiter, and storage system exist everywhere; their names and implementations differ, but "the reasons those things exist and the reasons they fail will continue to be basically the same." Theoretical/design knowledge (how to design for scale, troubleshooting, analysis) transfers; tooling familiarity is the learning curve.
- **Confidence**: emerging
- **Quote**: "The way I saw this framed by a friend recently was that the proper nouns are different when you leave Google, but the concepts are all the same. So there will be a thing that looks like a load balancer. There will be a thing that does rate limiting. There will be storage systems. They'll all have different names, depending on what cloud provider you're using or what internal systems have been built bespoke inside of that organization. But the reasons those things exist and the reasons they fail will continue to be basically the same."
- **Our assessment**: Plausible and well-corroborated by the rest of the corpus's SRE-philosophy material (e.g., the Treynor interview's definition of SRE as "software engineering applied to operations" — a concept, not a tool). Treat as a durable framing, not a rigorous claim.

### Claim 2: "Scale shock" — non-Google orgs operate at dozens-to-low-hundreds of services, not thousands, which changes the economics of change (white-glove fixes beat tooling)
- **Evidence**: Carla Geisser's healthcare.gov war-room anecdote (a "big" system was ~500 computers — "nothing" by Google standards); Laura Nolan at Slack finding that onboarding most services onto new infra is more economic to do by hand ("white glove them all") than to build tooling, because you deal with "dozens or low hundreds rather than thousands of different services."
- **Confidence**: emerging
- **Quote**: "If you're changing something at the infrastructure level, or you're bringing in a new thing and you want to onboard most of the existing services onto it, you can kind of actually just go and white glove them all, as opposed to having to go and run around and try and get teams to do this for you or build tooling. It actually becomes more economic to just go and make the changes yourself, because you're dealing with dozens or low hundreds rather than thousands of different services."
- **Our assessment**: A real and useful conditioning variable for the guide — the tooling-vs-manual-tradeoff the AI-ops chapters assume (build automation) is itself scale-dependent. Smaller orgs may be better served by manual reliability work first.

### Claim 3: Replication norms differ sharply — at Google you'd "never fathom a service with no replication"; a startup can run a single replica per deployment
- **Evidence**: Cody Smith (Camus Energy): "you never would have even fathomed having a service that had no replication, even within a cluster. Whereas now, we have deployments of our product for customers with, every single deployment has the same number of replicas of our front end, which is one."
- **Confidence**: emerging
- **Quote**: "you never would have even fathomed having a service that had no replication, even within a cluster. Whereas now, we have deployments of our product for customers with, every single deployment has the same number of replicas of our front end, which is one. We've never needed more than one. It's never come up."
- **Our assessment**: Anecdotal but illustrative of how reliability *engineering* (not just tooling) is scaled to the actual risk profile. Useful counterweight to the assumption that HA/replication patterns are universal.

### Claim 4: A uniform control surface (Kubernetes) is what finally enables portable, organization-transferable tooling — heterogeneity ("Thrift and MessagePack and God knows what") made tooling hard at Google-scale-adjacent orgs
- **Evidence**: Laura Nolan argues the loss of Google's guaranteed lower-stack uniformity ("you don't have that sort of guaranteed control surface to latch onto") is what made writing tooling harder outside Google, and that Kubernetes "does give you a relatively uniform kind of control surface that you can build software according to and have it be relatively transferable organization to organization."
- **Confidence**: emerging
- **Quote**: "I think that's why we're seeing such a big explosion of tooling around Kubernetes, because Kubernetes does give you a relatively uniform kind of control surface that you can build software according to and have it be relatively transferable organization to organization."
- **Our assessment**: Reasonable and consistent with the broader industry shift the corpus observes (Kubernetes as the de-facto control plane). Relevant to the guide's automation/release material as a precondition for reusable tooling.

### Claim 5: Don't start a reliability program with SLOs — start with basics (what is the system doing? what's critical? what's the business function?) — or teams "get mad about not knowing how their systems are performing"
- **Evidence**: Carla Geisser: many orgs "have read the Google SRE book, and they know the words SLO and SLA, and they're very excited to start implementing those. But that isn't necessarily the place for them to start." Laura Nolan strongly agrees ("if you asked 100 people, probably 90 of them would say" SLOs-first, but "not every organization actually understands what is critical about their product" nor "has the right monitoring to have the right SLIs").
- **Confidence**: emerging
- **Quote**: "A lot of people at this point have read the Google SRE book, and they know the words SLO and SLA, and they're very excited to start implementing those. But that isn't necessarily the place for them to start. In a lot of cases, they might have not quite enough production hygiene. They might not even know, really, anything about how their systems are behaving. And so to start immediately with, oh, we need SLAs and SLOs for this product, doesn't help them. They just get mad about not knowing how their systems are performing."
- **Our assessment**: Strong, specific, and high-value. This is the episode's headline claim and it directly challenges the simplified "SRE = SLOs-first" narrative. It is corroborated by the corpus's SLO-skeptic material (S1E4 Rethinking SLOs) and conditioned — not contradicted — by S5E2 (SLOs as shared vernacular), which applies to orgs that already have monitoring/ownership. See Cross-References → Contradicts/conditioning.

### Claim 6: "SRE in a box" is infeasible — you cannot package a product that understands a given org's systems and gives context-aware reliability guidance
- **Evidence**: Laura Nolan: the consultancy work Carla describes "is not something that you can standardize in the same way. You can't build a product that's SRE in a box that will come and actually understand your systems and give you that context aware take." The episode's own summary question is literally "why can't you build 'SRE in a box' that jump-starts pretty much any organization?"
- **Confidence**: emerging
- **Quote**: "You can't build a product that's SRE in a box that will come and actually understand your systems and give you that context aware take on the— I think there's something quite wrong about that. Always do the SLOs first [INAUDIBLE]."
- **Our assessment**: Consistent with Claim 5 and with the corpus's repeated warnings that SLOs/automation imposed without ownership degrade into check-box exercise (see S5E2 Claim 3). Good guardrail for any guide section tempted to present a one-size-fits-all SRE onboarding recipe.

### Claim 7: What Google publishes is NOT uniformly adopted inside Google — adoption is "lumpy," and even Google teams run "Potemkin village SLOs" (a random metric + a number that's been passing)
- **Evidence**: Carla Geisser: "whenever Google puts out a paper or a piece of documentation, people assume that it has been uniformly adopted inside of Google. And we all know from our own experience that that's not true." Laura Nolan: teams "might have Potemkin village SLOs, where they have a thing that looks like SLOs, but it's not really that meaningful. They picked a random metric, and they picked a number that would be passing for most of the past quarter, and that's their SLO now, because somebody said that they had to have SLOs."
- **Confidence**: emerging
- **Quote**: "whenever Google puts out a paper or a piece of documentation, people assume that it has been uniformly adopted inside of Google. And we all know from our own experience that that's not true. Even adoption of something like SLOs is very lumpy inside of Google."
- **Our assessment**: Important epistemological caveat for the entire corpus — external readers over-index on published Google practice as if it were uniform. This is a meta-point the guide should carry when citing Google SRE sources.

### Claim 8: SRE's "grand unifying theory" is that it is a production-system-specific manifestation of *systems thinking* (cascading-failure / metastable-state insight is the core SRE intuition)
- **Evidence**: Laura Nolan's keynote-derived framing: "SRE is just a production system specific manifestation of system thinking." She cites the cascading-failure loop ("that kind of vicious cycle of load that causes retries that causes more load") as the canonical systems insight, and names methods like "East-BL" (examining control structures: what happens if a link breaks / traffic doubles / is wrong) for finding system vulnerabilities.
- **Confidence**: emerging
- **Quote**: "My grand unifying theory of SRE is that actually, SRE is just a production system specific manifestation of system thinking. And we do it in an informal way."
- **Our assessment**: A coherent, defensible framing (and Cody Smith adds "there are relatively few systems thinkers in the world. SRE has a staggering fraction of them," recommending Donella Meadows' *Thinking in Systems*). Useful as a conceptual anchor for Ch02; speculative as a "theory" but matches the systems-view thread elsewhere in the corpus (e.g., STPA, crisis-engineering notes).

### Claim 9: SRE emerges when you give a *small, motivated, empowered* team responsibility for a *critical, end-to-end* system — the three conditions are small + empowered + full-stack scope
- **Evidence**: Carla Geisser: "whatever happens when you take a small number of motivated and empowered operators and give them responsibility for something that is critical to the business, and it has to be responsibility for the entire chain of stuff." End-to-end scope means "there can never be another team who you can obviously point at and say, OK, cool. My responsibility ends here. It's definitely their fault. You have to feel a responsibility for the end-to-end system." Empowerment is required so they "have the ability to actually change the thing that is in their way."
- **Confidence**: emerging
- **Quote**: "there can never be another team who you can obviously point at and say, OK, cool. My responsibility ends here. It's definitely their fault. You have to feel a responsibility for the end-to-end system."
- **Our assessment**: A clean, testable org-design claim. Directly relevant to Ch04 (organizational patterns). The *empowerment* limb is corroborated by the corpus's "empowerment gap" theme (S3E1 Claim 7).

### Claim 10: Anti-pattern — "checkbox SRE": SREs acting as permanent consultant teams without service ownership produce shallow, tick-box PoR processes instead of deep context-aware engagement
- **Evidence**: Laura Nolan: an anti-pattern she's "seen in a few places is SREs who try to act like permanent consultant teams, but without any actual ownership over any services." At Google, a production-readiness review (PoR) is "three to six months doing deep work, understanding that service, understanding its architecture"; the tick-box version is "yep, yep, yep, yep, yep. And there's little room for thought or deep engagement." Carla adds it's "particularly common in industries or organizations that already have a lot of compliance folks" (government, finance, health care).
- **Confidence**: emerging
- **Quote**: "the anti-pattern that I've seen is end up with a lot of very shallow checkbox processes that the centralized SRE team asks other teams to do. So you'll end up with a PoR form and instead of doing— at Google, if you were PoR-ing a new service, that's a production readiness review, you might expect to spend three to six months doing deep work, understanding that service, understanding its architecture and how it behaves and ways it might be improved, and instrumenting it and all of that good stuff."
- **Our assessment**: High-value anti-pattern, and it *exactly matches* S5E2's warning that SLOs "imposed or created by others degrade into a compliance / check-the-box exercise" (S5E2 Claim 3). Strong internal corroboration across the corpus.

### Claim 11: The weekly production meeting is a portable, high-value SRE practice — a standing forum for "what happened in production, what are on-calls struggling with, what's risky, what's going well"
- **Evidence**: Laura Nolan's first fix at a post-Google job: "my team didn't have a weekly production meeting. And this is a thing that I think is a really valuable piece of culture and process." (Cross-echoes S5E2 Claim 11 — SLOs most useful as a historical review in a weekly sync.)
- **Confidence**: emerging
- **Quote**: "my team didn't have a weekly production meeting. And this is a thing that I think is a really valuable piece of culture and process. So just the idea of getting together once a week and having a meeting that is solely focused on what has happened in production, what are on-calls struggling with, what are we planning on doing in the next few days, what's risky, what's going well?"
- **Our assessment**: A concrete, adoptable practice with low maturity prerequisites — good candidate for a "start here" recommendation in Ch04.

### Claim 12: Anti-pattern — the single embedded SRE becomes the "ops person" doing all the toil (rollouts, config, Terraform, PromQL), gaining no traction and stalling career growth
- **Evidence**: Laura Nolan: "the worst passion is the single-embedded SRE that turns into the ops person and ends up being the person who's always called upon to do anything that's sort of production-oriented." Result: "you just end up doing all of the toil, all of the grunt work," with no peer SREs to develop alongside, hurting both impact and career ladder.
- **Confidence**: emerging
- **Quote**: "the single-embedded SRE that turns into the ops person and ends up being the person who's always called upon to do anything that's sort of production-oriented, like doing rollouts or doing config changes or managing Terraform and PromQL."
- **Our assessment**: Complements Claim 13 (don't sprinkle SREs) and the corpus's toil-reduction theme. Specific and actionable for Ch04 org design.

### Claim 13: Don't haphazardly sprinkle a handful of SREs across an org — a real SRE team must be *dense* with the right mindset and authority; separately, embed reliability-thinkers in dev
- **Evidence**: Carla Geisser: "Even a handful of very competent SREs, and then sprinkle them throughout your organization sort of haphazardly... it just doesn't work, because none of them can get traction." Cody Smith's preferred model: in a mature org, "a few people sort of sprinkled in dev that think about reliability" plus "a separate SRE team that really focuses on being able to meet the SLO as their primary objective."
- **Confidence**: emerging
- **Quote**: "Even a handful of very competent SREs, and then sprinkle them throughout your organization sort of haphazardly. A lot of places that I've consulted with try this... And it just doesn't work, because none of them can get traction and none of them can make any progress."
- **Our assessment**: A balanced, two-track org model (embedded reliability thinkers + a dense central SRE team). Aligns with the empowerment/ownership theme of Claims 9 and 12.

### Claim 14: The first *technical* reliability interventions after Google were circuit-breaking and throttling at strategic points — cheap, high-leverage stability fixes
- **Evidence**: Laura Nolan: after adding the weekly meeting, "the first thing was putting in circuit-breaking and throttling in a few strategic places that really needed it," explaining circuit-breaking as backing off when a dependency is "consistently returning bad results or is consistently slow" (especially effective against retry storms), and throttling as "a hard limit over time about how many requests can go from here to there."
- **Confidence**: emerging
- **Quote**: "Circuit breaking is basically when service A is talking to service B. And service A notices that service B is— or perhaps a particular instance of service B is implementation dependent, is consistently returning bad results or is consistently slow. What you can do there is you can basically back off for a little while. The idea here is that if you have a time-limited overload, you can stop making it worse by sending more results."
- **Our assessment**: Concrete, transferable technique with low maturity prerequisites — useful in the guide's resilience/incident-prevention material. Note these are defensive patterns that apply unchanged to AI/LLM serving stacks.

### Claim 15: Parting advice on reliability challenges — start smaller than you think (one user interaction / one flow), start with *culture* (personal attachment to reliability goals), and don't do the first knee-jerk fix
- **Evidence**: Carla Geisser: "start extremely small, smaller than you even think makes sense, with one user interaction or one piece of your system's flow" (e.g., "make the home page load in under 500 milliseconds 99% of the time"). Cody Smith: "start with culture... If problems are emerging steadily, it's because some number of the people around are not upholding reliability as a priority." Laura Nolan: "don't just do the first thing that pops into your head to fix the problem" — analyze the system; she gives a concrete war story (aligned two unsynced rate limits) as the better fix.
- **Confidence**: emerging
- **Quote**: "start extremely small, smaller than you even think makes sense, with one user interaction or one piece of your system's flow. And work your way outward from there, because the thing I've seen most often in organizations is everyone is running around saying, oh, no. Things are unreliable. But there's too many things."
- **Our assessment**: Consistent practitioner wisdom ("start small," "fix root cause not symptom") that dovetails with the corpus's incident/crisis material. The rate-limiter war story (Concrete Artifacts) is the illustrative artifact.

## Concrete Artifacts

### Artifact A — The "aligned rate limits" war story (Laura Nolan, S2E8)
A concrete example of Claim 15 (don't do the knee-jerk fix; analyze the system):

> One time, I worked with a company that would occasionally do a thing where it would
> require all of the end users to update their client. And sometimes, that caused
> problems. And the reason it caused problems was when a client would restart, it had
> to do a pretty expensive call back to base to get a bunch of data. And that call was
> rate limited. And so sometimes, we'd tell all the clients to update. But then we'd
> rate limit them when they tried to restart. Now, it turns out that there was a rate
> limiter on the mechanism that required clients to update as well. But it wasn't
> synced up with the other rate limit. So very simple systemic change was to align
> those two rate limits, and don't ever ask clients to update if they wouldn't get the
> permission to do the reboot [INAUDIBLE] call. And that was a pretty quick couple of
> lines change that made that operation safe.

### Artifact B — Circuit-breaking / throttling definitions (Laura Nolan, S2E8)
Definitions given when a host asked her to define the terms for listeners:

> Circuit breaking is basically when service A is talking to service B. And service A
> notices that service B ... is consistently returning bad results or is consistently
> slow. What you can do there is you can basically back off for a little while. The
> idea here is that if you have a time-limited overload, you can stop making it worse by
> sending more results. And it's particularly effective if you have that phenomenon
> where clients start hammering services with retries once things get a bit slow or a
> bit flaky. And I guess throttling is a similar idea, where you put in a hard limit
> over time about how many requests can go from here to there, or a delay in between
> repeated requests.

### Artifact C — Recommended primary source (systems thinking)
Cody Smith's book recommendation supporting Claim 8: Donella Meadows, *Thinking in
Systems* — "a really good primer on this topic." Laura Nolan also references her SRE
keynote on systems thinking delivered "just last month" relative to the recording.

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast.md` — Claim 6 ("The Prodcast's editorial intent was to challenge, not merely recap, the SRE Book orthodoxy — explicitly reframing topics such as SLOs"). S2E8's "don't start with SLOs" (Claim 5) is a concrete instance of that editorial challenge. Also Claim 2 (Season 2 = "Life of an SRE") situates this episode.
  - `docs-google-sre-prodcast-01-04-rethinking-slos.md` — the SLO-skeptic counterweight. Its Claim 5 ("Be skeptical of claims that SLOs solve everything") and Claim 1/8 (SLOs designed for aggregate B2C, go stale) are the same skeptical orbit as S2E8 Claim 5/6. No conflict; same direction.
  - `discussion-google-sre-ben-treynor-interview.md` — Claim 5 (PRRs examine a system before SRE takes responsibility) is the *deep* version of what S2E8 Claim 10 calls the shallow "tick-box PoR." Claim 10 (SRE's moral authority from an agreed SLO) is the mature-org counterpart to S2E8's warning that SLOs imposed without understanding become Potemkin (Claim 7).
  - `docs-google-sre-prodcast-03-01.md` — Claim 7 ("a skill gap AND an empowerment gap ... livelock") corroborates S2E8 Claim 9's *empowerment* condition for SRE to emerge.

- **Contradicts**:
  - (None — hard contradiction filed.) The one apparent conflict — S2E8 "don't start with SLOs" vs `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` (which promotes SLOs as "the cross-vertical common language" / "the shared vernacular") — is a **conditioning variable, not a contradiction**: S5E2 addresses *mature* orgs adopting SLOs as communication, while S2E8 addresses *immature* orgs lacking production hygiene/monitoring. Notably S5E2 Claim 3 ("SLOs imposed or created by others degrade into a compliance / check-the-box exercise") *agrees with* S2E8 Claim 10's checkbox-SRE anti-pattern, and S5E2 Claim 11 (SLOs useful as a weekly-sync historical review) *agrees with* S2E8 Claim 11's weekly production meeting. Per MINER §4a ("claims differ only in context ... that's a conditioning variable"), no contradiction issue is filed. If the guide's SLO material ever prescribes "SLOs-first for every org regardless of maturity," that would be the place the conditioning variable bites — worth a Smith note, not a contradiction filing.

- **Extends**:
  - `docs-google-sre-prodcast.md` — moves the index note's Season-2 "Life of an SRE" theme from a one-line description to extracted, cited claims (first Season-2 individual note in the corpus).
  - The corpus's AI-ops focus is *not* extended (no AI content here); this note adds the non-AI SRE-philosophy/organizational substrate the AI chapters sit on.

- **Novel**:
  - First source note to extract the **"SRE in a box" infeasibility** argument (Claim 6) and the **three-conditions-for-SRE** framework — small + empowered + end-to-end (Claim 9) — as named patterns.
  - First to capture the **"proper nouns change, concepts stay the same"** transfer framing (Claim 1) and the **"scale shock" / white-glove-vs-tooling economics** claim (Claim 2) from a primary Xoogler source.
  - First to record the **checkbox-SRE / shallow-PoR anti-pattern** (Claim 10) and the **single-embedded-SRE anti-pattern** (Claim 12) with verbatim panelist wording.

## Guide Impact

- **Chapter 02 (SRE Fundamentals / Philosophy)**: Add a "what transfers vs what doesn't" subsection built on Claim 1 (concepts transfer, tooling doesn't) and Claim 8 (systems thinking as the unifying theory). This grounds the chapter's philosophy in practitioner testimony rather than only the SRE Book.
- **Chapter 02 / SLO material**: Add an explicit *maturity precondition* to any "adopt SLOs" guidance, citing Claim 5 ("don't start with SLOs") + Claim 7 (Potemkin SLOs) + the conditioning variable vs S5E2. Recommendation: for orgs without production hygiene/monitoring, start with Claim 11 (weekly production meeting) and Claim 15 (start small, one flow) before SLOs.
- **Chapter 04 (Incident Management / On-call / Org Patterns)**: Add the three SRE-emergence conditions (Claim 9) and the two anti-patterns — checkbox/consultant SRE without ownership (Claim 10) and single-embedded-SRE-becomes-ops (Claim 12) — plus the "don't haphazardly sprinkle SREs; keep the team dense + embed reliability thinkers in dev" model (Claim 13). Add the weekly production meeting (Claim 11) and circuit-breaking/throttling as first technical interventions (Claim 14) to the portable-practices list.
- **Chapter 05 (Automation & Toil)**: Claim 2's scale-dependent tooling-vs-manual economics and Claim 12's toil-on-the-embedded-SRE are directly relevant to the toil-reduction discussion; resist presenting build-tooling as universally correct.

## Extraction Notes

- Source is a single self-contained transcript page; no linked sub-pages were followed (the page is a standalone episode transcript). The HTML returned HTTP 200 (94 KB); WebFetch was unavailable, so text was extracted locally via `html.parser` and read in full (157 lines of dialogue).
- `date_published` is estimated to 2022 (Season 2 aired 2022; the page exposes no structured per-episode date — consistent with sibling notes S1E8 and S3E1, which flag the same omission). This does not affect any claim.
- Transcripts contain `[INAUDIBLE]` / `[LAUGHS]` markers where audio was unclear; quoted passages preserve the speaker's words and omit those markers except where noted. One quote (Claim 6) ends mid-sentence at an `[INAUDIBLE]` boundary — preserved as-is.
- No AI/LLM content present; relevant to the guide only as SRE-philosophy/organizational substrate. Priority per triage: low.
- Verified cross-references against the actual cited notes (claims re-read, not inferred): `docs-google-sre-prodcast.md` Claims 2 & 6; `docs-google-sre-prodcast-01-04-rethinking-slos.md` Claims 1, 5, 8; `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claims 3, 11; `discussion-google-sre-ben-treynor-interview.md` Claims 5, 10; `docs-google-sre-prodcast-03-01.md` Claim 7.
