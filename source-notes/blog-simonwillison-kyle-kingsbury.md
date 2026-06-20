---
source_url: https://simonwillison.net/2026/Apr/15/kyle-kingsbury/
source_type: blog-post
title: "Quoting Kyle Kingsbury: Meat Shields and New ML Boundary Roles"
author: Kyle Kingsbury (quoted by Simon Willison)
date_published: 2026-04-15
date_extracted: 2026-05-25
last_checked: 2026-05-25
status: current
confidence_overall: emerging
issue: "#342"
---

# Quoting Kyle Kingsbury: Meat Shields and New ML Boundary Roles

> Kyle Kingsbury's essay names six new job categories emerging at the boundary
> between humans and ML systems, with the "meat shields" role — humans employed
> to bear accountability for ML failures — as the concept with the most immediate
> organizational and regulatory implications.

## Source Context

- **Type**: blog-post (Simon Willison's Weblog, "quotation" format — April 15,
  2026; single block-quote linking to Kyle Kingsbury's essay "The Future of
  Everything is Lies, I Guess: New Jobs" on aphyr.com/posts/419, which was
  followed per MINER §1 as the substantive linked source. Tags on the Simon
  Willison post: careers, ai, ai-ethics, kyle-kingsbury.)
- **Author credibility**: Kyle Kingsbury (aphyr) is the creator of the Jepsen
  database testing framework — one of the most respected practitioners in
  distributed systems, whose Jepsen analyses are industry-standard references
  for database consistency failures. This essay is analytical commentary, not
  empirical research, but Kingsbury's practitioner authority and rigor are
  well-established. Simon Willison is the creator of Django and runs one of the
  highest-signal AI tooling commentary feeds; his selection of Kingsbury's
  "meat shields" passage as a standalone quotation post is itself a relevance
  signal. Neither author is a vendor promoting a product.
- **Scope**: The Simon Willison page presents one block-quote from Kingsbury's
  essay — the "meat shields" passage. The full Kingsbury essay (aphyr.com/posts/419)
  covers six new job categories at the ML boundary: Incanters, Process Engineers,
  Statistical Engineers, Model Trainers, Meat Shields, and Haruspices. This note
  extracts from both sources; quotes from the full Kingsbury essay are marked
  "(aphyr.com/posts/419)". Does NOT cover: quantitative predictions, salary data,
  organizational implementation advice, or timeline estimates. The essay is part of
  a larger Kingsbury series "The Future of Everything is Lies, I Guess" (eight
  published installments as of April 2026) — adjacent essays on Work, Safety,
  Psychological Hazards, Dynamics, and Information Ecology were not linked from
  the Simon Willison page and were not extracted.

## Extracted Claims

### Claim 1: ML deployment is creating a distinct class of new jobs operating at the boundary between human and ML systems

- **Evidence**: Kingsbury's analytical framing in the essay opening. The structure
  of the essay — six named roles with concrete examples — constitutes evidence for
  the claim; these roles are observable in current job postings, regulatory
  developments, and practitioner reports.
- **Confidence**: emerging (practitioner analysis; consistent with observable trends
  but no empirical survey data cited)
- **Quote**: "As we deploy ML more broadly, there will be new kinds of work. I think
  much of it will take place at the boundary between human and ML systems."
  (aphyr.com/posts/419)
- **Our assessment**: The "boundary roles" framing is analytically useful for the
  guide. Rather than predicting wholesale displacement, Kingsbury identifies a more
  nuanced phenomenon: ML creates new work at the interface between automated and
  human judgment. This is consistent with what the corpus shows in job postings:
  "directing and reviewing agent-written code" (`discussion-hn-agentic-coding-jobs.md`)
  describes exactly a boundary role.

### Claim 2: "Incanters" — prompt specialists who know LLM quirks — will emerge as a distinct professional role, distinct from traditional programmers

- **Evidence**: Concrete enumeration of LLM idiosyncrasies that constitute specialist
  knowledge: ordering bias, context contamination, length degradation, and
  counterintuitive prompt strategies (threats, flattery, commands, false incentives).
  The role is contrasted with traditional programming.
