---
source_url: https://www.cncf.io/blog/2026/07/16/running-a-self-hosted-llm-in-kubernetes-with-vllm
source_type: blog-post
title: "Running a self-hosted LLM in Kubernetes with vLLM"
author: "Matt Kereczman (LINBIT)"
date_published: 2026-07-16
date_extracted: 2026-10-11
last_checked: 2026-10-11
status: current
confidence_overall: emerging
issue: "#1648"
---

# Running a self-hosted LLM in Kubernetes with vLLM

> A LINBIT-authored CNCF Member Post walkthrough of deploying a CPU-only vLLM OpenAI-compatible server on Kubernetes, whose transferable content is three operational facts: `--gpu-memory-utilization` governs memory reservation even in a CPU-only deployment (its 92% default caused startup failures; 0.80 gave headroom), model weights belong on a persistent volume mounted at the Hugging Face cache path so restarts and scale-to-zero skip re-download, and readiness is signalled by a `INFO: Application startup complete` log line after a multi-minute cold start, not by pod status.

## Source Context

- **Type**: blog-post (CNCF Member Post — vendor-authored hands-on lab walkthrough; CNCF highlights Kubernetes, llm-d, and Piraeus Datastore).
- **Author credibility**: Matt Kereczman, LINBIT (the vendor behind LINSTOR/DRBD). The post is a reproducible lab walkthrough with full manifests, an exact image, and a curl-verified response, but the vendor's own storage product is the architectural centerpiece, so the storage/DRBD recommendations are product-placement rather than independent evaluation. The vLLM-on-Kubernetes mechanics are vendor-independent and empirical.
- **Scope**: A single-namespace, single-node, CPU-only lab deployment of `meta-llama/Llama-3.2-1B-Instruct` served by vLLM, backed by a LINSTOR CSI StorageClass. Covers prerequisites (gated HF model access), PVC/Secret/Deployment/Service manifests, log-watching, curl testing, and scale-to-zero. Does NOT include GPU device plugins, node selectors, resource limits/requests, autoscaling, throughput/latency/cost measurements, or benchmark data. The 1B CPU-served model is lab scale, not production scale.

## Extracted Claims

### Claim 1: vLLM exposes an OpenAI-compatible REST API, so any existing OpenAI client can be pointed at a self-hosted instance with only a base-URL change
- **Evidence**: Author's description of vLLM's compatibility as the enabler of the hybrid self-host/managed architecture, demonstrated end-to-end by the curl test in the same post.
- **Confidence**: settled
- **Quote**: "Anything that already talks to the OpenAI API (LangChain, LlamaIndex, or your own code that calls the OpenAI SDK) can be pointed at a self-hosted vLLM instance with nothing more than a URL change."
- **Our assessment**: Buy the API-shape premise — vLLM's `/v1/chat/completions` OpenAI compatibility is well established and the post demonstrates it. Caveat: "nothing more than a URL change" is the vendor's framing and overstates operational parity. The `failure-litellm-vllm-embeddings-encoding-format` note shows the same vLLM surface rejecting an OpenAI-shaped payload that a stricter backend validated differently — OpenAI-compatible is a shape, not a guarantee of behavior.

### Claim 2: `--gpu-memory-utilization` governs how aggressively vLLM reserves memory *even on a CPU-only deployment*, and its 92% default caused startup failures in the author's lab; `0.80` provided enough headroom to initialize
- **Evidence**: The author's own testing: the flag is present in the CPU-only `vllm serve` args, and the note records the failure at the default and recovery at 0.80.
- **Confidence**: emerging
- **Quote**: "📝 **NOTE:** Even on a CPU-only deployment, vLLM uses the `--gpu-memory-utilization` flag to govern how aggressively it reserves memory for processing requests. Without this flag, vLLM defaults to 92% of available memory, which caused startup failures in my testing environment. Setting it to 0.80 provided enough headroom in my environment for the engine to initialize successfully."
- **Our assessment**: This is the highest-value operational datapoint and the primary extraction target flagged by the Prospector. The failure mode is real and non-obvious: a flag whose *name* implies GPU scope silently governs CPU deployments, and its default reserves enough memory to block engine initialization on a constrained node. Do not treat `0.80` as a tuned universal value — the author explicitly scopes it to "my environment"; it is a workaround, not a recommended constant. Treat the specific numbers as anecdotal, the mechanism (default reservation can defeat startup; lower the fraction to leave init headroom) as emerging.

