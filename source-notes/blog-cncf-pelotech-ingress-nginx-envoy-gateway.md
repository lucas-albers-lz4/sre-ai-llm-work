---
source_url: https://www.cncf.io/blog/2026/05/25/zero-downtime-migration-from-ingress-nginx-to-envoy-gateway
source_type: blog-post
title: "Zero-Downtime migration from ingress NGINX to Envoy Gateway"
author: "Andrew Katsikas, Pelotech"
date_published: "2026-05-25"
date_extracted: "2026-10-27"
last_checked: "2026-10-27"
status: current
confidence_overall: settled
issue: "#1916"
---

# Zero-Downtime migration from ingress NGINX to Envoy Gateway

> Weighted DNS with ExternalDNS/Route 53 (swap aws-weight between coexisting Ingress and HTTPRoute) avoids the DNS TTL/teardown race; rollback is a weight swap and validates zero-downtime migration from Ingress NGINX to Envoy Gateway.

## Source Context

- **Type**: blog-post (practitioner case study, CNCF blog)
- **Author credibility**: Pelotech engineers (Andrew Katsikas) writing about a customer migration on AWS; vendor context noted but technical details are concrete.
- **Scope**: Covers controller selection (Envoy Gateway chosen among CNCF options), testing in Kind/Goldilocks with both controllers side-by-side, failure of naive cutover (DNS TTL vs teardown), weighted DNS solution via ExternalDNS/Route 53, operational gotchas (ArgoCD prune/manual deletion), multi-namespace hostname ownership pre-Gateway API 1.5 (ListenerSet as fix), and validation via polling script. Does not cover in-depth Gateway API internals beyond migration mechanics; closing paragraph is a services pitch (discarded).

## Extracted Claims

### Claim 1: Naive cutover dropped requests due to DNS TTL vs resource teardown
- **Evidence**: Observed during first migration on internal Goldilocks instance; polling script logged HTTP status codes over time showing downtime window.
- **Confidence**: settled
- **Quote**: "When we reviewed the log file, however, there was a window of downtime during the cutover. The culprit was DNS. When you swap an A record, you are at the mercy of the TTL that was set on the old record. Until that TTL expires, customers are still resolving to the old address. If the old Ingress is gone, those requests go nowhere."
- **Our assessment**: Clear sequencing failure - move traffic mechanism (record change) and teardown of old path must be decoupled from DNS propagation; this is the core gotcha most guides skip.

### Claim 2: Weighted DNS via ExternalDNS/Route 53 enables zero-downtime cutover by swapping weights
- **Evidence**: Ran Ingress (weight 100) and HTTPRoute (weight 0) simultaneously for same hostname via `external-dns.alpha.kubernetes.io/aws-weight`; swapped to Ingress 0 / HTTPRoute 100 with no failed requests observed by polling script.
- **Confidence**: settled
- **Quote**: "Instead of a hard cutover, we could run the Ingress and the HTTPRoute simultaneously, each registered with the same hostname but with different weights. By setting the Ingress weight high and the HTTPRoute weight to zero, the HTTPRoute would be live but receive no traffic, effectively inert. Once we were confident everything stood up correctly, we could swap the weights and move traffic over without creating or deleting any DNS records."
- **Our assessment**: Controller-agnostic pattern; decouples traffic shifting from record creation/deletion and makes rollback trivial (symmetric weight swap).

### Claim 3: Rollback is symmetric weight swap with no redeploy/recreate
- **Evidence**: Described as operational property of weighted DNS approach.
- **Confidence**: settled
- **Quote**: "If anything looks wrong post-cutover, swap the weights back. There is no DNS record to recreate, no resource to redeploy, and the rollback propagates the same way the cutover did."
- **Our assessment**: Strong operational benefit; important for risk mitigation in production migrations.

### Claim 4: ArgoCD prune disabled requires manual deletion of old Ingress
- **Evidence**: Observed in migration ("because we manage our clusters with ArgoCD and do not use the prune option, the old Ingress resource did not get cleaned up automatically. We had to delete it by hand through Argo.").
- **Confidence**: emerging
- **Quote**: "There was one manual step worth noting: because we manage our clusters with ArgoCD and do not use the prune option, the old Ingress resource did not get cleaned up automatically. We had to delete it by hand through Argo."
- **Our assessment**: GitOps-specific operational gotcha that must be accounted for in migration plan/runbook.

