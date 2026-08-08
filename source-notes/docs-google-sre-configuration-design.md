---
source_url: https://sre.google/workbook/configuration-design
source_type: documentation
title: "Configuration Design and Best Practices — SRE Workbook Chapter 14"
author: "Štěpán Davidovič, with Niall Richard Murphy, Christophe Kalt, and Betsy Beyer (Google SRE)"
date_published: 2018
date_extracted: 2026-08-08
last_checked: 2026-08-08
status: current
confidence_overall: settled
issue: "#815"
---

# Configuration Design and Best Practices — SRE Workbook Chapter 14

> The canonical Google SRE treatment of configuration *interface design*: configuration as a human-computer interface for modifying system behavior, the user-centric "fewer knobs" philosophy versus the infrastructure-centric view, static vs. dynamic defaults, mandatory-question minimization, the separate-interface-from-data architecture (DSL/UI compiling to plain JSON/YAML/protobuf), semantic validation and config tooling, per-snippet ownership and change tracking, and the three-property safe-configuration-change framework (gradual deployment, rollback, automatic rollback on loss of operator control). This is the configuration-interface doctrine that governs how model/prompt/agent/gateway configuration should be designed and rolled out — the pre-canary prerequisite for safe config releases.

## Source Context

- **Type**: documentation — Chapter 14 of the Site Reliability Engineering Workbook (O'Reilly, 2018), hosted on sre.google, licensed CC BY-NC-ND 4.0.
- **Author credibility**: Highest available. Štěpán Davidovič is a Google SRE practitioner-author; the chapter is credited with Niall Richard Murphy, Christophe Kalt, and Betsy Beyer (editors of the SRE Book/Workbook series). Published through Google's official SRE publication channel; the next chapter (Ch15, Configuration Specifics, by the same author) covers Jsonnet mechanics. The chapter describes experiences from Google's internal systems and names a worked example (the Canary Analysis Service).
- **Scope**: Covers (a) the definition of configuration as a human-computer interface and its reliability implications; (b) configuration philosophy — user-centric vs. infrastructure-centric views, questions-close-to-user-goals, mandatory vs. optional questions, static vs. dynamic defaults, "escaping simplicity" via optional overrides; (c) configuration mechanics — separating configuration from resulting data, tooling (semantic validation, syntax highlighting, linters, autoformatters), ownership and change tracking, and the three-property safe-configuration-change framework with hermeticity; (d) a worked example (Canary Analysis Service). Does NOT cover configuration language design in depth (deferred to Ch15), deployment-system specifics, or any AI/LLM tooling directly — the principles are evergreen and transferable to LLM-system configuration (prompt/model/agent/gateway config, feature-flag and config rollouts).

## Extracted Claims

### Claim 1: Configuration is "a human-computer interface for modifying system behavior" — a low-overhead way to change system functionality distinct from code changes, and the quality of that interface impacts the organization's ability to run the system reliably
- **Evidence**: The chapter's working definition and the "Configuration and Reliability" section. The reliability impact of a well-crafted config interface is compared explicitly to the impact of code quality on maintainability, with the added risk that a single option change can have dramatic effects and that config "often lives in an untested (or even untestable) environment."
- **Confidence**: settled
- **Quote**: "configuration—which we can loosely define as a human-computer interface for modifying system behavior—provides a low-overhead way to change system functionality." and "The quality of the human-computer interface of a system's configuration impacts an organization's ability to run that system reliably."
- **Our assessment**: The load-bearing definition. It frames config as *interface design*, not incidental implementation — the guide's LLM-ops content should adopt this framing for prompt/model/agent/gateway configuration. The untested-environment point is the key difference from code: config changes often bypass the review/test loop that code changes go through, which is precisely why the safe-apply framework (Claim 12) matters. We buy this fully; it is canonical first-party SRE doctrine.

### Claim 2: A good configuration interface allows quick, confident, testable changes — poor config UX increases mistakes, cognitive load, and learning curve, and config changes may need to be made under significant incident pressure
- **Evidence**: The "What Is Configuration?" and "Configuration and Reliability" sections. Changing a single option can have dramatic effects (the one-bad-firewall-rule example); config lives in an untested environment; "During an incident, a configuration system that can be simply and safely adjusted is essential."
- **Confidence**: settled
- **Quote**: "A good configuration interface allows quick, confident, and testable configuration changes. When users don't have a straightforward way to update configuration, mistakes are more likely." and "changing a single configuration option can have dramatic changes on functionality—for example, one bad firewall configuration rule may lock you out of your own system."
- **Our assessment**: Establishes the reliability stakes of config UX. For the guide, the incident-pressure point is the sharpest: during an LLM incident the operator must be able to flip a prompt/model/flag config safely and confidently — a config system that is hard to adjust during an incident is itself an incident amplifier. The firewall example is the canonical one-option-total-lockout warning.

### Claim 3: The configuration-philosophy ideal is "no configuration at all" — the system auto-detects the correct configuration from deployment/workload/existing config, and the desirable direction is away from many tunables toward simplicity, reducing both the surface area for error and operator cognitive load
- **Evidence**: The "Configuration Philosophy" opening. The NASA-control-room comparison argues that operator training "is no longer feasible for the majority of the industry," and that as system complexity grows, operator cognitive load becomes increasingly important.
- **Confidence**: settled
- **Quote**: "In the following philosophy, our ideal configuration is no configuration at all." and "While this ideal reduces the amount of control we can exercise over a system, it decreases both the surface area for error and cognitive load on the operator."
- **Our assessment**: A design-north-star rather than an achievable target (the chapter says so itself). The "surface area for error" framing is the reliability rationale for auto-configuration that the guide's resource-auto-negotiation content (e.g., auto-scaling, auto-batching) can cite. For LLM ops, "no configuration" maps to sane defaults that auto-adapt to deployment context — the direction of travel the chapter recommends, not a requirement.

### Claim 4: User-centric configuration (fewer knobs — answering config questions is a chore) is favored over infrastructure-centric (more knobs — tune to perfection), and limited configuration options can paradoxically lead to better adoption than extremely versatile software
- **Evidence**: The "Configuration Asks Users Questions" section, which contrasts the two views explicitly. The infrastructure-centric view is described as software that "effectively provides base infrastructure" requiring considerable user configuration. The adoption claim is stated directly, followed by the observation that systems starting infrastructure-centric may move user-centric as they mature by removing knobs.
- **Confidence**: settled
- **Quote**: "Perhaps counterintuitively, limited configuration options can lead to better adoption than extremely versatile software—onboarding effort is substantially lower because the software mostly works "out of the box.""
- **Our assessment**: The core product-design claim of the chapter and the most transferable one to LLM serving platforms (gateways, agent frameworks, prompt-config UIs): a model-serving platform that asks for a small, well-chosen set of knobs will be adopted faster than a maximally tunable one. The user-centric "fewer knobs, the better" vs. infrastructure-centric "more knobs, the better" tension is the same tension guide readers face when exposing config for LLM systems. We buy it as Google's stated experience; the adoption benefit is plausible but unmeasured (no metric given), so it rests on the authority of the source.

### Claim 5: Minimize the number of mandatory configuration questions — convert them to optional questions with safe defaults — because the life of an engineer is "an endless chain of individually small steps" and the principled reduction of those steps dramatically improves productivity
- **Evidence**: The "Mandatory and Optional Questions" section. Mandatory questions must be answered for any functionality (example: who to charge); optional questions improve quality (example: number of worker processes). The conversion path is stated ("instead of requiring the user to define whether an execution should be dry-run or not, we can simply do dry-run by default"). The failure signal for dynamic defaults is explicit: "If a significant portion of configuration users report problems with dynamic defaults, it's likely that your decision logic no longer matches the requirements of your current user base." The mandatory-question-reduction effort is quantified in the worked example (Claim 13).
- **Confidence**: settled
- **Quote**: "In order to remain user-centric and easy to adopt, your system should minimize the number of mandatory configuration questions." and "the life of an engineer is often an endless chain of individually small steps. The principled reduction of these small steps can dramatically improve productivity."
- **Our assessment**: A concrete, actionable design rule: every mandatory config question is a tax on adoption. For LLM systems, this directly prescribes the shape of setup flows (e.g., an LLM gateway shouldn't require the operator to specify model routing, retries, and limits before it will serve — dry-run-by-default, auto-negotiated resources). The dry-run-default example is notable because dry-run is now a first-class safety primitive in the corpus's AI-in-SRE content.

### Claim 6: Defaults can be dynamic rather than static — threads default to the number of execution cores, JVM heap auto-tunes to container memory — so users don't need to be asked; if a significant portion of users report problems with dynamic defaults, the decision logic no longer matches the user base
- **Evidence**: The dynamic-defaults subsection, with two worked deployment examples (threads = cores; JVM heap = container memory). The failure-detection guidance: if "a significant portion of configuration users report problems with dynamic defaults, it's likely that your decision logic no longer matches the requirements of your current user base" — improve the defaults broadly, or let a small fraction set the value manually.
- **Confidence**: settled
- **Quote**: "A computationally intensive system might typically decide how many computation threads to deploy via a configuration control. Its dynamic default deploys as many threads as the system (or container) has execution cores." and "Similarly, a Java binary deployed alone in a container could automatically adjust its heap limits depending on memory available in the container."
- **Our assessment**: The single most directly reusable claim for LLM serving config. Model-serving and gateway configs are full of "how many workers / how much memory / what batch size" knobs that are better auto-negotiated from the deployment context (GPU count, memory, load) than hardcoded. The failure signal — a significant portion of config users reporting problems with the dynamic defaults — is a concrete, testable trigger for revisiting the auto-decision logic. We buy it; the JVM-heap example is real containerization practice.

### Claim 7: Default choice matters because "most users will use the default" — the default is both a chance and a responsibility, and designating the wrong default does a lot of harm (opt-in vs. opt-out organ-donor example); remove optional questions with no clear use case rather than accumulating knobs
- **Evidence**: The defaults subsection cites the organ-donor default-effect research (defaults on opt-out produce dramatically greater donor ratios). The optional-question culling guidance ("You may want to remove these questions altogether. A large number of optional questions might confuse the user, so you should add configuration knobs only when motivated by a real need") and the inheritance-revert advice ("it is useful to be able to revert to the default value for any optional question in the leaf configurations") follow.
- **Confidence**: settled
- **Quote**: "Experience shows that most users will use the default, so this is both a chance and a responsibility. You can subtly nudge people in the right direction, but designating the wrong default will do a lot of harm."
- **Our assessment**: The most important guidance for LLM config defaults specifically: in a 2026 LLM landscape where a model's default temperature, default system prompt, default safety filter, and default timeout are shipped as values, the default *is* the behavior most users get. For the guide, this argues for treating default model/prompt/gateway values as first-class reliability artifacts subject to review — and for the "add knobs only when motivated by a real need" rule as a guard against config bloat in agent frameworks.

### Claim 8: "Escaping simplicity" means supporting power users via optional overrides layered on high-level, user-goal-near defaults — not a lowest-common-denominator default — and optimizing for the sum of hours spent configuring across the organization
- **Evidence**: The "Escaping Simplicity" section. The lowest-common-denominator strategy is rejected because it "impacts everyone" — even simplest use cases must be considered in low-level terms. The tea analogy (configure "hot green tea" then add "steep for five minutes") and the C++/Java-inline-assembly parallel are given. The org-level optimization ("optimizing for the sum of hours spent configuring across the organization") includes decision paralysis, correction time, and slower change due to lower confidence.
- **Confidence**: settled
- **Quote**: "By thinking about configuration in terms of optional overrides of default behavior, the user configures "green tea," and then adds "steep the tea for five minutes." In this model, the default configuration is still high-level and close to the user's goals, but the user can fine-tune low-level aspects."
- **Our assessment**: The escape-hatch pattern is the design that reconciles user-centric defaults with power-user needs — and the model the guide should recommend for LLM config (safe high-level defaults, documented low-level overrides). The "It's useful to think about optimizing for the sum of hours spent configuring across the organization" line is a rare, citable cost model: it counts configuration time as an organizational cost against which every added knob is weighed. The "If you find that more than a small subset of your users need a complex configuration, you may have incorrectly identified the common use cases" line is a sharp diagnostic.

### Claim 9: Separate the configuration interface from the resulting data — infrastructure operates on plain static data (Protocol Buffers, YAML, JSON) while users interact with a higher-level interface (DSL, Jsonnet, or a UI) that compiles to that data; the static data can then be queried/analyzed (e.g., which config parameters are used and by whom)
- **Evidence**: The "Separate Configuration and Resulting Data" section. All user questions "boil down to static information." The high-level interface is "a compilation, similar to how we treat C++ code." The static-data analysis benefit is concrete: "if the generated configuration data is in JSON format, it can be loaded into PostgreSQL and analyzed with database queries," enabling the owner to query "which configuration parameters are being used and by whom."
- **Confidence**: settled
- **Quote**: "To answer the age-old question of whether configuration is code or data, our experience has shown that having both code and data, but separating the two, is optimal." and "As the infrastructure owner, you can then quickly and easily query for which configuration parameters are being used and by whom."
- **Our assessment**: The chapter's resolution of the code-vs-data debate, and directly the architecture the guide should recommend for LLM config rollouts: a high-level prompt/config DSL (or a config UI) that compiles to plain JSON/YAML consumed by the gateway, making the effective config queryable and diffable. The ability to query which configuration parameters are being used and by whom is the auditability prerequisite for deprecating unused model/prompt knobs and for measuring the impact of a bad config option. We buy it as the standard Google config architecture.

### Claim 10: Store provenance metadata about how configuration was ingested (author, source path before compilation) so config authors can be tracked down; avoid tight coupling between the interface data format and the internal data format
- **Evidence**: The metadata subsection: "if you know the data came from a configuration file in Jsonnet or you have the full path to the original before it was compiled into data, you can track down the configuration authors." The coupling warning: you may use an internal data structure that contains consumed config plus implementation-specific data "that never needs to be surfaced outside of the system."
- **Confidence**: settled
- **Quote**: "When consuming the final configuration data, you will find it useful to also store metadata about how the configuration was ingested. For example, if you know the data came from a configuration file in Jsonnet or you have the full path to the original before it was compiled into data, you can track down the configuration authors."
- **Our assessment**: Complements Claim 9 and is the provenance half of incident attribution: when a bad model/prompt config is implicated, you need the origin (author + source path) not just the effective value. For LLM ops, this maps to prompt-version and config provenance tracking (who authored a system prompt, which repo/file it came from). The coupling warning supports keeping the public config schema distinct from internal representation. Settled as a prescription.

### Claim 11: Semantic (not just syntactic) validation can prevent outages — for every possible misconfiguration, ask whether it can be prevented "at the moment the user commits" — and tooling (syntax highlighting, linters, autoformatters) is the difference between "a chaotic nightmare and a sustainable and scalable system"
- **Evidence**: The "Importance of Tooling" section. Semantic-validation examples: "did the user reference a nonexistent directory (due to a typo), or need a thousand times more RAM than they actually have (because units aren't what the user expected)?" The tools list: syntax highlighting, a linter (Pylint example), an automatic syntax formatter (clang-format, autopep8 examples) — which "minimizes relatively unimportant discussions about formatting and decreases cognitive load."
- **Confidence**: settled
- **Quote**: "For every possible misconfiguration, we should ask ourselves if we could prevent it at the moment the user commits the configuration, rather than after changes are submitted."
- **Our assessment**: The commit-time-validation principle is the design requirement behind the guide's config-validation-at-commit content: validate semantics (not just schema) in CI/pre-commit for model/prompt/gateway configs — e.g., reject a prompt referencing a nonexistent model ID or a temperature outside the model's supported range before it ships. The tooling claim ("a chaotic nightmare" vs. "a sustainable and scalable system") is the rationale for treating linters/formatters for config languages as reliability infrastructure, not developer convenience. Settled.

### Claim 12: Each configuration snippet must have a clear owner; configuration must be versioned regardless of how it is ingested (files, web UI, or APIs); and config edits should be logged so that during incident response the full set of config edits in a change can be determined — enabling confident rollbacks and notification of affected parties
- **Evidence**: The "Ownership and Change Tracking" section. Directory-level ownership example ("their directories might be owned by a single production group"), the versioning requirement ("Checking configuration files into a versioning system... is equally important for configuration ingested by web UI or remote APIs"), and the incident-attribution purpose.
- **Confidence**: settled
- **Quote**: "Each configuration snippet for the system should have a clear owner." and "When a system configuration change is suspected as the culprit during an incident response, it is useful to be able to quickly determine the full set of configuration edits that went into the change."
- **Our assessment**: Ownership + versioning + edit-logging is the incident-attribution triad, and the LLM-ops gap is real: prompt/config edits made via a web UI or an agent are exactly the "web UI or remote API" ingestion path the chapter warns must still be versioned. For the guide, this is a hard requirement for model/prompt/feature-flag systems: every effective config must be reconstructible at any point in time, and the change log must be queryable during incidents. Settled.

### Claim 13: For a configuration change to be safe it must have three properties — (1) gradual deployment avoiding an all-or-nothing change, (2) the ability to roll back, and (3) automatic rollback (or at minimum stopping progress) if the change leads to loss of operator control; rollability requires hermeticity
- **Evidence**: The "Safe Configuration Change Application" section. Gradual deployment is tied to "avoid a global all-at-once push" with the Kubernetes rolling-update reference and a cross-reference to Canarying Releases (Ch16). Rollback "can mitigate an outage much more quickly than attempting to patch it with a temporary fix." The loss-of-operator-control requirement is illustrated by the screen-resolution-countdown and firewall-yourself-out examples. Hermeticity: config referencing mutable external resources (e.g., a network filesystem) cannot be rolled back.
- **Confidence**: settled
- **Quote**: "For a configuration change to be safe, it must have three main properties:" and "The ability to be deployed gradually, avoiding an all-or-nothing change" / "The ability to roll back the change if it proves dangerous" / "Automatic rollback (or at a minimum, the ability to stop progress) if the change leads to loss of operator control" and "In order to be able to roll forward and roll back configuration, it must be hermetic. Configuration that requires external resources that can change outside of its hermetic environment can be very hard to roll back."
- **Our assessment**: The single highest-value transferable artifact in the chapter — a three-property acceptance test for any config change, directly applicable to LLM model/prompt/gateway/flag rollouts. Note the third property is the config-specific version of the "Big Red Button / stop-progress" requirement in the corpus: a config change that risks losing operator control (e.g., a gateway config that, once applied, could lock operators out of the gateway) needs an automatic reset. Hermeticity is a non-obvious prerequisite: a prompt config that references an external mutable dataset is not safely rollable. This is the pre-canary prerequisite the Prospector flagged; it should be paired with the canarying-release mechanics note rather than duplicated.

### Claim 14: Configuration design should be purposeful — it "carries aspects of both API and UI design" — not a side effect of system implementation; the worked Canary Analysis Service example spent about a month reducing mandatory questions and finding good defaults, producing a widely adopted system with little need for support
- **Evidence**: The conclusion and the ACM-Queue-referenced worked example. The conclusion states the design requirement directly; the case study gives the concrete effort figure ("about a month") and the outcome ("Because it was easy to use, it was widely adopted internally. We've seen little need for user support") with the honest caveat that "we have not eliminated misconfigurations and user support entirely, nor do we ever expect to."
- **Confidence**: settled
- **Quote**: "Configuration design carries aspects of both API and UI design and should be purposeful—not just a side effect of system implementation." and "When designing this practical internal system, we spent about a month trying to reduce mandatory questions and finding good answers for optional questions. Our efforts created a simple configuration system. Because it was easy to use, it was widely adopted internally."
- **Our assessment**: The worked example is the chapter's proof that the philosophy is applied, not hypothetical — a month of dedicated config-interface effort produced measurable adoption and low support load. For the guide, the "API and UI design" framing is the citable basis for treating config-interface design as an engineering discipline with a dedicated budget. The "we have not eliminated misconfigurations and user support entirely" caveat is an important realism note against config-utopia claims. The adoption/support claims are qualitative (no metrics), so we take the direction as settled and the magnitude as directional.

## Concrete Artifacts

### Artifact A — The three-property safe-configuration-change framework (section "Safe Configuration Change Application", verbatim)

```
For a configuration change to be safe, it must have three main properties:
  - The ability to be deployed gradually, avoiding an all-or-nothing change
  - The ability to roll back the change if it proves dangerous
  - Automatic rollback (or at a minimum, the ability to stop progress) if the
    change leads to loss of operator control
```

Supporting statements (verbatim):
- "Instead, push the new configuration out gradually—doing so allows you to detect issues and abort a problematic push before causing a 100% outage."
- "Rolling back the offending configuration can mitigate an outage much more quickly than attempting to patch it with a temporary fix—there is inherently lower confidence that a patch will improve things."
- "In order to be able to roll forward and roll back configuration, it must be hermetic. Configuration that requires external resources that can change outside of its hermetic environment can be very hard to roll back. For example, configuration stored in a version control system that references data on a network filesystem is not hermetic."

### Artifact B — Dynamic-default examples (section "Mandatory and Optional Questions", verbatim)

```
"A computationally intensive system might typically decide how many computation
threads to deploy via a configuration control. Its dynamic default deploys as
many threads as the system (or container) has execution cores."

"Similarly, a Java binary deployed alone in a container could automatically
adjust its heap limits depending on memory available in the container."
```

### Artifact C — Configuration tooling checklist (section "Importance of Tooling", verbatim-condensed)

```
Semantic validation:
  "did the user reference a nonexistent directory (due to a typo), or need a
  thousand times more RAM than they actually have (because units aren't what the
  user expected)?"
  "we should ask ourselves if we could prevent it at the moment the user commits
  the configuration, rather than after changes are submitted"

Syntax tooling:
  - Syntax highlighting in editors
  - Linter: "Use a linter to identify common inconsistencies in language use."
  - Automatic syntax formatter: "Built-in standardization minimizes relatively
    unimportant discussions about formatting and decreases cognitive load as
    contributors switch projects."
```

### Artifact D — The two configuration views (section "Configuration Asks Users Questions", verbatim)

```
Infrastructure-centric view:
  "It's useful to offer as many configuration knobs as possible. Doing so
  enables users to tune the system to their exact needs. The more knobs, the
  better, because the system can be tuned to perfection."

User-centric view:
  "Configuration asks questions about infrastructure that the user must answer
  before they can get back to working on their actual business goal. The fewer
  knobs, the better, because answering configuration questions is a chore."
```

## Cross-References

### Candidates from miner-related-notes.md (lexical retrieval)

The following candidates from `miner-related-notes.md` were evaluated:

1. **`docs-google-sre-prodcast-03-11-embracing-complexity.md`** (score 0.3333) — **Corroborates** Claim 3 (automation and abstraction don't simplify — they add new layers, "human-machine teaming," that become a job in themselves). The config chapter's dynamic-defaults section warns "Implementing more complexity in the system creates more work for users (e.g., increased cognitive load to read documentation)" and its philosophy section warns operator cognitive load grows with system complexity — the same layer-addition/cognitive-load warning as the complexity note, applied in the configuration domain. Both independently argue that abstraction/complexity has a real human cost. The link is principle-level, not mechanical; the two sources do not overlap on config interface design itself.

2. **`docs-google-sre-eliminating-toil.md`** (score 0.2821) — **Corroborates** Claim 1 (toil = "the repetitive, predictable, constant stream of tasks related to maintaining a service"; cognitive load and learning curve of manual operations). The config chapter's mandatory-question minimization is a toil-avoidance design stance: "the life of an engineer is often an endless chain of individually small steps" is the config-domain restatement of the toil thesis, and every mandatory config question is exactly the kind of manual, repetitive step the toil note's six characteristics describe. Also corroborates Claim 6 (ticket-driven toil is insidious because it "accomplishes its goal") in spirit: the config chapter's "remove optional questions that start without a clear use case" is the same simplify-before-adding complexity argument. See Primary cross-references for the full mapping.

3. **`docs-google-sre-prodcast-03-06-incident-response-tooling.md`** (score 0.2564) — **Corroborates** Claim 12 ("clumsy automation" — automation that increases workload at high-cognitive-load moments is harmful). The config chapter requires that config be "simply and safely adjusted" during incidents (Claim 2 here) — the tooling note's clumsy-automation warning is the same design constraint stated from the incident-response side: at peak cognitive load (an incident), config mechanisms must not add load. Principle-level corroboration; no overlap on config design.

4. **`docs-google-sre-prodcast-03-05-building-reliable-systems.md`** (score 0.2308) — **Dismissed.** Covers database reliability culture, interface-safety for function calls, and simplification-via-deprecation. No configuration-interface-design claims to corroborate or contradict; the "simplification" theme there means turning systems off, not reducing config knobs.

5. **`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md`** (score 0.2308) — **Dismissed.** SLOs as vernacular and bespoke per-service SLO design. No configuration-interface claims; the chapter's config doctrine is orthogonal to SLO design.

6. **`docs-google-sre-creating-production-launch-plan.md`** (score 0.2308) — **Corroborates** Claim 10 (launch controls should be "self-contained runtime configuration change[s]," not server restarts, with all code deployed and verified before launch day). The launch-plan report's preference for config-only launch actions is the deployment-side instance of the config chapter's "low-overhead way to change system functionality" (Claim 1 here) — both treat configuration change as the preferred, cheap, reversible mechanism for changing behavior in production. See Primary cross-references for the mapping.

7. **`docs-google-sre-prodcast-02-08-life-beyond-google.md`** (score 0.2308) — **Dismissed.** Scale shock / org-scale economics of SRE (white-glove fixes vs. tooling, replication norms). No config-interface-design claims.

8. **`docs-google-sre-prodcast-05-04-del-cid-ai-sre.md`** (score 0.2308) — **Dismissed.** AI-for-SRE tagging and golden-data evaluation of agent labels. No configuration-interface claims; its "team-specific tag taxonomies embedded in LLM instructions" is about model prompting, not config design.

9. **`docs-google-sre-prodcast.md`** (score 0.2308) — **Dismissed.** Prodcast index page with episode listings; no substantive claims to cross-reference.

10. **`docs-google-sre-reliable-product-launches.md`** (score 0.2051) — **Corroborates** Claim 17 (server-side config files to enable/disable features and set parameters like sync frequency — "releasing a new version becomes much easier if we don't need to maintain parallel release tracks") and Claim 11 (feature-flag frameworks must automatically handle failure and independently revert each change immediately). The SRE Book's config-file-controlled client behavior is an instance of config-as-low-overhead-change, and the feature-flag reversion requirement corroborates this chapter's safe-config-change properties (gradual + rollback, Claim 13 here). See Primary cross-references for the mapping.

### Primary cross-references (from the Prospector's triage and manual search)

- **Corroborates**:
  - `docs-google-sre-canarying-releases.md` **Claim 4** (in Google's experience a majority of incidents are triggered by binary or configuration pushes) — the config chapter's whole "Safe Configuration Change Application" section exists because config pushes are a dominant incident source; the two chapters are the workbook's paired treatment (Ch14 = safe config apply, Ch16 = canarying). The canarying note's **Claim 5** (a deployment that cannot roll back forces patch-during-outage, prolonging user impact) corroborates Claim 13 here (rollback as a required safe-config property).
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` **Claim 8** (the Batch Platform "follows the principle of convention over configuration so that the user can benefit from sensible defaults rather than specifying every last detail of their setup") — the batch paper independently names the same defaults philosophy as the config chapter's user-centric view (Claims 4-7 here): convention-over-configuration with sensible defaults is the batch-domain implementation of the config chapter's "fewer knobs / defaults are a responsibility" doctrine. Strong independent corroboration from a later (2021) Google SRE paper.
  - `docs-google-sre-ai-engineering-reliable-operations.md` **Claim 14** (Intervening Pull Request Problem — in high-velocity AI SDLC, rely on "aggressive reliance on dynamic configuration and feature flags to instantly disable problematic code paths") — the AI-in-SRE whitepaper makes dynamic configuration and feature flags a first-class safety mechanism for AI-accelerated development, corroborating the config chapter's config-as-low-overhead-change (Claim 1) and its safe-apply framework (Claim 13) as the mechanism behind "instantly disable problematic code paths."
  - `docs-google-sre-prodcast-03-11-embracing-complexity.md` **Claim 3**, `docs-google-sre-prodcast-03-06-incident-response-tooling.md` **Claim 12**, `docs-google-sre-creating-production-launch-plan.md` **Claim 10**, `docs-google-sre-reliable-product-launches.md` **Claims 11 and 17**, `docs-google-sre-eliminating-toil.md` **Claim 1** — see Candidates list above.

- **Contradicts**: None identified, and no contradiction issue filed. The chapter is a design-philosophy/mechanics treatment that agrees with every config-related claim already in the corpus. Potential tensions checked and resolved as conditioning variables rather than contradictions: (a) the chapter's "fewer knobs" user-centric doctrine (Claim 4) vs. the infra-centric power-user needs it itself accommodates via "escaping simplicity" (Claim 8) — that is the chapter's own reconciliation (layered overrides on defaults), not a self-contradiction; (b) the chapter's "defaults are a chance and a responsibility" (Claim 7) vs. the S5E2 SLOs note's "bespoke, artisanally crafted per service" stance (`docs-google-sre-prodcast-05-02-slos-hidalgo-singer.md` Claim 2) — these address different objects (config defaults for broadly-deployed platforms vs. SLO targets for individual services) and neither prescribes the other's domain, so no conflict; (c) dynamic defaults (Claim 6) auto-negotiating resources vs. the corpus's capacity-planning caution against automatic behavior — the config chapter explicitly provides for overriding dynamic defaults when they misfit ("If you need to restrict resource usage, it's useful to be able to override dynamic defaults in the configuration"), which is the same override-and-monitor mechanism the capacity content assumes.

- **Extends**:
  - `docs-google-sre-canarying-releases.md` — the Prospector flagged this as the primary overlap. The canarying chapter (Ch16) is the rollout *mechanics* for gradual config change; this chapter (Ch14) is the *pre-canary prerequisite*: the three-property safe-apply framework (Claim 13) defines what makes a config change canary-able at all (gradual + rollback + auto-stop). The canarying note's guidance on evaluation integration and rollback assumes the config system supports gradual application — this chapter supplies the design requirement. Linked, not duplicated.
  - `docs-google-sre-reliable-data-processing-minimal-toil.md` — extends Claim 10 (dry-run semantics) and Claim 12 (two-phase mutation) by providing the config-side version of safe application (Claim 13 here: gradual, rollback, auto-rollback) and the separate-interface-from-data architecture (Claim 9) that makes config changes dry-runnable and queryable. The batch paper's "convention over configuration" (Claim 8 there) is also the strongest corpus corroboration of this chapter's defaults philosophy.
  - `docs-google-sre-ai-engineering-reliable-operations.md` — extends Claim 4 (mandatory dry-run support for every API) and Claim 14 (dynamic configuration + feature flags as the Intervening-Pull-Request mitigation) with the config-interface design doctrine: the AI-in-SRE paper assumes config/flag infrastructure exists and is safe to change; this chapter specifies how that config should be designed (separate interface from data, provenance metadata, semantic validation at commit, ownership + change logging, three-property safe apply).
  - `docs-google-sre-infrastructure-change-management.md` — extends Claim 15 (the 10-item Preflight Checklist) with the configuration-specific change discipline: ICM covers the organizational planning of large change; this chapter covers the configuration-interface design (ownership, versioning, edit-logging, safe apply) that the preflight-checked changes run under.
  - `docs-google-sre-reliable-product-launches.md` — extends Claim 17 (server-side config files controlling client behavior) and Claim 11 (feature-flag framework requirements) with the config-interface design principles that make flag-driven rollouts safe: separate-interface-from-data (Claim 9), provenance (Claim 10), commit-time validation (Claim 11), and the three-property safe apply (Claim 13).

- **Novel**: Content new to the corpus:
  - **Configuration as a human-computer interface and a reliability concern on par with code quality** (Claims 1-2) — no existing note frames config interface design as a reliability discipline.
  - **The user-centric vs. infrastructure-centric view** (Claim 4, Artifact D) — the explicit "fewer knobs, the better" / "more knobs, the better" dichotomy with the adoption argument.
  - **Mandatory vs. optional question taxonomy and the minimization rule** (Claim 5) — including the "endless chain of individually small steps" productivity rationale.
  - **Static vs. dynamic defaults** (Claim 6, Artifact B) — threads-default-to-cores and JVM-heap-auto-tunes-to-container examples; the "significant portion of users reporting problems" failure signal.
  - **Defaults as "both a chance and a responsibility"** (Claim 7) — with the organ-donor default-effect evidence; the "add knobs only when motivated by a real need" rule.
  - **Escaping simplicity via optional overrides on high-level defaults** (Claim 8) — the power-user escape hatch that avoids lowest-common-denominator config, and the "sum of hours spent configuring" cost model.
  - **Separate-interface-from-data architecture** (Claims 9-10) — DSL/Jsonnet/UI compiling to plain protobuf/YAML/JSON, with queryable config data ("which parameters are used and by whom") and ingestion-provenance metadata.
  - **Commit-time semantic validation + config tooling** (Claim 11, Artifact C) — semantic validation at the moment the user commits; linter/autoformatter/highlighting as reliability infrastructure.
  - **Ownership + versioning + change logging for incident attribution** (Claim 12) — including versioning of UI/API-ingested config and the "determine the full set of config edits" incident-attribution capability.
  - **The three-property safe-configuration-change framework with hermeticity** (Claim 13, Artifact A) — gradual deployment, rollback, automatic rollback/stop-progress on loss of operator control, plus hermeticity as a rollback prerequisite.
  - **The Canary Analysis Service worked example** (Claim 14) — the "about a month reducing mandatory questions" effort figure and the widely-adopted outcome.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability / Release Engineering)**: The most impacted chapter. Add: (a) the three-property safe-configuration-change framework (Claim 13, Artifact A) as a mandatory acceptance test for every model/prompt/gateway/flag config change — gradual, rollback, auto-rollback-or-stop on loss of operator control, and hermeticity (a prompt config referencing an external mutable dataset is not rollable) — and pair it with the canary mechanics from `docs-google-sre-canarying-releases.md` as the rollout layer on top of this pre-canary prerequisite; (b) the separate-interface-from-data architecture (Claim 9) as the recommended design for prompt/model config systems (high-level DSL/UI compiling to plain JSON consumed by the gateway, with queryable effective config) — this is what makes feature-flag/prompt-version rollouts diffable and auditably attributable (Claim 10 provenance); (c) commit-time semantic validation (Claim 11) as the config-validation gate — reject a prompt referencing a nonexistent model ID or an out-of-range parameter before it ships; (d) dynamic defaults (Claim 6, Artifact B) as the model for resource auto-negotiation in serving config (workers/GPU memory/batch size derived from deployment context, overridable, with the "significant portion of users reporting problems" as the revisit trigger).

- **Chapter 04 (Oncall & Toil)**: Add the user-centric config philosophy (Claims 4-5) to the toil-reduction content — every mandatory config question and config knob is a toil source ("the endless chain of individually small steps"), so config-interface design is a toil-avoidance lever; cite `docs-google-sre-eliminating-toil.md` for the shared toil definition. Add the ownership/versioning/change-logging triad (Claim 12) as the incident-attribution mechanism: during a config-caused LLM incident, the full set of config edits in the change must be reconstructible to enable confident rollback.

- **Chapter 03 (Runbooks & Agents)**: Add config ownership/versioning/change-logging (Claim 12) to agent control-plane requirements — config ingested by web UI or APIs (including by agents) must still be versioned and logged so agent-driven config edits are attributable. Add commit-time semantic validation (Claim 11) as a pre-commit hook pattern for agent-runbooks that change prompt/model/config. Add the "escaping simplicity" override model (Claim 8) as the design for agent config surfaces (safe high-level defaults + documented low-level overrides).

- **Chapter 02 (SLOs / Error Budgets / Principles)**: Add Claim 1's definition of configuration as a human-computer interface and the reliability-impact claim, with the "one bad firewall rule can lock you out" example, to the change-management principles (paired with `docs-google-sre-canarying-releases.md` Claim 4 — majority of incidents from binary or configuration pushes). Add the defaults-responsibility claim (Claim 7) to the safe-defaults guidance: defaults are reliability artifacts because "most users will use the default."

## Extraction Notes

- The full chapter at https://sre.google/workbook/configuration-design was fetched and read end-to-end in a single WebFetch. The chapter's linked sibling pages (Ch15 Configuration Specifics, Ch13 Data Processing Pipelines, Ch16 Canarying Releases, SRE Book simplicity, the ACM Queue Canary Analysis Service article) were not followed per the Prospector's guidance — the chapter itself is the substantive source, its cross-links are already covered by existing source notes (canarying, data-processing, eliminating-toil) or are out of scope (Ch15 Jsonnet mechanics; the ACM Queue article is a reference, not required for extraction).
- All quotes were copied verbatim from the fetched chapter text. The three-property safe-change list (Artifact A) is quoted as a contiguous bulleted list; where a sentence carried an inline link or footnote marker (e.g., the "system configuration change" sentence in Claim 12), the quote was trimmed to the contiguous fragment carrying the meaning. No two non-adjacent sentences were spliced into a single quoted passage.
- `date_published` is the Workbook's 2018 publication year (O'Reilly, April 2018). Per the Prospector's triage, this 2018-era source is deliberately treated as evergreen canonical SRE practice via the `sre-workbook` site-crawl seed; the pre-Dec-2025 rejection rule does not apply, and the claims are timeless configuration-design doctrine, mined at `settled` confidence.
- `confidence_overall` is `settled`: the source is the canonical Google SRE Workbook, authored by named Google SRE practitioners, hosted on the official sre.google domain, and the claims are explicit design prescriptions with worked examples (dynamic defaults, Canary Analysis Service). The qualitative adoption/support claims in Claim 14 are directional (no metrics), noted per-claim; this does not reduce the overall grade because the framework claims are prescriptive doctrine, not measured results.
- No contradiction issue was filed (see Cross-References → Contradicts for the three tension points checked and resolved as conditioning variables, and the verification that no open `contradiction`-labeled issues exist).
- Cross-references were verified per MINER.md §4b: every cited note was re-read and each cited claim number confirmed against the actual `### Claim:` headings before writing (canarying-releases Claims 4-5; reliable-data-processing-minimal-toil Claims 8, 10, 12; ai-engineering-reliable-operations Claim 14; infrastructure-change-management Claim 15; reliable-product-launches Claims 11, 17; creating-production-launch-plan Claim 10; eliminating-toil Claim 1; prodcast-03-11 Claim 3; prodcast-03-06 Claim 12).
- All ten candidates from `miner-related-notes.md` are disposed of in the Candidates subsection above (4 cited, 6 dismissed). The candidates file itself is not committed.
- One WebFetch caveat: the fast-model WebFetch of the sre.google page returned the chapter's full text in structured form. Spot-check any high-value quotes (especially Claims 1, 6, 13 and Artifacts A-D) against the live URL if the Assayer wants extra confidence.
