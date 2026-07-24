---
source_url: https://www.promptfoo.dev/blog/mckinsey-lilli-appsec-vs-ai-jailbreak/
source_type: blog-post
title: "McKinsey's Lilli Looks More Like an API Security Failure Than a Model Jailbreak"
author: "Michael D'Angelo (Co-founder & CTO, Promptfoo)"
date_published: 2026-03-10
date_extracted: 2026-07-24
last_checked: 2026-07-24
status: current
confidence_overall: emerging
issue: "#464"
---

# McKinsey's Lilli Looks More Like an API Security Failure Than a Model Jailbreak

> A post-mortem analysis of the McKinsey Lilli incident arguing it was fundamentally
> an application-security breach (exposed API surface, SQL injection, BOLA) where the
> AI layer amplified the blast radius without changing the entry vector. The central
> architectural insight — prompts, routing rules, and retrieval settings as mutable
> application data — defines a new class of AI incident rooted in database compromise
> rather than model jailbreak.

## Source Context

- **Type**: blog-post (security incident case study by a vendor CTO)
- **Author credibility**: Michael D'Angelo is Co-founder & CTO of Promptfoo (site
  banner notes "Promptfoo is now part of OpenAI"). The article is an incident analysis
  based on CodeWall's March 9, 2026 writeup and public reporting from The Register.
  The author is a credible practitioner with security-domain expertise, but the article
  is commentary on third-party findings rather than primary incident investigation.
  Exact payloads were not published by CodeWall ("the public record does not
  independently prove every reported row count or every step of exploitation"), so
  specific exploitation details are treated as plausible but unverified at the
  individual-query level. The architectural observations (mutable config → blast radius
  amplification) are the author's own analysis and the highest-confidence extract.
- **Scope**: Covers (1) the reported AppSec attack chain (exposed API surface, SQL
  injection via JSON key concatenation, BOLA), (2) the architectural insight about
  mutable prompt/routing/config storage, (3) the "blast radius, not entry vector"
  framing, (4) a four-point audit checklist for enterprise AI assistants, and (5)
  the implication that most "AI incidents" will start as software bugs and end as
  model behavior changes. Does NOT cover: specific exploit payloads, remediation
  implementation details, a full red-teaming methodology, or comparisons to other
  AI security frameworks. Referenced sources (CodeWall, The Register, McKinsey case
  studies) were not independently verified beyond what the article quotes.

## Extracted Claims

### Claim 1: The McKinsey Lilli incident was an AppSec failure (exposed API surface, SQL injection, BOLA) reaching an AI system, not a model jailbreak
- **Evidence**: The article opens with this thesis: "McKinsey's Lilli looks, on the
  public record, like an application-security incident that reached an AI system, not
  a model jailbreak." CodeWall's writeup identified "exposed API documentation,
  unauthenticated endpoints, a SQL injection condition, and cross-user access."
  McKinsey confirmed to The Register that issues were fixed within hours. The article
  states: "The initial foothold appears to have been a familiar AppSec chain: exposed
  API surface, missing authentication, unsafe SQL construction, and broken object-level
  authorization."
- **Confidence**: emerging (based on second-hand reporting; exact payloads were not
  published)
- **Quote**: "McKinsey's Lilli looks, on the public record, like an application-security incident that reached an AI system, not a model jailbreak."
- **Our assessment**: This is the article's central claim and is well-supported by the
  public record as summarized. The caveat is that exact payloads were not published, so
  the chain of exploitation cannot be independently replicated step-by-step. However,
  the class of bug (public routes, backend injection, missing authorization) is
  identifiable from the incident description. The claim is significant because it
  reframes AI incident response away from "model behavior analysis" toward application
  security investigation — a practical reorientation for incident responders.

### Claim 2: If prompts, routing rules, and retrieval settings exist as mutable application data, then database write access can change model behavior without a code deployment
- **Evidence**: The article states: "The architectural issue is straightforward. If
  prompts, routing rules, and retrieval settings live as mutable application data, then
  database write access can change model behavior without a code deploy." This is the
  article's key architectural insight — not a finding specific to McKinsey, but a
  general property of any enterprise assistant architecture where configuration lives
  in application tables.
- **Confidence**: settled (this is a logical consequence of architecture design, not
  contingent on the incident's specifics)
- **Quote**: "If prompts, routing rules, and retrieval settings live as mutable application data, then database write access can change model behavior without a code deploy."
- **Our assessment**: This is the highest-confidence claim in the source and the most
  novel contribution to the guide. It identifies a specific architectural risk pattern
  that is present whenever an enterprise assistant stores its behavioral configuration
  (prompts, routing rules, retrieval policy) in the same database as application data.
  A SQL injection or BOLA vulnerability that grants write access to that database
  becomes functionally equivalent to modifying the assistant's source code — but
  without the guardrails of code review, CI/CD, or deployment gates. This claim should
  anchor the guide's security architecture principles for enterprise AI assistants.

### Claim 3: The AI-specific element of the incident was not the entry point but the blast radius — the model became the interface to a compromised application
- **Evidence**: The article explicitly separates the entry vector from the impact:
  "The AI-specific part was not the entry point. It was the blast radius." It further
  explains: "If the same backend stored prompts, routing rules, retrieval metadata,
  and user history, then backend access reached the system that shaped Lilli's answers."
  The bottom line synthesizes: "The model became the interface to a compromised
  application."
- **Confidence**: emerging
- **Quote**: "The AI-specific part was not the entry point. It was the blast radius."
- **Our assessment**: This framing is the article's most important conceptual
  contribution. It directly addresses a common misattribution pattern in AI incident
  response: because the model is the visible layer, incidents are classified as "model
  failures" (jailbreaks, safety failures) when the root cause is a standard application
  vulnerability. For the guide's incident response chapter, this provides a concrete
  diagnostic heuristic: when an AI incident is reported, first determine whether the
  model was *attacked* or was the *interface to an already-compromised application*.

### Claim 4: CodeWall reported an AppSec chain beginning with public API documentation and unauthenticated endpoints, followed by JSON-key SQL injection, then BOLA/cross-user access
- **Evidence**: The article describes CodeWall's reported chain: "CodeWall's March 9,
  2026 writeup says its autonomous agent found exposed API documentation, unauthenticated
  endpoints, a SQL injection condition, and cross-user access." On the SQL injection
  mechanism: "CodeWall says ordinary JSON values were parameterized, but
  attacker-controlled JSON keys or identifiers were still concatenated into SQL syntax."
  The article identifies the cross-user access pattern as BOLA: "the application accepts
  an object identifier and returns a record without verifying that the caller is allowed
  to see it."
- **Confidence**: anecdotal (second-hand from CodeWall; exact payloads unpublished)
- **Quote**: "CodeWall says ordinary JSON values were parameterized, but attacker-controlled JSON keys or identifiers were still concatenated into SQL syntax."
- **Our assessment**: The specific exploitation chain is reported second-hand and
  cannot be independently verified at the payload level. However, the class of
  vulnerability is familiar and the mechanism (JSON key concatenation into SQL syntax)
  is well-documented in security research. The article acknowledges this limitation:
  "Because CodeWall did not publish the exact payloads, the public cannot reconstruct
  each query or iteration step by step. It can still reconstruct the class of bug:
  public routes, backend injection, and missing object-level authorization." The
  higher-order pattern — mutable data in application tables changing AI behavior — does
  not depend on the specific exploitation details.

### Claim 5: SQL injection via JSON keys and identifiers is a documented, plausible attack pattern (not exotic), supported by OWASP guidance, Claroty research, and CVE-2026-25544
- **Evidence**: The article cites three independent references to support the
  plausibility of JSON-key SQL injection: OWASP's SQL Injection Prevention Cheat Sheet
  (table names, column names, and sort-order indicators are protected differently than
  bind variables protect values), Claroty's "research on JSON-based SQL used to bypass
  WAFs," and "NVD's writeup for CVE-2026-25544 in Payload CMS."
- **Confidence**: settled (the cited references are independently verifiable)
- **Quote**: "OWASP's SQL Injection Prevention Cheat Sheet makes the underlying point directly: table names, column names, and sort-order indicators are not protected the same way bind variables protect values."
- **Our assessment**: The article correctly identifies that JSON-key concatenation into
  SQL is not about the values (which are parameterized) but about the schema-level
  identifiers (keys, field names, sort parameters), which typically cannot be bind
  variables. This is a well-understood SQL injection variant in the security community.
  The Claroty and CVE-2026-25544 references provide independent verification that this
  pattern has been observed and exploited in real products. This claim is important for
  the guide because it redirects security audits to look beyond standard value-based
  parameterization to also cover key/field-name injection paths.

### Claim 6: Database compromise of an enterprise AI assistant can turn a write into a prompt change, a metadata edit into a retrieval alteration, and a permissions flaw into cross-user data synthesis
- **Evidence**: The article describes the escalation: "A write can become a prompt
  change. A metadata edit can change what the system retrieves. A permissions flaw can
  let the assistant synthesize another employee's history into a normal-looking
  response." It frames this as an amplification mechanism distinct from model
  subversion: "The model does not need to be tricked in the usual jailbreak sense if
  the surrounding system feeds it altered instructions, altered context, or altered
  permissions."
- **Confidence**: emerging
- **Quote**: "A write can become a prompt change. A metadata edit can change what the system retrieves. A permissions flaw can let the assistant synthesize another employee's history into a normal-looking response."
- **Our assessment**: This claim concretizes the "blast radius" framing from Claim 3
  into specific impact scenarios. Each scenario (→ prompt change, → retrieval alteration,
  → cross-user synthesis) maps to a different component of an enterprise assistant
  (system prompt storage, retrieval pipeline, access-control metadata). These scenarios
  are not speculative — they are direct consequences of the mutable-data architecture
  pattern. For the guide, each scenario implies a specific security control: prompt
  integrity verification, retrieval ACL enforcement, and access-control metadata
  hardening, respectively.

### Claim 7: Teams should audit four control points — public routes, SQL/ORM injection in JSON keys, BOLA coverage, and mutable prompt/config storage as governed configuration
- **Evidence**: The article lists four bullet points under "What teams should audit":
  (1) "public and undocumented routes that bypass standard authentication and
  authorization middleware," (2) "SQL or ORM paths that treat request keys, JSON paths,
  field names, or sort parameters as dynamic identifiers," (3) "BOLA coverage for
  assistants that can read internal knowledge, employee records, or client-linked
  objects," and (4) "prompts, routing rules, retrieval policy, and access-control
  metadata stored as mutable rows instead of governed configuration."
- **Confidence**: emerging (these are the author's recommendations, not validated
  findings)
- **Quote**: "public and undocumented routes that bypass standard authentication and authorization middleware"
- **Our assessment**: This is a practical, actionable audit checklist derived from the
  incident analysis. Each bullet maps to a specific vulnerability class from the
  incident: (1) the exposed API documentation and unauthenticated endpoints, (2) the
  JSON-key SQL injection, (3) the cross-user access (BOLA), and (4) the mutable
  prompt/routing/data architecture pattern. The checklist is not exhaustive but is
  well-scoped and directly grounded in an observed incident. For the guide, this
  provides a concrete, citable audit framework for enterprise AI assistant security
  reviews. The fourth bullet — where the article recommends "governed configuration"
  rather than "mutable rows" — is the most forward-looking recommendation and the
  least commonly implemented in current architectures.

### Claim 8: More enterprise "AI incidents" will start as ordinary software bugs and end as changes in model behavior — teams should audit the application layer, not just model behavior
- **Evidence**: The article's concluding paragraphs: "As more enterprise assistants
  store prompts, retrieval policy, and user context in ordinary backend systems, more
  'AI incidents' will start the same way. They will begin as familiar software bugs and
  end as changes in model behavior." And the warning against misclassification: "The
  easy mistake is to classify incidents like this as model failures because the model
  is what users see. The more useful framing is simpler: the model became the interface
  to a compromised application."
- **Confidence**: emerging
- **Quote**: "They will begin as familiar software bugs and end as changes in model behavior."
- **Our assessment**: This claim is the article's forward-looking thesis and is the
  most significant for the guide's incident response and security chapters. It predicts
  that as AI assistants become more tightly integrated with backend systems (storing
  prompts, retrieval config, user context), the incident class will shift. The claim
  is logically consistent with the architectural pattern described (mutable config in
  application databases), but it is a prediction, not an empirical finding. It
  nonetheless provides a strong rationale for the guide to recommend cross-team
  incident response (AppSec + AI infra) rather than siloed model-behavior analysis.

### Claim 9: McKinsey described Lilli as a firmwide system with 72% active usage, handling 500K+ prompts/month and 4.5M+ queries across 200K+ documents
- **Evidence**: The article cites McKinsey's own public case studies: "72 percent of
  the firm was active on the platform and that Lilli handled more than 500,000 prompts
  a month," and "answered more than 4.5 million queries over more than 200,000
  documents."
- **Confidence**: settled (McKinsey's own case study data, cited by the article)
- **Quote**: "72 percent of the firm was active on the platform and that Lilli handled more than 500,000 prompts a month"
- **Our assessment**: This provides scale context for the incident — Lilli was not an
  experimental or low-traffic system but a firmwide deployment with substantial
  adoption. The scale amplifies the significance of the attack-chain analysis: a
  vulnerability class that might be low-severity in a small deployment becomes
  high-severity at this scale. Useful for the guide when discussing risk assessment
  and blast-radius analysis for enterprise AI assistants.

## Concrete Artifacts

### Audit Checklist (verbatim from "What teams should audit" section)

```
public and undocumented routes that bypass standard authentication and authorization middleware
SQL or ORM paths that treat request keys, JSON paths, field names, or sort parameters as dynamic identifiers
BOLA coverage for assistants that can read internal knowledge, employee records, or client-linked objects
prompts, routing rules, retrieval policy, and access-control metadata stored as mutable rows instead of governed configuration
```

Source: promptfoo blog, "What teams should audit" section. Four bullet points presented
as the practical audit checklist derived from the incident analysis.

### Bottom Line Framing (verbatim from "Bottom line" section)

```
The easy mistake is to classify incidents like this as model failures because the model is what users see.
The more useful framing is simpler: the model became the interface to a compromised application.
```

Source: promptfoo blog, "Bottom line" section. The article's concluding two-sentence
framing that captures the core reframing.

### Tags (verbatim from article footer)

```
security-vulnerability
ai-security
owasp
```

Source: promptfoo blog, tags at bottom of article.

## Cross-References

- **Corroborates**:
  - `blog-promptfoo-jailbreaking-vs-prompt-injection.md` (#421) — **Claim 1** (prompt
    injection targets the application's trust boundaries; jailbreaking targets the
    model's safety training) provides the taxonomic framework that this source's
    incident analysis operationalizes. The McKinsey Lilli incident is a textbook
    example of an application-layer attack (SQL injection, BOLA) that reached an AI
    system — the model was not "jailbroken" in the safety-training sense; the
    application was compromised. **Claim 4** (prompt injection can compromise
    privileged system components; jailbreaking stays within the model's text generation)
    is demonstrated empirically by the Lilli incident: the backend database was the
    "privileged system component" that SQL injection reached, and that access then
    altered model behavior. (Verified: jailbreaking note Claim 1 = targets model safety
    training; Claim 4 = jailbreaking stays within text generation, prompt injection
    reaches privileged components.)
  - `blog-promptfoo-building-security-scanner-llm-apps.md` (#292) — **Claim 2** (the
    LLM "launders" untrusted input: the LLM transforms input into output that "looks
    and feels safe") describes the mechanism by which SQL injection via JSON keys
    (Claim 4 of this note) leads to undetected behavior changes — the LLM output
    looks normal even when the backend has been compromised. **Claim 4** (deadly duo:
    exposure to untrusted content + privileged actions) captures exactly the risk
    pattern this incident exemplifies: the database was a privileged action target,
    and its compromise gave the attacker the ability to alter prompts and routing
    without a code deploy. (Verified: scanner note Claim 2 = laundering; Claim 4 =
    deadly duo.)
  - `blog-pagerduty-production-ai-agent-gaps.md` — **Claim 5** (AI agents are highly
    susceptible to prompt injection, 80-90% range, citing Chang et al., 2026) provides
    quantitative context for why the Lilli incident's database-level compromise route
    is especially dangerous: even if model-level defenses are strong, the application
    layer (database, API surface) provides an alternative path that bypasses model
    safety entirely. **Claim 14** (defense-in-depth guardrails) aligns with this
    note's recommendation (Claim 7) to treat prompt/routing/config as governed
    configuration. (Verified: PagerDuty note Claim 5 = 80-90% prompt injection
    susceptibility; Claim 14 = defense-in-depth guardrails.)
  - `docs-google-sre-prodcast-04-01-security-sre-intersection.md` — The security-SRE
    intersection framing aligns with this note's thesis: the Lilli incident was not
    an AI failure but a security failure reaching an AI system, requiring both AppSec
    and SRE response. The specific Security/SRE framing from the prodcast — security
    identifies vulnerability classes, SRE implements resilient systems — maps onto
    this note's recommendation that both teams must collaborate on AI assistant
    architecture reviews.

- **Contradicts**: None identified. The article's central claim (that the Lilli
  incident was an AppSec failure rather than a model jailbreak) does not contradict
  any existing source note — it provides a real-world incident case study that
  operationalizes the jailbreak-vs-injection taxonomy from
  `blog-promptfoo-jailbreaking-vs-prompt-injection.md` rather than contradicting it.
  The "mutable config as blast radius amplifier" pattern is novel and does not oppose
  any existing claim. CONTRADICTIONS.md has no open entries and there are no open
  `contradiction`-labeled issues. No contradiction issue is required.

- **Extends**:
  - Extends `blog-promptfoo-jailbreaking-vs-prompt-injection.md` by providing a
    *real-world incident case study* that operationalizes the jailbreak-vs-injection
    taxonomy. That note establishes the conceptual distinction; this note demonstrates
    it with a concrete incident where the application layer (exposed API, SQL
    injection, BOLA) was the entry vector and the model was the visible outcome. The
    taxonomy note asks "what's the difference?"; this note answers "here's what it
    looks like when an enterprise assistant is compromised through the application
    layer."
  - Extends `blog-promptfoo-building-security-scanner-llm-apps.md` by providing a
    *production incident case study* that justifies the scanner's design principles.
    The scanner note describes tooling for detecting injection paths in code; this
    note shows what happens when those paths are missed in production. The "deadly
    duo" (untrusted content + privileged actions) is demonstrated in the Lilli
    incident: the database was a privileged action target, and backend access was
    gained through a classic AppSec chain.
  - Extends `blog-pagerduty-production-ai-agent-gaps.md` by providing a *specific
    architectural vulnerability pattern* (mutable prompt/routing/config storage) that
    the PagerDuty-identified guardrails should be designed to prevent. The PagerDuty
    note identifies general gaps in production AI agent deployments; this note
    identifies a concrete architecture decision (where to store prompts and routing
    rules) that can create or close those gaps.

- **Novel**:
  - The **"prompts/routing/config as mutable data → blast radius amplification"**
    architectural risk pattern (Claim 2) is not present in any existing source note.
    It identifies a specific, actionable architecture decision (storing prompts and
    routing rules in application tables vs. governed configuration) that determines
    whether a database compromise becomes an AI behavior change. This is the article's
    most novel contribution.
  - The **"blast radius, not entry vector"** reframing (Claim 3) is a new conceptual
    tool for incident classification. No existing note provides this diagnostic
    heuristic for distinguishing AI-attacks from application-compromises-reaching-AI.
  - The **four-point audit checklist** (Claim 7 / Concrete Artifacts) is a practical,
    citable framework for enterprise assistant security reviews — derived from a
    real incident rather than from theoretical threat modeling. No existing note
    provides a similar checklist grounded in an incident post-mortem.
  - The **McKinsey Lilli incident as a worked case study** is entirely new to the
    corpus. No existing source note covers this incident.
  - The "they will begin as familiar software bugs and end as changes in model
    behavior" prediction (Claim 8) provides a forward-looking thesis that could
    anchor the guide's AI incident response framework — no existing note makes this
    specific prediction about incident-class evolution.

## Guide Impact

- **Chapter 06 (Security & Trust)**: This is the primary destination. Add:
  - A **"Mutable Configuration as Blast Radius Amplifier" subsection** in the
    security architecture section, citing Claim 2. The recommendation: prompts,
    routing rules, retrieval policy, and access-control metadata should be stored as
    governed configuration (with code-review gates and deployment controls), not as
    mutable rows in the application database. This is a specific, citable architecture
    principle derived from an observed incident.
  - The **four-point audit checklist** (Claim 7 / Concrete Artifacts) as a structured
    review framework for enterprise AI assistant security audits. Each bullet maps
    to a vulnerability class: public routes (authentication coverage), JSON-key SQL
    injection (parameterization completeness), BOLA coverage (authorization
    completeness), and mutable config governance (configuration security).
  - The **"blast radius, not entry vector" diagnostic heuristic** (Claim 3) in the
    threat-classification section, as a decision tree: "Is the model being attacked
    (jailbreak/prompt injection), or is the model the interface to an already-compromised
    application?" This reframes the incident response triage question.
  - The **"familiar software bugs → model behavior changes" prediction** (Claim 8)
    as a rationale for cross-team incident response (AppSec + AI infra) rather than
    siloed model-behavior analysis.

- **Chapter 04 (Incident Response / Diagnostics)**: Add a **"Detecting AppSec-origin
  AI incidents"** subsection that uses this case study to establish a diagnostic
  pattern: when an AI assistant's behavior changes unexpectedly (unusual responses,
  retrieval of unauthorized data), check the application layer — exposed endpoints,
  SQL injection detection logs, BOLA analytics — before assuming model-level
  subversion. The "mutable config" architecture check (are prompts/routing rules
  stored in the application database?) should be a standard incident-response runbook
  step.

- **Chapter 02 (Agent Architecture & Threat Model)**: Add the **"prompts as governed
  configuration" principle** (Claim 2) to the security architecture requirements for
  enterprise AI assistants. The threat model should document the decision: if prompts,
  routing rules, and retrieval settings are stored in the application database, the
  threat model must include "database write → behavior change" as a distinct risk
  path, separate from "model jailbreak" and "prompt injection." This risk path
  requires controls at the database layer (SQL injection prevention, BOLA prevention,
  CDC/audit logging) rather than the model layer (guardrails, safety classifiers).

## Extraction Notes

- Source is a single blog post (published 2026-03-10 by Michael D'Angelo, Co-founder &
  CTO of Promptfoo). Read in full via fetched HTML; all direct quotes were extracted
  character-for-character from the article text and verified against the source.
- The article references CodeWall's March 9, 2026 writeup and McKinsey's public case
  studies as external sources. These were not followed for independent verification
  (CodeWall's writeup is behind a registration or paywall; McKinsey's case studies are
  standard public marketing material). The article itself acknowledges this limitation:
  "The exact payloads were not published, so the public record does not independently
  prove every reported row count or every step of exploitation." The specific
  exploitation details are therefore treated as plausible but unverified at the
  individual-query level.
- The article contains no code blocks, terminal transcripts, or YAML/JSON config
  examples. It contains one compact diagram ("diagram showing the AppSec chain on
  the left and the AI-layer impact on the right") whose exact content could not be
  extracted from the HTML. No sub-pages were followed; the article is self-contained
  and links only to general references (CodeWall, The Register, OWASP, Claroty, NVD,
  McKinsey case studies).
- The article has a "Newer post" link to "OpenClaw at Work: Prompt Injection Risks"
  and an "Older post" link to "Promptfoo is joining OpenAI" — these adjacent posts
  were not followed as they are separate articles.
- `confidence_overall` is set to **emerging** following precedent from similar
  Promptfoo incident-analysis notes. The architectural claims (mutable data → blast
  radius amplification) are logical consequences of system design and are high-confidence.
  The specific attack-chain details are second-hand from CodeWall and plausible but
  unverified at the payload level. The audit checklist and forward-looking thesis are
  the author's analysis and recommendations, not empirical findings. The cited
  references (OWASP, Claroty, CVE-2026-25544) are independently verifiable.
- No contradiction with any existing source note was found. The Lilli incident analysis
  supports and extends the jailbreak-vs-injection taxonomy from
  `blog-promptfoo-jailbreaking-vs-prompt-injection.md` rather than contradicting it.
  No contradiction issue was filed. CONTRADICTIONS.md has no open entries and there are
  no open `contradiction`-labeled issues.
