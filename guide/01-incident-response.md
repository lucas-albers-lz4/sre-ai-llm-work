# Incident Response

> How Google's IRT (Tech Incident Response Team) operates — from threshold-based
> activation through incident-command psychological safety to the cascading
> failure mitigation hierarchy. AI/LLMs enter as pre-on-caller triage assistants
> and anomaly-detection amplifiers, not as autonomous responders. For
> AI-specific incidents, the chapter covers the read-only AI Alert enrichment
> agent, the PagerDuty SRE Agent triage loop, measured MTTM reductions from
> AI-assisted investigation, and the rules for what an incident-response agent
> must never do.

## The IRT escalation model

### Threshold-based activation

Google's Tech IRT is a specialized escalation team that activates when "too many
incidents are opened in too short a period of time" — a threshold-based trigger
that distinguishes it from standard per-service on-call pages
[source: docs-google-sre-prodcast-06-09-irt-incident-response, Claim 1] [emerging].

This is not the same as escalating a single incident to a senior on-caller. IRT
activates when incident *volume* exceeds a threshold, signaling that something
systemic may be wrong. The trigger acknowledges that individual incidents may be
unrelated but their correlation in time is itself a signal.

**Rule**: Define a threshold-based trigger for your highest escalation tier —
not "escalate when this incident is hard," but "activate when N incidents fire
in M minutes." The volume is the signal.

### Assembly within ~10 minutes

When IRT activates, the response sequence is
[source: docs-google-sre-prodcast-06-09-irt-incident-response, Claim 2] [emerging]:

