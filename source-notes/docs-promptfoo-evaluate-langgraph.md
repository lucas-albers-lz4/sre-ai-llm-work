---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-langgraph
source_type: docs
title: "Promptfoo: Evaluate LangGraph — Typed Graph State Behind a file:// Provider and a Reused Red-Team Custom Target"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-23
date_extracted: 2026-10-23
last_checked: 2026-10-23
status: current
confidence_overall: emerging
issue: "#1696"
---

# Promptfoo: Evaluate LangGraph

> A vendor walkthrough that brings a compiled LangGraph `StateGraph` with a
> typed Pydantic `ResearchState` under promptfoo by exposing it as a
> `file://./provider.py` Python provider — and the one genuine delta over the
> CrewAI sibling is that the adapter hands the graph's **structured final state
> straight back** (`{"output": result}`) instead of regex-extracting JSON from
> free text, so the `is-json` `defaultTest` schema is a direct state-contract
> check. The same provider file is then reused as a red-team "Custom Target".
> The walkthrough is otherwise the same template as the CrewAI page: a mocked
> three-node agent, one test case, a claimed 100% pass rate, and **no** CI
> gating, thresholds, baselines, or graph-internal observability.

## Source Context

- **Type**: docs (vendor recipe guide — promptfoo "Evaluate LangGraph: Red
  Teaming and Testing Stateful Agents", under Evals → Guides → Integrations;
  auto-discovered from the registered `promptfoo-docs` site-crawl seed). Single
  guide page; no sub-pages followed.
- **Author credibility**: Promptfoo, the LLM eval / red-team vendor. First-party
  documentation of its own `file://` Python provider and red-team "Custom
  Target" surfaces — authoritative for the documented code/config shapes and
  directly checkable against an installed CLI, but vendor-positioned: no run
  results beyond a screenshot, no metrics, no independent validation, and the
  LangGraph binding is demonstrated only against the vendor's own scaffolded
  example.
- **Scope**: Covers (1) an optional `npx promptfoo@latest init --example
  integration-langgraph` scaffold; (2) requirements and pip-install version
  ranges; (3) the full `agent.py` (`ResearchState`, a three-node `StateGraph`,
  and an `asyncio.run(app.ainvoke(...))` runner); (4) the `provider.py`
  `call_api` adapter; (5) a `promptfooconfig.yaml` with `file://` provider, an
  `is-json` schema `defaultTest`, and one `python` assertion; (6) manual `eval`
  / `view` runs; and (7) a multi-step red-team walkthrough that points a "Custom
  Target" at `file://./provider.py`. Does NOT cover: CI gating, thresholds,
  baseline comparison, regression suites, cost/latency SLOs, graph-node or
  checkpoint inspection, OTel/trace assertions, or findings triage/export.
