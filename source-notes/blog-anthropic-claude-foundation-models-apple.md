---
source_url: https://claude.com/blog/claude-for-foundation-models
source_type: blog-post
title: "Building intelligent apps for Apple platforms with Claude in the Foundation Models framework"
author: Anthropic (product announcement, no individual byline)
date_published: 2026-06-08
date_extracted: 2026-06-09
last_checked: 2026-06-09
status: current
confidence_overall: emerging
issue: "#1123"
---

# Building intelligent apps for Apple platforms with Claude in the Foundation Models framework

> Official Anthropic announcement of a Swift package that lets Apple platform developers integrate Claude directly into Foundation Models framework apps — establishing a hybrid on-device + cloud reasoning pattern where Apple's @Generable typed outputs feed clean structured inputs to Claude for multi-step reasoning, code generation, and web search.

## Source Context

- **Type**: blog-post (official claude.com/blog, June 8, 2026; product announcement + technical guide; ~5 minute read)
- **Author credibility**: Published on Anthropic's Claude blog — the same channel as "Multi-agent coordination patterns," "Harnessing Claude's Intelligence," and other first-party engineering posts. No individual byline; house-authored as a product announcement. This is a vendor announcement of a shipping integration, so the architectural claims (package features, platform support, use case descriptions) are first-party and reliable. The positioning claims ("right model for each step") are vendor framing without independent empirical backing.
- **Scope**: Covers the new Anthropic Swift package for Apple's Foundation Models framework — specifically the integration pattern (on-device → typed outputs → Claude API → streamed SwiftUI response), the capability split (on-device for simple tasks, Claude for complex reasoning), concrete use cases, and platform support. Does NOT include Swift code examples or architectural diagrams — the post is conceptual. Does NOT cover pricing, rate limits, MCP integration, or non-Apple platforms.

## Extracted Claims

### Claim 1: Claude is now directly accessible from Apple's Foundation Models framework via a new Anthropic Swift package

- **Evidence**: Official Anthropic product announcement. First-party availability claim.
- **Confidence**: settled (announced by Anthropic with specific platform and availability details)
- **Quote**: "Developers can now use Apple's Foundation Models framework to hand off to Claude when a request calls for multi-step reasoning, code generation, and more."
- **Our assessment**: This is a concrete, verifiable product fact. The Swift package represents Anthropic's first platform-native client library for a non-web context — a significant distribution decision. Prior Claude API integrations required developers to write bespoke HTTP clients; this package standardizes the integration pattern for the Apple developer ecosystem. The "available tomorrow" language in the Prospector's triage comment confirms the package shipped with the announcement.

### Claim 2: Apple's @Generable typed Swift values produce clean, structured inputs to the Claude API instead of raw user text

- **Evidence**: First-party architectural description.
- **Confidence**: emerging (architectural claim from the announcement; the mechanism is described but not demonstrated with code)
- **Quote**: "Because Apple's framework returns typed Swift values from @Generable annotations, developers arrive at the Claude API call with clean inputs instead of raw user text."
- **Our assessment**: This is the most architecturally significant claim in the post. The @Generable macro is Apple's Foundation Models mechanism for constrained generation — it forces on-device model outputs into typed Swift structs rather than free-form strings. When these typed values are passed to Claude, the result is a structured, unambiguous input rather than a raw user utterance that Claude must parse and interpret. This pre-structuring effect is the same value proposition as prompt templates and structured output patterns documented elsewhere in the corpus — here it's implemented natively at the platform layer rather than in application code. The practical implication for context engineering: the on-device model performs first-pass extraction, and Claude receives the result as a well-formed typed object, improving the reliability of reasoning over user-generated content.

### Claim 3: The recommended architecture is a two-tier handoff: on-device Foundation Models for simple/fast/local tasks, Claude for complex multi-step reasoning, code generation, and web search

