---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/
source_type: docs
title: "Promptfoo Configuration: Model-Graded — LLM Rubric"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-26
date_extracted: 2026-09-26
last_checked: 2026-09-26
status: current
confidence_overall: emerging
issue: "#1471"
---

# Promptfoo Configuration: Model-Graded — LLM Rubric

> The per-type reference page for promptfoo's flagship `llm-rubric` assertion —
> the gap the hub note (#1305) explicitly left open ("the remaining per-type
> sub-pages (g-eval, pi, llm-rubric, ...) were not followed"). It contributes
> the corpus's **first non-text judge input surface** (audio: the target's
> `response.audio` is attached to the grading request, inline base64 wav/mp3
> ≤ 20 MiB, and an assertion carrying a `transform` **silently drops the audio**
> so the same assert type grades audio, transcript, or text depending on config
> shape), the **checkable per-credential default-judge roster** behind the hub
> note's "unpinned judge" finding (`gpt-5` / `claude-sonnet-4-5-20250929` /
> `gemini-2.5-pro` / `mistral-large-latest` / `openai/gpt-5` / the configured
> Azure deployment, plus a text-only Codex-login fallback), the
> **custom-judge `metadata` → `GradingResult.metadata` passthrough** that
> carries upload/trace IDs into `afterEach` hooks, and a third instance of the
> **symmetric fail-closed `not-` inversion** sentence (this time for
> `not-llm-rubric`).

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "LLM Rubric"
  per-type model-graded assert reference page under
  `/docs/configuration/expected-outputs/model-graded/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own `llm-rubric` behavior — authoritative for *what promptfoo does*
  with a given config (judge selection, audio attachment, negation semantics,
  metadata propagation), but vendor-positioned: the page carries no measured
  judge-agreement, gate-failure-rate, cost, or calibration figures, and its one
  comparative claim ("It is similar to OpenAI's model-graded-closedqa prompt,
  but can be more effective and robust in certain cases.") is asserted without
  evidence or a defined "certain cases." Everything below is checkable against
  an installed CLI.
- **Scope**: A fourteen-section reference page (How to use it, How it works,
  **Audio output**, Using variables in the rubric, Overriding the LLM grader,
  Setting grader parameters, OpenAI-compatible judges with thinking output,
  Customizing the rubric prompt, Non-English Evaluation (Options 1-3 +
  Assertion-Specific Prompts), Object handling in rubric prompts, Threshold
  Support, Pass vs. Score Semantics + Common misconfiguration, Negation with
  `not-llm-rubric`, Further reading). It is the per-type deep-dive on the
  rubric-judge member of the model-graded class that
  `docs-promptfoo-model-graded-metrics.md` (#1305) catalogued at claim level
  and explicitly did **not** follow — that note's Extraction Notes list
  "llm-rubric" among the unf followed sub-pages, and it also states that its
  own Claims 2/5/6/8/9/10 reproduce several of this page's sections, so this
  note carries the **delta** (audio grading, the default-judge roster, the
  Codex-login text-only boundary, metadata passthrough, the `not-` sentence)
  and cross-references rather than re-extracts the shared material. The page's
  outbound links (`agent-rubric`, the vLLM judge recipe, the model-graded
  overview, object-template handling) are all already-mined surfaces in this
  corpus; see Extraction Notes.
- **Last updated**: the page footer reads "Last updated on **Sep 26, 2026** by
  **mldangelo-oai**" — current, and the documented examples are `gpt-5`-era.

## Extracted Claims

### Claim 1: `llm-rubric` can grade a non-text target — promptfoo attaches the target provider's `response.audio` to the grading request when an audio-capable OpenAI Chat Completions grader is selected, and `modalities: [text]` is what makes the judge's JSON verdict come back as text while the audio itself is what it grades
- **Evidence**: The "Audio output" section: the grader-selection sentence, the
  worked `openai:chat:gpt-audio-1.5` assert with `modalities: [text]`, and the
  return-contract sentence naming the sources of compatible audio (OpenAI
  Realtime, audio chat, text to speech, or a custom target provider returning
  the same audio fields).
- **Confidence**: settled (documented product behavior on the vendor's own page)
- **Quote**: "To evaluate tone, pacing, or pronunciation, choose an audio-capable OpenAI Chat Completions grader. Promptfoo attaches the target provider's response.audio to the grading request:" and "modalities: [text] requests the grader's JSON result as text. The grader listens to the attached audio and uses the transcript as supporting context. This works with audio from OpenAI Realtime, audio chat, text to speech, or a custom target provider that returns the same audio fields."
- **Our assessment**: This is a genuinely new *judge input surface* for the
  corpus — nothing in any of the 200 existing notes documents a non-text
  channel into a model-graded verdict. The two halves of the contract matter
  separately: the audio is the graded artifact, the transcript is only
  "supporting context," so a voice-quality rubric (tone, pacing, pronunciation)
  is satisfied by audio the transcript cannot express. Operationally this
  changes what "the output" means for a gate: an eval suite that has been
  text-shaped end to end (prompt → `response.text` → judge) now has a path
  where the payload under test is a WAV file, and the graded object is no
  longer inspectable in a text diff or a log line. Treat it as the audio
  analogue of the hub note's "the residual unpinned inputs" thread: the corpus
  now has a channel with its own precondition list (next claim) and its own
  silent-degradation mode (the claim after that).

### Claim 2: The audio input contract is narrow and fails loudly on the wrong shapes — the target must return **inline base64** audio as `wav` or `mp3` up to 20 MiB (blob references and other formats raise a *grading error*), and the built-in Realtime provider converts its default PCM16 output to WAV (including in persistent conversations) with `output_audio_format: pcm16` required for grading
- **Evidence**: The "Audio output" section's format/limit paragraph, verbatim
  (see Concrete Artifacts for the full paragraph as rendered).
- **Confidence**: settled (documented product behavior)
- **Quote**: "The target must return inline base64 audio with format: wav or format: mp3, up to 20 MiB. Blob references and other formats produce a grading error. The built-in Realtime provider converts its default PCM16 output to WAV, including in persistent conversations; use output_audio_format: pcm16 for grading."
- **Our assessment**: Note the asymmetry that makes this claim worth having:
  the *wrong* shape is loud (a grading **error**, not a silent text grade) but
  the *right* shape is conditional on a provider-specific knob. A Realtime
  target left at a non-PCM16 output format does not fail the eval — it just
  never becomes gradable audio, and the suite degrades to grading the
  transcript (Claim 3's silent path). The 20 MiB inline ceiling is also an
  infrastructure fact, not just a config fact: the audio bytes travel *in* the
  grading request and then in the persisted assertion metadata (Claim 4), so
  a long-voice-agent gate multiplies eval payload size by the audio length
  per assertion. For a CI gate that stores per-assertion results, budget for
  it. And a provider that returns audio by blob reference — the natural design
  for large audio — is *incompatible* with grading as documented, which means
  "the target supports audio" and "the target is gradeable" are two different
  capabilities.

### Claim 3: The silent-degradation trap — an assertion with `transform` grades the transformed text and **does not attach the original audio**, so the same `llm-rubric` type grades audio, transcript, or text-only depending on grader choice *and* config shape, with no error
- **Evidence**: The "Audio output" section's closing two sentences: the
  text-only-grader behavior sentence and the `transform` sentence (the contrast
  is explicit on the page, adjacent sentences).
- **Confidence**: settled (documented product behavior — and this is the page
  telling you the degraded mode exists, not the Miner inferring it)
- **Quote**: "Text-only graders retain their existing behavior and evaluate the text output or transcript." and "An assertion with transform grades the transformed text and does not attach the original audio."
- **Our assessment**: This is the claim worth having, and the reason this
  page is more than a re-run of the hub note. A `transform` is a normal,
  unrelated piece of config (normalizing a transcript, stripping timestamps,
  redaction) and adding one to an audio assert does not break the run — the
  judge still returns `{reason, score, pass}`, the assertion still passes or
  fails, and the report shows a normal verdict. What changed is that the judge
  is now grading *text* (the transform's output) while the rubric still says
  "The speaker sounds calm and speaks at a steady pace." So the failure mode is
  not a false negative on tone — it is a rubric that is being applied to a
  representation of the output that cannot express the rubric's property, and
  it will look green forever. This is the same class as the hub note's
  score-blind pass (Claim 10 there) and the vLLM truncated-`<think>` misparse
  (Claim 6 there): a *config* property that makes the gate incapable of
  failing the property it names, reviewable only by reading the config. The
  operational rule it implies: `transform` and audio grading are mutually
  exclusive on a single assertion, and a gate that means to grade voice must
  assert the absence of `transform` (or carry the transform in the *target*
  rather than the assertion).

### Claim 4: The observability handle is a separate metadata flag — successful audio grades carry `renderedGradingPromptAudio: true` in assertion metadata, while `renderedGradingPrompt` holds the text prompt *without* the attached audio bytes, so the rendered prompt is not evidence the grader heard anything
- **Evidence**: The same closing sentence of the "Audio output" section, and
  the section's cross-reference to the plain-text grader behavior.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Successful audio grades include renderedGradingPromptAudio: true in assertion metadata; renderedGradingPrompt contains the text prompt without the attached audio bytes."
- **Our assessment**: This closes a debuggability hole the page would otherwise
  leave open. The natural instinct on a suspicious voice-grade verdict is to
  look at the rendered grading prompt — and for audio grades that artifact is
  *by design* not the whole request, so inspecting it cannot distinguish
  "the judge received audio and disliked it" from "the judge received text
  only." A single boolean in assertion metadata is the difference between an
  auditable gate and an undebuggable one, and it generalizes into a rule for
  Ch05: when a verdict is produced from a channel the report does not render,
  require a positive marker for that channel. Note the marker is on
  *successful* audio grades only, so its absence is ambiguous (failed grade?
  text-only grade? no assertion?) — which is precisely why the gate-review
  checklist should require the positive marker per assertion rather than
  infer coverage from the pass/fail column.

### Claim 5: The default judge is selected per ambient credential, and this page enumerates the roster with concrete model IDs — OpenAI → `gpt-5`, Codex/ChatGPT login → `openai:codex-sdk` (conditional), Anthropic → `claude-sonnet-4-5-20250929`, Google AI Studio → `gemini-2.5-pro` (via `GEMINI_API_KEY`/`GOOGLE_API_KEY`/`PALM_API_KEY`), Google Vertex → `gemini-2.5-pro`, Mistral → `mistral-large-latest`, GitHub token → `openai/gpt-5`, Azure → the configured Azure GPT deployment
- **Evidence**: The "How it works" section's roster (verbatim in Concrete
  Artifacts), plus the Codex-login entry's three-way condition. The page's
  later "Overriding the LLM grader" section opens with the summarizing
  sentence "By default, llm-rubric uses gpt-5 for grading."
- **Confidence**: settled (documented product behavior — the IDs and the
  env-var names are stated outright, not inferred)
- **Quote**: "Under the hood, llm-rubric uses a model to evaluate the output based on the criteria you provide. By default, it uses different models depending on which API keys are available:"
- **Our assessment**: This is the checkable enumeration of the hub note's
  (#1305 Claim 1) "unpinned judge" finding, and it converts a vague rule into
  a grep-able one: a runner with `ANTHROPIC_API_KEY` set is grading with
  `claude-sonnet-4-5-20250929` whether or not anyone chose it, and a runner
  with a GitHub token is grading with `openai/gpt-5` — an OpenRouter-style
  namespaced ID on a completely different routing surface. Three of the eight
  entries (Mistral's `mistral-large-latest`, Vertex's `gemini-2.5-pro`,
  Azure's "your configured deployment") are *floating* or environment-defined
  even in name, so "pin your judge" is not satisfiable by copying the default
  list into a config. The Codex-login entry is the most operationally
  surprising: the default depends on a package being installed and a session
  being signed in — i.e. on the *state of a developer's machine*, which no
  config file records. This claim also bears directly on open contradiction
  **#1352**; see Cross-References. Note the page carries both statements
  ("different models depending on which API keys are available" here, and "by
  default, llm-rubric uses gpt-5" two sections later), and the table above
  shows the second is the OpenAI-credential branch rather than an absolute
  pin — I record that as evidence, not as a verdict on #1352.

### Claim 6: The Codex/ChatGPT-login fallback is text-only — assertions that need embeddings or moderation still require an API-key-backed provider override, so a credential-selected judge can be silently *incapable* of part of the suite, not merely differently calibrated
- **Evidence**: The "How it works" section's closing note, immediately after
  the roster and the "You can override this" pointer.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Codex/ChatGPT login fallback is text-only. Assertions that need embeddings or moderation still require an API-key-backed provider override."
- **Our assessment**: A distinct failure class from the calibration drift in
  Claim 5. The ambient judge changes *what* the verdict means when it swaps
  models; this says the ambient judge can lack a *capability* the assertion
  needs, so the failure is a missing provider class rather than a differently
  opinionated one. In practice this constrains the Codex-login path (a laptop
  logged into ChatGPT, no API keys) for any suite that mixes `llm-rubric` with
  embedding- or moderation-backed asserts: the text asserts grade, the others
  need an explicit provider, and nothing in the run's pass/fail output says
  which asserts were graded by which provider class. The same "a default
  judge is a function of the environment, not of the config" thesis as Claim
  5, one step more dangerous because it is invisible in the report rather than
  merely surprising.

### Claim 7: `not-llm-rubric` is fail-closed in both directions — grader transport or parse failures are reported as failures, so inversion never turns a failed grader call into a pass; this is the third per-assert instance of that sentence (after the hub note's `not-trajectory:goal-success` and the g-eval note's `not-g-eval`)
- **Evidence**: The "Negation with not-llm-rubric" section: the invert
  sentence, the worked `not-llm-rubric` assert, and the failure-semantics
  sentence (verbatim below).
- **Confidence**: settled (documented product behavior)
- **Quote**: "not-llm-rubric passes when the rubric criterion does not match. Transport or parse failures from the grader are reported as failures in both directions — a grader error is not treated as evidence that the criterion was or was not met, so inversion never silently turns a failed grader call into a pass."
- **Our assessment**: Valuable as a *third* data point, and the wording is
  now near-identical across pages, which makes a family-level statement
  tempting — I do not make it. All three statements are scoped to the
  *inverted* form ("in both directions" means the judge failure is not
  attributed to the criterion, whichever way the assertion is pointed), and no
  page states the analogous property for the *positive* form of `llm-rubric`.
  So the hub note's (#1305 Claim 4) asymmetry finding stands unchanged: a
  `not-llm-rubric` "must not apologize" gate cannot be waved through by a
  broken judge, while a positive `llm-rubric` gate's broken-judge behavior is
  undocumented. What the three instances do establish is a *convention*: every
  `not-` section in the model-graded family that has been mined so far carries
  the same fail-closed sentence, so an operator auditing a negation assert
  should expect it and should treat its absence on a *new* assert type as a
  question for the vendor rather than as an implied pass.

### Claim 8: A custom `llm-rubric` provider can return its own `metadata`, and promptfoo copies those keys onto the assertion's `GradingResult.metadata` alongside `renderedGradingPrompt` — making per-assertion fields such as upload IDs or trace IDs available in hooks like `afterEach`
- **Evidence**: The closing paragraph of the "Setting grader parameters
  (temperature, etc.)" subsection.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Custom llm-rubric providers can also return a metadata object in their ProviderResponse. promptfoo copies those keys onto the assertion's GradingResult.metadata alongside renderedGradingPrompt, which makes per-assertion fields such as upload IDs or trace IDs available in hooks like afterEach."
- **Our assessment**: The correlation-id plumbing between an eval verdict and
  the request that produced it — the mechanism that lets a failing gate row
  be joined to the trace/upload it came from *after* the fact, without
  re-running. That is the difference between a gate you debug by re-running
  and a gate you debug by query, and it is the eval-side counterpart to the
  Ch02/trace-correlation material. It also arrives with an implicit
  caveat worth stating: the provenance data comes from the *judge provider's*
  response, so if the judge is the ambient one (Claim 5) the metadata's
  trustworthiness is exactly as good as the judge's self-report — the field
  records what the grader said it did, which is a claim, not proof. Pair it
  with the `renderedGradingPromptAudio` marker (Claim 4), which is
  promptfoo's own generated evidence rather than a provider-supplied one,
  and note the two live in the same metadata object.

### Claim 9: The vendor's own steer is that an agent-capable grader belongs in `agent-rubric`, not in `llm-rubric` — an agent provider *can* be supplied to `llm-rubric`, but the page routes file-inspecting and tool-using grading to the dedicated type because it "makes the capability intentional, validates that the grader is an agent runtime, and uses an agent-oriented safety prompt"
- **Evidence**: The "How it works" section's agent-rubric paragraph, directly
  after the Codex-login text-only note.
- **Confidence**: settled for the documented steer (the page states the
  recommendation and the three reasons); the safety comparison itself is the
  vendor's judgment, not a measured property
- **Quote**: "When a judge needs to inspect files or use coding-agent tools as part of grading, use agent-rubric. Although an agent provider can also be supplied to llm-rubric, agent-rubric makes the capability intentional, validates that the grader is an agent runtime, and uses an agent-oriented safety prompt."
- **Our assessment**: The first place in the corpus where the vendor states
  the trade-off in terms of *safety posture* rather than capability — the
  plain-rubric type is the one that does not validate what it is holding and
  does not switch to an agent-oriented safety prompt, so an agent provider
  quietly passed to `llm-rubric` gets a plain judge's instructions while
  holding an agent's privileges. That is a privilege/prompt mismatch of
  exactly the kind the indirect-prompt-injection material (#401) describes
  from the tested-agent side: the grader processes untrusted target output,
  and whether it treats that output as *evidence* rather than *instructions*
  depends on which assertion type the config named. The operational rule:
  choose the assert type by the grader's *capability class*, and if the grader
  can run tools, it must be `agent-rubric` (whose isolation/sandbox guidance
  the hub note's Claim 11 already records) rather than a provider block on a
  plain rubric assert.

### Claim 10: The override precedence is stated as an exact three-level chain on this page — `assertion.provider` > `test.options.provider` > `defaultTest.options.provider` — with the shorthand-provider trap restated as "unless you also repeat the full object there", and the `temperature=0` note sharpened to "only needed when you're pointing at a different model or provider whose default differs"
- **Evidence**: The "Setting grader parameters" subsection's precedence
  paragraph and its `note` block, plus the three override forms in
  "Overriding the LLM grader".
- **Confidence**: settled (documented product behavior) — but see Our
  assessment: this is re-confirmation, not a new mechanism
- **Quote**: "Provider precedence is exact: assertion.provider overrides test.options.provider, which overrides defaultTest.options.provider. If your default grader is a full object with config, do not add a shorthand provider: openai:chat:... on the assertion unless you also repeat the full object there." and "The built-in OpenAI grader already defaults to temperature=0, so this override is only needed when you're pointing at a different model or provider whose default differs. GPT-5 series reasoning models ignore temperature and do not need it set."
- **Our assessment**: Included as a *sharpen*, not a discovery: the hub note
  (#1305 Claims 2 and 7) already holds the precedence chain, the
  shorthand-drops-`config` trap, the built-in `temperature=0` default, and
  the GPT-5-ignores-temperature caveat, and this page says the same four
  things. The two genuine deltas are (a) this page orders
  `test.options.provider` above `defaultTest.options.provider` as *distinct*
  levels, where the hub compressed them into one tier — worth a line in a
  config review, because the test-level block is the one an author edits last
  and forgets; and (b) the precedence sentence pairs the shorthand trap with
  its remedy ("repeat the full object there") rather than with the
  alternative. Recording it so the Assayer can see the delta was checked
  rather than skipped.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/
(the section each comes from is named). The default-judge roster is a bulleted
list on the page; backticks mark the page's inline code spans.

### Audio-capable grader config (verbatim from "Audio output")

```yaml
assert:
  - type: llm-rubric
    value: The speaker sounds calm and speaks at a steady pace.
    provider:
      id: openai:chat:gpt-audio-1.5
      config:
        modalities: [text]
