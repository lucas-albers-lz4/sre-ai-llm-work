---
source_url: https://www.cncf.io/blog/2026/07/13/operating-opentelemetry-at-scale-with-opamp
source_type: blog-post
title: "Operating OpenTelemetry at scale with OpAMP"
author: Dotan Horovits (CNCF Ambassador), recapping an interview with Andy Keller (OpAMP maintainer; Principal Engineer, BindPlane)
date_published: 2026-07-13
date_extracted: 2026-10-09
last_checked: 2026-10-09
status: current
confidence_overall: emerging
issue: "#1571"
---

# Operating OpenTelemetry at scale with OpAMP

> A CNCF Ambassador's recap of an OpenObservability Talks episode with an OpAMP
> maintainer: OpAMP is a standardized, agent-agnostic control protocol under
> OpenTelemetry for remotely configuring, updating, and health-monitoring large
> fleets of telemetry agents — with the two durable transferable patterns being
> the supervisor's restart-with-revert-to-last-known-good config rollout and a
> gateway fan-in multiplexer that bounds control-plane connection overhead for
> network-segmented fleets.

## Source Context

- **Type**: blog-post (CNCF Ambassador Post — a written recap of a podcast
  interview, not a deep-read engineering post). No YAML, no config files, no
  protocol schema, no benchmarks, and no failure report are included. The only
  concrete artifacts are architectural descriptions and quoted scale anecdotes.
- **Author credibility**: Dotan Horovits is a CNCF Ambassador and host of
  *OpenObservability Talks*; he is the interviewer and recap author, not the
  protocol author. The technical claims are attributed to Andy Keller, an OpAMP
  maintainer and Principal Engineer at BindPlane (a commercial telemetry-pipeline
  vendor). The protocol itself is an OpenTelemetry project; the vendor-neutral
  parts are the upstream spec (`opamp-spec`) and the Go reference
  implementation (`opamp-go`), which this note prefers as the authoritative
  reference where the post leans on vendor framing.
- **Scope**: Covers OpAMP's purpose and design (two Protobuf message types,
  read-only extension vs read/write supervisor), the diversity and scale of
  collector deployments, the supervisor's restart-with-rollback semantics, the
  generic name-value config payload that makes the protocol agent-agnostic
  (Kubernetes via the OpAMP Bridge, SDKs, Fluent Bit), the SDK hot-reload
  requirement, the new OpAMP Gateway Extension (fan-in multiplexer, Alpha),
  and the roadmap (config diff support, hot-reloading, a telemetry-policy
  OTEP), plus the "observability for your observability" principle. Does NOT
  cover: any LLM/AI operation, code, config schema, metrics, or incident
  postmortems. It is adjacent cloud-native telemetry-infrastructure material,
  not core AI-ops material. Mild vendor flavor: several architectural claims are
  secondhand from a BindPlane engineer and the post links BindPlane's own
  gateway-launch blog.

## Extracted Claims

