---
source_url: https://www.cncf.io/blog/2026/07/27/federating-clusters-for-zero-downtime-kubernetes
source_type: blog-post
title: "Federating clusters for zero-downtime Kubernetes"
author: "Dominik Táskai (CNCF Ambassador and Linkerd Contributor)"
date_published: 2026-07-27
date_extracted: 2026-10-22
last_checked: 2026-10-22
status: current
confidence_overall: emerging
issue: "#1820"
---

# Federating clusters for zero-downtime Kubernetes

> A practitioner build-log that runs all three Linkerd multicluster modes (federated, flat mirror, gateway mirror) side by side on three GKE clusters, kills one cluster, and measures the difference: a federated service rebalanced 33/33/33 → 50/50 with zero errors and no config change, while the explicitly-named mirrored services returned 503/502 because the client had asked for a specific remote — "Mirroring hands you control; federation hands you automation." Its transferable payload for the guide is the mode-selection decision (a labelling choice, not an app change) and a catalogue of silent-failure gotchas (VPC peering without route exchange, overlapping pod CIDRs, a missing service-mirror controller that leaves `linkerd multicluster check` green).

## Source Context

- **Type**: blog-post (CNCF Project Maintainer Post — practitioner tutorial with a runnable companion repo, `github.com/dtaskai/linkerd-multicluster-demo`, and copy-pasteable scripts).
- **Author credibility**: Dominik Táskai, described on the page as "CNCF Ambassador and Linkerd Contributor" — i.e. vendor-adjacent to the project whose multicluster extension the post teaches. The evidence is concrete and reproducible (a public repo, an explicit address plan, endpoint dumps, before/after traffic splits), not marketing copy, but every number is author-run on a three-cluster, one-node-per-cluster demo (~$10–15/day) rather than a production fleet. The chaos-test results are a single demonstration, not a benchmark.
- **Scope**: Multi-region Kubernetes service exposure over Linkerd's multicluster extension: the three modes and how to choose between them, cross-cluster mTLS trust-anchor setup, network prerequisites, a full-cluster-loss chaos test, the per-service labelling that changes behaviour, and an operational-gotchas list. Does **NOT** cover: AI/LLM workloads, inference serving, GPU scheduling, model traffic, SLOs, or alerting design (the monitoring item is one line in a checklist). It also does not test cascade behaviour, retry amplification, or failover under load — the chaos test scales one cluster's deployments to zero and samples traffic.

## Extracted Claims

### Claim 1: The default multi-region failure mode is that identical copies of a service are not treated as one thing, so cluster loss degrades into a runbook (restore, repoint DNS) that was paid for in advance
- **Evidence**: Opening framing of the post, which is the problem statement the rest of the post answers with Linkerd's multicluster extension.
- **Confidence**: emerging
- **Quote**: "Every multi-region setup eventually meets the same awkward moment: a whole cluster goes away, and the identical copy of your service running two regions over might as well not exist, because nothing is wired to treat them as one thing. Failover becomes a runbook: restore, repoint DNS, and wait for an outage that, on paper, you'd already paid to survive."
- **Our assessment**: This is the guide-relevant shape of the problem: redundancy that is *geographic* but not *semantic*. The cost the author names is not the second cluster — it is the runbook (a manual, repeatable, incident-time action) that has to exist because the two deployments are only incidentally related. Useful framing for the guide's failover/runbook discussion, and it sets up the later claim that the fix is a labelling decision rather than an application change.

### Claim 2: Linkerd's multicluster extension offers three modes that are not mutually exclusive — the mode is chosen per service via a label on the same set of links
- **Evidence**: The post's mode table, plus the worked demo in which three services on one fully-meshed link topology use three different modes. The traffic-generator output shows the three patterns serving in the same mesh (`[federated]`, `[flat-west]`, `[flat-east]`, `[gateway]`).
- **Confidence**: settled (mechanism is a documented label; demonstrated with `kubectl label svc/...` and endpoint dumps)
- **Quote**: "Linkerd's multicluster extension supports three modes. The nice thing is they're not mutually exclusive: on the same set of linked clusters, the mode is chosen per service via a label."
- **Quote**: "Three modes, one mesh, one set of clusters, and the only difference between them is a label."
- **Our assessment**: The load-bearing operational point. It moves multi-region topology from an architectural commitment (build a mesh, pick a pattern) to a per-service attribute that can be changed later — and it means a platform can run all three at once. For the guide this is the concrete answer to *how do you make failover a property of the platform rather than of the app*. Caveat: the label vocabulary is Linkerd-specific; the generalisable pattern is *cross-cluster traffic behaviour is per-service declarative metadata, not per-client code*.

### Claim 3: The network topology, not the application, decides which modes are available — hierarchical mirroring works on any network, flat and federated require real pod-to-pod connectivity
- **Evidence**: The mode table's "Network Requirement" column, the paragraph that follows it, and the demo topology (VPC-native GKE on peered VPCs gives the flat network; the `analytics` service is exported through a gateway precisely because it lives in a cluster without flat connectivity).
- **Confidence**: settled (constraint stated by the project and demonstrated by the mixed setup)
- **Quote**: "The distinction that matters operationally is that hierarchical mirroring works on any network. Only the gateway IP needs to be reachable, while flat and federated modes need real pod-to-pod connectivity."
- **Our assessment**: The precondition that has to be checked *before* choosing a mode, and the reason the post's networking gotchas (Claims 10–12) are failover-critical rather than cosmetic: without pod-to-pod routability, federation is simply not an option, and the platform is back to named remotes. The author also makes the mixing point explicitly — a flat network for the core workload plus a gateway for the specialised one — which is the realistic architecture rather than a single-mode story.

### Claim 4: A federated service becomes one load-balanced endpoint spanning every cluster, and it absorbs the loss of a whole cluster with no application change
- **Evidence**: The `frontend` deployment description plus the endpoint dump showing three clusters' pods inside a single service's endpoint set, and the chaos test in Claim 7.
- **Confidence**: settled (endpoints shown; behaviour measured in the chaos test)
- **Quote**: "A single federated frontend service in each cluster load-balances across all nine pods (3 replicas × 3 clusters). When a cluster goes down, the remaining six pods absorb the traffic with no application changes."
- **Our assessment**: Note what the mechanism is: not a redirect, not a DNS change, not a client-side list — the endpoint set of one Service in one cluster simply contains pods in the other clusters, and the mesh's own load balancer keeps spreading requests across whatever is left. That is why the failure required no action. The corollary the author draws at the end is the design rule: "federation is the right default for anything that should simply be available everywhere".