```

### Audio input contract and degradation modes (verbatim paragraph from "Audio output")

> The target must return inline base64 audio with format: wav or format: mp3,
> up to 20 MiB. Blob references and other formats produce a grading error. The
> built-in Realtime provider converts its default PCM16 output to WAV,
> including in persistent conversations; use output_audio_format: pcm16 for
> grading. Text-only graders retain their existing behavior and evaluate the
> text output or transcript.
>
> An assertion with transform grades the transformed text and does not attach
> the original audio. Successful audio grades include
> renderedGradingPromptAudio: true in assertion metadata;
> renderedGradingPrompt contains the text prompt without the attached audio
> bytes.

### Default judge per ambient credential (verbatim roster from "How it works")

```
- OpenAI API key: gpt-5
- Codex/ChatGPT login: openai:codex-sdk when the Codex SDK package is
  installed, Codex is signed in, and no higher-priority API credentials are set
- Anthropic API key: claude-sonnet-4-5-20250929
- Google AI Studio API key: gemini-2.5-pro (GEMINI_API_KEY, GOOGLE_API_KEY, or PALM_API_KEY)
- Google Vertex credentials: gemini-2.5-pro (service account credentials)
- Mistral API key: mistral-large-latest
- GitHub token: openai/gpt-5
- Azure credentials: Your configured Azure GPT deployment
```

(Line-wrapped here for width; the page renders each as one bullet.)

Verbatim preamble: "Under the hood, llm-rubric uses a model to evaluate the
output based on the criteria you provide. By default, it uses different models
depending on which API keys are available:"

Verbatim override pointer: "You can override this by setting the provider
option (see below)."

### Grader judge verdict shape (verbatim from "How it works")

```json
{
  "reason": "<Analysis of the rubric and the output>",
  "score": 0.5, // 0.0-1.0
  "pass": true // true or false
}
```

### Grader parameters via the object form (verbatim from "Setting grader parameters (temperature, etc.)")

```yaml
assert:
  - type: llm-rubric
    value: Is not apologetic and provides a clear, concise answer
    provider:
      id: openai:gpt-5-mini
      config:
        temperature: 0