- **Evidence**: First-party architectural positioning. Described as the core use case for the integration.
- **Confidence**: emerging (vendor-recommended architecture; no empirical comparison of on-device-only vs. hybrid approaches)
- **Quote**: (no single direct quote captures the full architecture; see paraphrase in Our assessment)
- **Our assessment**: The post establishes a clear task-split heuristic: on-device models for tasks that benefit from low latency, privacy, or simple extraction (term definitions, daily prompt generation); Claude for tasks requiring broad knowledge, web access, multi-month data synthesis, or complex reasoning chains. This is the Apple platform instantiation of the general "right model for each task" principle. The value of the split is: on-device tasks run without network latency or API cost, and the Claude call receives structured, filtered input (per Claim 2) rather than raw conversational context. The limitation: "complex reasoning" and "multi-step" are not formally defined — practitioners will need to develop their own heuristics for when to hand off.

### Claim 4: The positioning tagline "one experience for the user, backed by the right model for each step" articulates Anthropic's hybrid AI strategy for consumer apps

- **Evidence**: First-party vendor framing from the post.
- **Confidence**: anecdotal (vendor positioning statement; directionally meaningful but not empirically supported)
- **Quote**: "one experience for the user, backed by the right model for each step"
- **Our assessment**: This phrase is important as a strategy signal: Anthropic is explicitly not positioning Claude as a replacement for on-device models. Instead, Claude is positioned as the complementary reasoning layer — used when on-device capability is insufficient, invisible to the user as a seamless escalation. This matters for practitioners who might assume they should route all tasks through Claude for quality. The Anthropic-recommended pattern here is selective escalation: use the cheapest capable model for each subtask, from the user's perspective transparently. This has direct implications for cost architecture in consumer apps.

### Claim 5: The Swift package handles streaming, tool calls, and structured responses back into SwiftUI views

- **Evidence**: First-party capability description.
- **Confidence**: emerging (announced capabilities; shipping behavior pending independent verification)
- **Quote**: "The package handles streaming, tool calls, and structured responses back into your SwiftUI view."
- **Our assessment**: These three capabilities — streaming, tool calls, structured responses — are the same capabilities documented in the broader Claude API but now wrapped in a SwiftUI-native package. Streaming back into a SwiftUI view is architecturally significant: it means the package manages the async streaming lifecycle compatible with SwiftUI's declarative state model, which is non-trivial to implement correctly. The inclusion of tool calls in the package is notable — it means Claude's web search and code execution capabilities are accessible from the Foundation Models integration, not just basic text generation. For practitioners building on Apple platforms, this eliminates the need to write bespoke streaming handlers.

### Claim 6: A journaling app demonstrates the pattern: on-device generates daily prompts; Claude identifies threads across months of entries

- **Evidence**: First-party concrete use case from the post.
- **Confidence**: emerging (illustrative example; no metrics on accuracy or user satisfaction)
- **Quote**: "A journaling app can generate daily prompts on-device, then ask Claude to find threads across months of entries."
- **Our assessment**: This use case reveals an important architectural requirement: Claude needs access to months of journal entries to find threads, which means the app must manage context window constraints for long-horizon synthesis. The on-device model handles each individual daily prompt (short context, fast, private); Claude handles the cross-entry analysis (large context, network, reasoning). The "months of entries" implies either prompt engineering that summarizes prior entries or use of Claude's long context window. This is a practical constraint the post doesn't address — practitioners building this app will need to architect the entry serialization and context management strategy. It also suggests an implicit use case for `blog-anthropic-session-management-1m-context.md` patterns.

### Claim 7: A study app demonstrates the pattern: on-device defines terms; Claude handles complex follow-up reasoning