1. Find the on-call engineers already paged (they've already opened incidents)
2. Pull everyone into a video conference — the highest-bandwidth coordination channel
3. Assess: "do we understand what is wrong and who are the right people to be
   working on this and let's get them here right now, at any cost"
4. Target: within about 10 minutes

> This results in seeing what's broken, finding the on calls that have already
> been paged because they've already opened incidents, assuming that that's the
> case, and dragging everyone together, usually into a video conference, because
> I found that's the highest bandwidth way of getting people on the same page
> and making sure that you aren't duplicating roles and you've got the right
> people in the room.

**Rule**: Your incident response escalation target should be ~10 minutes from
threshold breach to assembled team. Video conference, not chat — the bandwidth
matters for coordination under uncertainty.

### Adaptive capacity: borrow expertise, don't just escalate

IRT provides what reliability engineering literature calls "adaptive capacity" —
the ability for a team to borrow capability, knowledge, or "connective tissue"
from another team during an incident. The intervention that repeatedly resolves
paralysis is simply "hey, how about I just take over for you"
[source: docs-google-sre-prodcast-06-09-irt-incident-response, Claim 7] [settled].

This is distinct from hierarchical escalation (pushing the problem up the chain).
It's horizontal borrowing — IRT brings expertise and coordination bandwidth,
not just authority.

**Rule**: Build an escalation tier whose job is adaptive capacity (bringing
expertise and coordination), not just decision authority. The person who says
"let me take over for you" unblocks more incidents than the person who says
"tell me what's happening."

## Psychological safety in incidents

### Deference to the incident commander

> Everyone needs to be aware of who is actually in control of the incident and
> defer to them. So there's, regardless of position in a company, regardless of
> level, managerial relationships or the like, someone is in charge and they
> should be listened to and it should be treated as a temporary leadership
> position.
> [source: docs-google-sre-prodcast-06-09-irt-incident-response, Claim 3] [settled]

The IC role only works if the organization actually defers to it across
org-chart boundaries. The "temporary leadership position" framing is critical:
it's not a permanent transfer of authority, it's a time-bounded role that ends
with the incident.

**Rule**: The incident commander's authority must cross org-chart boundaries for
the duration of the incident. If a director's report can overrule the IC because
of level, the IC role is performative.

### The "would you like to take over as IC?" diffusal

> If someone is encroaching, maybe, a simple phrase is would you like to take
> over as IC? — I have literally done that.
> [source: docs-google-sre-prodcast-06-09-irt-incident-response, Claim 4] [emerging]

This is a deliberate diffusal technique that stops encroachment without
escalation or conflict. It reframes the encroacher's intervention as a
willingness to own the incident — which they almost always decline.

**Rule**: Train incident commanders in the "would you like to take over as IC?"
diffusal. It's a low-cost, high-impact technique for protecting IC authority
without creating conflict.

### Vapor lock: responsibility without knowledge

> There's a level of feeling of responsibility for something but not knowing
> what to do that can make people vapor lock or deadlock, almost, in responding
> to things.
> [source: docs-google-sre-prodcast-06-09-irt-incident-response, Claim 5] [emerging]

"Vapor lock" is a named failure mode: responsibility + no clear action →
paralysis. IRT's remedy is the repeated presence: "we're here to help."

**Rule**: If an incident responder vapor-locks, the intervention is not more
information — it's removing the isolation. "We're here to help" breaks the
paralysis loop more effectively than "here's what you should do."

### Better to apologize for a page

> The attitude is if we're paged for a completely specious thing, the attitude
> is please don't page us for that next time, but feel free to page us with new
> problems, because don't let the problem sit and simmer if you don't know what
> to do. — it's better to apologize for a page than to apologize for not a page.
> [source: docs-google-sre-prodcast-06-09-irt-incident-response, Claim 6] [settled]

This is the cultural norm that enables the IRT escalation model. The framing is
nuanced: corrective feedback for repeated false alarms (don't page us for
*that* again), but encouragement to page with novel problems (don't let it sit
and simmer).

**Rule**: Adopt "better to apologize for a page than for not a page" as an
explicit escalation norm. Correct false-alarm patterns, but never punish an
escalation that turned out to be a non-incident — the next one might not be.

## Cascading failure mitigation

### The triggering conditions checklist

When a cascading failure is suspected, check these six triggering categories
before anything else
[source: docs-google-sre-address-cascading-failures, Claim 12] [settled]:

1. **Process death** — Query of Death, assertion failures, OOM kills
2. **Process updates** — new binaries or configs pushed simultaneously
3. **New rollouts** — altered request profiles or resource usage
4. **Organic growth** — gradual capacity exceedance
5. **Planned changes** — drains, turndowns, traffic shifts
6. **Request profile changes** — payload cost changes, data growth

> During a cascading failure, it's usually wise to check for recent changes and
> consider reverting them.

**Rule**: Before diagnosing any cascading failure, check for recent changes
across all six categories. The most common trigger is a change the responder
doesn't know about yet.

### The immediate mitigation hierarchy

When a service is in an active cascading failure, apply these mitigations in
order
[source: docs-google-sre-address-cascading-failures, Claim 14] [settled]:

1. **Increase resources** — buy headroom if possible
2. **Stop health check failures/deaths** — disable service health checks
   temporarily to stop the crash loop
3. **Restart servers** — clear accumulated state
4. **Drop traffic** — aggressively, e.g., to 1% of normal
5. **Enter degraded modes** — serve errors or partial results
6. **Eliminate batch/bad traffic** — stop non-critical work

> Once a service passes its breaking point, it is better to allow some
> user-visible errors or lower-quality results to slip through than try to
> fully serve every request.

The hysteresis pattern is critical: if 10% of servers are healthy, load must
drop to ~1,000 QPS (not ~10,000) to stabilize — roughly a 10:1 reduction
[source: docs-google-sre-address-cascading-failures, Claim 3] [settled].

```
1. Address the triggering condition (revert recent changes)
2. Reduce load aggressively (e.g., to 1% of traffic)
3. Let servers become healthy and warm caches
4. Gradually ramp up load, monitoring for re-entry into overload
```
*Recovery procedure from [source: docs-google-sre-address-cascading-failures, Concrete Artifacts].*

**Rule**: During a cascading failure, drop traffic to ~1% before investigating
root cause. The mild-reduction instinct (shed 10-20%) fails because of
hysteresis — the system needs to drop far below the breaking point to recover.
Diagnose once stable, not while burning.

## Overload as an incident trigger

### The fast-error feedback loop

The most common overload-to-cascade pattern: a server returns fast errors under
load → the latency-based load balancer sees those servers as "efficient" →
routes MORE traffic to the already-overloaded server → cascade.

In one Google case study, the perceived per-request CPU in the affected region
was 10× lower than actual because errors were counted as cheap requests. The fix:
count each error as 120% CPU utilization
[source: docs-google-sre-handling-overload, Claim 1] [settled].

**Rule**: When implementing load shedding, ensure the load balancer and
load-shedding system communicate. A server returning fast errors must not
appear healthier than one processing real traffic.

### The retry storm: 20× spike from synchronized clients

During the Pokémon GO launch, client retry logic without jitter or exponential
backoff produced "thundering herd" spikes reaching 20× the previous global RPS
peak. The fix: truncated exponential backoff with jitter
[source: docs-google-sre-handling-overload, Claim 3] [settled].

The mathematics of multi-layer retry amplification: a 3-layer system with 4
attempts per layer produces 4³ = 64 attempts at the lowest layer per single
user action — a product, not a sum
[source: docs-google-sre-address-cascading-failures, Claim 4] [settled].

**Rule**: Every client that retries must use randomized exponential backoff with
jitter. For LLM API callers (SDKs, agent frameworks), audit retry logic before
launch — a retry without jitter is a cascade-in-waiting.

### Load shedding as the safety net

When overload is unavoidable, load shedding trades some user-visible errors for
system survival. Prefer optimistic throttling (don't shed until global capacity
is reached, then work from lowest priority upward) for most systems
[source: docs-google-sre-handling-overload, Claim 11] [settled].

> In many cases, if the system is only throttling non-interactive retryable
> requests, then your system is probably working as intended.

The load shedding code path that works today may break silently — test it
regularly. "The code path you never use is the code path that (often) doesn't
work" [source: docs-google-sre-address-cascading-failures, Claim 11] [settled].

**Rule**: Exercise your load-shedding code paths in staging regularly. The
shedding path that works at deployment will not necessarily work six months
later if untested. If throttling is only hitting batch/background traffic,
that's design working as intended — don't overreact.

## AI in incident response

### Agents for triage, not command

AI agents are "pretty good at triaging bugs — the summarizing, triaging and
routing of things." Anomaly detection and correlation capabilities are improving:
systems now surface relevant dashboards and information without human prompting,
where previously "if a human had not suggested all of the relevant dashboards,
all of the relevant information, there was no added information when something
went wrong" [source: docs-google-sre-prodcast-06-09-irt-incident-response,
Claim 8] [emerging].

