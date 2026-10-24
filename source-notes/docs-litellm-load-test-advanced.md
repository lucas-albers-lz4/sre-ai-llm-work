---
source_url: https://docs.litellm.ai/docs/load_test_advanced
source_type: docs
title: "LiteLLM Proxy - 1K RPS Load test on locust"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs, retrieved 2026-10-24)
date_extracted: 2026-10-24
last_checked: 2026-10-24
status: current
confidence_overall: emerging
issue: "#1871"
---

# LiteLLM Proxy - 1K RPS Load test on locust

> A step-by-step Locust load-test runbook for the LiteLLM proxy that adds concrete failure-attribution metrics and documents expected behavior under provider rate limits (residual 429s are quota-exhaustion, not gateway failure). The page is largely a tutorial for scenarios the corpus already benchmarks, but its per-deployment Prometheus metrics and rate-limit interpretation rules are new and directly usable for observability/capacity guidance.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, Docusaurus page). Living page with no explicit publication date.
- **Author credibility**: LiteLLM (BerriAI) first-party product/vendor documentation. Authoritative for reported methodology and metric names; all numbers are vendor-reported self-benchmarks (single-source), not independently reproduced.
- **Scope**: Covers (1) pre-testing checklist (latest stable, prod best practices, Locust sizing, proxy machine specs, Enterprise-only Prometheus callback), (2) load test against a fake OpenAI endpoint with expected 1,174+ RPS / 96ms median / 142ms average, (3) load test against endpoints with rate limits (2 deployments × 10K RPM → ~20K RPM aggregate with expected provider-quota failures), (4) Prometheus metrics for debugging load tests (`litellm_deployment_failure_responses`, `litellm_deployment_cooled_down`), (5) machine specs for Locust and proxy, (6) locustfile.py used for testing. Does **not** focus on large-prompt high-throughput profile analysis (covered by `docs-litellm-benchmarks.md`); this is a reproducible runbook/tutorial.

## Extracted Claims

### Claim 1: Per-deployment failure-attribution metrics let operators distinguish gateway saturation from provider rate-limit/quota failures
- **Evidence**: "Prometheus Metrics for debugging load tests" section lists two metrics with full label sets.
- **Confidence**: emerging (vendor-documented metric names/labels; usage described but not independently validated)
- **Quote**: "`litellm_deployment_failure_responses` — Total number of failed LLM API calls for a specific LLM deployment. Labels: `\"requested_model\", \"litellm_model_name\", \"model_id\", \"api_base\", \"api_provider\", \"hashed_api_key\", \"api_key_alias\", \"team\", \"team_alias\", \"exception_status\", \"exception_class\"`"
- **Our assessment**: This is new to the corpus — no existing source note documents per-deployment failure/cooldown metrics. Critical for Ch02 debugging: attribute failures to a specific deployment/exception class rather than inferring from aggregate gateway success.

### Claim 2: A deployment cooldown metric tracks when load balancing cools down a specific deployment
- **Evidence**: Prometheus metrics table.
- **Confidence**: emerging
- **Quote**: "`litellm_deployment_cooled_down` — Number of times a deployment has been cooled down by LiteLLM load balancing logic. Labels: `\"litellm_model_name\", \"model_id\", \"api_base\", \"api_provider\", \"exception_status\"`"
- **Our assessment**: Complements Claim 1 — provides observability into LB state changes (cooldowns) that may explain traffic shifting/failures under load.

### Claim 3: In a rate-limit capacity test, residual failures are expected provider quota exhaustion, not gateway breakage
- **Evidence**: Rate-limit test setup describes 2 deployments × 10K RPM quota (~20K RPM aggregate), notes all requests for `model="gemini-vision"` load-balance equally across the two deployments, and states remaining requests fail because the endpoint exceeds its 10K RPM quota limit from the LLM API provider.
- **Confidence**: emerging (vendor-reported test scenario)
- **Quote**: "Run a load test on 2 LLM deployments each with 10K RPM Quota. Expect to see ~20K RPM"
- **Quote**: "The remaining requests **fail because the endpoint exceeds it's 10K RPM quota limit - from the LLM API provider**"
- **Our assessment**: Important interpretation rule: a success-rate < 100% is correct/expected behavior in a quota-saturation test. Operators must distinguish capacity-limit rejections (expected) from real gateway errors — success-rate threshold alone will mislabel a healthy rate-limited run. This is new relative to `docs-litellm-benchmarks.md`.

