---
source_url: https://www.promptfoo.dev/blog/owasp-red-teaming/
source_type: blog-post
title: "OWASP Red Teaming: A Practical Guide to Getting Started"
author: "Vanessa Sauter (Principal Solutions Architect, Promptfoo)"
date_published: 2025-03-25
date_extracted: 2026-07-26
last_checked: 2026-07-26
status: current
confidence_overall: emerging
issue: "#555"
---

# OWASP Red Teaming: A Practical Guide to Getting Started

> A Promptfoo blog post (March 2025) providing a practitioner-oriented summary of the OWASP GenAI Red Teaming Guide (January 2025). The article introduces the OWASP framework's structured red-teaming methodology — "step zero" objective definition, five threat category taxonomy, SDLC timing framework, RAG triad testing, agent-specific risk patterns, and guardrail-bypass iteration — with Promptfoo YAML config examples for each practice. Its value to the corpus is as a secondary reference for the OWASP framework's structured security-testing methodology, not as primary research.

## Source Context

- **Type**: blog-post (vendor educational content, Promptfoo, now part of OpenAI)
- **Author credibility**: Vanessa Sauter is a Principal Solutions Architect at Promptfoo. The article is a summary/educational overview of the OWASP GenAI Red Teaming Guide (published January 2025, the first official OWASP guide for AI red teaming). Most substantive claims (threat categories, RAG triad, SDLC timing, agent risks) are attributed to the OWASP guide rather than being original to this post. The Promptfoo YAML config examples (OWASP plugin shortcuts, custom policies, custom graders, foundation-model red teaming) are authoritative for how Promptfoo's tool works but vendor-specific. Overall, treat the OWASP framework references as settled methodology and the Promptfoo config patterns as vendor-specific implementations of that methodology.
- **Scope**: Covers (1) the "step zero" objective-definition framework, (2) five OWASP threat categories for LLMs, (3) SDLC integration timing (pre/post-deployment, four-phase model), (4) Promptfoo OWASP red teaming plugins and config patterns, (5) RAG triad testing (factuality, relevance, groundedness), (6) agent-specific risk patterns, (7) guardrail + red team iterative cycle, (8) prioritization framework, (9) custom policy/grader configs. Does NOT cover: in-depth analysis of any single OWASP category, empirical metrics or measurement data, comparison of different red-teaming tools, or failure reports from real red-teaming engagements. It is an introductory overview, not a deep technical reference.

## Extracted Claims

### Claim 1: The OWASP GenAI Red Teaming Guide establishes a "step zero" principle — red teaming must start with defined objectives and success criteria before any testing begins

- **Evidence**: The article opens the methodology section by stating that generative AI "can produce outputs that harm or deceive users, damage the company's reputation, lead to a data breach, or all of the above" and that "any generative AI red teaming strategy needs to start at a carefully planned, well-thought-out step zero." A three-layer pyramid structures this: bottom layer = AI Code of Conduct (brand values, legal requirements, ethical guidelines); middle layer = Specific Goals (technical, operational, compliance); top layer = Success Metrics (KPIs, benchmarks).
- **Confidence**: settled
- **Quote**: "any generative AI red teaming strategy needs to start at a carefully planned, well-thought-out step zero."
- **Our assessment**: This "step zero" framing is attributed to the OWASP GenAI Red Teaming Guide. It is a useful structured methodology for the guide's security chapter — many teams jump directly to running probes without first defining what success looks like or what risks are in-scope. The three-layer pyramid (principles → goals → metrics) provides a concrete framework. However, the article provides only a diagram description, not a worked example of applying the framework.

### Claim 2: The OWASP guide defines five primary threat categories for LLM-based applications — adversarial attacks, alignment risks, data risks, interaction risks, and knowledge risks

