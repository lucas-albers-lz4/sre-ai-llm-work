---
source_url: https://www.promptfoo.dev/blog/building-a-security-scanner-for-llm-apps/
source_type: blog-post
title: "Building a Security Scanner for LLM Apps"
author: "Dane Schneider (Staff Engineer, Promptfoo)"
date_published: 2025-12-16
date_extracted: 2026-07-18
last_checked: 2026-07-18
status: current
confidence_overall: emerging
issue: "#292"
---

# Building a Security Scanner for LLM Apps

> A vendor (Promptfoo) blog post introducing a GitHub Action–based code scanner
> for LLM-specific vulnerabilities. The key technical contribution is a
> call-graph / IO-flow tracing methodology for detecting prompt-injection paths
> in code, supported by three real CVE case studies and a "custom guidance"
> mechanism for managing alert-fatigue tradeoffs. The "deadly duo" refinement
> of Simon Willison's lethal trifecta is the main conceptual framing.

## Source Context

- **Type**: blog-post (vendor product announcement with technical content)
- **Author credibility**: Dane Schneider is a Staff Engineer at Promptfoo
  (the site banner notes Promptfoo is now part of OpenAI). The article is a
  product announcement for Promptfoo's commercial code scanner, not independent
  research. The CVE case studies are real, publicly documented vulnerabilities
  (CVE-2024-5565, CVE-2024-7042, CVE-2024-23751) and the article's analysis
  of them is technically sound. The methodological claims (call-graph tracing,
  far-tracing requirement) are the author's own engineering argument for why
  their approach is justified. The "lethal trifecta" and "deadly duo" framing
  is attributed to Simon Willison's existing work. The custom guidance pattern
  and the focus-matters thesis are Promptfoo-specific but describe a generalizable
  design tradeoff. Overall, treat the CVE analysis as high-credibility and the
  methodology/product claims as vendor-positioned (plausible but not independently
  validated).
- **Scope**: Covers the methodological argument for why LLM apps need a
  specialized code scanner (call-graph tracing, far-tracing, laundering concept),
  the "deadly duo" threat model, three CVE worked examples, the custom guidance
  mechanism, and product positioning (GitHub Action). Does NOT cover: runtime
  red-teaming (covered by `blog-promptfoo-ai-orchestrated-cyberattacks.md`),
  evaluation metrics (`blog-promptfoo-asr-not-portable-metric.md`), or regulatory
  compliance (`blog-promptfoo-ai-regulation-2025.md`). It is a vendor product
  announcement first and a methodology piece second.

## Extracted Claims

### Claim 1: A purpose-built code scanner focused specifically on LLM/agent vulnerabilities finds issues that general code-reviewers (human or automated) miss
- **Evidence**: The article states that during Promptfoo's internal use, the
  scanner flagged issues that "other automatic code review tools" missed, and
  in "several cases" it was the only reviewer to catch the problem. This is
  attributed to focus: the scanner has one job and is designed for a small set
  of specific patterns.
- **Confidence**: anecdotal
- **Quote**: "it was the only reviewer, human or bot, which flagged that particular issue."
- **Our assessment**: The claim is self-reported by the vendor with no
  independent validation. The mechanism is plausible (specialization improves
  detection for domain-specific patterns), but the "only reviewer" framing
  lacks quantitative context (total PRs reviewed, false-positive rate, etc.).
  Use as a supporting argument for dedicated LLM-security tooling, not as
  standalone evidence.

### Claim 2: The LLM "launders" untrusted input, making prompt injection fundamentally different from traditional injection — you cannot sanitize an output that IS the privileged action
- **Evidence**: The article explains the traditional injection pattern (untrusted
  input → privileged action) and contrasts it with the LLM case where an
  additional step (the LLM) sits between input and action. The LLM transforms
  the input into output that "looks and feels safe" but still encodes the attack.
  Unlike traditional SQL/XSS injection where sanitization is possible, LLM
  outputs that ARE database queries or shell commands cannot be sanitized because
  the "entire thing is untrusted."
- **Confidence**: emerging
- **Quote**: "the LLM 'launders' the untrusted input into an output that looks and feels safe, but really isn't."
- **Our assessment**: This is a well-framed articulation of the fundamental
  difference between traditional injection and prompt injection. The "laundering"
  metaphor is useful for the guide. The claim is technically sound: if an LLM
  output IS a shell command, trying to "sanitize" it means deciding which parts
  of a command are safe — which is effectively the same problem as detecting
  injection in the first place. High value for the guide's security chapters.