### Claim 1: OpAMP is a standardized protocol under the OpenTelemetry project that gives a central backend remote configure/update/health/status control over observability agents
- **Evidence**: The post defines OpAMP as a network protocol specification sitting under OpenTelemetry (which is why it lives there), with the spec in the `opamp-spec` repository and a Go reference implementation in `opamp-go`. The linked architecture diagram is attributed to `opentelemetry.io`. This is the vendor-neutral core of the source.
- **Confidence**: settled (the protocol's existence, ownership, and purpose are independently verifiable; the CNCF post is a recap)
- **Quote**: "This is where **Open Agent Management Protocol (OpAMP)** comes into the picture: it provides a standardized protocol that lets a central backend automatically configure agents, push updates, monitor their health, and collect status information."
- **Our assessment**: This is a factual, checkable framing. OpAMP is a control-plane protocol for the telemetry data plane, analogous to (but distinct from) how a Kubernetes control plane reconciles a fleet of kubelets. For the guide, the transferable idea is "a standard protocol for remotely managing a fleet of observability/telemetry agents" — relevant to any org running many Collector or agent instances. It is not itself an LLM-ops claim.

### Claim 2: Before OpAMP, telemetry fleet management was fragmented — organizations built multiple in-house agent-management protocols, each with different transports
- **Evidence**: Andy's first-person account of BindPlane's pre-OpAMP history, quoted in the post. Anecdotal (one vendor's experience) but concrete about the fragmentation problem OpAMP addresses.
- **Confidence**: anecdotal
- **Quote**: "We probably developed in-house three, four, maybe five different agent management protocols. Some were HTTP-based, long polling. We used WebSockets. We used protobufs. We used JSON."
- **Our assessment**: A plausible and recognizable motivation — every platform team that manages agents ends up reinventing a config-push/watch protocol. The claim is one vendor's war story, not a measurement, so confidence is anecdotal. It supports OpAMP's value proposition without proving it; the existence of a standard does not guarantee adoption or correctness.

### Claim 3: Collector deployments span an enormous range — from a few massive gateways to embedded devices (point-of-sale machines, laptops) — and, in the IoT/embedded case, scale reaches millions of collectors that must be reasoned about
- **Evidence**: Andy's examples of deployment diversity, plus the post's explicit range "dozens to millions." These are illustrative figures from the interview, not measured census data.
- **Confidence**: anecdotal
- **Quote**: "but then we also even see people deploying collectors to embedded devices. We have collectors in point of sale machines. We have collectors on laptops collecting Windows events for security tracking."
- **Our assessment**: The *direction* (huge cardinality of cheap agents at the edge) is credible and is the real reason a control protocol is needed, but "millions" is an unmeasured upper bound from a vendor interview. Do not present the number as a finding. The transferable point is that a fleet-control design must handle both a handful of high-throughput gateways and very many low-resource edge agents.

### Claim 4: The OpAMP supervisor implements a restart-with-rollback config rollout — it writes the new config to disk, restarts the collector, and reverts to the last-known-good config if the new one fails to start
- **Evidence**: The post's description of the supervisor's approach, plus a direct quote from Andy stating the revert behavior explicitly as the "not breaking your telemetry pipelines remotely" safeguard. The post links the supervisor specification in `opentelemetry-collector-contrib`. No config examples or failure cases are shown.
- **Confidence**: emerging
- **Quote**: "If it doesn't start, it will revert the config and run with the last known good config so that we're not breaking your telemetry pipelines remotely."
- **Our assessment**: This is the single most transferable pattern in the source and the one the triage flagged as durable: a remote config push that is *self-validating by attempt* — apply, restart, and auto-revert if the process cannot come up. It is a concrete instance of the SRE doctrine that a safe config change needs automatic rollback, not just a manual rollback button (see Cross-References → `docs-google-sre-configuration-design.md` Claim 13). The caveat is that "fails to start" is only one class of bad config: a config that starts but silently degrades telemetry would not trip this revert. Confidence is emerging because the source describes the mechanism conceptually with no failure cases or validation logic shown.

### Claim 5: The protocol is deliberately minimal — two Protobuf message types (server-to-agent and agent-to-server) — with a read-only extension and a read/write supervisor as the two agent-side components
- **Evidence**: The post states the "just two messages" design and distinguishes the **OpAMP extension** (read-only: reports current configuration and health) from the **OpAMP supervisor** (a separate process alongside the collector implementing read and write). Andy's quote describes the supervisor's intermediary role.
- **Confidence**: emerging (the shape is verifiable against the spec; the post is a summarizer)
- **Quote**: "It kind of sits between the management platform and the collector. It speaks to the collector on behalf of the management platform, and it can accept changes."
- **Our assessment**: The read-only-extension vs read/write-supervisor split is a clean least-privilege design: monitoring-only agents need no write path, so the capability that can break telemetry is an opt-in component. That is directly analogous to the guide's recurring "read-only enrichment agent vs actuating agent" distinction in the AI-in-SRE material. The "two messages" minimalism is an architectural claim worth citing; verify against the spec before treating as settled.

### Claim 6: The config payload is intentionally a generic map of name-value pairs, making the protocol agent-agnostic — the same control plane can manage Collector, Kubernetes, SDKs, and non-OTel agents
- **Evidence**: The post states the payload is intentionally generic and that OpAMP is already used to manage SDKs and Kubernetes deployments, plus Fluent Bit. The Kubernetes path goes through the **OpAMP Bridge** → OpenTelemetry Operator → CRDs → Collectors (Andy's quote). The protocol "defines the communication contract, but doesn't dictate what agents do with the configuration."
- **Confidence**: emerging
- **Quote**: "The remote config message is just a map of name-value pairs, where that value can be anything."
- **Our assessment**: This is the key generalization claim: by making the payload opaque name-value data rather than Collector-specific, OpAMP becomes a general remote-agent-config transport. That is the property most relevant to AI-ops — it means the same pattern could carry config for guardrail processes, routers, or agent sidecars. The trade-off the source does not discuss is validation: a generic payload cannot be semantically validated by the control plane, which pushes config correctness onto the agent (contrast the guide's emphasis on semantic config validation).

### Claim 7: The Kubernetes integration uses an OpAMP Bridge as an intermediary that talks to the OpenTelemetry Operator, which reads CRDs and deploys Collectors
- **Evidence**: Andy's quoted architecture description. This is the concrete mechanism by which a non-Kubernetes-native control platform manages Kubernetes-native workloads without teaching the platform Kubernetes.
- **Confidence**: emerging
- **Quote**: "rather than communicating with [OTel] Collectors, you're communicating with this OpAMP Bridge. The OpAMP Bridge is communicating within the cluster with the OpenTelemetry Operator, and that Operator reads CRDs and deploys Collectors."
- **Our assessment**: A standard adapter pattern: translate the external control protocol into the platform-native declarative mechanism (CRDs), and let the platform's existing reconciler do the actual work. This is a good pattern for the guide's "declarative control plane" discussion — it avoids reimplementing Kubernetes rollout semantics in the management backend.

### Claim 8: Remote SDK reconfiguration requires hot-reloading, because applications cannot be shut down and restarted the way collectors can
- **Evidence**: The post contrasts the SDK path with the collector path: the Java SDK can speak OpAMP and receive remote config, but the operational model differs. Stated as a design constraint, not demonstrated.
- **Confidence**: emerging
- **Quote**: "Reconfiguring SDKs, however, requires a different operational model, as we can't shut down applications to reconfigure the SDK. SDKs require hot-reloading capabilities rather than the restart-based approach used for collectors."
- **Our assessment**: A sharp and durable distinction that generalizes directly to agent fleets: for restartable sidecar/collector processes, restart-with-rollback is a viable config-apply model; for in-process instrumentation or library code inside a long-lived service, config must hot-reload with no restart. The guide should carry this as a conditioning variable when prescribing "push config and restart" patterns for AI/agent components.

### Claim 9: The OpAMP Gateway Extension is a Collector extension that multiplexes OpAMP traffic, fanning in ~100k edge collectors through ~100 gateways (≈1k each) to bound WebSocket connection overhead on the management platform and support network-segmented fleets
- **Evidence**: Andy's worked example ("100,000 collectors ... 100 OpAMP gateways ... 1,000 collectors connect to each one"). The post describes the gateway as an OTel Collector extension acting as a multiplexer, analogous to OTel data gateways but for the control plane, and notes specific benefits (reduced connection overhead, support for network-segmented environments, more efficient network use). The gateway's launch blog is at bindplane.com.
- **Confidence**: anecdotal (the 100k/100/1k figure is an illustrative interview example, not a measured result)
- **Quote**: "Let's say I've got 100,000 collectors deployed across my many different clusters in my organization, instead of all the 100,000 [collectors] connecting to the management platform, I can deploy 100 OpAMP gateways, have 1,000 collectors connect to each one, and then those 100 connect to the management platform."
- **Our assessment**: The *topology* — hierarchical fan-in so leaf agents never connect directly to the control backend — is a standard and sound scaling pattern (the same shape as OTel data gateways and hierarchical service meshes). It directly serves network-segmented environments where edge agents cannot reach the management system. The specific arithmetic is deliberately illustrative and must not be presented as a benchmark. Vendor adjacency is strongest here: the feature is an Alpha launch by BindPlane.

### Claim 10: OpAMP is in beta with mixed component maturity; the roadmap prioritizes config-diff support, true hot-reloading, and a telemetry-policy OTEP that separates intent from configuration
- **Evidence**: The post's roadmap section states beta status and the active priorities. The telemetry-policy OTEP is described as a draft that would introduce policy as distinct from configuration.
- **Confidence**: emerging (roadmap items are directional; status is a point-in-time claim)
- **Quote**: "This would introduce policy as a concept distinct from configuration — communicating intent (like "filter out these log messages" or "add this attribute") rather than specific implementation details."
- **Our assessment**: The intent-vs-configuration distinction is the most conceptually interesting roadmap item: it would let the control plane express *what* should happen and let each agent implement it per its capabilities. This mirrors the guide's declarative-config theme (intended state vs imperative detail) and the agent-control-plane discussion. It is a draft OTEP, so it is emerging at best, and the guide should not depend on it.

### Claim 11: The guiding principle is "observability for your observability" — the telemetry pipeline itself must be monitored because it is too critical to be a black box
- **Evidence**: Andy frames OpAMP's evolution as "moving into this observability for your observability realm," and the post states the principle directly and lists what OpAMP provides (real-time visibility into collector health, configuration drift, and operational status).
- **Confidence**: emerging (a principle/position, well-argued but not evidenced)
- **Quote**: "you need to know is your observability actually working?"
- **Our assessment**: The principle is sound and generalizes to any telemetry/control plane: monitoring that silently stops reporting looks identical to "everything is fine." For the guide's LLM-ops content this is a citable framing — the telemetry that tells you your agents/models are healthy must itself have a health signal. The source asserts the principle but offers no concrete health-signal design (e.g., which metrics detect a silent collector), so it is a framing to adopt, not a procedure to follow.

## Concrete Artifacts

No code, config, schema, or metrics were present in the source. The artifacts below
are the architectural descriptions the post provides, restated faithfully and
attributed.

### Artifact 1: Supervisor-based rollout semantics (as described in the post)

```
"it writes new configurations to disk, shuts down the collector, and restarts
 it with the new configuration. Critically, it includes safety mechanisms:
 'If it doesn't start, it will revert the config and run with the last known
 good config so that we're not breaking your telemetry pipelines remotely.'"
— post prose + direct quote from Andy Keller
```

### Artifact 2: Gateway fan-in topology (illustrative arithmetic, not a benchmark)

```
Edge collectors            OpAMP gateways            Management platform
  ~100,000       ──────►   ~100 (≈1,000 each)  ──────►  OpAMP Server
                              multiplexer                (single backend)
Purpose (per post):
  - reduced connection overhead on the OpAMP Server
  - support for network-segmented environments where edge collectors
    can't directly reach external management systems
  - more efficient use of network resources
Status: OpAMP Gateway Extension launched in Alpha (BindPlane vendor blog).
```

### Artifact 3: Component inventory (as described in the post)

```
OpAMP Extension   — read-only component: reports current config + health status.
OpAMP Supervisor  — separate process alongside the collector; read + write;
                    applies new config with restart-and-revert-to-last-good.
OpAMP Bridge      — intermediary to Kubernetes: talks to the OTel Operator,
                    which reads CRDs and deploys Collectors.
OpAMP Gateway     — Collector extension acting as an OpAMP multiplexer (Alpha).
Protocol          — 2 Protobuf messages: server-to-agent, agent-to-server;
                    spec in opamp-spec; reference impl in opamp-go.
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-google-sre-configuration-design.md` — **Claim 13** states
    the three properties a safe configuration change must have, the third being
    **"Automatic rollback (or at a minimum, the ability to stop progress) if the
    change leads to loss of operator control."** The OpAMP supervisor
    (Claim 4 here) is a concrete, deployed instance of exactly that third
    property applied to a remote agent fleet: the collector restarts into the
    new config and the supervisor auto-reverts to last-known-good if it does
    not start, so a bad remote push cannot take down telemetry. This is the
    strongest cross-corpus link for the source and was not on the candidate
    list; it was found by searching the corpus for config-rollback doctrine.
  - `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
    **Claim 4** describes the declarative alternative where "different
    components ... produce the specific part of the intent that they are
    responsible for" and "the same system ... takes care of rolling out the
    intended state across the fleet, following policies." OpAMP is a
    telemetry-domain instance: a central backend holds the intended agent
    configuration and reconciles it across the fleet. **Claim 5** (bounded
    blast radius via decomposition) is reinforced by the Gateway fan-in
    topology (Claim 9 here), which bounds the control-plane failure domain.

- **Contradicts**: None that meets the MINER.md §4a bar. One **tension** is
  recorded rather than filed: `source-notes/docs-google-sre-ai-engineering-reliable-operations.md`
  **Claim 14** ("Intervening Pull Request Problem") argues that "A simple binary
  rollback to 'last known good' becomes risky when dozens of changes have been
  submitted in rapid succession" because rollback may discard critical fixes and
  security patches. This source presents last-known-good revert as an unqualified
  safety win. These operate in different contexts — OpAMP's revert is a
  *configuration* rollback for restartable telemetry agents at human-paced config
  velocity, while the Google claim concerns *code* rollback under machine-velocity
  AI-generated changes — so it is a conditioning variable, not an opposition. The
  guide should present last-known-good revert as safe for bounded config state
  and flag the high-velocity caveat separately.

- **Extends**:
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` —
    Complement, not overlap (the triage reached the same conclusion). Honeycomb
    covers *instrumenting agent internals* with OTel GenAI semantic conventions
    (LLM/tool spans, `gen_ai.conversation.id` propagation, Agent Timeline). This
    source covers the *fleet control layer* below that: how you remotely
    configure and health-manage the collector/agent processes that carry those
    spans. The two together describe the instrumentation (app layer) and the
    managed data plane (agent/collector layer) of an OTel-based AI-ops stack.

- **Novel**:
  - **OpAMP itself** — no existing note in the corpus covers OpAMP, collector
    fleet management, or a standardized remote-agent-config protocol. Searches
    for "opamp", "collector fleet", and "last known good" across `source-notes/`
    return no prior note describing this protocol.
  - The **generic name-value config payload as an agent-agnostic control
    transport** (Claim 6), including the Kubernetes Bridge → Operator → CRD path
    (Claim 7) and the SDK hot-reload constraint (Claim 8).
  - The **control-plane fan-in topology** (Claim 9) as a concrete technique for
    bounding management-backend connection overhead in network-segmented fleets.
  - The **"observability for your observability"** framing (Claim 11) as applied
    to a telemetry fleet.

## Guide Impact

- **Chapter 02 (Observability)**: Add a short "observability for the telemetry
  pipeline itself" subsection. The citable content is the principle (Claim 11)
  plus the concrete mechanism this source documents: a control plane that reports
  collector health, configuration drift, and operational status (Claim 1), and a
  fan-in gateway topology for fleets too large or too segmented to reach the
  management backend directly (Claim 9). Note that OpAMP is adjacent
  telemetry-infrastructure, not an LLM-specific tool — frame it as the
  data-plane-layer analog to the app-layer agent instrumentation already cited
  from `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`.

- **Chapter 03 (Runbooks and Agents / emerging agent control plane)**: This is
  the best fit for the source's transferable pattern. Use the supervisor's
  restart-with-revert-to-last-known-good rollout (Claim 4) as a worked
  prior-art example of a declarative agent control plane with automatic
  rollback, alongside `docs-google-sre-configuration-design.md` Claim 13 (the
  three-property safe-config-change test) and
  `docs-google-sre-prodcast-03-13-imperative-declarative.md` Claim 4 (components
  contribute to one intended state that the system rolls out). Pair Claim 8 (SDK
  hot-reload vs collector restart) as the conditioning variable: whether
  restart-with-rollback is acceptable depends on whether the managed component
  can be restarted.

- **Chapter 05 (LLM Ops Reliability)**: The roadmap's intent-vs-configuration
  distinction (Claim 10) is a conceptual extension of the guide's declarative
  configuration theme and is worth a forward-looking mention, but it is a draft
  OTEP and should be labeled as such, not presented as available. Do **not**
  over-extract: the source has no AI/LLM content and no operational metrics, so
  its contribution to AI-ops chapters is analogical only.

## Extraction Notes

- **Source was read in full** via WebFetch (the CNCF post is a single page). The
  post is a podcast recap and, as the triage predicted, contains no YAML, config,
  schema, metrics, or failure report. The note is deliberately right-sized: it
  extracts the architectural patterns the triage identified (supervisor
  rollback, generic name-value payload, gateway fan-in) and resists over-claiming
  the scale figures.
- **Candidate list disposition** (`miner-related-notes.md`, read first): the 10
  candidates were each considered and either cited or dismissed. Cited from
  outside the candidate list: `docs-google-sre-configuration-design.md`
  (Claim 13, automatic rollback) and
  `docs-google-sre-ai-engineering-reliable-operations.md` (Claim 14, the
  last-known-good tension); both were found by targeted corpus search. From the
  candidate list: `docs-google-sre-prodcast-03-13-imperative-declarative.md`
  (cited, Extends). Explicitly dismissed as not materially overlapping:
  `docs-google-sre-prodcast-03-07-retail-gaming.md`,
  `docs-google-sre-eliminating-toil.md`,
  `docs-google-sre-reliable-product-launches.md`,
  `docs-google-sre-prodcast-03-01.md`,
  `docs-google-sre-prodcast-03-11-embracing-complexity.md`,
  `docs-google-sre-on-call.md`,
  `docs-google-sre-slo-engineering-case-studies.md`,
  `docs-litellm-anthropic-advisor-tool.md`, and
  `docs-litellm-completion-function-call.md` — the candidate scorer surfaced
  them on generic SRE/observability vocabulary, but none addresses fleet control,
  remote config management, rollback mechanics, or telemetry-agent scaling, so
  no honest corroboration/contradiction exists with them.
- **Confidence**: `confidence_overall: emerging`. The protocol's existence and
  ownership are settled, but the author is a recap interviewer rather than a
  protocol author, the substantive quotes come from a vendor-employed maintainer,
  the scale figures are illustrative, and there are no config artifacts or
  measurements. Individual protocol-shape claims (Claims 1, 5) are stated at
  higher confidence than the architectural/scale claims.
- **Quotes**: All `Quote` fields are copied character-for-character from the
  fetched page. Where the source prose inserted an attribution inside a quote
  (the embedded-devices quote in Claim 3), only the contiguous speaker fragment
  was quoted. The Claim 9 quote retains the source's own bracketed `[collectors]`
  editorial insertion and the Claim 7 quote retains the source's `[OTel]`
  insertion exactly as they appear.
- **No contradiction issue was filed.** Per MINER.md §4a, the
  last-known-good rollback tension with
  `docs-google-sre-ai-engineering-reliable-operations.md` Claim 14 is a
  context/conditioning difference (config rollback of restartable agents vs code
  rollback at machine velocity), not an opposition that would force different
  guide advice. Existing open `contradiction`-labeled issues were checked; none
  concerns OpAMP or this source.
- **Vendor-adjacency caveat**: BindPlane (the interviewed maintainer's employer)
  launched the OpAMP Gateway Extension in Alpha and the post links BindPlane's
  launch blog. The gateway topology and the "millions of collectors" framing
  should be attributed as vendor-adjacent, and the upstream `opamp-spec` /
  `opamp-go` preferred as the primary reference for protocol facts.