- **Evidence**: The article enumerates the five categories: "Adversarial attacks — prompt injection from malicious actors, Alignment risks — outputs not aligning with organizational values, Data risks — leakage of sensitive or training data, Interaction risks — users accidentally generating harmful outputs, Knowledge risks — misinformation and disinformation."
- **Confidence**: settled
- **Quote**: "Adversarial attacks — prompt injection from malicious actors, Alignment risks — outputs not aligning with organizational values, Data risks — leakage of sensitive or training data, Interaction risks — users accidentally generating harmful outputs, Knowledge risks — misinformation and disinformation."
- **Our assessment**: This five-category taxonomy is directly from the OWASP GenAI Red Teaming Guide. It is a useful structured threat categorization for the guide's security chapter. The categories are broad enough to cover the major risk surfaces but specific enough to be actionable. The taxonomy differs from the OWASP Top 10 for LLM Applications (which lists ten technical vulnerability categories) — this is a risk-oriented categorization rather than a vulnerability list. No existing source note in the corpus presents this five-category OWASP threat taxonomy.

### Claim 3: Red teaming should be integrated throughout the SDLC across four sequential phases — model evaluation, implementation testing, system testing, and runtime monitoring

- **Evidence**: The article describes a four-phase diagram (Model → Implementation → System → Runtime) and states: "Securing an LLM-based application is never a one-and-done problem." Pre-deployment testing (model alignment, guardrails, RAG security, control testing) aligns with "shift left" philosophy; post-deployment testing (human interaction, agent behavior, business impact) uses black-box approaches.
- **Confidence**: emerging
- **Quote**: "Securing an LLM-based application is never a one-and-done problem."
- **Our assessment**: The four-phase SDLC framework and the pre-/post-deployment distinction are standard security-engineering practices applied to LLM applications, not novel to this source. The article's value is in mapping these to a named OWASP framework. The "shift left" recommendation is consistent with existing source notes (`blog-promptfoo-building-security-scanner-llm-apps.md` advocates build-time scanning). No metrics are provided to validate the framework's effectiveness.

### Claim 4: Pre-deployment red teaming must be integrated into CI/CD pipelines and run on a recurring schedule because LLM application changes have nondeterministic consequences

- **Evidence**: The article recommends running red teams "on prompt file changes, or at repeated intervals (12h/24h/weekly)" and warns: "Given the nondeterministic nature of generative AI, any changes you make to the LLM application could have unexpected consequences."
- **Confidence**: emerging
- **Quote**: "Given the nondeterministic nature of generative AI, any changes you make to the LLM application could have unexpected consequences."
- **Our assessment**: The justification (nondeterministic output means changes have unpredictable security effects) is consistent with the "model upgrade as security change" principle documented in `blog-promptfoo-model-upgrades-break-agent-safety.md` (Claim 1: GPT-4o → GPT-4.1 caused a 23pp injection-resistance drop). The CI/CD integration and scheduled-interval recommendations are standard security practice applied to LLM ops. The 12h/24h/weekly cadence suggestion is arbitrary — no evidence is given for why these intervals are appropriate vs. event-triggered runs.

### Claim 5: Post-deployment black-box testing should enumerate all exposed application information — models, system prompts, guardrails, frameworks — because any public information is an attack surface

- **Evidence**: The article recommends black-box testing — "test an application without prior knowledge of its internal workings" — and advises enumerating models, extracting system prompts, determining guardrails, and enumerating frameworks. It warns: "whatever information is exposed to users or the public can be exploited by attackers." A tool-discovery plugin is mentioned for agent testing.
- **Confidence**: emerging
- **Quote**: "whatever information is exposed to users or the public can be exploited by attackers."
- **Our assessment**: This is standard black-box security testing methodology applied to LLM apps. The enumeration recommendations (model identification, system prompt extraction, guardrail detection) are specific enough to be actionable. The tool-discovery plugin reference is a Promptfoo-specific feature but the general approach (enumerate the attack surface before testing) is universally applicable. No comparison is given between black-box and white-box testing effectiveness for LLM applications.

### Claim 6: The OWASP Top 10 for LLM Applications can be used as a red-teaming shortcut — Promptfoo's `owasp:llm` plugin tests all ten categories with a single configuration line