- **Confidence**: emerging (the role exists today under the label "prompt engineer";
  the enumerated quirks are documented in ML research; whether this solidifies into
  a distinct profession or gets absorbed into general engineering practice is unresolved)
- **Quote**: "LLMs are weird. You can sometimes get better results by threatening them,
  telling them they're experts, repeating your commands, or lying to them that they'll
  receive a financial bonus." (aphyr.com/posts/419)
- **Our assessment**: The "Incanter" framing captures something real: prompt
  engineering does require specialist knowledge of model quirks that most programmers
  do not have. However, the guide should treat this as a transitional role — as models
  improve and prompting becomes more systematic (see harness-engineering sources), the
  need for incantation-style workarounds may decrease. The Incanter represents one end
  of a spectrum that the guide's context-engineering chapter (Ch04) already addresses
  from the craft side.

### Claim 3: "Process Engineers" will build quality-control workflows that catch ML errors before they cause harm, particularly in high-stakes professional domains

- **Evidence**: Concrete law-firm example: firms implementing document review workflows
  with deliberately introduced errors to catch both intentional and accidental AI
  mistakes, then integrating with legal research systems and training staff. The
  lawyer-penalty pattern (AI hallucinations submitted as court filings) is cited as
  the problem this role addresses.
- **Confidence**: emerging (the lawyer penalty pattern is documented in multiple real
  cases; the deliberate-error QC workflow is described as an emerging practice, not
  a confirmed widespread norm)
- **Quote**: "Lawyers keep getting in trouble because they submit AI confabulations in
  court" (aphyr.com/posts/419)
- **Our assessment**: The Process Engineer role is the QC-layer institutional response
  to AI unreliability in professional contexts. This connects to Ch03 (Safety and
  Verification) at the organizational level — Process Engineers build the institutional
  workflow, not just the technical check. The deliberate-error insertion technique
  is a concrete artifact worth noting for teams designing AI quality gates.

### Claim 4: "Statistical Engineers" will measure and control ML variability using domain-specific analysis, surfacing performance disparities invisible to aggregate accuracy metrics

- **Evidence**: Specific examples: LLM output is influenced by option ordering; LLMs
  may perform well on English text but "pathologically" on other languages or
  time-series data. Comparison to psychometrics as the discipline for modeling
  human behavioral variability. Option-ordering effects are backed by ML literature.
- **Confidence**: emerging (ordering bias and cross-domain performance disparities
  are documented; "Statistical Engineer" as a named professional role is Kingsbury's
  coinage, not yet an established job-market category)
- **Quote**: "Models will not simply be '95% accurate'. Instead, an ML
  optimizer...might perform well on English text, but pathologically on timeseries"
  (aphyr.com/posts/419)
- **Our assessment**: This claim targets a real failure mode in AI adoption: over-reliance
  on aggregate metrics that mask subgroup performance failures. The Statistical Engineer
  is the practitioner who surfaces hidden failures before they cause harm. For the guide,
  this suggests evaluation harness design (Ch02) must include subgroup and domain
  performance analysis, not just headline accuracy — and that teams need someone with
  the mandate to perform this analysis, not just the tooling.

### Claim 5: "Model Trainers" — subject-matter experts hired to produce training data and evaluations — are being employed at scale under poor working conditions

- **Evidence**: Scale AI and Mercor are cited as employers of large numbers of
  subject-matter specialists. Kingsbury describes postdocs and specialists in
  esoteric fields (e.g., Carolingian Renaissance scholars) being employed to teach
  models specialized knowledge, and quotes what he describes as industry framing of
  the scale. The poor-conditions observation (bossware, low pay, no union) draws on
  documented reporting on training-data labor practices.
- **Confidence**: emerging (Scale AI and Mercor's training-data operations are publicly
  documented; "largest harvesting" is Kingsbury's characterization rather than a
  metric; labor-condition claims are consistent with published reporting)
