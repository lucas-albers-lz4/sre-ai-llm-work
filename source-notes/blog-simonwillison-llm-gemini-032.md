---
source_url: https://simonwillison.net/2026/May/19/llm-gemini-2/
source_type: blog-post
title: "llm-gemini 0.32"
author: Simon Willison
date_published: 2026-05-19
date_extracted: 2026-05-28
last_checked: 2026-05-28
status: current
confidence_overall: anecdotal
issue: "#973"
---

# llm-gemini 0.32

> A one-bullet release announcement adding `gemini-3.5-flash` to the `llm` CLI's Gemini plugin — notable primarily for its same-day availability with the Google I/O GA launch, demonstrating the rapid-response pattern in the `llm` plugin ecosystem for newly-released models.

## Source Context

- **Type**: blog-post (Willison "beat" format — a minimal link-blog post, under 100 words, containing a single release-note bullet and two cross-links; this is the thinnest source format used on simonwillison.net)
- **Author credibility**: Simon Willison is the creator of the `llm` CLI and the llm-gemini plugin itself. This is first-party release documentation from the plugin's author — factual accuracy about what was added is high. The post contains no practitioner analysis; it is a minimal changelog pointer, not an experience report.
- **Scope**: A single feature: `gemini-3.5-flash` model availability in the llm-gemini plugin. Cross-links to a separate, more substantive post about Gemini 3.5 Flash itself (already mined as `blog-simonwillison-gemini35-flash-pricing.md`). Does NOT include workflow guidance, code examples, plugin architecture discussion, or any mention of the llm 0.32 API architectural changes.

## Extracted Claims

### Claim 1: The llm-gemini plugin version 0.32 adds `gemini-3.5-flash` as a new accessible model via the `llm` CLI