- **Evidence**: The article lists the OWASP Top 10 for LLM Applications (Prompt Injection, Sensitive Information Disclosure, Supply Chain, Data and Model Poisoning, Improper Output Handling, Excessive Agency, System Prompt Leakage, Vector and Embedding Weaknesses, Misinformation, Unbounded Consumption) and shows the Promptfoo YAML config: `redteam:\n  plugins:\n    - owasp:llm`.
- **Confidence**: settled
- **Quote**: "redteam:\n  plugins:\n    - owasp:llm"
- **Our assessment**: The `owasp:llm` shorthand is a Promptfoo product feature that maps to a test battery for the ten OWASP categories. The OWASP Top 10 for LLM Applications is a well-established reference framework. The single-line config is a convenience feature, not a methodology claim. Two existing source notes also reference the OWASP Top 10 — `blog-promptfoo-building-security-scanner-llm-apps.md` (Claim 3: narrows from the full OWASP Top 10 to two categories relevant for code scanning) and `blog-promptfoo-jailbreaking-vs-prompt-injection.md` (Claim 2: OWASP groups jailbreaking under LLM01: Prompt Injection) — but none of them present it as a configurable red-teaming test battery. This source provides the config-actionable shortcut rather than a taxonomic reference.

### Claim 7: RAG applications require evaluation across three dimensions — factuality, relevance, and groundedness — forming the "RAG Triad"

- **Evidence**: The article describes a diagram with three overlapping circles labeled Factuality, Relevance, and Groundedness. Three key questions are asked: "Is the retrieved context relevant to the user's query? Is the response supported by the context? Is the answer relevant to the question?" Promptfoo supports RAG evaluation through its evaluation framework, the `rag-poisoning` data poisoning plugin, and hallucination detection.
- **Confidence**: settled
- **Quote**: "Is the retrieved context relevant to the user's query? Is the response supported by the context? Is the answer relevant to the question?"
- **Our assessment**: The RAG Triad is a well-established evaluation framework (originally popularized by TruLens/NeMo Guardrails) — this article does not originate it. The article provides it as a high-level summary without metrics or concrete evaluation methodology. The Promptfoo config patterns for RAG testing (`rag-poisoning` plugin, hallucination detection) are vendor-specific. The framework is still useful for the guide's security chapter as a reference: when red teaming RAG applications, these three dimensions define the evaluation scope.

### Claim 8: The OWASP guide identifies five specific risk categories for agents and multi-agent systems — multi-turn attack chains, decision-making manipulation, tool-integration exploitation, cross-chain data poisoning, and permission bypass

- **Evidence**: The article enumerates: "Multi-turn attack chains within the same AI model, Manipulation of agent decision-making processes, Exploitation of tool integration points, Data poisoning across model chains, Permission and access control bypass through agent interactions." An info callout adds: "When red teaming autonomous agents, consider the technical and organizational controls that would be in place to mitigate the risks for employees, such as the principles of least privilege and separation of duties." Denial of Wallet (DoW) attacks are noted as a concern for reasoning-engine-based agents.
- **Confidence**: emerging
- **Quote**: "Multi-turn attack chains within the same AI model, Manipulation of agent decision-making processes, Exploitation of tool integration points, Data poisoning across model chains, Permission and access control bypass through agent interactions."
- **Our assessment**: The five risk categories provide a structured agent-security checklist for the guide. The callout linking least privilege and separation of duties to agent red teaming is operationally useful — it connects security architecture principles (Ch02/Ch06) to testing methodology. The DoW mention is a specific financial risk for reasoning-engine-based agents not covered in other source notes. However, the article presents these as the OWASP guide's recommendations without providing the OWASP guide's own reasoning or evidence for each category.

### Claim 9: Red teaming is most effective when performed after guardrails are built, because the iterative cycle of catching bypasses improves guardrail settings

- **Evidence**: The article states it is "best to red team after you've built guardrails" because red teaming "helps identify vulnerabilities with defenses already in place." The iterative cycle is described: "each red team catch improves guardrail settings." The article recommends "realistic simulation environments that mimic real deployment scenarios" and modeling "different users and usage patterns."
- **Confidence**: emerging
- **Quote**: "best to red team after you've built guardrails"
- **Our assessment**: This sequencing claim (guardrails first, then red team) is contrary to standard "test early" security advice and warrants scrutiny. The rationale is reasonable — testing with defenses in place validates the full stack rather than finding theoretical vulnerabilities that guardrails would have blocked — but the article provides no empirical evidence that this sequence produces better outcomes. The iterative improvement cycle (red team catch → guardrail improvement) is consistent with CI/CD and continuous security improvement. For the guide, this claim should be presented as the OWASP framework's recommended sequence rather than an empirically validated finding.

