---
source_url: https://docs.litellm.ai/docs/benchmarks
source_type: docs
title: "Benchmarks — LiteLLM AI Gateway Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs, no byline or date; benchmark content scoped to v1.101.0, retrieved 2026-09-23)
date_extracted: 2026-09-23
last_checked: 2026-09-23
status: current
confidence_overall: emerging
issue: "#1430"
---

# Benchmarks (LiteLLM Docs)

> LiteLLM's canonical gateway-capacity page: a high-throughput deployment
> profile A/B (3,000 RPS at 50K–100K-token prompts vs a v1.101.0 baseline)
> with per-component measured effects, plus two SRE-generalizable
> measurement rules the corpus otherwise lacks — a server-side success metric
> is blind to the failures that never arrive, and closed-loop load tests
> measure the client's queueing, not the gateway (think-time / Little's Law).

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, a
  single living Docusaurus page, no byline or publication date). The page's
  substantive benchmark content is explicitly scoped to **v1.101.0** and to a
  nightly-build deployment profile described as "still in development."
- **Author credibility**: LiteLLM (BerriAI) first-party product/vendor
  documentation. Authoritative for *what LiteLLM reports as its own measured
  results and its own methodology descriptions* — but every number is
  vendor-reported, self-benchmarked, single-source, and not independently
  reproduced (`network_mock` benchmark script and a Locust snippet are
  published, but not the complete high-throughput profile harness).
- **Scope**: Covers (1) the high-throughput deployment profile vs v1.101.0
  A/B (results, test setup, per-component measured effects, metric semantics,
  scope caveats); (2) short-request, fake-OpenAI-endpoint capacity tables on
  4-CPU/8-GB machines (2 vs 4 instances, `x-litellm-overhead-duration-ms`);
  (3) the reproducible `network_mock` and fake-endpoint harnesses; (4)
  `/realtime` latency benchmarks; (5) logging-callback overhead (GCS bucket,
  LangSmith); (6) a Locust think-time / Little's Law analysis. Does **not**
  cover (deliberately, per the Prospector): the LiteLLM-vs-Portkey comparison
  table (competitor marketing; v1.79.1 vs v1.14.0, single 5-minute run, no
  methodology detail). The page is a *different page* from the one rejected in
  #1380 (`/docs/aiohttp_benchmarks`); this page contains zero `aiohttp`
  mentions and is about the current release profile.

## Extracted Claims

### Claim 1: The high-throughput deployment profile sustained 3,000 RPS with 100% client-visible success on large-prompt traffic, while the v1.101.0 baseline settled near 190 RPS at 92.07% success
- **Evidence**: The headline results paragraph states the target was reached;
  the results table gives 16x RPS (3.00K vs 0.19K), 32x tokens/sec (224.61M
  vs 6.92M), and per-pod/worker shape (33 pods × 4 workers vs 132 pods × 1
  worker, both 132 total workers, both 528 GiB; profile 132 vCPU vs baseline
  264 vCPU).
- **Confidence**: emerging (vendor-reported, single-source, nightly profile —
  the page itself says the profile "is still in development")
- **Quote**: "The profile reached the full 3,000 RPS target with 100 percent client-visible success. The baseline settled near 190 RPS and returned a successful response for 92.07 percent of requests."
- **Our assessment**: The headline before/after is a *combined-profile* A/B,
  not attributable to any single change (Claim 6 states it is "not a
  single-variable test"), and the baseline is a deliberately under-provisioned
  132-pod shape, not a representative default deployment. The number to
  extract is the *pattern* (fewer pods, more workers, less pod overhead → 16x
  RPS at the same worker count), not "3,000 RPS" as a universal capacity
  figure.

### Claim 2: The latency improvements are extreme but all measured against the same 132-worker count — p50 6.950s → 30.581ms, p95 27.451s → 54.029ms, p99 29.826s → 91.645ms, TTFT p50 9.400s → 31.667ms
- **Evidence**: The results table's Request latency / TTFT rows, paired with
  the deployment rows confirming total workers stayed 132 in both arms.
- **Confidence**: emerging (vendor-reported tables; the same nightly-profile
  caveat as Claim 1 applies)
- **Quote**: "(table data — see Concrete Artifacts, High-throughput profile results)"
- **Our assessment**: The same-throughput latency collapse is the strongest
  evidence that the profile's wins are real and deployment-shape-driven rather
  than hardware-driven: both arms ran 132 workers and 528 GiB, and the p50
  moved ~227x. Still vendor-measured against an in-process mock, so treat as
  directional for the guide's capacity material, not a universal number.

### Claim 3: Each component of the profile was A/B-tested separately at 200–1,000 RPS before the combined run, and the page publishes the individual deltas
- **Evidence**: The "What made the difference" table lists nine changes each
  with a customer-impact line and a measured effect; the section intro states
  they were "measured separately before the complete profile was tested."
- **Confidence**: settled (the vendor states the measurement design; the
  individual deltas are as reproducible as the published `network_mock`
  harness permits)
- **Quote**: "Each change below was measured separately before the complete profile was tested."
- **Our assessment**: This is where the page earns its keep: the individual
  A/Bs (Rust admission token counting 46/53/100 ms → 4.9/6.8/10.2 ms at
  50K/75K/100K tokens; spend-collector sidecar p99 1.8s → 830ms; CPU burst
  limit p99 830 → 670ms; ALB 502s 15 → 0; replica ~48s after a load step)
  are the only part of the page that isolates cause and effect. Still
  vendor-measured, but these are the knobs the guide can name as "large"
  versus "negligible" (metrics sidecar ~2 millicores/pod).

### Claim 4: A gateway-side success metric cannot see the failures that never reach it — the v1.101.0 run measured 100% gateway-side success while Locust measured 92.07%
- **Evidence**: The "How to read the metrics" section states the HTTP 200
  rate comes from Locust specifically because it "includes failures that
  never reached the gateway," and gives the failure breakdown (5,118
  client-visible failures: 4,546 timeouts/dropped connections, 457 HTTP 504,
  115 HTTP 502) that never reached the gateway.
