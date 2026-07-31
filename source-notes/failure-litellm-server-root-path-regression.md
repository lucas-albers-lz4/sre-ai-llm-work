---
source_url: https://docs.litellm.ai/blog/server-root-path-incident
source_type: failure-report
platform: blog
title: "Incident Report: SERVER_ROOT_PATH regression broke UI routing"
author: "Yuneng Jiang (Senior SWE @ LiteLLM), Ishaan Jaffer (CTO, LiteLLM), Krrish Dholakia (CEO, LiteLLM)"
date_published: 2026-02-21
date_extracted: 2026-07-31
last_checked: 2026-07-31
status: current
confidence_overall: settled
issue: "#688"
---

# Failure Report: LiteLLM SERVER_ROOT_PATH regression broke UI routing behind path-prefixed reverse proxies

> An unrelated PR (#19467) that was intended to fix a *different* UI 404 issue silently dropped `root_path=server_root_path` from the FastAPI app initialization in `proxy_server.py`. Deployments using `SERVER_ROOT_PATH` behind a reverse proxy with a path prefix (`/api/v1`, `/llmproxy`) got 404s on all UI pages for ~4 days while the LLM API path kept working — undetected because no automated or manual test exercised the non-default config, and default deployments passed CI.

## Source Context

- **Platform**: Vendor engineering incident blog published on `docs.litellm.ai/blog` (Docusaurus), tagged `incident-report`, `ui`, `stability`. Published 2026-02-21.
- **Author credibility**: Very high — co-authored by LiteLLM's Senior SWE (Yuneng Jiang), CTO (Ishaan Jaffer), and CEO (Krrish Dholakia). The report includes the exact code diff that introduced the regression, both PR references with commit hashes, a remediation table, a full timeline, and operator resolution steps.
- **Scope**: A specific, fully root-caused and remediated production regression in LiteLLM's proxy deployment configuration (`SERVER_ROOT_PATH` / FastAPI `root_path`). It generalizes to a class of bugs — a deployment-config parameter whose only consumers are non-default deployments, so a regression that drops it is invisible to any test suite that exercises only default configurations.

## What Was Attempted

- **Goal**: Serve the LiteLLM proxy UI correctly when deployed behind a reverse proxy (Nginx, Traefik, AWS ALB) that routes traffic to LiteLLM under a path prefix.
- **Tool/approach**: LiteLLM proxy's FastAPI app in `proxy_server.py`, configured via the `SERVER_ROOT_PATH` environment variable. FastAPI's `root_path` parameter "tells the application about this prefix so it can correctly serve static files, generate URLs, and handle routing."
- **Setup**: LiteLLM proxy deployed behind a reverse proxy with a path prefix such as `/api/v1` or `/llmproxy`; `SERVER_ROOT_PATH` set in the environment.

## What Went Wrong

- **Symptoms**: All UI pages returned 404 Not Found for deployments using `SERVER_ROOT_PATH` behind a path-prefixed reverse proxy. Swagger/OpenAPI docs were broken when accessed through the configured root path. The LLM API path was completely unaffected.
- **Severity**: High — complete failure of the UI/admin surface for affected deployments.
- **Duration**: ~4 days (Jan 22 merge of the regressing PR → Jan 26 merge of the fix).
- **Detection channel**: User reports on nightly builds — no automated monitor or test surfaced it.
- **Reproducibility**: Deterministic for any deployment using `SERVER_ROOT_PATH` behind a path-prefixed reverse proxy; invisible to default (no-prefix) deployments.

### Symptom A: UI 404s only for path-prefixed deployments; LLM API routing unaffected

- **Evidence**: The Summary section explicitly scopes the blast radius. API calls were not affected; only UI pages and Swagger/OpenAPI docs through the configured root path.
- **Quote**: "Users who deploy LiteLLM behind a reverse proxy with a path prefix (e.g., `/api/v1` or `/llmproxy`) found that all UI pages returned 404 Not Found."
- **Confidence**: settled.

### Symptom B: Swagger/OpenAPI docs broken through the configured root path

- **Evidence**: Summary bullet enumerates the docs surface as also broken.
- **Quote**: "Swagger/OpenAPI docs: Broken when accessed through the configured root path."
- **Confidence**: settled.

## Root Cause (if identified)

- **Author's diagnosis**: PR #19467 (`73d49f8`) removed the `root_path=server_root_path` line from the `FastAPI()` constructor in `proxy_server.py`. Without `root_path`, FastAPI treats all requests as if the application were mounted at `/`, causing path mismatches for any deployment using `SERVER_ROOT_PATH`. The PR "was intended to fix a different UI 404 issue" — the parameter was dropped as a side effect.
- **Our assessment**: Agree completely. This is the classic collateral-damage config regression: an unrelated change drops a line that only matters to non-default deployments. `root_path` is uniquely treacherous because it is a no-op when unset — every default-path deployment behaves identically before and after the drop, so the diff review and the default test suite both pass. The severity is High precisely because of that stealth.
- **Category**: genuine-bug (collateral-damage config drop in LiteLLM), but representative of a generic anti-pattern — **deployment-config regressions confined to non-default configurations are invisible to default-path CI**.

### Root-cause detail A: The exact diff — one line removed, no test noticed

- **Evidence**: The Root cause section shows the removed line in the `FastAPI()` constructor. The diff touches only `proxy_server.py` app initialization.
- **Quote**: "PR [#19467](https://github.com/BerriAI/litellm/pull/19467) (`73d49f8`) removed the `root_path=server_root_path` line from the `FastAPI()` constructor in `proxy_server.py`:"
- **Confidence**: settled.

### Root-cause detail B: The three-fold coverage gap that let it ship and survive ~4 days

- **Evidence**: The report enumerates three reasons the regression went undetected. Together they describe a default-path CI blindspot.
- **Quote**: "The regression went undetected because: 1. **No automated test** verified that `root_path` was set on the FastAPI app. 2. **No manual test procedure** existed for `SERVER_ROOT_PATH` functionality. 3. **Default deployments** (without `SERVER_ROOT_PATH`) were unaffected, so most CI tests passed."
- **Confidence**: settled.

## Recovery Path

- **What they switched to**: A four-part remediation, all marked ✅ Done:
  1. Restore `root_path=server_root_path` in FastAPI app initialization — PR #19790 (`5426b3c`).
  2. Add unit tests for `get_server_root_path()` and FastAPI app initialization — `test_server_root_path.py`.
  3. Add a CI workflow that builds the Docker image and tests UI routing with `SERVER_ROOT_PATH` on every PR — `test_server_root_path.yml`.
  4. Document a manual test procedure for `SERVER_ROOT_PATH` — Discussion #8495.
- **Workaround**: None beyond upgrading. The fix ships in `v1.81.3.rc.6` or higher.
- **Unresolved**: None stated; status is Resolved.

### Fix detail A: The unit tests cover both the unset and the set branches of the config getter plus FastAPI init

- **Evidence**: The linked `test_server_root_path.py` asserts `get_server_root_path()` returns `""` when `SERVER_ROOT_PATH` is unset or empty (preserving `X-Forwarded-Prefix` support) and returns the value when set, then verifies the FastAPI app gets `root_path` wired through from the env var in both modes. (Linked file fetched from `BerriAI/litellm` main via GitHub API; see Concrete Artifacts.)
- **Confidence**: settled (for the linked artifact at extraction time).

### Fix detail B: The CI workflow gates every PR on real-deployment UI routing, not just unit behavior

- **Evidence**: The CI workflow section describes a Docker-based workflow running "on every PR against `main`": it builds the image, boots a container with `SERVER_ROOT_PATH` set (both `/api/v1` and `/llmproxy`), asserts the UI returns valid HTML at `{ROOT_PATH}/ui/`, and fails the build if the UI is unreachable.
- **Quote**: "This prevents future regressions where changes to `proxy_server.py` accidentally break `SERVER_ROOT_PATH` support."
- **Confidence**: settled (as described by the report; the referenced workflow file itself was not found at `BerriAI/litellm` main HEAD during extraction — see Extraction Notes).

## Concrete Artifacts

**Incident metadata (verbatim from source):**
```
Date: January 22, 2026
Duration: ~4 days (until fix merged January 26, 2026)
Severity: High
Status: Resolved
Note: This fix is available starting from LiteLLM v1.81.3.rc.6 or higher.
```

**The regressing diff — `root_path=server_root_path` removed from `FastAPI()` init (tokens verbatim from the source; whitespace normalized from the page's single-line rendering):**
```diff
     app = FastAPI(
         docs_url=_get_docs_url(),
         redoc_url=_get_redoc_url(),
         title=_title,
         description=_description,
         version=version,
-        root_path=server_root_path,
         lifespan=proxy_startup_event,
     )
```

**Remediation table (verbatim from source):**

| # | Action | Status | Code |
|---|--------|--------|------|
| 1 | Restore `root_path=server_root_path` in FastAPI app initialization | ✅ Done | [`#19790`](https://github.com/BerriAI/litellm/pull/19790) (`5426b3c`) |
| 2 | Add unit tests for `get_server_root_path()` and FastAPI app initialization | ✅ Done | `test_server_root_path.py` |
| 3 | Add CI workflow that builds Docker image and tests UI routing with `SERVER_ROOT_PATH` on every PR | ✅ Done | `test_server_root_path.yml` |
| 4 | Document manual test procedure for `SERVER_ROOT_PATH` | ✅ Done | Discussion #8495 |

**CI workflow details (verbatim from source):**

> 1. Builds the LiteLLM Docker image
> 2. Starts a container with `SERVER_ROOT_PATH` set (tests both `/api/v1` and `/llmproxy`)
> 3. Verifies the UI returns valid HTML at `{ROOT_PATH}/ui/`
> 4. Fails the workflow if the UI is unreachable

**Timeline (verbatim from source):**

| Time (UTC) | Event |
|------------|-------|
| Jan 22, 2026 04:20 | PR [#19467](https://github.com/BerriAI/litellm/pull/19467) merged, removing `root_path=server_root_path` |
| Jan 22–26 | Users on nightly builds report UI 404 errors when using `SERVER_ROOT_PATH` |
| Jan 26, 2026 17:48 | Fix PR [#19790](https://github.com/BerriAI/litellm/pull/19790) merged, restoring `root_path=server_root_path` |
| Feb 18, 2026 | CI workflow [`test_server_root_path.yml`](https://github.com/BerriAI/litellm/blob/main/.github/workflows/test_server_root_path.yml) added to run on every PR |

**Resolution steps for users (verbatim from source):**
```
pip install --upgrade litellm
```

```
# In your environment or docker-compose.yml
SERVER_ROOT_PATH="/your-prefix"
```

> "Then confirm the UI is accessible at `http://your-host:4000/your-prefix/ui/`."

**Regression unit tests — excerpt from the linked `test_server_root_path.py`** (fetched from `BerriAI/litellm` main via GitHub API on 2026-07-31; path `tests/proxy_unit_tests/test_server_root_path.py`; excerpt covers the config-getter branches and the FastAPI-init wiring):

```python
def test_get_server_root_path_unset():
    """
    Test that get_server_root_path returns empty string when SERVER_ROOT_PATH is unset
    """
    with mock.patch.dict(os.environ, {}, clear=True):
        # We need to make sure SERVER_ROOT_PATH is not in env
        if "SERVER_ROOT_PATH" in os.environ:
            del os.environ["SERVER_ROOT_PATH"]

        root_path = utils.get_server_root_path()
        assert (
            root_path == ""
        ), "Should return empty string when unset to allow X-Forwarded-Prefix"


def test_get_server_root_path_set():
    """
    Test that get_server_root_path returns the value when SERVER_ROOT_PATH is set
    """
    with mock.patch.dict(os.environ, {"SERVER_ROOT_PATH": "/my-path"}, clear=True):
        root_path = utils.get_server_root_path()
        assert root_path == "/my-path", "Should return the set value"


def test_fastapi_app_initialization_mock():
    """
    Simulate how proxy_server.py initializes FastAPI app with the root_path.
    We don't import proxy_server because it has global side effects/singletons.
    Instead we verify the logic flow.
    """
    from fastapi import FastAPI

    # CASE 1: Proxy Mode (Unset)
    with mock.patch.dict(os.environ, {}, clear=True):
        if "SERVER_ROOT_PATH" in os.environ:
            del os.environ["SERVER_ROOT_PATH"]

        server_root_path = utils.get_server_root_path()
        app = FastAPI(root_path=server_root_path)
        assert app.root_path == ""

    # CASE 2: Direct Mode (Set)
    with mock.patch.dict(os.environ, {"SERVER_ROOT_PATH": "/custom-root"}, clear=True):
        server_root_path = utils.get_server_root_path()
        app = FastAPI(root_path=server_root_path)
        assert app.root_path == "/custom-root"
```

## Extracted Claims

### Claim 1: An unrelated PR can silently drop a deployment-config parameter that only non-default deployments depend on — a collateral-damage config regression
- **Evidence**: PR #19467 (`73d49f8`), which "was intended to fix a different UI 404 issue," removed `root_path=server_root_path` from the `FastAPI()` constructor in `proxy_server.py`. The report shows the exact diff with the single removed line.
- **Confidence**: settled
- **Quote**: "The `root_path` parameter was present in `proxy_server.py` since early versions of LiteLLM. It was removed as a side effect of PR [#19467](https://github.com/BerriAI/litellm/pull/19467), which was intended to fix a different UI 404 issue."
- **Our assessment**: This is the highest-value extraction. The root cause is not a subtle runtime race — it is a single configuration line dropped as an unintended side effect of an unrelated change. The config parameter is a no-op when unset, which is exactly what makes the drop invisible to diff review and to default-path testing. Any LLM gateway or FastAPI service deployed behind a path-prefixing reverse proxy is exposed to this failure class.

### Claim 2: The impact was scoped to UI/admin surfaces only — LLM API routing was completely unaffected
- **Evidence**: The Summary's bullet list explicitly scopes impact: "LLM API calls: No impact. API routing was unaffected." while "All UI pages returned 404 for deployments using `SERVER_ROOT_PATH`."
- **Confidence**: settled
- **Quote**: "LLM API calls: No impact. API routing was unaffected."
- **Our assessment**: This scoping is what makes the incident genuinely surprising and worth documenting: the revenue-critical API path was green the entire time, while the operator-facing UI was down. A monitoring setup that only tracks request success on the LLM path (the common case for gateway deployments) would see zero error budget burn during this incident. UI/admin health needs its own synthetic checks.

### Claim 3: The regression went undetected because of a three-fold coverage gap — no automated test, no manual test procedure, and default deployments passing CI
- **Evidence**: The Root cause section enumerates all three reasons explicitly.
- **Confidence**: settled
- **Quote**: "No automated test verified that `root_path` was set on the FastAPI app. No manual test procedure existed for `SERVER_ROOT_PATH` functionality. Default deployments (without `SERVER_ROOT_PATH`) were unaffected, so most CI tests passed."
- **Our assessment**: This is the core SRE lesson — the default-path CI blindspot. A regression confined to a non-default configuration is invisible to any suite that only exercises defaults, and "most CI tests passed" is a category error when the regressed path has zero coverage. The fix for this class is not more of the same tests; it is a CI gate that boots the *non-default* configuration (see Claim 5).

### Claim 4: The incident was High severity, lasted ~4 days, and was surfaced by user reports on nightly builds rather than by monitoring
- **Evidence**: The incident metadata (Severity: High; Duration: ~4 days, Jan 22–26, 2026) and the Timeline row for Jan 22–26 describing user reports.
- **Confidence**: settled
- **Quote**: "Users on nightly builds report UI 404 errors when using `SERVER_ROOT_PATH`"
- **Our assessment**: The detection channel matters: nightly-build users (pre-release adopters) hit the 404 before general release and reported it. This is a "user-report-driven" incident — the kind that lands on oncall as a handful of ambiguous "the dashboard is broken" tickets (Ch04 relevance) with no alert to tie them together. A ~4-day window for a config regression that was fully deterministic from day one is a direct cost of the coverage gap in Claim 3.

### Claim 5: The durable remediation was restoring the param plus a PR-gated Docker CI workflow that boots the proxy under the non-default config and asserts the UI responds — not just more unit tests
- **Evidence**: The remediation table and CI workflow section describe the four-part fix, including "a CI workflow that builds the Docker image and tests UI routing with `SERVER_ROOT_PATH` on every PR."
- **Confidence**: settled
- **Quote**: "This prevents future regressions where changes to `proxy_server.py` accidentally break `SERVER_ROOT_PATH` support."
- **Our assessment**: The reusable pattern is the *configuration-level* regression gate: build the real artifact (Docker image), start it with the deployment-specific env var set, and assert the user-visible surface (valid HTML at `{ROOT_PATH}/ui/`) responds — failing the build otherwise. This is materially different from a unit test that checks a getter function, because it exercises the whole boot path with the real config. The dual-prefix matrix (`/api/v1` and `/llmproxy`) also encodes the supported deployment topologies explicitly.

### Claim 6: The CI workflow runs on every PR against main and fails the build if the UI is unreachable under either supported path prefix
- **Evidence**: The CI workflow details list four steps, including "Fails the workflow if the UI is unreachable."
- **Confidence**: settled
- **Quote**: "1. Builds the LiteLLM Docker image 2. Starts a container with `SERVER_ROOT_PATH` set (tests both `/api/v1` and `/llmproxy`) 3. Verifies the UI returns valid HTML at `{ROOT_PATH}/ui/` 4. Fails the workflow if the UI is unreachable"
- **Our assessment**: Gating on every PR (not just at release time) is what converts a one-time fix into a durable regression guard. The "fails if unreachable" property makes the check a hard gate rather than an informational probe. Note: at extraction time the referenced workflow file returned 404 on `BerriAI/litellm` main, so this claim rests on the report's description (see Extraction Notes).

### Claim 7: Users remediate by upgrading; the fix ships in `v1.81.3.rc.6` or higher
- **Evidence**: The note at the top of the report and the "Resolution steps for users" section.
- **Confidence**: settled
- **Quote**: "> **Note:** This fix is available starting from LiteLLM `v1.81.3.rc.6` or higher."
- **Our assessment**: A simple, low-toil resolution (upgrade) is the flip side of the config-drop root cause: because no data or schema changed, there is no migration — restore the parameter, ship it, and users upgrade. The guidance to verify the UI at `http://your-host:4000/your-prefix/ui/` doubles as a manual smoke test that did not exist before the incident (the remediation's item 4).

## Cross-References

- **Corroborates the "default-path CI blindspot" pattern in**:
  - `failure-litellm-model-cost-map-silent-fallback.md` (Lessons 1 & 2) — The closest parallel in the corpus. That incident: a malformed JSON cost-map entry merged to main, silent fallback to a stale local backup, with no CI validation on the config file; the remediation added CI validation (`test-model-map.yaml`) and a warning log. This incident: a dropped config param, silent 404s for non-default deployments, with no test exercising the config; the remediation added a PR-gated CI workflow and unit tests. Both are the same shape — *a regression confined to a non-default configuration that default-path CI cannot see, fixed by adding a CI gate that exercises the non-default config* — at different layers (data-format validation vs. deployment-topology routing).
  - `failure-litellm-httpx-cache-eviction.md` (Claim 5) — That note documents a regression that stayed live ~6 days because it only manifested under a non-default runtime condition (cache TTL expiry / capacity eviction) that the existing test suite didn't exercise. The ~4-day window here is the same stealth dynamic: the failure condition is real but absent from the default test path.
  - `failure-litellm-prisma-reconnect-event-loop-blocking.md` (Claim 6) — That incident only manifested under partial-failure conditions (unresponsive DB, TCP close hangs) invisible to standard healthy/stopped testing. Same principle in a different dimension: non-default *runtime state* (this note: non-default *deployment configuration*). Both argue that testing must deliberately exercise the non-default conditions, not just the happy path.
  - `failure-litellm-wildcard-model-access-desync.md` (Root Cause section) — Same vendor, same family of config-handling bugs: a config update path (cost-map reload) that updated one structure but not the derived in-memory set, silently breaking wildcard auth for new models. Both are "configuration changed, and a non-default consumer silently broke because no test covered the coupling." This note adds the *config-parameter-drop* variant (a param deleted entirely) to the *config-update-incompleteness* variant already documented there.

- **Extends**:
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` (Claim 4) — Botros's "generalize the outage" principle ("see how the outage that happened could happen in another way?") is directly instantiated by this incident's remediation: rather than just restoring `root_path`, the team generalized into unit tests, a Docker-boot CI gate, and a documented manual test procedure so the whole class of "proxy_server.py change breaks root_path" is caught forever. The report is a clean case study of an outage-driven, generalized fix.
  - `blog-litellm-fastapi-middleware-performance.md` — Both touch FastAPI app internals in `proxy_server.py` (middleware plumbing vs. the `root_path` constructor parameter). Together they show the FastAPI app-init surface as a recurring fragility point in the LiteLLM proxy: a performance hazard (BaseHTTPMiddleware overhead) and a configuration hazard (dropped constructor param). No contradiction — different subsystems, compatible direction.

- **Contradicts**: None. No existing source note claims default-path CI is sufficient, or that `root_path` / `SERVER_ROOT_PATH` handling is covered. No contradiction issue filed (see Extraction Notes).

- **Novel**: First source note in the corpus covering:
  1. **The `SERVER_ROOT_PATH` / FastAPI `root_path` config regression** behind reverse-proxy path prefixes (`/api/v1`, `/llmproxy`) — a deployment-topology config failure, distinct from the runtime failure modes in other LiteLLM notes.
  2. **The "deployment-config CI blindspot" pattern** — a config parameter whose only consumers are non-default deployments, so a regression that drops it is invisible to default-path CI and diff review (because the param is a no-op when unset).
  3. **The Docker-boot deployment-config regression gate** — the PR-gated workflow pattern that builds the real image, boots it with the non-default env var set, asserts the user-visible UI surface responds with valid HTML, and fails the build otherwise.
  4. **The UI-404 / API-200 scoping** — a regression that breaks the operator/admin surface while leaving the revenue-critical LLM API path untouched, making it invisible to API-centric error-budget monitoring.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — gateway deployment config behind a reverse proxy)**: Add a concrete failure pattern: "Deployment-config regressions confined to non-default configurations are invisible to default-path CI." Use the LiteLLM `SERVER_ROOT_PATH` incident as the case study: an unrelated PR (#19467) dropped `root_path=server_root_path` from the FastAPI init, and every deployment behind a path-prefixed reverse proxy (`/api/v1`, `/llmproxy`) lost its UI for ~4 days while the LLM API path stayed green. Specific guidance: (a) treat `root_path`/path-prefix config as a supported deployment topology with explicit test coverage, not an afterthought; (b) maintain a synthetic check for the operator surface (UI/admin) in addition to API-path checks, since API monitors saw zero error budget burn here.

- **Chapter 02 or 04 (Testing / CI for LLM ops)**: Add the "config-parity testing" pattern from the remediation:
  1. Unit test the config getter and its consumption — `test_server_root_path.py` asserts `get_server_root_path()` returns `""` when unset/empty (preserving `X-Forwarded-Prefix`) and the value when set, and verifies the FastAPI app is initialized with `root_path` wired from the env var in both modes.
  2. Add a PR-gated Docker-boot regression workflow — `test_server_root_path.yml`: build the image, start a container with `SERVER_ROOT_PATH` set (both supported prefixes), assert valid HTML at `{ROOT_PATH}/ui/`, and fail the build if unreachable. Reference this as the canonical guard for "config that only manifests behind a reverse proxy."

- **Chapter 01 (Incident Response — timeline/severity post-mortem structure)**: Use this incident as a case study for the "user-reported, no-alert" incident anatomy: High severity, deterministic from day one, ~4 days to fix because the detection channel was nightly-build user reports rather than monitoring. The timeline and the three-reason detection-gap enumeration are directly reusable as post-mortem structure for config-regression incidents.

- **Chapter 04 (Oncall / Toil)**: Note that user-reported UI 404s on nightly builds are a toil source and an unreliable detection channel. Recommend synthetic UI health probes for path-prefixed deployments so the "dashboard is broken" class of tickets gets an alert, not an oncall investigation.

## Extraction Notes

- Source read in full via WebFetch of `https://docs.litellm.ai/blog/server-root-path-incident` (Docusaurus blog page, self-contained single-page incident report; no substantive narrative sub-pages to follow). All quoted passages copied from the rendered page text; PR/commit references, the remediation table, and the timeline are reproduced as rendered.
- Two linked pages were followed as artifacts: the regression test file `tests/proxy_unit_tests/test_server_root_path.py` (fetched via GitHub API from `BerriAI/litellm` main, 2026-07-31 — included as an excerpt in Concrete Artifacts) and the CI workflow `test_server_root_path.yml`. **The workflow file returned HTTP 404 at `BerriAI/litellm` main HEAD during extraction**, even though the report's remediation table and timeline reference it (`https://github.com/BerriAI/litellm/blob/main/.github/workflows/test_server_root_path.yml`). Claim 6 therefore rests on the report's own description of the workflow; the Assayer may want to verify whether the file was moved/renamed or removed since the report (dated Feb 21, 2026) was published.
- Two formatting normalizations were applied to code artifacts, matching the convention used in sibling LiteLLM notes ("formatting is normalized ... without altering tokens"): (1) the regressing diff was rendered single-line in the source page and is presented here as a readable multi-line diff preserving all tokens; (2) the `SERVER_ROOT_PATH` config example in the source lacked a newline between the comment and the assignment (rendered as `docker-compose.ymlSERVER_ROOT_PATH="/your-prefix"`), presented here split onto two lines.
- The regression-test artifact is labeled an excerpt: the fetched file continues beyond the FastAPI-init test shown here; the excerpt covers the config-getter branches and the app-init wiring that are the note's core evidence. The full file can be re-fetched at the linked path.
- No contradiction issue filed: verified against CONTRADICTIONS.md (no open entries) and all existing source notes. Nothing in the corpus claims default-path CI is sufficient for non-default deployment configs, or that `root_path`/`SERVER_ROOT_PATH` handling is otherwise covered; the closest notes (model-cost-map silent fallback, wildcard desync) are complementary, not conflicting — they document *different* variants of the same "config change silently breaks a non-default consumer" family.
- Cross-reference candidates from `miner-related-notes.md` not cited above, each dismissed in one line:
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — AI-agent spectrum/guardrails, unrelated to deployment-config regressions.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server, unrelated.
  - `docs-google-sre-reliable-product-launches.md` — Launch-coordination engineering, unrelated.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — AI-for-SRE tooling, unrelated.
  - `docs-langfuse-security-and-guardrails.md` — Security/guardrail stacks, unrelated.
  - `blog-litellm-save-claude-code-costs.md` — LiteLLM cost-cutting features, unrelated.
  - `blog-pagerduty-sre-agent-triage.md` — SRE Agent triage, unrelated.
  - `docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` — SLO fundamentals, unrelated.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — IR tooling breadth/roadmap; its meta-retrospective claim is about aggregating many postmortems, whereas this incident's CI workflow is a single-incident remediation — related in spirit, not cited.
  - `docs-google-sre-prodcast-03-05-building-reliable-systems.md` — cited under Extends (Claim 4, generalize-the-outage).
- The triage comment also named `failure-litellm-encrypted-content-affinity.md` as loosely related; it is not cited because it documents a routing-affinity failure (cryptographic content binding) at a different layer, and does not bear on deployment-config regressions.