This aligns with the pre-on-caller triage pattern documented in Chapter 3:
agents compress time-to-clue in the ~3-4 minutes before the human arrives. The
agent reads, summarizes, and recommends; the human decides and acts
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 5] [settled].

**Rule**: Deploy AI as a triage amplifier during incidents — surface relevant
dashboards, correlate anomalies, and summarize the situation. Do not delegate
incident command to an AI. The "summarize, triage, route" pattern is the
highest-confidence AI use case in incident response today.

### The AI Alert pattern: read-only, time-bounded, evidence-based

Google's AI Alert system intercepts alerts before they reach a human, operating
within a tight 2-minute budget using massive parallelism to query monitoring
systems, logging platforms, production change logs, and dependency graphs.
Findings are linked back to source data and appended to the original alert
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 9] [settled].

> AI Alert focuses on providing verifiable facts and evidence-based insights
> rather than speculative conclusions.

The design constraints matter: read-only mode, a 2-minute bound, and
verifiable facts only — not speculative root-cause guesses.

**Rule**: Start AI incident response at L1 (read-only enrichment). An
enrichment agent should have a hard time budget, produce evidence-linked
findings, and never mutate production state.

### AI incident triage loop

PagerDuty's SRE Agent implements a concrete AI-incident triage workflow
[source: blog-pagerduty-sre-agent-triage, Claim 2] [emerging]:

```
Monitor breach (eval threshold exceeded)
        │
        ▼
SRE Agent checks monitor status (resolved already?)
        │
        ▼
Pulls failing traces from AI observability (e.g., Arize)
        │
        ▼
Reviews eval explanations and summarizes trace patterns
        │
        ▼
Checks recent code changes (via GitHub connector)
        │
        ▼
Produces diagnosis + ranked next steps
        │
        ▼
Learnings feed back into the system
```
*Triage loop from [source: blog-pagerduty-sre-agent-triage, Concrete Artifacts].*

The triage loop connects to AI-specific data sources — observability traces,
not just logs and metrics — and produces a diagnosis with ranked actions
rather than raw data dumps
[source: blog-pagerduty-sre-agent-triage, Claim 4] [emerging].

**Rule**: Wire your triage agent to AI observability traces, not just
traditional monitoring. An LLM eval alert means "something might be wrong
according to the model" — not "something is broken" in the traditional sense.
The diagnostic path is different (prompt change, retrieval tweak, model swap)
from a traditional infrastructure incident (rollback, restart, scale)
[source: blog-pagerduty-sre-agent-triage, Claim 1] [emerging].

### Measured impact of AI-assisted investigation

