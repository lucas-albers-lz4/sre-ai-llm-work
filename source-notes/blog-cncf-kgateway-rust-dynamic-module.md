---
source_url: https://www.cncf.io/blog/2026/05/15/extending-ai-gateways-with-rust-custom-transformations-in-kgateway
source_type: blog-post
title: "Extending AI gateways with Rust: Custom transformations in kgateway"
author: "Michael Uzukwu, kgateway Contributor"
date_published: "2026-05-15"
date_extracted: "2026-11-07"
last_checked: "2026-11-07"
status: current
confidence_overall: emerging
issue: "#1966"
---

# Extending AI gateways with Rust: Custom transformations in kgateway

> A kgateway contributor's hands-on lab for replacing the built-in Rust
> transformation filter with a custom Envoy dynamic module, which surfaces a
> version-coupling failure class (control plane / Envoy / Rust SDK / toolchain
> must match), a controller-reconciliation gotcha (out-of-band Envoy image edits
> are reverted; inject through `GatewayParameters` + `parametersRef`), and a
> non-discriminating "proof" that the module loaded (the response header it
> checks is also set by the `TrafficPolicy`).

## Source Context

- **Type**: blog-post (hands-on tutorial, CNCF blog, kgateway Contributor).
- **Author credibility**: Michael Uzukwu is a kgateway contributor writing a
  vendor-community lab on kgateway's own extension mechanism. Credible for *how
  the mechanism is wired* (manifests, Dockerfile, versions, observed errors) in
  the stated `kind` environment; not independent production evidence. The lab is
  a single-node local cluster with a mock LLM (`httpbun`), no production
  telemetry, no failure report from a real estate.
- **Scope**: Covers building a custom Envoy dynamic module in Rust, packaging it
  into an Envoy image, deploying it through kgateway on `kind`, injecting the
  custom image via `GatewayParameters`, routing an OpenAI-compatible path to a
  mock LLM with `URLRewrite`, adding response headers with a `TrafficPolicy`, and
  a troubleshooting table. Does NOT cover: production deployment, capacity or
  latency, upgrade testing across kgateway releases, multi-provider behavior, or
  a discriminating test that the module actually executed (see Claim 10).
- **Evidence strength**: Tutorial-grade. The mechanics are concrete and
  reproducible; the reliability conclusions are the author's lab experience, not
  measured production outcomes. `confidence_overall` is therefore `emerging`.

## Extracted Claims

### Claim 1: A custom Envoy dynamic module is the extension path when the gateway's built-in policies and templating do not cover a required behavior; kgateway's built-in `rustformation` filter can be replaced outright
- **Evidence**: The article opens with the "what about the ones they don't
  cover?" framing and states that the lab replaces kgateway's default
  `rustformation` (Jinja templating) module with a custom one.
- **Confidence**: settled (mechanism described and demonstrated)
- **Quote**: "kgateway already includes a built-in rustformation filter that supports Jinja templating. This lab extends that pattern by replacing the default module with a custom one – useful when the built-in templating isn’t sufficient for your specific use case."
- **Our assessment**: The correct decision boundary is "built-in policy cannot
  express the behavior", not "we prefer Rust". Replacing the default module buys
  arbitrary Envoy-API power at the cost of owning a compiled artifact and its ABI
  coupling (Claims 2-3). This is the extension-of-last-resort pattern.

### Claim 2: Extending through a custom module couples three independently versioned surfaces — the kgateway control plane, the Envoy data plane, and the Rust module/SDK/toolchain — and kgateway v2.3 introduced breaking changes to the Rust dynamic-module system
- **Evidence**: The v2.3 note names the tested control-plane version
  (`v2.3.0-rc.1`) and states that v2.3 breaks the Rust dynamic-module system;
  the Dockerfile pins the Envoy base image to `v1.36.4` and the builder to
  `rust:1.88`; the lab installs Gateway API CRDs `v1.4.0`.