### Claim 3: Mounting the Hugging Face cache path (`/root/.cache/huggingface`) on a persistent volume means weights download once and later pod restarts skip the download entirely
- **Evidence**: Explicit mountPath explanation plus the Deployment's `volumeMount` at that path backed by the `vllm-models` PVC.
- **Confidence**: settled
- **Quote**: "The mountPath of the container is `/root/.cache/huggingface`. This is where the vLLM container caches downloaded model weights. By backing this path with a persistent volume, the model is downloaded from Hugging Face only once, and later pod restarts skip the download entirely because they will persist on the LINSTOR-provided persistent storage."
- **Our assessment**: Buy this as a concrete, reproducible cold-start mitigation. The mechanism is generic and storage-vendor-independent: the download cache lives at a fixed container path, so persisting that path decouples pod lifecycle from weight-fetch cost. The specific PVC backing (LINSTOR) is incidental to the pattern.

### Claim 4: Scaling the Deployment to zero preserves the PVC and its cached weights, so scaling back up skips the re-download
- **Evidence**: The "Pausing the deployment" section documents `--replicas=0` then `--replicas=1` and explicitly states the PVC and weights are retained.
- **Confidence**: settled
- **Quote**: "💡 **TIP:** Scaling the deployment to zero keeps the PVC and cached model weights intact. The model will not need to be re-downloaded when you scale the deployment back up."
- **Our assessment**: This is the scale-to-zero corollary of Claim 3 and a practical pause/troubleshoot pattern: the PVC is the state boundary, so a zero-replica Deployment still costs storage but avoids re-fetch latency on resume. Directly relevant to cold-start/SLO design and cost trade-offs for self-hosted inference (idle storage cost vs. re-download time).

### Claim 5: First startup takes minutes (weights download plus engine init), and the readiness signal is the `INFO: Application startup complete` log line — a pod can be running long before it can serve
- **Evidence**: The "Watching the logs" section states the first start takes a few minutes, needs ~2.5GB of weights plus engine init, and names the log line to wait for before testing.
- **Confidence**: emerging
- **Quote**: "The first startup takes a few minutes. vLLM needs to download the model weights from Hugging Face (roughly 2.5GB for this model) and initialize the engine."
- **Quote**: "After you see something such as INFO: Application startup complete, you are ready to test."
- **Our assessment**: The readiness-by-log-line detail (rather than container/pod status) is operationally important but only anecdotal at this scale: it is stated prose, not a probe configuration, and the post provides no timing measurements for probes/timeouts. The transferable lesson is that cold-start duration for self-hosted inference is dominated by weight fetch + engine init, so readiness probes and SLOs must budget for it; the exact "few minutes" figure is lab-specific.

### Claim 6: Meta Llama weights are gated on Hugging Face, requiring an access request and a read-scoped token wired into the container via `secretKeyRef`
- **Evidence**: The Prerequisites list (request access, create a read token) and the Deployment's `HF_TOKEN` env sourced from the `hf-token-secret` Secret.
- **Confidence**: settled
- **Quote**: "Meta Llama models are gated on Hugging Face, meaning you need to request access before you can download them."
- **Our assessment**: A real onboarding/supply-chain prerequisite for self-hosting gated models: the deployment cannot bootstrap without an out-of-band access grant, and the token must be injected as a Secret. Worth recording because "just deploy the server" assumes a credential/entitlement step that a managed-API path does not expose.

### Claim 7: The example PVC requests a thin-provisioned, two-replica LVM volume via the `linstor-csi-lvm-thin-r2` StorageClass, at 50Gi ReadWriteOnce
- **Evidence**: The PVC manifest and the section text describing the StorageClass's provisioned volume.
- **Confidence**: settled
- **Quote**: "The PVC uses the `linstor-csi-lvm-thin-r2` storage class, which provisions a thin-provisioned LVM volume with two replicas across the cluster."
- **Our assessment**: The manifest is concrete and reproducible as an *example*, but the StorageClass is the vendor's product and is not validated here at scale. Treat the shape (a StorageClass + RWO + sized PVC for model weights) as the transferable part; treat the specific class and replica count as product-placement. ReadWriteOnce is worth noting: a single-writer access mode constrains how replicas can share the same weight volume.