- **Last updated**: Oct 23, 2026 (page footer: "Last updated on **Oct 23, 2026**
  by **renovate\[bot\]**") — same day as extraction, so `date_published` carries
  the last-updated date (same convention as the sibling `docs-promptfoo-*`
  notes).

## Extracted Claims

### Claim 1: promptfoo positions itself as running structured evaluations and red-team scans over a LangGraph agent, and the whole setup can be scaffolded from a single `--example` command
- **Evidence**: The intro states the eval surfaces (test prompts, output
  verification, benchmarking, red teaming) and the Highlights list walks setup →
  provider/agent files → YAML tests → runs → optional red team. The scaffold
  command is given up front and is said to create `promptfooconfig.yaml`, agent
  scripts, and test cases.
- **Confidence**: settled (documented product claim + scaffold command)
- **Quote**: "defining test prompts, verifying outputs, benchmarking performance, and performing red team testing to uncover biases, safety gaps, and robustness issues."
- **Our assessment**: The scope sentence promises "benchmarking performance",
  but the page contains no latency, cost, or throughput measurement — only a
  one-case pass rate. Treat "benchmarking" as marketing language, not a
  documented capability of this walkthrough. The scaffold command is the
  genuinely reusable onboarding shortcut.

### Claim 2: The example pins a concrete version floor — `langgraph>=1.2.11,<2`, `langchain-openai>=1.6.2,<2`, `pydantic>=2.13.5,<3`, Python 3.10–3.12, and Node.js `>=22.22.0`
- **Evidence**: The "Requirements" list ("Python 3.10-3.12 tested", Node
  `>=22.22.0`, Node 24 LTS recommended) and the Step 3 install command with
  upper bounds on all three Python packages.
- **Confidence**: settled (documented requirements)
- **Quote**: "Python 3.10-3.12 tested"
- **Our assessment**: Bounded ranges are the reproducibility baseline the corpus
  asks for, and the upper bounds (`<2`, `<3`) are stronger than an open-ended
  `pip install langgraph`. Two caveats the page leaves implicit: the `python`
  assertion means promptfoo must resolve its own interpreter (the coupling
  documented in `docs-promptfoo-python-assertions.md` Claim 1), and the
  requirements text names "GPT-5-mini" while the code defaults to `gpt-4o`
  (Claim 5) — so pinning the framework does not pin the model actually used.

### Claim 3: The agent is a compiled `StateGraph` over a typed Pydantic `ResearchState` (`query`, `raw_info`, `summary`) with three linear nodes — `search_info` → `summarize_info` → `output_summary`
- **Evidence**: `class ResearchState(BaseModel)` declares the three string
  fields; `graph = StateGraph(ResearchState)`; the three nodes are registered
  with `add_node` and chained with `add_edge`; entry/finish points are set and
  `graph.compile()` returns the app.
- **Confidence**: settled (documented code)
- **Quote**: `graph = StateGraph(ResearchState)`
- **Our assessment**: This is the LangGraph-specific binding the Prospector asked
  for: state is declared as a typed model rather than CrewAI's free-text
  `expected_output` prompt. The graph is strictly linear (no conditional edges,
  no fan-out, no tools, no checkpointer), so it demonstrates the framework API
  but not the *stateful multi-agent graph* behaviour the intro advertises.

### Claim 4: The provider returns the graph's structured final state directly (`{"output": result}`), with no regex or JSON parsing step — the key delta from the CrewAI adapter
- **Evidence**: `run_research_agent` does
  `result = asyncio.run(app.ainvoke(ResearchState(query=prompt)))` and returns
  `result`; `call_api` wraps it as `return {"output": result}`. There is no
  `re.search`, no `json.loads`, and no extraction branch anywhere in
  `provider.py`, unlike the CrewAI guide's regex ` ```json ` / `{...}` match.
- **Confidence**: settled (documented code; direct comparison with the sibling
  page)
- **Quote**: `return {"output": result}`
- **Our assessment**: Yes to the Prospector's question (a): a typed state makes
  the output contract cheaper to assert because the adapter does not have to
  recover JSON from prose — the graph result is already the object the schema
  describes. But the page never serializes it (`model_dump()` / `json.dumps`),
  and promptfoo's `is-json` assertion expects JSON, so the shown code relies on
  the harness coercing a Pydantic object. That is an unstated dependency, not a
  stronger guarantee. "Stronger" is also overstated: the schema only checks
  field names/types, and the only behavioural test is `'summary' in output`
  (Claim 6).

### Claim 5: The adapter contract is a module-level `call_api(prompt, options, context)` that reads `options["config"]["model"]` (default `"gpt-4o"`) and `apiBaseUrl`, passes them into the graph runner, and returns exceptions as data via `{"error": str(e)}`
- **Evidence**: `config = options.get("config", {})`;
  `model=config.get("model", "gpt-4o")`; `base_url=config.get("apiBaseUrl")`;
  the outer `except Exception as e:` returns `{"error": str(e)}`. The docstring
  calls it the "Main API function that external tools or systems will call".
- **Confidence**: settled (documented code)
- **Quote**: `model=config.get("model", "gpt-4o"),`
- **Our assessment**: Structurally identical to the CrewAI adapter
  (`docs-promptfoo-evaluate-crewai.md` Claims 2–3), including the
  errors-returned-as-data choice. The delta is only the inner call — a compiled
  graph's `ainvoke` rather than `crew.kickoff_async` — which confirms the
  adapter shape is framework-agnostic. The `gpt-4o` default contradicts the
  page's own "GPT-5-mini" requirement (Claim 2), so a reader following the code
  does not run the model the requirements describe.

### Claim 6: The `is-json` `defaultTest` pins the three `ResearchState` fields as a global output contract, and a single case adds a `python` assertion that merely checks `'summary' in output`
- **Evidence**: `defaultTest: assert: - type: is-json` with schema properties
  `query`, `raw_info`, `summary` (all `string`) and
  `required: ['query', 'raw_info', 'summary']`; the one test case asserts
  `type: python`, `value: "'summary' in output"`.
- **Confidence**: settled (documented config)
- **Quote**: `required: ['query', 'raw_info', 'summary']`
- **Our assessment**: This answers the Prospector's (a) in the affirmative: the
  schema is bound to the typed state's fields, not to regex-extracted text, so it
  is a genuine state-contract check. It is still a *shape* check: it cannot tell
  a real summary from a mock one, and the `python` assertion is nearly redundant
  with the schema's `required`. The pairing mirrors the CrewAI note's Claims 4–5
  almost exactly, reinforcing that the assertion primitives are already
  documented and only the binding is new.

### Claim 7: Despite the "stateful" framing, the eval observes only the final state — the provider exposes no intermediate node outputs, checkpoints, or traces, and the page defers state inspection to a "next step"
- **Evidence**: `call_api` returns a single `{"output": result}`; nothing reads
  graph nodes, checkpoints, or OTel spans. The "Next Steps" section says to
  "Add a checkpoint saver to inspect intermediate states", i.e. it is not part
  of the eval as shipped.
- **Confidence**: emerging (negative finding from reading the full code/config;
  the page's own next-step advice corroborates the gap)
- **Quote**: "Add a checkpoint saver to inspect intermediate states"
- **Our assessment**: This is the most important limit on the "stateful graph"
  claim. In-process execution makes internals *reachable*, but this adapter does
  not reach them — so the page is a final-output eval of a graph, not a
  trajectory or state-transition eval. Contrast `docs-promptfoo-evaluate-google-adk.md`
  Claims 1 and 6, where an in-process provider deliberately returns session
  state, plugin events, artifacts, and OTel spans; LangGraph's typed state is an
  obvious place to do the same, and this page does not.

### Claim 8: The sample agent is deliberately mocked and the only reported metric is a one-case "Pass rate: 100%" — no failure data, evaluation set, or real search integration
- **Evidence**: `search_info` returns a hard-coded f-string prefixed `(Mock)`
  behind `# TODO: Replace with real search API integration`; `tests:` contains a
  single "Basic research test"; Step 7's narrative lists "Pass rate: 100%" as the
  outcome.
- **Confidence**: settled (documented code + stated result)
- **Quote**: "Pass rate: 100%"
- **Our assessment**: A 1/1 pass rate is not evidence of agent quality, and the
  mocked search node means the thing being graded is largely the summary prompt.
  This matches the CrewAI sibling's thin-evidence profile and should be cited as
  an onboarding template, not as evaluation methodology. The corpus rule "a green
  eval is not evidence until you can name what it measured"
  (`guide/05-llm-ops-reliability.md:567`) applies directly.

### Claim 9: The red-team flow reuses the same local provider as a "Custom Target" (`file://./provider.py`), with `temperature: 0.5` and a 500 ms inter-request delay
- **Evidence**: Step 9 says to choose Target Type "Custom Target", name the
  target `research-agent`, and set Target ID to `file://./provider.py`; the
  Custom Configuration example is `{"temperature": 0.5}`; Additional
  Configuration sets `Delay: 500`.
- **Confidence**: settled (documented config + explanation)
- **Quote**: "This adds 500ms between requests to simulate a real user and reduce overload."
- **Our assessment**: The reuse-the-provider-as-target mechanism is identical to
  the CrewAI note's Claim 6, so it is not new to the corpus; what this page adds
  is a second framework instance proving the mechanism is not CrewAI-specific.
  The 500 ms delay is a sane probe-rate cap for an agent that runs an LLM call
  per request. The `temperature: 0.5` default is *not* pinned to 0, so red-team
  verdicts carry run-to-run variance; as in the CrewAI note (Claim 7) this is a
  conditioning difference from `docs-promptfoo-chatbase-redteam.md` Claim 7, not
  a contradiction.

### Claim 10: The red-team wizard requires application context (purpose, features, domain, restrictions) to focus attack generation, and the example declares that all outputs are mock data with no access to private information
- **Evidence**: Step 10 lists the four context fields and their filled values
  (research assistant; query processing/summarization/structured JSON; research
  and education; only research prompts, no unethical queries, mock data only).
- **Confidence**: settled (documented guidance)
- **Quote**: "Providing this context helps the red teaming tool generate meaningful and focused attacks, avoiding time wasted on irrelevant prompts."
- **Our assessment**: Same scoping discipline as the CrewAI note's Claim 8:
  domain/rules context narrows the probe space, and the mock-data stance keeps
  real user content out of the attack corpus. The page gives no measurement of
  the effect, so the claim is vendor guidance rather than evidence.

### Claim 11 (explicit gap): The page contains **no** CI gating, thresholds, baselines, cost/latency SLOs, or commit-triggered runs — every eval and red-team run is a manual CLI or browser action
- **Evidence**: Execution is `npx promptfoo eval` (Step 7), `npx promptfoo view`
  (Steps 7–8), then `npx promptfoo redteam run` or the browser "Run Now" option
  (Step 12); there is no workflow file, exit-code gate, threshold, or baseline
  anywhere on the page, and the Conclusion claims only a "repeatable" workflow.
- **Confidence**: settled (absence — verified by reading the full page; the
  Prospector flagged the same gap)
- **Quote**: "npx promptfoo redteam run"
- **Our assessment**: This is the anti-over-claim the Prospector required. The
  page demonstrates harness *wiring*, not eval *practice*: no gate can be built
  from it without supplying fail criteria and CI integration. It also cannot
  serve the seed's "CI gating" scope. The "repeatable" language in the
  conclusion refers to re-running the same config, not to reproducibility
  controls (no `--repeat`, no `--no-cache`, no pinned model).

## Concrete Artifacts

All artifacts copied from the source page's code blocks
(https://www.promptfoo.dev/docs/guides/evaluate-langgraph). Code blocks are
re-flowed only at the newline level to restore line breaks lost in HTML
extraction (same convention as the sibling `docs-promptfoo-*` notes). Nothing
is altered semantically.

### Artifact 1: `agent.py` — Pydantic state, three-node `StateGraph`, and runner (verbatim, re-flowed)

```python
import asyncio
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

# Define the data structure (state) passed between nodes in the graph
class ResearchState(BaseModel):
    query: str            # The original research query
    raw_info: str = ""    # Raw fetched or mocked information
    summary: str = ""     # Final summarized result

# Function to create and return the research agent graph
def get_research_agent(model="gpt-4o", base_url=None):
    # ChatOpenAI reads OPENAI_API_KEY from the environment when initialized
    llm = ChatOpenAI(model=model, base_url=base_url)

    # Create a stateful graph with ResearchState as the shared state type
    graph = StateGraph(ResearchState)

    # Node 1: Simulate a search function that populates raw_info
    def search_info(state: ResearchState) -> ResearchState:
        # TODO: Replace with real search API integration
        mock_info = f"(Mock) According to recent sources, the latest trends in {state.query} include X, Y, Z."
        return ResearchState(query=state.query, raw_info=mock_info)

    # Node 2: Use the LLM to summarize the raw_info content
    def summarize_info(state: ResearchState) -> ResearchState:
        prompt = f"Summarize the following:\n{state.raw_info}"
        response = llm.invoke(prompt)  # Call the LLM to get the summary
        return ResearchState(query=state.query, raw_info=state.raw_info, summary=response.text)

    # Node 3: Format the final summary for output
    def output_summary(state: ResearchState) -> ResearchState:
        final_summary = f"Research summary for '{state.query}': {state.summary}"
        return ResearchState(query=state.query, raw_info=state.raw_info, summary=final_summary)

    # Add nodes to the graph
    graph.add_node("search_info", search_info)
    graph.add_node("summarize_info", summarize_info)
    graph.add_node("output_summary", output_summary)

    # Define the flow between nodes (edges)
    graph.add_edge("search_info", "summarize_info")
    graph.add_edge("summarize_info", "output_summary")

    # Set the starting and ending points of the graph
    graph.set_entry_point("search_info")
    graph.set_finish_point("output_summary")

    # Compile the graph into an executable app
    return graph.compile()

# Function to run the research agent with a given query prompt
def run_research_agent(prompt, model="gpt-4o", base_url=None):
    # Get the compiled graph application
    app = get_research_agent(model=model, base_url=base_url)

    # Run the asynchronous invocation and get the result
    result = asyncio.run(app.ainvoke(ResearchState(query=prompt)))

    return result
```

### Artifact 2: `provider.py` — the `file://` adapter (verbatim, re-flowed)

```python
from agent import run_research_agent

# Main API function that external tools or systems will call
def call_api(prompt, options, context):
    """
    Executes the research agent with the given prompt.

    Args:
        prompt (str): The research query or question.
        options (dict): Provider configuration, including model and apiBaseUrl.
        context (dict): Contextual information (currently unused).

    Returns:
        dict: A dictionary containing the agent's output or an error message.
    """
    try:
        # Run the research agent and get the result
        config = options.get("config", {})
        result = run_research_agent(
            prompt,
            model=config.get("model", "gpt-4o"),
            base_url=config.get("apiBaseUrl"),
        )

        # Wrap and return the result inside a dictionary
        return {"output": result}
    except Exception as e:
        # Handle any exceptions and return a provider error
        return {"error": str(e)}

# If this file is run directly, execute a simple test
if __name__ == "__main__":
    print("✅ Testing Research Agent provider...")
    test_prompt = "latest AI research trends"
    result = call_api(test_prompt, {}, {})
    print("Provider result:", result)
```

### Artifact 3: `promptfooconfig.yaml` (verbatim, re-flowed)

```yaml
# Description of this evaluation job
description: 'LangGraph Research Agent Evaluation'

# List of input prompts to test the provider with
prompts:
  - '{{input_prompt}}'

# Provider configuration
providers:
  - id: file://./provider.py
    label: Research Agent

# Default test assertions
defaultTest:
  assert:
    - type: is-json
      value:
        type: object
        properties:
          query:
            type: string
          raw_info:
            type: string
          summary:
            type: string
        required: ['query', 'raw_info', 'summary']

# Specific test cases
tests:
  - description: 'Basic research test'
    vars:
      input_prompt: 'latest AI research trends'
    assert:
      - type: python
        value: "'summary' in output"
```

### Artifact 4: Requirements and install commands (version strings verbatim from "Requirements" / Step 3; bullet markers removed)

```
Python 3.10-3.12 tested
Node.js >=22.22.0 (Node.js 24 LTS recommended)
OpenAI API access (for GPT-5-mini and other OpenAI models)

python3 -m pip install 'langgraph>=1.2.11,<2' 'langchain-openai>=1.6.2,<2' 'pydantic>=2.13.5,<3'
npm install -g promptfoo
```

### Artifact 5: Red-team Custom Target config (verbatim from Step 9)

```
Target Type: Custom Target
Target Name: research-agent
Target ID: file://./provider.py

Custom Configuration (JSON):
{
  "temperature": 0.5
}

Delay: 500
Extension Hook: (empty)
```

### Artifact 6: Red-team application context (list items verbatim from Step 10; field labels normalized)

```
Main purpose of the application:
- Answers research queries and summarizes relevant information.
- Focuses on generating structured outputs with query, raw_info, and summary.
- Provides helpful, clear, and concise summaries without adding unsafe or speculative content.

Key features provided:
- Query processing and information gathering.
- Summarization of raw research data.
- Clear, structured JSON output.
- Filtering irrelevant or harmful information.

Industry or domain:
- Research, Education, Content Generation, Knowledge Management.

System restrictions or rules:
- The system only responds to research-related prompts.
- It avoids answering unethical, illegal, or sensitive queries.
- All outputs are mock data—it has no access to real-time or private information.
```

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or explicitly dismissed before writing)

- **Dismissed — unrelated to a `file://` provider adapter or a LangGraph binding**:
  `docs-promptfoo-enterprise-findings-reports.md` (post-scan finding
  disposition/export matrix — a reporting layer *after* a scan; this page has no
  findings content); `docs-promptfoo-enterprise-guardrails.md` (runtime
  guardrail enforcement HTTP endpoint — deployment-time defense, not eval
  wiring); `docs-promptfoo-pi-scorer.md` (an external model-graded scorer, not a
  provider adapter); `docs-litellm-evals-api.md` (gateway-hosted Evaluations
  API); `docs-litellm-batches-api.md` (batch rate limiting);
  `docs-langfuse-mcp-server.md` (docs MCP server);
  `blog-pagerduty-sre-agent-triage.md` (AI incident triage);
  `docs-google-sre-team-lifecycles.md`, `docs-google-sre-eliminating-toil.md`
  (SRE org design and toil). None concern wrapping a stateful graph agent behind
  a local Python provider or reusing it as a red-team target.
- **Cited — `docs-promptfoo-evaluate-openai-agents-python.md`**: see Extends
  below. It is the closest agent-framework sibling in the candidate list (a
  Python-SDK agent wrapped as a provider), but its concern is the OTel/tracing
  bridge and trajectory assertions (Claims 1–6), none of which this page
  implements (Claim 7 above).

### Cross-references with existing source notes

- **Corroborates**:
  - `docs-promptfoo-evaluate-crewai.md` **Claim 1** — a local agent is brought
    under promptfoo by pointing a provider at a Python file rather than a hosted
    model endpoint: "`id: file://./agent.py`". This page uses the identical
    mechanism with `id: file://./provider.py` (Artifact 3). (Verified: #1681
    Claim 1 ✓)
  - `docs-promptfoo-evaluate-crewai.md` **Claim 2** — that note establishes the
    module-level `call_api(prompt, options, context)` signature, the
    `options["config"]` read, and the `{"output": ...}` return; this page's
    `provider.py` is the same contract with `run_research_agent` substituted for
    the CrewAI invocation (Claim 5). (Verified: #1681 Claim 2 ✓)
  - `docs-promptfoo-evaluate-crewai.md` **Claim 3** — provider failures are
    returned as data, not raised, so a broken agent becomes a failed case rather
    than a harness crash. This page's outer `except Exception as e: return
    {"error": str(e)}` is the simpler instance of the same choice (Claim 5).
    (Verified: #1681 Claim 3 ✓)
  - `docs-promptfoo-evaluate-crewai.md` **Claim 6** — the eval provider is
    reused as the red-team "Custom Target", so one artifact is exercised by both
    harnesses. Here the target is `file://./provider.py` (Claim 9). (Verified:
    #1681 Claim 6 ✓)
  - `docs-promptfoo-evaluate-crewai.md` **Claim 9** — the page has no CI gating,
    no thresholds/baselines, and no commit-triggered runs; only manual
    CLI/browser actions. This page is the same (Claim 11). (Verified: #1681
    Claim 9 ✓)
  - `docs-promptfoo-evaluate-openai-agents-python.md` **Claim 14** — that page
    likewise carries an explicit "no CI gating" gap; the three agent-framework
    recipes in the corpus (CrewAI, OpenAI Agents Python, LangGraph) now agree on
    this absence, which strengthens the negative finding. (Verified: #1707
    Claim 14 ✓)
  - `docs-promptfoo-testing-llm-chains.md` **Claim 3** — a custom provider is the
    documented way to invoke an implementation promptfoo does not host: "A
    custom provider is a short Javascript file that defines a `callApi`
    function. This function can invoke your chain." This page is the Python
    `call_api` form of the same pattern. (Verified: #1575 Claim 3 ✓)

- **Contradicts**: None. The only surface is this page's `temperature: 0.5` for
  the red-team run (Claim 9) versus the `temperature: 0` in
  `docs-promptfoo-chatbase-redteam.md` Claim 7 — a difference in shown default
  across two vendor recipes, reconcilable by setting `temperature: 0`, hence a
  conditioning choice not a contradiction (MINER.md §4a). No open `C-NNN` entry
  is relevant. The CrewAI note's regex-extraction vs this page's direct state
  return (Claim 4) is a framework difference, not opposing claims. No
  contradiction issue filed.

- **Extends**:
  - `docs-promptfoo-evaluate-crewai.md` — that note documents the local
    `file://` provider adapter and the JSON-Schema `defaultTest` over
    regex-extracted free text. This page extends it with a second framework
    binding: a typed Pydantic state handed back directly (Claims 3–4), which
    removes the extraction step and makes the schema a state-contract check.
    It also confirms the adapter contract is framework-agnostic (Claim 5) — the
    synthesis the Prospector asked for.
  - `docs-promptfoo-evaluate-google-adk.md` **Claim 1** — the ADK note argues an
    in-process Python provider is what makes sessions, artifacts, plugin events,
    and native spans assertable. This page is a counter-example to reading that
    as automatic: its provider is also in-process, yet it surfaces only the final
    state (Claim 7), showing that in-process is necessary but not sufficient for
    graph-internal eval. (Verified: google-adk Claim 1 ✓)
  - `docs-promptfoo-evaluate-google-adk.md` **Claim 12** — the harness-selection
    rule (use the framework's own eval for framework-native metrics; use
    promptfoo for cross-framework comparison, red teams on the same surface, or
    OTel trace assertions). This page is a plain promptfoo eval + red-team
    instance with no `langgraph`-native eval comparison, so it does not exercise
    the rule's first branch. (Verified: google-adk Claim 12 ✓)
  - `docs-promptfoo-evaluate-openai-agents-python.md` **Claim 1** — that note
    explains that when promptfoo lacks a first-class provider for a Python
    framework SDK, the SDK is wrapped as a Python provider. This page applies the
    same reasoning to LangGraph: there is no native LangGraph provider, so the
    compiled graph is wrapped in `provider.py`. (Verified: #1707 Claim 1 ✓)
  - `docs-promptfoo-testing-llm-chains.md` **Claim 2** — the `exec:` script
    provider is the alternative external-system route; this page chooses the
    module/`call_api` route, so the two notes together bound the adapter space
    (as the CrewAI note also observed). (Verified: #1575 Claim 2 ✓)

- **Novel**:
  1. **The LangGraph `StateGraph` + typed Pydantic state binding** (Claim 3) —
     no existing note drives a compiled graph through a promptfoo provider.
  2. **Direct structured-state return instead of regex extraction** (Claim 4) —
     the concrete delta from the CrewAI adapter, and the reason the `is-json`
     `defaultTest` is a state-contract check rather than a prose-parsing
     recovery check.
  3. **The "in-process but final-output-only" limit** (Claim 7) — a negative
     finding that qualifies the ADK note's in-process recommendation: reachable
     internals are not asserted internals. No existing note states this.
  4. **The `gpt-4o`-default vs "GPT-5-mini" requirement inconsistency** (Claims
     2, 5) — a concrete example of framework pinning without model pinning.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "A green eval is not evidence until you
  can name what it measured" (`guide/05-llm-ops-reliability.md:567`) and "A gate
  that cannot fail is not a gate" (`:655`)**: add the typed-state provider
  pattern as the LangGraph instance of the local-agent adapter already cited from
  `docs-promptfoo-evaluate-crewai.md`. Specifically: `file://./provider.py` +
  `call_api` returning the graph result directly (Claims 4–5) removes the
  regex-extraction failure mode, but the source still supplies no thresholds,
  baselines, or CI job (Claim 11) and its only test is a 1/1 green (Claim 8), so
  a gate built from it must supply its own fail criteria. Use it as the
  counter-example to "pass rate = quality".
- **Chapter 05 — "Read the assert's own defaults before trusting its verdict"
  (`:443`) / output-contract design**: add the `is-json` schema bound to
  `ResearchState`'s `query`/`raw_info`/`summary` (Claim 6) beside the CrewAI
  `candidates` schema. Note the explicit caveat: the shown adapter returns a
  Pydantic object without serializing it, so the state-contract check depends on
  harness coercion that the page does not document; and the schema validates
  shape, not summary quality.
- **Chapter 06 (Security & Trust) — "Red-teaming as a CI gate"
  (`guide/06-security-and-trust.md:120`)**: add this page as a *second* worked
  instance of the local-code red-team target class already cited from
  `docs-promptfoo-evaluate-crewai.md` Claim 6 — same `file://` provider reused as
  a Custom Target (Claim 9). Include the 500 ms probe-rate cap and the
  application-context scoping (Claim 10), and state plainly that the run is
  manual (`npx promptfoo redteam run` / browser), so it does not satisfy the
  chapter's "continuous" requirement as written (Claim 11).
- **Chapter 03 (Runbooks and Agents) — "Agent evaluation in production"
  (`guide/03-runbooks-and-agents.md:268`)**: if the guide recommends exercising
  an agent framework end-to-end, cite the provider-adapter contract (Claims 1–5)
  as the reusable mechanism, but use Claim 7 to caution that wrapping a stateful
  graph does not automatically yield state/step-level eval — a reader who wants
  to grade intermediate nodes must return checkpoints or spans from the
  provider, as the ADK note does (`docs-promptfoo-evaluate-google-adk.md`
  Claims 1, 5–6).

## Extraction Notes

- Source read in full via WebFetch of the single page
  (https://www.promptfoo.dev/docs/guides/evaluate-langgraph). Footer at
  extraction: "Last updated on **Oct 23, 2026** by **renovate\[bot\]**"; no
  canonical first-published date, so `date_published` carries the last-updated
  date (same convention as sibling `docs-promptfoo-*` notes). The Prospector saw
  an earlier render dated Oct 12, 2026; the page has since been re-stamped, but
  the extracted content matches the Prospector's description.
- Prospector had three overlapping triage comments (novelty medium → low → low).
  This note follows the most specific guidance: extract the LangGraph binding
  **as a delta** over the CrewAI note, answer the typed-state question directly
  (Claim 4), and do not re-derive the provider-adapter contract or the assertion
  primitives. Where the delta is small, that is stated rather than inflated.
- Internal inconsistencies preserved as data, not papered over: the "Requirements"
  list names "GPT-5-mini" while `agent.py`/`provider.py` default to `gpt-4o`
  (Claims 2, 5); the results figure is captioned "(July 2025)" under an Oct 23,
  2026 footer. These are docs-drift signals and a reason the note's guide impact
  avoids citing exact model behaviour.
- No sub-pages followed. The substantive external links are LangGraph's
  checkpoint reference and promptfoo's red-team docs; the checkpoint link is
  precisely the *not-covered* intermediate-state inspection (Claim 7), and the
  red-team primitives are already mined in the corpus, so following them would
  not add binding-specific evidence.
- Quotes verified character-for-character against the fetched rendered content
  before writing. Code blocks are re-flowed only at the newline level to restore
  line breaks lost in HTML extraction (same convention as
  `docs-promptfoo-evaluate-crewai.md`); no characters in the code are changed.
  Where meaningful content spans non-adjacent lines, the claim is stated in
  prose and the full block placed in Concrete Artifacts rather than splicing.
- Cross-reference verification per MINER.md §4b: every cited claim number was
  re-read in its note before citation — CrewAI #1681 Claims 1, 2, 3, 6, 9;
  testing-llm-chains #1575 Claims 2, 3; google-adk Claims 1, 12; openai-agents-
  python #1707 Claims 1, 14. All 10 candidate paths from
  `miner-related-notes.md` were cited or explicitly dismissed above.
- `confidence_overall` = `emerging`: first-party vendor documentation is
  authoritative for the documented code/config (individual claims graded
  `settled` where they are direct code/config facts), but the page is a thin
  single-example walkthrough with a mocked agent, one test, no metrics, and no CI
  content; the operational value (the typed-state delta and its limits) is our
  synthesis across this page and the surrounding corpus.
- `registry/sources.json` and `registry/claims-index.json` were intentionally not
  edited: they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