### Claim 5: Flat mirroring exposes a remote service under an explicit name (`<svc>-<cluster>`) with traffic going straight to the remote pods, so the client — not the platform — chooses the cluster
- **Evidence**: The `api` deployment description, the label applied (`mirror.linkerd.io/exported=remote-discovery`), and the `kubectl get svc` output in `north` showing `api-west` and `api-east` as two distinct Services alongside the local `frontend` and the federated `frontend-federated`.
- **Confidence**: settled
- **Quote**: "The client in `north` picks `api-west` or `api-east` explicitly. Traffic will go straight to the remote pods with no gateway in the path."
- **Our assessment**: The stated reason to reach for this mode is locality — the post names keeping a request in-region for data locality as the motivating case. That is a conditioning variable, not a best practice: the mode exists precisely when the client has a reason to care *which* cluster answers, and that reason has to survive the failure. It is the counterweight to federation, not a fallback.

### Claim 6: Gateway mirroring is the reachability escape hatch — the endpoint is the remote cluster's gateway IP, not the remote pods
- **Evidence**: The `analytics` deployment (east only, exported hierarchically), the `analytics-east-gw` Service appearing in `west` and `north`, the endpoint dump showing `35.186.xxx.xxx:4143`, and the source's own statement of the trade.
- **Confidence**: settled
- **Quote**: "The endpoints for this service point at east's gateway IP, not the analytics pods directly. That's the right trade when you can't guarantee flat-network connectivity, or when you specifically want the gateway handling load balancing and mTLS termination."
- **Our assessment**: Two things worth carrying to the guide: (a) gateway mode is the only mode whose network requirement is "Gateway IP reachable", which makes it the fallback when the flat network cannot be built; (b) the gateway is an *additional* failure domain — which the chaos test makes explicit (Claim 9). A gateway that is up while its cluster is down still yields 502s, because the gateway lives in the cluster that died.

