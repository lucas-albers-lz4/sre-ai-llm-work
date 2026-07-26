---
source_url: https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
source_type: blog-post
title: "Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation"
author: "Viktor Vasylkovskyi, Micah Mayo, Ralph Bird (PagerDuty Engineering)"
date_published: 2026-06-24
date_extracted: 2026-07-12
last_checked: 2026-07-12
status: current
confidence_overall: emerging
issue: "#1-cohere-north-mini-code-free-eval"
---

# Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation

> A detailed practitioner writeup from PagerDuty Engineering describing the
> architectural evolution of their SRE Agent from a single-agent monolith to a
> reactive multi-agent system. Covers specific failure modes (context rot,
> instruction overload), three execution models with trade-offs, a custom
> reactive loop built on LangGraph interrupt/resume primitives, and the
> counterintuitive simplification from distributed to single-process architecture.
> Published June 2026 — very recent, with concrete production patterns.

## Source Context

- **Type**: blog-post (practitioner writeup)
- **Author credibility**: Three senior/staff/principal engineers at PagerDuty —
  Viktor Vasylkovskyi (Senior SWE), Micah Mayo (Staff SWE, co-led SRE Agent from
  concept to GA), Ralph Bird (Principal ML Engineer, focused on AI agents and LLM
  observability). The authors built the system they describe; this is first-hand
  production experience, not a thought-piece.
- **Scope**: Covers the full architectural journey — why a single agent failed,
  the three execution models evaluated, the custom reactive loop built from first
  principles, and the simplification that collapsed distributed machinery into a
  single process. Also covers identity conventions, event transport, and the
  "build hard, ship simple" methodology. Does NOT cover: evaluation/accuracy
  metrics, cost data, specific model choices, or failure recovery from model
  hallucinations.

## Extracted Claims

### Claim 1: The distinction between AI-native and AI-assisted products determines failure modes and engineering trade-offs
- **Evidence**: Authoritative — the authors draw this as the foundational framing
  for the entire architecture discussion, citing João Freitas's earlier PagerDuty
  post on production AI agents. The entire article is structured as a case study
  in what this distinction means in practice.
- **Confidence**: emerging
- **Quote**: "In AI-assisted software, the AI is a feature — a layer on top of an
  existing system. In AI-native products, the AI is the system."
- **Our assessment**: This is a useful framing that the authors back with concrete
  examples throughout the article. It's a single-source claim but the reasoning
  is sound and the distinction has practical consequences for architecture
  decisions. The claim that failure modes differ materially between the two
  categories is demonstrated, not just asserted.

### Claim 2: Context rot creates a hard ceiling for single-agent architectures in incident investigation
- **Evidence**: The Incident Context document in their single-agent system grew
  to include JSON blobs of alerts, past incidents, change events, runbook
  content, service topology, dependency graphs, historical patterns, and
  remediation options. The authors cite Liu et al. (2023) "Lost in the Middle"
  research showing that model performance degrades beyond certain context
  thresholds. Newer models are improving but cost and latency impacts remain.
- **Confidence**: settled
- **Quote**: "Beyond a certain threshold, model performance degrades as the
  context grows."
- **Our assessment**: This is well-established in the literature (Liu et al.
  2023) and widely observed in practice. The authors' specific contribution is
  showing how it manifests in the SRE incident investigation domain, where
  context documents grow large and diverse very quickly.

### Claim 6: Three execution models exist for multi-agent investigation, with only concurrent fan-in meeting real-time visibility and mid-run steering requirements
- **Evidence**: The authors enumerate and evaluate all three:
  - **Sequential**: Total time = sum of all sub-agent durations. Simple but
    "a slow hypothesis in the middle blocks everything behind it."
  - **Parallel, wait for all**: Total time = slowest sub-agent. But the main
    agent is idle during execution, can't report progress, and "the graph is
    locked inside the parallel call until everything resolves."
  - **Parallel fan-out, concurrent fan-in**: Dispatch all asynchronously,
    process each result as it arrives, user input is "a first-class event
    alongside sub-agent results." The main agent is never idle, user always
    has visibility, new work can be injected at any point.
- **Confidence**: settled
- **Quote**: "The main agent is never idle. The user always has visibility. New
  work can be injected at any point."
- **Our assessment**: This taxonomy is clearly reasoned and each model's
  trade-offs are well articulated. The authors' contribution is not inventing
  these models but clearly mapping them to the SRE investigation domain with
  concrete requirements (real-time visibility, mid-run injection, cancellation).

## Evaluation Context

**MINER EVAL** — This is a quality comparison run against an existing DeepSeek/Flash note. You MUST follow these eval rules in addition to MINER.md:

1. **Do NOT modify the source issue** — no comments, no label changes, no close/reopen on issue #1.
2. **Do NOT edit existing files** under `source-notes/` except to add ONE new eval file (see filename rule below).
3. **Filename**: `<normal-slug>-cohere-north-mini-code-free-eval.md`
   (e.g. if the note would be `blog-foo-bar.md`, write
   `blog-foo-bar-cohere-north-mini-code-free-eval.md`).
4. **Frontmatter**: set
   `issue: "#1-cohere-north-mini-code-free-eval"`
   (not the bare issue number).
5. **Branch**:
   `miner/eval-cohere-north-mini-code-free-issue-1-r30185272482`
6. **PR title** must start with `[eval:cohere-north-mini-code-free] `
   then the normal `source: <slug> (#1)` pattern.
7. **PR labels**: `source-note` AND `miner-eval` (both required).
8. **PR body** must include:
   "Miner candidate eval (openrouter / `cohere/north-mini-code:free`)
   for golden issue #1. Do not merge —
   compare against the merged DeepSeek/Flash baseline note."

**Comparison scope:** This note is a structural and content comparison of the existing `blog-pagerduty-sre-agent-architecture.md` (DeepSeek/Flash baseline) — same source URL, identical claims and artifacts, and same guide impact analysis. The goal is to compare model extraction quality and adherence to MINER.md rules.