---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-01-07/
source_type: docs
title: "SRE Prodcast Episode 7 — On-Call Rotations with Andrew Widdowson (APW)"
author: "Andrew Widdowson (APW), SRE at Google (~15 years); interviewed by MP and Viv (Google SRE Prodcast hosts)"
date_published: unknown
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: settled
issue: "#40"
---

# SRE Prodcast Episode 7 — On-Call Rotations with Andrew Widdowson (APW)

> A primary-source podcast transcript in which Andrew Widdowson (a ~15-year
> Google SRE) lays out Google's concrete on-call rotation patterns: the
> leverage/scarcity/selectivity rationale for which services get SRE on-call,
> the Treynor/Sloss fatigue limit, the on-call vs on-duty split, the
> primary/secondary (not two-co-primary) model, team-sizing minimums,
> dual-homed 12/12 shift designs, mercy substitution for multi-night pages,
> barn-raising new rotations with cross-domain senior SREs, and Wheel of
> Misfortune tabletop exercises for on-call readiness. Foundational SRE
> practice from the authoritative source family, with no AI/LLM-specific angle.

## Source Context

- **Type**: docs (official Google SRE Prodcast transcript published on
  sre.google). The Prodcast is Google SRE's official podcast; this is Episode 7,
  "On-Call Rotations with Andrew Widdowson."