### Claim 8: The reference deployment serves a 1B instruction-tuned model on CPU via the `vllm-cpu-release-repo` image, verified end-to-end by a curl request that returns an OpenAI-format response with token usage
- **Evidence**: The Deployment uses `public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:latest` and the model `meta-llama/Llama-3.2-1B-Instruct`; the curl test returns `finish_reason: stop` and a `usage` block (15 prompt / 9 completion / 24 total tokens).
- **Confidence**: settled
- **Quote**: "The model used in this blog is `meta-llama/Llama-3.2-1B-Instruct`, a small but capable model from Meta that has been fine-tuned to follow user instructions."
- **Our assessment**: The end-to-end curl with a real token-usage response is what makes this empirical rather than pure marketing — the server actually serves. But the evidence is deliberately lab scale: one 1B model, CPU, single replica, no concurrency, no latency/throughput numbers. It establishes the pattern works, not that it is production-ready.

### Claim 9 (vendor claim): The post attributes durability to LINSTOR/DRBD replication — the volume survives node failure and is "not a single point of failure"
- **Evidence**: Author prose describing LINSTOR as built on DRBD with replicated block storage, and the conclusion's single-point-of-failure claim.
- **Confidence**: anecdotal
- **Quote**: "Replicated storage is a good fit for storing large model weight files that need to survive pod restarts and node failures."
- **Quote**: "Caching the model weights on a LINSTOR volume means that pod restarts are fast, and the DRBD-backed replication means that the volume is not a single point of failure."
- **Our assessment**: Do not lift this as a general pattern. The central architectural pillar (LINSTOR/Piraeus CSI, `linstor-csi-lvm-thin-r2`, DRBD replication) is the vendor's own product, and the "not a single point of failure" conclusion is asserted, not tested — the lab is single-node, so node-failure survival is not demonstrated. The transferable content is "persist weights on replicated storage rather than the container layer"; the vendor recommendation behind it stays a product-placement claim.

### Claim 10: Self-hosting is positioned as a complementary pattern to managed APIs for cost predictability at high volume, latency control, and data-residency, with an inference router as the hybrid next step
- **Evidence**: The introduction's rationale and the conclusion's llm-d suggestion.
- **Confidence**: anecdotal
- **Quote**: "Self-hosting is a complementary option that some teams choose for reasons such as cost predictability at high request volumes, more control over latency, and controlling data-residency to meet contractual or regulatory requirements."
- **Quote**: "If you are building toward hybrid AI, a natural next step is to layer in an inference router that dispatches requests between the local deployment and a managed API based on cost, latency, or capability requirements."
- **Our assessment**: The self-vs-managed argument is generic and adds little beyond framing; the guide already treats managed/self-hosted routing as a cost/attribution question. Keep it as context, not as a new claim. The llm-d pointer is a forward-looking suggestion ("directions for further exploration rather than configurations covered in this lab") and is unexercised here.

## Concrete Artifacts

**PVC + Hugging Face token Secret (verbatim from source, command block):**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: vllm-models
spec:
  storageClassName: linstor-csi-lvm-thin-r2
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: Secret
metadata:
  name: hf-token-secret
type: Opaque
stringData:
  token: "REPLACE_WITH_YOUR_TOKEN"
```

**vLLM Deployment + Service (verbatim from source; the CPU image and the memory-utilization arg are the two substantive knobs):**
```yaml
VLLM_IMAGE=public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:latest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: vllm
  template:
    metadata:
      labels:
        app.kubernetes.io/name: vllm
    spec:
      containers:
      - name: vllm
        image: $VLLM_IMAGE
        command: ["/bin/sh", "-c"]
        args: [
          "vllm serve meta-llama/Llama-3.2-1B-Instruct --gpu-memory-utilization 0.80"
        ]
        env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-token-secret
              key: token
        ports:
          - containerPort: 8000
        volumeMounts:
          - name: llama-storage
            mountPath: /root/.cache/huggingface
      volumes:
      - name: llama-storage
        persistentVolumeClaim:
          claimName: vllm-models
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-server
spec:
  selector:
    app.kubernetes.io/name: vllm
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