- **Evidence**: Verbatim release note bullet from both the blog post and the linked GitHub release page (https://github.com/simonw/llm-gemini/releases/tag/0.32). This is the only change documented in the 0.32 release.
- **Confidence**: settled (first-party release documentation from the plugin's creator; GitHub release confirms the sole change)
- **Quote**: "New model `gemini-3.5-flash` for Gemini 3.5 Flash."
- **Our assessment**: The plugin release makes Gemini 3.5 Flash accessible to any practitioner using the `llm` CLI toolchain via `llm install llm-gemini` followed by `llm -m gemini-3.5-flash`. Viewed alongside `blog-simonwillison-gemini35-flash-pricing.md` (which documents the model's pricing, specifications, and benchmark costs in depth), this release note is the access-path counterpart — the how vs. the what. For practitioners already in the `llm` ecosystem, the upgrade path is `llm install -U llm-gemini` with no other configuration required.

### Claim 2: The llm-gemini 0.32 plugin was published the same day as Google's GA launch of Gemini 3.5 Flash at Google I/O (May 19, 2026)

- **Evidence**: Post timestamp ("Posted 19th May 2026 at 11:46 pm"); `blog-simonwillison-gemini35-flash-pricing.md` Claim 1 confirms Gemini 3.5 Flash launched at Google I/O on May 19, 2026. The GitHub release page confirms the commit on May 19.
- **Confidence**: settled (post date and GitHub release date are both May 19, 2026)
- **Quote**: (no direct quote; date inferred from "Posted 19th May 2026 at 11:46 pm")
- **Our assessment**: Same-day plugin availability demonstrates the rapid-response pattern in the `llm` ecosystem: when a major model launches at GA, the plugin ecosystem can respond within hours. This mirrors the pattern documented in `blog-simonwillison-llm-openrouter-06.md` Claim 2, where Willison added the `llm openrouter refresh` command specifically to test Kimi 2.6 as soon as it appeared on OpenRouter. Both cases show the toolchain being updated reactively to model availability. For harness engineers evaluating different model-access patterns, the `llm` plugin ecosystem consistently demonstrates 0-day or near-0-day model availability.

### Claim 3: Willison tested Gemini 3.5 Flash using the updated plugin on the same day as the plugin release, using his standard "pelican on a bicycle" benchmark

- **Evidence**: Willison's own statement in the post, linking to both his Gemini 3.5 Flash notes and the pelican SVG output generated via the plugin.
- **Confidence**: settled (first-party statement; the linked notes are from the same date)
- **Quote**: "See also my notes on Gemini 3.5 Flash, and the pelican I drew using this upgrade to the plugin."
- **Our assessment**: This is the third in-corpus case where Willison updates a plugin or installs a new model access path and immediately runs the pelican benchmark as validation — after GPT-5.5 via Codex plugin (`blog-simonwillison-gpt55-codex-plugin.md`) and Kimi 2.6 via llm-openrouter (`blog-simonwillison-llm-openrouter-06.md`). The pelican test functions both as a functional test (does the model work via the plugin?) and as a cross-model creative-code capability comparison. The workflow "plugin update → immediate pelican benchmark → notes published same day" is a repeatable practitioner validation pattern.

## Concrete Artifacts

### llm-gemini 0.32 release notes (verbatim)

```
llm-gemini 0.32 — LLM plugin to access Google's Gemini family of models

Release notes:
  - New model `gemini-3.5-flash` for Gemini 3.5 Flash.

Released: May 19, 2026 at 11:46 pm
Source: github.com/simonw/llm-gemini/releases/tag/0.32
```

### CLI access path for Gemini 3.5 Flash via the `llm` plugin

```bash
# Install the llm-gemini plugin (first time)
llm install llm-gemini

# Upgrade to 0.32 to get gemini-3.5-flash
llm install -U llm-gemini

# Access Gemini 3.5 Flash via the llm CLI
llm -m gemini-3.5-flash 'Your prompt here'
```

*Source: llm plugin system conventions, with model slug `gemini-3.5-flash` confirmed verbatim by the 0.32 release note.*

## Cross-References

- **Corroborates**:
  - `blog-simonwillison-gemini35-flash-pricing.md` Claim 1: That note confirms Gemini 3.5 Flash launched at Google I/O on May 19, 2026 as a GA release — skipping the preview qualifier used by prior Gemini 3.x models. The same-day plugin release confirms the model was production-accessible via the `llm` CLI from day one.
  - `blog-simonwillison-llm-openrouter-06.md` Claim 2: The llm-openrouter note documents Willison adding the `refresh` command specifically to enable immediate access to a newly-launched model (Kimi 2.6 on OpenRouter). This source is a second instance of the same pattern: a plugin update released the same day as a model GA launch to enable immediate CLI access. Two examples from the same author establish this as a recurring rapid-response workflow, not a one-off.

- **Contradicts**: None identified.

- **Extends**:
  - `blog-simonwillison-gemini35-flash-pricing.md`: That note documents what Gemini 3.5 Flash is — pricing, specifications, benchmark costs, capabilities, and the Interactions API. This source provides the complementary access-path documentation: how practitioners reach the model via the `llm` CLI toolchain. Together, the two notes constitute a complete practitioner picture of Gemini 3.5 Flash: the model's properties (pricing note) and its CLI access mechanism (this note).
  - `blog-simonwillison-llm031.md` Claim 1: That note documents llm 0.31 adding native GPT-5.5 support — the same pattern of new-model access expansion in the `llm` ecosystem, on the OpenAI side. Together, `llm 0.31` (native GPT-5.5, April 24, 2026) and `llm-gemini 0.32` (`gemini-3.5-flash`, May 19, 2026) show the `llm` toolchain tracking model availability across vendors within weeks of each GA launch.
  - `blog-simonwillison-llm032a0.md`: The llm-gemini plugin version (0.32) aligns with the `llm` library architectural refactor (0.32a0, announced April 29, 2026). The version number proximity suggests llm-gemini 0.32 may incorporate compatibility with the new typed streaming parts and messages API introduced in the library refactor; however, the release note does not mention this explicitly. See Extraction Notes for the speculative nature of this connection.

- **Novel**:
  - **First in-corpus documentation of the `llm-gemini` plugin as a Gemini model access path**: No prior source note documents the `llm-gemini` plugin name, install command, or `gemini-3.5-flash` model slug for CLI use. This is the first in-corpus record of this specific access path.
  - **Third in-corpus example of the "same-day plugin update → pelican benchmark" pattern**: The first was GPT-5.5 via Codex plugin (`blog-simonwillison-gpt55-codex-plugin.md`), the second was Kimi 2.6 via llm-openrouter (`blog-simonwillison-llm-openrouter-06.md`), this is the third. Three instances strengthen the claim that Willison's pelican benchmark is a practitioner-level functional validation test applied immediately upon gaining new model access, not a retrospective comparison.

## Guide Impact

- **Chapter 01 (Daily Workflows — `llm` CLI model access)**: If the guide documents the `llm` CLI toolchain for accessing frontier models, add `llm-gemini` as the Gemini-family access plugin alongside llm-openrouter (multi-provider) and the built-in OpenAI plugin. The Gemini 3.5 Flash access path (`llm install llm-gemini && llm -m gemini-3.5-flash '...'`) is now documented. For completeness, the guide should distinguish three plugin access categories: (1) vendor-native plugins (`llm-gemini` for Gemini, `llm-openai-via-codex` before llm 0.31); (2) models built into the base `llm` package (OpenAI post-0.31); (3) multi-model aggregators (`llm-openrouter`). This source fills the Gemini-native plugin slot.

- **Chapter 02 (Harness Engineering — Model Selection Interface)**: The same-day plugin availability pattern (Claim 2) is relevant to harness engineers evaluating how quickly new models reach their toolchain. Both the Gemini 3.5 Flash case (0-day availability via llm-gemini) and the Kimi 2.6 case (0-day availability via `llm openrouter refresh`) demonstrate that the `llm` plugin ecosystem can provide sub-24-hour access to newly-launched GA models. This is a practical consideration when comparing plugin-based vs. SDK-based model access strategies — the plugin ecosystem's rapid release cadence is an operational benefit.

- **No substantial new patterns**: The Prospector triage assessment (novelty: low, substance: thin) was correct. This source is incremental tooling coverage; the model's characteristics and market context are fully documented in `blog-simonwillison-gemini35-flash-pricing.md`. The main guide value is the access-path documentation and the third data point on the rapid-response plugin workflow pattern.

## Extraction Notes

- **Very thin source (Willison "beat" format)**: The post is under 100 words and contains a single release-note bullet plus two cross-links. This is the minimal Willison publication format, designed for link-blog bookmarking rather than practitioner education. The Prospector's assessment ("expect low signal extraction") was accurate.
- **No sub-pages followed beyond GitHub release**: The GitHub release page (https://github.com/simonw/llm-gemini/releases/tag/0.32) confirms the sole change is the `gemini-3.5-flash` model addition. The linked Google I/O blog post (blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5/) and the Gemini 3.5 Flash notes (simonwillison.net/2026/May/19/gemini-35-flash/, already in corpus as `blog-simonwillison-gemini35-flash-pricing.md`) were not re-fetched as they are already mined.
- **Version number alignment (speculative)**: The llm-gemini plugin reaching version 0.32 on May 19, 2026, while the `llm` library's 0.32a0 alpha was published April 29, 2026 (`blog-simonwillison-llm032a0.md`), may indicate a deliberate version alignment or coincidence. The release note contains no statement about compatibility with the 0.32a0 architectural changes (typed streaming parts, messages API). This observation is noted under Extends without being elevated to an extracted claim.
- **Fragment URL in issue body**: The issue URL includes `#atom-everything` (Atom feed anchor). `source_url` uses the canonical page URL without the fragment, consistent with prior Willison source notes in this corpus.
- **CLI commands**: The `llm install llm-gemini` and `llm -m gemini-3.5-flash` commands are inferred from plugin system conventions documented in `blog-simonwillison-llm031.md`, `blog-simonwillison-llm-openrouter-06.md`, and `blog-simonwillison-gpt55-codex-plugin.md`. The plugin name `llm-gemini` and model slug `gemini-3.5-flash` are confirmed verbatim by the release note.
- **Cross-reference verification performed**: `blog-simonwillison-gemini35-flash-pricing.md` Claim 1 confirmed at lines 28-32 (Gemini 3.5 Flash GA launch, May 19, 2026 at Google I/O). `blog-simonwillison-llm-openrouter-06.md` Claim 2 confirmed at lines 32-36 (same-day Kimi 2.6 test motivation; `refresh` command). `blog-simonwillison-llm031.md` Claim 1 confirmed at lines 27-31 (native GPT-5.5 via llm 0.31). `blog-simonwillison-llm032a0.md` date_published 2026-04-29 confirmed at frontmatter line 6. All claim numbers verified by document-order count.