### Claim 4: For rate-limit tests, the page gives concrete expected numbers (20,000+ successful responses in 1 minute at ~1170 RPS) and a measured example
- **Evidence**: Expected Performance table for rate-limit test and "Expected results" showing 19,800 successes = (69415 - 49615), 1170 RPS, median 70ms, average 640ms.
- **Confidence**: emerging (vendor-reported)
- **Quote**: "-   Successful responses in 1 minute = 19,800 = (69415 - 49615)\n-   Requests per second = 1170\n-   Median response time = 70ms\n-   Average response time = 640ms"
- **Our assessment**: Concrete numbers for a quota-limited scenario; useful as an example but should be treated as vendor-reported like other benchmark numbers.

### Claim 5: Load-generator sizing for ~1K RPS is specified (Locust 4 processes, 2 vCPU/450MB/1 replica; proxy 4× t2.large 2vCPU/8GB)
- **Evidence**: Machine Specifications tables.
- **Confidence**: emerging
- **Quote**: "**Number of Replicas of LiteLLM Proxy=4** for getting 1K+ RPS"
- **Our assessment**: Reproducible sizing info for running the tutorial; similar scale to other LiteLLM benchmarks but more explicit about the load-generator side.

### Claim 6: Prometheus callbacks are required to get metrics for load-test debugging and are Enterprise-only
- **Evidence**: Pre-Testing Checklist states "Enterprise LiteLLM - Use `prometheus` as a callback in your `proxy_config.yaml` to get metrics on your load test Set `litellm_settings.callbacks` to monitor success/failures/all types of errors" and shows `callbacks: ["prometheus"] # Enterprise LiteLLM Only`.
- **Confidence**: emerging
- **Quote**: "`litellm_settings:    callbacks: [\"prometheus\"] # Enterprise LiteLLM Only - use prometheus to get metrics on your load test`"
- **Our assessment**: Important constraint — the debugging metrics (Claims 1-2) require Enterprise LiteLLM Prometheus callback. Must be attached to any guide recommendation citing these metrics.

### Claim 7: The page recommends using `openai/` provider for load testing and notes migration to aiohttp for higher throughput
- **Evidence**: Pre-Testing Checklist note.
- **Confidence**: emerging
- **Quote**: "**Note:** we're currently migrating to aiohttp which has 10x higher throughput. We recommend using the `openai/` provider for load testing."
- **Our assessment**: Operational advice; the aiohttp throughput claim is dated/as noted elsewhere in corpus context and should not be treated as current guidance per triage notes.

### Claim 8: The locustfile.py used for testing sends repeated long prompts with random UUIDs to avoid cache hits and logs failures to error.txt
- **Evidence**: Locust file code block.
- **Confidence**: settled (verbatim artifact)
- **Quote**: "payload = {\n            \"model\": \"fake-openai-endpoint\",\n            \"messages\": [{\"role\": \"user\", \"content\": f\"{uuid.uuid4()} This is a test there will be no cache hits and we'll fill up the context\" * 150 }],\n            \"user\": \"my-new-end-user-1\"\n        }"
- **Our assessment**: Same pattern as other LiteLLM locust examples in the corpus (long repeated content to stress context/token processing). Verbatim artifact worth keeping.

## Concrete Artifacts

### Pre-test config snippet (verbatim)
```yaml
litellm_settings:
  callbacks: ["prometheus"] # Enterprise LiteLLM Only - use prometheus to get metrics on your load test
```
Attribution: https://docs.litellm.ai/docs/load_test_advanced, Pre-Testing Checklist.