```

"The same shape works under defaultTest.options.provider and
test.options.provider."

### Negation form (verbatim from "Negation with not-llm-rubric")

```yaml
assert:
  - type: not-llm-rubric
    value: Apologizes or hedges before answering
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) **Claim 1**
    — "By default, the judge behind every model-graded assertion is unpinned
    — promptfoo's built-in grading provider picks its model from whichever
    credentials happen to be present in the environment." This page is the
    enumeration that claim asserted: the same credential families (OpenAI,
    Anthropic, Google AI Studio, Vertex, Mistral, GitHub, Azure, Codex login)
    now resolve to named model IDs (Claim 5), and the Codex-login entry adds
    the state-dependent condition. This is a sharpening of Claim 1, not a
    replacement — Claim 1's "unpinned" remains the finding; the roster is its
    checkable form. (Verified: read Claim 1 and the "Overriding the LLM
    grader" quote in #1305 directly.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 10** — the
    score-blind `llm-rubric` pass (`{"pass": true, "score": 0}` passes with no
    `threshold`, `pass` defaulting to `true`). This page states the identical
    semantics, including the same worked example, so the guide's Ch05
    "A gate that cannot fail is not a gate" row has now two independent
    citations on the same per-type page. Deliberately **not** re-extracted as
    a new claim here. (Verified: read Claim 10 and its quotes in #1305.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claims 2 and 7** —
    the grader-override precedence + shorthand-`config`-inheritance trap, and
    the "built-in grader already runs at `temperature=0`; GPT-5 series ignores
    `temperature`" pair. Restated on this page (Claim 10) with the extra
    `test.options.provider` vs `defaultTest.options.provider` ordering.
    (Verified: read Claims 2 and 7 in #1305.)
  - `source-notes/docs-promptfoo-g-eval.md` (#1349) **Claim 5** — the
    symmetric fail-closed inversion: "`not-g-eval` passes when the grader score
    is below the threshold. Transport or parse failures from the grader are
    reported as failures in both directions…". This page's `not-llm-rubric`
    sentence (Claim 7) is the same wording on a different assert type — the
    convention is now visible across two per-type pages plus the hub's
    `not-trajectory:goal-success`. Also **Claim 7** of that note (expanding the
    provider shorthand into `id`+`config` to pin `temperature`) is the same
    mechanism restated here. (Verified: read Claims 5 and 7 in
    `docs-promptfoo-g-eval.md` directly.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 11** — the
    `agent-rubric` note (coding-agent grader, `openai:codex-sdk` default,
    read-only sandboxing, `metadata.agentProvider`). This page is the
    *routing* side of that claim: it states that an agent provider can be
    supplied to `llm-rubric` but that the capability should be made
    intentional via `agent-rubric`, with the grader-safety reason stated
    (Claim 9). (Verified: read Claim 11 in #1305.)
  - `source-notes/blog-promptfoo-model-upgrades-break-agent-safety.md` (#482)
    **Claim 2** — "Pin model IDs and safety settings — do not ship 'latest'"
    plus re-run-the-suite-on-upgrade. Claim 5 is the eval-judge version of
    exactly that rule: a model-graded gate that does not pin its judge is
    shipping an unpinned model, and the roster shows which one it shipped
    depends on the runner's environment. (Verified: read Claim 2 and its
    quotes in #482 directly.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` (#261)
    **Claim 11** — "Specific judge rubrics beat vague ones" (explicit pass/fail
    criteria make different judge models converge). The ambient-judge roster
    (Claim 5) is the config-side reason this matters: with the judge free to
    change, rubric specificity is the only variance control left, and
    `rubricPrompt` (plus the object-form `config`) is where that specificity
    lives. (Verified: read Claim 11 in #261 directly.)
  - `source-notes/docs-promptfoo-answer-relevance.md` **Claim 1** — the
    two-provider-class structure (a text provider for question generation *and*
    an embedding provider for similarity). Claim 6's "assertions that need
    embeddings or moderation still require an API-key-backed provider
    override" is the same two-class reality seen from the ambient-default side:
    a suite with an embedding-backed assert cannot be fully served by the
    text-only Codex-login fallback. (Verified: read Claim 1 and its quotes in
    `docs-promptfoo-answer-relevance.md` directly.)
  - `source-notes/blog-promptfoo-indirect-prompt-injection-web-agents.md`
    (#401) — the grader-side LLM-judge and untrusted-content framing that
    Claim 9's "use `agent-rubric` so the grader gets an agent-oriented safety
    prompt" instantiates: whether the judge treats untrusted target output as
    evidence rather than instructions is a function of the assertion type
    chosen. (Verified: the hub note (#1305) already cites #401 Claims 10/11
    for this framing; confirmed the #401 note exists in `source-notes/` with
    that content — see Extraction Notes for the exact scope of this citation.)

- **Contradicts**: No new contradiction filed. The only candidate tension is
  the default-judge pin, and it is **already filed as #1352** (open,
  `needs-resolution`): hub #1305 Claim 1 ("nothing is pinned") vs the g-eval
  per-type page's `gpt-4.1-2025-04-14`. This page is evidence *for* that
  contradiction's open question rather than a new conflict, so per MINER.md
  §4a I am not picking a verdict here and not filing a duplicate:
  - For `llm-rubric`, the page carries **both** formulations — the credential
    roster ("By default, it uses different models depending on which API keys
    are available") and the flat pin ("By default, llm-rubric uses gpt-5 for
    grading", in the "Overriding the LLM grader" section) — and the roster sits
    earlier on the same page, which makes the flat sentence readable as the
    OpenAI-credential branch rather than an absolute pin.
  - That is the same page structure the g-eval side of #1352 has, but I did
    **not** re-read the g-eval page in this extraction, so whether it also
    carries a credential roster is unverified here. This note therefore
    neither extends nor resolves #1352; it is offered to the resolver as a
    hypothesis to check, with the `llm-rubric` observation recorded in Claim 5.
  - Also checked: the `not-` fail-closed sentence (Claim 7) sits on the same
    fail-closed side as the hub's Claim 4 and the g-eval note's Claim 5, so it
    corroborates rather than opposes. The precedence chain (Claim 10) is
    consistent with the hub's ordering. `CONTRADICTIONS.md` has no open
    `C-NNN` entries; the only open `contradiction`-labeled issues are #1307
    (missing-trace semantics) and #1352 (judge pin).

- **Extends**:
  - `source-notes/docs-promptfoo-model-graded-metrics.md` (#1305) — closes
    the "llm-rubric was not followed" gap its Extraction Notes records, for
    the deltas listed above (audio channel, judge roster, Codex-login
    text-only limit, metadata passthrough, `not-` sentence). The shared
    material (threshold semantics, multilingual `rubricPrompt`,
    `PROMPTFOO_DISABLE_OBJECT_STRINGIFY`, vars-in-rubric, `showThinking`) is
    cited above rather than re-extracted.
  - `source-notes/docs-promptfoo-javascript-assertions.md` **Claim 1** — the
    `boolean | number | GradingResult` return contract and the `GradingResult`
    shape; this page documents the other direction of that same object — a
    custom judge provider *populating* `GradingResult.metadata` (Claim 8) —
    so the custom-JS and custom-provider extension points meet on one
    structure. (Verified: read Claim 1 in
    `docs-promptfoo-javascript-assertions.md` directly.)
  - `source-notes/docs-promptfoo-factuality.md` **Claim 4** — that note records
    the factuality page's *silence* on its default grader and places it on
    #1352's ambient side. This page supplies the contrasting case: a per-type
    page that *does* document its roster, and whose silence-vs-roster
    difference is exactly the discriminator a resolver needs for #1352.
    (Verified: read Claim 4 and its assessment in
    `docs-promptfoo-factuality.md` directly.)
  - `source-notes/docs-promptfoo-model-graded-context-recall.md` **Claim 2**
    — the score-blind/fail-open per-assert family (`threshold` documented as
    `(default: 0)` there, `llm-rubric`'s version of the same class is the hub
    note's Claim 10). This page adds the audio analogue: an assertion that
    cannot fail on the property its rubric names because the graded artifact
    is not what the rubric describes (Claim 3). (Verified: read Claim 2 in
    `docs-promptfoo-model-graded-context-recall.md` directly.)

- **Novel**:
  1. **A non-text judge input surface.** `response.audio` attached to the
     grading request, an audio-capable OpenAI Chat Completions grader,
     `modalities: [text]` for the verdict, inline base64 wav/mp3 ≤ 20 MiB, blob
     refs erroring, the Realtime PCM16→WAV conversion, and
     `output_audio_format: pcm16` (Claims 1-2). Nothing in the corpus
     documented a non-text channel into a model-graded verdict — `grep` for
     `response.audio`, `renderedGradingPromptAudio`, `output_audio_format`, and
     `gpt-audio` across `source-notes/` and `guide/` returns **zero** hits
     (the audio material elsewhere in the corpus is LiteLLM transcription,
     Langfuse multimodal datasets, and Gemini multimodal red-teaming — none of
     it an eval-grader input).
  2. **The `transform`-drops-audio silent degradation** (Claim 3) — a config
     property that makes an audio gate incapable of failing while it reports
     normal verdicts.
  3. **A positive, per-assertion evidence marker for the graded channel**
     (`renderedGradingPromptAudio`) and the explicit statement that
     `renderedGradingPrompt` does *not* include the audio bytes (Claim 4).
  4. **The per-credential default-judge roster with concrete model IDs**
     (Claim 5) — new detail, and the first corpus statement of which judge a
     given ambient credential actually selects.
  5. **The Codex/ChatGPT-login fallback's text-only boundary** (Claim 6) — a
     capability gap in the ambient default, not a calibration difference.
  6. **Custom-judge `metadata` passthrough to `GradingResult.metadata` and
     `afterEach` hooks** (Claim 8) — the eval-verdict → request correlation
     path (upload IDs, trace IDs).
  7. **The vendor's own steer that agent-capable grading belongs in
     `agent-rubric`** for safety-prompt reasons, not only capability reasons
     (Claim 9).

## Guide Impact

- **Chapter 05 (`### A gate that cannot fail is not a gate`) — add a row to
  the "six independent ways to report green while verifying nothing" table.**
  The existing `llm-rubric` row cites #1305 Claim 10 (score-blind pass). This
  note adds a second, independent `llm-rubric` row on the *audio* axis: an
  audio-grade assert carrying a `transform` grades the transformed text and
  never attaches the audio — "An assertion with transform grades the
  transformed text and does not attach the original audio" [source:
  docs-promptfoo-llm-rubric, Claim 3] — so a tone/pacing/pronunciation rubric
  is applied to a transcript and the run reports a normal verdict. Same class
  as the table's other rows (a property of the config, reviewable before the
  run, invisible in the report), and the source-side fix is a rule, not a
  knob: `transform` and audio grading are mutually exclusive per assertion.
- **Chapter 05 (judge-pinning rule) — upgrade "the judge is ambient" from a
  mechanism to a checklist.** The rule currently derives from #1305 Claim 1;
  this note gives it a concrete grep list (Claim 5): `OPENAI_API_KEY` →
  `gpt-5`, `ANTHROPIC_API_KEY` → `claude-sonnet-4-5-20250929`, Gemini/Vertex
  → `gemini-2.5-pro`, `MISTRAL_API_KEY` → `mistral-large-latest`, a GitHub
  token → `openai/gpt-5`, Azure → whatever deployment is configured, and a
  signed-in Codex CLI → `openai:codex-sdk` (state-dependent, invisible in
  config). Add the corollary (Claim 6): if the suite contains embedding- or
  moderation-backed asserts, a text-only fallback is not enough — assert a
  pinned, API-key-backed judge explicitly. Note in the text that three of the
  roster entries are floating even by name, so "pin the judge" cannot be
  satisfied by copying the defaults.
- **Chapter 05 (can the gate tell a model break from a broken judge?) — add
  the positive-marker rule.** For any channel the report does not render, the
  checklist should require evidence the judge received that channel, not
  infer it from a verdict: "Successful audio grades include
  renderedGradingPromptAudio: true in assertion metadata;
  renderedGradingPrompt contains the text prompt without the attached audio
  bytes" [source: docs-promptfoo-llm-rubric, Claim 4]. Pair with the
  correlation path (Claim 8): custom `llm-rubric` providers can put upload /
  trace IDs on `GradingResult.metadata` for `afterEach` hooks, so a failing
  gate row is joinable to the request that produced it without a re-run — and
  flag that this provenance is provider-*reported* (weaker than the
  promptfoo-generated marker).
- **Chapter 06 (red-team configs) — the guide's own example asserts are live
  instances of the unpinned, score-blind pattern.** `guide/06-security-and-trust.md`
  shows `llm-rubric` asserts in Test 1 (refuses data export) and Test 2
  (architecture-leak refusal) with a pinned *target* model and no `threshold`
  and no judge `provider` — i.e. exactly the config that (a) draws its verdict
  from the ambient judge (Claim 5) and (b) passes on the judge's `pass` field
  alone. Recommend either annotating those examples with `threshold: 1` (or a
  judge `provider` block) or marking them illustrative-only, so a reader does
  not copy an unpinned, score-blind gate out of the guide. Per Claim 9, prefer
  `agent-rubric` over passing an agent provider when a red-team grader needs
  to inspect files or run tools — the vendor's reason is the agent-oriented
  safety prompt, which is the grader-side half of the untrusted-content
  material already in Ch06.
- **Chapter 05 / Ch02 (conditional) — if a voice gate is ever written up as
  an SLI**, state its unit and its ceilings: the grade is a 0.0-1.0 judge score
  over an audio artifact, the audio travels inline in the grading request and
  in persisted assertion metadata up to 20 MiB per assertion, blob-reference
  audio is not gradeable at all, and a target that returns audio by reference
  (a normal design for long audio) is silently outside the gate. That is a
  measurement-design question, not a promptfoo question, and it only becomes
  real if the guide takes a position on audio evaluation.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/).
  Footer reads "Last updated on Sep 26, 2026 by mldangelo-oai" — page undated,
  so `date_published` carries the last-updated date (same convention as the
  sibling notes #1287/#1288/#1289/#1305). Every quote above was verified
  character-for-character against the fetched rendered text (a second pass over
  the raw HTML to confirm wording and the inline-code spans); code blocks
  copied verbatim. The default-judge roster is line-wrapped in Concrete
  Artifacts for width, which is stated inline there.
- **Scope discipline (per the triage's "extract the delta, not the page")**:
  deliberately **not** re-extracted as claims because #1305 already holds them
  verbatim — Threshold Support, Pass vs. Score Semantics + Common
  misconfiguration (score-blind pass; #1305 Claim 10), the grader-override
  forms and shorthand-`config` trap (Claim 2 there, restated here only as the
  sharpen in Claim 10), multilingual `rubricPrompt` Option 1 (Claim 8 there),
  vars-in-rubric hallucination detection (Claim 9 there), object handling /
  `PROMPTFOO_DISABLE_OBJECT_STRINGIFY` (Claim 9 there), `showThinking: false`
  (Claim 5 there), and the built-in-`temperature=0` note (Claim 7 there). The
  multilingual **Options 2 and 3** (a language instruction appended to the
  rubric value — verbatim: "Responds politely and helpfully. Provide your
  evaluation reason in German." — and a fully native-language rubric, Japanese
  and German examples) are recorded here only in this note: they add no
  mechanism beyond #1305 Claim 8's override surface, which already carries the
  assertion-family reach restriction that this page restates verbatim
  ("Note: Option 1 works with llm-rubric, g-eval, and model-graded-closedqa.
  For other assertion types like factuality or context-recall, create
  assertion-specific prompts that match their expected formats."). Also not
  re-extracted: the `# ❌ Problem` / `# ✅ Option A`/`Option B` fix pair for
  the 0/1-rubric misconfiguration, identical in mechanism to #1305 Claim 10.
- **Sub-pages followed: none.** This page's outbound links are
  `agent-rubric` (already mined at #1305 Claim 11), the vLLM provider guide's
  judge recipe (the #1305 Claim 5/6 material, which this page cross-references
  rather than restates), the model-graded overview (#1305 itself), and the
  object-template-handling troubleshooting anchor (#1305 Claim 9). Per MINER.md
  §1 I checked whether any was a substantive new surface: each is a link-line
  pointer to material already extracted with claim-level depth, so none was
  re-fetched. The parent hub page and the two adjacent siblings (Factuality =
  already mined; Max Score = open issue #1472) were not followed either.
- **Triage key-question resolutions**: (a) the per-credential default-judge
  table is extracted verbatim as an artifact and as Claim 5, including the
  Codex-login text-only boundary (Claim 6); (b) `not-llm-rubric` fail-closed
  is extracted as the third instance of that sentence (Claim 7), and I answer
  the triage's question — is it now strong enough to state fail-closed as a
  family-level property? — as **no**: all three statements are scoped to the
  *inverted* form, and no page documents the positive form, so the guide should
  keep labeling it per-assert. What is new is that the wording is now
  consistent across pages, which makes the *absence* of that sentence on a
  future assert type a question worth asking; (c) the precedence caveat is
  extracted as a sharpen only (Claim 10) because the mechanism is the hub's.
- **No contradiction issue filed**, per MINER.md §4a — the only tension found
  (per-type pinned-ID sentence vs the family-wide ambient claim) is already
  filed as **#1352** and this page's evidence is recorded under
  **Contradicts:** for the resolver, with no verdict picked here. I did not
  re-read the g-eval page to test whether it carries a credential roster like
  this one does, so #1352 is neither extended nor resolved by this note.
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — each cited or dismissed
  by name):
  - `docs-promptfoo-model-graded-metrics.md` — **cited heavily** (Corroborates
    Claims 1/2/7/10/11; Extends; the Contradicts discussion).
  - `docs-promptfoo-g-eval.md` — **cited** (Corroborates Claims 5 and 7), found
    by searching `source-notes/` since it was not in the candidate list.
  - `docs-promptfoo-factuality.md` — **cited** (Extends, Claim 4), in the
    candidate list.
  - `docs-promptfoo-classifier-grading.md` — fixed-classifier rung; its judge
    trust caveats (Claim 5's threshold non-portability) are the deterministic
    side of the boundary this page's ambient-judge roster is the other side of,
    but no claim of it is corroborated or extended here; **dismissed**.
  - `blog-promptfoo-owasp-red-teaming.md` — red-team SDLC/CI-integration
    methodology; no judge-grading config surface; **dismissed**.
  - `blog-promptfoo-red-team-gemini.md` — per-model red-team plugin config and
    reasoning-DoS plugins; touches multimodal attack surface but nothing about
    eval-grader input channels; **dismissed**.
  - `docs-litellm-batches-api.md` — LiteLLM rate-limit/batch accounting; no
    eval-judge semantics; **dismissed**.
  - `blog-pagerduty-sre-agent-triage.md` — LLM-as-judge *alerting* for incident
    triage; no eval-assert config surface; **dismissed**.
  - `blog-promptfoo-red-team-claude.md` — per-model red-team config; its
    `llm-rubric`-as-tool framing was already used by #1305 to source the
    semantics this page documents, so citing it again would be circular;
    **dismissed** (with that reasoning recorded).
  - `docs-promptfoo-model-graded-context-recall.md` — **cited** (Extends,
    Claim 2), in the candidate list.
  - `docs-google-sre-team-lifecycles.md` — Google SRE workbook chapter on team
    lifecycles; no LLM-eval content; **dismissed**.
  - Additionally found by searching `source-notes/` and cited:
    `docs-promptfoo-answer-relevance.md` (Claim 1),
    `docs-promptfoo-javascript-assertions.md` (Claim 1),
    `blog-promptfoo-model-upgrades-break-agent-safety.md` (Claim 2),
    `blog-promptfoo-asr-not-portable-metric.md` (Claim 11).
  - `blog-promptfoo-indirect-prompt-injection-web-agents.md` (#401) is cited
    under Corroborates for Claim 9's grader-safety steer; the supporting
    claim numbers (#401 Claims 10/11, the LLM-grader + untrusted-content
    framing) were verified via the #1305 note's own verified cross-reference
    to that note rather than by re-reading #401 in this pass — treat the
    #401 claim numbers as carried-over-and-consistent, not re-verified here.
- **Cross-ref verification (§4b)**: every cited claim number was located in the
  cited note before writing — #1305 Claims 1/2/7/10/11, `g-eval` Claims 5/7,
  `answer-relevance` Claim 1, `context-recall` Claim 2, `factuality` Claim 4,
  `javascript-assertions` Claim 1, #482 Claim 2, #261 Claim 11 — and each
  claim's content checked against what it is cited for. No claim numbers
  invented; no quotes attributed to other notes.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1288, #1289, #1305, #1349): the individual
  mechanism/default claims are settled-for-product-behavior and directly
  checkable against an installed CLI, but this is vendor documentation with no
  measured judge-agreement, gate-failure, or cost figures, no independent
  practitioner validation, and an unevidenced comparative claim
  ("can be more effective and robust in certain cases"). The operational
  framing (silent audio degradation, credential-dependent judge
  determinism, provenance strength of provider-reported metadata) is the
  Miner's synthesis on top of documented behavior.
- **No CLI probe was run** in this trial (no promptfoo install in the Miner
  environment), so the audio-grading mechanics, the credential→judge roster,
  and the `not-` failure semantics are documented-behavior claims, verified
  against the page text only.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