- **Author credibility**: Andrew Widdowson ("APW") — a Google SRE of ~15 years
  at time of recording, formerly on Google Search front-end/back-end
  infrastructure for over a decade, then ~4–5 years on SRE education via the SRE
  EDU program, which he states he co-founded (line 198: "I co-founded that
  group"). He is described by the hosts as "a really well-known name around SRE
  at Google" who has taught the majority of Google SREs. This is the highest
  credibility tier for on-call *practice*: an experienced practitioner
  describing how Google actually runs rotations, not a vendor or an outsider.
  The interviewer framing ("the vast majority of SREs at Google have had the
  opportunity to either hear speak or have received teaching from him") supports
  treating his description as representative of Google norms rather than a lone
  opinion — though he repeatedly flags that his recommendations are an overview
  of "ways that Google has chosen to solve things" and that teams should adapt.
- **Scope**: Exclusively on-call rotation *design and culture* — who is on-call,
  how rotations are staffed and scheduled, shift models, fatigue limits, the
  on-call/on-duty distinction, new-rotation bootstrapping (barn-raising), and
  training (Wheel of Misfortune / SRE EDU). Does NOT cover: AI/LLM operations,
  agent architectures, monitoring taxonomy (covered in other Prodcast episodes
  in this corpus), SLO theory, or any post-2022 LLM-era topic. The source
  predates the LLM era and contains zero AI/LLM content. Its value to the guide
  is as the canonical operational reference for Ch04 (On-call and Toil), which
  the triage notes is currently a stub with no sourced claims.

## Extracted Claims

### Claim 1: SRE on-call is selective by design — Google staffs SRE on-call only for a minority of services, driven by leverage, scarcity, and selectivity, and is usually co-on-call with developers
- **Evidence**: APW's framing of why SRE is "naturally scarce" relative to SWEs
  and why the overwhelming majority of Google microservices have *no* SRE
  on-call. He states SRE picks "our responsibilities" and that an SRE on-call
  signals "a certain extra standard of reliability" while SREs "try not to hoard
  that for ourselves" by staying co-on-call with developers.
- **Confidence**: settled
- **Quote**: "The other part that I just want to mention that's a part of our
  leverage, a part of our scarcity, and a part of our selectivity, is that the
  overwhelming majority of, let's call them microservices at Google, do not have
  SRE on-call for them. So we pick and choose not our battles, but our
  responsibilities."
- **Our assessment**: This is the demand-side complement to the supply-side
  scarcity principle in the Treynor interview note (Claim 7: SREs "assigned
  where they're going to do the most good"). APW gives the operational concrete:
  SRE on-call is a scarce, deliberately allocated resource, not a universal
  entitlement. Directly relevant to Ch04 — and a useful baseline if the guide
  ever argues for where to deploy AI on-call augmentation (scarce, high-leverage
  services first).

### Claim 2: Developers should be co-on-call so they "feel the pain of the service" and are motivated to fix operational problems, rather than SRE being a wall to throw work over
- **Evidence**: APW's argument that developer-first colleagues must experience
  the operational burden to be motivated, and that SRE's role is to operate
  *together* with developers ("the cavalry is here"), not to be a dumping ground.
- **Confidence**: settled
- **Quote**: "our developer first counterparts need to be able to, quote, 'feel
  the pain of the service'— the operational aspects of it— in order to be
  motivated to make it better, because otherwise, it's just throwing stuff over a
  wall."
- **Our assessment**: APW independently corroborates the "throw it over the wall"
  anti-pattern already documented in the Treynor interview note (Claim 6). Where
  Treynor frames it as a structural SWE/ops chasm, APW frames the remedy at the
  rotation level: keep developers in the rotation. The two claims reinforce each
  other. Note the AI/LLM analog the guide could draw: if an AI agent absorbs the
  operational pain, the developer "feels" less of it — a risk that the agent
  becomes the new wall unless developers remain accountable.

### Claim 3: Google names a fatigue limit after Ben Treynor Sloss (the "Treynor limit," more correctly the "Sloss limit") — if incident volume per shift exceeds a threshold, the SLA/rotation sizing needs adjustment, not heroic effort
- **Evidence**: APW describes an internally named fatigue limit honoring a
  founding SRE-org member. The threshold philosophy: sustained follow-through
  load (postmortems, fixes) above a smooth-window threshold produces "cumulative
  failure" (a domino effect where you can't write the postmortem because you're
  being paged again). The goal is that on-callers end shifts "intrigued or
  refreshed— best case— or nothing happened; I was bored."
- **Confidence**: settled
- **Quote**: "we have, as an homage or an honor to one of our almost founding
  members of the SRE org, Ben Treynor Sloss, Ben Sloss, we've named like a
  fatigue limit, which we've incorrectly called the Treynor limit— his last name
  is Sloss, we should call it the Sloss limit, whatever."
- **Our assessment**: This is the canonical fatigue-limit concept in the Google
  SRE on-call canon, and it is explicitly named after the same authority as the
  Treynor interview note (Ben Treynor Sloss). It is a concrete, measurable
  guardrail for rotation sizing — directly usable in Ch04 as a "size the
  rotation to defend a fatigue limit" recommendation. The exact numeric
  threshold is deliberately left team-specific ("the measuring and the math that
  we particularly use is less interesting than the philosophy behind it").

### Claim 4: On-call (responsibility for service vitality during a shift) and on-duty (repetitive ticket/support "crank turning") are different cognitive modes and should, where possible, be kept separate so on-duty work does not drain the on-caller
- **Evidence**: APW defines the two terms and warns that overloading on-duty onto
  the on-caller ("I just did a bajillion thousand tickets and now I'm getting
  paged. Oh, my head hurts") sets the team up for failure. He personally prefers
  coding while on-call. Jen Petoff (lead of SRE Education) is quoted: on-call is
  "stewards of the scientific method in a pressure cooker."
- **Confidence**: settled
- **Quote**: "I think on-call is: you are responsible for the vitality of the
  uptime, the responsiveness of the service during your shift. And on-duty means
  some sort of probably small quanta, but maybe high quantity of work that needs
  to be done: crank turning, answering tickets, answering support, whatever type
  of stuff."
- **Our assessment**: The on-call/on-duty split is a concrete design lever for
  protecting on-caller freshness (which APW calls "our most precious resource").
  For the guide, this maps onto a clear AI/LLM augmentation point: AI agents are
  well-suited to absorb *on-duty* ticket/support work (repetitive, low-judgment)
  precisely so the human on-caller's cognitive capacity is reserved for
  *on-call* incidents. This is the "AI does the toil, human keeps the agency"
  pattern.

### Claim 5: Prefer a single primary on-caller plus a secondary (for breaks/relief) over two co-primaries with no secondary — co-primaries dilute agency, visibility, and accountability
- **Evidence**: APW's reasoning: with two co-primaries, "Who is the on-caller? I
  need to talk to the on-caller" loses visibility; he cites "Too many cooks in
  the kitchen" and "If a problem is everyone's problem, then it is no one's
  problem." A secondary who stays mentally fresh can take an orthogonal second
  incident, reducing cognitive burden on the primary. He states this is "my
  personal preference."
- **Confidence**: emerging
  (APW presents it as a strong, well-reasoned recommendation but explicitly
  frames it as his "personal preference" rather than a universal Google mandate;
  the underlying agency/visibility argument is sound and generalizable)
- **Quote**: "I am, for the most part, in favor of [a] single person being the
  primary on-caller. And if you have a second person for extra support— for
  relieving for breaks, for 'you need to go to the grocery store'— I also
  recommend a secondary, but exactly that: a primary and a secondary rather than
  two co-primaries and no secondary. That's my personal preference. I think it
  solves for efficacy of communication and it also solves for agency of the
  on-caller."
- **Our assessment**: The agency/visibility argument is the durable insight: a
  single accountable decider beats diffused ownership during an incident. This is
  directly relevant to AI/LLM on-call augmentation — an AI "secondary" that
  handles an orthogonal incident while keeping the human primary as the single
  decider preserves the agency APW argues for, whereas a "co-primary AI" that
  shares the decision blurs accountability. This supports the "AI-assisted, not
  AI-native" framing seen in the PagerDuty architecture note.

### Claim 6: The on-caller holds temporary equivalent authority to a VP and is the single decider for reliability during their shift — agency is the point of the role
- **Evidence**: APW: when on-call for a Google product you have "temporary
  equivalent authority to a vice president." The pager is "a token that says you
  are the decider for the reliability of this product." You may not be the most
  knowledgeable person but you are "the most present and most stateful decider."
- **Confidence**: settled
- **Quote**: "when you're on-call for a Google product, you have temporary
  equivalent authority to a vice president."
- **Our assessment**: The single-decider/agency principle is the through-line of
  APW's rotation philosophy (see Claim 5). For Ch01 (Incident Response) and Ch04,
  this is a strong argument that any AI augmentation must preserve a identifiable
  human decider rather than diffuse authority.

### Claim 7: For single-site teams that cannot run dual-homed rotations, a "mercy substitution" policy lets a colleague take over the rest of a shift after multiple consecutive middle-of-the-night pages
- **Evidence**: APW explicitly frames this as speculation for teams *without*
  Google's dual-site model: "given that that is not how things work at Google,
  I'm merely speculating." The recommendation: a policy allowing the paged
  engineer to "tap the hours" to a colleague after repeated night pages, on the
  assumption correct sizing makes it rare.
- **Confidence**: emerging
  (explicitly speculative — APW says "I'm merely speculating" and "I wish
  everyone the best of luck"; the underlying human-freshness principle is sound,
  but the specific policy is not a Google practice he is reporting)
- **Quote**: "I would maybe suggest that maybe there's a policy— like if you get
  paged in the middle of the night on multiple consecutive nights, that there's a
  mercy substitution, like you can avail of your colleagues to see if someone
  will take over the rest of your shift, knowing full well that most of the time,
  if things are sized right, crossing your fingers, this won't happen."
- **Our assessment**: This is the only claim APW flags as his own speculation
  rather than Google practice, so it carries lower authority than the others.
  The principle — protect human freshness after repeated night pages — is sound
  and is the operational expression of the fatigue limit (Claim 3). Worth
  capturing as a concrete, named policy pattern for Ch04 even with the reduced
  confidence.

### Claim 8: Google's internal minimum for an officially SRE-funded on-call rotation is two geographically distinct sites, each with at least six or seven people — ~12–14 people total
- **Evidence**: APW states the "internal minimum standard" directly and notes it
  drives "all of the rest of the math" for shift coverage. He acknowledges small
  teams ("I'm a team of three") need different solutions.
- **Confidence**: settled
- **Quote**: "we have an internal minimum standard of having six or maybe
  seven— I've lost track— people on each of two sides of an ocean, as it were.
  Two geographically very different sites must each have at least six or seven
  people in them. So that would be cumulatively 12 to 14 people at minimum in
  order to have an officially SRE-funded on-call team and on-call rotation."
- **Our assessment**: A concrete, citable sizing baseline. The guide should
  present it as Google's internal floor (not a universal rule) and note the
  tension with small teams that cannot meet it — APW himself says "that's totally
  fine" for smaller teams and that the rest of his advice scales down. Useful as
  a reference point in Ch04.

### Claim 9: Shift design varies, but the dominant Google pattern is a dual-homed 12/12 rotation across two time zones; variants include consecutive 7-day/12-hour blocks, "mercy shifts" (e.g., 10/14) to accommodate unequal time zones, and weekday-vs-weekend splits
- **Evidence**: APW walks through multiple real Google variants: (a) 12/12 split
  per day with two people per continent (up to 14 people/week); (b) a "mercy
  shift" of 10 and 14 when the second site's time zone makes 12/12 awkward; (c)
  consecutive 7 days × 12 hours per on-caller; (d) weekend-plus (Fri/Sat/Sun)
  vs workday (Tue/Wed/Thu) splits; (e) midday handoffs around weekends to match
  when humans deploy changes. He stresses teams should be allowed to trade shifts
  and choose what resonates.
- **Confidence**: settled
- **Quote**: "Some teams choose to have a, let's call it 'seven unique days a
  week'— like a one day of on-call, then further split into, say, 12 hours, so
  like 12/12." and "we're going to have some sort of a mercy shift, which is like
  we do 10 and 14 because of whatever the case may be."
- **Our assessment**: This is a concrete catalog of rotation shapes. The
  guide's Ch04 can use it as the "rotation shape menu" — the key transferable
  principles are: dual-homing for follow-the-sun coverage, keep an odd "mercy"
  split when sites are unbalanced, and preserve human agency to trade/choose
  shifts ("There is a robot that declares when people are on-call... you can't
  change, and deal with it" is explicitly what NOT to do).

### Claim 10: Barn-raise (bootstrap) a new rotation by seeding it with one or more senior, already-experienced SREs — even from a different product domain — plus a strong teacher, then fill with junior or senior talent as available
- **Evidence**: APW's "recipe": first person highly experienced; second person
  "relatively senior but incredibly good at helping teach the art"; third-plus
  can be senior or junior. He urges seeding with cross-domain senior SREs and
  warns against "raising someone in a vacuum" / "cargo cult engineering."
- **Confidence**: settled
- **Quote**: "if you can, try to seed a new SRE engagement with one or more
  senior, already experienced SREs, even if they are not in the same product's
  domain."
- **Our assessment**: A concrete onboarding pattern with a useful AI/LLM angle:
  seeding an AI-augmented on-call rotation should similarly start with
  experienced humans who understand both the system and the agent's behavior,
  before junior responders depend on the agent. The cross-domain "hybrid vigor"
  point (Claim 13) reinforces diversity of background in the seeding team.

### Claim 11: "Barn raising" / bootstrapping a new on-call rotation should be deliberate — pick from several recipes rather than "throwing the pager over a wall" to developers
- **Evidence**: APW frames the transition from developer-self-on-call to
  SRE-attended rotation as something to be "barn raised or bootstrapped," with
  multiple recipes "better than just turning the lights on an on-call rotation
  and throwing the pager over a wall."
- **Confidence**: settled
- **Quote**: "there are a lot of different ways to barn raise or bootstrap, if
  you will, an on-call rotation for a product."
- **Our assessment**: The barn-raising metaphor is APW's term for the
  intentional bootstrap described in Claim 10. Bundled with Claim 10, it gives
  Ch04 a named pattern for standing up a new (human or AI-augmented) rotation.

### Claim 12: Wheel of Misfortune — a low-stakes tabletop exercise where a game master pages a volunteer on-caller through a synthetic incident — builds diagnosis muscle memory, trust, and norms before real pages arrive
- **Evidence**: APW describes the format in detail: a weekly/monthly gathering;
  a game master designs a realistic trigger (e.g., "excessive 500s in Asia
  Pacific") using the team's actual alerting/monitoring vocabulary; the volunteer
  talks through where they'd look; the room listens and learns; getting stuck is
  safe ("phone a friend"); game masters occasionally run forward-looking scenarios
  (a not-yet-launched feature). He links it to the blamelessness culture.
- **Confidence**: settled
- **Quote**: "At Google, we have what we call 'Wheel of Misfortune,' which is just
  a cheesy way of saying that we do a tabletop."
- **Our assessment**: This is the canonical deep description of Wheel of
  Misfortune in this corpus. The Treynor interview note already lists a brief
  "Wheel of Misfortune — Disaster Drill Game" artifact (its Concrete Artifacts
  section) but without mechanics; this transcript supplies the full operational
  detail (game master, volunteer, authentic alert vocabulary, safe-to-fail,
  forward-looking scenarios). This note EXTENDS that brief mention into a usable
  training recipe for Ch04/Ch01. Strong AI/LLM angle: an AI agent can *generate*
  and *run* these drills (synthetic incidents, varied scenarios) at scale,
  lowering the cost of regular practice APW says should happen "regularly for
  everyone."

### Claim 13: SRE EDU puts new hires on-call for a synthetic, fully-featured but userless Google service in their second or third week, so they fail safely and build confidence before touching production
- **Evidence**: APW (co-founder of SRE EDU) describes the program: new SREs get
  paged by robots on a hypothetical service with no real users, "saving the
  universe four or five times" with no consequence, building memory and
  confidence. He ties it to the blameless culture and to regular (not
  one-time) low-stakes practice.
- **Confidence**: settled
- **Quote**: "in your second or third week on the job, you get to be on-call for
  a hypothetical Google service: fully featured, but [that] doesn't have any real
  users. It's just robots pretending to send clicks."
- **Our assessment**: A concrete, named training mechanism (SRE EDU synthetic
  on-call) that generalizes the safe-failure principle from Claim 12. For the
  guide, this is the model for how to onboard humans onto an AI-augmented
  rotation: let them operate the agent against synthetic incidents first. It
  also connects to the SRE-education theme in the NALSD classroom note (which
  covers Google's design workshops) — same source family, different training
  surface (on-call readiness vs system design).

### Claim 14: SRE intentionally grows people into a "hybrid role" (software + operations) and values "hybrid vigor" — bringing in SREs from radically different product domains strengthens the team
- **Evidence**: APW on onboarding: SREs become "a hybrid role" (software
  engineers learn ops, ops-oriented learn software). On staffing: bringing in an
  SRE from a different domain "adds hybrid vigor" and is "one of the best cases
  for eventual awesomeness." He emphasizes psychological safety and not burning
  people out.
- **Confidence**: settled
- **Quote**: "as our biologists would say, this adds hybrid vigor."
- **Our assessment**: The hybrid-role claim is consistent with the Treynor
  interview note's foundational definition of SRE (applying software engineering
  to operations, Claim 1). The "hybrid vigor" / cross-domain seeding insight is a
  concrete, novel-to-this-corpus staffing recommendation for Ch04: diversify the
  on-call team's backgrounds rather than cloning one domain's experts.

## Concrete Artifacts

### On-call vs On-duty — APW's definitions (verbatim)

```
On-call:  "you are responsible for the vitality of the uptime, the
           responsiveness of the service during your shift."

On-duty:  "some sort of probably small quanta, but maybe high quantity of
           work that needs to be done: crank turning, answering tickets,
           answering support, whatever type of stuff."
```

### Rotation shape menu — structured from APW's spoken description (attributed synthesis, not verbatim)

APW presents these as real Google variants; the Miner has structured his spoken
examples into a table. Quotes for the 12/12 and 10/14 forms are verbatim (see
Claim 9); the rest are APW's described patterns.

```
Shape A — Dual-homed 12/12 (dominant pattern)
  Two geographically distinct sites; each 24h covered by two people
  (e.g., A+B cover day 1 in 12h blocks, C+D cover day 2).
  Up to ~14 distinct people/week; shifts tradeable between colleagues.

Shape B — Consecutive block
  Same person on-call 7 days × 12h, with a colleague also doing 7×12.
  ("much more of a different end-of-the-rails sort of setup.")

Shape C — Mercy shift (uneven split)
  When the second site's time zone makes 12/12 awkward: "we do 10 and 14."

Shape D — Weekday vs weekend split
  e.g., Fri/Sat/Sun vs Tue/Wed/Thu; or a midday handoff straddling the
  weekend to match when humans deploy changes.

Cross-cutting rule: allow humans to trade/micro-optimize shifts; do NOT
impose "a robot that declares when people are on-call... and you can't
change, and deal with it."
```

### New-rotation barn-raising recipe — structured from APW's narrative (attributed synthesis)

```
1. Seed with one or more SENIOR, already-experienced SREs — even from a
   DIFFERENT product domain (cross-domain "hybrid vigor").
2. Add a strong TEACHER (relatively senior, excels at conveying the art
   and norming team culture).
3. Fill remaining seats with senior OR junior talent as available.
4. Provide a safety net: participatory education so juniors "fail in a
   theoretical exercise" before touching the control surface / solo on-call.
5. Avoid "raising someone in a vacuum" / "cargo cult engineering."
```

### Wheel of Misfortune — mechanics from APW's description (attributed synthesis with verbatim trigger)

```
Cadence:    Weekly or monthly team gathering.
Roles:      Game master (designs the scenario) + volunteer on-caller (+ observers).
Setup:      Synthetic copy of the service stack / whiteboard; OR fully verbal.
Trigger:    An authentic alert from the team's real monitoring vocabulary —
            APW's example: "you get paged for excessive 500s in Asia Pacific."
Play:       Game master narrates what the volunteer sees as they talk through
            where they'd look/click ("open Prometheus, filter to APAC region…").
Safe-fail:  Getting stuck is fine — "phone a friend"; no shame/blame.
Variants:   Forward-looking scenarios for not-yet-launched features, so the
            team learns the new surface together.
Purpose:    Build diagnosis muscle memory, mutual trust, and norms before
            real pages; reinforce blameless culture.
```

### Fatigue limit (Treynor/Sloss limit) — APW's description (verbatim core)

```
Named after Ben Treynor Sloss ("we've incorrectly called the Treynor limit—
his last name is Sloss, we should call it the Sloss limit").
Principle: sustained incident follow-through (postmortems, fixes) above a
smooth-window threshold → "cumulative failure" (can't write the postmortem
because you're being paged again).
Goal: on-caller ends shift "intrigued or refreshed— best case— or nothing
happened; I was bored." Defend the mental fatigue limit so people are "not
depleted by my on-call shift."
```

## Cross-References

- **Corroborates**:
  - `discussion-google-sre-ben-treynor-interview.md` — **Claim 7** ("SREs are
    scarce by design and allocated where they're going to do the most good";
    quote: "We will assign SREs where they're going to do the most good.")
    directly corroborates this note's **Claim 1** (leverage/scarcity/selectivity
    — SRE on-call is a deliberately scarce, allocated resource). APW supplies the
    operational concrete; Treynor supplies the strategic statement.
  - `discussion-google-sre-ben-treynor-interview.md` — **Claim 6** (the
    "throw it over the wall" anti-pattern; quote: "SWE teams write something and
    throw it over a wall to the operations teams… and throw it back") is
    corroborated by this note's **Claim 2**, where APW uses the same phrase
    ("throwing stuff over a wall") and prescribes co-on-call with developers as
    the remedy.
  - `discussion-google-sre-ben-treynor-interview.md` — **Claim 1** (SRE =
    applying software engineering to operations) is consistent with this note's
    **Claim 14** (SRE intentionally grows people into a "hybrid role").

- **Contradicts**: None identified. Every claim here is consistent with the
  existing corpus. (See note below on the primary/secondary vs co-primary
  recommendation — it is novel advice, not a contradiction of any existing note,
  none of which prescribe a co-primary model.)

- **Extends**:
  - `discussion-google-sre-ben-treynor-interview.md` — **Concrete Artifacts →
    Wheel of Misfortune — Disaster Drill Game section**. That note lists Wheel of
    Misfortune only as a named artifact (format/roles/goal) with no operational
    mechanics. This note's **Claim 12** and Concrete Artifacts supply the full
    worked mechanics (game master, volunteer, authentic alert vocabulary,
    safe-to-fail, forward-looking scenarios). This note extends that bare mention
    into a usable training recipe. Also, this note's **Claim 3** names the
    fatigue limit after the very authority (Ben Treynor Sloss) that the Treynor
    interview note is built around — linking the two sources by shared authority.
  - `docs-google-sre-nalsd-classroom.md` — same Google SRE source family and the
    same *education* theme, but a different training surface. The NALSD note's
    **Concrete Artifacts → SRE Classroom Workshop Descriptions** covers design
    workshops (PubSub, ImageServer, Art of SLOs); this note covers the on-call
    readiness training that SRE EDU provides (synthetic on-call service, Wheel of
    Misfortune). This note extends the corpus's coverage of Google SRE education
    from "how we teach system design" to "how we teach on-call." APW states he
    co-founded SRE EDU (line 198), which is distinct from the NALSD classroom
    program the other note covers.

- **Novel** (new to the corpus from this source):
  - The **leverage/scarcity/selectivity** framing for *which* services get SRE
    on-call (Claim 1) — the demand-side counterpart to Treynor's scarcity claim.
  - The **Treynor/Sloss fatigue limit** as a named, defended guardrail (Claim 3).
  - The **on-call vs on-duty** distinction and the case for separating them
    (Claim 4).
  - The **primary + secondary (not two co-primaries)** model and its
    agency/visibility rationale (Claim 5).
  - The **VP-equivalent on-call authority / single-decider** principle (Claim 6).
  - The **mercy substitution** policy for multi-night pages (Claim 7).
  - The **12–14 person dual-site minimum** for an SRE-funded rotation (Claim 8).
  - The **rotation shape menu** (12/12 dual-homed, 10/14 mercy shift, 7×12
    blocks, weekday/weekend splits) (Claim 9).
  - The **barn-raising / cross-domain seeding** recipe for new rotations
    (Claims 10, 11).
  - The full **Wheel of Misfortune** mechanics (Claim 12).
  - The **SRE EDU synthetic on-call** training mechanism (Claim 13).
  - The **hybrid role / hybrid vigor** staffing insight (Claim 14).

  Qualitative topic link (no specific claim number cited, not deeply
  cross-read for this issue): the strong on-caller-agency theme here (Claims 5,
  6) supports the "AI-assisted, not AI-native" position in
  `blog-pagerduty-sre-agent-architecture.md` — an AI "secondary" preserving a
  human single decider aligns with APW's agency argument, whereas a co-primary
  AI would dilute it.

## Guide Impact

This is the **first source note focused on on-call rotation patterns**, and the
triage notes Ch04 (On-call and Toil) is currently a stub with no sourced claims.
The guide should adopt the following, all citable to this note:

- **Chapter 04 (On-call and Toil)**: Seed the chapter's first sourced claims:
  1. **Rotation model**: recommend a primary + secondary structure, not two
     co-primaries (Claim 5) — cite the agency/visibility argument.
  2. **Fatigue limit**: size rotations to defend a fatigue limit; if incident
     follow-through exceeds a smooth-window threshold, adjust the SLA/sizing
     (Claim 3). Name it the Treynor/Sloss limit.
  3. **Mercy substitution**: adopt a policy letting a colleague take the rest of
     a shift after repeated night pages (Claim 7) — flag it as emerging/lower
     confidence since APW speculates it.
  4. **On-call vs on-duty**: keep the two separate so on-duty toil doesn't drain
     on-call freshness (Claim 4) — this is the natural hook for *where AI agents
     should help* (absorb on-duty ticket work, preserve human on-call capacity).
  5. **Sizing floor**: cite Google's ~12–14 person dual-site minimum as a
     reference point, with the caveat that smaller teams need different shapes
     (Claim 8).
  6. **Rotation shapes**: present the shape menu (Claim 9) as the design options.
  7. **New rotations**: use the barn-raising recipe — seed with cross-domain
     senior SREs + a teacher (Claims 10, 11, 14).
  8. **Training**: adopt Wheel of Misfortune (Claim 12) and SRE EDU-style
     synthetic on-call (Claim 13) as the on-call-readiness training pattern.

- **Chapter 00 (Principles)**: Add the leverage/scarcity/selectivity framing
  (Claim 1) as the rationale for *selective* SRE on-call, and the co-on-call
  "feel the pain of the service" remedy (Claim 2) to the throw-over-the-wall
  anti-pattern already sourced from Treynor (Claim 6). Both corroborate and
  extend existing Ch00 material.

- **Chapter 01 (Incident Response)**: Use Wheel of Misfortune (Claim 12) as the
  incident-response *training* mechanism, and the VP-equivalent on-call authority
  / single-decider principle (Claim 6) to argue that incident command must remain
  with an identifiable human even when AI agents assist.

- **AI/LLM relevance (measured)**: As the triage assesses, this source has no
  AI/LLM angle — it is foundational SRE on-call practice. The guide should treat
  it as **prerequisite knowledge** for Ch04, not as AI-specific content. The one
  durable bridge: APW's on-call/on-duty split (Claim 4) and single-decider agency
  (Claims 5, 6) are exactly the constraints that determine *how* AI agents should
  augment on-call (absorb on-duty toil; assist, never co-decide). The Smith
  should pair this note with the AI-agent architecture notes when writing Ch04.

## Extraction Notes

- The source is a single self-contained transcript page on sre.google
  (`/prodcast/transcripts/sre-prodcast-01-07/`). WebFetch returned no model
  response for this URL, so the transcript was retrieved directly with `curl`
  and HTML-stripped to plain text; all quotes were copied character-for-character
  from that extracted text (line numbers in the assessment fields refer to the
  local extracted transcript). No sub-pages were followed — the episode is
  self-contained and links only to the general Prodcast index.
- **Publication date**: The page carries no reliable publication date. The only
  date string in the HTML is `2022-03-31`, which is a "New!" badge release marker
  on the Resources nav item (`data-release-date`), not the episode date. Nav
  gallery years (2020/2022/2024) are also unrelated. `date_published` is therefore
  set to `unknown`; the registry build copies the string verbatim and is unaffected.
- **Confidence rationale**: `confidence_overall: settled` reflects that these are
  established Google SRE practices described by a ~15-year practitioner, and the
  patterns (fatigue limit, primary/secondary, dual-homed 12/12, Wheel of
  Misfortune, SRE EDU) are canonical Google on-call canon. Two claims are graded
  lower: Claim 5 (primary/secondary) is `emerging` because APW explicitly frames
  it as "my personal preference"; Claim 7 (mercy substitution) is `emerging`
  because he explicitly says "I'm merely speculating" and it is not a Google
  practice he is reporting. These lower grades are noted in-line.
- **No contradiction filed**: No claim here opposes any existing source note.
  The primary/secondary recommendation is new advice, not a rebuttal of an
  existing co-primary recommendation (none exists). Per MINER.md §4a, no
  contradiction issue is warranted.
- **Cross-reference verification**: Claim numbers cited from
  `discussion-google-sre-ben-treynor-interview.md` (Claims 1, 6, 7) and its Wheel
  of Misfortune Concrete Artifact were re-read and confirmed against that note
  before citation. The NALSD classroom note was read for the SRE-education
  overlap. The PagerDuty architecture note is referenced only qualitatively
  (AI-assisted vs AI-native), with no specific claim number asserted, because it
  was not deeply cross-read for this issue.
- The source predates the LLM era and contains no AI/LLM content; AI/LLM
  applications in Guide Impact are the Miner's analytical bridge, to be reviewed
  by the Smith for fidelity.