- **Confidence**: settled (reported failure accounting with a clear causal
  mechanism — the gateway never received the requests, so its own Prometheus
  metric could not see them)
- **Quote**: "The v1.101.0 run had 5,118 client-visible failures: 4,546 client timeouts or dropped connections, 457 HTTP 504 responses, and 115 HTTP 502 responses. The gateway did not receive these requests, so its own success metric showed 100 percent while Locust showed 92.07 percent."
- **Our assessment**: The single most SRE-generalizable claim on the page.
  The failure shape (dropped connections + LB 504/502 during overload) is
  exactly the class that a server-side metric is structurally blind to. The
  guide's Ch02 success-measurement rules should state this as a general rule:
  HTTP 200 rate must be measured outside the thing being measured.

### Claim 5: The page's metric semantics deliberately split by vantage point — throughput and request latency come from the gateway's Prometheus metrics, TTFT and HTTP-200 rate from Locust
- **Evidence**: The "How to read the metrics" section's three sentences
  assigning each metric to its generator.
- **Confidence**: settled (documented methodology, internally consistent)
- **Quote**: "The HTTP 200 rate comes from Locust because it includes failures that never reached the gateway."
- **Our assessment**: A concrete, reusable labeling discipline for gateway
  benchmarks: bottleneck-side metrics (RPS, tokens/sec, p50/p95/p99 from the
  gateway) vs client-visible metrics (TTFT, success rate). When a vendor table
  mixes vantage points, this section is the key to interpreting it. Worth
  generalized into the guide's benchmark-interpretation material.

### Claim 6: The page explicitly disclaims universal applicability — the A/B is "not a single-variable test," the mock excludes provider latency, and the numbers are "not universal production sizing guidance"
- **Evidence**: The "Benchmark scope" section paragraphs state the combined
  run used different pod shapes and run durations (24m 22s vs 5m 7s), seat the
  individual effects in "separate A/B tests at 200 to 1,000 RPS," and warn to
  "measure a representative workload" before choosing worker counts, pod
  resources, and HPA targets.
- **Confidence**: settled (explicit scope statement by the vendor)
- **Quote**: "This is a before-and-after comparison of the complete profile, not a single-variable test. The deployments used different pod shapes and ran for different lengths of time. The individual effects in the table above come from separate A/B tests at 200 to 1,000 RPS."
- **Quote**: "The in-process mock model excludes provider latency. These results measure gateway capacity for this specific traffic shape and should not be treated as universal production sizing guidance. Measure a representative workload before choosing worker counts, pod resources, and HPA targets."
- **Our assessment**: The vendor itself defuses the obvious misuse — treating
  these as sizing guidance. The note should carry this caveat verbatim; the
  guide should not restate the headline numbers without it. Also flags for the
  Smith: the page's own short-request sections (below) are on different
  hardware and workloads ("not directly comparable"), so two result sets on
  the same page must stay separate in any synthesis.

### Claim 7: The high-throughput profile is not GA — it ships only in nightly builds and these results came from "the earliest available version of the complete profile"
- **Evidence**: The "Nightly benchmark" admonition box directly above the
  results table.
- **Confidence**: emerging (dated status; the profile may GA and change the
  figures)
