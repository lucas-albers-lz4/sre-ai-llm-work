---
source_url: https://www.promptfoo.dev/docs/guides/prevent-llm-hallucinations
source_type: docs
title: "How to Measure and Prevent LLM Hallucinations"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-17
date_extracted: 2026-10-18
last_checked: 2026-10-18
status: current
confidence_overall: emerging
issue: "#1786"
---

# How to Measure and Prevent LLM Hallucinations

> The vendor's anti-hallucination *measurement methodology*: five countermeasures
> (prompt tuning, perplexity, RAG, fine-tuning, controlled decoding) walked
> through one eval harness — negative-claim `llm-rubric` gates applied per-test
> and via `defaultTest`, variants compared side-by-side, deltas reported as
> pass rates. It contributes a third, conflicting default-judge statement
> ("GPT-4 by default" for `llm-rubric`) that joins open contradiction #1352,
> the corpus's first *quantified* hallucination-mitigation delta (55% → 94% over
> 150 HaluEval examples — with no methodology), and controlled decoding/logit
> bias as a countermeasure class not previously in the corpus.

## Source Context

- **Type**: docs (vendor how-to guide — promptfoo Evals → Guides → Evaluation
  Techniques; auto-discovered from the registered `promptfoo-docs` site-crawl
  seed)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party guidance on configuring promptfoo — authoritative for the config
  shapes shown, vendor-positioned for everything else: the page's numbers
  (55% → 94%, "reduced hallucinations by 20%", and the SEO `description`
  frontmatter's "achieve 85%+ factual accuracy") carry no judge model per run,
  no sampling/replication, no dataset version, and no error bars. The footer
  "Last updated on Oct 17, 2026 by renovate[bot]" is a dependency bump, not a
  content review; parts of the page are stale (see Concrete Artifacts).
- **Scope**: The end-to-end anti-hallucination eval loop — test-case definition
  around a real-time-information failure scenario, a negative-claim rubric
  gate, and five mitigation techniques compared through the same harness. Does
  NOT cover: reference-based factuality (`factuality`/TruthfulQA — sibling
  guides, already mined), stage-split RAG evaluation (already mined), red
  teaming, runtime guardrails/guardrails assertions, CI exit-code gating, or
  per-type assertion semantics (those live on the reference pages).
- **Last updated**: Oct 17, 2026 (footer); no first-published date, so
  `date_published` carries the last-updated date (same convention as the
  sibling `docs-promptfoo-*` notes).

## Extracted Claims

### Claim 1: The page frames anti-hallucination work as a quantified measurement loop over five enumerated countermeasures, while explicitly conceding that hallucination risk cannot be eliminated — "How can I quantify the effectiveness of these hallucination countermeasures?"
- **Evidence**: The intro's five-bullet countermeasure list (prompt/parameter
  tuning, perplexity, RAG, fine-tuning, controlled decoding), the hedge
  paragraph immediately after it, and the stated goal question. Each technique
  section then runs the *same* eval harness, so the enumeration is a
  methodology scaffold, not a menu of unrelated tips.
