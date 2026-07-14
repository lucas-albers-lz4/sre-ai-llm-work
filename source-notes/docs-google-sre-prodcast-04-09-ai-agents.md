---
source_url: https://sre.google/prodcast/transcripts/sre-prodcast-04-09/
source_type: docs
title: "The One With AI Agents, Ramón Llamas, and Swapnil Haria (SRE Prodcast S4E9)"
author: "Ramón Medrano Llamas (Senior Staff SRE, Google Core SRE) and Swapnil Haria (Software Engineer, Google Core Labs); interviewed by Steve McGhee & Matt Siegler (Google SRE Prodcast hosts)"
date_published: 2025 (est.; Season 4 — exact episode air date is not published on the transcript page)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: settled
issue: "#105"
---

# The One With AI Agents, Ramón Llamas, and Swapnil Haria (SRE Prodcast S4E9)

> A first-person Google-practitioner account of *building* production AI agents
> for SRE: the agent spectrum, read-vs-write capability boundaries, the
> pre-on-caller triage pattern, the golden-label / postmortem-trajectory
> evaluation methodology, the Generic Mitigations taxonomy, proactive
> change-review use cases, and explicit limits on where LLMs (and autonomy)
> should *not* go.

## Source Context

- **Type**: docs (official Google SRE Prodcast episode transcript — S4E9,
  "The One With AI Agents"). The page is a full, public HTML transcript on the
  official sre.google domain; it was fetched and stripped of scripts/styles to
  recover the dialogue verbatim.
- **Author credibility**: Highest available. Ramón Medrano Llamas is a Senior
  Staff SRE at Google (12 years; Core SRE — runs infrastructure from
  auth to data; ~1 year building production-management agents). Swapnil Haria is
  a Software Engineer in Core Labs (the part of Google building AI agents for
  different use cases), with a background spanning VLSI, processors, OS, and
  databases before agentic work. Both are *practitioners who built the system*,
  not vendors or commentators — this is primary-source, deployed-experience
  testimony, which is rarer and higher-signal than the vendor blog posts in the
  corpus. Hosts Steve McGhee (Reliability Advocate, SRE) and Matt Siegler (ML
  Infrastructure SRE) are practicing Google SREs.
- **Scope**: The episode covers (a) what "agent" means, built incrementally
  from static algorithms through LLM-augmented to full agents; (b) agent
  capabilities and the read-only vs world-modifying boundary; (c) safety
  guardrails (sandboxing + human permission for writes); (d) what already works
  in production — one-shot alert summarization and the agent-as-pre-on-caller
  triage pattern; (e) the hard problem of *evaluation* — golden labels from
  historical incidents, hill climbing, postmortem trajectory matching, the
  data-retention problem, and the "production has no sandbox" framing; (f) the
  Generic Mitigations taxonomy and terminology-collision failure story; (g)
  proactive / pre-incident use cases; (h) explicit limits — don't use LLMs
  where regex/specialist models fit, and don't insulate humans from learning
  (Ironies of Automation); (i) an autonomy-levels outlook. It does NOT cover
  agent coding details, model architecture, or specific tooling internals.

## Extracted Claims