- **Quote**: "The high-throughput profile is still in development and is available in nightly builds. These results used the earliest available version of the complete profile."
- **Our assessment**: Prevents the guide from recording the profile (or the
  3,000 RPS figure) as current, stable capability. Treat the deployment shape
  as directional vendor work-in-progress, stamp v1.101.0, and expect churn.

### Claim 8: The profile's per-component wins come from separating concerns off the inference workers — Rust token counting, per-pod PgBouncer, spend and metrics sidecars, RPS/TPS autoscaling
- **Evidence**: The "What made the difference" table's change/impact/effect
  triples: Rust admission token counting (50K/75K/100K counts 46/53/100 ms →
  4.9/6.8/10.2 ms), PgBouncer per pod (Postgres held 86–175 connections
  across 11–29 pods with no waiting clients), spend-collector sidecar (p99
  1.8s → 830ms at 700 RPS), metrics sidecar (~2 millicores/pod at 700 RPS),
  higher CPU burst limit (p99 830 → 670ms), gateway keep-alive (ALB 502s 15 →
  0 at 200 RPS), RPS/TPS autoscaling (new replica ~48s after a 200-user
  step), admission token-count reuse (streaming mock requests finish within
  ~30ms of non-streaming).
- **Confidence**: emerging (vendor-measured at 200–1,000 RPS; the 
  admission-token-counting and sidecar deltas corroborate the sidecar
  architecture direction in `blog-litellm-sub-millisecond-proxy-overhead`)
- **Quote**: "50K / 75K / 100K counts fell from 46 / 53 / 100 ms to 4.9 / 6.8 / 10.2 ms."
- **Our assessment**: The measurable statement of the architecture the
  sub-millisecond-overhead post predicted without numbers: the big knobs are
  Rust token counting, the spend-collector sidecar, and the CPU burst limit;
  the metrics sidecar and keep-alive are near-negligible or capability items
  (~2 millicores, 502 elimination). The guide can cite these as *which knobs
  are large* for a LiteLLM-style gateway at high prompt volume, dated to
  v1.101.0.

### Claim 9: Closed-loop load tests measure the client's queueing, not the gateway — at the same RPS, a no-think-time client holds ~8x the in-flight depth and reports ~8x the latency (Little's Law)
- **Evidence**: The "Why the think time matters" section computes the
  numbers: 1,000 users with a 0.75s mean think time and ~110ms responses
  complete a request ~every 0.86s, offering ~1,160 RPS with ~130 requests in
  flight; a closed-loop client with no think time holds 1,000 in flight, ~8x
  the queue depth, so latency = in-flight / throughput gives ~8x the reported
  latency at identical throughput.
- **Confidence**: settled (Little's Law; the arithmetic is spelled out on the
  page and is regenerable)
- **Quote**: "A closed-loop client with no think time is measuring something else. 1000 concurrent workers that send the next request the moment the previous one returns hold 1000 requests in flight, about 8x the queue depth of these runs. Once a gateway is saturated its throughput is fixed, and by Little's Law the latency each client observes is just requests in flight / throughput. So the same deployment, at the same RPS, reports roughly 8x the latency purely because the client queued 8x as much work into it. Latency and concurrency are not independent, and neither number means anything without the other."
- **Our assessment**: The page's most transferable claim and entirely
  vendor-independent. It is a load-test-design rule for *any* gateway
  benchmark, including the guide's own eval runs: report RPS and in-flight
  depth together, or latency figures are uninterpretable. Do not let a
  higher-RPS report be misread as "faster" when it is the client queueing
  deeper.

### Claim 10: The page gives an explicit correction procedure for comparing against its tables — keep the 0.5–1s think time, or hold in-flight request count near 130 and report it alongside latency
- **Evidence**: The closing paragraph of the think-time section states both
  options and the "report RPS first" rule.
- **Confidence**: settled (direct methodology instruction)
- **Quote**: "To compare against the tables above, either keep the 0.5s to 1s think time, or hold your client's in-flight request count near 130 and report it alongside the latency. It is also worth reporting RPS first: if your run shows higher RPS and higher latency than these tables, your gateway is faster than this benchmark and your client is simply queueing deeper."
- **Our assessment**: Concrete and actionable — the guide can lift this
  directly as a load-test validity rule: hold concurrency ~130 (or think time
  0.5–1s) and report RPS before latency.

### Claim 11: `network_mock: true` intercepts outbound requests at the httpx transport layer, benchmarking pure proxy hot-path overhead with canned responses and no mock provider
- **Evidence**: The "Setting Up Benchmarking with Network Mock" section gives
  the config, the `--num_workers 8` start command, and
  `python scripts/benchmark_mock.py --requests 2000 --max-concurrent 200 --runs 3`, and links
  the published script.