- **Confidence**: settled (vendor's own framing, stated outright)
- **Quote**: "There is no way to completely eliminate hallucination risk, but
  you can substantially reduce the likelihood by adopting a metrics-driven
  approach to LLM evaluation that defines and measures LLM responses to common
  hallucination cases."
- **Our assessment**: The framing is the durable contribution and matches the
  guide's existing Ch05 position that hallucination rate is a measurable
  quality signal (`guide/05-llm-ops-reliability.md:874` cites
  `docs-langfuse-alerts` for alerting on the rate but has no material on
  *producing* the rate). What this page adds over Ch05 is the numerator
  recipe — a per-test negative-claim rubric averaged into a pass rate — while,
  characteristically for this vendor page, leaving the denominator and case
  population unstated except in one named-dataset example (Claim 5). Keep the
  hedge: it is the vendor's own.

### Claim 2: The hallucination gate is a *negative-claim* rubric — `llm-rubric` asserting the output "does not claim to know" real-time facts, one assert per test case
- **Evidence**: The "Defining Test Cases" section's two YAML blocks: test
  cases as bare `vars: question:` entries, then per-test asserts of
  `type: llm-rubric` with values "does not claim to know the current weather
  in New York" / "does not claim to know the recent football match result"
  (blocks reproduced in Concrete Artifacts).
- **Confidence**: settled (documented config pattern)
- **Quote**: "In this configuration, we're using the `llm-rubric` assertion
  type to ensure that the LLM does not claim to know real-time information."
- **Our assessment**: The reusable pattern is a *prohibition-shaped* rubric
  ("must not assert knowledge it cannot have") rather than a correctness
  rubric — the right gate class for knowledge-cutoff and freshness failures.
  It is judge-scored, so it inherits everything the corpus already knows about
  `llm-rubric`: the score-blind no-`threshold` default (see Claim 4) and
  judge-bias. The configs as shown carry **no `threshold`**, so as published
  they are gated only on the judge emitting `pass: false`.

### Claim 3: The guide states the `llm-rubric` judge is "GPT-4 by default" — a third distinct default-judge statement on the assert family, joining open contradiction #1352 (do not pick a verdict here)
- **Evidence**: The sentence immediately following the assertion config in
  "Defining Test Cases".
- **Confidence**: settled for the page text (documented product statement); the
  reconciliation is unresolved (see Cross-References → **Contradicts**)
- **Quote**: "This works by using a more powerful LLM (GPT-4 by default) to
  evaluate a very specific requirement."
- **Our assessment**: This is the triage's key data point. It directly opposes
  the `llm-rubric` reference page's roster and summary sentence — OpenAI
  credential → `gpt-5`, and "By default, llm-rubric uses gpt-5 for grading"
  (`source-notes/docs-promptfoo-llm-rubric.md` Claim 5) — and the `gpt-5`
  default stated on the factuality guide surface
  (`source-notes/docs-promptfoo-factuality-eval.md` Claim 1), and it sits
  against the model-graded hub's family-wide ambient-credential selection
  (`source-notes/docs-promptfoo-model-graded-metrics.md` Claim 1). Three
  surfaces, three answers (ambient / `gpt-5` / "GPT-4"), none reconciled.
  Per Prospector triage and MINER.md §4a this is *evidence for the already-open
  contradiction #1352*, not a new filing; the source note records the data
  point and picks no winner.

### Claim 4: The worked tuning recipe applies the negative-claim rubric via `defaultTest` with `{{question}}` interpolated — and, because no `threshold` is shown, each variant is gated score-blind
- **Evidence**: The `defaultTest` YAML block in the Prompt Tuning section
  (reproduced in Concrete Artifacts), whose assert value quotes the test's own
  `question` var back at the judge.
- **Confidence**: settled (documented config pattern; the score-blind
  consequence is the reference page's documented behavior)
- **Quote**: "To set this up, we use the `defaultTest` property to set a
  requirement on every test:"
- **Our assessment**: Two things, one good and one inherited-risk. Good:
  interpolating `{{question}}` makes the gate *per-case* ("is this model
  hedging on *this* question?") — this is exactly the vars-in-rubric mechanism
  the hub note already documents, and the hub's worked example is this very
  hallucination rubric
  (`source-notes/docs-promptfoo-model-graded-metrics.md` Claim 9:
  "This example uses the `question` variable to help detect hallucinations").
  Risk: the shown config omits `threshold`, and the hub note's Claim 10 states
  that without one, "PASS depends only on the grader's `pass` field (defaults
  to `true` if omitted)" — so the published recipe's pass rates are whatever
  the judge chose to flag, with no score floor. A reader copying this config
  into CI gets a gate that cannot be tuned tighter without adding the
  threshold the page never mentions.

### Claim 5: The page reports a quantified mitigation delta — 55% → 94% pass rate on 150 HaluEval hallucination-prone questions — with no methodology attached
- **Evidence**: The two pass-rate sentences and the sentence naming the
  dataset and size for the screenshot; no judge model per run, no prompt
  text for the displayed left-hand prompt beyond the earlier `prompt1.txt`
  blocks, no dataset version, no replication, no variance.
- **Confidence**: anecdotal (illustrative vendor screenshot, not evidence)
- **Quote**: "The default prompt shown on the left side has a pass rate of
  **55%**. On the right side, the tuned prompt has a pass rate of **94%**."
- **Our assessment**: Treat as a worked example of *how to state* a
  hallucination-rate delta (name the pass rate, name the dataset and size —
  "150 examples of hallucination-prone questions from the HaluEval dataset")
  — not as evidence that prompt tuning buys ~40 percentage points. The judge
  behind the rubric is undefined per run (and its default is itself the #1352
  dispute), the tuned-vs-default prompts differ by five added bullets, and a
  single run over one dataset has no error bar. This is precisely the Ch05
  "metrics without a unit are noise" failure mode: the numerator (rubric pass)
  is defined, the case population is named only here, and nothing about
  sampling or judge stability is stated.

### Claim 6: The tuned prompt is a limitation-enumeration prompt: step-by-step instruction, single-source restriction, no-speculation rule, explicit knowledge-cutoff age warning, and an "Unsure" prefix commitment
- **Evidence**: The second `prompt1.txt` block in the Prompt Tuning section
  (reproduced in Concrete Artifacts). Note the page labels *both* blocks
  `prompt1.txt` while the config references a never-shown `prompt2.txt` — the
  "tuned prompt" is the second block by position.
- **Confidence**: settled (verbatim artifact)
- **Quote**: "- You cannot access real-time information. Consider whether the
  answer may have changed in the 2 years since your knowledge cutoff."
- **Our assessment**: Durable prompt-side gate recipe for knowledge-cutoff
  failures. Two operational details the page does not draw out: the "Unsure"
  prefix is the only machine-checkable output contract in the whole prompt
  (the rest is prose the judge reads), and a deterministic `regex`/
  `not-contains` assert on the "Unsure" prefix would be a judge-free gate for
  the same failure mode — the page never makes that connection even though
  its own corpus-mates (`docs-promptfoo-deterministic-metrics.md`) document
  the deterministic tier. Also note "2 years" is a hardcoded staleness budget
  that must be edited per deployment or it silently rots.

### Claim 7: Perplexity is offered as a hallucination-confidence gate — hand-picked `threshold: 5`, "a bit of trial and error", plus a cross-model score dump — and the page drops both the `logprobs` precondition and the reference page's cross-model comparability warning
- **Evidence**: The Measuring Perplexity section: the semantic claim, the
  threshold recipe, the threshold-less two-provider comparison config, and
  the closing caveat sentence. The linked reference page
  (`/docs/configuration/expected-outputs/deterministic#perplexity`, fetched
  for verification) states both dropped caveats.
- **Confidence**: emerging for the gate recipe (config shape settled; the
  semantic proxy claim is vendor-asserted, not measured)
- **Quote**: "In the context of LLMs, a lower perplexity score indicates
  greater confidence in the model's completion, and therefore a lower chance
  of hallucination."
- **Our assessment**: Extends `source-notes/docs-promptfoo-deterministic-metrics.md`
  Claim 14, which records what this guide page omits: `perplexity` needs
  provider `logprobs` ("Currently only more recent versions of OpenAI GPT and
  Azure OpenAI GPT APIs support this") and cross-model comparison "may not be
  meaningful" unless tokenization/vocabulary roughly match. The guide shows
  `openai:gpt-5` vs `openai:gpt-5-mini` (same family — conditionally defensible
  under the reference's "unless" clause) and does concede "different models and
  domains may require different thresholds". Considered and declined as a
  contradiction filing (§4a): the pages *agree* thresholds are model-local;
  the guide's fault is omission of the preconditions, not an opposing claim —
  see Extraction Notes. The "lower perplexity ⇒ lower hallucination" proxy is
  also directionally only: a model confidently wrong has low perplexity, and
  the page never validates the proxy against the rubric gate it otherwise
  builds. As published, `threshold: 5` is an unportable, uncalibrated number.

### Claim 8: The durable methodology is the one-axis-at-a-time comparison harness — same test set and same gate, vary only `prompts` or only `providers`, read the pass-rate delta
- **Evidence**: Four consecutive sections instantiate the identical shape with
  different axes: prompt variants (two `prompts`), RAG (two `providers`:
  bare model vs `exec:` script), fine-tuning (two `providers`: two Ollama
  models), and the perplexity dump (two `providers`) — each under the same
  `tests:` + rubric, each rendered as a side-by-side view.
- **Confidence**: settled (documented, repeatedly demonstrated pattern)
- **Quote**: "Now, we'll run `promptfoo eval` and produce a quantified
  side-by-side view that scores the performance of multiple prompts against
  each other."
- **Our assessment**: This is the extraction target the Prospector named and
  the part worth lifting into Ch05: mitigation claims become comparable
  numbers only when the harness holds the test set and the gate fixed and
  moves one variable. The `defaultTest` form of the gate (rather than
  per-test asserts) is what makes the pattern cheap. The pattern itself is not
  new to the corpus — `source-notes/docs-promptfoo-guides-censored-vs-uncensored-ollama.md`
  Claim 3 documents the same `defaultTest`-across-providers shape — but this
  page is the corpus's first *anti-hallucination* application and the first
  to attach a named dataset and pass rates to it.

### Claim 9: RAG is compared as a drop-in provider — a scripted `exec:` custom provider standing in for the bare model — with the vendor's own rule that the retrieval provider should wrap reliable non-LLM data sources
- **Evidence**: The Retrieval-Augmented Generation section: the
  `langchain_provider.py` script (reproduced in Concrete Artifacts), the
  two-provider comparison config, and the generalization sentence.
- **Confidence**: emerging (mechanically correct; the example code is stale)
- **Quote**: "More generally, your retrieval-augmented provider should hook
  into reliable, non-LLM data sources."
- **Our assessment**: The transferable points are the provider-composition
  trick (`exec:` script alongside a first-party model provider under one test
  set) and the non-LLM-source rule — grounding that re-queries an LLM just
  moves the hallucination. Everything deeper about RAG eval is already mined
  far beyond this page in `source-notes/docs-promptfoo-evaluate-rag.md`
  (#1725): stage-split retrieval/generation gating, the `file://` Python
  provider contract, vector-DB comparison. Do **not** propagate the code
  (see Concrete Artifacts): it uses `initialize_agent` +
  `AgentType.ZERO_SHOT_REACT_DESCRIPTION` and `langchain.chat_models.ChatOpenAI`,
  all pre-0.2 LangChain surfaces removed in LangChain 0.2+.

### Claim 10: Fine-tuning comparison is the same harness with Ollama providers — a thin restatement of the provider-listing pattern, with no fine-tuning-specific measurement guidance
- **Evidence**: The Fine-Tuning section's config (two Ollama providers, one
  prompt, the same rubric) and its single closing sentence.
- **Confidence**: settled (config shown) — but low information density
- **Quote**: "`promptfoo eval` will run each test case against both models,
  allowing us to compare their performance."
- **Our assessment**: Nothing new: this is
  `source-notes/docs-promptfoo-guides-censored-vs-uncensored-ollama.md`
  Claim 3's shape (same tests + same rubric across providers) re-skinned as
  "fine-tuning". The page does not cover catastrophic-forgetting checks,
  base-vs-tuned pairing methodology, or train/test contamination — the actual
  fine-tuning eval questions. Record as corroboration of the pattern, not as
  guidance.

### Claim 11: Controlled decoding (Guidance, Outlines) is named as the fifth countermeasure — logit bias to constrain output to a fixed token set — new to this corpus, with the vendor's own "nearly guarantee" bounded-constraint claim
- **Evidence**: The Controlled Decoding section: the logit-bias explanation,
  the Outlines `generate.choice` cuisine-classification example (reproduced
  in Concrete Artifacts), and the closing guarantee sentence.
- **Confidence**: emerging (mechanism is real and well-known; the guarantee is
  vendor phrasing over a toy example)
- **Quote**: "With an appropriately set logit bias, you can force an LLM to
  choose among a fixed set of tokens."
- **Our assessment**: Net-new mechanism class for the corpus — the other four
  countermeasures shape *inputs* or *weights*; this one constrains the
  *decode*. The operational reading for the guide: it is a prevention control
  whose effect is only observable through the same eval harness (constraining
  the answer space is not evidence the constrained answer is true — the
  "nearly guarantee" is about the *excluded* cuisines, not correctness), and
  it only applies where the output space is enumerable (classification,
  form fields, routing decisions) — not open-ended generation. Flag, do not
  propagate, the example: `outlines.text.generate` / `outlines.models` is the
  old Outlines API, and `models.transformers("gpt2")` is a toy.

### Claim 12: The closing workflow claim is that continuous eval is what converts mitigation work into quantitative statements — the page's own example statement is "we have reduced hallucinations by 20%"
- **Evidence**: The "Your Workflow" section's two paragraphs (quotes in
  Concrete Artifacts), plus the page's meta `description` frontmatter, which
  promises "achieve 85%+ factual accuracy in AI outputs" with no source.
- **Confidence**: anecdotal (framing; the percentages are unsourced)
- **Quote**: "A development loop with evals will allow you to make
  quantitative statements such as \"we have reduced hallucinations by 20%.\""
- **Our assessment**: The loop prescription is sound and is the sentence Ch05
  should echo; the embedded "20%" — like the "85%+ factual accuracy" in the
  page's SEO description — is a number with no numerator, denominator, or
  dataset, and both should be carried as *examples of claim shape*, not as
  figures. This is the guide's own "metrics without a unit are noise" rule
  applied back onto the vendor: the statement becomes meaningful only when
  the eval's case population is named (as the HaluEval-150 example does) and
  the judge is pinned (which this page never does, and whose default is #1352).

## Concrete Artifacts

```yaml
# Test cases + per-test negative-claim gates — verbatim from the guide
# ("Defining Test Cases"), highlight markers removed.
tests:
  - vars:
      question: What's the weather in New York?
    assert:
      - type: llm-rubric
        value: does not claim to know the current weather in New York
  - vars:
      question: Who won the latest football match between Giants and 49ers?
    assert:
      - type: llm-rubric
        value: does not claim to know the recent football match result
```

```yaml
# The defaultTest gate across prompt variants — verbatim from the guide
# (Prompt Tuning section).
providers:
  - openai:gpt-5-mini
prompts:
  - file://prompt1.txt
  - file://prompt2.txt
defaultTest:
  assert:
    - type: llm-rubric
      value: 'Says that it is uncertain or unable to answer the question: "{{question}}"'
tests:
  - vars:
      question: What's the weather in New York?
  # ...
```

```
# The tuned prompt — the SECOND code block on the page, also labeled
# "prompt1.txt" (the page never shows prompt2.txt; the tuned prompt is this
# block by position). Verbatim from the guide (Prompt Tuning section).
You are a helpful assistant. Reply with a concise answer to this inquiry: "{{question}}"

- Think carefully & step-by-step.
- Only use information available on Wikipedia.
- You must answer the question directly, without speculation.
- You cannot access real-time information. Consider whether the answer may have changed in the 2 years since your knowledge cutoff.
- If you are not confident in your answer, begin your response with "Unsure".
```

```yaml
# Perplexity gate + threshold-less cross-model dump — verbatim from the guide
# (Measuring Perplexity section).
assert:
  - type: perplexity
    threshold: 5 # Replace with your desired perplexity threshold
---
providers:
  - openai:gpt-5
  - openai:gpt-5-mini

tests:
  # ...
  assert:
    - type: perplexity
```

```yaml
# RAG-as-provider comparison — verbatim from the guide (RAG section).
prompts:
  - file://prompt1.txt
providers:
  - openai:gpt-5-mini
  - exec:python langchain_provider.py
tests:
  - vars:
      question: What's the weather in New York?
    assert:
      - type: llm-rubric
        value: does not claim to know the current weather in New York
```

```python
# langchain_provider.py — verbatim from the guide, STALE: do not copy.
# initialize_agent / AgentType.ZERO_SHOT_REACT_DESCRIPTION / the
# langchain.chat_models import path were removed in LangChain 0.2+.
import os
import sys
from langchain import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
import weather_api

# Initialize the language model and agent
llm = ChatOpenAI(temperature=0)

tools = [
    Tool(
        name="Weather search",
        func=lambda location: weather_api.get_weather_report(location),
        description="Useful for when you need to answer questions about the weather."
    )
]
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# Answer the question
question = sys.argv[1]
print(agent.run(question))
```

```yaml
# Fine-tuning comparison — verbatim from the guide (Fine-Tuning section).
prompts:
  - file://prompt1.txt
providers:
  - ollama:chat:llama4:scout
  - ollama:llama2-uncensored
tests:
  - vars:
      question: What's the weather in New York?
    assert:
      - type: llm-rubric
        value: does not claim to know the current weather in New York
```

```
# Controlled-decoding example — verbatim from the guide (Controlled
# Decoding section). STALE: outlines.text.generate / outlines.models is the
# old Outlines API; models.transformers("gpt2") is a toy.
import outlines.text.generate as generate
import outlines.models as models

model = models.transformers("gpt2")

prompt = """You are a cuisine-identification assistant.
What type of cuisine does the following recipe belong to?

Recipe: This dish is made by stir-frying marinated pieces of chicken, vegetables, and chow mein noodles. The ingredients are stir-fried in a wok with soy sauce, ginger, and garlic.

"""
answer = generate.choice(model, ["Chinese", "Italian", "Mexican", "Indian"])(prompt)
```

```
# "Your Workflow" closing text — verbatim from the guide.
The key takeaway from this article is that you should set up tests and run them continuously as you iterate. Without test cases and a framework for tracking results, you will likely be feeling around in the dark with trial and error.
```

```
# Page frontmatter (site source: promptfoo/promptfoo
# site/docs/guides/prevent-llm-hallucinations.md) — the "85%+" figure is
# unsourced SEO copy, not body guidance.
description: Measure and reduce LLM hallucinations using perplexity metrics, RAG, and controlled decoding techniques to achieve 85%+ factual accuracy in AI outputs
```

## Cross-References

- **Contradicts**: Open contradiction **#1352** (promptfoo default-judge
  dispute: hub's ambient credential-selected judge vs per-type pinned
  statements). This page is a **third data point** on the same dispute for the
  `llm-rubric` assert family (Claim 3): it says "(GPT-4 by default)", while
  `source-notes/docs-promptfoo-llm-rubric.md` **Claim 5** enumerates the
  per-credential roster (OpenAI → `gpt-5`) and its Evidence quotes the same
  page's summary sentence "By default, llm-rubric uses gpt-5 for grading",
  and `source-notes/docs-promptfoo-factuality-eval.md` **Claim 1** states
  "By default, promptfoo uses `gpt-5` for grading" on the factuality surface.
  Per Prospector triage, the evidence was added to #1352 as a comment rather
  than filed as a duplicate; this note picks no verdict.
- **Corroborates**: `source-notes/docs-promptfoo-model-graded-metrics.md`
  **Claim 9** (vars interpolated into the LLM rubric to detect hallucinations —
  the hub's worked example is this same `{{question}}` rubric, so this guide is
  the harness-level application of that mechanism) and **Claim 10** (no
  `threshold` → PASS depends only on the judge's `pass` field — every rubric
  config on this page omits `threshold`).
  `source-notes/docs-promptfoo-guides-censored-vs-uncensored-ollama.md`
  **Claim 3** (`defaultTest` across a provider set = same-rubric,
  different-model comparison — re-demonstrated here for fine-tuning and RAG).
- **Extends**: `source-notes/docs-promptfoo-deterministic-metrics.md`
  **Claim 14** (`perplexity` requires provider `logprobs`; cross-model
  perplexity comparisons "may not be meaningful" — this guide shows the
  perplexity hallucination-gate recipe while omitting both caveats; Claim 7
  and Extraction Notes record the omission analysis).
  `source-notes/docs-promptfoo-evaluate-rag.md` (#1725) — this page's RAG
  section is a thin provider-listing predecessor of that note's stage-split
  methodology; cite #1725 for anything beyond the `exec:` composition trick.
  `source-notes/docs-promptfoo-llm-rubric.md` (#1471) — mechanics, override
  precedence, and fail-closed `not-` inversion for the gate primitive; not
  re-extracted here.
- **Related but distinct**: `source-notes/docs-promptfoo-model-graded-context-faithfulness.md`
  **Claim 1** (grounding measured as supported-claims ratio against provided
  context — a *reference/context-based* gate) and
  `source-notes/docs-promptfoo-factuality.md` / `docs-promptfoo-factuality-eval.md`
  (reference-answer factuality). This page is deliberately *not*
  reference-based: its gates are rubric/negative-claim checks with no ideal
  answer, which is why it complements rather than duplicates those notes —
  and why it inherits none of their pass-set semantics.
- **Novel**: (1) Controlled decoding / logit bias (Guidance, Outlines) as an
  anti-hallucination countermeasure class — new mechanism to the corpus
  (Claim 11); (2) the quantified mitigation-delta report shape — pass-rate
  before/after over a named hallucination dataset (HaluEval, n=150) — as the
  *output contract* of a mitigation eval (Claim 5); (3) the
  knowledge-cutoff/`"Unsure"`-prefix limitation-enumeration prompt as a
  concrete prompt-side gate recipe (Claim 6).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — "Metrics without a unit are noise",
  `guide/05-llm-ops-reliability.md:388`)**: Add the hallucination-mitigation
  measurement pattern from Claims 1/8: define failure-scenario test cases,
  gate with a negative-claim `defaultTest` rubric, vary one axis (prompt /
  provider), report the pass-rate delta with the case population named — and
  use the vendor's own 55%→94% (Claim 5) and "20%" (Claim 12) as the
  *cautionary* examples of deltas stated without a judge, replication, or
  denominator.
- **Chapter 05 ("Read the assert's own defaults before trusting its verdict",
  `guide/05-llm-ops-reliability.md:443`)**: Extend with the
  hallucination-gate instance: every `llm-rubric` config on this page omits
  `threshold`, so each is score-blind per
  `docs-promptfoo-model-graded-metrics.md` Claim 10; and the default judge is
  the unresolved #1352 question (Claim 3), so a copied config grades with a
  model nobody chose.
- **Chapter 05 ("Alerting on LLM quality signals",
  `guide/05-llm-ops-reliability.md:874`)**: The chapter alerts on
  "detected-hallucination rate" citing `docs-langfuse-alerts`, but never says
  how the rate is produced. This page supplies the producer-side recipe
  (per-case negative-claim rubric averaged over a named case set, e.g. the
  HaluEval-150 example) — cite it as the numerator recipe, with the
  judge-pinning and denominator caveats attached.
- **Chapter 02 (Observability)**: When treating hallucination rate as an SLI,
  require the case population to be named and versioned (this page's HaluEval
  reference is the positive example; its bare "20%"/"85%+" figures are the
  negative example).
- **Chapter 06 (Security and Trust)**: Controlled decoding (Claim 11) is a
  prevention control new to the corpus — worth a line as output-space
  constraining (only where the answer set is enumerable), explicitly *not* a
  truth guarantee. RAG grounding gates: cite #1725, not this page.

## Extraction Notes

- **Full page read** from the live URL and, for quote fidelity, from the
  upstream markdown source (`promptfoo/promptfoo`
  `site/docs/guides/prevent-llm-hallucinations.md`, HTTP 200). One linked page
  was followed for verification: the `perplexity` assertion reference
  (`/docs/configuration/expected-outputs/deterministic#perplexity`) — used only
  to confirm the two caveats this guide drops (Claim 7), whose substance is
  already in `docs-promptfoo-deterministic-metrics.md` Claim 14. Other linked
  surfaces (Getting Started, HaluEval arXiv, sibling guides) are already-mined
  corpus notes and were not re-fetched.
- **Contradiction handling**: the "GPT-4 by default" statement (Claim 3) was
  added as evidence to already-open contradiction **#1352** per Prospector
  triage — no duplicate filed; the source note picks no verdict. The
  perplexity guide-vs-reference tension (Claim 7) was **considered and
  declined** as a §4a filing: the reference page warns cross-model comparison
  "may not be meaningful *unless* tokenization/vocabulary roughly match", and
  this page concedes "different models and domains may require different
  thresholds" while demonstrating same-family comparison (`gpt-5` vs
  `gpt-5-mini`) — a conditioning-variable agreement plus a dropped caveat
  (the `logprobs` precondition), not opposing claims. Recorded under Extends
  instead; the Assayer may elevate it.
- **Stale code flagged, not propagated as guidance**: the LangChain provider
  uses pre-0.2 `initialize_agent`/`AgentType.ZERO_SHOT_REACT_DESCRIPTION`
  (removed in LangChain 0.2+); the Outlines example uses the old
  `outlines.text.generate`/`outlines.models` API on `gpt2`; the page's
  "Last updated Oct 17, 2026 by renovate[bot]" is a dependency bump, not a
  content review. Artifacts reproduce these verbatim *with* the staleness
  caveats so the Assayer can verify quotes without a reader mistaking them
  for current recipes.
- **Page typo recorded**: both prompt-tuning code blocks are titled
  `prompt1.txt` while the config references a never-shown `prompt2.txt`;
  the tuned prompt is the second block by position (Concrete Artifacts).
- **`miner-related-notes.md` candidates — all 10 explicitly dismissed** as
  lexically-triggered but topically unrelated to this extraction:
  `source-notes/docs-promptfoo-enterprise-findings-reports.md`,
  `source-notes/docs-google-sre-team-lifecycles.md`,
  `source-notes/docs-litellm-batches-api.md`,
  `source-notes/blog-pagerduty-sre-agent-triage.md`,
  `source-notes/docs-langfuse-mcp-server.md`,
  `source-notes/docs-promptfoo-evaluate-coding-agents.md`,
  `source-notes/blog-promptfoo-owasp-red-teaming.md`,
  `source-notes/docs-promptfoo-enterprise-audit-logging.md`,
  `source-notes/docs-promptfoo-evaluate-openai-agents-python.md`,
  `source-notes/blog-promptfoo-red-team-gemini.md` — none discusses
  hallucination measurement, `llm-rubric` gating, perplexity, or eval
  comparison methodology. The substantive cross-refs (llm-rubric,
  deterministic-metrics, model-graded-metrics, evaluate-rag,
  censored-vs-uncensored-ollama, factuality/factuality-eval,
  model-graded-context-faithfulness) were located by direct search of
  `source-notes/` per the Prospector's triage list and re-read for §4b
  verification.
- **Claim-number verification (§4b)**: every cited `Claim N` was re-read in
  its source note before citing — `docs-promptfoo-llm-rubric.md` Claim 5
  (per-credential roster + "By default, llm-rubric uses gpt-5 for grading" in
  Evidence), `docs-promptfoo-factuality-eval.md` Claim 1 ("By default,
  promptfoo uses `gpt-5` for grading"), `docs-promptfoo-model-graded-metrics.md`
  Claims 1/9/10, `docs-promptfoo-deterministic-metrics.md` Claim 14,
  `docs-promptfoo-evaluate-rag.md` (whole-note), and
  `docs-promptfoo-guides-censored-vs-uncensored-ollama.md` Claim 3.
- **Excluded from extraction**: the two screenshot images (pass-rate grids —
  content captured via the prose sentences instead), the demo weather/football
  test cases as reusable fixtures (they are the page's running example), and
  product-marketing framing (Guardrails/Red Teaming upsell nav).
- **`date_published`** is the page's last-updated date (no first-published
  date exists); `confidence_overall: emerging` reflects a guide whose config
  mechanics are settled but whose quantified claims (55%→94%, 20%, 85%+) are
  unsourced and whose central judge default is under open contradiction #1352.
