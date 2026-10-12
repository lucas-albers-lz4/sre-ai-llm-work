---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-crewai
source_type: docs
title: "Promptfoo: Red Teaming a CrewAI Agent — Local File Provider, JSON-Schema Output Contract, and a Custom Red-Team Target"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-12
date_extracted: 2026-10-12
last_checked: 2026-10-12
status: current
confidence_overall: emerging
issue: "#1681"
---

# Promptfoo: Red Teaming a CrewAI Agent

> A vendor walkthrough that brings a locally-run CrewAI multi-agent app under
> promptfoo by exposing it as a `file://./agent.py` provider — a module-level
> `call_api(prompt, options, context)` that wraps the async `crew.kickoff_async`
> in `asyncio.run`, regex-extracts JSON from the agent's free text, and returns
> `{"output": ...}` (errors returned as data, never raised) — then reuses the
> **same local file** as a red-team "Custom Target", with a JSON-Schema
> `is-json` `defaultTest` assertion pinning the output shape. The transferable
> core is the **provider-adapter contract for grading a self-hosted agent**, not
> eval-in-CI practice: the page ships **no** CI gating, thresholds, or baseline
> comparisons.

## Source Context

- **Type**: docs (vendor recipe guide — Promptfoo "Red Teaming a CrewAI Agent",
  under Evals → Guides → Integrations; auto-discovered from the registered
  `promptfoo-docs` site-crawl seed). Single guide page.
- **Author credibility**: Promptfoo, the LLM eval / red-team vendor. First-party
  documentation of the product's own `file://` Python provider and red-team
  "Custom Target" surfaces — authoritative for the documented config and code
  shapes, and directly checkable against an installed CLI, but vendor-positioned:
  no metrics, no run results, no independent validation, and the "example is
  CrewAI-specific" framing means the CrewAI binding is demonstrated only against
  the vendor's own scaffolded example.
- **Scope**: Covers (1) an optional `npx promptfoo@latest init --example
  integration-crewai` scaffold; (2) prerequisites and pinned versions; (3) the
  full `agent.py` implementation (CrewAI `Agent`/`Task`/`Crew` plus the
  promptfoo provider interface); (4) a `promptfooconfig.yaml` with a `file://`
  provider, a JSON-Schema `is-json` `defaultTest`, and a custom `python`
  assertion; (5) running `promptfoo eval` and `promptfoo view`; and (6) a
  multi-step red-team walkthrough configuring the same local file as a "Custom
  Target", plus application-context and plugin/strategy selection. Does NOT
  cover: CI gating, thresholds, baseline comparison, regression suites,
  defenses/guardrails, or findings triage/export.