### Claim 1: An "agent" is best understood as a spectrum — from static deterministic algorithms, through algorithms with LLM-augmented steps, to full agents with no fixed script that dynamically construct their own step sequence
- **Evidence**: Swapnil's incremental definition, contrasting a static algorithm
  ("a set of sequences… I can work through with pen and paper") with a full
  agent ("there is no script anymore. The agent gets an input. It has some
  high-level understanding of how to solve the problem, but it comes up with its
  own set of sequence, steps dynamically on the fly").
- **Confidence**: settled
- **Quote**: "So I think the right way to talk about agents is to build
  incrementally. So we have our static deterministic algorithms, where it's a
  set of sequences. You have an input. I can work through with pen and paper--
  how the operations are going to happen? How the input is going to be
  transformed into the final output? So that's a static algorithm."; "And then
  we go to the other end, which is the full agent, where there is no script
  anymore. The agent gets an input. It has some high-level understanding of how
  to solve the problem, but it comes up with its own set of sequence, steps
  dynamically on the fly."
- **Our assessment**: A clean, durable framing that maps onto the guide's
  agent-autonomy discussion. Useful because it lets the Smith grade claims by
  where on the spectrum a given practice sits, rather than treating "agent" as a
  monolith.

### Claim 2: Agent capabilities split into two categories — fetching context not in training data (read), and world-modification with side effects (write) — and you must know exactly what you hand the agent because when/how a capability gets called is hard to predict
- **Evidence**: Swapnil on tool calls bringing dynamic/up-to-date info;
  Ramón on "world modification capabilities or capabilities with side effects,"
  e.g. "if we are in production, trigger a binary rollout." Ramón's warning that
  prediction of invocation is "not that trivial."
- **Confidence**: settled
- **Quote**: "there are others, like a world modification capabilities or
  capabilities with side effects, like, I don't know, if we are in production,
  trigger a binary rollout, So the tools and the capabilities that you give to
  the agent, you need to know what you are giving it because knowing or
  predicting how and when they are going to be called is not that trivial."
- **Our assessment**: This read/write split is the conceptual backbone of the
  whole safety discussion (Claims 3, 5, 15, 16). It is consistent with and more
  sharply stated than the human-in-the-loop emphasis in the adjacent Prodcast
  notes; a strong anchor for the guide's autonomy/guardrail section.

### Claim 3: The default guardrail is to deny agents any world-mutating action and require explicit human permission before any write — writes run in a sandbox, and anything that breaks the sandbox needs an additional check
- **Evidence**: Swapnil: "we don't allow them to make any kind of world
  modification erm, any ways to mutate the state of the world. So right actions
  are typically very restricted" and "we try to get human permission before it
  does anything. So it will recommend that you do this, or it will say, can I go
  ahead and make this call?" Ramón cites Claude Code as a tool with "some safety
  parameters as well."
- **Confidence**: settled
- **Quote**: "So typically, at least in the agents that we build today, we don't
  allow them to make any kind of world modification erm, any ways to mutate the
  state of the world. So right actions are typically very restricted."; "In our
  case, we try to get human permission before it does anything. So it will
  recommend that you do this, or it will say, can I go ahead and make this call?
  And there'll be a yes or no option."; "Now, this is a common pattern that you
  see it in tools that are, for example in Claude code, that is a CLI to do
  coding in your computer and your workstation. It has some safety parameters as
  well."
- **Our assessment**: Concrete, operational guardrail detail from a team that
  shipped this. The Claude Code citation is a nice external corroboration that
  the read/restricted-write pattern is becoming a cross-tool norm. Maps directly
  to the guide's "keep a human in the loop for writes" guidance.

### Claim 4: One-shot alert summarization already works reliably well in production — the agent weaves signal from noise across logs/Prometheus and can surface a hidden error via a large-context "needle in a haystack" search
- **Evidence**: Ramón: "one shot summaries, or one shot responses… It can
  summarize the situation really well for you." Swapnil: thousands of lines of
  logs per second; the LLM "summarizing all of it and weeding out the wheat from
  the chaff," and "you can dump a lot of information in there and say, OK, do you
  see anything that resembles the error message I'm seeing? So you can use it to
  find a needle in a haystack."
- **Confidence**: settled
- **Quote**: "One thing that we have seen that works really, really well across
  the board is what is called one shot summaries, or one shot responses. So you,
  in production, give the agent access to many data sources… It can summarize the
  situation really well for you"; "So this is one way in which an LLM can help,
  where it's summarizing all of it and weeding out the wheat from the chaff in
  some ways, keeping the important bits, removing all of the extraneous
  information."; "So you can use it to find a needle in a haystack if you wanted
  to."
- **Our assessment**: This is the single most "shipped and working" claim in the
  episode, and it corroborates Treynor's S4E3-style summarization claim (see
  Cross-References). High-value for the guide's alerting/incident section:
  summarization is the low-risk, high-payoff on-ramp the Smith can recommend
  first.

### Claim 5: The agent acts as a pre-on-caller — it performs the common triage steps (release check, error-rate diff) in the ~3–4 minutes before the human arrives, either finding root cause or ruling out mitigations, but the human still makes the call and applies changes
- **Evidence**: Swapnil's end-to-end description: "the agent steps in first. By
  the time the human gets to their desk, which is typically three or four
  minutes… the agent has already done a lot of the common steps that the
  on-caller would have done." It "can either say, hey, look I found, the
  underlying root cause. Or it can say… I have ruled out these 16 things." The
  human "have[s] to make the call… here's how I can apply the changes directly."
- **Confidence**: settled
- **Quote**: "So when the alert gets triggered, we have some use cases where the
  agent steps in first. By the time the human gets to their desk, which is
  typically three or four minutes, or they are context-switching away from
  working on something else, the agent has already done a lot of the common
  steps that the on-caller would have done."; "And they have to make the call,
  OK, this looks right. Here's the agent supporting evidence for that. And if it
  looks right, here's how I can apply the changes directly."
- **Our assessment**: This is the concrete operational pattern the index note
  promised but did not mine. It is a precise, deployable shape (triage-before-
  human, ruled-out-set presentation, human owns the write) that the guide's
  incident-management chapter can adopt almost verbatim. Strongly corroborates
  the human-in-the-loop stance elsewhere in the corpus.