**In-cluster verification request (verbatim from source):**
```bash
curl http://vllm-server.default.svc.cluster.local:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.2-1B-Instruct",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

**Observed response (verbatim from source):**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 9,
    "total_tokens": 24
  }
}
```

**Log-watch and pause/resume commands (verbatim from source; the rendered `--replicas**=**0` bolding is a markdown artifact, the intended command is `--replicas=0`):**
```
kubectl logs -f deployment/vllm-server
kubectl scale deployment vllm-server --replicas=0
kubectl scale deployment vllm-server --replicas=1
```

## Cross-References

- **Corroborates**:
  - `failure-litellm-vllm-embeddings-encoding-format.md` — **Claim 1** ("A gateway fix that stops one provider's SDK from injecting a default can break a stricter sibling provider by passing an explicit `None` instead of omitting the parameter") and **Claim 2** ("`Some providers treat omitted and explicitly-null parameter values differently`"). Both notes center on the same vLLM operator surface. This note's Claim 1 states the positive premise — vLLM is an OpenAI-compatible backend you can point existing OpenAI clients at — and the LiteLLM incident note is the failure counterpart: because vLLM is *compatible in shape but strict in validation*, an OpenAI-shaped payload can still be rejected. Together they establish "OpenAI-compatible vLLM is a real drop-in *and* a distinct validation contract." Different subsystems (serving bootstrap vs. gateway→backend embeddings payload), so this is corroboration on the parity theme, not on the same claim.

- **Contradicts**: None. No existing note claims vLLM's memory-reservation behavior, GPU-only scope for `--gpu-memory-utilization`, or anything about weight-cache persistence / readiness signalling. Verified against `CONTRADICTIONS.md` (no open `C-NNN` entries). No contradiction issue filed.

- **Extends**:
  - `blog-cncf-understanding-dynamic-resource-allocation-kubernetes.md` — **Claim 6** ("Capacity-based selection with CEL can produce a Pending Pod when no device meets the threshold") and **Claim 5** (rolling-update claim-retention fallback). That note covers GPU/accelerator capacity and allocation mechanics on the Kubernetes substrate; this note adds the adjacent capacity-pressure failure mode on the *same* substrate from the serve side — a memory-reservation default (92%) that blocks engine startup on a constrained node rather than a scheduling rejection. Both are "the scheduler/node can't give the workload what it asks for," one surfacing as `FailedScheduling`, the other as an engine that won't initialize. Related axis: Kubernetes capacity for inference workloads; not a corroboration of DRA mechanics.

- **Novel**: First source note in the corpus covering:
  1. **Self-hosted vLLM serving bootstrap on Kubernetes** — no existing note covers deploying/serving an OpenAI-compatible model server on-cluster (the only other vLLM note is a gateway→backend payload incident).
  2. **`--gpu-memory-utilization` governing a CPU-only deployment** — a flag whose name implies GPU scope but whose default can silently defeat CPU engine startup; captured with the failure symptom and workaround.
  3. **Weights-on-PVC at the Hugging Face cache path as a cold-start mitigation**, including the scale-to-zero-preserves-cache corollary.
  4. **Readiness as a log line after a multi-minute weight-fetch + engine-init cold start** for self-hosted inference.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — Cost, capacity, and fallback patterns)**: Add a self-hosted-serving capacity note under the capacity-planning material (near guide/05-llm-ops-reliability.md:970, "Cost, capacity, and fallback patterns"). Concrete guidance: (a) size memory reservation deliberately for inference engines — do not assume a `--gpu-memory-utilization`-style flag is inert on CPU; its default can reserve enough to block startup, so lower the fraction to leave initialization headroom [source: blog-cncf-running-self-hosted-llm-kubernetes-vllm, Claim 2]; (b) persist model weights on a volume at the engine's download-cache path so pod restarts and scale-to-zero skip the multi-GB re-fetch [Claim 3, Claim 4]; (c) budget readiness/SLOs for a cold start dominated by weight fetch + engine init, and treat "pod running" as distinct from "engine ready" [Claim 5]. Also note the gated-model entitlement prerequisite before a deployment can bootstrap [Claim 6].