### Claim 3: Most serious LLM app vulnerabilities relevant to code scanning reduce to prompt injection, with jailbreak risk as a secondary area — not the full OWASP Top 10
- **Evidence**: The article narrows from the OWASP Top 10 for LLM Applications
  to two categories relevant to code scanning: prompt injection (described as
  "The big kahuna") and jailbreak risk. Other OWASP categories are framed as
  vectors for prompt injection (data poisoning, embedding weaknesses, improper
  output handling, excessive agency), out of scope for code scanning (supply
  chain, model poisoning, misinformation), or difficult to judge from code alone
  (unbounded consumption). Sensitive information disclosure is "most concerning
  when it coincides with prompt injection or jailbreak risk."
- **Confidence**: emerging
- **Quote**: "Nearly everything that can go terribly wrong in an LLM app from a security perspective is upstream of it, downstream of it, or somehow connected."
- **Our assessment**: This is a prioritization claim, not an empirical finding.
  It is useful as a threat-modeling heuristic for code-level review (where to
  invest scanning effort), but it reflects the scanner's design scope rather
  than an objective ranking of vulnerability prevalence. The "big kahuna"
  framing is worth capturing as a memorable label.

### Claim 4: The "deadly duo" — exposure to untrusted content + privileged actions — creates a vulnerability even without private data access, extending Simon Willison's lethal trifecta
- **Evidence**: The article summarizes Willison's lethal trifecta (access to
  private data, exposure to untrusted content, ability to externally communicate)
  and then argues that only two of the three are needed: "Exposure to untrusted
  content + privileged actions is enough to create a vulnerability even without
  access to private data." The article also notes Willison's own expansion that
  the trifecta covers only data exfiltration, and there are "plenty of other,
  even nastier risks" from agent tools — destructive SQL, system compromises,
  and emptying crypto wallets — which the deadly duo captures.
- **Confidence**: emerging
- **Quote**: "Exposure to untrusted content + privileged actions is enough to create a vulnerability even without access to private data."
- **Our assessment**: This is a useful refinement of Willison's frame. The
  original trifecta focused on data exfiltration (data access + untrusted content
  + external communication); the deadly duo captures destructive actions where
  no data access is needed. The article adds "privileged actions" as a category
  broader than just "external communication" — this includes database queries,
  shell commands, and API calls. This is not novel per se (Willison's own
  follow-up post makes a similar point) but it is clearly stated and citable.

### Claim 5: General security scanners cannot effectively detect LLM injection paths because they rely on a sanitization shortcut that does not apply when the output itself IS the dangerous action
- **Evidence**: General scanners can flag any string passed unsanitized to a
  privileged action (database query, shell command) — they take the shortcut of
  not needing to trace the input's origin because best practice is to sanitize
  every input regardless. For LLM apps, this shortcut breaks down: LLM output
  used directly as a query or command cannot be sanitized, so flagging every
  such instance would produce unhelpful alerts.
- **Confidence**: emerging
- **Quote**: "If we flagged every instance of an LLM output being used for a privileged action without sanitization, we'd drown developers in unhelpful alerts."
- **Our assessment**: This is a key methodological insight for the guide. It
  explains why existing SAST/DAST tooling is insufficient for LLM apps and
  motivates the need for a different approach (far tracing, Claim 6). The
  argument is technically sound and generalizable beyond Promptfoo's product.

### Claim 6: Far tracing — exhaustively tracing where inputs to LLM calls come from and how outputs are used, combined with agent capability modeling — is the method for detecting prompt injection in code
- **Evidence**: The article describes the approach: tracing inputs and outputs
  "across many files, function calls, and prompts," then combining the IO-flow
  knowledge with the LLM/agent's capabilities (tools and permissions) to
  determine whether a lethal trifecta or deadly duo exists. The article contrasts
  this with general scanners that "can take a shortcut" by flagging any
  unsanitized string — LLM scanners cannot use that shortcut.
- **Confidence**: emerging
- **Quote**: "tracing where inputs to LLM calls come from and how outputs from LLM calls are used, often across many files, function calls, and prompts"
- **Our assessment**: The far-tracing methodology is the article's core
  technical contribution. The claim that this is computationally expensive
  ("incredibly slow and expensive, particularly if it used AI") is a frank
  acknowledgement that the approach has cost implications. The insight that
  general scanners cannot use their standard shortcut for LLM apps is sound.
  The capability-modeling dimension (what tools/permissions does the agent
  have?) connects code scanning to agent autonomy decisions, which makes this
  relevant to guide chapters beyond just security tooling.

