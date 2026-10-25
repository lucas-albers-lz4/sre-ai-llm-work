---
source_url: https://www.cncf.io/blog/2026/07/22/multi-cluster-databases-on-kubernetes-architecture-and-deployment
source_type: blog-post
title: "Multi-Cluster databases on Kubernetes: Architecture and deployment"
author: "Edith Puclla (CNCF Ambassador) and Ivan Groenewold (Tech Lead, Percona for MongoDB)"
date_published: 2026-07-22
date_extracted: 2026-10-25
last_checked: 2026-10-25
status: current
confidence_overall: emerging
issue: "#1734"
---

# Multi-Cluster databases on Kubernetes: Architecture and deployment

> A vendor-authored architecture walkthrough whose transferable payload is quorum placement and post-failover headroom: a 2+2 replica split across two sites has no majority when the link fails (both sides stop accepting writes), while a 2+2+1 placement with a fifth voter in a third location restores a 3-of-5 majority — and even a successful failover leaves the surviving set at bare majority, one node away from read-only. Useful as a concrete, checkable illustration of "redundancy must be reasoned about, not assumed" and of "survived failover" not equalling "healthy"; it contains no AI/LLM content.

## Source Context

- **Type**: blog-post (CNCF blog, vendor-authored architecture walkthrough with runnable `cr.yaml` snippets, MCS API setup, and a deployment workflow).
- **Author credibility**: Edith Puclla is described as a CNCF Ambassador; Ivan Groenewold is a Tech Lead at Percona for MongoDB. The authors are vendor-adjacent to the Percona Operator used as the example, and the piece is explicitly a Percona-operator walkthrough, but the quorum reasoning is a general MongoDB/distributed-systems property rather than a product benchmark. The post was reviewed by Chetan Shivashankar, Technical Lead, Kubernetes at Percona. No production incident data, blast-radius measurements, or cost figures are presented.
- **Scope**: Multi-cluster MongoDB on Kubernetes — site roles (Main vs Replica), the Kubernetes Multi-Cluster Services (MCS) API, 2+2+1 voter placement, the deployment workflow, and expected failover behaviour. Vitess and CloudNativePG are named only as relational equivalents. Does **NOT** cover AI/LLM workloads, inference serving, vector stores, SLOs, alerting, or measured failure behaviour; the authors say a follow-up post will run chaos-engineering experiments. The "~12 seconds" election figure is asserted from MongoDB defaults, not benchmarked here.

## Extracted Claims

### Claim 1: A single Kubernetes cluster has no built-in recovery for cluster-level failures, so a database that must survive a regional outage, corrupted control plane, or network partition has to span clusters
- **Evidence**: The opening problem statement, followed by three scenarios the architecture targets: disaster recovery, live migration, and maintenance without downtime. No failure data is shown; this is architectural framing.
- **Confidence**: emerging (the Kubernetes limitation is real, but the multi-cluster remedy is asserted rather than measured in this post)
- **Quote**: "However, it has no built-in mechanism to handle failures at the cluster level itself: a regional outage, a corrupted control plane, or a network partition can take down your entire database with no automatic recovery path."
- **Our assessment**: The durable point is the failure-domain boundary, not the MongoDB specifics: single-cluster self-healing covers Pod/Node loss but not loss of the cluster itself. That is a useful Ch00 illustration for "redundancy must be reasoned about, not assumed." Caveat: the source is a vendor architecture post; it does not demonstrate the remedy under a real regional failure (see Claim 8).

### Claim 2: All nodes in every participating cluster belong to one MongoDB replica set, and that single membership is what enables cross-cluster voting and leader election
- **Evidence**: The architecture overview states that nodes in different Kubernetes clusters are members of the same MongoDB replica set; the rest of the post's quorum reasoning depends on this.
- **Confidence**: settled (MongoDB replica-set mechanism)
- **Quote**: "All nodes, regardless of which cluster they run in, belong to a single MongoDB replica set, which is what enables cross-cluster voting and leader elections."
- **Our assessment**: This is the key separation: Kubernetes control planes remain independent, while the database's consensus group spans them. The transferable design question for any stateful service is whether its consensus membership spans the same failure domains as its data — spanning clusters in the Kubernetes layer alone does not create a cross-cluster quorum.