- **Quote**: "'The largest harvesting of human expertise ever attempted.' Of course
  there's bossware, and shrinking pay, and absurd hours, and no union"
  (aphyr.com/posts/419)
- **Our assessment**: The second sentence is load-bearing: the Model Trainer role, despite
  its importance to model quality, exists under poor labor conditions. For the guide's
  Team Adoption chapter, this raises a talent pipeline question: if model quality depends
  on human expertise harvesting and working conditions are poor, the supply of willing
  experts is at risk. Teams that depend on model quality in specialized domains should
  be aware of this dependency.

### Claim 6: "Meat Shields" — humans employed to bear accountability for ML system failures — are an emerging organizational role driven by the accountability gap between ML systems and legal/social responsibility frameworks

- **Evidence**: Four concrete categories of existing accountability patterns: (1) internal
  review roles (Meta's human content moderators reviewing automated moderation decisions),
  (2) external legal liability (lawyers penalized for LLM-generated false court filings),
  (3) formalized responsibility structures (Data Protection Officers), (4) convenient
  third-party contractors (Buscaglia, named as an example of someone who can be
  "thrown under the bus when the system as a whole misbehaves"). Academic backing via
  Madeline Clare Elish's "moral crumple zone" concept (see Claim 8).
- **Confidence**: emerging (individual examples are documented; "meat shields" as a
  systematic organizational pattern is Kingsbury's forward-looking analysis supported
  by current examples, not yet a documented norm at scale)
- **Quote**: "I think we will see some people employed (though perhaps not explicitly) as
  _meat shields_: people who are accountable for ML systems under their supervision.
  The accountability may be purely internal, as when Meta hires human beings to review
  the decisions of automated moderation systems. It may be external, as when lawyers
  are penalized for submitting LLM lies to the court. It may involve formalized
  responsibility, like a Data Protection Officer. It may be convenient for a company
  to have third-party subcontractors, like Buscaglia, who can be thrown under the bus
  when the system as a whole misbehaves."
  (simonwillison.net/2026/Apr/15/kyle-kingsbury/ — verbatim, confirmed via two
  separate fetches)
- **Our assessment**: This is the highest-value claim in the source. Kingsbury is
  identifying a structural organizational response to a real problem: AI systems cannot
  accept legal or social accountability. The four-category taxonomy (internal review /
  external liability / formalized role / convenient contractor) is analytically useful
  — each represents a different organizational design choice with different implications
  for the humans involved and different risks of accountability misuse. The guide
  should use this taxonomy in Ch05 when discussing team structure for regulated-industry
  AI deployments.

### Claim 7: The structural necessity of meat shields derives from the fact that only humans can provide social redress — apologizing, facing legal consequences, and being motivated by accountability — in ways ML systems cannot

- **Evidence**: Kingsbury's analytical framing for why the meat-shield role is
  structurally necessary, not merely a transitional artifact of imperfect regulation.
  The argument: legal systems and social trust mechanisms are built around human agency
  and motivation; an LLM cannot be sued, imprisoned, or shamed, and cannot feel the
  consequences of its decisions.
- **Confidence**: emerging (the legal accountability observation is correct under
  current law; the social-redress framing is Kingsbury's analysis, not yet a settled
  academic or legal position)
- **Quote**: (no direct quote confirmed verbatim; see paraphrase in Our assessment)
- **Our assessment**: Kingsbury argues that the meat-shield role is not merely a
  transitional workaround for imperfect regulation — it reflects a deeper structural
  gap between AI capabilities and accountability infrastructure. Until AI systems are
  given legal personhood or accountability is otherwise restructured at the legal-system
  level, human intermediaries are structurally necessary for accountability, not just
  convenient. This is a principle-level observation for Ch00: human-in-the-loop is not
  merely a compliance checkbox but a structural requirement for operating AI systems
  within existing accountability frameworks.

### Claim 8: Madeline Clare Elish's "moral crumple zone" concept describes how accountability is systematically concentrated on lower-status, more-vulnerable actors when ML systems fail, shielding system designers

- **Evidence**: Kingsbury cites Elish's academic work directly and describes the
  concept: responsibility flows downward to more-vulnerable, lower-status actors
  while the people who designed and deployed the system are protected. Elish's
  concept was originally developed in the context of human-robot interaction and
  autonomous vehicle failures.
- **Confidence**: settled (Elish's academic work is documented and published;
  Kingsbury's description accurately represents the concept)
- **Quote**: "Madeline Clare Elish calls this concept a moral crumple zone"
  (aphyr.com/posts/419)
- **Our assessment**: This is the academic anchor for the meat-shield pattern. The
  "moral crumple zone" is more precise than "meat shield": it captures the
  directional nature of the accountability transfer — responsibility flows downward
  to the more-vulnerable party. For the guide's Ch05, this framing is useful when
  discussing organizational design: companies can structure AI deployments so that
  accountability concentrates on individual practitioners or easily-scapegoated
  contractors rather than on the designers or decision-makers who chose to deploy the
  system. Practitioners should understand the moral crumple zone dynamic before
  accepting accountability roles in AI deployments.

### Claim 9: "Haruspices" — ML system investigators — will analyze model inputs, outputs, and internal states post-failure to determine why automated systems behaved as they did

- **Evidence**: Concrete examples: healthcare models diagnosing different patient
  groups differently; drone targeting failures resulting in harm; content moderation
  falsely flagging benign images. Analogy to NTSB aircraft accident investigators
  is used to define the scope and rigor of the role. Deployed by ML companies,
  courts, journalists, and agencies like the NTSB itself.
- **Confidence**: emerging (the investigator role already exists in academic ML
  fairness research and incident response; Kingsbury's prediction is that it will
  formalize into a distinct profession at scale)
- **Quote**: "When models go wrong, we will want to know why. What led the drone to
  abandon its intended target and detonate in a field hospital?"
  (aphyr.com/posts/419)
- **Our assessment**: The Haruspex role is the post-hoc accountability mechanism:
  when a meat shield has already taken the consequences, someone must still understand
  what the ML system did and why, to prevent recurrence and to enable accountability
  assignment. This maps to incident response and post-mortem practices discussed
  in `blog-ghaw-fault-investigation.md`, but elevated to a formal professional role
  with NTSB-level rigor. The drone example is significant — it connects ML
  accountability to life-or-death contexts where post-failure investigation is
  already expected to be rigorous and independent.

## Concrete Artifacts

### Kingsbury's Four-Category Meat Shield Accountability Pattern

```
Kyle Kingsbury's taxonomy of accountability structures for ML systems
(aphyr.com/posts/419, "The Future of Everything is Lies, I Guess: New Jobs")
Quoted via simonwillison.net/2026/Apr/15/kyle-kingsbury/

Type 1 — Internal human review:
  Example: Meta hires human beings to review the decisions of automated
           moderation systems
  Structure: Employee who reviews/approves ML outputs; accountable for
             what passes through

Type 2 — External legal liability:
  Example: Lawyers penalized for submitting LLM-generated false citations
           to courts
  Structure: Professional whose license or standing bears the cost of
             ML errors

Type 3 — Formalized responsibility role:
  Example: Data Protection Officer
  Structure: Named role with explicit accountability by regulation or
             organizational policy

Type 4 — Convenient third-party contractor:
  Example: Buscaglia (named as contractor who can be "thrown under the bus
           when the system as a whole misbehaves")
  Structure: External contractor as organizational distance between
             system failure and system designers

Academic framing: "moral crumple zone" (Madeline Clare Elish) — the
structural pattern where accountability is concentrated on lower-status,
more-vulnerable actors while system designers are shielded.
```

### Kingsbury's Six New ML Boundary Roles

```
Kyle Kingsbury's six new ML boundary roles
(aphyr.com/posts/419, "The Future of Everything is Lies, I Guess: New Jobs")

1. Incanters
   - Prompt specialists aware of LLM quirks: ordering bias, context
     contamination, length degradation
   - Framing: speak to Claude instead of working directly with code
   - Key quirk: "You can sometimes get better results by threatening them,
     telling them they're experts, repeating your commands, or lying to them
     that they'll receive a financial bonus"

2. Process Engineers
   - Build QC workflows around ML outputs; integrate with professional systems
   - Example: Law firms inserting deliberate errors into AI documents to catch
     both intentional and accidental mistakes before court submission

3. Statistical Engineers
   - Measure and control ML variability; surface hidden performance disparities
   - Example: LLM choice influenced by option ordering; accurate on English,
     pathological on timeseries or other languages
   - Analogous discipline: psychometrics for modeling human behavioral variability

4. Model Trainers
   - Subject-matter experts providing training data and model evaluations
   - Employed at scale by Scale AI, Mercor; poor working conditions (bossware,
     low pay, no union)
   - Example specialists: postdocs in Carolingian Renaissance history

5. Meat Shields
   - Bear accountability for ML system failures under organizational supervision
   - Structural necessity: LLMs cannot apologize, go to jail, or provide social
     redress
   - Academic framing: "moral crumple zone" (Madeline Clare Elish)
   - Four structural forms: internal review / external liability / formalized role
     / convenient contractor

6. Haruspices
   - Investigate ML system behavior post-failure; analyze inputs, outputs,
     internal states
   - Analogous to NTSB accident investigators
   - Deployed by: ML companies, courts, journalism, government agencies
   - Example cases: healthcare bias, drone targeting failures, content moderation
```

## Cross-References

- **Corroborates**: `discussion-hn-agentic-coding-jobs.md` — The Zapier job posting
  ("directing and reviewing agent-written code, not writing it by hand") is a
  concrete early example of Kingsbury's boundary-role pattern. The Zapier role maps
  most closely to Kingsbury's Process Engineer (building a QC workflow around agent
  output) and Incanter (having "opinions about which models to use for which tasks").
  Both sources agree that AI deployment creates new human roles defined by their
  relationship to AI output rather than to code directly.

- **Corroborates**: `blog-thebatch-ng-aiteam-structure.md` Claim 1 — Andrew Ng's
  observation that engineers are absorbing PM, design, and marketing roles sits alongside
  the Kingsbury taxonomy. The two sources describe different dynamics: Ng addresses
  how existing engineers expand their scope; Kingsbury addresses the distinct specialist
  roles created *because of* AI deployment (Process Engineers, Statistical Engineers,
  Haruspices). The guide should present both: existing engineers become generalists AND
  new specialists emerge at the AI boundary.

- **Corroborates**: `blog-anthropic-compliance-api.md` Claim 4 — The Compliance API's
  explicit exclusion of inference activity from audit logging creates exactly the
  accountability gap that Kingsbury's meat-shield pattern is responding to. Both sources
  independently establish that human intermediaries are currently structurally necessary
  to fill accountability gaps in AI systems. The Compliance API documents the
  infrastructure gap; Kingsbury names the organizational role that fills it.

- **Extends**: `blog-anthropic-kepler-verifiable-ai-financial.md` — Kepler's architecture
  for auditable AI in financial services is one production implementation of what Kingsbury
  would call the Process Engineer and Statistical Engineer roles: building verification
  and measurement infrastructure around AI outputs in a regulated domain. Kingsbury
  provides the organizational-role vocabulary; Kepler provides a production case study
  of what those roles look like in practice for a high-accountability domain.

- **Extends**: `blog-ghaw-fault-investigation.md` — Kingsbury's "Haruspices" role maps
  to the fault investigation workflows documented in the GitHub Agentic Workflows corpus.
  The GHAW source documents technical tooling for agentic fault investigation (CI Doctor,
  Schema Consistency Checker); Kingsbury describes the professional role that would operate
  such tooling at scale and in high-stakes contexts. Together: tooling exists today,
  formalization into a professional role is Kingsbury's prediction.

- **Novel**:
  - **The "meat shields" vocabulary and four-category accountability taxonomy**: No
    existing source note names this pattern or provides this structural breakdown of how
    organizations assign accountability for ML failures. This is the first corpus entry
    directly addressing the organizational mechanics of who bears accountability.
  - **"Moral crumple zones" (Madeline Clare Elish) as academic anchor**: No existing
    source note references Elish's concept. This gives the guide an academic citation
    for the accountability-concentration pattern in AI deployments.
  - **Haruspices as a named post-failure investigation role**: While GHAW fault
    investigation tooling is documented, the framing of model investigation as a distinct
    profession with NTSB-level rigor is new to the corpus.
  - **Full six-role taxonomy of ML boundary work**: Kingsbury's taxonomy is the most
    comprehensive structured breakdown of new AI-adjacent roles in the corpus.
  - **Model Trainer labor-conditions observation**: No existing source discusses the
    working conditions of training-data workers and the dependency this creates for
    model quality.

## Guide Impact

- **Chapter 05 (Team Adoption) — high priority**: The six-role taxonomy should anchor
  a "What new roles does AI deployment create?" section. The guide currently addresses
  engineer:PM ratio compression (`blog-thebatch-ng-aiteam-structure.md`) and
  generalist-engineer roles, but does not address the distinct specialist roles that AI
  creates at its deployment boundaries. Recommend adding: boundary-role taxonomy with
  Kingsbury's six categories, noting which are already visible in job postings (Incanter,
  Process Engineer) and which are emerging (Haruspex, Statistical Engineer).