### Claim 7: Vanna.AI CVE-2024-5565 demonstrates the "laundered injection" pattern: LLM-generated Plotly code passes through `exec()` without validation
- **Evidence**: Actual CVE with code snippet. Vanna.AI generates visualization
  code from natural language via an LLM, then runs it through `exec()`. The
  scanner flagged it with the assessment "This is classic prompt injection:
  user input flows into an LLM, the LLM output is executed, and the result is
  used in a dangerous way."
- **Confidence**: settled
- **Quote**: "This is classic prompt injection: user input flows into an LLM, the LLM output is executed, and the result is used in a dangerous way (in this case, by executing arbitrary code)."
- **Our assessment**: Real, well-documented CVE. The `exec()` pattern is the
  clearest example of the laundering concept from Claim 2 — the LLM output
  looks like safe Plotly code but is arbitrary Python. Useful as the canonical
  "don't exec LLM output" worked example for the guide.

### Claim 8: LangChain.js CVE-2024-7042 demonstrates LLM-generated database query injection — GraphCypherQAChain executes LLM-generated Neo4j Cypher queries without validation
- **Evidence**: CVE with code showing `this.graph.query(extractedCypher)` where
  `extractedCypher` was generated by an LLM call. The article notes this
  vulnerability existed in both the Python and JavaScript versions of LangChain,
  calling it "a common pitfall in text-to-query tools."
- **Confidence**: settled
- **Quote**: "const context = await this.graph.query(extractedCypher); // Executed directly"
- **Our assessment**: Real CVE, well-documented. The text-to-query pattern
  (natural language → LLM → database query) is increasingly common (Text-to-SQL,
  Text-to-Cypher, Text-to-API). The fact that both Python and JS versions were
  affected suggests this is a design-level vulnerability, not a language-specific
  bug. Useful worked example for the guide's chapter on agent tool design.

### Claim 9: LlamaIndex CVE-2024-23751 (Text-to-SQL without validation) is a borderline case where default-scanning would produce too much noise — the custom guidance mechanism resolves this
- **Evidence**: The article describes how the scanner analyzed this CVE and
  **filtered it out** by default because Text-to-SQL is a common pattern and
  teams "might want" the LLM to execute `DROP TABLE` queries depending on their
  security model. Adding a "defense-in-depth" custom guidance directive made the
  scanner flag the vulnerability instead. The reasoning: flagging at the library
  level "would be overzealous" — the scanner should only flag issues that are
  "directly exploitable."
- **Confidence**: emerging
- **Quote**: "alert fatigue makes developers ignore legitimate findings, or just turn off scanning altogether in frustration."
- **Our assessment**: This is the most valuable CVE in the source for the guide
  because it illustrates the fundamental tradeoff between scanner strictness and
  alert fatigue, and presents a concrete resolution mechanism (custom guidance).
  The CVE itself is real (CVE-2024-23751); the claim about scanner behavior is
  vendor-specific but the design pattern (config-level guidance that shifts
  detection rules) is generalizable.

### Claim 10: Custom guidance — defense-in-depth directives in the scanner's config — provides a mechanism to tune scanner strictness without changing code, balancing comprehensiveness vs. alert fatigue
- **Evidence**: The article demonstrates a concrete YAML guidance directive.
  With default settings, the scanner emits an "all clear" for the LlamaIndex
  Text-to-SQL pattern. With the following guidance added, it flags it:
  ```
  guidance: |
    We follow defense-in-depth principles. Do not assume that downstream
    systems (databases, APIs, external services) have proper access controls.
    Flag cases where untrusted or LLM-generated content is passed to
    privileged operations without validation at the application layer.
  ```
- **Confidence**: anecdotal
- **Quote**: "guidance: |\n  We follow defense-in-depth principles. Do not assume that downstream\n  systems (databases, APIs, external services) have proper access controls.\n  Flag cases where untrusted or LLM-generated content is passed to\n  privileged operations without validation at the application layer."
- **Our assessment**: This is the most novel pattern in the source — a
  config-level mechanism for encoding organizational security posture that
  changes scanner behavior. Directly relevant to the guide's chapter on
  security tooling design. The pattern generalizes beyond Promptfoo: any
  AI-security scanner that must operate across teams with different risk
  tolerances needs a mechanism like this. The concrete YAML makes it citable
  and reusable.