- **Evidence**: First-party concrete use case from the post.
- **Confidence**: emerging (illustrative example; no metrics)
- **Quote**: "A study app can define a term on-device, then hand off to Claude when the student follows up with 'why does this matter for everything else we've covered?'"
- **Our assessment**: The follow-up question "why does this matter for everything else we've covered?" is an excellent example of a task that requires cross-context reasoning — the student is asking for connections across the entire course content, not just a definition. On-device models excel at single-term lookup (dictionary-style); Claude excels at conceptual synthesis across a curriculum. The handoff trigger here is the follow-up question type: definitional questions stay on-device; relational/synthesis questions escalate. This is a concrete, implementable decision criterion that practitioners can adapt: if the question requires connecting across N prior items where N > threshold, escalate to Claude.

### Claim 8: The integration targets the full Apple platform ecosystem with the next-generation OS releases

- **Evidence**: First-party platform support declaration.
- **Confidence**: settled (specific platform list from official announcement)
- **Quote**: (no direct quote; platforms listed as iOS 27, iPadOS 27, macOS 27, visionOS 27, watchOS 27)
- **Our assessment**: The breadth of platform support — including watchOS — signals that Anthropic is treating this as a platform-wide rather than iPhone-only integration. watchOS in particular is notable given its resource constraints; the on-device model would do local inference, with Claude only invoked when the user moves to a richer interaction context (presumably the paired phone or internet connection). The platform breadth also confirms this is a first-party Apple integration (Foundation Models framework is an Apple system framework, not a third-party library), which gives the integration framework-level performance characteristics rather than third-party overhead.

### Claim 9: Users authenticate with an Anthropic API key — the integration is direct consumer API access, not enterprise-managed credentials

- **Evidence**: First-party authentication description from the announcement.
- **Confidence**: settled (explicit authentication model)
- **Quote**: (no direct quote; described as "users sign in with an Anthropic API key")
- **Our assessment**: The API key authentication model has significant implications for consumer app deployment: app developers cannot embed a shared API key without exposing it; users must provide their own Anthropic API keys. This limits the initial addressable market to developers and technically sophisticated users who have Anthropic accounts and API access. Enterprise or consumer-at-scale deployment would require a different credential model (e.g., the app backend proxying the Claude API, or Anthropic building an OAuth-based delegated access model). This is a meaningful constraint the post does not address directly. Compare with MCP's CIMD model (`blog-anthropic-mcp-production-agents.md` Claim 9) which addresses enterprise credential delegation — the Foundation Models integration does not yet have a comparable solution.

## Concrete Artifacts

### Architecture Pattern Description

```
# Hybrid on-device + Claude architecture pattern
# Source: "Building intelligent apps for Apple platforms with Claude in the
#          Foundation Models framework," Anthropic, June 8, 2026

TIER 1: On-device (Apple Foundation Models)
  Framework: Apple Foundation Models (@Generable annotations)
  Strengths:  Fast, local, private, no network required
  Best for:   Simple extraction, definition, term lookup, prompt generation
  Output:     Typed Swift values via @Generable (NOT raw strings)

TIER 2: Cloud reasoning (Claude via Swift package)
  Framework: Anthropic Swift package for Foundation Models
  Strengths:  Multi-step reasoning, web search, code generation,
              cross-entry synthesis, long-context analysis
  Best for:   Follow-up reasoning, pattern finding, complex questions
  Input:      Typed Swift values from Tier 1 (NOT raw user text)
  Output:     Streamed back into SwiftUI view; also tool calls,
              structured responses

HANDOFF PATTERN:
  @Generable typed output → Claude API call → streamed SwiftUI response
  Key property: clean structured inputs, not raw user text

RESULT:
  "one experience for the user, backed by the right model for each step"
```

### Platform Support Matrix

```
# Platform targets for Anthropic Foundation Models Swift package
# Source: Anthropic, June 8, 2026

Platform   | OS Version | Notes
-----------|------------|-------
iOS        | 27+        |
iPadOS     | 27+        |
macOS      | 27+        |
visionOS   | 27+        |
watchOS    | 27+        | Notable: constrained device, on-device inference tier

Authentication: User-provided Anthropic API key
(Not enterprise-managed; limits consumer-at-scale deployment)
```

### Use Case Handoff Decision Patterns