- **Last updated**: Oct 12, 2026 (page footer: "Last updated on **Oct 12, 2026**
  by **renovate\[bot\]**") — same day as extraction.

## Extracted Claims

### Claim 1: promptfoo evaluates a locally-defined CrewAI agent by pointing a provider at a local Python file — `id: file://./agent.py` with a `label` and a `config.model` — rather than at a hosted model endpoint
- **Evidence**: The `promptfooconfig.yaml` provider block (`- id: file://./agent.py
  # Local file provider (make sure path is correct!)`), under the heading "Define
  the provider — here we point to our local agent.py". The page's own summary
  names the result: "Created a provider that Promptfoo can call."
- **Confidence**: settled (documented config; the `file://` prefix is a
  first-party promptfoo feature)
- **Quote**: "Created a provider that Promptfoo can call."
- **Our assessment**: This is the page's one structurally new, reusable element:
  it is the concrete mechanism for aiming an eval harness at *local agent logic*
  rather than a remote inference endpoint. It is the Python-native sibling of
  the custom-provider pattern already mined at
  `docs-promptfoo-testing-llm-chains.md` Claim 3 (a JS `callApi` that shells out
  to an external chain) and an instance of the pipeline-wide `file://` Python
  hook set documented at `docs-promptfoo-python-assertions.md` Claim 10. The
  CrewAI-specific parts (Agent/Task/Crew roles) are scaffolding; the contract is
  the provider indirection.

### Claim 2: The provider entrypoint is a module-level `call_api(prompt, options, context)` that bridges promptfoo's synchronous provider call to the async CrewAI runtime by wrapping `crew.kickoff_async(inputs={'job_requirements': prompt})` in `asyncio.run`, reads the model from `options["config"]["model"]`, and returns `{"output": result}`
- **Evidence**: The `agent.py` code block: the `call_api` docstring says it
  wraps the async function in a synchronous call for Promptfoo; the body does
  `config = options.get("config", {})`, `model = config.get("model",
  "openai/gpt-4.1")`, `result = asyncio.run(run_recruitment_agent(prompt,
  model=model))`, and returns `{"output": result}` on success.
- **Confidence**: settled (documented code)
- **Quote**: "Calls the CrewAI recruitment agent with the provided prompt.
  Wraps the async function in a synchronous call for Promptfoo."
- **Our assessment**: The `{"output": ...}` return and the `options["config"]`
  read are the provider-side contract; the `asyncio.run` bridge is the
  framework-specific detail (CrewAI's `kickoff_async` is async, promptfoo's
  Python provider call is sync). A reader adapting this to another async agent
  framework keeps the `call_api` shape and the `asyncio.run` bridge; only the
  inner agent invocation changes. Note the config default is hard-coded to
  `openai/gpt-4.1`, matching the page's pin below.

### Claim 3: Provider failures are returned as data, not raised — empty agent output, a missing JSON block, a JSON decode error, and any unexpected exception each return a `{"error": ...}` dict (parse failures also return `raw_output`), so a broken agent surfaces as a failed case rather than a harness crash
- **Evidence**: The `run_recruitment_agent` error branches
  (`{"error": "CrewAI agent returned an empty response."}`, `{"error": "No valid
  JSON block found in the agent's output.", "raw_output": output_text}`,
  `{"error": f"Failed to parse JSON from agent output: {str(e)}", "raw_output":
  json_string}`), and `call_api`'s outer `except` returning `{"error": f"An
  unexpected error occurred: {str(e)}"}` — with the inline comments "🔥 Catch and
  report any error as part of the output".
- **Confidence**: settled (documented code)
- **Quote**: "🔥 Catch and report any error as part of the output"
- **Our assessment**: This is a deliberate fail-closed-looking choice at the
  adapter layer: the provider never throws, so the eval run continues and the
  case is graded against an error object. It is orthogonal to the assertion
  design (Claims 4–5): an `is-json` schema check on an `{"error": ...}` output
  will not match the `candidates` schema and should fail — but the guide's "a
  gate that cannot fail is not a gate" discipline
  (`guide/05-llm-ops-reliability.md:655`) still says to *test* that an error
  return actually renders red rather than being silently absorbed. The `raw`
  field on the error path (`{"error": ..., "raw": result.get("raw_output",
  "")}`) exists to preserve unparseable output for debugging.

### Claim 4: The target agent's output shape is made a testable invariant via `defaultTest.assert` with `type: is-json` and an inline JSON Schema requiring a `candidates` array of objects (each with `name`/`experience` kinds of fields)
- **Evidence**: The `defaultTest:` block in `promptfooconfig.yaml`:
  `- type: is-json` with a `value:` JSON Schema declaring `candidates` as an
  array of objects, `required: ['candidates']`; the page's own summary lists
  "Ensure output is valid JSON" among the YAML test goals.
- **Confidence**: settled (documented config)
- **Quote**: "Ensure output is valid JSON" (page's "What did we just do?"
  summary) and, from the schema artifact, "required: ['candidates']"
- **Our assessment**: This is the page's answer to a free-form agent returning
  prose: wrap the shape requirement as a `defaultTest` schema assertion so every
  case is checked against it, then add case-specific behavior checks. The
  pattern is a conditioning-independent way to catch structural drift (the agent
  stops emitting JSON) separately from semantic quality. The schema is shallow —
  it constrains `candidates` to an array of objects but the shown `items`
  properties omit `required`, so it verifies the array/object shape more than the
  per-candidate field contract.

### Claim 5: A second, custom `python` assertion layers a runtime structural check — `"'candidates' in output and isinstance(output['candidates'], list)"` — on top of the JSON-schema `defaultTest`
- **Evidence**: The `tests:` entry `assert: - type: python # Custom Python check
  value: "'candidates' in output and isinstance(output['candidates'], list)"`.
- **Confidence**: settled (documented config)
- **Quote**: "'candidates' in output and isinstance(output['candidates'], list)"
- **Our assessment**: A small demonstration that the schema assertion and a
  custom Python predicate are complementary, not redundant: the schema enforces
  the contract globally while the Python check re-asserts one property on a
  specific case. It is a live use of the `python` assertion binding documented at
  `docs-promptfoo-python-assertions.md` (Claims 8, 10) — and, per that note's
  Claim 1, it inherits the runner's interpreter-resolution dependency, which this
  page does not mention. Treat the Python assertion here as a capability
  demonstration, not a gate recipe.

### Claim 6: The same local file provider is reused as a red-team target — Target Type "Custom Target", Target ID `file://./agent.py` — so the scan attacks the agent's own logic instead of a hosted model
- **Evidence**: Step 8's configuration ("Under **Target Type**, select: `Custom
  Target`", "Under Target ID, set the file reference to match your local
  provider: `file://./agent.py`") and the explicit consequence sentence.
- **Confidence**: settled (documented config + explanation)
- **Quote**: "Instead of hitting GPT-4 or cloud models, it will **directly test
  your `agent.py` logic**."
- **Our assessment**: This is the page's most transferable red-team idea: the
  target class is *local agent code reached through the same `file://` adapter
  used for eval*, so the eval harness and the red-team harness exercise one
  artifact. It is the local-code counterpart to the external-HTTP target class
  mined at `docs-promptfoo-chatbase-redteam.md` (Claims 3, 5): Chatbase
  red-teams an opaque remote endpoint via `http` + transforms; this page
  red-teams a `file://` adapter you own. The mechanism (reuse the provider id as
  the target id) is the novel bit.

### Claim 7: The red-team target sets `temperature: 0.5` in its custom config and a 500 ms inter-request delay, the latter to reduce load/avoid overloading the target
- **Evidence**: Step 8's "Custom Configuration (JSON)" default
  (`{"temperature": 0.5}`) and "Additional Configuration" → "Delay → 500", with
  the parenthetical explanation.
- **Confidence**: settled (documented config + explanation)
- **Quote**: "This adds 500ms between requests to simulate a real user and
  reduce overload."
- **Our assessment**: The delay is a probe-rate limit against a target that
  runs a full multi-agent `kickoff` per request — a concrete instance of the
  "don't let the scan DoS your own endpoint" discipline. Note the page does
  *not* pin `temperature: 0` for the red-team run the way determinism guidance
  would prefer (contrast `docs-promptfoo-chatbase-redteam.md` Claim 7, which
  pins `temperature: 0`); the shown default is `0.5`, so red-team verdicts here
  carry more run-to-run variance than the corpus's reproducibility discipline
  would advise. The page does not discuss reruns or variance.

### Claim 8: The red-team walkthrough requires supplying application context (purpose, key features, domain, system restrictions/rules) and explicitly uses mock/synthetic outputs so no real user data is exposed
- **Evidence**: Step 9's four context fields ("Main purpose of the
  application", "Key features provided", "Industry or domain", "System
  restrictions or rules") and the rule text.
- **Confidence**: settled (documented guidance)
- **Quote**: "Outputs are mock summaries and job recommendations, with no access
  to real user data."
- **Our assessment**: Two operational points worth generalizing. First, the
  system-rules field ("The system only responds to recruitment-related queries.
  It rejects non-recruitment prompts...") scopes the probe set so the scan does
  not waste attacks on out-of-domain inputs — the page states this rationale:
  "Providing this context helps the red teaming tool generate meaningful and
  realistic tests, avoiding time wasted on irrelevant attacks." Second, the
  mock-data stance keeps real PII out of the red-team corpus. Both align with the
  corpus's black-box-target discipline (chatbase Claim 9's mock-data note); the
  page gives no measurement of how much the context improves the scan.

### Claim 9 (explicit gap): The page contains **no** CI gating content — eval and red-team runs are manual terminal/browser actions (`promptfoo eval`, `promptfoo view`, `promptfoo redteam run` or "Run Now"), with no pipeline files, exit-code gates, baseline comparisons, or commit-triggered runs
- **Evidence**: Every execution step is interactive: Step 6 runs `promptfoo
  eval` by hand then `promptfoo view`; Step 7 opens a local web viewer; Step 11
  offers "Option 1: Save the YAML and run from terminal" or "Option 2: Click
  **Run Now** in the browser interface". No workflow/CI file, threshold, or
  baseline appears anywhere on the page.
- **Confidence**: settled (absence — verified by reading the full page; the
  Prospector also flagged this gap)
- **Quote**: "Option 2: Click **Run Now** in the browser interface for a
  simpler, visual run."
- **Our assessment**: This is the anti-over-claim the Prospector instructed us to
  preserve. Any guide framing of this page as an eval *gate* would be an
  extrapolation the source does not support. The page demonstrates harness
  *mechanics* (provider adapter, output contract, red-team target), not
  eval-in-CI *practice*. The seed's stated scope ("eval harnesses, CI gating,
  red-team/regression for LLM apps") is only partly served: red-team target
  wiring yes, CI gating no.

### Claim 10: The guide pins concrete version ranges rather than open-ended installs — Python 3.10–3.13, Node.js `>=22.22.0`, and `crewai>=1.15.22,<2`
- **Evidence**: The "Requirements" list ("Python 3.10–3.13", "Node.js
  `>=22.22.0`", "OpenAI API access for GPT-4.1") and the install command
  `python -m pip install "crewai>=1.15.22,<2"`.
- **Confidence**: settled (documented requirements)
- **Quote**: "Promptfoo requires Node.js `>=22.22.0`." and "Use Python 3.10
  through 3.13 for the CrewAI version used by this example."
- **Our assessment**: Pinned ranges are the reproducibility baseline the corpus
  asks for. The Python 3.10–3.13 window is a real constraint: per
  `docs-promptfoo-python-assertions.md` Claim 1, the runner must resolve its own
  Python too (the page's assertion uses `type: python`), so the adapter's
  interpreter and the agent's interpreter need to be the same compatible
  version — a coupling this page leaves implicit.

## Concrete Artifacts

All artifacts copied from the source page's code blocks
(https://www.promptfoo.dev/docs/guides/evaluate-crewai). Code blocks re-flowed
only at the newline level to restore line breaks lost in HTML extraction (same
convention as the sibling `docs-promptfoo-*` notes).

### Artifact 1: `agent.py` — CrewAI agent plus the promptfoo provider interface (verbatim, re-flowed)

```python
import asyncio
import json
import re
import textwrap
from typing import Any, Dict
from crewai import LLM, Agent, Crew, Task


def get_recruitment_agent(model: str = "openai/gpt-4.1") -> Crew:
    """
    Creates a CrewAI recruitment agent setup.
    This agent's goal: find the best Ruby on Rails + React candidates.
    """
    agent = Agent(
        role="Senior Recruiter specializing in technical roles",
        goal="Find the best candidates for a given set of job requirements and return the results in a valid JSON format.",
        backstory=textwrap.dedent("""
            You are an expert recruiter with years of experience in sourcing top talent for the tech industry.
            You have a keen eye for detail and are a master at following instructions to the letter, especially when it comes to output formats.
            You never fail to return a valid JSON object as your final answer.
        """).strip(),
        verbose=False,
        llm=LLM(model=model)
    )
    task = Task(
        description="Find the top 3 candidates based on the following job requirements: {job_requirements}",
        expected_output=textwrap.dedent("""
            A single valid JSON object. The JSON object must have a single key called "candidates".
            The value of the "candidates" key must be an array of JSON objects.
            Each object in the array must have the following keys: "name", "experience", and "skills".
            - "name" must be a string representing the candidate's name.
            - "experience" must be a string summarizing the candidate's relevant experience.
            - "skills" must be an array of strings listing the candidate's skills.
            Example of the expected final output:
            {
              "candidates": [
                {
                  "name": "Jane Doe",
                  "experience": "8 years of experience in Ruby on Rails and React, with a strong focus on building scalable web applications.",
                  "skills": ["Ruby on Rails", "React", "JavaScript", "PostgreSQL", "TDD"]
                }
              ]
            }
        """).strip(),
        agent=agent
    )
    # ✅ Combine agent + task into a Crew setup
    crew = Crew(agents=[agent], tasks=[task])
    return crew


async def run_recruitment_agent(prompt, model='openai/gpt-4.1'):
    """
    Runs the recruitment agent with a given job requirements prompt.
    Returns a structured JSON-like dictionary with candidate info.
    """
    crew = get_recruitment_agent(model)
    try:
        # ⚡ Trigger the agent to start working
        result = await crew.kickoff_async(inputs={'job_requirements': prompt})

        # The result might be a string, or an object with a 'raw' attribute.
        output_text = ""
        if result:
            if hasattr(result, 'raw') and result.raw:
                output_text = result.raw
            elif isinstance(result, str):
                output_text = result

        if not output_text:
            return {"error": "CrewAI agent returned an empty response."}

        # Use regex to find the JSON block, even with markdown
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```|({[\s\S]*})", output_text)
        if not json_match:
            return {
                "error": "No valid JSON block found in the agent's output.",
                "raw_output": output_text,
            }

        json_string = json_match.group(1) or json_match.group(2)
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse JSON from agent output: {str(e)}",
                "raw_output": json_string,
            }
    except Exception as e:
        # 🔥 Catch and report any error as part of the output
        return {"error": f"An unexpected error occurred: {str(e)}"}


def call_api(prompt: str, options: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the CrewAI recruitment agent with the provided prompt.
    Wraps the async function in a synchronous call for Promptfoo.
    """
    try:
        # ✅ Run the async recruitment agent synchronously
        config = options.get("config", {})
        model = config.get("model", "openai/gpt-4.1")

        result = asyncio.run(run_recruitment_agent(prompt, model=model))

        if "error" in result:
            return {"error": result["error"], "raw": result.get("raw_output", "")}

        return {"output": result}
    except Exception as e:
        # 🔥 Catch and return any error as part of the output
        return {"error": f"An error occurred in call_api: {str(e)}"}


if __name__ == "__main__":
    # 🧪 Simple test block to check provider behavior standalone
    print("✅ Testing CrewAI provider...")
    # 🔧 Example test prompt
    test_prompt = "We need a Ruby on Rails and React engineer with at least 5 years of experience."
    # ⚡ Call the API function with test inputs
    result = call_api(test_prompt, {}, {})
    # 📦 Print the result to console
    print("Provider result:", json.dumps(result, indent=2))
```

### Artifact 2: `promptfooconfig.yaml` (verbatim, re-flowed)

```yaml
description: 'CrewAI Recruitment Agent Evaluation'

# 📝 Define the input prompts (using variable placeholder)
prompts:
  - '{{job_requirements}}'

# ⚙️ Define the provider — here we point to our local agent.py
providers:
  - id: file://./agent.py # Local file provider (make sure path is correct!)
    label: CrewAI Recruitment Agent
    config:
      model: openai/gpt-4.1

# ✅ Define default tests to check the agent output shape and content
defaultTest:
  assert:
    - type: is-json # Ensure output is valid JSON
      value:
        type: object
        properties:
          candidates:
            type: array
            items:
              type: object
              properties:
                name:
                  type: string
                experience:
                  type: string
        required: ['candidates']

# 🧪 Specific test case to validate basic output behavior
tests:
  - description: 'Basic test for RoR and React candidates'
    vars:
      job_requirements: 'List top candidates with RoR and React'
    assert:
      - type: python # Custom Python check
        value: "'candidates' in output and isinstance(output['candidates'], list)"
```

### Artifact 3: Red-team Custom Target config (verbatim from Step 8)

```
Target Type: Custom Target
Target Name: crewAI-recruitment
Target ID: file://./agent.py

Custom Configuration (JSON):
{
  "temperature": 0.5
}

Delay: 500
Extension Hook: (empty)
```

### Artifact 4: Requirements and install commands (verbatim from "Requirements" / Step 3)

```
Python 3.10–3.13
Node.js >=22.22.0
python -m pip install "crewai>=1.15.22,<2"
npm install -g promptfoo
promptfoo eval --env-file .env
```

### Artifact 5: Red-team execution options (verbatim from Step 11)

```
Option 1: Save the YAML and run from terminal
promptfoo redteam run

Option 2: Click Run Now in the browser interface for a simpler, visual run.
```

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or dismissed before writing)

- **Dismissed — unrelated to a local `file://` provider adapter**:
  `docs-promptfoo-enterprise-findings-reports.md` (post-scan finding disposition
  / export matrix — the reporting layer *after* a scan; this page is the
  provider/scan-configuration layer and contains no findings content);
  `docs-promptfoo-enterprise-guardrails.md` (runtime guardrail *enforcement*
  HTTP endpoint — a deployment-time defense contract, not eval provider wiring);
  `docs-promptfoo-pi-scorer.md` (external model-graded scorer);
  `docs-litellm-batches-api.md` (batch rate limiting);
  `docs-langfuse-mcp-server.md` (docs MCP server);
  `blog-pagerduty-sre-agent-triage.md` (AI incident triage);
  `docs-google-sre-team-lifecycles.md`,
  `docs-google-sre-eliminating-toil.md`,
  `docs-google-sre-reliable-product-launches.md`, and
  `docs-google-sre-prodcast-04-09-ai-agents.md` (SRE org/toil/launch/agent-
  spectrum — no harness or provider-adapter overlap). None touch wrapping a
  self-hosted multi-agent app behind a `file://` provider or reusing it as a
  red-team target.

### Cross-references with existing source notes

- **Corroborates**:
  - `docs-promptfoo-testing-llm-chains.md` **Claim 3** — that note documents
    wrapping an external implementation behind a custom provider so promptfoo
    can evaluate a system it does not host: "A custom provider is a short
    Javascript file that defines a `callApi` function. This function can invoke
    your chain." This page is the Python-native form of the same pattern
    (`call_api` module at `file://./agent.py`), confirming the provider-adapter
    approach as the documented way to bring un-hosted logic under the harness.
    (Verified: #1575 Claim 3 ✓)
  - `docs-promptfoo-testing-llm-chains.md` **Claim 2** — the script provider
    (`exec:python langchain_example.py`) is the other documented route to an
    external chain; this page chooses the module/`call_api` route instead, so
    the two notes together bound the space of external-system adapters. (Verified:
    #1575 Claim 2 ✓)
  - `docs-promptfoo-python-assertions.md` **Claim 10** — that note establishes
    that `file://` is a uniform Python hook into *every* pipeline stage
    including providers ("You can use Python for any part of your eval pipeline
    without writing JavaScript"). This page is a concrete, in-use
    `file://provider.py` instance of that claim's provider stage. (Verified:
    #1499 Claim 10 ✓)
  - `docs-promptfoo-configuration-guide.md` **Claim 1** — that note fixes the
    output-transform order (`transformResponse` → test transform → assertion
    transform) and the fact that an assertion's input is *not* the model's raw
    output. This page does its output shaping (JSON parse) inside the provider
    `call_api` and returns `{"output": result}` already structured, so the
    `is-json` assertion receives the adapter's shaped value — a provider-stage
    instance of the same "know what the assertion actually receives" rule.
    (Verified: #1513 Claim 1 ✓)

- **Contradicts**: None. The only apparent surface — this page's red-team run
  leaves the default `temperature: 0.5` (Claim 7) where
  `docs-promptfoo-chatbase-redteam.md` Claim 7 pins `temperature: 0` for
  red-team reproducibility — is a difference in shown default across two
  vendor recipes, not two sources opposing each other on a predicate, and both
  recipes could be reconciled by setting `temperature: 0`. Per MINER.md §4a
  this is a conditioning choice, not a contradiction; no issue filed.
  CONTRADICTIONS.md has no relevant open `C-NNN` entry. (Verified: chatbase #1654
  Claim 7 = target body pins `stream: false` + `temperature: 0` ✓)

- **Extends**:
  - `docs-promptfoo-testing-llm-chains.md` — that note covers the *concept* of
    wrapping an external chain behind a script/custom provider. This page
    extends it with a complete, runnable Python example: the `asyncio.run`
    sync/async bridge (Claim 2), errors-returned-as-data (Claim 3), and — net
    new — reusing the same provider id as a red-team Custom Target (Claim 6).
  - `docs-promptfoo-python-assertions.md` — extends the `file://` Python hook
    model from the assertion stage (that note's focus) to the *provider* stage,
    and adds the runner-interpreter coupling the CrewAI adapter implies
    (Claims 2, 10) that the assertions page documents as a footgun (its
    Claim 1).
  - `docs-promptfoo-chatbase-redteam.md` — extends the corpus's red-team
    external-target material to a second target class: not an opaque remote HTTP
    endpoint (that note's `http` target) but a `file://` adapter over code you
    own, reached by reusing the eval provider id as the red-team target id
    (Claim 6).

- **Novel**:
  1. **The CrewAI-specific `file://` provider binding** (Claims 1–2) — no
     existing note covers driving a CrewAI multi-agent `kickoff_async` through a
     promptfoo provider, nor the `asyncio.run` sync bridge.
  2. **Errors-returned-as-data at the provider layer** (Claim 3) — the empty/
     no-JSON/decode/exception branches all return `{"error": ...}`.
  3. **Reusing the eval provider id as a red-team Custom Target** (Claim 6) —
     the same `file://./agent.py` drives both eval and red-team, so one artifact
     is exercised by both harnesses.
  4. **The JSON-Schema `is-json` `defaultTest` + custom `python` assertion
     pairing** (Claims 4–5) as a worked agent-output contract.
  5. **The explicit CI-gating gap** (Claim 9) — documented here as a negative
     finding so synthesis does not read a gate into a manual walkthrough.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "A green eval is not evidence until you
  can name what it measured" (`guide/05-llm-ops-reliability.md:567`) and "A gate
  that cannot fail is not a gate" (`:655`)**: add the provider-adapter pattern as
  the mechanism for gating a *self-hosted agent* rather than a hosted model.
  Cite `file://./agent.py` + `call_api(prompt, options, context)` (Claim 2) and
  the errors-as-data return (Claim 3), cross-linking
  `docs-promptfoo-testing-llm-chains.md` Claim 3. State plainly, per Claim 9,
  that this source gives the *harness wiring* only — it has no thresholds, no
  baselines, and no CI job — so a gate built from it must supply its own
  fail criteria and commit-triggered run.
- **Chapter 05 — "Read the assert's own defaults before trusting its verdict"
  (`:443`) / output-contract design**: add the JSON-Schema `is-json`
  `defaultTest` (Claim 4) as a concrete way to make an agent's output *shape* a
  testable invariant, with the custom `python` assertion (Claim 5) as the
  behavior check layered on top. Note the schema shown is shallow (no per-item
  `required`), so it catches structural drift more than field-level contract.
- **Chapter 06 (Security & Trust) — "Red-teaming as a CI gate"
  (`guide/06-security-and-trust.md:120`) and "Continuous adversarial testing is
  mandatory" (`:122`)**: add the local-code target class (Claim 6) — pointing the
  red-team Custom Target at the same `file://` provider used for eval — beside
  the external-HTTP target class documented at
  `docs-promptfoo-chatbase-redteam.md` Claims 3/5. Include the probe-rate
  caveat (Claim 7: 500 ms delay to avoid overloading a full multi-agent
  `kickoff` per request) and the mock-data / system-rules scoping (Claim 8).
  Reiterate that this page performs these runs **manually** (Claim 9), so Ch06's
  "run before each deployment" is not satisfied by the source as written.
- **Chapter 03 (Runbooks and Agents) — "Agent evaluation in production"
  (`guide/03-runbooks-and-agents.md:268`)**: cite the provider-adapter contract
  (Claims 1–2) as the reusable way to exercise an agent framework under an eval
  harness without instrumenting the framework itself; the CrewAI `Agent`/`Task`
  roles are scaffolding, the `call_api` indirection is the transferable part.

## Extraction Notes

- Source read in full via WebFetch of the single page
  (https://www.promptfoo.dev/docs/guides/evaluate-crewai). Footer: "Last updated
  on **Oct 12, 2026** by **renovate\[bot\]**"; no canonical first-published date,
  so `date_published` carries the last-updated date (same convention as the
  sibling `docs-promptfoo-*` notes #1513, #1610, #1654).
- Two Prospector triage comments on the issue disagree on novelty (medium vs low)
  but agree on type (`triaged:text`, docs) and on the key question (the
  provider-adapter contract vs the CrewAI binding). This note follows the
  *second, more specific* comment's extraction guidance: extract the provider
  adapter, the JSON-Schema/output contract, the red-team target config, and the
  pinned ranges; treat CrewAI product details as scaffolding; and — per its
  explicit instruction — do **not** over-claim CI gating (Claim 9 records the
  absence).
- No sub-pages followed. The page's only substantive external links are CrewAI's
  GitHub repo and sibling promptfoo integration guides (OpenAI Assistants,
  LangGraph, Google ADK); the provider/assertion/red-team surfaces they would
  deepen are already mined in the corpus and cited rather than re-extracted.
- Quotes verified character-for-character against the fetched rendered content
  before writing. Code blocks re-flowed only at the newline level to restore line
  breaks lost in HTML extraction (same convention as `docs-promptfoo-testing-
  llm-chains.md` and `docs-promptfoo-python-assertions.md`). Where a `Quote`
  field cites a code/config fragment, the fragment is copied verbatim; where the
  meaningful content spanned non-adjacent lines, the claim is stated in prose and
  the full block placed in Concrete Artifacts rather than splicing.
- Cross-references: every cited claim number was re-read and verified per
  MINER.md §4b before citation — testing-llm-chains #1575 Claims 2 & 3;
  python-assertions #1499 Claims 1 & 10; configuration-guide #1513 Claim 1;
  chatbase-redteam #1654 Claim 7 (and its Claim 3/5 by section context). All 10
  candidate paths from `miner-related-notes.md` were cited or explicitly
  dismissed in the block above.
- `confidence_overall` = `emerging`: first-party vendor documentation is
  authoritative for the documented config and code shapes (individual claims
  graded `settled` where they are direct code/config facts), but the page is a
  thin, single-example walkthrough with no metrics, no run results, and no CI
  content; its operational value (the provider-adapter-for-local-agents pattern)
  is our synthesis across the page and the surrounding corpus. Consistent with
  the sibling promptfoo notes.
- `registry/sources.json` and `registry/claims-index.json` were intentionally not
  edited: they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