## Concrete Artifacts

### Code snippet: Vanna.AI CVE-2024-5565 (Python)

```python
def get_plotly_figure(plotly_code: str, df: pd.DataFrame):
    ldict = {'df': df, 'px': px, 'go': go}
    exec(plotly_code, globals(), ldict)  # LLM-generated code executed here
```
Source: promptfoo blog, "Testing on Real CVEs → Vanna.AI" section. CVE-2024-5565.

### Code snippet: LangChain.js CVE-2024-7042 (JavaScript)

```javascript
const generatedCypher = await this.cypherGenerationChain.call({
  question,
  schema: this.graph.getSchema(),
});
// ...
const context = await this.graph.query(extractedCypher); // Executed directly
```
Source: promptfoo blog, "LangChain.js: LLM Output to Database Queries" section. CVE-2024-7042.

### Code snippet: LlamaIndex CVE-2024-23751 (Python)

```python
raw_response_str, metadata = self._sql_database.run_sql(query_bundle.query_str)
```
Source: promptfoo blog, "LlamaIndex: Text-to-SQL Without Validation" section. CVE-2024-23751.

### Custom guidance config example (YAML)

```
guidance: |
  We follow defense-in-depth principles. Do not assume that downstream
  systems (databases, APIs, external services) have proper access controls.
  Flag cases where untrusted or LLM-generated content is passed to
  privileged operations without validation at the application layer.
```
Source: promptfoo blog, "Custom guidance" section. The guidance changes scanner
behavior from "all clear" (default) to flagging the LlamaIndex pattern.

### The "Deadly Duo" vs "Lethal Trifecta" comparison (from the article's framing)

```
Lethal Trifecta (Willison):
  1. Access to your private data
  2. Exposure to untrusted content
  3. Ability to externally communicate
  → Data exfiltration risk

Deadly Duo (this article):
  1. Exposure to untrusted content
  + 2. Privileged actions (destructive SQL, shell commands, API calls)
  → System-compromise / destruction risk without needing private data
```
Source: promptfoo blog, "The Lethal Trifecta (and Deadly Duo)" section.

## Cross-References

