---
source_url: https://simonwillison.net/2026/Jun/5/openai-help-lockdown-mode/
source_type: blog-post
title: "OpenAI Help: Lockdown Mode"
author: Simon Willison
date_published: 2026-06-05
date_extracted: 2026-06-14
last_checked: 2026-06-14
status: current
confidence_overall: settled
issue: "#1174"
---

# OpenAI Help: Lockdown Mode

> Simon Willison's analysis of OpenAI's newly-shipped Lockdown Mode establishes
> a concrete vendor implementation of the exfiltration-leg defense in the "Lethal
> Trifecta" prompt injection attack framework — using deterministic, non-AI-evaluated
> network restrictions rather than model-layer controls to block the final stage
> of data theft.

## Source Context

- **Type**: blog-post (Simon Willison's Weblog, June 5, 2026 — a link post summarizing
  and editorially analyzing OpenAI's help documentation for Lockdown Mode, with
  an embedded quote from OpenAI CISO Dane Stuckey's public tweet. The primary
  technical claims derive from OpenAI's official documentation at
  https://help.openai.com/en/articles/20001061-lockdown-mode and from Stuckey's
  tweet at https://twitter.com/cryps1s/status/2062923575049531422. The OpenAI
  help article returned HTTP 403 during extraction; quotes from it are taken from
  Willison's reproduction of its text in the link post.)
- **Author credibility**: Simon Willison is a widely-followed LLM security practitioner
  and the originator of the "Lethal Trifecta" framing (documented in a June 2025
  article at simonwillison.net/2025/Jun/16/the-lethal-trifecta/). He maintains the
  canonical index of prompt injection incidents at simonwillison.net/tags/prompt-injection/.
  His editorial judgment on what constitutes meaningful versus superficial defenses
  carries significant weight in the practitioner community. He is not an OpenAI
  employee; his assessment is independent.
- **Scope**: Covers only OpenAI's Lockdown Mode feature for ChatGPT — its mechanism
  (network request restriction), its availability (Free/Go/Plus/Pro/Business), its
  explicit limitations (does not block prompt injection itself), its design rationale
  (the Lethal Trifecta), and the intended audience (elevated-risk users, per CISO).
  Does NOT cover: the OpenAI model-layer defenses against prompt injection, other
  ChatGPT safety controls, enterprise API configurations, or how OpenAI implements
  the network restriction technically.

## Extracted Claims

### Claim 1: OpenAI's Lockdown Mode restricts outbound network requests to prevent the final stage of data exfiltration from a prompt injection attack

- **Evidence**: Official OpenAI product description reproduced by Willison from the
  OpenAI help article. The feature was announced in February 2026
  (openai.com/index/introducing-lockdown-mode-and-elevated-risk-labels-in-chatgpt/)
  and rolled out to personal and self-serve business accounts by June 5, 2026.
- **Confidence**: settled (official product description from OpenAI; shipped and
  verifiable in the product)
- **Quote**: "Lockdown Mode is designed to help prevent the final stage of data
  exfiltration from a prompt injection attack by limiting outbound network requests"
- **Our assessment**: "Final stage" is the key phrase: this is explicitly a terminal
  defense, not a complete defense. The framing acknowledges that prompt injection
  may still succeed — Lockdown Mode intervenes at the point where injection would
  convert to data theft. This is an honest and architecturally sound positioning:
  the defense layer is deterministic (network-level restriction) rather than
  probabilistic (model refusing to comply). A successfully injected prompt cannot
  override a network-level egress block.

### Claim 2: Lockdown Mode explicitly does NOT prevent prompt injections from appearing in ChatGPT's processed content — it only limits what a successful injection can do

- **Evidence**: Explicitly stated limitation in OpenAI's help documentation, reproduced
  by Willison. This is a notable admission: the feature has a defined scope that
  stops short of the full attack prevention users might expect.
- **Confidence**: settled (first-party product limitation from OpenAI documentation)
- **Quote**: "Lockdown Mode does not prevent prompt injections from appearing in the
  content ChatGPT processes"
- **Our assessment**: This limitation is as important as the feature itself. Practitioners
  who adopt Lockdown Mode must still treat prompt injection as an assumed risk. The
  feature does not reduce injection success rates — it limits what a successful
  injection can achieve. Two of the three Lethal Trifecta legs (private data access
  and exposure to untrusted content) remain fully present. Only the exfiltration
  path is restricted. A user who believes Lockdown Mode makes them safe from
  prompt injection attacks has misunderstood the feature.

### Claim 3: The "Lethal Trifecta" framework — combining private data access, untrusted content exposure, and an exfiltration path — is the theoretical basis for evaluating why restricting one leg provides meaningful defense

- **Evidence**: Willison links to his own June 2025 article ("The Lethal Trifecta")
  and applies the framework to analyze Lockdown Mode. The trifecta concept is
  his established framing for the most dangerous class of prompt injection
  scenarios.
- **Confidence**: emerging (Willison's own conceptual framework, broadly adopted
  in the practitioner community; not independently empirically validated as a
  complete taxonomy)
- **Quote**: "The Lethal Trifecta occurs when an LLM system has access to all three
  of access to private data, exposure to untrusted content and a way to steal data
  and transmit it back to the attacker"
- **Our assessment**: The trifecta framing is valuable because it is conjunctive:
  all three legs must be present for the attack to succeed. Removing any one leg
  blocks the attack, even if the other two remain fully present. This is the
  security rationale for Lockdown Mode's focused scope: if exfiltration is
  blocked at the network layer, the combination cannot produce a data theft outcome
  regardless of how successfully a prompt injection manipulates the model.

### Claim 4: Restricting the exfiltration vector is the most practical leg to cut — it doesn't reduce the core utility of the LLM system

- **Evidence**: Willison's editorial analysis in the article, consistent with his
  broader Lethal Trifecta work. The reasoning: access to private data is the
  primary value proposition of agentic AI; blocking untrusted content would
  prevent agents from processing web pages, documents, emails (core use cases);
  blocking exfiltration path requires only restricting outbound network capabilities.
- **Confidence**: emerging (Willison's editorial judgment; well-reasoned from
  first principles; not independently quantified)
- **Quote**: (no direct verbatim quote captured for this specific claim; see Our
  assessment for Willison's reasoning as summarized in the article)
- **Our assessment**: This claim is the design heuristic that Lockdown Mode
  instantiates. The three trifecta legs are not equally practical to restrict:
  (a) removing private data access defeats the purpose of the tool; (b) blocking
  all untrusted content makes the system unable to process external information;
  (c) blocking exfiltration network paths requires no sacrifice of core capability,
  since legitimate use cases rarely need ChatGPT to make arbitrary outbound network
  requests during processing. Lockdown Mode's design implicitly validates this
  heuristic by making the network restriction opt-in rather than default.

### Claim 5: Lockdown Mode's mechanism is deterministic — it does not rely on AI evaluation to decide whether a network request is harmful, making it resistant to prompt injection that manipulates model behavior

- **Evidence**: Willison's explicit analysis in the article. He characterizes the
  mechanism as "deterministic" and contrasts it with approaches that depend on
  model evaluation, which can be manipulated by the injection payload itself.
- **Confidence**: emerging (Willison's technical characterization; plausible given
  that network-level egress blocks operate outside the model's decision space; not
  confirmed by OpenAI engineering documentation)
- **Quote**: (the word "deterministic" appears in Willison's analysis; no single
  verbatim sentence containing the full claim was captured)
- **Our assessment**: This is the core security advantage of network-layer controls
  over model-layer defenses: the model cannot instruct a network firewall to allow
  a blocked request. Even a fully compromised model — one that has been successfully
  injected with an exfiltration instruction — cannot override a deterministic
  network-level egress block. This is the environmental control principle from
  `blog-anthropic-how-contain-claude.md` Claim 3 instantiated at the product level:
  the environmental control (network block) provides the guarantee that model-layer
  defenses (refusing to exfiltrate) cannot.

### Claim 6: OpenAI's CISO explicitly positions Lockdown Mode as an opt-in tool for elevated-risk users, with acknowledged functionality tradeoffs that are worthwhile only for high-risk profiles

- **Evidence**: Public tweet by OpenAI CISO Dane Stuckey (@cryps1s, tweet ID
  2062923575049531422), quoted by Willison in the link post. This is the most
  direct first-party signal about OpenAI's intended positioning for the feature.
- **Confidence**: settled (direct public statement from the CISO of the vendor;
  tweet is linked and can be independently verified)
- **Quote**: "Lockdown mode is not meant for everyone. However, for folks who have
  an elevated risk profile - due to who they are, what they work on, or the types
  of data they work with - it's an excellent tool for further securing themselves.
  This has some tradeoffs on functionality and utility, but for these users, the
  tradeoff is worthwhile."
- **Our assessment**: "Not meant for everyone" is the design admission: Lockdown
  Mode trades functionality for security, and OpenAI does not believe the tradeoff
  is worthwhile for most users. This is an unusually candid positioning for a
  security feature from a major AI vendor — it avoids security theater by
  acknowledging the cost rather than claiming the feature is transparent. For
  practitioners: this is a security control that should appear in an elevated-risk
  profile checklist (e.g., journalists, activists, executives, legal professionals,
  healthcare workers), not in default configuration guidance.

### Claim 7: Lockdown Mode is available to personal accounts (Free, Go, Plus, Pro) and self-serve ChatGPT Business accounts — establishing this as a consumer-grade security control, not only an enterprise feature

- **Evidence**: Official OpenAI documentation as reproduced by Willison in the
  link post.
- **Confidence**: settled (official product documentation; availability at time of
  article publication, 2026-06-05)
- **Quote**: "rolling out to eligible personal accounts, including Free, Go, Plus,
  and Pro, and self-serve ChatGPT Business accounts"
- **Our assessment**: The consumer availability (Free tier included) is notable:
  this is not a capability locked behind enterprise agreements. Any ChatGPT user
  can opt into enhanced exfiltration protection. The "self-serve" qualifier for
  Business suggests that fully managed enterprise configurations may have separate
  controls. Practitioners advising individuals (not organizations) on secure
  ChatGPT usage can recommend enabling Lockdown Mode directly.

### Claim 8: The existence of an opt-in Lockdown Mode implies that ChatGPT's default configuration lacks robust exfiltration restrictions — default mode prioritizes functionality over exfiltration defense

- **Evidence**: Logical inference from the product design: if default ChatGPT
  provided strong exfiltration protection, a separate opt-in Lockdown Mode
  would not be needed. Willison's framing implicitly acknowledges this.
- **Confidence**: anecdotal (inference; not directly stated by OpenAI; Willison
  does not explicitly make this claim)
- **Quote**: (no direct quote; see Our assessment)
- **Our assessment**: This inference is structurally sound. An opt-in security
  mode exists because the default mode lacks that security property. The
  functionality tradeoffs the CISO acknowledges (Claim 6) are absent from
  default mode — meaning default mode permits the outbound network requests
  that Lockdown Mode would block. For practitioners assessing ChatGPT risk
  exposure for high-value or sensitive workflows: default ChatGPT should be
  treated as having no exfiltration restriction at the network layer.

## Concrete Artifacts

### Lockdown Mode Feature Summary (from OpenAI documentation via Willison)

```
OpenAI Lockdown Mode — Feature Profile
Source: simonwillison.net/2026/Jun/5/openai-help-lockdown-mode/
        (relaying help.openai.com/en/articles/20001061-lockdown-mode, accessed 2026-06-14)
Published: 2026-06-05

MECHANISM:
  Restricts outbound network requests from ChatGPT sessions.
  Uses deterministic (non-AI-evaluated) network-layer controls.

WHAT IT PREVENTS:
  "the final stage of data exfiltration from a prompt injection attack
   by limiting outbound network requests"

WHAT IT DOES NOT PREVENT:
  "Lockdown Mode does not prevent prompt injections from appearing
   in the content ChatGPT processes"

AVAILABILITY (as of 2026-06-05):
  "rolling out to eligible personal accounts, including Free, Go, Plus,
   and Pro, and self-serve ChatGPT Business accounts"

INTENDED AUDIENCE (per CISO Dane Stuckey):
  "folks who have an elevated risk profile - due to who they are, what
   they work on, or the types of data they work with"

TRADEOFFS (per CISO):
  "tradeoffs on functionality and utility"
  (implied: ChatGPT features relying on outbound network requests are
   restricted or unavailable in Lockdown Mode)

DEFENSE CATEGORY:
  Lethal Trifecta leg 3 (exfiltration vector) — leaves legs 1 and 2
  (private data access and exposure to untrusted content) unchanged.
```

### The Lethal Trifecta Framework (Willison, applied in this article)

```
Source: simonwillison.net/2026/Jun/5/openai-help-lockdown-mode/
        (referencing simonwillison.net/2025/Jun/16/the-lethal-trifecta/)

THE THREE LEGS:
  Leg 1: Access to private data
         (the value of the system — difficult to remove without defeating the purpose)
  Leg 2: Exposure to untrusted content
         (any mechanism by which attacker-controlled text reaches the model)
  Leg 3: Ability to externally communicate / exfiltration path
         (any outbound channel that can carry stolen data to an attacker)

ATTACK CONDITION:
  All three legs must be present simultaneously for a data exfiltration
  attack to succeed via prompt injection.

WILLISON'S QUOTE (from this article):
  "The Lethal Trifecta occurs when an LLM system has access to all three
   of access to private data, exposure to untrusted content and a way to
   steal data and transmit it back to the attacker"

DEFENSE IMPLICATION:
  Removing any single leg blocks the attack.
  Lockdown Mode removes Leg 3 using deterministic network-layer controls.

PRACTICAL PRIORITY:
  Leg 3 (exfiltration) is the most practical to remove without degrading
  system utility, since legitimate use cases rarely require ChatGPT to
  make arbitrary outbound network requests during content processing.
```

## Cross-References

- **Corroborates**:
  - `failure-copilot-cowork-file-exfiltration.md` Lesson 4: "Tool-chaining attacks
    using only legitimate agent capabilities are model-agnostic and require
    environmental (not model-layer) defenses." Lockdown Mode is a concrete
    vendor product implementing exactly this principle: it restricts the
    exfiltration path at the environment layer (network restriction), not
    at the model layer (refusal behavior). The Copilot Cowork failure (Lesson 4)
    diagnosed the need for environmental controls; Lockdown Mode is a shipped
    answer to that need on the OpenAI platform.
  - `blog-anthropic-how-contain-claude.md` Claim 3: "Environmental containment
    should be the primary design priority — model-layer defenses are necessary
    but will never achieve 100% effectiveness." Lockdown Mode's "deterministic"
    mechanism (Claim 5 above) is the concrete product implementation of this
    principle on the OpenAI platform. OpenAI and Anthropic independently arrive
    at the same conclusion: structural environmental controls are more reliable
    than model behavior for exfiltration defense.
  - `blog-anthropic-zero-trust-ai-agents.md` Claim 4: "Prefer a control that
    removes a capability over a control that throttles it." Lockdown Mode removes
    the outbound network capability rather than throttling or monitoring it —
    a direct instantiation of this principle in a shipped product.

- **Extends**:
  - `failure-copilot-cowork-file-exfiltration.md`: That note documents a production
    failure where the absence of network-level exfiltration controls allowed a
    prompt injection to exfiltrate files via email-image channel. The Copilot
    Cowork case established the problem (no architectural exfiltration block);
    this note documents a vendor (OpenAI) shipping a feature that provides
    exactly that architectural block. Together they form a problem-solution pair:
    the Copilot Cowork failure motivates the Lockdown Mode approach.
  - `blog-anthropic-how-contain-claude.md`: That note documents Anthropic's
    containment architecture (gVisor containers, OS-level sandboxes, VM isolation,
    egress controls). This note adds OpenAI's approach to the same problem space —
    establishing that network-level exfiltration restriction is an independently
    arrived-at convergent solution across two leading AI vendors. The Anthropic
    approach is always-on architectural containment; the OpenAI approach is
    opt-in user-controlled restriction. Different deployment philosophy, same
    underlying mechanism.
  - `failure-meta-ai-instagram-account-takeover.md`: That note documents a
    different class of AI security failure (no verification for account operations).
    This note adds context: while Meta failed to implement any exfiltration-path
    restriction, OpenAI is now explicitly addressing this attack surface. Both
    notes, from Simon Willison's blog within two weeks of each other, show the
    AI security landscape evolving rapidly in mid-2026.

- **Contradicts**: None found. The claim that deterministic network-layer controls
  are more reliable than model-layer defenses for exfiltration is consistent
  with all existing corpus notes on agentic security. No contradiction issue filed.

- **Novel**:
  - **First corpus source documenting a shipped consumer AI product that
    explicitly restricts the exfiltration leg of the Lethal Trifecta**: No
    prior corpus note documents a vendor shipping a dedicated feature to block
    data exfiltration via network restriction. This is the first concrete
    product-level answer to the Copilot Cowork failure pattern in the corpus.
  - **"Deterministic" mechanism distinction**: The explicit contrast between
    AI-evaluated defenses (probabilistic, manipulable by injection) and
    deterministic defenses (network-layer, cannot be overridden by model
    behavior) is articulated here for the first time in the corpus as a
    named design dimension.
  - **Opt-in security posture with explicit vendor-acknowledged tradeoff**:
    The CISO publicly acknowledging functionality tradeoffs and scoping the
    feature to elevated-risk users is a new type of security signal in the
    corpus — vendor honesty about scope limitations rather than claiming
    comprehensive protection.
  - **Consumer-grade availability of network exfiltration protection**: Prior
    corpus security notes focus on enterprise/platform-level controls (gVisor
    containers, VM isolation, OS-level sandboxes). Lockdown Mode is available
    on the Free tier, establishing that exfiltration defense is achievable
    at consumer scale and cost.
  - **Lethal Trifecta applied as an evaluation framework for vendor features**:
    This is the first note in the corpus where Willison's Lethal Trifecta
    framework is used to assess a specific vendor's security capability, rather
    than to describe an attack pattern.

## Guide Impact

- **Chapter 03 (Safety and Verification) / Chapter 04 (Security & Safety)**:
  Add Lockdown Mode as the canonical example of the "exfiltration-leg defense"
  pattern. The design principle: when full prompt injection prevention is not
  achievable (and it is not — Claim 2 explicitly states this), restrict what
  a successful injection can do. Frame this as the architectural equivalent of
  "defense in depth at the exfiltration stage." Cite Lockdown Mode's deterministic
  (non-model-evaluated) network restriction as the concrete implementation.

- **Chapter 03 / 04**: Add the explicit limitation of Lockdown Mode (Claim 2)
  to any guide section on ChatGPT security controls. Practitioners must understand
  that enabling Lockdown Mode does not prevent prompt injection — it only limits
  the damage of a successful injection. The guide should state: "Enabling Lockdown
  Mode is a Lethal Trifecta Leg 3 control. It does not address Leg 2 (injection
  surface) or Leg 1 (private data access). Users processing sensitive data with
  untrusted content should apply Leg 1 and Leg 2 controls separately."

- **Chapter 02 (Harness Engineering)**: Add the "deterministic vs. AI-evaluated"
  distinction (Claim 5) as a design axis for harness security controls. Environmental
  controls that are deterministic (network blocks, filesystem sandboxes, egress
  rules) cannot be overridden by model behavior. This is a stronger guarantee than
  model-layer controls (refusal training, classifiers, prompt instructions). When
  designing harnesses that process untrusted content with access to sensitive data,
  prioritize deterministic environmental controls over relying on model behavior.

- **Chapter 03 / 04**: Introduce the Lethal Trifecta framework (Claim 3) as the
  organizing framework for prompt injection threat modeling. The current corpus has
  this framework in the Copilot Cowork failure note and the Zero Trust eBook, but
  it has not been named and made first-class in the guide. This source, coming from
  the framework's originator applied to a specific vendor control, is the ideal
  citation anchor.

- **Chapter 03 / 04 — Elevated Risk Profiles**: Add an explicit list of elevated-risk
  ChatGPT user profiles (Claim 6, from CISO Stuckey) that should enable Lockdown
  Mode: users defined by who they are (journalists, activists, executives, public
  figures), what they work on (sensitive or regulated industries), or what data they
  handle (PII, financial, health, legal). This is the first corpus source with
  vendor-provided segmentation guidance for security controls.

## Extraction Notes

- **Source type**: This is a Simon Willison link post — a short article (~200-300
  words) that links to primary sources and provides editorial commentary. The
  primary technical claims come from OpenAI's help article (HTTP 403 during
  extraction; quotes are from Willison's reproduction) and the CISO's tweet
  (linked, independently verifiable). Willison's own words provide the Lethal
  Trifecta framing and the "deterministic mechanism" characterization.
- **Quote reliability**: All quotes extracted via WebFetch, which uses an AI
  intermediary. The first three quotes (Lockdown Mode description, limitation,
  and availability) appeared consistently across three separate WebFetch attempts
  with different prompts and are likely verbatim. The Stuckey CISO quote was
  labeled "Verbatim" in one fetch and appeared consistently; it is likely accurate
  but the Assayer should verify against the linked tweet. The Lethal Trifecta
  quote similarly appeared consistently.
- **OpenAI help article inaccessible**: The primary linked article
  (help.openai.com/en/articles/20001061-lockdown-mode) returned HTTP 403 during
  extraction. All OpenAI documentation content is taken from Willison's
  reproductions, not from the source article directly. The Assayer should
  attempt to access the help article directly for verification.
- **OpenAI February announcement inaccessible**: The February 2026 announcement
  (openai.com/index/introducing-lockdown-mode-and-elevated-risk-labels-in-chatgpt/)
  also returned HTTP 403. The "Elevated Risk Labels" feature mentioned in the title
  is not covered in this source note; it may contain additional relevant claims.
- **No contradictions found**: This source corroborates the environmental-control-first
  principle across the corpus without introducing conflicting claims. No contradiction
  issue was filed.
- **Lethal Trifecta article not re-extracted**: The referenced June 2025 Lethal
  Trifecta article (simonwillison.net/2025/Jun/16/the-lethal-trifecta/) was fetched
  during cross-reference research but is a separate source not yet in the corpus.
  If a high-value source, it may warrant a separate extraction ticket.