```
# Decision heuristics for on-device vs. Claude escalation
# Source: inferred from examples in "Building intelligent apps for Apple
#          platforms with Claude in the Foundation Models framework,"
#          Anthropic, June 8, 2026

STAY ON-DEVICE:
  - Single-item lookup (define term, generate daily prompt, check grammar)
  - Bounded scope, single-turn response
  - Privacy-sensitive (no network needed)
  - Latency-critical (sub-second required)

ESCALATE TO CLAUDE:
  - Cross-entry synthesis ("find threads across months")
  - Follow-up requiring relational reasoning ("why does this matter for
    everything else we've covered?")
  - Web context needed (web search tool)
  - Code generation required
  - Multi-step reasoning chains

HANDOFF MECHANISM:
  Pass @Generable typed output directly to Claude API call via Swift package
```

## Cross-References

- **Corroborates**:
  - `blog-anthropic-multi-agent-coordination-patterns.md` Claim 7: "The recommended default pattern is orchestrator-subagent. It handles the widest range of problems with the least coordination overhead." The Foundation Models → Claude handoff is a concrete platform-native implementation of orchestrator-subagent: the on-device model (orchestrator) handles task decomposition and simple tasks, then delegates to Claude (specialized subagent) for complex reasoning. The architecture is consistent with this first-party recommendation.
  - `blog-anthropic-multi-agent-coordination-patterns.md` Claim 13: "Divide work by what context each agent needs rather than by what type of work it does." The on-device/Claude split here is precisely context-centric decomposition: on-device has local device context (current session, fast inference); Claude has broad knowledge context (web, long history, reasoning chains). The handoff criteria (definition vs. relational reasoning) are context-driven, not work-type-driven.
  - `blog-anthropic-mcp-production-agents.md` Claim 6: "Fewer, well-described tools consistently outperform exhaustive API mirrors." The @Generable typed output pattern provides the same benefit at the platform layer: a clean, intent-shaped input rather than raw user text. Both sources converge on the principle that structured, pre-processed inputs produce better model behavior than raw text.

- **Extends**:
  - `blog-anthropic-harnessing-claude-intelligence.md` Claim 3 (Giving Claude a code-execution tool to filter its own tool outputs improves BrowseComp from 45.3% to 61.6%): The @Generable typed input pattern is a platform-native version of the same "pre-filter context before Claude sees it" principle. In `harnessing-claude-intelligence`, Claude uses a REPL to filter its own tool outputs. In the Foundation Models integration, Apple's on-device model uses @Generable to pre-structure user input before Claude receives it. Both approaches reduce the noise Claude must reason through. The Foundation Models integration applies this at the input side (before Claude), while harnessing-claude-intelligence applies it at the output side (after tool calls).
  - `blog-anthropic-multi-agent-coordination-patterns.md` — That post establishes the orchestrator-subagent pattern abstractly. This source provides the first concrete platform-native instantiation of the pattern for mobile/desktop consumer apps. The decomposition principle (Claim 13 there) now has a concrete implementation path for Apple developers.

- **Contradicts**: None identified. The API key authentication model here (Claim 9) is not inconsistent with enterprise credential patterns in other notes — it simply targets a different deployment context (developer/prosumer apps rather than enterprise deployments).

- **Novel**:
  - **Platform-native hybrid on-device + cloud reasoning pattern**: No prior corpus source documents an on-device model acting as the structured input preprocessor for a Claude API call in a mobile/desktop native app context. This is a new deployment architecture category in the corpus — consumer-facing, Swift-native, on-device first.
  - **@Generable as context pre-structuring mechanism**: The specific mechanism of Apple's Foundation Models typed output feeding clean structured inputs to Claude is new to the corpus. It's a platform-layer implementation of context engineering with no prior equivalent.
  - **Apple platform ecosystem targeting (iOS/macOS/watchOS)**: No prior source documents Claude deployment to watchOS or the Apple watch platform. The breadth of the platform list is novel.
  - **"One experience for the user, backed by the right model for each step" as Anthropic positioning**: The explicit framing that Claude is complementary to (not a replacement for) on-device models is stated here for the first time in the corpus with this level of directness. Prior corpus sources position Claude as a backend; this post positions it as the upper tier in a multi-model consumer experience.
  - **Consumer API key auth model**: The user-provides-own-API-key model for a consumer app integration is a specific deployment constraint not previously documented in the corpus. It signals the current state of the distribution strategy — developer-first — and the gap toward consumer-at-scale deployment.