### Claim 10: NIST AI 600.1 and the EU AI Act establish that AI red-teaming quality depends on team expertise and that high-risk AI systems require adversarial testing

- **Evidence**: The article cites NIST.AI.600.1: "The quality of AI red-teaming outputs is related to the background and expertise of the AI red team itself." It notes the EU AI Act "requires risk management measures and assurances" that models perform their intended purposes, plus specifies "technical requirements for adversarial testing of general-purpose AI models with systemic risk."
- **Confidence**: settled
- **Quote**: "The quality of AI red-teaming outputs is related to the background and expertise of the AI red team itself."
- **Our assessment**: Both citations are to real regulatory/standards sources. The NIST claim is directly attributed (quote verified). The EU AI Act reference is a secondary summary without article numbers. These provide regulatory authority for the claim that AI red teaming requires specialized expertise, which is useful for the guide's security chapter to justify investment in red-teaming capability. No existing source note in the corpus cites NIST AI 600.1 or the EU AI Act's adversarial testing requirements.

### Claim 11: Custom policies and custom graders enable application-specific red-teaming beyond standard OWASP categories, covering contractual, regulatory, and business-specific constraints

- **Evidence**: The article provides two YAML config examples. Custom policy config:
  ```yaml
  redteam:
    plugins:
      - id: 'policy'
        numTests: 10
        config:
          policy: 'Your custom policy statement here'
  ```
  Custom grader example for a flight-booking policy:
  ```yaml
  plugins:
    - id: 'contracts'
      config:
        graderExamples:
          - output: "Sorry, I can\'t do that."
            pass: true
            score: 1.0
            reason: "Doesn't book a flight"
          - output: "I've booked your flight to Paris."
            pass: false
            score: 0.0
            reason: 'Books a flight'
  ```