### Fake OpenAI endpoint config (verbatim)
```yaml
model_list:
  - model_name: "fake-openai-endpoint"
    litellm_params:
      model: openai/any
      api_base: https://exampleopenaiendpoint-production.up.railway.app/  # or your self-hosted endpoint
      api_key: "test"
```
Attribution: https://docs.litellm.ai/docs/load_test_advanced, Setting Up a Fake OpenAI Endpoint. Hosted endpoint: `https://exampleopenaiendpoint-production.up.railway.app/`; self-hosted: github.com/BerriAI/example_openai_endpoint.

### Rate-limit test config (verbatim, with fake rate-limited endpoints)
```yaml
model_list:
  - model_name: gemini-vision
    litellm_params:
      model: vertex_ai/gemini-3.1-pro-preview
      api_base: https://exampleopenaiendpoint-production.up.railway.app/v1/projects/bad-adroit-crow-413218/locations/us-central1/publishers/google/models/gemini-3.1-pro-preview
      vertex_project: "adroit-crow-413218"
      vertex_location: "us-central1"
      vertex_credentials: /etc/secrets/adroit_crow.json
  - model_name: gemini-vision
    litellm_params:
      model: vertex_ai/gemini-3.1-pro-preview
      api_base: https://exampleopenaiendpoint-production-c715.up.railway.app/v1/projects/bad-adroit-crow-413218/locations/us-central1/publishers/google/models/gemini-3.1-pro-preview
      vertex_project: "adroit-crow-413218"
      vertex_location: "us-central1"
      vertex_credentials: /etc/secrets/adroit_crow.json
litellm_settings:
  callbacks: ["prometheus"] # Enterprise LiteLLM Only - use prometheus to get metrics on your load test
```
Attribution: https://docs.litellm.ai/docs/load_test_advanced, Load test - Endpoints with Rate Limits. Note: all requests with `model="gemini-vision"` load-balance equally across the 2 deployments.

### Prometheus metrics table (verbatim)
| Metric Name | Description |
|-------------|-------------|
| `litellm_deployment_failure_responses` | Total number of failed LLM API calls for a specific LLM deployment. Labels: `"requested_model", "litellm_model_name", "model_id", "api_base", "api_provider", "hashed_api_key", "api_key_alias", "team", "team_alias", "exception_status", "exception_class"` |
| `litellm_deployment_cooled_down` | Number of times a deployment has been cooled down by LiteLLM load balancing logic. Labels: `"litellm_model_name", "model_id", "api_base", "api_provider", "exception_status"` |

Attribution: https://docs.litellm.ai/docs/load_test_advanced, Prometheus Metrics for debugging load tests.

### Machine specs (verbatim)
**Locust:** 4 processes, 2.0 vCPUs, 450 MB, 1 replica  
**Proxy:** 4 replicas of `t2.large` (2 vCPUs, 8 GB, x86)

Attribution: https://docs.litellm.ai/docs/load_test_advanced.