### Claim 6: The real business value is compressing user-facing unavailability (SLO/SLA "bleed"), not just saving the engineer a few minutes — fewer minutes of service-unavailable is "really, really what it's about"
- **Evidence**: Ramón's reframing after the toil-saving discussion: an alert
  means "some service is bleeding out some reliability. And some users are
  affected" with "revenue impact… financial or a reputational" cost; the agent
  "reduces the amount of time that your service is not available for your users."
- **Confidence**: settled
- **Quote**: "what matters is that when you have an alert, you have an SLO or an
  SLA that is under the threshold or whatever it is. That typically means that
  some service is bleeding out some reliability. And some users are affected…
  this reduces the amount of time that your service is not available for your
  users, which is really, really what it's about"
- **Our assessment**: An important framing correction: justify agent investment
  on MTTR/unavailability reduction and user impact, not engineer-comfort. Useful
  for the guide's "measure the agent's value" guidance.

### Claim 7: Evaluation is the golden question, and production is fundamentally harder to evaluate than coding agents because "production is not a sandbox" — you cannot let the agent take the destructive action just to see what happens
- **Evidence**: Ramón contrasts the dev-side coding agent ("you spin a sandbox,
  worst-case scenario is like, just compile your application… If it compiles,
  passes the unit test, you have an evaluation there") with production ("When
  you are on the right-hand side in production and you have agents that they
  might take actions in production, there is no-- production is not a sandbox.
  And if you decide like, hey, this agent is going to drain every single cluster
  or every single data center… it's gonna go for it").
- **Confidence**: settled
- **Quote**: "When you are doing a development agent, like for coding, for Cursor
  this kind of stuff, you have a sandbox… you have the luxury of being at the, I
  call it, the left-hand side of the development cycle because you spin a
  sandbox, worst-case scenario is like, just compile your application with the CL
  or the patch that is producing. And that's the test. If it compiles, passes
  the unit test, you have an evaluation there."; "When you are on the right-hand
  side in production and you have agents that they might take actions in
  production, there is no-- production is not a sandbox."
- **Our assessment**: One of the episode's most cited insights and a clean
  principle for the guide's evaluation section: the sandbox that makes coding
  agents evaluable does not exist in production, so you must evaluate against
  historical/labeled data (Claims 8–10) rather than live trial-and-error. This
  is the crux of the "non-deterministic system evaluation" theme the index note
  flagged.

### Claim 8: Build a golden-label evaluation set from historical incidents — label each alert with the action that actually fixed it (e.g. "we rolled back the binary. We upsized the cell. We took some emergency quotas. We throttled the user"), then check the agent's output against those labels; but real-world dashboard data is retained only ~20–30 days, so golden data must be continuously regenerated
- **Evidence**: Swapnil's full description: the labels are "golden labels that
  you can have. And for each incident, we need to find out what was the actual
  action that fixed the issue." Plus the retention problem: "the real-world data
  that the agent is looking at, dashboards and things like that, often gets lost
  over time. It might be retained for, let's say, 20 days, 30 days. But beyond a
  certain point, you lose access to that old data." Closing the loop: record the
  on-caller's final step so the agent improves.
- **Confidence**: settled
- **Quote**: "So in our case, we had a bunch of alerts, and we had the right
  labels for each of them. So the label was something like, we rolled back the
  binary. We upsized the cell. We took some emergency quotas. We throttled the
  user, things like that. These are golden labels that you can have. And for each
  incident, we need to find out what was the actual action that fixed the issue.";
  "the real-world data that the agent is looking at, dashboards and things like
  that, often gets lost over time. It might be retained for, let's say, 20 days,
  30 days. But beyond a certain point, you lose access to that old data."
- **Our assessment**: Concrete, replicable evaluation practice — the
  practitioner counterpart to the PagerDuty "golden dataset + LLM-as-a-judge + CI
  gate" pipeline (see Cross-References). The ~20–30-day retention caveat is a
  genuinely useful, non-obvious operational detail the Smith should surface:
  golden-data programs decay unless continuously refreshed.

### Claim 9: The build methodology is golden-dataset-first, then iterative hill climbing (RLHF is one technique), using in-context learning on a vanilla model — they do NOT train a new model; they just engineer the prompt context
- **Evidence**: Swapnil: "the first step in any of these agent-building workflows
  is to have something called a golden data set. It has the input… and it has a
  perfect output or a good enough output." Ramón: "The overall objective is
  called hill climbing… iterative hill climbing is an umbrella term… RLHF…
  is a technique that you could use." On model choice: "the models that we use is
  Gemini vanilla… we just use the context. What we do is in context learning."
- **Confidence**: settled
- **Quote**: "So it's important to start with the end in mind. So for example,
  the first step in any of these agent-building workflows is to have something
  called a golden data set. It has the input… and it has a perfect output or a
  good enough output for that use case."; "The overall objective is called hill
  climbing, because you can think of it as trying to get to a local maxima. So
  iterative hill climbing is an umbrella term for this. And RLHF, Reinforcement
  Learning through Human Feedback, is a technique that you could use."; "the
  models that we use is Gemini vanilla… we just use the context. What we do is in
  context learning. So when we are creating is the context for the prompt, it
  might be a loop of multiple prompts to the same model with different
  information."
- **Our assessment**: Demystifies "building an agent" as prompt-context
  engineering + golden-data iteration, not model training. This lowers the
  barrier for readers and matches the guide's "you're not training models,
  you're composing them" reality. Strong, practical material.

### Claim 10: Postmortems are "super great training data" because they contain the full *trajectory* (timeline of steps), not just the final mitigation — you compare the agent's step-by-step trajectory against the human's to find where it went wrong (wrong tool call, misread tool output, missing tool)
- **Evidence**: Ramón: postmortems give "the trajectory of the person… And you
  have what is called the timeline. So you have all the steps that the person
  took." Inspecting agent output "is exactly that timeline but produced by one of
  the agents. So you can see, I'm calling this tool, and I got this data. This is
  a red herring." Swapnil adds the agent's output is compared to "this was the
  exact mitigation" — and mismatches reveal "did it call a tool wrong? Did it
  interpret the output of a tool wrongly? Or… did it not have the right tool to
  call?"
- **Confidence**: settled
- **Quote**: "It's this super great training data because adjusting or golden
  data for two reasons. It's not only that you have the response of, this is the
  mitigation that we had. You have the trajectory of the person, typically in
  postmortems… And you have what is called the timeline. So you have all the
  steps that the person took."; "So when we are inspecting the agent output,
  what we're seeing is exactly that timeline but produced by one of the agents.
  So you can see, I'm calling this tool, and I got this data. This is a red
  herring."
- **Our assessment**: The trajectory-matching idea is the episode's most
  original evaluation contribution and is novel to the corpus (no other note
  describes comparing agent step-sequences to postmortem timelines). It also
  reinforces the guide's postmortem-culture material (Ch15) from a new angle:
  good postmortems are now *machine-readable training/eval data*, so format
  matters (see Claim 13).

### Claim 11: A concrete agent failure came from tools returning dates in different time zones (UTC vs Mountain time) — humans knew the convention, the agent didn't, so they wrapped every system to always return Mountain View time
- **Evidence**: Swapnil's "example that we often quote": tools "were returning
  dates in different time zones. So one of them would say the alert happened in
  UTC time. The other would say in Mountain time. And this was well known for
  humans who are used to these things, but it was not obvious to the agent." Fix:
  "all the time zones are in Mountain View time zone… we made sure we had wrappers
  around each of our systems so that they would always return things in Mountain
  View time zone."
- **Confidence**: settled
- **Quote**: "there were a bunch of tools that our production agent had access
  to. And all of them were returning dates in different time zones. So one of
  them would say the alert happened in UTC time. The other would say in Mountain
  time. And this was well known for humans who are used to these things, but it
  was not obvious to the agent. So we have a specific line in there where we say,
  OK, all the time zones are in Mountain View time zone, which is the
  headquarters for Google, and we made sure we had wrappers around each of our
  systems so that they would always return things in Mountain View time zone."
- **Our assessment**: A vivid, specific failure story — exactly the kind of
  concrete artifact the Assayer looks for. The lesson (normalize inputs at the
  tool-wrapper boundary; agents don't know human conventions) generalizes beyond
  time zones and is a great caution for the guide's integration section.

### Claim 12: A shared, cross-team "Generic Mitigations" taxonomy is required so the same action means the same thing everywhere — but the first taxonomy broke on terminology collisions ("escalate" meant severity-bump to one team, hand-off to another → renamed "delegate"; "experiments" meant different things), and Google has published a Generic Mitigations list of ~20
- **Evidence**: Swapnil: "we are trying to build a common language of sorts for
  some of these mitigations. So we have a taxonomy… you would roll back a binary.
  You would add resources." Terminology collisions forced renames. Ramón: "There
  is a nice publication that is called Generic Mitigations that we made public…
  it already has 20 of them."
- **Confidence**: settled
- **Quote**: "we had to move to 'delegate.' Same with 'experiments,' different
  teams consider 'experiments' to be different things. So when we say 'roll back
  an experiment,' they might understand it differently. But we need this common
  language to be there in all of the postmortem so that the agent, which is the
  same across these teams, can improve consistently."; "There is a nice
  publication that is called Generic Mitigations that we made public. I think it
  was like a few years ago. It already has 20 of them."
- **Our assessment**: Two valuable things: (1) the concrete failure mode of a
  shared vocabulary (terminology collision) and how they resolved it; (2) a
  pointer to the public Generic Mitigations publication, grounding the index
  note's S1E1 reference in primary content. Directly useful for the guide's
  runbook/mitigation-language material.

### Claim 13: The majority of the work in building production AI agents is NOT the AI — it is integration plumbing: connecting tools, data access, and converting postmortems in inconsistent formats across teams into a uniform human-and-machine-readable form
- **Evidence**: Ramón: "the majority of the work that you are putting together
  for working in AI is not in AI. It's integrating different tools, different
  data access, accessing different postmortems in different formats for different
  teams." The single highest-leverage step: "just formatting the postmortem in
  human and machine readable format. So they are all the same. That gets you
  like a head."
- **Confidence**: settled
- **Quote**: "one thing that we discovered working on this is that the majority
  of the work that you are putting together for working in AI is not in AI. It's
  integrating different tools, different data access, accessing different
  postmortems in different formats for different teams that there might be old,
  for example, postmortems from last year. It takes a while to curate and process
  all of these. So for example, just formatting the postmortem in human and
  machine readable format. So they are all the same. That gets you like a head."
- **Our assessment**: A sobering, realistic counterweight to "just prompt an
  LLM" optimism. Worth elevating in the guide as the expected cost profile of
  agent projects — most effort is data/tooling integration, which loops back to
  why postmortem formatting (Claim 10) and the mitigation taxonomy (Claim 12)
  matter so much.

### Claim 14: Beyond incident response, agents earn their keep as (a) day-to-day companions for routine production touches (rollouts, performance regression, capacity moves) and (b) pre-change risk reviewers that flag risky configuration before it ships — "the best time to mitigate an incident is 0"
- **Evidence**: Ramón: "In 98% of the time that you don't have an incident, you
  still have to touch production… Agents can help with that." And prevention:
  "the best time to mitigate an incident is 0… agents might help us enforcing and
  discovering these spots where there are risks that we don't know about,
  dependencies, a service that has five 9s of SLO depending on one service that
  has two." Swapnil's admission-control example: the agent flags a bad config
  "even before you make that change-- so when you send that change out for
  review."
- **Confidence**: emerging
- **Evidence note**: Described as work "we are looking at" / examples, i.e.
  near-term roadmap rather than a shipped, measured result — hence emerging.
- **Quote**: "In 98% of the time that you don't have an incident, you still have
  to touch production because you need to do your rollout. You need to observe
  performance regression."; "the best time to mitigate an incident is 0. So it's
  preventing the incidents from happening… agents might help us enforcing and
  discovering these spots where there are risks that we don't know about,
  dependencies, a service that has five 9s of SLO depending on one service that
  has two"; "even before you make that change-- so when you send that change out
  for review, it can step in and say, hey, look, you've configured the admission
  control in this way, but I don't think that's the right idea, based on what I
  see."
- **Our assessment**: Extends the guide's automation/toil and proactive-SRE
  material with specific, plausible patterns. The "5-nines depending on
  2-nines" SLO-dependency detection and the change-review gate are the most
  concrete and actionable; the rest is directionally sound but not yet
  measured, so treat as emerging.

### Claim 15: Explicit limits — do NOT use LLMs where a regex or a small specialist model fits (anomaly detection on a time series is "faster, cheaper, and more reliable" as a classic method), and do NOT use LLMs to insulate humans from challenging incidents, or you break their learning loop (the "Ironies of Automation")
- **Evidence**: Ramón: "One thing I would not use LLMs for is for when you can
  use a regular expression for things" and "the classic statistical methods or
  very small specialist models for doing certain things, like anomaly detection
  of a time series. It's a much better-suited model. They're faster, cheaper, and
  more reliable." Swapnil: don't use LLMs "for insulating humans from challenging
  situations… as engineers, that's how we learn over time… if it's completely
  offloaded to an agent and we have no idea that an outage even happened because
  the agent took care of it for us, because in that way, we'll never learn."
  Steve names "The Ironies of Automation, where the more you automate a thing,
  the worse you get at it."
- **Confidence**: settled
- **Quote**: "One thing I would not use LLMs for is for when you can use a
  regular expression for things."; "there are some cases where the classic
  statistical methods or very small specialist models for doing certain things,
  like anomaly detection of a time series. It's a much better-suited model.
  They're faster, cheaper, and more reliable."; "one thing I would not like to
  see LLMs used for is insulating humans from challenging situations… if it's
  completely offloaded to an agent and we have no idea that an outage even
  happened because the agent took care of it for us, because in that way, we'll
  never learn."; "There's a famous paper called The Ironies of Automation, where
  the more you automate a thing, the worse you get at it."
- **Our assessment**: This is the episode's most important *caution* and a
  deliberate counterweight to agent enthusiasm. Both limits are well-supported
  and directly usable in the guide: (1) right-tool-for-the-job (don't LLM what a
  regex/specialist model does better); (2) preserve the human learning loop —
  which dovetails with the incident-response note's "an outage you don't learn
  from is a failure" (see Cross-References).

### Claim 16: Agent autonomy is incremental and leveled — every agent they have today requires human verification before acting, but the next frontier is defining the conditions under which agents can act automatically and even self-recover
- **Evidence**: Ramón: "how is the autonomy of these agents is something that is
  incremental. So we are going to see levels of autonomy going on… all the agents
  that we have… they always require a human verification before going and execute
  some actions." Future work: "how could be the conditions or what we should be
  having in production for leaving the agents to do things automatically? So how
  we could… recover from an agent breaking some stuff or the agent recover itself
  and these kind of things?"
- **Confidence**: emerging
- **Evidence note**: Framed as an outlook / research direction ("what I would
  like to work next"), not a deployed capability — hence emerging.
- **Quote**: "how is the autonomy of these agents is something that is
  incremental. So we are going to see levels of autonomy going on. So I think we
  are at the beginning of this because all the agents that we have and the agents
  that I have seen around, they always require a human verification before going
  and execute some actions."; "how could be the conditions or what we should be
  having in production for leaving the agents to do things automatically? So how
  we could, for example, recover from an agent breaking some stuff or the agent
  recover itself and these kind of things?"
- **Our assessment**: A clean autonomy-levels framing that lets the guide present
  current practice (human-in-the-loop, Claims 3/5) as "level 0–1" and the
  self-recovering agent as an open, cautious horizon. Consistent with — not in
  tension with — the human-in-the-loop emphasis across the corpus.

## Concrete Artifacts

### Agent capability / safety model (from the dialogue)

```
Agent capabilities, as described by Ramón & Swapnil:
  - Context-fetching (READ): pull dynamic/up-to-date info the model's
    training data lacks (weather, location, Prometheus time series, logs).
  - World-modification (WRITE / side effects): e.g. "trigger a binary
    rollout" — must be known and bounded, because when/how it is invoked
    is "not that trivial" to predict.

Default guardrail (Swapnil):
  - No world-mutating action allowed by default.
  - Writes happen in a sandbox; breaking the sandbox needs extra checks.
  - Before any write: "we try to get human permission... can I go ahead
    and make this call? And there'll be a yes or no option."
```

### The pre-on-caller triage pattern (Swapnil, verbatim workflow)

```
When the alert fires:
  1. Agent steps in FIRST.
  2. In the ~3-4 min before the human reaches their desk, the agent does
     the common on-caller steps:
       - "was there a release recently?"
       - "Is the new release showing a higher error rate than the old?"
  3. Agent either:
       - reports the underlying root cause, OR
       - reports "I have ruled out these 16 things" (ruled-out set).
  4. Human reviews the agent's evidence and MAKES THE CALL.
  5. Human applies the change directly ("here's how I can apply the
     changes directly").
```

### Golden-label evaluation set (Swapnil, verbatim example labels)

```
Per-alert golden labels = the action that actually fixed the issue:
  - "we rolled back the binary"
  - "we upsized the cell"
  - "we took some emergency quotas"
  - "we throttled the user"
Agent output is checked against these actual labels.
Caveat: real-world dashboard data retained only ~20-30 days before
loss -> golden data must be continuously regenerated; close the loop by
recording the on-caller's final action.
```

### Build methodology (Swapnil / Ramón)

```
1. Golden data set first: input + "perfect / good-enough" output.
2. As a human, list the tools/dashboards you'd use; teach the LLM those.
3. Compare against ideal response; iteratively remove variance.
4. Objective = iterative "hill climbing" (local maxima); RLHF is one
   technique under that umbrella.
5. Model = Gemini vanilla; method = IN-CONTEXT learning (prompt-context
   engineering + multi-prompt loops). NO model training.
```

### Evaluation via postmortem trajectory matching (Ramón)

```
Postmortem = mitigation + TIMELINE (the human's step-by-step trajectory).
Inspect agent output as the same kind of timeline:
  "I'm calling this tool, and I got this data. This is a red herring.
   And calling this other tool..."
Mismatch analysis:
  - did it call a tool wrong?
  - did it interpret a tool's output wrongly?
  - did it not have the right tool to call?
```

### Generic Mitigations taxonomy — terminology collision (Swapnil)

```
Goal: a cross-team common language of mitigations (rollback, add
resources, run experiments...).

Failure: "escalate" meant "hand off to another service's on-caller" to
the agent team, but the incident system used "escalate" to mean
"increase severity" -> collision. Resolution: renamed to "delegate".
"experiments" also meant different things across teams.

Reference: public "Generic Mitigations" publication (~20 mitigations).
```

### Named failure story — multi-timezone tool outputs (Swapnil)

```
Tools returned dates in different time zones:
  - one said the alert happened in UTC
  - another said Mountain time
Humans knew the convention; the agent did not.
Fix: "all the time zones are in Mountain View time zone" + wrappers
around every system to always return Mountain View time.
```

## Cross-References

- **Corroborates**:
  - **`docs-google-sre-prodcast-03-03-treynor-ai-ml.md` Claim 8** (Gemini
    incident summarization turns chat history + signals into a paragraph for a
    new responder in "five seconds or two seconds," saving ~6 minutes) and
    **Claim 9** (summaries must be role-aware). S4E9's Claim 4 (one-shot
    summarization, wheat-from-chaff, needle-in-haystack) is the same practice
    described from the *builder's* side, adding the operational shape. Treynor
    Claim 11 (AI drafts YAML, human owns submission, ~3x faster with review)
    corroborates S4E9 Claims 3/5 (human owns the write).
  - **`docs-google-sre-prodcast-03-06-incident-response-tooling.md` Claim 8**
    (AI is "a tool like anything else" — good at toil/summarization/automatic
    rollbacks but "not creative… at the moment" and not to be trusted on
    crown-jewel systems without human oversight) directly corroborates S4E9
    Claims 3/5/15. **Claim 14** ("An outage that you don't learn from is a
    failure") corroborates S4E9 Claim 15's "don't insulate humans from learning"
    (Ironies of Automation) caution. **Claim 16** (destructive automation must
    not default to total action on bad input; keep a human in oversight)
    corroborates the write-guardrail stance.
  - **`blog-pagerduty-production-ai-agent-gaps.md` Claim 10** (automated
    evaluation pipelines: golden datasets + LLM-as-a-judge + CI gates) is the
    vendor-ecosystem parallel to S4E9 Claim 8/9 (golden-label eval) — PagerDuty
    frames it as a *pipeline*; S4E9 as an *incident-history labeling* practice.
    Complementary, not redundant. PagerDuty's "predictable outcomes from a
    non-deterministic system" framing (around line 294) is the same evaluation
    problem S4E9 Claim 7 names "production is not a sandbox."
  - **`blog-incidentio-ai-sre-incident-run.md`** (human-in-the-loop; tool
    integration → human-in-the-loop → gradual automation) corroborates S4E9
    Claims 3/5/16 (gradual, human-verified autonomy rather than autonomous
    action).
  - **`docs-google-sre-prodcast.md` Claim 8** already names S4E9 at the index
    level ("AI agents for alert summarization… challenges of evaluating
    non-deterministic systems") and points to "golden data sets." This note
    **extends** that index entry with the actual mined transcript (see Extends).

- **Extends**:
  - **`docs-google-sre-prodcast.md`** — the index note explicitly defers deep
    transcript extraction ("the substance lives in linked transcripts — being
    mined separately"). This note fulfills that deferral for S4E9, supplying the
    concrete claims the index only summarized.
  - **`docs-google-sre-prodcast-01-05-client-transparent-migrations.md`** (its
    Cross-References point to a non-AI "golden dataset" pattern as the SRE
    ancestor of agent eval, via dark-launch/Claim 11). S4E9's golden-label
    practice (Claim 8) is a concrete, named instantiation of that lineage —
    production incident labels as the eval set.
  - **`docs-google-sre-prodcast.md` S1E1 → Generic Mitigations** (the index
    lists Generic Mitigations in S1E1's further reading). S4E9 Claim 12 cites
    the *public Generic Mitigations publication* directly and shows why the
    taxonomy matters for agents — grounding that index reference in primary
    content.

- **Contradicts**: None material. The autonomy stance here (human verification
  required today; autonomous/self-recovering agents are an explicit *future*
  horizon, Claim 16) is fully consistent with the human-in-the-loop emphasis in
  Treynor (03-03), incident-response-tooling (03-06), PagerDuty, and incident.io
  notes. No contradiction issue is filed. (If anything, S4E9's "production has no
  sandbox" (Claim 7) *sharpens* rather than opposes the PagerDuty eval-pipeline
  claim — it explains *why* offline golden-data eval is mandatory.)

- **Novel**: First-person Google-practitioner account of *building* production
  AI agents for SRE (vs vendor blogs or theoretical discussion). New to the
  corpus:
  - The **pre-on-caller triage pattern** with the ruled-out-set presentation
    (Claim 5) — a concrete, deployable operational shape.
  - **Postmortem trajectory matching** as an evaluation method (Claim 10) — no
    other note describes comparing agent step-sequences to postmortem timelines.
  - **Golden *labels* from historical incidents** (rollback/upsize/quota/
    throttle) as the eval set, including the ~20–30-day retention decay caveat
    (Claim 8).
  - Named failure stories: **multi-timezone tool outputs** confusing the agent
    (Claim 11) and **terminology collisions** in the mitigations taxonomy
    ("escalate"→"delegate") (Claim 12).
  - The **"production has no sandbox"** framing distinguishing dev-side coding
    agents from prod-side action agents as the core evaluation difficulty
    (Claim 7).
  - The **autonomy-levels** outlook: current agents all require human
    verification; self-recovering agents are an open horizon (Claim 16).
  - The sober **"most AI effort is integration plumbing, not AI"** reality check
    (Claim 13).

## Guide Impact

- **Chapter 02 (SRE Fundamentals / AI in SRE)**: Add the agent-spectrum framing
  (Claim 1: static → LLM-augmented → full agent) and the read-vs-write
  capability split (Claim 2) as the conceptual backbone for any "should we agent
  this?" decision. Cite the "production has no sandbox" evaluation principle
  (Claim 7) and the golden-label methodology (Claim 8) as the concrete
  first-thing-to-build. Add the explicit limits (Claim 15): don't LLM what a
  regex/specialist model does better; don't insulate humans from learning.

- **Chapter 04 (Incident Management / On-call / Alerting)**: Add the
  **pre-on-caller triage pattern** (Claim 5) as the recommended first
  agent-shaped deployment — agent acts in the 3–4 min before the human, presents
  a ruled-out set + evidence, human owns the write. Corroborates Treynor's
  summarization claim (03-03 Claim 8) and extends it with operational detail.
  Add alert summarization as the low-risk on-ramp (Claim 4: wheat-from-chaff +
  needle-in-haystack). Add postmortem **trajectory matching** (Claim 10) to the
  evaluation section and to the postmortem-culture material: well-structured
  postmortems are now machine-readable eval/training data, so format matters.
  Add the Ironies-of-Automation caution (Claim 15) to the autonomy section so
  the guide warns against removing humans from the learning loop.

- **Chapter 05 (Automation & Toil)**: Add the **proactive / pre-incident** use
  cases (Claim 14): day-to-day companion for rollouts/regression/capacity, and
  the change-review gate that flags risky config before ship (admission-control
  example; SLO-dependency drift detection). Add the **"most effort is
  integration plumbing, not AI"** reality check (Claim 13) to set expected cost
  profiles. Add the Generic Mitigations taxonomy requirement (Claim 12) to the
  runbook/mitigation-language material, citing the public publication and the
  "escalate"→"delegate" terminology-collision lesson. Reference the autonomy-
  levels framing (Claim 16) to present current human-in-the-loop practice as the
  baseline and self-recovering agents as a cautious horizon.

## Extraction Notes

- The source is a single public transcript page on sre.google
  (https://sre.google/prodcast/transcripts/sre-prodcast-04-09/). Fetched via
  `curl` (95 KB HTML), scripts/styles stripped, and the dialogue reconstructed
  from `<strong>SPEAKER:</strong>` markers. All quotes marked direct were copied
  character-for-character from the recovered transcript, including speech
  disfluencies present in the source (e.g. "world modification erm, any ways" in
  Claim 3). Spot-check any quote against the live URL.
- Speakers verified: Ramón Medrano Llamas (Senior Staff SRE, Core SRE), Swapnil
  Haria (SWE, Core Labs), hosts Steve McGhee and Matt Siegler. The episode is
  S4E9, "The One With AI Agents," in Season 4 ("Friends and Trends").
- `date_published` is estimated at 2025 (Season 4; the exact episode air date is
  not published on the transcript page — only the series launch date 2022-03-31
  appears in related index metadata). The triage comment notes Season 4 episodes
  postdate Dec 2025, so 2025 is a safe lower bound; refine if an exact date is
  found.
- No part of the source was paywalled; the transcript is publicly accessible.
- This note is the deep, transcript-level mining the index note
  (`docs-google-sre-prodcast.md`) explicitly deferred for S4E9. It does not edit
  the guide; only the Smith touches `guide/`.
- No contradiction issue was filed: the human-in-the-loop / human-verification
  stance here is consistent with all adjacent notes (Treynor 03-03,
  incident-response-tooling 03-06, PagerDuty, incident.io).