Google's Incident Hypothesis system uses RAG to analyze real-time monitoring
anomalies, service playbooks, application logs, incident management data, and
patterns from similar past incidents. Analysis confirmed a measurable 10%
reduction in Mean Time to Mitigate (MTTM) — from informational assistance
alone, at L1 autonomy
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 10] [settled].

Google's Investigation Dashboards generate an incident-specific single pane
of glass on demand. ML-based anomaly detection increased overall findings by
195%, and the dashboards delivered a 44% MTTM reduction across supported
incidents
[source: docs-google-sre-ai-engineering-reliable-operations, Claim 11] [settled].

**Rule**: L1 AI assistance (recommendation only, no actuation) delivers
measurable value — the 10% and 44% MTTM reductions are the strongest published
evidence for AI-investigation ROI. Start here before advancing to higher
autonomy levels.

### Generic mitigations: fix symptoms first

Google's incident response doctrine: apply "generic mitigations" (roll back,
drain traffic, add capacity) as the first action on impact — fix symptoms,
not causes, to buy time for root-cause analysis
[source: docs-google-sre-anatomy-of-an-incident, Claim 5] [settled].

> A generic mitigation is an action that you can take to reduce the impact of
> a wide variety of outages while you're figuring out what needs to be fixed.
> Your first priority should always be to stop or lessen the user impact, not
> to figure out what's causing the issue.

**Rule**: Build a catalog of generic mitigations (rollback, drain, add-capacity)
that agents can recommend without understanding root cause. The first AI action
should be "which generic mitigation fits the symptoms?" — not "what caused this?"

### The human floor: 20–30 minutes

Once a human is involved in outage response, the outage will last at least
20 to 30 minutes. Automation and self-healing are the primary levers to reduce
this floor [source: docs-google-sre-anatomy-of-an-incident, Claim 4] [settled].

This is the strongest quantitative argument for AI-assisted incident response:
human involvement sets a minimum TTR of 20–30 minutes. Pre-on-caller triage,
AI Alert enrichment, and Investigation Dashboards all target compressing the
pre-human response phase and accelerating the human's time-to-clue once they
arrive.

**Rule**: Measure AI incident-response impact against the 20–30 minute human
floor. Any AI assistance that reduces time-to-clue below this threshold is
reducing the irreducible human component of TTR.

## What NOT to do during AI-assisted incidents

### Don't paste secrets or PII into a model

Incident responders under time pressure can paste logs, configs, and database
output into an LLM without sanitizing. Models are external services — data
shared with them leaves your tenant.
[editorial]

**Rule**: Gate the incident-response agent behind a data-sanitization layer.
The agent should receive structured alert context (service, SLO, recent
deploys, error budget status) — not raw log dumps that may contain secrets.
[editorial]

### Don't let the agent act without human approval

Google's production AI agents default-deny all world-mutating actions and
require explicit human permission before writes
[source: docs-google-sre-prodcast-04-09-ai-agents, Claim 3] [settled].

PagerDuty's AI incident response taxonomy captures this as three actions:
classify whether escalation is needed, run only pre-approved remediations,
and file follow-up tickets for the owning team — never invent a remediation
[source: blog-pagerduty-sre-agent-triage, Claim 6] [emerging].

**Rule**: An incident-response agent can classify, recommend, and ticket.
It should never execute a remediation that hasn't been pre-approved by a human.

### Don't treat AI eval alerts like infrastructure alerts

A drop in a relevance metric is not the same as a broken service. The fix
is typically a prompt change, retrieval tweak, model swap, or eval re-tune
— not a rollback or restart. However, the same low-relevance alert can also
be caused by an upstream service failure. The agent must distinguish between
these two root causes by checking traces against code and recent changes
[source: blog-pagerduty-sre-agent-triage, Claim 10] [emerging].

**Rule**: Separate AI-eval alerts from infrastructure alerts in your paging
taxonomy. An eval-driven alert should not necessarily wake a human at 2 a.m.
PagerDuty's planned approach is to automatically re-check noisy eval scores
on small samples before paging
[source: blog-pagerduty-sre-agent-triage, Claim 7] [anecdotal].

---
*Sources for this chapter: docs-google-sre-prodcast-06-09-irt-incident-response,
docs-google-sre-address-cascading-failures, docs-google-sre-handling-overload,
docs-google-sre-prodcast-04-09-ai-agents, docs-google-sre-ai-engineering-reliable-operations,
docs-google-sre-anatomy-of-an-incident, blog-pagerduty-sre-agent-triage*
*Last updated: 2026-08-11*