- **Chapter 05 (Provider parity in the shared forwarding path)**: The existing section (guide/05-llm-ops-reliability.md:343) already warns that a shared OpenAI-compatible forwarding path is not behaviorally uniform. This source supplies the *self-hosted* side of that parity surface: vLLM is a drop-in by API shape [Claim 1] but a distinct validation contract. Recommend a one-line cross-link noting that a self-hosted vLLM backend belongs in the "test the non-default provider with exact-wire assertions" rule already present there.

- **Chapter 02 (Observability / readiness)**: Add a readiness-probe example: for a self-hosted inference pod, liveness/readiness cannot key off pod status alone — the engine emits `INFO: Application startup complete` only after weights download and engine init complete [Claim 5]. Recommend the guide note ready-gating on that signal (or an equivalent health endpoint) with probe `initialDelaySeconds`/`failureThreshold` sized for the cold-start window.

## Extraction Notes

- Deep-read of the full CNCF Member Post article (single page), including all manifests, the log-watch step, the curl test, the observed JSON response, and the pause/resume conclusion. No paywall; fully readable. No substantive sub-pages followed — the article links only to the Piraeus Operator repo and vLLM K8s docs (used by the author as the manifest source), neither of which adds claims beyond the post itself.
- Per the Prospector triage, extraction is scoped to the three primary targets (memory-utilization startup failure, PVC weight caching, readiness/cold-start) plus supporting claims. The vendor's storage/DRBD/DR recommendations are recorded as an explicit vendor claim (Claim 9) but **not** promoted to a general pattern, and the generic self-vs-managed argument is kept as context (Claim 10) rather than elevated.
- All quotes copied character-for-character from the rendered page, including the emoji-prefixed NOTE/TIP/IMPORTANT blocks. Two markdown normalizations: (1) the `kubectl scale ... --replicas**=**0` text renders with literal bold markers in the fetch and is reproduced in the artifact block as the intended `--replicas=0` with a note; (2) YAML command heredocs are shown without the surrounding `cat <<EOF | kubectl apply -f -` wrapper for readability, but the resource bodies are unmodified.
- `confidence_overall: emerging` — the deployment mechanics are reproducible and partly empirical (real manifests, real curl/token-usage response), but the central operational datapoint (Claim 2) and the readiness timing (Claim 5) are single-lab, environment-specific anecdotes; the durability claim (Claim 9) is untested vendor assertion; and the whole source is 1B-model, single-node, CPU lab scale with no production metrics.
- Cross-reference candidates from `miner-related-notes.md` not cited above, each dismissed in one line (lexical retrieval returned SRE prodcast / LiteLLM-param / Langfuse notes, none on self-hosted serving):
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — SLOs in retail/gaming; no inference-serving content.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — imperative vs declarative config; Kubernetes is declarative but the topic (reconciliation model) does not touch this note's claims.
  - `docs-google-sre-reliable-product-launches.md` — launch checklists; unrelated.
  - `docs-langfuse-roadmap.md` — Langfuse observability roadmap; unrelated.
  - `docs-google-sre-eliminating-toil.md` — toil definition/measurement; unrelated.
  - `docs-google-sre-team-lifecycles.md` — SRE team formation; unrelated.
  - `docs-google-sre-prodcast-03-01.md` — SRE methodology; unrelated.
  - `docs-langfuse-compatibility.md` — Langfuse version compatibility; unrelated.
  - `docs-litellm-completion-input-params.md` — LiteLLM completion parameter gates; adjacent to provider-param semantics but no overlap with this note's serving/capacity claims.
  - `docs-langfuse-sdk-overview.md` — Langfuse SDK instrumentation; unrelated.
- The two cited cross-references (`failure-litellm-vllm-embeddings-encoding-format`, `blog-cncf-understanding-dynamic-resource-allocation-kubernetes`) were found by searching `source-notes/` directly; both were re-read and their claim numbers verified against the cited content before writing (MINER.md §4b). No contradiction found.