- **Confidence**: settled for the stated versions; emerging as a general rule
  (one lab, no cross-version matrix)
- **Quote**: "Note on kgateway v2.3: This lab was built and tested with kgateway v2.3.0-rc.1. kgateway v2.3 introduces breaking changes to the Rust dynamic module system. If you’re using an older version, refer to the migration guide in the kgateway repository. The custom header logic (X-Custom-Transformed: true) remains valid and has been ported to the new structure."
- **Our assessment**: The highest-value ops claim in the post. A control-plane
  minor bump is not a drop-in for a custom module — it can invalidate the
  compiled `.so`. Operators should add the extension ABI to the release-pinning
  matrix and treat kgateway line moves as breaking until the module is rebuilt
  and re-tested against the new data plane.

### Claim 3: The author's own conclusion is that the SDK must match Envoy exactly and the Rust toolchain must satisfy the module's dependencies, so "one version mismatch and everything breaks"
- **Evidence**: The "Final thoughts" section lists three lessons; lesson 1 is
  the version-coupling rule, backed by the concrete pins in Claims 2 and 4.
- **Confidence**: emerging (first-person lab experience; no tested version
  matrix or failure catalogue)
- **Quote**: "The SDK must match Envoy exactly. The Rust version must support your dependencies. One version mismatch and everything breaks."
- **Our assessment**: Directionally credible and consistent with how dynamic
  modules are loaded, but it is not a tested compatibility table. Operational
  translation: pin and record the quadruple (kgateway, Envoy, dynamic-module SDK,
  Rust toolchain) per image, and build/re-test the module whenever any leg moves.

### Claim 4: The article's prerequisites contradict themselves on the minimum Rust version — the install list says Rust 1.85+ while the body says the module "requires Rust 1.88 or later", and the Dockerfile resolves the conflict to `rust:1.88`
- **Evidence**: The "Before you start" list says `Rust (1.85+)`, then an
  "Important" note raises the floor to 1.88; the multi-stage Dockerfile's
  builder is `rust:1.88`.
- **Confidence**: settled (the document literally states both)
- **Quote**: "Rust (1.85+) – Builds the Rust module (optional; you can build inside Docker)"
- **Quote**: "The Rust module requires Rust 1.88 or later. If you encounter build errors with older versions, update your Dockerfile to use rust:1.88."
- **Our assessment**: The internal contradiction is itself evidence for the
  version-drift failure class: a reader who follows the prerequisites list builds
  with 1.85 and hits exactly the build errors the body warns about. Treat the
  Dockerfile pin, not the prose prerequisites, as the executable contract.

### Claim 5: The kgateway controller reverts direct edits to the Envoy data-plane image; the supported extension-injection path is a `GatewayParameters` object referenced from the Gateway's `spec.infrastructure.parametersRef`
- **Evidence**: Part 6 is titled around deploying the custom image "without
  kgateway's controller reverting changes" and wires the image through a
  `GatewayParameters` resource plus a JSON patch adding
  `/spec/infrastructure/parametersRef`.
- **Confidence**: settled for this controller (documented workaround);
  emerging as a generalization
- **Quote**: "To deploy your custom image without kgateway’s controller reverting changes, use GatewayParameters:"
- **Our assessment**: A concrete instance of the controller-owns-its-workload
  reconciliation gotcha: an out-of-band edit to a controller-managed object is
  drift and gets reconciled away. The durable rule is to express the change
  through a first-class parameter resource (the source of truth), not by editing
  the generated workload directly. This is the deployment-time analog of GitOps
  drift correction.

### Claim 6: For a kind-loaded local image, the working `GatewayParameters` shape is `registry: ""`, the local repository/tag, and `pullPolicy: IfNotPresent`, paired with `kind load docker-image`
- **Evidence**: The `GatewayParameters` manifest uses an empty registry with the
  comment "Empty = use local images"; the troubleshooting table maps
  `ImagePullBackOff` to the same fix.