- **Chapter 05 (Team Adoption) — organizational design decision**: The four-category meat
  shield taxonomy should appear as a framework for teams designing AI accountability
  structures in regulated industries. Teams must consciously choose which accountability
  structure they are creating. Practitioners should understand the "convenient contractor"
  risk (Type 4) before accepting accountability roles in AI deployments.

- **Chapter 00 (Principles)**: The Kingsbury/Elish observation that only humans can provide
  social redress for AI failures is a foundational principle for why human-in-the-loop
  is structurally necessary, not merely a compliance checkbox. Recommend adding this as
  an explicit principle: "AI systems cannot accept accountability; humans in the loop
  are load-bearing, not decorative."

- **Chapter 03 (Safety and Verification)**: The Statistical Engineer role (measuring
  hidden performance disparities across subgroups, languages, domains) should inform
  evaluation harness design. Aggregate accuracy metrics are insufficient; verification
  must include subgroup performance analysis. The guide should specify who performs this
  analysis and what skills they need, not just what tooling to use.

## Extraction Notes

- **Primary source**: Simon Willison's "Quoting Kyle Kingsbury" page
  (simonwillison.net/2026/Apr/15/kyle-kingsbury/) — contains one block-quote from
  Kingsbury's essay. Very short page with no additional Willison commentary beyond
  the quotation format.