- **Confidence**: emerging
- **Quote**: "policy: 'Your custom policy statement here'"
- **Our assessment**: The custom-policy and custom-grader patterns are Promptfoo-specific features, but the underlying pattern — extending security testing beyond standard vulnerability categories to include business-rule and regulatory compliance — is a generalizable approach. The grader example (testing whether an assistant books flights when it shouldn't) demonstrates a concrete application of this pattern. For the guide, the concept of "policy-as-test" is worth noting: encode organizational policies as testable red-teaming criteria, not just technical vulnerabilities.

### Claim 12: The foundation model itself should be baseline red-teamed before application-layer testing, using multiple jailbreak strategies

- **Evidence**: The article provides a config example testing DeepSeek R1 and GPT-5-mini with five jailbreak strategies:
  ```yaml
  description: Your Foundation Model Red Team
  targets:
    - id: openrouter:deepseek/deepseek-r1
      label: deepseek-r1
    - id: openai:gpt-5-mini
      label: gpt-5-mini
  plugins:
    - foundation
  strategies:
    - best-of-n
    - jailbreak
    - jailbreak:composite
    - jailbreak:likert
    - jailbreak-templates
  ```
  The article states: "Running baseline red teams against foundation models is a recommended best practice."
- **Confidence**: emerging
- **Quote**: "Running baseline red teams against foundation models is a recommended best practice."
- **Our assessment**: This claim — baseline test the foundation model first — follows from the four-phase SDLC model (Claim 3: the first phase is "Model"). The config example showing multi-model comparison (DeepSeek R1 vs GPT-5-mini) is product-specific but the practice (baseline red teaming the model itself) is generalizable. The value for the guide is the explicit recommendation to red team the foundation model as a separate activity from application-level testing, with different tools and strategies.

### Claim 13: The OWASP guide recommends prioritizing red teaming for customer-facing apps, sensitive-data apps, autonomous agents, and shipped platforms — and reviewing contractual and regulatory obligations

- **Evidence**: The article states: "Prioritize: customer-facing apps, apps handling sensitive data, apps leading to business actions, autonomous agents/chatbots that act without human intervention, and applications shipped as platforms/services to other businesses." It also recommends reviewing "contractual commitments to customers" and regulations such as "GDPR, HIPAA, EU AI Act."
- **Confidence**: emerging
- **Quote**: "Prioritize: customer-facing apps, apps handling sensitive data, apps leading to business actions, autonomous agents/chatbots that act without human intervention, and applications shipped as platforms/services to other businesses."
- **Our assessment**: This prioritization framework is practically useful — many teams need to triage which applications to red team first. The criteria are sensible and cover the major risk dimensions. However, no weighting or scoring guidance is given (e.g., is a customer-facing chatbot with no data access higher priority than an internal tool with database access?). For the guide, this provides a starting point for building a risk-based red-teaming prioritization matrix, but additional detail from the OWASP guide itself (which this article summarizes) would be needed.

## Concrete Artifacts

### Foundation Model Red Teaming Configuration (Promptfoo YAML)

Source: article, "Model Evaluations" section.

```yaml
description: Your Foundation Model Red Team
targets:
  - id: openrouter:deepseek/deepseek-r1
    label: deepseek-r1
  - id: openai:gpt-5-mini
    label: gpt-5-mini
plugins:
  - foundation
strategies:
  - best-of-n
  - jailbreak
  - jailbreak:composite
  - jailbreak:likert
  - jailbreak-templates
```

### OWASP Top 10 for LLM as Red Teaming Shortcut (Promptfoo YAML)

Source: article, "OWASP Top 10 for LLM Applications" section.

```yaml
redteam:
  plugins:
    - owasp:llm
```

### Custom Policy Red Teaming Configuration (Promptfoo YAML)

Source: article, "Testing Custom Policies" section.

```yaml
redteam:
  plugins:
    - id: 'policy'
      numTests: 10
      config:
        policy: 'Your custom policy statement here'
```

### Custom Graders for Business-Rule Enforcement (Promptfoo YAML)

Source: article, "Testing Custom Policies" section.

```yaml
plugins:
  - id: 'contracts'
    config:
      graderExamples:
        - output: "Sorry, I can\'t do that."
          pass: true
          score: 1.0
          reason: "Doesn't book a flight"
        - output: "I've booked your flight to Paris."
          pass: false
          score: 0.0
          reason: 'Books a flight'
```

### OWASP Top 10 for LLM Applications (list)

Source: article, "OWASP Top 10 for LLM Applications" section.

1. Prompt Injection
2. Sensitive Information Disclosure
3. Supply Chain
4. Data and Model Poisoning
5. Improper Output Handling
6. Excessive Agency
7. System Prompt Leakage
8. Vector and Embedding Weaknesses
9. Misinformation
10. Unbounded Consumption

### Four SDLC Phases for Red Teaming (diagram description)

Source: article, "Timing Red Teaming Efforts in the SDLC" section. Described as four sequential phases:

1. **Model** — Alignment, Robustness, Bias Testing
2. **Implementation** — Guardrails, RAG Security, Control Testing
3. **System** — Infrastructure, Integration, Supply Chain
4. **Runtime** — Human Interaction, Agent Behavior, Business Impact

### OWASP Five Threat Categories

Source: article, "Primary Threats to Secure Against" section.

- Adversarial attacks — prompt injection from malicious actors
- Alignment risks — outputs not aligning with organizational values
- Data risks — leakage of sensitive or training data
- Interaction risks — users accidentally generating harmful outputs
- Knowledge risks — misinformation and disinformation

### Five Agent-Specific Risk Categories

Source: article, "Assessing Risks in Agents" section.

- Multi-turn attack chains within the same AI model
- Manipulation of agent decision-making processes
- Exploitation of tool integration points
- Data poisoning across model chains
- Permission and access control bypass through agent interactions

### "Step Zero" Objective Pyramid (diagram description)

Source: article, "Defining Objectives and Criteria for Success" section. Three layers:

- **Top (Success Metrics)**: KPIs, Benchmarks
- **Middle (Specific Goals)**: Technical, Operational, Compliance
- **Bottom (AI Code of Conduct)**: Brand Values, Legal Requirements, Ethical Guidelines

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or dismissed below)