- **Confidence**: settled (reproducible, published harness — the config and
  commands reproduce the mechanism directly)
- **Quote**: "The fastest way to benchmark proxy overhead is using network_mock mode. This intercepts outbound requests at the httpx transport layer and returns canned responses, no need for setting up a mock provider."
- **Our assessment**: The reproducible core of the page — unlike the
  high-throughput profile, this harness can be run locally today. Useful for
  the guide's benchmark-methodology section as the concrete way to isolate
  gateway overhead from provider/network latency (complements the
  same-machine mock methodology in `blog-litellm-sub-millisecond-proxy-overhead`).

### Claim 12: Doubling the LiteLLM proxy from 2 to 4 instances halves median latency (200 → 100 ms) and cuts p99 from 1,200 → 240 ms; "workers equal to CPU count gives optimal performance"
- **Evidence**: The 2-Instance and 4-Instance performance tables (POST
  /chat/completions rows) and the "Key Findings" bullets.
- **Confidence**: emerging (vendor short-request benchmark against a fake
  endpoint, not comparable to the large-prompt profile)
- **Quote**: "Doubling from 2 to 4 LiteLLM instances halves median latency: 200 ms → 100 ms."
- **Quote**: "Setting workers equal to CPU count gives optimal performance."
- **Our assessment**: A separate, lower-value result set (short bodies, 4
  CPU/8 GB) that the page itself says is "not directly comparable" with the
  large-prompt benchmark. The "workers = CPU count" guidance is the
  transferable bit — the 4-instance table's `LiteLLM Overhead Duration` row
  (p95 8ms at 1,170 RPS, median 2ms) underlies the page's "8ms P95 latency at
  1k RPS" headline. Keep separate from the profile numbers in synthesis.

### Claim 13: Logging callbacks (GCS Bucket, LangSmith) are "no impact" on gateway RPS and latency at ~1,130 RPS
- **Evidence**: The "Logging Callbacks" tables: GCS Bucket RPS 1,133.2 → 1,137.3, median 140 → 138 ms; LangSmith RPS 1,133.2 → 1,135, median 140 → 132 ms.
- **Confidence**: emerging (vendor claim at a single load point; only RPS and
  median shown; no high-percentile or error-rate columns)
- **Quote**: "Using GCS Bucket has no impact on latency, RPS compared to Basic Litellm Proxy"
- **Our assessment**: Useful as a vendor-reported data point that out-of-path
  logging callbacks need not be the bottleneck, but the table is thin (no p95/
  p99, no error rates) and contradicts the spend-collector sidecar finding that
  *in-path* async work did matter at higher RPS. Treat as "log-side work was
  neutral at ~1.1k RPS," not a general law.

### Claim 14: The benchmark environment omits production infrastructure — single PostgreSQL, no Redis used
- **Evidence**: The "Infrastructure Recommendations" section states the runs
  used a single PostgreSQL instance and no Redis, calling it "a benchmark
  configuration rather than a production one," and points to the Database
  Sizing / Redis Sizing / Production Best Practices pages.
- **Confidence**: settled (explicit scope statement)
- **Quote**: "The runs above used a single PostgreSQL instance and no Redis, which is a benchmark configuration rather than a production one."
- **Our assessment**: An honest scope note — the numbers exclude the DB and
  Redis load a real deployment carries. Reinforces treating everything on the
  page as directional. Worth keeping as a caveat attached to any guide cite of
  the 2/4-instance tables.

## Concrete Artifacts

### High-throughput profile results (verbatim table)