- **Followed link**: Kyle Kingsbury's full essay (aphyr.com/posts/419, "The Future
  of Everything is Lies, I Guess: New Jobs") followed per MINER §1 as the substantive
  linked source. All six job categories come from this page. Quotes marked
  "(aphyr.com/posts/419)".
- **Quote verification**: The full "meat shields" block-quote (Claim 6) was confirmed
  verbatim via two separate WebFetch calls to the Simon Willison page, with consistent
  results. Quotes from the aphyr.com article were extracted via WebFetch and confirmed
  via targeted re-fetch; high confidence but noted as secondary source in each claim.
- **Claim 7**: The "only humans can apologize or go to jail" framing was present in
  WebFetch summaries but not confirmed verbatim character-for-character; marked as
  "(no direct quote; see paraphrase in Our assessment)" per MINER §2a.
- **Prior closed PR**: A prior Miner PR (#672, branch `miner/issue-342-r25693862815`)
  was opened and subsequently CLOSED for this issue. This is a fresh extraction.
- **Essay series**: Kingsbury's "New Jobs" essay is one of eight installments in "The
  Future of Everything is Lies, I Guess" on aphyr.com (posts 412–420 as of April 2026).
  Adjacent essays on Work (#418), Safety (#417), Psychological Hazards (#416), and
  Dynamics (#412) were not followed — they were not linked from the Simon Willison page
  and would constitute independent sources warranting separate issues.