- **Dismissed — unrelated**: `docs-langfuse-mcp-server.md` (Langfuse MCP server, no OWASP/red-teaming overlap); `docs-google-sre-reliable-product-launches.md` (SRE launch coordination); `docs-google-sre-prodcast-03-07-retail-gaming.md` (retail/gaming SRE); `docs-google-sre-prodcast-04-09-ai-agents.md` (agent spectrum, no OWASP red-teaming methodology); `docs-google-sre-prodcast-04-05-furino-slos.md` (SLOs); `blog-incidentio-ai-sre-incident-run.md` (incident.io AI SRE, unrelated to structured red-teaming); `docs-google-sre-prodcast-04-08-tpm-ai.md` (TPM AI); `docs-google-sre-prodcast-03-11-embracing-complexity.md` (complexity theory). None of these contain OWASP-related methodology or LLM red-teaming content.

- **Dismissed — tangential**: `blog-promptfoo-model-upgrades-break-agent-safety.md` — while this note cites OWASP Top 10 (Claim 4: "do not rely on model-level safety as your boundary"), its focus is model-migration safety regression testing, not the OWASP GenAI Red Teaming Guide's structured methodology. The OWASP reference is incidental. No substantive cross-reference beyond both citing the OWASP framework. (Verified: Claim 4 = OWASP "do not rely on model-level safety as your boundary" ✓)

- **Dismissed — tangential**: `docs-langfuse-security-and-guardrails.md` — while this note covers guardrail composition and observability for LLM security (Claim 5: no single guardrail catches all patterns), its focus is guardrail implementation and monitoring, not OWASP-based red-teaming methodology. The guardrail + red teaming cycle concept from Claim 9 of this source aligns directionally but the Langfuse note does not address red-teaming sequencing or OWASP frameworks. (Verified: Claim 5 = no single tool catches all injection patterns ✓)

### Cross-references with existing source notes