```
| Category        | Metric                   | High-throughput profile | v1.101.0    | Change |
| Deployment      | Gateway pods             | 33                      | 132         | 4x fewer |
|                 | Workers per pod          | 4                       | 1           |         |
|                 | Total workers            | 132                     | 132         | same    |
| Throughput      | Requests/sec             | 3.00K                   | 0.19K       | 16x     |
|                 | Tokens/sec               | 224.61M                 | 6.92M       | 32x     |
|                 | Projected tokens/30 days | 582.20T                 | 17.94T      | 32x     |
| Reliability     | HTTP 200 rate (Locust)   | 100.00%                 | 92.07%      |         |
| Request latency | p50                      | 30.581 ms               | 6.950 s     | 227x    |
|                 | p95                      | 54.029 ms               | 27.451 s    | 508x    |
|                 | p99                      | 91.645 ms               | 29.826 s    | 325x    |
| TTFT            | p50                      | 31.667 ms               | 9.400 s     | 297x    |
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "High-throughput profile: 3,000 RPS with 50K to 100K-token prompts — Results."

### Per-component measured effects (verbatim table)

```
| Change                   | Customer impact                                   | Measured effect                                                        |
| Rust admission token     | Reduces CPU spent counting large prompts before   | 50K / 75K / 100K counts fell from 46 / 53 / 100 ms                     |
| counting                 | dispatch.                                         | to 4.9 / 6.8 / 10.2 ms.                                                |
| PgBouncer per pod        | Prevents database connections from multiplying    | Postgres held 86 to 175 connections across 11 to 29 pods,              |
|                          | with every worker.                                | with no waiting PgBouncer clients.                                     |
| Spend collector sidecar  | Keeps spend processing away from inference        | At 700 RPS, p99 fell from 1.8 s to 830 ms. Total compute               |
|                          | workers.                                          | stayed roughly the same.                                               |
| Metrics sidecar          | Keeps Prometheus scrapes away from inference      | The sidecar used about 2 millicores per pod at 700 RPS.                |
|                          | workers.                                          |                                                                        |
| Higher CPU burst limit   | Prevents all workers in a pod from being          | At 700 RPS, p99 fell from 830 ms to 670 ms.                            |
|                          | throttled together.                               |                                                                        |
| Gateway keep-alive       | Keeps load-balancer connections valid during      | ALB-generated 502 responses fell from 15 to zero in the                |
|                          | scaling.                                          | 200 RPS test.                                                          |
| RPS and TPS autoscaling  | Reacts to traffic before CPU becomes saturated.   | A new replica was added about 48 seconds after a 200-user              |
|                          |                                                   | load step.                                                             |
| Admission token-count    | Avoids counting the same large streaming prompt   | Streaming mock requests finished within about 30 ms of                 |
| reuse                    | twice in mock tests.                              | non-streaming requests.                                                |
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "What made the difference."

### Test setup (verbatim)

```
| Dimension        | Configuration                                                  |
| Load generator   | Distributed Locust with one master and 30 workers              |
| Traffic          | 3,000 simulated users at one request per second each           |
| Request mix      | 50K, 75K, and 100K-token prompts in equal shares               |
| Streaming        | 50 percent of requests                                         |
| Endpoint         | /v1/chat/completions with max_tokens: 16                       |
| Authentication   | Virtual key with a budget, so admission token counting and     |
|                  | budget reservation ran                                          |
| Model            | In-process mock model with response caching disabled           |
| Network path     | Public AWS Application Load Balancer                           |
| Client timeout   | 60 seconds                                                     |
| Run duration     | High-throughput profile: 24m 22s. Baseline: 5m 7s.             |
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "Test setup."

### `network_mock` proxy config (verbatim)

```
model_list:
  - model_name: db-openai-endpoint
    litellm_params:
      model: openai/gpt-5.6-terra
      api_key: "sk-fake-key"
      api_base: "https://api.openai.com"

litellm_settings:
  network_mock: true
  callbacks: []
  num_retries: 0
  request_timeout: 30