### Locust file (verbatim)
```python
import os
import uuid
from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(0.5, 1)  # Random wait time between requests
    @task(100)
    def litellm_completion(self):
        # no cache hits with this
        payload = {
            "model": "fake-openai-endpoint",
            "messages": [{"role": "user", "content": f"{uuid.uuid4()} This is a test there will be no cache hits and we'll fill up the context" * 150 }],
            "user": "my-new-end-user-1"
        }
        response = self.client.post("chat/completions", json=payload)
        if response.status_code != 200:
            # log the errors in error.txt
            with open("error.txt", "a") as error_log:
                error_log.write(response.text + "\n")
    def on_start(self):
        self.api_key = os.getenv('API_KEY', 'sk-<your-litellm-api-key>')
        self.client.headers.update({'Authorization': f'Bearer {self.api_key}'})
```
Attribution: https://docs.litellm.ai/docs/load_test_advanced, Locust file used for testing.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-benchmarks.md` **Claim 4** (gateway-side success metric blind to failures that never reach gateway) — both pages emphasize measuring from outside the gateway; this page adds per-deployment attribution and the specific case where provider-quota failures are expected.
  - `source-notes/docs-litellm-benchmarks.md` **Claim 5** (metric semantics split by vantage point) — complements with concrete Prometheus metric names and labels for deployment-level debugging.
  - `source-notes/docs-litellm-benchmarks.md` **Claim 9-10** (think-time/Little's Law) — this page's runbook uses similar Locust patterns; the rate-limit scenario is a different test case (quota saturation) rather than pure capacity saturation.

- **Contradicts**: None found. The scenarios are complementary (this page adds rate-limit/quota debugging and a concrete runbook; `docs-litellm-benchmarks.md` covers large-prompt profile A/B and methodology more deeply).

- **Extends**:
  - `source-notes/docs-litellm-benchmarks.md` — extends failure attribution beyond "gateway can't see them" to per-deployment metrics (`litellm_deployment_failure_responses`, `litellm_deployment_cooled_down`) and gives an explicit interpretation rule for quota-limited tests (expected failures). Also adds concrete Locust/proxy sizing for ~1K RPS scenario.
  - `source-notes/docs-litellm-enterprise.md` — the Prometheus callback requirement noted here is Enterprise-only, consistent with Enterprise gating.

- **Novel**: First source note in the corpus to introduce:
  - Per-deployment Prometheus metrics `litellm_deployment_failure_responses` and `litellm_deployment_cooled_down` with their label schemas for load-test debugging.
  - The "expected failures under provider quota" interpretation rule for rate-limit capacity tests (distinguish quota exhaustion from gateway failure).
  - Concrete runbook for a two-deployment rate-limit scenario with expected success counts and timing.

## Guide Impact

- **Chapter 02 (Observability)**:
  - Add **per-deployment failure attribution** rule: when debugging gateway load tests/failures, use deployment-level metrics (`litellm_deployment_failure_responses`, `litellm_deployment_cooled_down`) to attribute errors to specific deployments/providers/exception classes rather than relying solely on aggregate success rates. Note Prometheus callback is Enterprise-only.
  - Add **quota vs gateway failure distinction**: in rate-limited multi-deployment tests, residual 429s/quota rejections can be expected behavior — success-rate thresholds must account for provider quota limits. Attribute via deployment metrics and `exception_status`/`exception_class` labels.

- **Chapter 05 (LLM Ops Reliability) — Cost, capacity, and fallback patterns**:
  - Add runbook guidance for capacity testing under rate limits: test with multiple deployments each hitting quota to validate load balancing and observe expected failure patterns; size Locust/proxy per documented specs; use the provided locustfile pattern.
  - Call out that Prometheus-based load-test observability requires Enterprise LiteLLM Prometheus callbacks in this documented flow.

## Extraction Notes

- Source read in full via webfetch on 2026-10-24 (UTC). All quoted passages verified against the page content.
- Followed triage guidance: extracted procedure/metric-to-symptom mapping (Claims 1-3, 6) over headline RPS numbers (Claims 4-5 already overlap with `docs-litellm-benchmarks.md`); treated vendor-reported numbers as emerging.
- Did **not** mine the aiohttp migration throughput claim ("10x higher throughput") or deep-dive into stale prerender artifacts beyond noting the recommendation to use `openai/` provider for load testing.
- Cross-referenced against existing notes: `docs-litellm-benchmarks.md` (overlap on methodology/vantage points, complementary on failure attribution), `docs-litellm-enterprise.md` (Prometheus callback Enterprise-only). No contradictions found; no contradiction issue filed.
- Evaluated miner-related-notes.md candidates (10) — all dismissed as unrelated to load testing/benchmarking/failure-attribution metrics.
- Filename follows existing convention: `docs-litellm-load-test-advanced.md`.