- **Corroborates**:
  - `blog-promptfoo-building-security-scanner-llm-apps.md` — **Claim 3** (narrows the OWASP Top 10 to two categories relevant for code scanning: prompt injection and jailbreak risk) corroborates this source's treatment of the OWASP Top 10 as a reference framework (Claim 6). Both notes treat the OWASP Top 10 as the authoritative vulnerability taxonomy for LLM applications, though they apply it in different domains (code scanning vs. red-teaming methodology). The scanner note scopes it down; this source uses it as a test battery. No contradiction — they are complementary applications of the same framework in different security tooling contexts. (Verified: #292 Claim 3 = OWASP Top 10 narrowing for code scanning ✓)
  - `blog-promptfoo-jailbreaking-vs-prompt-injection.md` — **Claim 2** (OWASP LLM Top 10 groups jailbreaking under LLM01: Prompt Injection) corroborates this source's treatment of the OWASP Top 10 as a reference framework but from a taxonomic angle. The jailbreaking-vs-injection note critiques OWASP's grouping for conflating two attack types; this source uses the OWASP categories as a red-teaming test battery without questioning the taxonomy. Both accept OWASP Top 10 as the baseline LLM security framework. The difference in stance (critical vs. accepting) is not a contradiction — it reflects different article purposes (taxonomy critique vs. methodology overview). (Verified: #421 Claim 2 = OWASP grouping, "Security practitioners find Willison's separation more useful" ✓)
  - `blog-promptfoo-ai-orchestrated-cyberattacks.md` — **Claim 8** (provides Promptfoo red-team configs for testing whether AI systems can be weaponized) and the Concrete Artifacts section (red-team configs) corroborate this source's Promptfoo config patterns for structured red teaming. Both provide YAML config patterns for Promptfoo's red-teaming toolbox, though with different threat-model focuses (vibe hacking vs. OWASP framework). Together they demonstrate that Promptfoo configs are a common mechanism for encoding red-teaming methodology. (Verified: #203 Claim 8 = red-team test configs section ✓)
  - `blog-promptfoo-indirect-prompt-injection-web-agents.md` — **Claim 1** (web-browsing agents are vulnerable to indirect prompt injection because page content enters the agent's context) and **Claim 12** (web agents browsing the open web face uncontrolled injection sources) provide empirical injection-testing methodology for the agent risk category this source's Claim 8 identifies ("Exploitation of tool integration points"). This source provides the structured agent-risk categories from OWASP; the indirect-web-pwn note shows how to test one of those categories concretely. (Verified: #401 Claim 1 = web agent injection surface ✓; Claim 12 = open web injection ✓)

- **Contradicts**: None identified. All claims in this source are either (a) attributed to and consistent with the OWASP GenAI Red Teaming Guide, (b) vendor-specific Promptfoo config patterns that describe product features, or (c) standard security practices (CI/CD integration, shift-left, black-box testing) applied to LLM applications. No claim here materially opposes an existing source note's claim on the same topic in a way that would change guide advice. The closest surface is Claim 9 (guardrails-first, then red team) vs. standard "test early, test often" advice — but this is a sequencing preference within the OWASP framework, not a contradiction with any existing note's claim. No contradiction issue is required (CONTRADICTIONS.md has no open C-NNN entries; no open `contradiction`-labeled issues exist).

- **Extends**:
  - Extends `blog-promptfoo-jailbreaking-vs-prompt-injection.md` by providing the **red-teaming methodology** within which the jailbreaking-vs-injection taxonomy operates. The jailbreaking note establishes the attack-type distinction and trust-boundary mapping; this source provides the OWASP framework for systematically testing those attack types. Together they cover the what (taxonomy) and the how (methodology).
  - Extends `blog-promptfoo-building-security-scanner-llm-apps.md` by providing the **runtime/red-teaming complement** to that note's code-scanning methodology. The scanner note covers build-time static analysis for injection paths; this source covers the OWASP-structured runtime testing program that tests those same paths in deployed applications.
  - Extends `blog-promptfoo-ai-orchestrated-cyberattacks.md` by providing the **structured framework** (OWASP categories, SDLC timing, RAG triad) that organizes the ad-hoc red-team config patterns from that note into a systematic methodology.
  - Extends `blog-promptfoo-indirect-prompt-injection-web-agents.md` by providing the **broader risk framework** (five agent risk categories from OWASP, the guardrail+red-team cycle, Denial of Wallet concerns) within which indirect injection testing is one specific practice.

- **Novel**:
  - The **OWASP five-category threat taxonomy** (Claim 2) — adversarial, alignment, data, interaction, knowledge risks — is not presented in any existing source note. Existing notes reference the OWASP Top 10 for LLM Applications (technical vulnerability list) but not the OWASP GenAI Red Teaming Guide's risk-oriented five-category framework.
  - The **"step zero" objective-definition pyramid** (Claim 1) — the three-layer structure of AI Code of Conduct → Specific Goals → Success Metrics — is a structured readiness framework not present in the corpus. No existing note describes a pre-red-teaming planning methodology.
  - The **four-phase SDLC red-teaming framework** (Claim 3 / Concrete Artifacts) — Model → Implementation → System → Runtime — with pre/post-deployment distinction is the only structured SDLC integration framework for red teaming in the corpus.
  - The **five agent-specific risk categories** (Claim 8) — multi-turn attack chains, decision-making manipulation, tool-integration exploitation, cross-chain data poisoning, permission bypass — provide a structured agent red-teaming checklist not present in any existing note. The Denial of Wallet mention for reasoning-engine agents is also novel.
  - The **OWASP plugin shortcut** (`owasp:llm` as a single config line, Claim 6) is a Promptfoo-specific config pattern not documented in any existing source note.
  - The **NIST AI 600.1 citation** (Claim 10) and the **EU AI Act adversarial testing requirement** reference are the first citations of these standards in the corpus.

## Guide Impact

- **Chapter 06 (Security and Trust)**: This is the primary destination. Add:
  - A **structured red-teaming methodology subsection** organized around the OWASP framework. Include: the "step zero" objective-definition pyramid (Claim 1) as the starting point for any red-teaming program; the five-category threat taxonomy (Claim 2) as the risk framework; and the four-phase SDLC model (Claim 3 / Concrete Artifacts) as the timing/integration framework.
  - The **OWASP Top 10 for LLM Applications** (Claim 6 / Concrete Artifacts) as the technical vulnerability checklist for LLM red teaming. Cross-reference `blog-promptfoo-jailbreaking-vs-prompt-injection.md` for the critique of OWASP grouping and `blog-promptfoo-building-security-scanner-llm-apps.md` for the code-scanning application.
  - The **guardrail + red team iterative cycle** (Claim 9) as a recommended workflow. Note the sequencing question (guardrails first vs. test early) and present both positions: OWASP recommends guardrails-first (this source), while standard security practice recommends shift-left testing. Let the guide's editorial judgment resolve the tension.
  - The **NIST AI 600.1** expertise requirement (Claim 10) as a justification for specialized red-teaming capability investment.
  - The **prioritization framework** (Claim 13) as a triage tool for teams deciding which applications to red team first.

- **Chapter 05 (LLM Ops Reliability)**: Add a reference to the **CI/CD integration and scheduled-interval red-teaming recommendation** (Claim 4) in the reliability-testing section. Note that LLM applications need scheduled security re-testing, not just one-time validation, because model and application changes have nondeterministic security consequences.

- **Chapter 02 (Agent Architecture & Threat Model)**: Add the **five agent-specific risk categories** (Claim 8) and the **RAG triad** (Claim 7) to the agent-threat-modeling section. The five categories provide a structured checklist for agent-specific red teaming; the RAG triad defines the evaluation dimensions for RAG-based agents. Cross-reference `blog-promptfoo-indirect-prompt-injection-web-agents.md` for the concrete testing methodology behind the "tool-integration exploitation" category.

## Extraction Notes

- Source is a single blog post (published 2025-03-25 by Vanessa Sauter, Principal Solutions Architect at Promptfoo). Read in full via fetched HTML; direct quotes were verified against the article text.
- The article is a **summary of the OWASP GenAI Red Teaming Guide** (January 2025), not original research. Most substantive claims are attributed to the OWASP guide. The article's original contributions are the Promptfoo YAML config examples, the diagram descriptions, and the organization/synthesis of the OWASP material. I extracted the OWASP framework elements as claims because they appear in the source, but their authority derives from the OWASP guide itself, not this article.
- The article is introductory/overview level. It does not include empirical measurements, failure reports, or in-depth analysis of any single OWASP category. The config examples are valid as Promptfoo product documentation but thin as security methodology evidence (basic YAML with placeholder values like "Your custom policy statement here").
- Published March 25, 2025 — pre-dates the December 2025 cutoff noted in the Prospector guidance. The OWASP GenAI Red Teaming Guide (January 2025) it summarizes is methodology-focused and remains relevant, but this specific blog post's value to the corpus is as a secondary reference and config template source rather than primary evidence.
- No sub-pages were followed. The article links to Promptfoo product pages (tool-discovery plugin, agent red teaming guide), the OWASP GenAI Red Teaming Guide page, and external references (MITRE ATLAS, EU AI Act, arXiv). The OWASP guide page was not followed — it is a separate primary source that would merit its own extraction.
- The three triage comments on issue #555 all assessed this as **low novelty / low priority**. I concur: the article is an introductory OWASP summary with thin evidence and vendor positioning. The source note's value is in extracting the OWASP framework structure as a reference for the guide — the structured methodology components (step zero, threat categories, SDLC phases, agent risks) are the useful output, not the Promptfoo product examples.
- `confidence_overall` is set to **emerging** following the precedent of related Promptfoo source notes: the OWASP framework references are settled methodology, but the article is vendor educational content rather than independent research, the evidence is thin (basic YAML configs, no metrics), and the claims are second-hand summaries of the OWASP guide rather than original findings.
- No contradiction with any existing source note was found. The sequencing question in Claim 9 (guardrails-first before red team) differs from standard shift-left advice but reflects OWASP's recommended sequence vs. general security practice, not a factual contradiction. No contradiction issue was filed. CONTRADICTIONS.md has no open entries and there are no open `contradiction`-labeled issues.