- **Corroborates**:
  - `blog-promptfoo-ai-orchestrated-cyberattacks.md` — covers prompt injection
    as an offensive threat vector and provides red-team configs for testing AI
    systems. This note covers *code-level detection* of the same injection paths.
    Together they argue that prompt injection must be addressed both at runtime
    (red-teaming) and at build time (code scanning). No contradiction — they
    are complementary layers of defense.
  - `blog-pagerduty-production-ai-agent-gaps.md` — Claim 5 (prompt injection
    susceptibility 80-90%) and Claim 14 (defense-in-depth guardrails) establish
    the scope and severity of the prompt-injection problem. This note's Claim 6
    (far tracing methodology) describes a code-level detection approach for
    finding injection paths that the PagerDuty guardrails would need to block.
    Complementary — risk magnitude (PagerDuty) + detection method (this note).
  - `docs-google-sre-prodcast-05-06-ai-safety.md` — Claim 1 (safety is "squishy
    and a continuum") and Claim 3 (the "changing the wheel while the bus is
    running" fix loop) describe the operational reality of AI safety. This
    note's claim that scanners must trace far rather than rely on sanitization
    (Claim 5-6) is a methodological consequence of that squishiness. Both
    sources argue that traditional deterministic security approaches are
    inadequate for LLM systems.

- **Contradicts**: None identified. All claims in this source are either
  vendor-specific product descriptions, real CVE analyses, or refinements of
  existing conceptual frames (deadly duo extending lethal trifecta). No claim
  here opposes an existing note's claim in a way that would change guide advice.
  No contradiction issue is required (CONTRADICTIONS.md has no entries and there
  are no open `contradiction`-labeled issues).

- **Extends**:
  - Extends `blog-promptfoo-ai-orchestrated-cyberattacks.md` and `blog-pagerduty-production-ai-agent-gaps.md` by adding a *code-scanning methodology* layer to
    the prompt-injection defense stack. Both existing notes cover runtime testing
    (red-teaming, guardrails); this note covers build-time static analysis of
    injection paths in source code. Together they describe a defense-in-depth
    strategy spanning build time and runtime.
  - Extends the "lethal trifecta" concept (Simon Willison, cited in the article)
    with the "deadly duo" refinement that captures destructive-action risks
    beyond data exfiltration. This is a useful conceptual extension for the
    guide's threat-modeling section.

- **Novel**:
  - The far-tracing / call-graph methodology for LLM-specific code scanning
    (Claim 6) — no existing note describes a static-analysis approach for
    detecting prompt-injection paths in code.
  - The "laundering" framing (Claim 2) as a concrete explanation for why
    prompt injection resists traditional sanitization approaches — more specific
    than general "prompt injection is hard" statements elsewhere in the corpus.
  - The three CVE case studies as worked examples of LLM-injection patterns
    in real, deployed libraries — `exec()`, database-query injection, and
    Text-to-SQL. These are specific, citable, real-world failures.
  - The custom guidance mechanism (Claim 10) as a design pattern for balancing
    scanner strictness vs. alert fatigue — not present in any existing note.
  - The "deadly duo" as a named, scoped threat model (Claim 4) that separates
    destructive-action risk from data-exfiltration risk — refines the broader
    "lethal trifecta" framing used elsewhere in the corpus.

## Guide Impact

- **Chapter 06 (Security and Trust)**: This is the primary destination. Add:
  - A "why general SAST doesn't work for LLM apps" subsection citing Claim 5
    (sanitization shortcut doesn't apply) and Claim 2 (laundering mechanism)
    to explain why teams need LLM-specific code scanning, not just their
    existing security tooling.
  - The "deadly duo" threat model (Claim 4) as a complement to the lethal
    trifecta — explicitly scoping destructive-action risk (destructive SQL,
    shell commands, API misuse) alongside data-exfiltration risk.
  - The three CVE case studies (Claims 7-9, Concrete Artifacts) as worked
    examples of LLM-injection patterns the guide should reference. The
    Vanna.AI `exec()` case is the canonical "never exec LLM output" example;
    the LangChain.js Cypher-injection case illustrates text-to-query risks;
    the LlamaIndex Text-to-SQL case illustrates the alert-fatigue tradeoff.
  - The custom guidance pattern (Claim 10) as a design recommendation for
    security tooling — configurable strictness that encodes organizational
    security posture without code changes.

- **Chapter 04 (Observability & Incident Response)**: The far-tracing
  methodology (Claim 6) is relevant for incident-response investigations:
  tracing the IO flow from untrusted input through the LLM to a privileged
  action is the same investigative pattern a responder would follow when
  analyzing a prompt-injection incident. Recommend adding a note that code
  scanning traces (Claim 6 mapping) can seed incident-response playbooks.

- **Chapter 03 (Runbooks and Agents)**: The "far tracing" methodology (Claim 6)
  requires knowing an agent's tools and permissions — this connects code
  scanning to agent capability documentation. Recommend that agent runbooks
  and capability inventories be structured in a way that a scanner (or a
  responder) can trace the IO flow and determine whether a deadly duo exists.

## Extraction Notes

- Source is a single blog post (published 2025-12-16 by Dane Schneider, Staff
  Engineer at Promptfoo). Read in full via fetched HTML; all quotes in this
  note were checked against the source page character-for-character before
  writing.
- The article is a vendor product announcement (Promptfoo's commercial code
  scanner) with significant technical substance in the methodology section and
  CVE case studies. I extracted the generalizable security patterns (laundering,
  deadly duo, far tracing, custom guidance) separately from the product-specific
  framing (GitHub Action, PR comments, etc.). The "Focus Matters" and product
  description sections are mostly positioning.
- The article's framing of the "lethal trifecta" and "deadly duo" is attributed
  to Simon Willison's existing work. I extracted the deadly duo as the article's
  refinement rather than re-extracting the lethal trifecta as novel.
- No sub-pages were followed — the article is self-contained and links only to
  generic Promptfoo product pages (GitHub app install, docs). No part of the
  source was paywalled; publicly accessible.
- The three CVEs are real (CVE-2024-5565, CVE-2024-7042, CVE-2024-23751) and
  can be independently verified via the CVE database and linked PRs/commits.
  The scanner-behavior claims around these CVEs (that the scanner flagged or
  didn't flag them) are vendor-specific and unverifiable without access to the
  scanner.
- The site banner notes "Promptfoo is now part of OpenAI" — this is post-
  acquisition content (OpenAI acquired Promptfoo in 2025/2026). The article
  does not reference the acquisition in its body.