### Claim 3: Site roles split control-plane ownership — the Main Site operator owns TLS, credentials, and replica-set initialization, while Replica Sites run unmanaged and copy those secrets in
- **Evidence**: The role definitions and the `unmanaged: true` manifest snippet. The stated reason is to prevent two independent operators from controlling the same database.
- **Confidence**: settled (documented operator behaviour; mechanism is plainly shown)
- **Quote**: "The Operator runs with unmanaged mode to true, which means it does not generate certificates or user credentials, and does not attempt to initialize a new replica set."
- **Quote**: "This prevents the problem where two independent operators attempt to control the same database simultaneously."
- **Our assessment**: Generalises beyond MongoDB: in a multi-writer platform, exactly one control plane should own identity/initialization, and the others should join as managed-but-not-initializing members. The operational cost is real and understated: secrets must be copied from the Main Site, so the Replica Site has a configuration dependency on the Main Site that must itself be recoverable. The source does not discuss what happens when the Main Site's secrets are lost.

### Claim 4: A MongoDB replica set needs a strict majority of voting members to elect a primary and accept writes, so a symmetric 2+2 split across two locations deadlocks on partition — both sides stop accepting writes even though every server is healthy
- **Evidence**: The explicit quorum argument in "How to Design for High Availability", supported by the normal-state and after-partition diagrams.
- **Confidence**: settled (consensus arithmetic; standard MongoDB replica-set behaviour)
- **Quote**: "A MongoDB replica set requires a strict majority of its voting members to elect a Primary and accept writes. With four voting members spread equally across two locations, neither side can reach a majority if the network between them is severed, and both sides stop accepting writes, even if every server is healthy."
- **Our assessment**: The most transferable claim in the source. "Two replicas in each of two sites" sounds redundant but produces no writable side under partition: availability is a function of *where the voters are*, not how many copies exist. Worth using in Ch00 as a checkable counterexample to replica-count reasoning.