### Claim 7: Chaos test result — with one of three clusters scaled to zero, the federated service rebalanced 33/33/33 → 50/50 with zero errors and no configuration change
- **Evidence**: `./scripts/06-chaos-test.sh` scales every deployment in `east` to zero replicas, then a traffic generator in `north` samples all three service patterns. The source prints the before/after split and the prose interpretation.
- **Confidence**: emerging (single author-run demo on three small clusters; no error-rate series, sample size, or duration is shown — "zero errors" is an observation from the script's own output, not a reported metric)
- **Quote**: "Before:  west=33% east=33% north=33%"
- **Quote**: "After:   west=50% north=50%              ← automatic rebalance, zero errors"
- **Quote**: "Traffic redistributes immediately. No errors, no config changes. As east's pods drop out of the endpoint list, Linkerd's load balancer simply spreads requests across what's left."
- **Our assessment**: The one measured result in the post that answers the guide's failover question, and the mechanism is worth naming precisely: *removal* from the endpoint list is automatic, not *addition* of a fallback target. The proportion went to 50/50 because the surviving pods are simply all that is left. Two caveats the guide should carry: the test scales a cluster's deployments to zero, which is not the same as losing the cluster's network, its control plane, or its region; and "zero errors" is the script's eyeball, not an error-rate SLO. Treat as a demonstrated mechanism, not a proven availability figure.

### Claim 8: The flat-mirrored service returned 503s after the cluster loss — described as correct behaviour, because the client had explicitly asked for a remote that is gone
- **Evidence**: The chaos-test output block for `api-east` plus the source's interpretation of who owns the recovery.
- **Confidence**: settled (protocol-level behaviour; the source's reasoning is a design stance, and its correctness depends on the client honouring the contract)
- **Quote**: "After:   api-east returns 503s           ← expected: the remote pods are gone"
- **Quote**: "This is the correct behavior. The client explicitly asked for `api-east`, and east is down. Handling that is the client's job: fail over to `api-west`, retry, or front the two with a TrafficSplit. Mirroring hands you control; federation hands you automation."
- **Our assessment**: The cleanest statement in the post of a control/automation trade, and the guide-relevant sentence is the last one. The 503 is not a bug in the platform — it is the platform honouring an explicit request. But "correct" is a contract claim: the client's retry/failover logic has to be *there*, and the post's own list of remedies (fail over, retry, TrafficSplit) is a to-do list for the client team. Note the guide-relevant asymmetry: federation converts a client obligation into a platform property.

### Claim 9: The gateway-mirrored service returned 502s after the same cluster loss, because the gateway that served it was in the cluster that died
- **Evidence**: The chaos-test output block for `analytics-east-gw` plus the one-line explanation.
- **Confidence**: settled
- **Quote**: "After:   analytics-east-gw returns 502s  ← the gateway is down too"
- **Quote**: "Same story here, the client asked for a specific remote, and that remote is gone."
- **Our assessment**: Useful as the concrete instance of *the relay is a failure domain too* — a gateway-mirrored service inherits the fate of the cluster hosting the gateway, and the two status codes (503 for a dead backend, 502 for a dead relay) let an operator distinguish the two cases from the client side. It is also the reminder that *gateway mode needs less network* buys reachability, not redundancy.

### Claim 10: A recovered cluster rejoins the federation under-weighted (~14% instead of an even third) unless its replica count is restored — capacity, not membership, determines the share
- **Evidence**: The source's parenthetical note on the restore step, with the concrete numbers.
- **Confidence**: emerging (one observed figure on a 9-pod demo; the arithmetic is consistent — 1 of 7 healthy pods after a restore-to-1 is ~14% — but the source gives no measurement series)
- **Quote**: "The script restores `frontend` to its full `FRONTEND_REPLICAS` count rather than leaving it at 1, otherwise east would rejoin the federation under-weighted, landing around 14% instead of an even third."
- **Quote**: "Within 15–30 seconds all three patterns recover: the federated service rebalances back to 33/33/33, and the mirrored services start answering again."
- **Our assessment**: A subtle and genuinely useful failure mode for the guide's capacity-and-recovery discussion: the federation is *proportional*, so a cluster that comes back under-provisioned silently receives a proportionally smaller share of traffic. The blast radius is a service that is up but degraded for everyone, with no error signal — the cluster is healthy, the *service* is under-capacity. The source's fix (restore the replica count) is a deployment action, not a mesh action, which is exactly the kind of thing an operator forgets after an incident.

### Claim 11: VPC peering without custom-route exchange on both sides leaves pod CIDRs unadvertised, and the symptom is "DNS resolves fine, then connections just hang"
- **Evidence**: The infra script is described as setting up full-mesh peering "with `–export-custom-routes` and `–import-custom-routes` so pod CIDRs are actually advertised"; the gotchas section states the failure explicitly.
- **Confidence**: settled (network fact; symptom described by the author as the hard-to-diagnose case)
- **Quote**: "Creating the peering isn't enough. You have to pass `–export-custom-routes` and `–import-custom-routes` on both sides, or the pod CIDRs never get advertised. The symptom is brutal to diagnose: DNS resolves fine, then connections just hang. Maddening to debug."
- **Our assessment**: A textbook silent failure for the guide's failure-mode catalogue: the control plane is healthy, service discovery works, and the failure surfaces as a hang with no error. The reason it is dangerous is precisely that DNS *succeeds* — a check that stops at *does the name resolve* passes on a completely broken cross-cluster path. The guide should name the discriminating test: resolve is not connectivity.

### Claim 12: Overlapping pod CIDRs across peered VPCs break routing silently — pods get responses from the wrong cluster, or connections time out with nothing useful in the logs
- **Evidence**: The address-plan section's explicit warning, the script's non-overlapping CIDR requirement, and the gotchas entry on GKE's default allocation.
- **Confidence**: settled (routing fact; symptom reported by the author)
- **Quote**: "Non-overlapping ranges are non-negotiable. If pod CIDRs overlap across peered VPCs, routing breaks silently. Pods get responses from the wrong cluster, or connections time out with nothing useful in the logs. Ask me how I know."
- **Quote**: "GKE auto-allocates large ranges out of the `10.0.0.0/8` space by default, and three clusters built with defaults will overlap, at which point peering fails silently. Always set explicit, non-overlapping `–cluster-ipv4-cidr` and `–services-ipv4-cidr`."
- **Our assessment**: "Pods get responses from the wrong cluster" is the scary version: not an error but a *cross-talk* failure where a request is answered by a replica in a region the caller did not select, breaking the locality assumption that motivated flat mirroring in the first place. The guide value is the pattern — platform defaults that are safe for one cluster are unsafe for three, so a multi-cluster platform must pin its own address plan as configuration rather than inherit it.

### Claim 13: A GKE regional cluster multiplies `--num-nodes` by the zone count, so `--num-nodes 1` silently becomes three nodes per cluster
- **Evidence**: The "One zone, not three" note in the infra section, the `.env` comment, and the gotchas entry ("Easy to miss until the bill arrives"). The demo's `CLUSTER_NODE_COUNT=1` is pinned with `--node-locations` to a single zone to avoid it.
- **Confidence**: settled (documented GKE behaviour)
- **Quote**: "A GKE regional cluster places `–num-nodes` nodes in each of three zones by default. With `–num-nodes 1` that's 3 nodes per cluster, 9 total, and triple the bill. The script pins `–node-locations` to a single zone so `CLUSTER_NODE_COUNT=1` really means one node per cluster."
- **Quote**: "A regional cluster with `–num-nodes 1` quietly gives you three nodes (one per zone). We pin `–node-locations` to a single zone to keep it at one. Easy to miss until the bill arrives."
- **Our assessment**: Not a reliability failure but a capacity-accounting failure, and a good instance of the guide's *measure the thing you think you configured* rule: the configuration knob says 1, the cluster has 3, and the discrepancy surfaces only on the invoice. Worth carrying as a capacity-planning caveat for multi-cluster platform builds.

### Claim 14: One service-mirror controller is required per consumed link — miss one and the Link CR is created, nothing mirrors, and `linkerd multicluster check` still looks green
- **Evidence**: The install commands in the post explicitly set one controller per consumed link (west and north each get a third controller for the `east-gw` link; east gets two because it does not consume its own analytics), and the gotchas entry names the symptom.
- **Confidence**: settled (mechanism shown in the config; symptom described by the author)
- **Quote**: "Each cluster needs one service-mirror controller per link it consumes. Miss one and the Link CR is created, but nothing mirrors, and `linkerd multicluster check` still looks green, so you'll stare at it for a while before the penny drops."
- **Our assessment**: The highest-value item in the post for the guide's failure-mode catalogue: the health check is green because it validates the *link*, not the *mirroring*. A verification tool that checks one link in the chain and declares success is exactly the *all-health-checks-green-but-degraded* shape the corpus already has a note for (see Cross-References). The transferable rule: a topology check must assert the *end-to-end property* (a mirrored endpoint actually exists), not the presence of the configuration object.

### Claim 15: A federated service's name suffix is fixed (`<svc>-federated`), and a single Link CR cannot be both gateway and flat — dual behaviour needs two named links and a matching controller each
- **Evidence**: The gotchas section, plus the demo topology that implements exactly this (`east` flat link + `east-gw` gateway link, with controllers for both on `west` and `north`).
- **Confidence**: settled
- **Quote**: "The federated service is always `<svc>-federated`; you can't change the suffix. Clients have to target `frontend-federated`, not `frontend`. Plan your naming around it, or use a TrafficSplit to point `frontend` at `frontend-federated`."
- **Quote**: "A single Link CR is either gateway or flat, not both. To get both behaviors to the same cluster you create two links with different names. That's why our setup uses `east` (flat) and `east-gw` (gateway) as separate links, with a matching controller for each on the consuming clusters."
- **Our assessment**: Two naming/coupling constraints that a platform team has to design around *before* clients are written: the client-visible name of a federated service is fixed by the platform, and the topology's coupling unit (a link) can carry only one mirroring mode. The TrafficSplit escape hatch for the naming constraint is the standard Kubernetes answer and the post points at it.

### Claim 16: Cross-cluster mTLS uses one shared trust anchor with per-cluster issuer certificates, so a compromised issuer can be rotated in isolation
- **Evidence**: The install script's generated certificate hierarchy and the paragraph explaining it; the production checklist's "Separate issuer certs per cluster (don't skip it!)" and "cert-manager with a shared CA instead of hand-rolled `step` certificates".
- **Confidence**: settled (mechanism stated; certificate layout shown)
- **Quote**: "Per-cluster issuer certs are a production habit worth keeping: if one cluster's issuer is compromised you rotate it in isolation, without touching the others. The shared root is what lets cross-cluster mTLS work at all. Every proxy can verify every other proxy's identity back to the same anchor."
- **Our assessment**: The trust-anchor pattern (one shared root, per-cluster leaves/issuers) is the standard way to get mutual authentication across a fleet while keeping blast radius small, and it is exactly the shape the corpus already uses for secrets (a cert-manager self-signed CA → ClusterIssuer → CA Certificate → Issuer → leaf chain, and a central provider propagated to every cluster). The rotation-isolation property is the point: the shared root is the only thing that cannot be rotated independently, so it is the thing to protect. Note the demo used hand-rolled `step` certificates and the production checklist itself says to use cert-manager instead — the demo's mechanism is not the production recommendation.

### Claim 17: The mode-selection decision framework: cluster-agnostic client → federated; client must pick a cluster → flat mirror; no flat network → gateway mirror; explicit traffic weights → flat mirror + TrafficSplit; singleton service → mirror
- **Evidence**: The decision table the author says they would hand a teammate after running all three side by side, followed by the statement that the modes mix freely.
- **Confidence**: emerging (author's own framework, derived from one demo; not a published standard)
- **Quote**: "Should the client be cluster-agnostic? Federated"
- **Quote**: "Does the client need to pick a specific cluster? Flat mirror"
- **Quote**: "Is there no flat network between clusters? Gateway mirror"
- **Quote**: "Do you need automatic failover with no app changes? Federated"
- **Quote**: "Do you need traffic splitting with explicit weights? Flat mirror + TrafficSplit"
- **Quote**: "Is the service a singleton (only in one cluster)? Mirror (flat or gateway)"
- **Quote**: "And you can mix them freely in the same mesh. The label on each service decides its behavior independently of the others."
- **Our assessment**: The most quotable artifact in the post — a question→mode table rather than a product-choice argument. Its real value for the guide is that the questions are about *client obligations* (does the client need to know where it is? does it need weighted routing?), which is the axis a platform team should reason on. Two of the six entries are decided by network topology rather than client need, which is worth flagging: the framework is only as good as the flat network underneath it. The "Is the service a singleton (only in one cluster)? Mirror (flat or gateway)" entry is also a useful reminder that a service that only exists in one cluster cannot be federated and needs the explicit naming treatment.

### Claim 18: Automatic failover removes a real chunk of operational toil, and the two operational recommendations are to alert on a federated service's endpoint count dropping and to test failover by scaling a cluster to zero in staging
- **Evidence**: The post's key-takeaways paragraph and the production checklist.
- **Confidence**: emerging (author's framing; the checklist items are recommendations, not measured outcomes)
- **Quote**: "For teams running across regions, that's a real chunk of operational toil gone: your services run everywhere, traffic finds the healthy copies, and you pick the multicluster mode per service based on what that service actually needs."
- **Quote**: "pipe Linkerd-Viz metrics into your Prometheus/Grafana stack, and alert on a federated service's endpoint count dropping"
- **Quote**: "scale a cluster to zero in staging and confirm traffic redistributes"
- **Our assessment**: The toil claim is the post's own, and it is checkable against the runbook inventory: if failover is a label, the "restore, repoint DNS, and wait" runbook from Claim 1 disappears — that is the toil, removed by *construction* rather than by a script. The two checklist items are the guide's monitoring and drill recommendations in the source's own words, and the first is unusually concrete: the federated endpoint count is a bespoke SLI that indicates degraded redundancy *before* users feel it. Note the caveat: the checklist is one line in a list; the post gives no threshold, no window, and no dashboard.

### Claim 19: The author's own summary judgement is that the capability is mostly wiring, not complexity
- **Evidence**: Closing section of the post, reporting the author's surprise at building it.
- **Confidence**: anecdotal (one practitioner's impression; the demo's scripts are ~6 steps)
- **Quote**: "What surprised me most about building this is how little of it is genuinely complex. It's mostly wiring. Once the trust anchor is shared and the links are up, adding a service to the federation is a single `kubectl label`, and removing a cluster is as simple as letting it go down. The mesh adjusts on its own."
- **Our assessment**: Worth recording as a counterweight to the guide's "complexity is an externality" principle: here the complexity sits in the *one-time* platform wiring (trust anchor, links, address plan, controller counts) and the per-service marginal cost is a label. But the same post's gotchas list is where the complexity actually lands — it is deferred, not absent, and each gotcha is a silent failure rather than a loud one. The honest reading for the guide: multi-region failover is cheap to *adopt* and expensive to *mis-configure silently*.

## Concrete Artifacts

**Artifact 1 — the three modes, their labels, and their network requirements (source table, reproduced):**

| Mode | Label | What happens | Network Requirement |
|------|-------|--------------|---------------------|
| Hierarchical (gateway) | `mirror.linkerd.io/exported=true` | Service mirrored as `<svc>-<cluster>`, traffic routed through a gateway | Gateway IP reachable |
| Flat (pod-to-pod) | `mirror.linkerd.io/exported=remote-discovery` | Service mirrored as `<svc>-<cluster>`, traffic goes directly to remote pods | Flat network (pod IPs routable) |
| Federated | `mirror.linkerd.io/federated=member` | All same-name services unioned into `<svc>-federated`, load balanced across all clusters | Flat network (pod IPs routable) |

**Artifact 2 — the mode-selection decision framework (source table, reproduced):**

| Question | → Mode |
|----------|--------|
| Should the client be cluster-agnostic? | Federated |
| Does the client need to pick a specific cluster? | Flat mirror |
| Is there no flat network between clusters? | Gateway mirror |
| Do you need automatic failover with no app changes? | Federated |
| Do you need traffic splitting with explicit weights? | Flat mirror + TrafficSplit |
| Is the service a singleton (only in one cluster)? | Mirror (flat or gateway) |

**Artifact 3 — the address plan used by the infra script (source table, reproduced; non-overlapping ranges are the point):**

| Cluster | VPC Subnet | Pod CIDR | Service CIDR |
|---------|------------|----------|--------------|
| west | 10.10.0.0/20 | 10.100.0.0/14 | 10.104.0.0/20 |
| east | 10.20.0.0/20 | 10.108.0.0/14 | 10.112.0.0/20 |
| north | 10.30.0.0/20 | 10.116.0.0/14 | 10.120.0.0/20 |

**Artifact 4 — the chaos test, verbatim output blocks (source; note the `←` annotations are the author's):**

```
Before:  west=33% east=33% north=33%
After:   west=50% north=50%              ← automatic rebalance, zero errors
```

```
Before:  api-east responds normally
After:   api-east returns 503s           ← expected: the remote pods are gone
```

```
Before:  analytics-east-gw responds normally
After:   analytics-east-gw returns 502s  ← the gateway is down too
```

**Artifact 5 — the endpoint dumps proving what each mode resolves to (verbatim from the source):**

```
# Federated: endpoints span all three clusters
$ linkerd --context west diagnostics endpoints frontend-federated.mc-demo.svc.cluster.local:8080
NAMESPACE   IP            PORT   POD                        SERVICE
mc-demo     10.100.1.15   8080   frontend-xxx-west          frontend.mc-demo
mc-demo     10.108.0.42   8080   frontend-xxx-east          frontend.mc-demo
mc-demo     10.116.0.33   8080   frontend-xxx-north         frontend.mc-demo

# Flat mirror: endpoints are the remote pod IPs
$ linkerd --context north diagnostics endpoints api-west.mc-demo.svc.cluster.local:8080
NAMESPACE   IP            PORT   POD                        SERVICE
mc-demo     10.100.2.10   8080   api-xxx-west               api.mc-demo

# Gateway mirror: the endpoint is east's gateway IP on port 4143
$ kubectl --context west -n mc-demo get endpoints analytics-east-gw
NAME               ENDPOINTS             AGE
analytics-east-gw  35.186.xxx.xxx:4143   30s
```

**Artifact 6 — one service-mirror controller per consumed link (verbatim from the source):**

```bash
# west: gatewayless, with one controller per cluster it consumes from
linkerd --context west multicluster install --gateway=false \
  --set controllers[0].link.ref.name=east \
  --set controllers[1].link.ref.name=north \
  --set controllers[2].link.ref.name=east-gw \
  | kubectl --context west apply -f -

# east: gateway enabled here, controllers for the clusters it consumes
linkerd --context east multicluster install --gateway=true \
  --set controllers[0].link.ref.name=west \
  --set controllers[1].link.ref.name=north \
  | kubectl --context east apply -f -

# north: gatewayless, controllers for west, east, and east's gateway link
linkerd --context north multicluster install --gateway=false \
  --set controllers[0].link.ref.name=west \
  --set controllers[1].link.ref.name=east \
  --set controllers[2].link.ref.name=east-gw \
  | kubectl --context north apply -f -
```

**Artifact 7 — link generation: flat links for federated/flat services, a separate named link for the gateway-aware export (verbatim from the source):**

```bash
# Flat links (no gateway) — for federated + flat-mirrored services
linkerd --context east multicluster link-gen --cluster-name=east --gateway=false \
  | kubectl --context west apply -f -
linkerd --context west multicluster link-gen --cluster-name=west --gateway=false \
  | kubectl --context east apply -f -
# ... (all six directions)

# Gateway-aware link from east (for the analytics hierarchical export)
linkerd --context east multicluster link-gen --cluster-name=east-gw \
  | kubectl --context west apply -f -
linkerd --context east multicluster link-gen --cluster-name=east-gw \
  | kubectl --context north apply -f -
```

**Artifact 8 — the certificate hierarchy for cross-cluster mTLS (verbatim from the source):**

```
root.crt (shared trust anchor)
├── issuer-west.crt + issuer-west.key
├── issuer-east.crt + issuer-east.key
└── issuer-north.crt + issuer-north.key
```

**Artifact 9 — the traffic-generator output proving all three patterns live in one mesh (verbatim from the source):**

```
[federated]  frontend from east
[federated]  frontend from west
[federated]  frontend from north
[flat-west]  api from west
[flat-east]  api from east
[gateway]    analytics from east
```

**Artifact 10 — the production checklist (verbatim items from the source):**

```
Bidirectional links between all clusters (full mesh) so every cluster has the federated service
cert-manager with a shared CA instead of hand-rolled `step` certificates
Separate issuer certs per cluster (don't skip it!)
NetworkPolicies restricting cross-cluster traffic to only the services that need it
Linkerd authorization policies for fine-grained access control
pipe Linkerd-Viz metrics into your Prometheus/Grafana stack, and alert on a federated service's endpoint count dropping
keep Link CRs and multicluster config in version control
scale a cluster to zero in staging and confirm traffic redistributes
```

**Artifact 11 — the one-line labelling that changes a service's cross-cluster behaviour (verbatim from the source):**

```bash
for ctx in west east north; do
  kubectl --context $ctx -n mc-demo label svc/frontend mirror.linkerd.io/federated=member
done
```

## Cross-References

- **Corroborates**:
  - `source-notes/blog-cncf-geo-distributed-ai-k0smos.md` — **Claim 2** ("A single Kubernetes cluster cannot span geographies, so multi-cluster orchestration becomes non-negotiable for geo-distributed AI") is the same constraint this source solves from the traffic-management side, and its **Claim 10** (A custom Flower operator reconciles a declarative "Federation" custom resource so nodes join and exit the federation gracefully as they are provisioned/deprovisioned) is the same *declarative-membership* shape as this post's per-service label. Complementary: that note is the control-plane/topology angle (k0s/k0smotron/k0rdent, GPU lifecycle, WAN latency); this note is the data-path angle (how a client reaches a service in another cluster and what happens when that cluster dies). This note's Claim 3 (flat/federated modes require real pod-to-pod connectivity) is the network-precondition counterpart to that note's Claim 5 (cross-site data plane over Cilium WireGuard P2P tunnels, ~35ms) — both are the same *interconnect is the constraint* point.
  - `source-notes/failure-cncf-kubeflow-cilium-60-idle-gpus.md` — **Claim 2** ("Correct systems can produce silent collective failure") and **Claim 6** ("Instrumentation is essential for detection"). This source's Claim 14 is the same failure shape in a different layer: the Link CR exists, the health check is green, and nothing mirrors — a correct-looking configuration that produces silent collective failure. Its Claim 7 ("Pattern generalizes beyond Cilium/Kubeflow") is the corpus's standing invitation, and this note answers it with four more instances (Claims 11, 12, 14, and the under-weighted rejoin in Claim 10).
  - `source-notes/docs-google-sre-data-processing-pipelines.md` — **Claim 5** ("Plan for dependency failure by designing for at least the largest failure in a dependency's advertised SLA — and Google stages DiRT regional-outage tests; an unplanned manual failover risks continuing to process stale data"). This source is the concrete regional-outage drill for a *traffic* dependency: `scale deploy --all --replicas=0` in a cluster stands in for its loss, and the claim that a manual failover is risky is exactly what the federation label eliminates (Claim 1 vs Claims 7/18). Its **Claim 4** ("Per-stage SLO measurement misses end-to-end corruption") is the same blind-spot shape as this note's Claim 14: the per-link check is green while the end-to-end property is broken.
  - `source-notes/docs-google-sre-prodcast-04-02-data-centers.md` — **Claim 4** ("Disaster testing must be *real* — DiRT simulates failures, but ISON actually shuts things off"). This source's chaos test is the same doctrine applied to a software topology: a real workload is killed and real traffic is sampled, and the numbers (33/33/33 → 50/50, 503s, 502s) come from the running system rather than a plan. **Claim 5** ("The math of real-world logistics lies") is the appropriate caveat — the post's own rejoin arithmetic (14% vs a third) is an estimate, not a measurement series.
  - `source-notes/docs-google-sre-twenty-years-lessons.md` — **Claim 2** ("Recovery mechanisms must be fully tested before an emergency") is the rule the production checklist's last item operationalises ("scale a cluster to zero in staging and confirm traffic redistributes"). **Claim 9** ("Automate mitigations for clear failure signals to reduce MTTR") is what federation *is* in this source: the mitigation (rebalance onto healthy replicas) is executed by the platform with no human in the loop. **Claim 7** ("Build degraded performance modes carefully and intentionally") is the counterweight — this source demonstrates the *fully-up* mode (federated) and the *fully-down* mode (503/502 on a named remote), but not the degraded middle.
  - `source-notes/docs-google-sre-eliminating-toil.md` — **Claim 2** ("Automatable" remediation documents — "log in to X, execute this command, check the output, restart Y if you see…" — are "essentially pseudocode to someone with software development skills," making runbook content itself the raw material for automation). This source's Claim 1 is exactly such a document ("restore, repoint DNS, and wait") and Claim 18 is what happens when the remediation is built into the platform instead of written down: the runbook disappears, which is the highest-leverage form of toil reduction the note's **Claim 15** ("Start small and improve") recommends — one `kubectl label` rather than a new automation project. **Claim 16** (the Saturn→Jupiter datacenter-repair automation case) is the same *replace repeated human repair with software-enforced policy* pattern, applied to network repair rather than service traffic.
  - `source-notes/blog-cncf-secret-sprawl-external-secrets-operator.md` — **Claim 10** (TLS between ESO and the Bitwarden SDK server is bootstrapped in-cluster with cert-manager — self-signed CA → ClusterIssuer → CA Certificate → local Issuer → leaf Certificate) is the same bootstrap shape as this source's shared trust anchor with per-cluster issuer certs (Claim 16), and **Claim 3** ("ESO propagates a rotation from the central provider to all clusters within the configured `refreshInterval` — rotate once, all clusters converge") is the cross-cluster propagation property this source gets by construction: one shared root, per-cluster issuers, isolated rotation.
  - `source-notes/docs-google-sre-prodcast-02-07-sabrina-farmer.md` — **Claim 11** (The future of SRE is to question the assumptions behind standing policies and ask "what would have to be true for the system to self recover?" — build systems that understand and circumvent their own failure modes rather than layering workarounds on top). This source's answer to that question is concrete and testable: a shared trust anchor plus links plus a per-service label, after which "The mesh adjusts on its own" (Claim 19) when a cluster dies. It is a pre-agent, non-LLM instance of the self-recovery property the guide's Ch00 principle names.
  - `source-notes/blog-cncf-otel-mesh-derived-metrics.md` — **Claim 3** ("The `client_id` label is the mTLS identity of the caller") and **Claim 4** (Linkerd's golden metrics computed from `response_total` and `response_latency_ms`) supply the measurement layer this source's checklist invokes: "pipe Linkerd-Viz metrics into your Prometheus/Grafana stack". The corpus already has the mesh-metrics extraction; this source supplies the *topology* the mesh metrics should be watched across, and the specific signal to watch (the federated endpoint count) is the one thing mesh golden metrics do not cover.

- **Contradicts**: None that meets the MINER.md §4a bar. Checked `CONTRADICTIONS.md` and the open `contradiction`-labeled issues (all 19 are promptfoo/LiteLLM documentation-internal); none concern multicluster, federation, service mesh, or failover topology, and no `C-NNN` entry exists on this topic. No existing note claims that automatic cross-cluster failover is unreliable, that a mesh-based approach is unsound, or that named remotes are the superior default, so no claim in this source materially opposes an existing one. Two **tensions** are recorded rather than filed:
  - `docs-google-sre-handling-overload.md` **Claim 1** (Load shedding must signal overload to the load balancer — fast error responses are interpreted as "efficient processing" by latency-based LBs, attracting *more* traffic and creating a positive feedback loop) versus this source's flat/gateway behaviour: after a cluster loss, the mirrored service returns a *fast* 503/502. The source calls that correct; the overload doctrine warns that fast errors can attract more traffic from a latency-based balancer. These are compatible rather than opposed — the mirrored 503 means "that remote is gone" and the client must fail over, and a latency-based LB in front of it would need to treat that as a dead target, not a fast success — but the source does not test a latency-based LB in the path, so the guide should not present the 503 as automatically safe for any client.
  - `docs-google-sre-address-cascading-failures.md` **Claim 10** (Intra-layer communication is prohibited — "always go downward in the stack") versus federated services, whose endpoint set spans clusters, so a same-tier service can now be answered by a replica in another region. This source never discusses retry amplification (**Claim 4**), cross-cluster latency, or the cascade behaviour of a federation whose members fail at once — the chaos test kills one of three clusters and samples traffic, which is not a cascade test. Recorded as a scope caveat on the "zero errors" result rather than as a contradiction: the source does not claim the cascade risk is absent.

- **Extends**:
  - `source-notes/blog-cncf-geo-distributed-ai-k0smos.md` — extends it from the control-plane side to the traffic-management side: k0s/k0smotron/k0rdent decide *which clusters exist*; this source decides *how a client in one of them reaches a service in another*. This note's Claim 3 (network preconditions) and Claims 11–12 (peering and CIDR planning) are the traffic-side counterpart to that note's Claim 12 ("The real friction in fragmented environments was GPU lifecycle management and cross-site networking — not the control-plane stack").
  - `source-notes/docs-google-sre-address-cascading-failures.md` — extends the mitigation hierarchy (**Claim 14**) with a case where the *first* rung is taken automatically by the platform and the human's job is only to decide the mode ahead of time. It also supplies the concrete federated-endpoint analogue of the chapter's "rarely-exercised code paths must be monitored" rule (**Claim 11**): the federation's failure path is exercised only when a cluster dies, which is why the checklist says to scale a cluster to zero in staging.
  - `source-notes/docs-google-sre-prodcast-01-03-alerting.md` — extends it with a concrete bespoke SLI: "alert on a federated service's endpoint count dropping" is a dependency-caused condition in the sense of **Claim 3** ("for dependency-caused outages you often cannot catch them pre-impact"), and a candidate for threshold rot in the sense of **Claim 12** ("if the service improved (two 9s → four 9s) but alerts stayed at two 9s, regressions go unnoticed"). The corpus's alerting doctrine has no example of an SLI that measures *redundancy* rather than *error rate*; this source supplies one.
  - `source-notes/docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` — extends the resilience-vs-capacity contrast: **Claim 10** (An early DeepMind anti-pattern was doubling capacity across sites instead of building resilience between experiments — "more and more points of failure") is the redundancy-without-resilience mistake; this source is the resilience-without-capacity-complement case (Claim 10: a recovered cluster that rejoins under-weighted). **Claim 3** (Standard Google infrastructure did not measure accelerators — dashboards showed CPU/memory but "nothing for how much GPU you were using" — so Damion had to build accelerator monitoring "from the ground up") is the same *you must instrument the thing you depend on* requirement as the endpoint-count alert.

- **Novel**: First source note in the corpus covering:
  1. **Cross-cluster service federation as a per-service labelling decision** — three modes (federated / flat mirror / gateway mirror) coexist on one set of links, chosen by a label, with a published question→mode decision framework (Claim 17).
  2. **A measured side-by-side failure-semantics contrast** under a whole-cluster kill: federated = automatic rebalance with zero errors and no config change; flat mirror = 503; gateway mirror = 502 (Claims 7–9). The corpus had failover theory and regional-outage drills, but no measurement of how three traffic-management topologies behave under the same outage.
  3. **The *automatic failover removes a runbook* argument** — failover as toil removed by construction rather than by a script (Claims 1 and 18).
  4. **A catalogue of silent multi-cluster misconfigurations** with named symptoms: VPC peering without custom-route exchange (DNS resolves, connections hang), overlapping pod CIDRs (responses from the wrong cluster), missing service-mirror controller (Link CR green, `linkerd multicluster check` green, nothing mirrors), fixed `-federated` naming, one Link CR = one mode (Claims 11–15).
  5. **Capacity-proportional federation membership** — a recovered cluster rejoins at ~14% instead of a third if its replica count is not restored (Claim 10), i.e. degraded-but-green membership.
  6. **Shared-trust-anchor cross-cluster mTLS with per-cluster issuer certs** for isolated rotation (Claim 16).
  7. **The federated endpoint count as a redundancy SLI** — the corpus's first concrete *alert on the size of your redundancy* signal (Claim 18).

## Guide Impact

- **Chapter 01 (Incident Response) — `guide/01-incident-response.md`, "Prepare before the incident" and "Open topics"**: The chapter's drill doctrine currently cites DiRT, Wheel of Misfortune, and "breaking the test environment" as the drill catalogue. Add this source's drill as the *multi-cluster* instance, with its exact form and cost: scale one cluster's deployments to zero in a staging copy of the topology, sample real traffic, and record what each traffic pattern does — the source's own checklist item is "scale a cluster to zero in staging and confirm traffic redistributes", and the recorded outcomes are the three-part split (federated rebalances to 50/50 with zero errors; flat mirror 503s; gateway mirror 502s). The drill's value is that it converts the existence of a failover runbook into a measured statement about *which* services fail over automatically and which require the client to act — which is also the answer to the chapter's unsourced open topic on triage/mitigation ordering for cluster loss. [source: blog-cncf-linkerd-multicluster-federation, Claims 7–9, 18]
- **Chapter 03 (Runbooks and agents) — `guide/03-runbooks-and-agents.md`, "Generic mitigations taxonomy"**: The taxonomy already lists "fail-over" as a mitigation that agents may recommend or apply, each with preconditions and a blast-radius estimate. This source supplies a concrete precondition for that entry: whether failover is a zero-touch, no-config-change platform action or a client-side obligation is decided *before the incident*, by the label the service was given at deploy time. Recommend the guide add a line stating that the "fail-over" mitigation's precondition is a property of the traffic topology (federated vs named-remote) and that the agent must not assume a failover action exists for a service that was mirrored. Note also that the failure modes this source enumerates (Claims 11, 12, 14) are precisely the "preconditions" a mitigation catalog needs to encode — they are silent, so a catalog that lists actions without topology preconditions will recommend actions that appear to succeed. [source: blog-cncf-linkerd-multicluster-federation, Claims 2, 7, 8, 11, 12, 14]
- **Chapter 02 (Observability) — `guide/02-observability.md`, "Platform-side observability: shared SLO dashboards" and the alerting material**: Two additions. (a) A concrete redundancy SLI the corpus lacks — "alert on a federated service's endpoint count dropping" — which measures the *size of the safety net* rather than the error rate, and therefore fires before users feel anything, provided it is wired to the mesh's endpoint data (the corpus's Linkerd note supplies the golden-metric families: `response_total`, `response_latency_ms`). Flag that the source gives no threshold and no window, so the guide should present it as a signal to be tuned, not a rule. (b) The chapter's existing "a provider's global SLO rollup can hide region-isolated outages for a small-footprint tenant" failure mode has a per-service analogue here: a federated endpoint list is the rollup, and a cluster dropping out of it shrinks the set silently. [source: blog-cncf-linkerd-multicluster-federation, Claims 7, 10, 18]
- **Chapter 04 (On-call and toil) — `guide/04-oncall-and-toil.md`, "What counts as toil"**: Add the runbook-as-toil instance: in the source's framing, the "restore, repoint DNS, and wait" failover runbook is the toil, and it is removed by construction when the platform federates the service (one `kubectl label` at deploy time instead of a runbook at incident time). This is the chapter's six-characteristic taxonomy applied to a case where the highest-leverage reduction is architectural rather than scripted — which is the chapter's "Simplification is the non-automation lever" argument in its sharpest form, and a concrete candidate for the toil-measurement ledger ("manual production change" / "completed ticket" units for failover-related work). [source: blog-cncf-linkerd-multicluster-federation, Claims 1, 18, 19]
- **Chapter 00 (Principles) — `guide/00-principles.md`, "What would have to be true for the system to self recover?"**: The section currently sources the self-recovery principle to `docs-google-sre-prodcast-02-07-sabrina-farmer` and frames it as aspirational with AI agents as one mechanism. This source is a non-AI, pre-agent instance of the same property — once the trust anchor is shared and the links are up, "The mesh adjusts on its own" when a cluster dies, with no human action and no config change. One-line citation is enough, and it strengthens (rather than replaces) the existing framing: self-recovery here is achieved by removing the client's obligation, not by making the client smarter. [source: blog-cncf-linkerd-multicluster-federation, Claims 7, 19]
- **Chapter 05 (LLM Ops Reliability) — `guide/05-llm-ops-reliability.md`**: No LLM-specific change, and this source must not be cited as LLM evidence — it contains no inference serving, no GPU scheduling, and no model traffic, and the Prospector triage flagged this explicitly. The transferable piece is narrow and should be labelled as such if used: an LLM gateway or inference tier served across regions inherits the same choice between a cluster-agnostic endpoint (automatic failover, no client change) and an explicitly-named regional endpoint (client owns failover), and the same silent-misconfiguration classes. If the guide has no general multi-region availability-topology subsection, cite this source there rather than in the LLM-specific chapters. [source: blog-cncf-linkerd-multicluster-federation, Claims 2, 5, 17]

## Extraction Notes

- **Deep read**: the full CNCF post was fetched and read end-to-end on 2026-10-22, then re-fetched with `curl` and text-extracted to verify every quoted fragment character-for-character (this also surfaced the source's rendering quirks: WordPress converts `--num-nodes`/`--export-custom-routes` into en-dashes (`–num-nodes`, `–export-custom-routes`) on the page, and the fenced blocks are wrapped in literal ``` markers inside the `<pre>` elements; both are reproduced as the page renders them). No paywall, no login. Code blocks were extracted from the raw HTML `<pre>` elements so the spacing and annotations are the source's own.
- **Sub-pages**: the post's outbound links are the companion repo (`github.com/dtaskai/linkerd-multicluster-demo`), the GKE VPC-native alias-IPs doc, and five Linkerd documentation pages. Per MINER.md §1 (up to 5 linked pages) the Linkerd docs were **not** fetched — the note records the post's own claims only, and any statement in the note about how the upstream docs describe the modes is the author's, not the docs'. The companion repo was likewise not fetched; it is cited only as the source names it. No claim in this note depends on either.
- **Evidence grading**: `confidence_overall: emerging`. The mechanisms (labels, controller wiring, trust anchor, naming constraints, CIDR rules) are stated concretely and are checkable in the companion repo, so several claims are graded `settled` at claim level; the chaos-test figures and the ~14% rejoin weight are single-author, single-run observations on three one-node clusters with no error-rate series, no sample count, and no duration, so they stay `emerging`/`anecdotal` and should not be quoted as availability numbers. The post has **no AI/LLM content** — recorded per the Prospector triage's explicit caution.
- **Candidate list disposition** (`miner-related-notes.md`, read first — 10 candidates, all dismissed): the lexical retrieval returned SRE prodcasts and LiteLLM parameter docs with no overlap. `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SLO granularity, unrelated. `blog-cncf-cloud-native-agentic-ai-security-platform.md` — multi-agent security on Kubernetes; its Claim 2 (mTLS via cert-manager *without* a service mesh) is a different architecture for the same problem, but it contains no multi-cluster or failover-topology material. `docs-google-sre-eliminating-toil.md` — toil taxonomy; directly relevant to the source's toil claim, so it was **cited** (see Corroborates) rather than dismissed. `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative vs declarative change; unrelated. `docs-litellm-batches-api.md` — LiteLLM batch rate limiting; unrelated. `docs-google-sre-reliable-product-launches.md` — launch checklists; unrelated. `docs-google-sre-on-call.md` — on-call balance and pager hygiene; no failover-topology content. `docs-google-sre-slo-engineering-case-studies.md` — SLO adoption; unrelated (this source has no SLOs). `docs-google-sre-prodcast-03-01.md` — SRE-as-methodology; unrelated.
- **Corpus search beyond the candidate list**: `source-notes/` was searched for `failover|multi-region|multi-cluster|cluster loss|chaos|service mesh|linkerd|traffic split|federat|silent failure|self-recover|toil|endpoint count|cert-manager|rotation|trust anchor|VPC peering|pod CIDR|cross-cluster`. Coverage gaps confirmed before writing: `linkerd` appears in exactly one existing note (`blog-cncf-otel-mesh-derived-metrics.md`), `multi-cluster` in exactly one (`blog-cncf-geo-distributed-ai-k0smos.md`), and `endpoint count`, `VPC peering`, `pod CIDR`, `cross-cluster`, `trust anchor`, `flat mirroring`, and `gateway mirroring` in none — so the claims in this note are genuinely first-in-corpus rather than restatements.
- **§4b verification**: every cross-reference above was checked by re-reading the cited source note and confirming the `### Claim N:` heading numbering in document order. Claim numbers cited: `blog-cncf-geo-distributed-ai-k0smos.md` Claims 2, 5, 10, 12; `failure-cncf-kubeflow-cilium-60-idle-gpus.md` Claims 2, 6, 7; `docs-google-sre-data-processing-pipelines.md` Claims 4, 5; `docs-google-sre-prodcast-04-02-data-centers.md` Claims 4, 5; `docs-google-sre-twenty-years-lessons.md` Claims 2, 7, 9; `docs-google-sre-eliminating-toil.md` Claims 2, 15, 16; `blog-cncf-secret-sprawl-external-secrets-operator.md` Claims 3, 10; `docs-google-sre-prodcast-02-07-sabrina-farmer.md` Claim 11; `blog-cncf-otel-mesh-derived-metrics.md` Claims 3, 4; `docs-google-sre-handling-overload.md` Claim 1; `docs-google-sre-address-cascading-failures.md` Claims 4, 10, 11, 14; `docs-google-sre-prodcast-01-03-alerting.md` Claims 3, 12; `docs-google-sre-prodcast-05-08-damion-yates-ai-systems.md` Claims 3, 10. No quote from another source note is reproduced here, so no quoted passage needed character-for-character verification.
- **No contradiction issue filed.** `CONTRADICTIONS.md` contains only the format template (no `C-NNN` entries), and all 19 open `contradiction`-labeled issues are promptfoo/LiteLLM documentation-internal conflicts; none concerns multicluster, federation, service mesh, or failover topology. The two tensions recorded under Cross-References (fast 503s vs the load-shedding feedback loop; cross-cluster same-tier endpoints vs the "always go downward in the stack" rule) are scope caveats rather than oppositions that would force different guide advice, so per MINER.md §4a's "When NOT to file" they are documented in the note instead of filed. No verdict is picked anywhere in this note.
- **Not touched**: `registry/sources.json` and `registry/claims-index.json` are derived indexes rebuilt after merge; per the Miner brief they were deliberately left unmodified, and this PR adds only the source note under `source-notes/`.