general_settings:
  master_key: "sk-<your-litellm-master-key>"
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "Setting Up Benchmarking with Network Mock" (normalized into valid YAML from the page's flattened code block).

### `network_mock` run commands + benchmark invocation (verbatim)

```
litellm --config benchmark_config.yaml --port 4000 --num_workers 8

python scripts/benchmark_mock.py --requests 2000 --max-concurrent 200 --runs 3
```

> "This measures pure proxy overhead on the hot path without any network latency to a real or fake provider."

Attribution: https://docs.litellm.ai/docs/benchmarks, same section. Script linked on the page: `scripts/benchmark_mock.py` in the LiteLLM repo.

### Fake OpenAI endpoint config (verbatim)

```
model_list:
  - model_name: "fake-openai-endpoint"
    litellm_params:
      model: openai/any
      api_base: https://exampleopenaiendpoint-production.up.railway.app/  # or your self-hosted endpoint
      api_key: "test"
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "Setting Up a Fake OpenAI Endpoint." Hosted endpoint: `https://exampleopenaiendpoint-production.up.railway.app/`; self-hosted: github.com/BerriAI/example_openai_endpoint.

### 2 and 4 instance performance tables (verbatim)

```
2 instances:
Type    Name                              Median 95%ile 99%ile Average Current RPS
POST    /chat/completions                 200    630    1200   262.46  1035.7
Custom  LiteLLM Overhead Duration (ms)     12     29      43    14.74   1035.7
Aggregated                               100    430     930   138.6   2071.4

4 instances:
Type    Name                              Median 95%ile 99%ile Average Current RPS
POST    /chat/completions                 100    150    240    111.73  1170
Custom  LiteLLM Overhead Duration (ms)      2      8     13      3.32   1170
Aggregated                                77    130    180     57.53   2340
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "2 Instance LiteLLM Proxy" / "4 Instances." Key Findings bullets: "Doubling from 2 to 4 LiteLLM instances halves median latency: 200 ms → 100 ms." "High-percentile latencies drop significantly: P95 630 ms → 150 ms, P99 1,200 ms → 240 ms." "Setting workers equal to CPU count gives optimal performance."

### `/realtime` metrics (verbatim)

```
Median latency: 59 ms | p95: 67 ms | p99: 99 ms | Average: 63 ms | RPS: 1,207
Test setup: Load — Locust 1,000 users, 0.5s-1s think time, 500 ramp-up.
System — 4 vCPUs, 8 GB RAM, 4 workers, 4 instances. DB: PostgreSQL (Redis unused).
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "`/realtime` API Benchmarks."

### Logging-callback overhead (verbatim)

```
GCS Bucket Logging:  Basic LiteLLM Proxy RPS 1133.2, Median 140 ms | with GCS RPS 1137.3, Median 138 ms
LangSmith logging:   Basic LiteLLM Proxy RPS 1133.2, Median 140 ms | with LangSmith RPS 1135, Median 132 ms
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "Logging Callbacks."

### Locust listener for the overhead header (verbatim code)

```python
import os
import uuid
from locust import HttpUser, task, between, events

# Custom metric to track LiteLLM overhead duration
overhead_durations = []

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    if response and hasattr(response, 'headers'):
        overhead_duration = response.headers.get('x-litellm-overhead-duration-ms')
        if overhead_duration:
            try:
                duration_ms = float(overhead_duration)
                overhead_durations.append(duration_ms)
                # Report as custom metric
                events.request.fire(
                    request_type="Custom",
                    name="LiteLLM Overhead Duration (ms)",
                    response_time=duration_ms,
                    response_length=0,
                )
            except (ValueError, TypeError):
                pass

class MyUser(HttpUser):
    wait_time = between(0.5, 1)  # Random wait time between requests
    def on_start(self):
        self.api_key = os.getenv('API_KEY', 'sk-<your-litellm-api-key>')
        self.client.headers.update({'Authorization': f'Bearer {self.api_key}'})

    @task
    def litellm_completion(self):
        # no cache hits with this
        payload = {
            "model": "db-openai-endpoint",
            "messages": [{"role": "user", "content": f"{uuid.uuid4()} This is a test there will be no cache hits and we'll fill up the context" * 150}],
            "user": "my-new-end-user-1"
        }
        response = self.client.post("chat/completions", json=payload)

        if response.status_code != 200:
            # log the errors in error.txt
            with open("error.txt", "a") as error_log:
                error_log.write(response.text + "\n")
```

Attribution: https://docs.litellm.ai/docs/benchmarks, "How to measure LiteLLM Overhead." The header it reads is documented as: "All responses from litellm will include the `x-litellm-overhead-duration-ms` header, this is the latency overhead in milliseconds added by LiteLLM Proxy."

## Cross-References

- **Corroborates**:
  - `blog-litellm-sub-millisecond-proxy-overhead.md` **Claim 5** (1,000 QPS no failures → 5,000 QPS on a single 4-CPU/8-GB instance, Feb 2026) — this page's short-prompt 4-instance table (1,170 RPS POST, p95 overhead 8ms) is the same single-instance-era measurement family, and its 3,000 RPS large-prompt profile is the follow-up at higher vCPU count and newer version (v1.101.0). Same vendor, same measurement theme, compatible direction.
  - `blog-litellm-sub-millisecond-proxy-overhead.md` **Claim 3** (proxy-overhead measurement methodology: same workload + mock on the same machine, latency delta = overhead) — this page's `network_mock` mode and the same-machine fake-endpoint harness are the operational realization of that methodology, now published with a runnable script (Claim 11 here).
  - `blog-litellm-fastapi-middleware-performance.md` **Claim 7** (~30% proxy-overhead reduction across optimizations, Feb 7, 2026) — contiguous program: the middleware post's aggregate reduction is a near-term increment on the same overhead target this page measures end-to-end at v1.101.0.
  - `blog-litellm-april-townhall-updates.md` **Claim 9** (10k+ RPS uptime target) — the 3,000-RPS large-prompt profile is a concrete step toward that stated reliability target, and the page's "workers equal to CPU count" finding is measurable feed for it.

- **Contradicts**: None found against the corpus, and no contradiction issue filed. The only apparent tensions are scope-conditioned, not real disputes:
    - `blog-litellm-rust-launch.md` reports the Rust-vs-Python gateway forwarding-path comparison at tiny request sizes (~0.05ms vs ~7.5ms overhead, 6,782 vs 453 req/s on a thin harness), while this page reports 4.9/6.8/10.2 ms *full admission-token counts* on 50K–100K-token prompts. Different measured object (pure forwarding path vs admission token counting), not a conflict.
    - `blog-litellm-sub-millisecond-proxy-overhead.md` **Claim 5**'s 5,000 QPS single-instance figure vs this page's 0.19K-RPS baseline: the difference is workload and provisioning (short prompts on 1 instance vs large prompts on 132 under-provisioned pods), which the page itself flags. Conditioning variable, not contradiction.

- **Extends**:
  - `blog-litellm-sub-millisecond-proxy-overhead.md` — that post proposed the optional sidecar architecture *without measured numbers* and stated the sidecar was "an optimization, not a requirement" (Claims 6, 7, 9). This page supplies the measured per-component deltas behind exactly that architecture direction (spend-collector sidecar 1.8s → 830ms, metrics sidecar ~2 millicores, Rust admission counting) at a version (v1.101.0) ahead of everything in the corpus. It moves the sidecar claim from designed to *measured on the gateway hot path*, and adds the profile caveat that it is nightly, not GA.
  - `blog-litellm-rust-launch.md` **Claim 1** (Rust core "describe, don't execute", token counting as a data-transform) — this page quantifies the admission-stage effect of the Rust token-counting component at large prompt sizes (46/53/100 ms → 4.9/6.8/10.2 ms), giving the migration's stated motivation a measured number.
  - `blog-litellm-fastapi-middleware-performance.md` — that post's reproducible per-change A/B benchmark (50K/1K/1-worker, zero-work endpoint) is the same measurement philosophy this page applies per-component at 200–1,000 RPS; together they form the corpus's "how LiteLLM measures itself" thread, and both had at least a partial public harness.
  - `blog-litellm-april-townhall-updates.md` — the 10k+ RPS reliability target and "investigate latency overhead" item (Claim 9) get their first quantitative milepost (3,000 RPS sustained on the large-prompt profile, still nightly).

- **Novel**: First source note in the corpus to introduce:
  - The client-visible-vs-gateway-side success divergence (100% vs 92.07% with the exact failure accounting) — a server-side success metric structurally cannot see requests that never arrive. New to Ch02's success-measurement material.
  - The Little's Law / think-time closed-loop analysis: in-flight depth, not user count, sets reported latency; ~130 in-flight ≈ 0.75s think time at this workload; report RPS and in-flight together. Vendor-independent and new to the corpus.
  - The high-throughput deployment profile as a *shape* (33 × 4 vs 132 × 1 worker) with the same-total-worker throughput comparison — first corpus source to frame gateway capacity as a pod/worker profile rather than a single QPS number.
  - The per-component sidecar/token-counting A/B deltas at 200–1,000 RPS (Rust counting, PgBouncer per pod, spend sidecar, CPU burst limit, keep-alive 502 elimination, RPS/TPS autoscaling).
  - The `network_mock: true` httpx-transport interception mode as a reproducible gateway hot-path benchmark harness, plus `x-litellm-overhead-duration-ms` as a vendor-proxy-overhead measurement header.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — Cost, capacity, and fallback patterns**:
  - Add, under gateway capacity, the **capacity as a profile, not a number** pattern (Claim 1, 3, 8): state capacity as a deployment shape (workers per pod, pod count, sidecar topology, autoscaling signal) with per-component measured deltas, and attach the v1.101.0 / nightly-build status (Claims 2, 7) so the numbers are dated. Include the "which knobs are big vs negligible" ranking: Rust token counting (~10x count-time reduction), spend-collector sidecar (1.8s → 830ms p99), CPU burst limit (830 → 670ms), vs metrics sidecar (~2 millicores) and keep-alive (capability item). Cross-reference the `blog-litellm-sub-millisecond-proxy-overhead` sidecar claim now that it has measured backing.
  - Add, to the Ch05 section that already cites `blog-litellm-april-townhall-updates` **Claim 9** (the "Latency overhead of long-running agent requests / 10k+ RPS" rule at guide/05 lines ~1109–1122), the hard rule: gateway-side success metrics cannot see overload failures that never arrive (Claim 4) — HTTP 200 must be measured at the client load generator. This directly strengthens the existing rule that gateway capacity must be planned for agent-session traffic separately.

- **Chapter 02 (Observability)**:
  - Add the **measure success outside the thing being measured** rule (Claims 4, 5): when a service reports 100% success while the client measures 92%, the server-side metric is structurally blind — LB-502/504 and dropped-connection failures are invisible to the gateway's Prometheus metric. Apply to any gateway-metric dashboard the guide recommends.
  - Add the **latency is meaningless without concurrency** load-test rule (Claims 9, 10): report RPS and in-flight request depth together; hold in-flight near ~130 or use a 0.5–1s think time for comparability; a "faster" higher-RPS run may be a deeper-queueing client. This is a reusable interpretation rule for every benchmark in the corpus.

- **Chapter 05 / benchmark methodology** (complements the existing reproducible-harness material from `blog-litellm-rust-launch` and `blog-litellm-fastapi-middleware-performance`):
  - Add `network_mock: true` + `scripts/benchmark_mock.py` as the reusable gateway hot-path overhead harness (Claim 11), and `x-litellm-overhead-duration-ms` + the Locust listener as the standard way to collect proxy overhead as a first-class metric (Concrete Artifacts). State the page's own scope warning verbatim (Claim 6): mock model excludes provider latency; measure a representative workload before sizing; the profile numbers are not universal sizing guidance.

## Extraction Notes

- Source read in full; a fresh copy of `https://docs.litellm.ai/docs/benchmarks` fetched via HTTP on 2026-09-23 (UTC) and all quoted passages verified character-for-character against that HTML (admonition box, result tables, prose sections). All table data reproduced from the page's own tables; code blocks normalized to valid YAML/Python tokens without changing semantics (the page renders them flattened).
- The Prospector's caution list was followed exactly: (1) all numbers marked vendor-reported and non-reproduced — confidence capped at `emerging`; (2) the high-throughput profile recorded as nightly/in-development, not GA (Claim 7), stamped v1.101.0; (3) the large-prompt profile and the short-prompt 4-CPU/8-GB tables kept as separate result sets (Claim 6, Claim 12); (4) the page's own "not a single-variable test" caveat preserved verbatim; (5) the **LiteLLM-vs-Portkey section was not extracted** — it is a competitor comparison (v1.79.1 vs Portkey v1.14.0, single 5-minute run, no methodology) and the Prospector explicitly excluded it; it exists on the page and is flagged as self-reported vendor material if the Smith wants it.
- Not a duplicate of #1380: that issue rejected `/docs/aiohttp_benchmarks` (a May 2025 httpx→aiohttp transport benchmark); this URL (`/docs/benchmarks`) is a rewritten page with zero `aiohttp` mentions, centered on v1.101.0 profile results.
- **Cross-reference verification (§4b)**: all cited claims were re-read in the cited notes and their numbers confirmed — `blog-litellm-sub-millisecond-proxy-overhead` Claims 3, 5, 6, 7, 9; `blog-litellm-rust-launch` Claim 1 and its Concrete Artifacts overhead table; `blog-litellm-fastapi-middleware-performance` Claim 7; `blog-litellm-april-townhall-updates` Claim 9. No fabricated claim numbers or quotes.
- **miner-related-notes.md candidates evaluated (10)**: all dismissed as unrelated to gateway capacity/benchmarking — docs-litellm-batches-api (batch rate-limiting surface), docs-litellm-bedrock-invoke (Bedrock passthrough), docs-litellm-audio-transcription (audio endpoint), docs-litellm-a2a-iteration-budgets (agent-loop budgets), docs-google-sre-prodcast-04-09-ai-agents (agent spectrum), blog-litellm-auto-router-v2 (routing config), docs-litellm-bedrock-converse (Bedrock passthrough), docs-litellm-a2a-cost-tracking (agent cost tracking), docs-langfuse-mcp-server (different vendor), docs-litellm-helicone-integration (telemetry integration). Candidates file read but not committed. The relevant overlap set came from the Prospector's triage comments (the four blog notes cited above), all read in full.
- No contradiction issue filed: verified against open `contradiction` issues (none match — open items concern A2A budget storage, proxied-card paths, promptfoo eval semantics, routing flavors, messages mapping) and CONTRADICTIONS.md (no LiteLLM benchmark/perf entry). The two near-tensions identified in **Contradicts** are conditioning/scope differences (short-prompt vs large-prompt; forwarding-path vs admission-count), not opposing claims at the same snapshot; the page's own "goals and set up **not** comparable" note settles the short/large-prompt split.
- Retention decision for the article's other blocks: the `/realtime` table (p50 59ms, 1,207 RPS) kept as a light Claim-12-adjacent artifact for completeness; the callback-overhead tables kept but marked thin (Claim 13); the infra-recommendation scope note kept (Claim 14) because it constrains how all other numbers should be read.