### Claim 5: Pre-Gateway API 1.5 forces hostname declaration at both Gateway and HTTPRoute (multi-namespace separation of concerns)
- **Evidence**: Multi-namespace environments require hostnames at Gateway (infra-owned) and HTTPRoute (app-owned), pulling app concerns into infra-owned resource.
- **Confidence**: emerging
- **Quote**: "The challenge is that prior to Gateway API 1.5, hostnames must be defined at both the Gateway level and the HTTPRoute level. The Gateway is a cluster-level resource, typically owned by a platform or infrastructure team. The HTTPRoute is an application-level resource, owned by developers. [...] When hostname configuration lives at the Gateway level, you are pulling an application concern up into infrastructure. That breaks exactly the separation of concerns that Gateway API is supposed to deliver."
- **Our assessment**: Real design tension; ListenerSet (Gateway API 1.5) addresses it but controller support was still landing at time of writing (Envoy Gateway RC).

### Claim 6: Envoy Gateway selected on CNCF alignment, annotation parity, mTLS/request buffering
- **Evidence**: Evaluated via ing-switch and comparison against Traefik/NGINX Gateway Fabric/Istio/Higress; CNCF status and internal alignment weighed heavily.
- **Confidence**: anecdotal
- **Quote**: "Beyond CNCF status, we cared about a few specific things: - Annotation parity with what we were already using - Support for real production requirements like mTLS and request buffering - A controller that honored Gateway API’s model of dedicated resources, rather than a sprawl of annotations [...] Envoy Gateway came out on top. It is a CNCF project, the spec is solid, and the CNCF runs it on its own infrastructure."
- **Our assessment**: Selection rationale is pragmatic; useful context but not directly the migration pattern.

### Claim 7: Cheap validation via polling script (tee-logged status codes) provides reviewable evidence
- **Evidence**: Simple shell script polling endpoint piped to terminal and log file with tee to monitor cutover.
- **Confidence**: emerging
- **Quote**: "To monitor the cutover, we wrote a simple shell script that polled our endpoint and piped the output to both the terminal and a log file using tee. This gave us a clear, reviewable record of HTTP status codes throughout the process."
- **Our assessment**: Low-cost, effective validation technique for cutover confidence.

## Concrete Artifacts

```yaml
# Ingress (start)
external-dns.alpha.kubernetes.io/aws-weight: "100"

# HTTPRoute (start, inert)
external-dns.alpha.kubernetes.io/aws-weight: "0"

# Swap for cutover
# Ingress
external-dns.alpha.kubernetes.io/aws-weight: "0"
# HTTPRoute
external-dns.alpha.kubernetes.io/aws-weight: "100"
```
*(Attributed: CNCF blog post "Zero-Downtime migration from ingress NGINX to Envoy Gateway", Pelotech, showing ExternalDNS + Route 53 weighted records.)*

```text
# Validation pattern (described)
# Simple polling script piped to tee for logged HTTP status codes during cutover
curl <endpoint> ... | tee cutover.log
```
*(Attributed: described in article as monitoring method.)*

## Cross-References

- **Corroborates**: 
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` (Claim 12) — weighted-DNS canary pattern (0%→1%→5% via weighted CNAMEs) for migration with bounded blast radius; this note extends with Kubernetes/ExternalDNS annotation-level implementation and the specific TTL/teardown failure mode plus rollback semantics.
- **Contradicts**: none identified.
- **Extends**:
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — adds concrete controller/annotations (ExternalDNS + Route 53 `aws-weight`), failure analysis (delete old Ingress before DNS TTL expires), GitOps pruning gotcha, and Gateway API multi-namespace/ListenerSet nuance.
- **Novel**: Specifics of Ingress NGINX → Envoy Gateway migration using ExternalDNS weighted records; ListenerSet separation-of-concerns issue pre-1.5 with controller lag; ing-switch evaluation usage; cheap polling validation during DNS-weight cutover.

## Guide Impact

- **Chapter 01 (Incident Response)**: Add concrete example of sequencing failure (DNS TTL vs resource teardown) and symmetric rollback via weight swap; emphasize "validate DNS propagation before tearing down old path".
- **Chapter 05 (LLM Ops Reliability / Release Engineering)**: Document weighted-DNS cutover as a controller-agnostic zero-downtime pattern for control-plane/routing migrations; include ExternalDNS annotation example and GitOps prune gotcha.
- **Chapter 02 (Observability)**: Recommend cheap poller (tee-logged status codes) as reviewable evidence during cutover rather than assuming success.
- **Chapter 00 (Principles)**: Note infra/app separation of concerns tension in Gateway API pre-1.5 (hostnames at Gateway+HTTPRoute) and ListenerSet as intended fix.

## Extraction Notes

- Read full article deeply (including controller comparison table, testing narrative, production gotchas). Skipped vendor CTA ("Reach out to us today") per triage guidance.
- No paywall/dead links encountered. Used webfetch content.
- Cross-referenced against prodcast 03-07 weighted-DNS mention; confirmed extends rather than duplicates (different context/implementation details).
- All quotes copied verbatim from fetched content.