- **Confidence**: settled (concrete manifest + troubleshooting row in the lab)
- **Quote**: "Load image with kind load docker-image and set pullPolicy: IfNotPresent and registry: “” in GatewayParameters"
- **Our assessment**: A distinct failure mode from Claim 5: reconciliation is
  about *which object owns the image*; `ImagePullBackOff` is about *whether the
  cluster can see the image at all*. Both fire on the same custom-image change,
  so a runbook needs both checks in order.

### Claim 7: The `filter_config` extension config uses a protobuf wrapper that is documented but easy to miss, and the author spent hours diagnosing the resulting error
- **Evidence**: Lesson 2 of the "Final thoughts" section states the format is
  non-obvious and names the documentation as the eventual source of the fix.
- **Confidence**: anecdotal (one author's debugging time; no error text shown)
- **Quote**: "The filter_config format is not obvious. The protobuf wrapper is documented, but easy to miss. I spent hours on this error before finding the solution in the docs."
- **Our assessment**: A runbook-style lesson: check the config wrapper type
  before debugging module logic. It also signals that extension config is less
  obvious than the core Gateway API CRDs — a schema-surface risk when the custom
  module is handed to another team.

### Claim 8: An `HTTPRoute` `URLRewrite` filter can remap the OpenAI-standard client path (`/v1/chat/completions`) to the backend's native path (`/llm/chat/completions`), preserving client API parity
- **Evidence**: The `httpbun-route` manifest matches `/v1/chat/completions` and
  replaces the full path with `/llm/chat/completions`; the article explains why.
- **Confidence**: settled (concrete, applied manifest)
- **Quote**: "httpbun expects the path /llm/chat/completions, but the OpenAI API standard uses /v1/chat/completions. The URLRewrite filter transparently transforms the path so clients can use the standard endpoint."
- **Our assessment**: Path parity is the path-dimension counterpart to parameter
  normalization in the shared forwarding path: the gateway silently rewrites the
  contract so clients keep the standard endpoint. Good for compatibility, but it
  means the client-visible path and the backend-observed path differ — exact
  wire/path assertions must account for the rewrite.

### Claim 9: A mock LLM (`httpbun`) deployed in-cluster lets the full gateway path — including the custom module — be exercised with no provider keys and zero spend
- **Evidence**: The architecture routes `curl → kgateway-proxy (Envoy) → Rust
  Module (.so) → httpbun (mock LLM) → response`; `httpbun` is deployed as a
  Kubernetes Deployment/Service and the author cites cost and focus as the
  benefit.
- **Confidence**: settled (demonstrated in the lab)
- **Quote**: "Starting with a mock LLM saves time and money. httpbun let me focus on the gateway, not the AI provider. I could test everything locally without worrying about API keys or costs."
- **Our assessment**: Higher fidelity than an in-process SDK stub because the
  request actually traverses Envoy and the module. But it is still a test
  double: what it validates depends on how faithfully it mimics the real backend
  (OpenAI-shaped responses, path, headers). Useful for mechanism tests, not for
  provider-parity claims.

### Claim 10: The article presents the `X-Custom-Transformed: true` response header as proof the Rust module executed, but the same header is also set by the `TrafficPolicy`, so the check is non-discriminating
- **Evidence**: The Rust snippet sets `X-Custom-Transformed` in
  `on_response_headers` and the article says it "provid[es] visible proof"; the
  Part 7 `TrafficPolicy` also sets `X-Custom-Transformed: true` (and
  `X-Smart-Header`) on the same route.
- **Confidence**: settled (the collision is visible from the article's own
  manifests)
- **Quote**: "This single line adds X-Custom-Transformed: true to every response, providing visible proof that your custom module is loaded and executing."
- **Quote**: "Look for X-Custom-Transformed: true – this proves your Rust module is working!"
- **Our assessment**: The test passes even if the module never loads, because
  the `TrafficPolicy` sets the identical header. A discriminating probe must use
  a value only the module can emit (or remove the header from the
  `TrafficPolicy`). This is the most important caveat for anyone reusing the lab
  as a verification recipe; it is a "green check that cannot fail" in
  miniature, and it should not be cited as evidence that the dynamic module ran.

### Claim 11: The post's troubleshooting table maps concrete, reproducible failure modes for the lab
- **Evidence**: The table lists `ImagePullBackOff` (load image + `pullPolicy` +
  empty registry), Rust version mismatch (`rust:1.88`), controller reverts
  (`GatewayParameters`), `404 page not found` (`URLRewrite`), and `BackendRef`
  port error (remove `port` when using `kind: Backend`).
- **Confidence**: settled (author-observed lab errors)
- **Quote**: "Remove port from backendRefs when using kind: Backend"
- **Our assessment**: Useful as a lab runbook, but these are `kind`-local and
  tutorial-path errors. Only the controller-revert and version-mismatch rows
  generalize to production; the image-loading and `BackendRef` rows do not.

### Claim 12: The closing section says "agentgateway supports all of these" even though the entire article is about kgateway — an apparent attribution artifact
- **Evidence**: The "Next steps: Production and real LLMs" section ends by
  naming agentgateway rather than kgateway; all preceding content targets
  kgateway.
- **Confidence**: settled (the text says it)
- **Quote**: "agentgateway supports all of these through its policy CRDs."
- **Our assessment**: Almost certainly a leftover from another draft; do not
  propagate the claim that agentgateway is the production continuation of this
  kgateway lab. It is recorded here only so the Smith does not lift it as fact.

## Concrete Artifacts

### Request flow (verbatim from the post)

```
curl → kgateway-proxy (Envoy) → Rust Module (.so) → httpbun (mock LLM) → response
```

Attribution: CNCF blog post, "Architecture overview".

### Multi-stage Dockerfile packaging the module into Envoy (verbatim from the post)

```dockerfile
# Stage 1: Build the Rust module
FROM rust:1.88 AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y clang

COPY rust/ ./rust/
WORKDIR /build/rust/rustformations
RUN cargo build --release

# Stage 2: Final Envoy image
FROM envoyproxy/envoy:v1.36.4

COPY --from=builder /build/rust/rustformations/target/release/librust_module.so /usr/local/lib/
ENV ENVOY_DYNAMIC_MODULES_SEARCH_PATH=/usr/local/lib
COPY envoy.yaml /etc/envoy/envoy.yaml

CMD ["envoy", "-c", "/etc/envoy/envoy.yaml"]
```

Attribution: CNCF blog post, "Part 5: The Docker Image".

### Custom-image injection via GatewayParameters (verbatim from the post)

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayParameters
metadata:
  name: custom-envoy
  namespace: kgateway-system
spec:
  kube:
    envoyContainer:
      image:
        registry: ""          # Empty = use local images
        repository: envoy-wrapper
        tag: latest
        pullPolicy: IfNotPresent
```

Attribution: CNCF blog post, "Part 6: Deploying the Custom Envoy Image".

### Linking GatewayParameters to the Gateway (verbatim command from the post)

```bash
kubectl patch gateway ai-gateway -n kgateway-system --type='json' -p='[{"op": "add", "path": "/spec/infrastructure", "value": {"parametersRef": {"name": "custom-envoy", "group": "gateway.kgateway.dev", "kind": "GatewayParameters"}}}]'
```

Attribution: CNCF blog post, "Part 6: Deploying the Custom Envoy Image".

### TrafficPolicy that also sets the "proof" header (verbatim from the post)

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: my-smart-header-filter
  namespace: kgateway-system
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbun-route
  transformation:
    response:
      set:
        - name: X-Custom-Transformed
          value: "true"
        - name: X-Smart-Header
          value: "method=%REQ(:METHOD)%&path=%REQ(:PATH)%"
```

Attribution: CNCF blog post, "Part 7: Create the TrafficPolicy for Custom Headers".

### Rust response-header hook (verbatim from the post)

```rust
fn on_response_headers(
    &mut self,
    envoy_filter: &mut EHF,
    end_of_stream: bool,
) -> abi::envoy_dynamic_module_type_on_http_filter_response_headers_status {
    // ... existing code ...
    envoy_log_trace!("on_response_headers");
    // ADD THIS: Custom header to prove the Rust module is working
    self.set_response_header("X-Custom-Transformed", b"true");
    // ... rest of the function
}
```

Attribution: CNCF blog post, "The Transformation Logic".

### Troubleshooting table (verbatim from the post)

```
Issue                              Solution
ImagePullBackOff on custom image   Load image with kind load docker-image and set pullPolicy: IfNotPresent and registry: “” in GatewayParameters
Rust version mismatch              Update Dockerfile to use rust:1.88 instead of rust:1.85
Gateway controller reverts image changes
                                   Use GatewayParameters instead of direct deployment edit
404 page not found                 Add URLRewrite filter to transform /v1/chat/completions → /llm/chat/completions
BackendRef port error              Remove port from backendRefs when using kind: Backend
kgateway.exe causing large git pushes
                                   Add to .gitignore and use git rm --cached
```

Attribution: CNCF blog post, "Troubleshooting Common Issues".

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path cited or dismissed):

- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
  **cited** (Extends; see below).
- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**:
  SLO granularity for retail/gaming operations; no gateway extension, ABI, or
  controller-reconciliation content.
- `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` —
  **dismissed**: agent security platform and policy-as-code; no custom Envoy
  module, version coupling, or data-plane reconciliation.
- `source-notes/docs-promptfoo-model-audit.md` — **dismissed**: model-scanning
  CLI and severity gates; unrelated to gateway extensibility.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch-coordination process; no gateway or extension content.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch rate
  limiting and token reservation; unrelated.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **dismissed**:
  within-request model composition and advisor billing; unrelated.
- `source-notes/docs-litellm-completion-function-call.md` — **dismissed**:
  capability predicates and tool injection; unrelated.
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**:
  supported-parameter gate; unrelated.
- `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — **dismissed**:
  agent-evaluation tracing bridge; unrelated.

**Primary cross-references:**

- **Corroborates**:
  - `source-notes/blog-cncf-cluster-aware-ai-agent-argo-gitops.md` **Claim 5**
    — that note's delivery chain is "decoupled" precisely because "Image Updater
    ... writing to Git ... preserves a single source of truth", so Argo CD
    reconciles the intended state rather than accepting out-of-band cluster
    edits. This note's Claim 5 is the same controller-owns-its-intended-state
    rule: direct edits to the Envoy image are reverted, and the supported change
    is through `GatewayParameters` + `parametersRef`. Different controller
    (Argo CD vs kgateway), same reconciliation principle.
  - `source-notes/blog-litellm-sub-millisecond-proxy-overhead.md` **Claim 3** —
    that note measures proxy overhead with "a mock LLM endpoint" running on the
    same machine so the latency delta excludes network noise. This note deploys
    `httpbun` for the same reason (exercise the proxy without provider keys or
    spend), but goes further by routing through a custom dynamic module
    (Claim 9).
  - `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md`
    **Claim 4** — the declarative alternative is that "different components ...
    produce the specific part of the intent that they are responsible for" and
    the system combines and rolls it out. A direct `kubectl` edit of the
    controller-owned Envoy Deployment is an imperative contributor to an
    intended state the controller already owns; Claim 5 here is what that
    abstraction looks like at the field level (`parametersRef`).
- **Contradicts**: None against an existing source note. Three **internal**
  inconsistencies are recorded but not filed as contradiction issues (see
  Extraction Notes): Rust 1.85+ vs 1.88 (Claim 4), the response-header "proof"
  that is not discriminating (Claim 10), and the `agentgateway` attribution in
  a kgateway article (Claim 12). None opposes a claim in another note, and none
  would change guide advice in two directions.
- **Extends**:
  - `source-notes/blog-litellm-rust-launch.md` **Claim 1** — that note's Rust
    core follows "describe, don't execute" and runs as a PyO3-invoked transform
    library inside the gateway process. This note documents the other Rust
    integration architecture: a standalone Envoy dynamic module loaded from a
    `.so` at runtime. Both are Rust on the gateway path, but the extension
    model, failure mode, and upgrade coupling are different — this note adds the
    extension/ABI dimension the Rust-launch note does not cover.
  - `source-notes/docs-litellm-adding-openai-compatible-providers.md` **Claim 2**
    — that note's `param_mappings` silently rename OpenAI parameters to a
    backend's names. This note's Claim 8 is the path-level equivalent: the
    gateway silently rewrites `/v1/chat/completions` to the backend path so
    clients keep the standard endpoint. Together they show OpenAI-compatibility
    parity is maintained by both parameter and path rewriting, and both must be
    asserted at the wire boundary.
  - `source-notes/docs-litellm-mock-requests.md` **Claim 10** — that note maps
    three test-only mocking knobs at three layers and finds that none
    synthetically exercises gateway fallback logic. This note adds a fourth kind
    of test surface — an out-of-process mock server (`httpbun`) that *does* keep
    the gateway path in the test — but Claim 10 here also shows the limit: a mock
    path only proves the module ran if the assertion is discriminating.
  - `source-notes/blog-cncf-policy-engine-offline-production-fidelity.md`
    **Claim 6** — that note's rule is that offline testing must be *identical*
    to what runs in the cluster, because making the engine accept test-shaped
    data would diverge behavior. `httpbun` is a test double on the same
    principle: it is useful only to the extent it mimics a real OpenAI-compatible
    backend; a non-discriminating header assertion is the equivalent of accepting
    test-shaped data into the test.
- **Novel**: First source note in the corpus to cover (a) kgateway and Envoy
  dynamic-module extensibility, (b) control-plane/data-plane/extension-SDK ABI
  coupling and its breaking-change surface, (c) the `GatewayParameters` +
  `parametersRef` injection path that avoids controller reconciliation reverts,
  (d) the `filter_config` protobuf-wrapper pitfall, and (e) a concrete example
  of a non-discriminating "module loaded" assertion.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "Pin to a supported line; separate
  patching from line moves"**: Add the extension ABI to the pin matrix. The
  current rule pins the gateway minor line and treats line moves as behavior
  changes; this source adds a harder case — a compiled Envoy dynamic module can
  break on the same line move because kgateway v2.3 introduced breaking changes
  to the Rust dynamic-module system (Claim 2). Recommend pinning and recording
  the quadruple (kgateway, Envoy, dynamic-module SDK, Rust toolchain) and
  rebuilding/re-testing the module on every control-plane line move (Claim 3).

- **Chapter 05 — release engineering / "Test in the environment you ship"**:
  Add the controller-reconciliation gotcha (Claim 5): on a controller that owns
  the data-plane Deployment, an out-of-band Envoy image edit is drift and is
  reverted; inject custom images through a first-class parameter resource
  (`GatewayParameters` referenced from `Gateway.spec.infrastructure.parametersRef`).
  Pair it with the local-image `ImagePullBackOff` fix (Claim 6) so the runbook
  distinguishes "wrong owner" from "image not visible".

- **Chapter 05 — "Provider parity in the shared forwarding path"**: Add path
  parity as the second half of the parity rule (Claim 8). The section already
  requires exact-wire parameter assertions; add that an `HTTPRoute` `URLRewrite`
  can make the client-visible path differ from the backend-observed path
  (`/v1/chat/completions` → `/llm/chat/completions`), so the exact-request
  assertion must cover the rewritten path too. This complements
  `docs-litellm-adding-openai-compatible-providers.md` Claim 2's parameter
  renames.

- **Chapter 05 — "A green eval is not evidence until you can name what it
  measured"**: Add the non-discriminating verification example (Claim 10). The
  source's `X-Custom-Transformed: true` check cannot fail because the
  `TrafficPolicy` sets the same header; the rule is to assert a value only the
  extension can produce (or remove the competing producer). This is the
  gateway-extension instance of "a gate that cannot fail is not a gate".

- **Chapter 06 (Security and Trust) — "Pin everything; verify releases"**: Add
  the custom Envoy image to the supply-chain surface (Claims 2, 5): the
  extension is delivered as a rebuilt base image (`envoyproxy/envoy:v1.36.4` +
  module), so both the base image and the Rust builder image are pinned inputs
  that must be verified like any other gateway dependency.

- **Chapter 00 (Principles)**: Add extensibility as a last resort after built-in
  policies (Claim 1): a custom dynamic module is justified only when the
  gateway's declared policy/templating cannot express the behavior, because it
  trades declarative configuration for an owned compiled artifact and its ABI
  coupling.

## Extraction Notes

- Read the full CNCF post (single page, no substantive sub-pages). The linked
  GitHub lab (`Mike-4-prog/kgateway-ai-gateway-lab`) was not crawled; manifests,
  the Dockerfile, and the Rust snippet are quoted from the article, which inlines
  them.
- All `Quote` fields are copied character-for-character from the fetched page,
  including the source's curly apostrophes and the `–` in "Rust (1.85+) – ...".
  The two quotes in Claim 10 are separate contiguous sentences from different
  sections; they are not spliced together.
- **Contradiction decision (no issue filed).** The source disagrees with itself
  in three places — the Rust floor (1.85+ vs 1.88, Claim 4), the header "proof"
  (Claim 10), and the closing `agentgateway` attribution (Claim 12). Per
  MINER.md §4a these are not filed as contradiction issues: none opposes a claim
  in an existing source note, and they are documentation/evidence-quality
  artifacts rather than two guide recommendations pointing in different
  directions. They are recorded as claims and extraction caveats so the Smith
  does not propagate the bad version floor, the false proof, or the wrong
  product attribution.
- One additional documentation artifact: the article's "Why ExtensionRef?"
  note says the `HTTPRoute` is linked to the `TrafficPolicy` via `ExtensionRef`,
  but the shown `HTTPRoute` has no `extensionRef` filter and the shown
  `TrafficPolicy` attaches via `spec.targetRefs`. Recorded here rather than as a
  claim; the `targetRefs` manifest is the artifact to trust.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  candidate paths are cited or dismissed above. Primary cross-reference
  verification (MINER §4b) re-read the cited claims in
  `blog-cncf-cluster-aware-ai-agent-argo-gitops.md` (Claim 5),
  `blog-litellm-sub-millisecond-proxy-overhead.md` (Claim 3),
  `docs-google-sre-prodcast-03-13-imperative-declarative.md` (Claim 4),
  `blog-litellm-rust-launch.md` (Claim 1),
  `docs-litellm-adding-openai-compatible-providers.md` (Claim 2),
  `docs-litellm-mock-requests.md` (Claim 10), and
  `blog-cncf-policy-engine-offline-production-fidelity.md` (Claim 6) before
  citing them; claim numbers and quoted passages were confirmed against the
  cited notes.
- `confidence_overall: emerging` — the mechanics are concrete and reproducible,
  but this is a single-author `kind` lab with a mock LLM, no production
  telemetry, no version matrix, and a non-discriminating validation check.
  Version-coupling and reconciliation claims are settled *for this lab* and
  emerging as operational rules.
- Per the Prospector's triage, the step-by-step install/apply walkthrough was not
  re-extracted; the note keeps the manifests that carry an ops-relevant claim.