### Claim 5: The 2+2+1 pattern — a fifth voter in a third location — restores a 3-of-5 majority, so one side can keep or elect a primary when one location or link fails
- **Evidence**: The quorum arithmetic plus the `externalNodes` configuration snippet for the third-site member; the post also states the general rule (odd number of voting members in different locations).
- **Confidence**: settled for the arithmetic; emerging for this particular operator implementation (the post's own snippets are internally inconsistent — see Concrete Artifacts)
- **Quote**: "Have an odd number of MongoDB voting members, placed in different locations, so that if one location or network link fails, one side can still have enough votes to keep/elect a Primary."
- **Quote**: "With 5 total votes, one side reaches 3 votes; a majority, and elects a new Primary. This is the 2+2+1 pattern."
- **Our assessment**: The placement rule generalises to any consensus-backed state store: size the voter set so every failure domain you intend to survive leaves one side with a strict majority. The third site can be small (the example's fifth member is an external node), which makes the pattern cheaper than a symmetric three-site data footprint — but it also means the third site is a quorum-critical dependency even though it holds little data.

### Claim 6: Automatic failover elects a new primary in a median "does not typically exceed 12 seconds" under default configuration, and applications should use retryable writes because the write gap can be longer across regions
- **Evidence**: The failover section's timing statement and the retryable-writes recommendation. The 12-second figure has no citation, benchmark, or distribution; the source does not say what "median" was measured over.
- **Confidence**: anecdotal (uncited vendor assertion, not measured in this post)
- **Quote**: "Under the default configuration, the median time before a cluster elects a new primary does not typically exceed 12 seconds; this includes the time to detect the failure and complete the election."
- **Quote**: "In a multi-region setup, cross-cluster network latency may extend this window, so your application connection logic should include retryable writes to handle the brief period during which no Primary is available."
- **Our assessment**: The recommendation (retryable writes) is sound and actionable; the number is not evidence. Treat the 12 seconds as a vendor default claim to verify against your own deployment and failure mode, not as an SLO input. The source itself says cross-cluster latency may extend it — which is the part operators should budget for.

### Claim 7: A successful failover leaves the database degraded, not recovered — the surviving set runs at the exact minimum majority, and one further node loss drives it into read-only majority-loss mode
- **Evidence**: The "Architecture After Failover" section enumerates the new primary, reduced redundancy, and eliminated fault tolerance; the source explicitly labels the state "degraded" and warns about the next loss.
- **Confidence**: settled for the quorum arithmetic; emerging for the operational framing (no measured incident or drill in the post)
- **Quote**: "After a regional failure, your database is still working, but it enters a “degraded” state. This means it is functioning, but with fewer resources than normal."
- **Quote**: "If you lose just one more node in Cluster B or the node at Cluster C, the database will lose its majority and lock into “read-only” mode."
- **Our assessment**: The highest-value operational claim. Failover consumes the headroom you will need for the *next* incident, so "we survived failover" is not the same as "we are healthy." The incident status after a failover should include remaining quorum/redundancy, not just the new primary's health. This is the claim that maps most directly to Ch01.

### Claim 8: In the 2+2+1 example, failover happens without human or operator intervention, but the authors have not yet measured how the architecture behaves under real failure conditions
- **Evidence**: The post's narrative of the failover ("without any operator or human intervention") plus the closing statement that a follow-up post will use chaos-engineering experiments to measure real failure behaviour.
- **Confidence**: emerging (mechanism is documented; the operational outcome is not measured here)
- **Quote**: "The replica set detected the failure, held an election, and promoted a new Primary, automatically, without human intervention. That is the 2+2+1 pattern working as designed."
- **Quote**: "In a follow-up post, we will put this architecture under deliberate pressure with chaos engineering experiments to measure exactly how it holds under real failure conditions."
- **Our assessment**: Buy the mechanism, discount the assurance. The post demonstrates configuration and expected protocol behaviour, not a drill result; there is no measurement of election duration distribution, data loss window, client error rate, or recovery under load. The promised follow-up is the evidence to watch for before treating any of this as production-validated.

### Claim 9: Multi-cluster also enables live migration and no-downtime maintenance, but a clean cutover still requires application-level planning around connection strings and write consistency
- **Evidence**: The three-scenario list at the top; the live-migration bullet carries an explicit caveat that coordinating a clean cutover requires application-level planning.
- **Confidence**: emerging (architectural possibility, not demonstrated in the post)
- **Quote**: "Note that coordinating a clean cutover still requires careful application-level planning around connection strings and write consistency."
- **Our assessment**: Useful as a boundary on the "multi-cluster makes migration easy" story: the platform can move data, but the application's connection handling and consistency expectations remain its own problem. This is the same control/automation split the corpus already records for multi-cluster service routing, transposed to state.

## Concrete Artifacts

**Artifact 1 — the 2+2+1 fifth member configured as an external node (verbatim from source; excerpt from "How to Design for High Availability"):**

```yaml
externalNodes:
    - host: third-site-rs0-4.psmdb.svc.clusterset.local
      votes: 1
      priority: 1
```

**Artifact 2 — the Replica Site's unmanaged mode (source excerpt; unrelated MCS fields omitted):**

```yaml
spec:
  # ----------------------------------------------------
  # This tells the Operator NOT to start a new database, 
  # but to join the existing one to prevent split-brain.
  # ----------------------------------------------------
  unmanaged: true
```

**Artifact 3 — the post's finalize step, which is internally inconsistent with its own prose (verbatim from source):**

```yaml
replsets:
 - name: rs0
   size: 2
   externalNodes:
   - host: replica-cluster-rs0-0.psmdb.svc.clusterset.local
     votes: 1
     priority: 1
   - host: replica-cluster-rs0-1.psmdb.svc.clusterset.local
     votes: 0
     priority: 0
```

The adjacent prose says: "Two nodes are added as voting members with lower priority, and the third as a non-voting member, this prevents split-brain if the Replica Site loses connectivity." The snippet shows only two external nodes, one with `votes: 1` and one with `votes: 0` — not the two-voting-plus-one-non-voting arrangement the prose describes. Do **not** treat the vote counts in this snippet as a verified pattern; the source contradicts itself.

**Artifact 4 — quorum arithmetic derived from the source's 2+2+1 example (our derivation, not a source table):**

| State | Voting members available | Strict majority (3 of 5)? | Writes |
|-------|--------------------------|---------------------------|--------|
| Normal | 5 | yes | yes |
| After Cluster A fails | 3 (B + C) | yes (exactly 3) | yes, but degraded |
| One more node lost (B or C) | 2 | no | read-only |

For contrast, the symmetric 2+2 arrangement leaves each side with 2 of 4 votes after partition, so neither side has a strict majority and both stop accepting writes.

## Cross-References

- **Corroborates**:
  - `docs-google-sre-address-cascading-failures` Claim 15: the SRE Book's warning that reliability mechanisms can trade one outage for another is exactly the shape of this source's post-failover claim — automatic failover restores writes by consuming redundancy, so the next failure is more dangerous. This note supplies concrete quorum mechanics for that general warning.
- **Extends**:
  - `blog-cncf-linkerd-multicluster-federation` Claim 4 and Claim 18: that note shows stateless cross-cluster traffic failover absorbing a whole cluster loss with no application change and removing operational toil. This source adds the stateful counterpart: for a consensus-backed store, surviving the loss is not the end state — the surviving members are at bare majority and the next loss is read-only. The two are complementary layers, not opposing results.
  - `blog-cncf-geo-distributed-ai-k0smos` Claim 2: that note establishes that a single Kubernetes cluster cannot span geographies and multi-cluster orchestration is required for geo-distributed AI. This source supplies the missing state-store placement rule — one consensus group spanning clusters, with voter placement that preserves a strict majority after any one site or link fails.
- **Contradicts**: none. The apparent tension with `blog-cncf-linkerd-multicluster-federation` Claim 7 (a federated service rebalanced with "zero errors" after a cluster was scaled to zero) is a layer difference, not a contradiction: that note measures stateless request routing, while this source measures a stateful replica set whose write availability depends on surviving quorum. The conditioning variable is whether the workload needs consensus, not whether multi-cluster failover "works."
- **Novel**: quorum placement (2+2+1), strict-majority loss, the read-only degraded state, and control-plane ownership split are all new to the corpus — no existing source note covers quorum design, split-brain avoidance, or multi-cluster state-store failover. The specific transfer to LLM state stores (agent session state, router learning state, vector caches) is our extrapolation, not a claim made by the source.

## Guide Impact

- **Chapter 01 (Incident Response)**: Add a post-failover status rule: after any failover, record the remaining redundancy/quorum headroom as part of incident status, not just "new primary elected." State plainly that "we survived failover" is not "we are healthy" (Claim 7), and that a stateful store can be one further node loss from read-only while every dashboard shows green. Cite this source for the mechanics; label the claim emerging because the source has no measured drill.
- **Chapter 00 (Principles)**: Add the 2+2+1 counterexample (Claims 4–5) to the "redundancy must be reasoned about, not assumed" discussion: four replicas split 2+2 across two sites have no writable side on partition, whereas a fifth voter in a third location yields a 3-of-5 majority. Include the checkable rule — count *voters per failure domain*, not replicas — and flag that the third site becomes quorum-critical even if it holds little data.
- **Chapter 05 (LLM Ops Reliability)**: Do **not** cite this source as AI/LLM evidence; it contains no LLM content. At most, use it as a cross-domain caution if the chapter discusses multi-cluster state stores for agent sessions, router state, or vector caches: the consensus-quorum check applies to those stores only if they are actually consensus-backed, and the source does not test that mapping. No immediate chapter edit is justified on this source alone.

## Extraction Notes

- Read the full article (all sections through the failover architecture and references). Did not follow the Percona operator how-to links (main-site config, interconnect guide, GKE MCS docs) because those are deployment mechanics outside the triage scope; the source's architectural claims are self-contained on the page.
- **Internal inconsistency carried into the note**: the article's prose describes adding two voting Replica Site nodes plus a third non-voting node, while the accompanying snippet shows only two external nodes with `votes: 1` and `votes: 0`. The 2+2+1 arithmetic is stated separately and is internally consistent, but the vote counts in the finalize snippet are not verified by this source (see Concrete Artifact 3).
- **Uncited metric**: the "median ... does not typically exceed 12 seconds" election figure has no citation, sample, or benchmark; treat as vendor/default assertion, not measurement. The authors promise a follow-up chaos-engineering post that would actually measure failure behaviour, so this note's operational claims remain emerging.
- **Vendor context**: Percona-authored/-reviewed content promoting the Percona Operator for MongoDB. The quorum reasoning is technically self-standing, but product-specific claims were not treated as independent evidence.
- **Candidate cross-reference dispositions** (from `miner-related-notes.md`): 
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed: retail/gaming SLO and platform-migration discussion; no quorum or state-store content.
  - `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` — dismissed: multi-agent Kubernetes security platform; its state is agent configuration/policy, not a consensus-backed store with quorum loss.
  - `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` — dismissed: imperative vs declarative change workflows; no replica-set or quorum material.
  - `source-notes/docs-google-sre-reliable-product-launches.md` — dismissed: launch process/checklist; unrelated to state-store failure domains.
  - `source-notes/docs-google-sre-ai-engineering-reliable-operations.md` — dismissed: AI autonomy/actuation governance; no consensus or database-failover claims.
  - `source-notes/blog-cncf-linkerd-multicluster-federation.md` — **cited** (Extends; stateless traffic failover vs stateful quorum headroom).
  - `source-notes/docs-google-sre-simplicity.md` — dismissed: complexity/simplicity economics; no operational quorum content.
  - `source-notes/docs-google-sre-slo-engineering-case-studies.md` — dismissed: SLO adoption case studies; no multi-cluster state-store failover.
  - `source-notes/docs-google-sre-prodcast-03-01.md` — dismissed: SRE methodology and feedback cycles; no quorum material.
  - `source-notes/docs-google-sre-prodcast-03-09-profiling-data.md` — dismissed: profiling/observability data modalities; unrelated to consensus or failover.
- Additional cross-references discovered by searching `source-notes/`: `docs-google-sre-address-cascading-failures` (Claim 15) and `blog-cncf-geo-distributed-ai-k0smos` (Claim 2), both cited above.