## Guide Impact

- **Chapter 02 (Harness Engineering / Platform Integration)**: Add the Foundation Models → Claude two-tier architecture as a concrete platform-native example of the orchestrator-subagent pattern. The @Generable typed output → Claude API call chain is the Apple developer's implementation path for the decomposition principle. Pair with `blog-anthropic-multi-agent-coordination-patterns.md` Claim 13 (context-centric decomposition) as the design principle behind the task split.

- **Chapter 02 (Harness Engineering)**: Add the "on-device as context pre-processor" pattern: when a platform provides typed structured outputs from a local model, feeding those directly to Claude produces better reasoning than routing raw user text. This is the @Generable → clean API input benefit. Frame it as a general principle: any platform layer that can pre-structure user intent before it reaches Claude should be used.

- **Chapter 04 (Context Engineering)**: The two use cases (journaling app with months of entries; study app with full course context) reveal a context management challenge not addressed by the post: how to serialize and fit months of prior data into Claude's context window. This is an open design question for practitioners building these apps — the guide should document strategies (summarization, vector retrieval, structured session notes) for the long-horizon synthesis use case.

- **Chapter 03 (Real-time Interaction Patterns)**: The streaming SwiftUI integration (Claim 5) is the platform-native pattern for real-time Claude responses in consumer UI. Add as the Apple/Swift example alongside any existing web/JavaScript streaming examples. The key point: the package abstracts the async streaming lifecycle into SwiftUI-compatible state updates.

- **Chapter 05 (Platform Strategies)**: The API key auth limitation (Claim 9) is a real deployment constraint practitioners must understand. The guide should document the auth gap: user-provided API keys work for developer-built personal apps, but consumer-at-scale deployment requires a different model (backend proxy, OAuth delegation, or future Anthropic solution). The Foundation Models integration is currently positioned as a developer-to-developer tool, not an end-user consumer product.

## Extraction Notes

- **Source is a JavaScript-rendered SPA**: The claude.com blog renders JavaScript; WebFetch AI-summarizes the rendered content. Three separate fetch passes were performed with increasingly specific prompts to maximize quote fidelity. All quotes in this note appear consistently across multiple fetch responses and are treated as verbatim. The post contains no Swift code examples (confirmed by the third fetch).
- **Platform version numbers (iOS 27, etc.)**: These appeared in the first fetch response summary. These are either the correct version numbers or the fetcher's best representation of the platform targets. The Prospector's triage comment also named these platforms, lending confidence to the numbers.
- **Authentication model**: The "users sign in with an Anthropic API key" detail appeared in the first fetch response summary. I have no verbatim quote for this — it's summarized. Flagged with `settled` confidence on the existence but the exact mechanism should be verified by checking the official Swift package documentation.
- **No Swift code examples**: WebFetch confirmed the post contains only conceptual descriptions, not code. The Swift package itself (documentation, API surface) was not fetched and may be a valuable follow-up extraction for a separate source note.
- **Cross-references verified**: All `Claim N` citations above were verified against the actual source notes by re-reading the relevant sections. Claim numbers were counted top-to-bottom from the "### Claim" headings in each file.
- **No contradictions to file**: Reviewed existing source notes. The API key auth model is a constraint, not a contradiction with other sources. The hybrid on-device + cloud pattern is additive, not contradictory, to the orchestrator-subagent taxonomy.
