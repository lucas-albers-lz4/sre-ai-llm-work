---
source_url: https://www.cncf.io/wp-content/uploads/2026/06/Identity-and-Access-Management-Whitepaper.pdf
source_type: docs
title: "Identity and Access Management Whitepaper"
author: "CNCF TAG Security and Compliance (20 named contributors/reviewers; p.1)"
date_published: 2026-06-04
date_extracted: 2026-10-21
last_checked: 2026-10-21
status: current
confidence_overall: emerging
issue: "#1819"
---

# Identity and Access Management Whitepaper

> A CNCF TAG Security normative reference architecture for cloud-native identity:
> two patterns (Basic = one implicit cluster trust zone; Advanced = zero-trust,
> every workload a trust boundary), an RFC 2119 requirement checklist, and the
> corpus's first *normative* statement of the two-identity decomposition the
> agent-auth essay only asserted — **workload identity from a SPIFFE SVID over
> mTLS**, **user identity and authorization context in the OAuth access token** —
> plus a citable audit baseline (log every request, never log the token, carry a
> per-request correlation ID, record the authorization decision). It is standards
> guidance with **zero** deployment, benchmark, or incident evidence.

## Source Context

- **Type**: docs (39-page PDF whitepaper, published by CNCF TAG Security and
  Compliance). The issue URL (`https://www.cncf.io/blog/2026/06/04/identity-and-access-management-whitepaper`)
  is only a ~200-word announcement post with a bullet list; the substantive
  artifact is the directly downloadable PDF linked twice from it
  (`https://www.cncf.io/wp-content/uploads/2026/06/Identity-and-Access-Management-Whitepaper.pdf`,
  HTTP 200, no form gate, PDF `CreationDate` 2026-06-01, announced 2026-06-04).
  **`source_url` points at the PDF** — that is what was read and what every quote
  below is drawn from.
- **Author credibility**: the PDF lists 20 named contributors and reviewers
  (Yoshiyuki Tabata, Hiroyuki Wada, Satarupa Deb, Takashi Norimatsu, Kyohei
  Mizumoto, Omri Gazitt, Maia Iyer, Yujia Lin, Eddie Knight, Evan Anderson,
  Brandt Keller, Jennifer Power, Justin Cappos, Marina Moore, John Kjell, Michael
  Lieberman, Jim Bugwadia, Andrew Block, Faseela K, Karena Angell), several of
  whom are maintainers of the standards it cites (Omri Gazitt is an AuthZEN
  author; the paper is "the result of a collaborative effort by the members of the
  CNCF TAG Security and Compliance"). It is anchored to published, independently
  maintained specifications — OAuth 2.0 (RFC 6749/6750) and RFC 9700, OIDC Core
  1.0, RFC 7636/7662/8414/8693/8705/9449, NIST SP 800-63 rev. 4, NIST SP
  800-162, Authorization API 1.0 (AuthZEN), SPIFFE — and no single vendor. It is
  a **normative, consensus-shaped** document, but it is a consensus *document*, not
  field evidence: it contains **no deployment, no benchmark, no metric, no
  incident, no CVE, and no implementation example**.
- **Scope**: authentication and authorization for cloud-native systems, split into
  two reference patterns (Basic, Advanced), each with a requirements section
  (common / workload #1 / workload #2 / OIDC OP / PDP / SPIFFE), two end-to-end
  request flows (stateful and stateless workloads), an actor table, privacy
  principles, and a glossary. It is explicitly *not* about IdP/IAM product
  design, authorization-policy management, user-managed authorization, async or
  long-running processing, message protocols, or **agent-oriented protocols
  (MCP, A2A)** — see Claim 1, which is the single most important boundary the
  guide must respect when citing this source.

## Extracted Claims

### Claim 1: The whitepaper explicitly excludes agent protocols (MCP, A2A) and asynchronous/long-running processing from its scope, while stating that its authentication and authorization principles are "intended to be reusable for agent-based systems" — so it must not be cited as agent-protocol guidance
- **Evidence**: §1.1 "Audience & Scope" exclusion list, plus footnote 8, which
  states the exclusion and the reusability claim in the same breath. §1.1 also
  narrows the paper to "HTTP-based protocols such as REST APIs and gRPC, as well
  as synchronous request-response patterns" and to "system-level authorization
  evaluated at runtime using Policy Enforcement Points (PEPs) and Policy Decision
  Points (PDPs)". (The exclusion sentence continues past a footnote marker with
  "legacy protocol support, such as raw TCP socket communication"; the quoted
  fragment below stops before the marker.)
- **Confidence**: settled (the document states its own scope boundary in
  explicit terms, twice — once in prose, once in a footnote).
- **Quote**: "Protocols that are not mentioned in this document include directory synchronization (e.g., SCIM), privileged access management (PAM), role engineering, on-premises access control systems, message protocols (e.g., AMQP, MQTT), agent-oriented or agent-to-agent interaction protocols or specifications (e.g., MCP, A2A)" / "While MCP and A2A are considered out of scope in this white paper, the authentication and authorization principles described here are intended to be reusable for agent-based systems."
- **Our assessment**: Buy the boundary and keep it attached to every citation of
  this source. A guide that says "CNCF's IAM whitepaper covers agent auth" would
  be citing a document that says the opposite. The correct form is: this is
  *cloud-native workload* IAM, and the agent case is explicitly anticipated but
  not specified. The second exclusion is easy to miss and matters for LLM ops:
  the paper says nothing about asynchronous or long-running processing, which is
  exactly the shape of most agent jobs and most batch inference. It also excludes
  authorization *policy management* — so it says nothing about how you author,
  review, or version policy, only how the decision is made and enforced.

### Claim 2: The paper's definition of "identity" explicitly includes automated agents as first-class subjects of authentication and authorization decisions — agent protocols are out of scope, but agents are in scope as subjects
- **Evidence**: §1 "Introduction" definition paragraph, and the Table 1 actor
  taxonomy, which lists a "Non-human actor" row (workloads or devices) with the
  risks "Workload impersonation, lateral movement".
- **Confidence**: settled (explicit definitional statement in the source).
- **Quote**: "In this white paper, the term “identity” explicitly includes both human identities and non-human entities, such as workloads, services, and automated agents, which are treated as first-class subjects in authentication and authorization decisions."
- **Our assessment**: This is the load-bearing sentence for a guide about agents,
  and it is stronger than the corpus's existing position. Google's SRE guidance
  (`docs-google-sre-ai-engineering-reliable-operations`, Claim 4) says agent
  identities must be "distinct from humans, strongly authenticated"; Lin Sun's
  essay argues agent identity and principal identity are two different things.
  This paper puts automated agents inside the *definition of identity* for the
  whole cloud-native IAM domain, which is the standards-body version of the same
  position. Two limits worth stating: the paper's "non-human" category is
  "workloads, services, and automated agents" — it does not distinguish an
  autonomous agent from a CronJob, so the guide should not read it as
  agent-specific design; and "first-class subjects" is a *scope* statement, not a
  design rule — it says an agent must be authenticated and authorized, not how.

### Claim 3: The paper's core contribution is a two-pattern selection axis — Basic (the Kubernetes cluster is one implicit trust zone, authentication and authorization applied at the perimeter) versus Advanced (zero-trust, every workload is its own trust boundary) — with a threat-model/mechanism comparison table
- **Evidence**: §2.3.1 "Rationale for Basic and Advanced Patterns", the Table 2
  comparison (reproduced verbatim in Concrete Artifacts), and the two pattern
  requirement sections (§3, §4). The paper also states the selection criteria:
  Basic suits "systems with limited external exposure or sensitivity"; Advanced
  "SHOULD be used for systems handling sensitive data, public-facing
  environments, or situations where the number of users is uncontrolled".
- **Confidence**: emerging (a normative architectural recommendation with no
  deployment evidence; the two patterns are proposed, not validated).
- **Quote**: "The Basic Pattern provides a minimal security baseline suitable for systems with limited external exposure or sensitivity. It treats the Kubernetes cluster as a single implicit trust zone, applying authentication and authorization primarily at the perimeter." / "The Advanced Pattern adopts a zero-trust approach, treating each workload as its own trust boundary and protecting against internal threats such as lateral movement and privilege escalation."
- **Our assessment**: The corpus has no such axis. It has a *placement* axis
  (where does enforcement live — gateway vs network boundary vs policy-as-code)
  and a *depth* axis (how many permission levels does the gateway resolve — see
  `docs-litellm-gateway-auth-reference`, Claim 7). It does not have a
  **trust-boundary granularity** axis: "is the cluster one trust zone, or is
  every workload one?" That is the question a platform team actually asks when
  deciding how much identity plumbing to build, and Table 2 answers it as a
  diffable list. Note the honest caveat the paper itself supplies: for regulated
  systems it says a full profile "such as FAPI, SHOULD be considered instead of
  selectively extending this pattern" — i.e. do not approximate FAPI by
  extending the Advanced pattern.

### Claim 4: The two identities are carried in two different artifacts — workload identity in the SPIFFE SVID presented over mTLS, user identity and authorization context in the OAuth access token — and the paper makes "both" the basis of the authorization decision ("dual-subject authorization")
- **Evidence**: §4.2.2 Stateful Workload #1 Requirement 3 and §4.2.3 Stateless
  Workload #1 Requirement 3 (Advanced pattern), the Advanced end-to-end flow
  step 5, and §4.5 PDP Requirement 2. The same split appears in the Basic
  pattern's optional token-exchange path (§3.2.3 Requirement 4) but is only
  *mandatory* in the Advanced pattern.
- **Confidence**: settled (the mechanism is stated unambiguously and is a direct
  restatement of OAuth/SPIFFE semantics); the security *benefit* is normative,
  not measured.
- **Quote**: "In this pattern, the SVID establishes the identity of the calling workload via mTLS, while the access token carries user identity and authorization context. This separation allows authorization decisions to be based on both the workload and the end user." / "This also enables the PDP to apply authorization policies based on workload identity in addition to user identity, supporting dual-subject authorization in the advanced pattern."
- **Our assessment**: This is the highest-value claim in the document for this
  corpus, and it is the same decomposition Lin Sun's essay argued for
  (`blog-cncf-agent-auth-lawyers-day-in-court`, Claim 6) — but where that note
  had a *slogan* ("An agent is not the user") and an unresolved checklist item
  ("Carry principal identities across requests"), this paper has the concrete
  artifact split: **which token carries which identity**, and the rule that the
  decision uses both. The corpus has never recorded that mapping. Note the
  asymmetry worth preserving: in the Advanced pattern the split is mandatory
  ("MUST use received access tokens for subsequent workload calls", "Including
  the internal access token in the API call is mandatory"), while in the Basic
  pattern token exchange is explicitly optional ("MAY exchange external access
  tokens for internal access tokens"). So the two-identity discipline is a
  *pattern-selection* consequence, not a universal.

### Claim 5: Authorization decisions must be delegated to a Policy Decision Point (NIST SP 800-162 P*P architecture) — and the PEP/PDP placement differs by pattern: PEP at the perimeter in Basic, PEP in every workload in Advanced
- **Evidence**: Basic Common Requirement 9 ("MUST adopt the NIST SP 800-162
  P*P architecture"), Basic Workload #1 Requirement 1 ("MUST delegate
  authorization to PDP"), Basic Workload #2 Requirement 6 ("MAY delegate
  authorization to PDP"), Advanced Workload #2 Requirement 6 ("MUST delegate
  authorization to PDP"), and the component-placement rules in §2.2.6/§2.2.7.
  The paper is explicit that the delegation is a *separation* requirement, not a
  centralization requirement.
- **Confidence**: settled (normative requirement text, stated identically in
  both patterns where it applies).
- **Quote**: "MUST delegate authorization to PDP." / "Note that this does not mean that a centralized policy engine is recommended and a distributed policy engine is not, but rather that one PDP functionality SHOULD exist within a Kubernetes cluster." / "In the basic pattern, workloads at the perimeter of the Kubernetes cluster SHOULD incorporate PEP functionality, and workloads that communicate only within the Kubernetes cluster MAY incorporate PEP functionality. In the advanced pattern, all workloads SHOULD incorporate PEP functionality."
- **Our assessment**: Read carefully, this is *not* the same claim as "put policy
  in the gateway", and the guide should not collapse them. The requirement is
  that authorization *logic* be separable from *application* logic ("This is to
  separate authorization logic from application logic and to enforce
  authorization"), and that the PEP — which in an agent gateway is the gateway —
  call out for a decision. The guide's existing Ch06 rule (gateway-side tool
  authorization) is the PEP half; this paper adds the requirement that the
  *decision* not live inside the request-handling code. Two consequences for the
  guide: (a) the corpus's existing OPA-via-MCP design
  (`blog-cncf-cloud-native-agentic-ai-security-platform`, Claim 3) is
  structurally a PDP even though the source never uses the word; (b) the Basic
  pattern explicitly permits *no* authorization at all on internal workloads
  ("not all workloads require authorization, and you MAY enforce authorization
  only if you want") — so a "standards-compliant perimeter" is *not* the same as
  "every workload is authorized", and the guide's audit-trail rule must not be
  read as being satisfied by perimeter-only enforcement.

### Claim 6: Authorization must be enforced at three granularities — function level, object level, and object property level — and the paper cites OWASP API Top 10 as the reason
- **Evidence**: Basic Common Requirement 8 (the requirement is not restated in
  §4, so it applies to both patterns). The rationale sentence names the source.
- **Confidence**: settled (normative requirement with an explicit rationale).
- **Quote**: "MUST implement authorization at the function level, the object level, and the object property level." / "This is to address broken authorization at the function, object, and object property levels, which are highly rated in the OWASP Top 10 API Security Risks 2023."
- **Our assessment**: This is the normative counterpart of the guide's existing
  red-team checklist. Ch06's "Function-calling authorization" currently sources
  the `rbac`/`bfla`/`bola` split to a red-teamer's probe taxonomy
  (`blog-promptfoo-red-team-gemini`, Claim 9) — an *attack* taxonomy. This
  paper supplies a *defense* taxonomy with the same three levels and a different
  authority (OWASP API Top 10 via the TAG). The guide can now say the three
  levels are both what you probe for and what you must enforce, and note that
  the third level (object property) is the one the corpus's gateway material
  does not cover at all — `docs-litellm-generic-guardrail-api`, Claim 5
  documents argument validation and redaction on `tool_calls`, but no
  property-level authorization of the object being touched.

### Claim 7: The audit baseline is a three-part MUST — log every request, never log the access token (or PII), carry a unique identifier per request, and record the authorization decision applied to that request — and the PDP must log every decision together with its input
- **Evidence**: Basic Workload #1 Requirement 2 and Workload #2 Requirement 1
  (identical text), Basic PDP Requirement 2, and Advanced PDP Requirement 2.
- **Confidence**: settled (normative requirement text, stated consistently in
  three places).
- **Quote**: "MUST log all requests." / "This is to enable investigation in the event of a security incident. Sensitive information, such as access tokens, MUST not be logged. The log MUST contain a unique identifier for each request (generate one if one does not exist) to allow for more efficient investigation. The log MUST also record the authorization decision applied to the request." / "MUST log all authorization decisions along with their input." / "Note that sensitive information such as Personally Identifiable Information (PII) MUST not be logged. Note that the log SHOULD contain the unique identifier from the PEP to allow for more efficient investigation."
- **Our assessment**: This is the most directly usable artifact in the document —
  a citable, normative audit baseline that answers a question the corpus keeps
  circling. Ch06's current rule is "Log the full agent decision trail — which
  tools were called, which MCP servers were consulted, what sub-agents were
  invoked", which says *what* to log but not the mandatory fields or the
  prohibition. This paper supplies four: request coverage, a per-request
  correlation ID (generate one if absent), the applied decision, and a
  never-log-the-token rule. The per-request ID requirement is the concrete
  counterpart to `docs-litellm-a2a-agent-gateway`, Claim 2 (trace grouping is a
  forwarding obligation, not a gateway guarantee), and the "record the
  authorization decision" requirement is the field that
  `docs-promptfoo-enterprise-audit-logging`, Claim 5 says is missing
  from a real product's schema. One caveat: the requirement is scoped to
  *requests through the PEP* and to the *PDP's* decisions — it is not an
  agent-decision-trail requirement (what the model reasoned), so it does not
  replace Ch06's trail rule; it constrains it (don't log the token).

### Claim 8: The PDP must be unreachable from outside the cluster, and in the Advanced pattern the PDP must authenticate the PEP with an SVID — so the decision component is itself a zero-trust participant
- **Evidence**: Basic PDP Requirement 1 ("MUST not be accessible at the network
  level from outside the Kubernetes cluster") and Advanced PDP Requirement 2
  ("MUST authenticate the PEP using an SVID"), plus the Advanced Common
  Requirement 1 (TLS for all components, including intra-cluster).
- **Confidence**: settled (normative requirement text).
- **Quote**: "MUST not be accessible at the network level from outside the Kubernetes cluster." / "MUST authenticate the PEP using an SVID." / "This is to minimize the implicit trust zone and to make authentication mandatory between PEP and PDP, just like any other workload, following the zero-trust network architecture concept."
- **Our assessment**: This closes a loop the corpus left open. The corpus's
  enforcement-layer sources all argue that enforcement must live *below* the
  model and *inside* the trust boundary — `blog-cncf-network-boundary-ai-agents-nginx-otel`,
  Claim 1 (the boundary must be architectural) and Claim 4 (network control is
  not intent control); `blog-cncf-cloud-native-agentic-ai-security-platform`,
  Claim 3 (the verdict comes from OPA, called over MCP). What none of them says
  is what the *verdict component* owes in return: it must not be reachable from
  outside the cluster, and the caller of the verdict must be authenticated. That
  is the availability/authority trade the guide never states: a PDP that is
  network-exposed becomes an attack surface that can affect authorization
  decisions — the exact failure mode the corpus documents for gateway
  fail-open defaults (`docs-litellm-a2a-agent-permissions`, Claim 1).

### Claim 9: The PDP is expected to implement ABAC or ReBAC rather than RBAC, with role explosion named as the reason — and the two models are explicitly not mutually exclusive
- **Evidence**: Basic PDP Requirement 4 (the requirement is not restated in
  §4.5, so it applies to both patterns), including the selection guidance for
  each model and the "not mutually exclusive" note in Requirement 5.
- **Confidence**: settled (normative recommendation with a stated rationale).
- **Quote**: "SHOULD adopt ABAC (Attribute-Based Access Control) or ReBAC (Relationship-Based Access Control) as the authorization model." / "Note that implementing fine-grained authorization with RBAC is difficult and MAY result in role explosion." / "Note that these models are not mutually exclusive."
- **Our assessment**: The corpus's gateway material resolves permissions as
  *lists* — a key's agent list, a team's agent list, access groups
  (`docs-litellm-a2a-agent-permissions`, Claims 1–4), i.e. RBAC in exactly the
  shape this paper warns about. This paper supplies the named alternative and
  the reason: attribute-based (subject, resource, action, environment) or
  relationship-based (ownership, hierarchy, group membership, sharing)
  decisions, with "role explosion" as the failure mode of the list-based
  approach. That is a better answer to the corpus's documented six-level MCP
  permission hierarchy (`docs-litellm-gateway-auth-reference`, Claim 7) than
  adding a seventh level would be. The paper also notes in the same requirement
  that the two models are not mutually exclusive, and that some implementations
  combine relationship-based and attribute-based conditions inside one policy
  framework — the parenthetical, which is why that clause is summarized here
  rather than quoted (the source renders the hyphenated compound across a line
  break). Note the strength difference: the paper says SHOULD, not MUST, and it
  says nothing about how such a policy is authored or versioned — the corpus's
  own policy-as-code notes cover that half
  (`blog-cncf-policy-engine-offline-production-fidelity`, Claim 6).

### Claim 10: The PEP↔PDP interface is expected to be the standard one — AuthZEN (Authorization API 1.0) — and the PDP may cache both policies and decisions, with staleness named as the risk in sensitive environments
- **Evidence**: Basic PDP Requirement 3 (standardized APIs to PEPs, AuthZEN
  alignment) and Requirements 6–7 (caching policies and decisions, with the
  "highly sensitive environments" caveat). AuthZEN is listed in §1.3 as one of
  the cited standards, with two of its three authors among the paper's named
  contributors/reviewers.
- **Confidence**: settled (normative requirement text; the AuthZEN interface
  itself is a published OpenID Foundation specification).
- **Quote**: "SHOULD provide standardized APIs to PEPs." / "This is to maintain interoperability between PEPs and PDP, and PDP SHOULD expose PEP–PDP interfaces aligned with Authorization API 1.0." / "MAY cache authorization decisions." / "Note that in highly sensitive environments, you SHOULD consider disabling caching entirely or tightly constraining it to reduce the risk of stale cached information."
- **Our assessment**: Two useful things here. First, AuthZEN gives the guide a
  *named* interface for the gateway→decision call, which it currently leaves
  implicit — the corpus's only concrete gateway→verdict contract is LiteLLM's
  `mcp_jwt_signer` guardrail (`docs-litellm-gateway-auth-reference`, Claim 4),
  a signed JWT, not a decision request. Second, the caching caveat is the
  availability/staleness trade-off the corpus documents for guardrails
  (`docs-litellm-generic-guardrail-api`, Claims 8–10) but never for *policy
  decisions*: a cached allow-decision is an authorization that outlives the
  state that justified it. That is a fail-open-by-time mechanism the guide does
  not currently name.

### Claim 11: Four privacy principles govern identity handling — data minimization (with `sub` as an opaque non-PII identifier), purpose limitation, right to erasure, and exposure limitation for tokens, logs, and policy inputs
- **Evidence**: §1.5 "Privacy Principles", quoted in full in Concrete Artifacts.
  The `sub` requirement names the specific claim and the specific alternatives it
  must not be.
- **Confidence**: settled (principles stated with specific, checkable
  requirements).
- **Quote**: "Data minimization: Systems SHOULD avoid storing personally identifiable information (PII) unless strictly necessary. For example, the `sub` claim in OIDC and OAuth tokens SHOULD use opaque, non-PII identifiers rather than user-chosen login names or email addresses." / "Exposure limitation: Systems that process identity-related data, including tokens, logs, and policy inputs, SHOULD limit unnecessary exposure of such data to prevent unauthorized disclosure."
- **Our assessment**: Directly constrains agent prompt/log handling, which is
  where the corpus's audit-trail rule is weakest. "Exposure limitation" names
  three surfaces — *tokens, logs, and policy inputs* — and "policy inputs" is
  the one that matters for LLM ops: a gateway that forwards a request (or its
  tool arguments) to a policy engine is forwarding identity-bearing data to a
  new destination. The `sub`-must-be-opaque rule is a one-line, citable
  requirement against putting user emails into tokens or audit records, and it
  pairs with the corpus's existing PII-handling caveat in
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry`, Claim 8. The erasure
  principle also supplies a mechanism the corpus lacks: because the identifier
  is opaque, deleting the mapping between identifier and individual satisfies
  erasure "without requiring changes to downstream authorization systems".

### Claim 12: Client authentication to the OpenID Provider is a pattern-dependent requirement — client ID and secret in Basic (with stronger methods explicitly permitted) and SPIFFE SVID in Advanced, where the SVID must be an X.509 certificate or a JWT
- **Evidence**: Basic Stateless Workload #1 Requirement 1 and Stateful Workload
  #1 Requirement 1 (the confidential-client requirement), Advanced Stateful
  Workload #1 Requirement 1 and Advanced Stateless Workload #1 Requirement 1,
  plus §4.6/§4.7 for the SVID issuance and delivery requirements.
- **Confidence**: settled (normative requirement text).
- **Quote**: "MUST perform client authentication to OIDC OP with an SVID." / "Note that the SVID MUST be in the form of an X.509 certificate or a JWT token." / "MUST perform client authentication to OIDC OP with a client ID and client secret." / "Note that you MAY use stronger client authentication methods, such as private_key_jwt using an asymmetric key pair or tls_client_auth/self_signed_tls_client_auth using a client certificate rather than client_secret_post using a client ID and client secret, based on the workload’s security requirements."
- **Our assessment**: Two things the guide should carry. First, the *shape* of
  the requirement — how the inbound caller authenticates to the identity
  provider is itself a pattern-dependent architectural decision, not a config
  detail, and the Basic pattern's allowance of `private_key_jwt` or
  `tls_client_auth` sits in between "static secret" and "SVID" for teams that
  cannot yet issue SVIDs. Second, note that the Basic pattern's default is
  still a *shared static secret* — `client_secret_post` — which is exactly the
  long-lived-credential class the corpus's supply-chain notes treat as a
  primary risk (`blog-cncf-securing-cicd-credentials-verification`, Claims 3–5:
  minimal permissions, `persist-credentials: false`, no long-lived signing
  keys). The whitepaper's own §1.2.1 recommendation — "the avoidance of
  long-lived credentials further reduce risk" — is the line to quote. The
  Advanced pattern's SVID requirement is the same recommendation made binding.

### Claim 13: Token hygiene is specified as a set of MUSTs — shortest practical access-token lifetime, sender-constrained tokens (DPoP or OAuth 2.0 Mutual-TLS) mandatory in the Advanced pattern, authorization code flow with PKCE S256 only, and short-lived single-use authorization codes whose reuse triggers revocation of all tokens issued from that code
- **Evidence**: Basic Common Requirement 6 (authorization code flow only) and
  Requirement 7 (PKCE, S256), Basic OIDC OP Requirement 4 (token issuance and
  management), Advanced OIDC OP Requirement 1 (sender-constrained tokens).
- **Confidence**: settled (normative requirement text).
- **Quote**: "MUST support only the authorization code flow for OIDC authentication." / "Authorization codes MUST be short-lived (SHOULD be maximum 60 seconds for enhanced security contexts such as FAPI), single-use only, and cryptographically secure (generated using a CSPRNG with high entropy and resistance to prediction)." / "When using PKCE, clients MUST use the S256 code challenge method. The OIDC OP MUST enforce the use of the S256 code challenge method to prevent downgrade attacks." / "Access Token: MUST have the shortest practical lifetime necessary for the use case to minimize the window of exposure if compromised." / "Access tokens and refresh tokens MUST be bound to external OAuth clients using DPoP or OAuth 2.0 Mutual-TLS to prevent unauthorized or illegitimate parties from using leaked or stolen tokens."
- **Our assessment**: The replay clause is the notable one and is not in the
  corpus: the OIDC OP "SHOULD treat it as a potential replay attack and revoke
  all tokens that were issued in response to that code" — i.e. replay of one
  authorization code invalidates the whole token family, not just the code. For
  an agent gateway that holds long-lived credentials for many users, that is a
  revocation-propagation requirement, and the corpus has no equivalent. The
  sender-constraint requirement is the standards version of the corpus's
  "declare, don't infer" instinct applied to tokens: if a token is stolen, it
  must still be unusable without the client's key.

### Claim 14: Workload identity has a bootstrap problem the paper names explicitly — before an SVID exists, mTLS is impossible, so the Workload Endpoint must be identified by platform attestation or a pre-shared join token — and SVIDs must be rotated automatically
- **Evidence**: §4.7 SPIFFE Workload Endpoint / SVID Delivery Mechanism
  Requirements 1–6 (including the bootstrap clause in Requirement 4), §4.6 SPIFFE
  Signing Authority Requirements 3, 5 and 6 (attestation-based issuance;
  automated rotation; trust-bundle distribution).
- **Confidence**: settled (normative requirement text; the bootstrap mechanism
  is left implementation-specific by the paper, which says so).
- **Quote**: "During initial bootstrap, the SPIFFE Workload Endpoint MUST use implementation-specific identification mechanisms such as platform-specific attestation, pre-shared join tokens, or other secure bootstrapping methods (as mTLS is not possible without an existing SVID)." / "MUST manage cryptographic keys securely and implement automated SVID rotation." / "The delivery mechanism MAY use the SPIFFE Workload API, CSI-based mechanisms such as the SPIFFE CSI Driver, SPIFFE Helper, Envoy SDS, or other implementation-specific methods."
- **Our assessment**: Two corpus-relevant observations. First, this is the same
  class of problem the corpus already documents for secrets: ESO's own bootstrap
  is an in-cluster self-signed CA issued by cert-manager
  (`blog-cncf-secret-sprawl-external-secrets-operator`, Claim 10) — a trust
  bootstrap problem with the same shape and the same "who issued the first
  credential" hole. Naming it here means the guide can talk about *identity
  bootstrapping* as a first-class operational concern rather than an
  implementation detail. Second, the enumeration of delivery mechanisms is
  useful because it is not mesh-only: "SPIFFE Helper, Envoy SDS" means a
  deployment can obtain SVIDs without a sidecar mesh — which lines up with the
  corpus's existing mesh-free agent topology
  (`blog-cncf-cloud-native-agentic-ai-security-platform`, Claim 2).

### Claim 15: The paper's own scope is one Kubernetes cluster and one trust domain — multi-cluster and cross-trust-domain federation are explicitly out of scope — and there must be one logical OIDC Provider per trust domain
- **Evidence**: §2.3 "Overall Picture" scope note, §2.2.1 (OIDC OP), §2.2.7
  (PDP), §3.4 OIDC OP Requirement 1, and the glossary definitions of "Trust
  Domain" and "Trust Bundle".
- **Confidence**: settled (explicit scope statements).
- **Quote**: "Multi-cluster deployments and cross-trust domain federation are intentionally out of scope for this white paper, even though the presented patterns can be extended to support those architectures." / "MUST ensure that only one logical OIDC OP exists within a single trust domain." / "In this white paper, a trust domain refers to the SPIFFE Trust Domain, which also serves as the trust boundary for OIDC and OAuth token issuance and validation."
- **Our assessment**: Read this before citing the source in a multi-cluster
  guide. The paper's trust model is one cluster = one trust domain = one
  logical OIDC OP, and it explicitly declines to extend to cross-trust-domain
  federation "even though the presented patterns can be extended". Two things
  the guide can use: the glossary's definition that the SPIFFE trust domain
  *is* the OIDC/OAuth issuance-and-validation boundary (so a trust domain is
  not a Kubernetes concept you can pick arbitrarily), and the requirement that
  exactly one logical OIDC OP exist per trust domain — a single-authentication-
  authority rule that is stronger than most multi-tenant deployments actually
  satisfy.

## Concrete Artifacts

All blocks below are reproduced from the PDF at `source_url` (page numbers given
in each attribution). Table cells are listed row by row with the cell text
unchanged; table layout is the only thing that changed.

### Table 2 — Basic and Advanced pattern threat models and security mechanisms (p.13, verbatim cell text)

```
Pattern                       | Basic                                    | Advanced
Threats Addressed             | External threats such as unauthorized     | External threats, and internal threats such
                              | access and impersonation at the perimeter.| as lateral movement and privilege escalation.
Protection - TLS protection   | Mandatory at the perimeter               | Mandatory for all components
Protection - mTLS between     | Not mandatory                            | Mandatory
workloads                     |                                           |
Protection - Multi-factor     | Not mandatory                            | Mandatory
authentication                |                                           |
Protection - Authorization    | Mandatory                                | Mandatory
code flow with PKCE           |                                           |
Protection - Access APIs with | Mandatory for APIs at the perimeter      | Mandatory for all APIs including internal APIs
access tokens                 |                                           |
Protection - Access token     | Mandatory                                | Mandatory
validation                    |                                           |
Protection - Delegation of    | Mandatory at the perimeter               | Mandatory for all workloads
authorization to PDP          |                                           |
```

Attribution: "Identity and Access Management Whitepaper", §2.3.1, Table 2:
"Basic and Advanced pattern threat models and security mechanisms".

### Basic Pattern end-to-end flow (p.14, §2.3.2, use case 1 — stateful workload)

```
5. Call w/o access token:
The browser sends a request to workload #1 using a session identifier such as a cookie, without
including an access token.
6. Issue ID token and access token:
Workload #1, acting as the OIDC RP, initiates the OIDC authorization code flow to request an ID
token and an access token. The OIDC OP issues these tokens after successful authentication and user
consent. Workload #1 validates the issued ID token before the Delegate authorization step.
7. Delegate authorization:
Workload #1, acting as the PEP, sends the user identity (from the session, or access token) together
with the requested resource and action to the PDP. The PDP returns an authorization decision, which
workload #1 enforces.
8. Call w/ access token (optional):
Workload #1 makes API calls to workload #2. Adding the access token to the API call is optional.
If the access token is included, workload #2 acts as the OAuth RS and validates the access token.
9. Delegate authorization (optional):
If the access token is included, workload #2, acting as the PEP, sends the user identity (from the
access token) together with the requested resource and action to the PDP. The PDP returns an
authorization decision, which workload #2 enforces.
```

Attribution: same paper, §2.3.2 "Basic Pattern", Figure 3-1. Steps 1–4 (the
browser→workload #1 request, the OIDC OP's authentication of the user, and the
RP/OP redirect) appear on the preceding page of the flow and are not reproduced.

### Advanced Pattern end-to-end flow (pp.16–17, §2.3.3, use case 1 — stateful workload)

```
1. Issue SVID:
This step represents a setup phase that occurs independently of the per-request flow described
below. The SPIFFE Signing Authority issues SVIDs, which are delivered to each workload through
the SPIFFE Workload API exposed by the local SPIFFE Workload Endpoint. This enables mutual
TLS (mTLS) authentication within the cluster. The SVID establishes the workload identity of workload
#1 and workload #2 via the mTLS connection. Note that the communication between the SPIFFE
Signing Authority and the SPIFFE Workload Endpoint is implementation-specific and outside the
scope of the SPIFFE specification.
2. Call w/o access token:
The browser sends a request to workload #1 using a session identifier such as a cookie, without
including an access token.
3. Issue ID token and access token:
Workload #1, acting as the OIDC RP, initiates the OIDC authorization code flow to request an ID
token and an access token. The OIDC OP issues these tokens after successful authentication and user
consent. Workload #1 validates the issued ID token before the Delegate authorization step.
4. Delegate authorization:
Workload #1, acting as the PEP, sends the user identity (from the session, or access token) together
with the requested resource and action to the PDP. The PDP returns an authorization decision, which
workload #1 enforces.
5. Call w/ internal access token w/ mTLS:
Workload #1 makes API calls to workload #2 using the internal access token and mTLS based on the
SVID. Including the internal access token in the API call is mandatory. Workload #2 acts as the OAuth
RS and validates the internal access token. In this pattern, workload identity is obtained from the
SVID, while user identity and authorization context are carried in the internal access token.
6. Delegate authorization:
Workload #2, acting as the PEP, sends the user identity (from the access token) together with the
requested resource and action to the PDP. The PDP returns an authorization decision, which
workload #2 enforces.
```

Attribution: same paper, §2.3.3 "Advanced Pattern", Figure 4-1. The stateless
variant (Figure 4-2, p.18) differs only in that the external access token is
issued directly to the API client and step 5 becomes "Exchange to internal access
token", which the paper marks non-optional in the Advanced pattern.

### Workload #1 common requirements — logging (p.20, §3.2.1, Basic; identical text in §3.3 Workload #2 Requirement 1)

```
1. MUST delegate authorization to PDP.
This is to separate authorization logic from application logic and to enforce authorization.
2. MUST log all requests.
This is to enable investigation in the event of a security incident. Sensitive information, such as
access tokens, MUST not be logged. The log MUST contain a unique identifier for each request
(generate one if one does not exist) to allow for more efficient investigation. The log MUST also
record the authorization decision applied to the request.
```

Attribution: same paper, §3.2.1 "Common Workload #1 Requirements".

### PDP requirements — Basic (p.24, §3.5)

```
1. MUST not be accessible at the network level from outside the Kubernetes cluster.
This is to eliminate the attack surface for attacks that could affect authorization decisions.
2. MUST log all authorization decisions along with their input.
This is to enable investigation in the event of a security incident. Note that sensitive information such
as Personally Identifiable Information (PII) MUST not be logged. Note that the log SHOULD contain
the unique identifier from the PEP to allow for more efficient investigation.
3. SHOULD provide standardized APIs to PEPs.
This is to maintain interoperability between PEPs and PDP, and PDP SHOULD expose PEP–PDP
interfaces aligned with Authorization API 1.0.
4. SHOULD adopt ABAC (Attribute-Based Access Control) or ReBAC (Relationship-Based
Access Control) as the authorization model.
This is to implement fine-grained authorization at the function, object, and object property levels. Note
that implementing fine-grained authorization with RBAC is difficult and MAY result in role explosion.
When selecting between ABAC and ReBAC, consider the following:
i. ABAC is well-suited when authorization decisions depend primarily on attributes of subjects,
resources, actions, and environmental context (e.g., time of day, location, risk score,
classification level).
ii. ReBAC is well-suited when authorization decisions depend primarily on relationships between
entities (e.g., ownership, organizational hierarchy, group membership, document sharing).
5. Note that these models are not mutually exclusive. Some implementations combine relationship-based
and attribute-based conditions within a single policy framework.
6. MAY cache policies and information.
This is to improve performance. Note that in highly sensitive environments, you SHOULD consider
disabling caching entirely or tightly constraining it to reduce the risk of stale cached information.
7. MAY cache authorization decisions.
This is to improve performance. Note that in highly sensitive environments, you SHOULD consider
disabling caching entirely or tightly constraining it to reduce the risk of stale cached information.
```

Attribution: same paper, §3.5 "PDP Requirements". (The source's line-wrapped
hyphenated compounds — "relationship-based" in Requirement 5 — are rendered
here as the page reads them.)

### PDP requirements — Advanced (p.28, §4.5)

```
1. MUST encrypt sensitive information, such as Personally Identifiable Information (PII) when stored.
This is to reduce the risk of unauthorized or unintended disclosure of sensitive information due to
attacks, misconfigurations, or operational errors.
2. MUST authenticate the PEP using an SVID.
This is to minimize the implicit trust zone and to make authentication mandatory between PEP and
PDP, just like any other workload, following the zero-trust network architecture concept. This also
enables the PDP to apply authorization policies based on workload identity in addition to user identity,
supporting dual-subject authorization in the advanced pattern.
```

Attribution: same paper, §4.5 "PDP Requirements".

### Privacy principles (p.9, §1.5)

```
• Data minimization: Systems SHOULD avoid storing personally identifiable information (PII) unless
strictly necessary. For example, the `sub` claim in OIDC and OAuth tokens SHOULD use opaque,
non-PII identifiers rather than user-chosen login names or email addresses.
• Purpose limitation: Identity information SHOULD be used only for authentication, authorization,
and auditing purposes directly related to the operation of the system.
• Right to erasure: When opaque identifiers are used, deleting the mapping between the identifier
and the individual MAY support user deletion requests without requiring changes to downstream
authorization systems.
• Exposure limitation: Systems that process identity-related data, including tokens, logs, and policy
inputs, SHOULD limit unnecessary exposure of such data to prevent unauthorized disclosure.
```

Attribution: same paper, §1.5 "Privacy Principles".

### Workload identity bootstrap (p.30, §4.7 Requirement 4)

```
4. (When deployed separately from SPIFFE Signing Authority)
MUST use secure communication with the SPIFFE Signing Authority.
This is to protect workload identity requests and responses from interception or tampering.
Communication security varies depending on the phase. During initial bootstrap, the SPIFFE
Workload Endpoint MUST use implementation-specific identification mechanisms such as
platform-specific attestation, pre-shared join tokens, or other secure bootstrapping methods
(as mTLS is not possible without an existing SVID). After obtaining an initial SVID, the SPIFFE
Workload Endpoint MUST use mTLS for subsequent communications with the SPIFFE Signing Authority to
provide mutual authentication and prevent spoofing.
```

Attribution: same paper, §4.7 "SPIFFE Workload Endpoint / SVID Delivery Mechanism
Requirements".

### Table 1 — actor definition and their interaction (p.8, §1.4)

```
End user        | External users such as customers
               | Participate in runtime authentication flows when accessing applications
               | Impersonation, credential theft
Internal user   | Internal users such as support or operations staff
               | Access applications or APIs that are not exposed to external users
               | Privilege misuse, insider threats
Administrator   | Users who manage policies or system configuration
               | Perform management and configuration tasks such as configuring identity federation,
               | client registration, and authorization policies
               | Misconfiguration, over-privileged access
Non-human actor | Workloads or devices
               | Interact with the system through service-to-service authentication and
               | authorization mechanisms
               | Workload impersonation, lateral movement
```

Attribution: same paper, §1.4 "Actors", Table 1: "Actor definition and their
interaction".

## Cross-References

**Candidates from `miner-related-notes.md` (all ten listed paths evaluated; two
cited, eight dismissed):**

- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**:
  retail/gaming SRE practice, SLO granularity, platform migration; no identity,
  authorization, or trust-boundary content.
- `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` —
  **cited** (Corroborates / Extends): Claim 2 (cert-manager per-agent identities
  with mTLS at each agent's own transport) is the practical instance of this
  paper's workload-identity half (Claim 4); Claim 3 (OPA policies invoked by the
  reviewer agent over MCP for a deterministic verdict) is a PDP in everything but
  name, and this paper supplies the requirements that component is missing
  (Claim 8: network isolation from outside the cluster, and PDP-side
  authentication of the PEP; Claim 10: ABAC/ReBAC rather than list-based
  permissions). This paper also lists mesh-free SVID delivery mechanisms
  (Claim 14), which is the same deployment choice that note makes.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
  **dismissed**: imperative vs declarative change workflows; the shared "policy
  as a reviewed artifact" theme is too loose to be an evidential cross-reference.
- `source-notes/docs-google-sre-on-call.md` — **dismissed**: on-call practice,
  pager budget, alert hygiene; no identity or authorization content.
- `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **cited**
  (Corroborates): Claim 5 (a 13-field record schema carrying "no source-IP,
  user-agent, request-id, or session attribution of any kind") is precisely the
  gap this paper's logging requirement closes — a per-request unique identifier
  and the applied authorization decision are MUSTs, not fields you may omit.
  Claim 2 (data-plane operations "tracked separately" with no named destination)
  is the product-side instance of this paper's "MUST log all requests".
- `source-notes/blog-cncf-agent-doc-access-tool-mix.md` — **dismissed**:
  documentation access and tool-mix product design; no identity or
  authorization content.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  taxonomy and reduction practice; unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch coordination and checklist practice; unrelated.
- `source-notes/docs-google-sre-team-lifecycles.md` — **dismissed**: SRE org
  design and adoption sequencing; unrelated.
- `source-notes/docs-google-sre-ai-engineering-reliable-operations.md` —
  **cited** (Corroborates): Claim 4 ("agent identities must be distinct from
  humans, strongly authenticated, on-demand") is Google's version of this
  paper's Claim 2 (automated agents as first-class subjects of authn/authz) and
  Claim 12 (SVID-based client authentication). This paper adds the *mechanism*
  and the *two-subject* form of the distinction that Google's line leaves
  implicit.

**Additional cross-references found by searching `source-notes/` beyond the
candidate list:**

- **Corroborates**:
  - `blog-cncf-agent-auth-lawyers-day-in-court.md`, Claim 6 (principal identity
    is a *separate* identity from agent identity) — this paper states the same
    decomposition normatively and, crucially, states *which artifact carries
    which identity* (Claim 4). Claim 5 of that note ("the system needs to know
    exactly which agent is making the request") is the workload-identity half,
    and this paper's Advanced pattern makes it mandatory via mTLS/SVID.
  - `blog-cncf-agent-auth-lawyers-day-in-court.md`, Claim 11 (the proposed stack
    is SPIFFE + cert-manager + Istio + agentgateway) — this paper independently
    mandates SPIFFE SVIDs as the workload-identity substrate (Claims 4, 12, 14)
    and the mesh-free delivery options ("SPIFFE Helper, Envoy SDS"), but it
    never names cert-manager; its issuance model is a SPIFFE Signing Authority
    inside a Trust Domain (Claim 15). Recorded as a difference in issuance
    model, not a conflict.
  - `blog-cncf-network-boundary-ai-agents-nginx-otel.md`, Claim 1 (the boundary
    must be "a property of the architecture, not a policy we hope the
    application respects") and Claim 4 (network control is not intent control)
    — this paper's PEP/PDP split is the same argument at the authorization
    layer, and Claim 8 adds the obligation the network-boundary note cannot
    supply: the decision component itself must be unreachable from outside the
    trust boundary.
  - `blog-cncf-4-body-problem-sre-context.md`, Claim 4 ("Every agent action
    requires a durable decision trace") — this paper's logging requirement
    (Claim 7) is the standards-specified, field-shaped version of the same
    requirement: per-request identifier, applied decision recorded, tokens
    excluded.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`, Claim 8
    (prompt/response capture "dramatically accelerates root-cause
    investigation but requires PII handling") — this paper's privacy
    principles (Claim 11) are the normative statement of that caveat:
    data minimization, opaque `sub`, exposure limitation for tokens, logs, and
    policy inputs.
  - `docs-litellm-a2a-agent-permissions.md`, Claim 7 (MCP's permission hierarchy
    extends to End-user / Agent / Org while A2A resolves only Key and Team) —
    this paper's ABAC/ReBAC requirement (Claim 9) gives the *shape* of the
    fine-grained model the corpus is reaching for, and names "role explosion" as
    the cost of the list-based approach that Claims 1–4 of that note document.
  - `docs-litellm-gateway-auth-reference.md`, Claim 4 (the `mcp_jwt_signer`
    zero-trust guardrail signs every outbound tool call with a short-lived
    RS256 JWT and publishes a JWKS endpoint) — the corpus's only concrete
    gateway→backend cryptographic-identity surface, and a partial instance of
    this paper's "MUST encrypt all communications between all components using
    TLS" (Advanced Common Requirement 1). Note the difference in kind: the
    paper mandates mTLS with an SVID, which is mutual authentication by
    construction, where a bearer JWT is verifiable but not sender-constrained.
  - `docs-google-sre-ai-engineering-reliable-operations.md`, Claim 5 (Actus as a
    decoupled actuation control plane / safety gateway for autonomous changes) —
    structurally the same placement argument as this paper's PEP/PDP separation
    (Claim 5): the safety verdict comes from a dedicated deterministic
    component, not from the acting model.
  - `docs-litellm-a2a-agent-gateway.md`, Claim 3 (the caller's virtual key and
    end-user ID are not propagated to the backend agent — re-propagation is a
    manual obligation via `extra_headers`) — the corpus's clearest field
    evidence for the gap this paper's two-identity split is designed to close
    (Claim 4): in the Basic pattern the internal access token carrying user
    identity is explicitly optional, and where it is used the downstream
    workload must "MUST use received access tokens for subsequent workload
    calls" to keep the principal's identity intact across the hop.
- **Extends**:
  - `blog-linsun-pod-deployment-unit-ai-agent.md`, Claim 18 (the article's open
    questions are identity ownership, policy attachment point, ownership/quotas,
    and observability) — this paper answers two of the four at the protocol
    level: identity ownership is a SPIFFE Trust Domain with a Signing Authority
    (Claim 15), and the policy attachment point is the PEP (perimeter in Basic,
    every workload in Advanced — Claim 5). It does not answer the multi-tenancy
    or ownership question.
  - `blog-linsun-sandboxing-agent-not-enough.md`, Claim 3 ("necessary, but not
    sufficient") — this paper is the standard-document version of the layer
    sandboxing leaves uncovered: who the workload is (SVID), who it acts for
    (access token), and which decision authorized the request (PDP).
  - `blog-cncf-secret-sprawl-external-secrets-operator.md`, Claim 10 (in-cluster
    cert-manager bootstrap of the ESO→Bitwarden TLS trust) — the same
    trust-bootstrap class as this paper's SVID bootstrap clause (Claim 14):
    something must be trusted before the first credential exists.
  - `blog-cncf-policy-engine-offline-production-fidelity.md`, Claim 6 (offline
    policy testing must be "identical to what runs in the cluster") — this paper
    covers the other half of the policy lifecycle (what the decision component
    must provide: interface, model, isolation, logging) but explicitly excludes
    policy authoring and management (Claim 1), so it complements rather than
    duplicates that note.
- **Contradicts**: none filed, and none warranted. Three tensions were examined
  and each fails the MINER §4a bar ("materially opposes an existing source
  note's claim on the same topic" and "both claims would lead to different
  guide advice"):
  1. **"Gateway enforcement" vs "decision in a PDP".** The guide's Ch06
     gateway-side enforcement rule (`docs-litellm-generic-guardrail-api`, Claim
     5; `docs-litellm-a2a-agent-permissions`, Claim 1) and this paper's
     "MUST delegate authorization to PDP" (Claim 5) are not opposed: in the
     paper's model the gateway *is* the PEP and enforces the decision the PDP
     returns. The paper adds a requirement the guide lacks (the decision logic
     must not live inside application logic) but denies nothing the guide
     asserts. The nearest thing to a real conflict is the Basic pattern's
     allowance that internal workloads need no authorization at all ("not all
     workloads require authorization, and you MAY enforce authorization only if
     you want") — but that is a *pattern-selection* consequence and a scope
     difference from a guide rule that is scoped to tool-enabled agents, i.e.
     the conditioning-variable case §4a explicitly excludes.
  2. **Mesh vs no mesh.** `blog-cncf-agent-auth-lawyers-day-in-court`, Claim 10
     pairs the gateway with a mesh; `blog-cncf-cloud-native-agentic-ai-security-platform`,
     Claim 2 argues mesh-free; this paper requires mTLS but explicitly lists
     mesh-free SVID delivery mechanisms. Three sources, three deployment
     choices on one axis — a difference in deployment choice, already recorded
     as such in the corpus.
  3. **Bearer JWT vs mTLS.** `docs-litellm-gateway-auth-reference`, Claim 4
     documents a shipping gateway that proves itself to the MCP server with a
     short-lived RS256 JWT, where this paper's Advanced pattern requires mTLS
     with an SVID. Different mechanisms for adjacent jobs (a gateway asserting
     itself to a downstream server, versus general workload mutual
     authentication); the paper does not assert that a JWT is illegitimate, and
     the corpus note does not assert that mTLS is unnecessary. Complementary,
     not opposed.
  `CONTRADICTIONS.md` was checked (it contains no entries) and all open
  `contradiction`-labeled issues were listed: the 18 open contradictions cover
  promptfoo and LiteLLM documentation conflicts (telemetry, audit-log access
  coverage, tool_choice mappings, cost maps, caching minimums, routing) and
  **none** covers IAM, PEP/PDP, SPIFFE, or identity decomposition, so no new
  contradiction issue was warranted. The closest existing item is #1597
  ("promptfoo audit-log 'access' coverage: page frames the feature as forensic
  access information ... vs an event taxonomy with zero read/access events"),
  which this source *strengthens* rather than duplicates: it supplies an
  external normative baseline for the same gap (MUST log every request; MUST
  record the authorization decision applied to it — Claim 7). That issue
  already exists and was not re-filed.
- **Novel** (new to the corpus):
  - The corpus's first **normative (RFC 2119) requirement checklist** for
    cloud-native identity, and the first source whose content is a *diffable
    standard* a platform team can check itself against — Basic §3 / Advanced §4
    read as two requirement lists to run against a deployment.
  - The **Basic-vs-Advanced pattern selection axis** (cluster-as-one-trust-zone
    vs every-workload-a-trust-boundary) with a threat-model/mechanism
    comparison table. The corpus has placement and depth axes for enforcement;
    it has no trust-boundary-granularity axis.
  - The **artifact-level two-identity split**: workload identity in the SVID
    over mTLS, user identity and authorization context in the access token, and
    the requirement that the decision be based on **both** ("dual-subject
    authorization"). The corpus had the decomposition as an essay thesis with an
    unresolved "carry principal identities across requests" checklist item.
  - The **function / object / object-property** authorization granularity as a
    MUST — the defensive counterpart to the corpus's `bfla`/`bola` red-team
    split — with the *object-property* level not covered anywhere in the
    corpus's gateway material.
  - The **audit-baseline triad** (log every request; never log the access token
    or PII; carry a per-request unique identifier; record the applied
    authorization decision) plus the PDP-side twin (log every decision *and
    its input*).
  - The **PEP/PDP interface named**: AuthZEN (Authorization API 1.0) as the
    standardized decision-request interface between enforcement and decision
    components — the corpus's only concrete gateway→verdict contract today is
    a signed JWT.
  - The **SVID bootstrap problem named explicitly** — "mTLS is not possible
    without an existing SVID" — together with the attestation / join-token
    bootstrap mechanisms and the automated-rotation requirement.
  - The **scope statement** the guide needs: automated agents are first-class
    identity subjects, while MCP and A2A are explicitly out of scope.

## Guide Impact

- **Chapter 06 — "Function-calling authorization"** (currently the
  `rbac`/`bfla`/`bola` split sourced to `blog-promptfoo-red-team-gemini`,
  Claim 9, plus the gateway-side guardrail rule from
  `docs-litellm-generic-guardrail-api`, Claim 5): add the *normative* three-level
  requirement from this source's Common Requirement 8 — "MUST implement
  authorization at the function level, the object level, and the object property
  level" — so the section's three levels stop being a red-teamer's probe
  taxonomy and become a defense-side checklist the guide can cite to OWASP API
  Top 10 via the TAG. Two specific additions: (a) note that the guide's
  `rbac` level ("does the model respect user permissions?") has a normative
  two-input form — the decision is made against the workload identity *and* the
  end user ("dual-subject authorization"); (b) name **object-property** level as
  the granularity the corpus's gateway material does not implement at all
  (`tool_calls` argument validation is not property-level authorization of the
  object being touched). Also add the placement requirement that follows from
  "MUST delegate authorization to PDP": the gateway is the PEP and must call out
  for the decision rather than deciding inline.
- **Chapter 06 — "An agent gateway's default is full access"** (sourced to
  `docs-litellm-a2a-agent-permissions`, Claim 1): this source supplies the
  *architectural* answer to the fail-open default, and one caution. The answer:
  a compliant deployment has an explicit PEP→PDP delegation with a mandated
  call ("MUST delegate authorization to PDP"), a PDP that is not reachable from
  outside the cluster, and — in the Advanced pattern — a PDP that authenticates
  the gateway with an SVID, so a gateway that cannot prove its identity gets no
  decision. The caution: the paper's **Basic** pattern explicitly permits
  internal workloads to skip authorization ("not all workloads require
  authorization, and you MAY enforce authorization only if you want"), so a
  perimeter-only deployment can be fully standards-compliant while leaving
  east-west agent traffic unauthorized. Recommend stating that explicitly in
  this section, alongside the rule's existing fail-open evidence.
- **Chapter 06 — "Agent auditability is becoming a compliance expectation"**
  (currently the rule "Log the full agent decision trail — which tools were
  called, which MCP servers were consulted, what sub-agents were invoked"):
  attach the four mandatory fields from this source's Workload #1 Requirement 2
  so the rule becomes checkable — log **every** request; **never** log the
  access token (or PII); carry a **unique identifier per request** (generate
  one if the request does not have one); **record the authorization decision
  applied to the request** — plus the PDP-side twin (log every decision *and its
  input*, and carry the PEP's request identifier). This also supplies the
  missing "what does the record have to name" answer that
  `docs-promptfoo-enterprise-audit-logging`, Claim 5 shows real products omit
  (no request-id, no session attribution). Pair the MUST-NOT-log-the-token
  rule with the guide's data-governance section so the audit trail and the
  privacy principle are stated as complementary constraints on the same record,
  not competing requirements.
- **Chapter 06 — "Gateway credential routing: declare, don't infer"**: add the
  *inbound* and *client-authentication* counterparts this source specifies. The
  section's rule is that the **outbound** credential must be declared rather
  than inferred; this source requires that (a) how the inbound caller
  authenticates to the identity provider is itself a declared, pattern-dependent
  choice — client ID + secret in Basic, SVID (X.509 or JWT) in Advanced, with
  `private_key_jwt` / `tls_client_auth` explicitly permitted in between — and
  (b) sender-constrained tokens MUST be validated for proof-of-possession when
  the resource server issues them (DPoP or OAuth 2.0 Mutual-TLS), so a stolen
  token is unusable without the client's key. The second is a strong
  fail-closed default that mirrors the section's existing "ambiguity must resolve
  to stop".
- **Chapter 06 — "Data governance for AI workloads"** (the provider
  data-sharing / retention / impact-assessment sections): add the privacy
  principles as the concrete design constraints on agent prompt and log
  handling — `sub` MUST be an opaque non-PII identifier (not a login name or
  email), and "exposure limitation" covers *tokens, logs, and policy inputs*.
  The third of those is the one an agent gateway creates and the guide does not
  currently name: a gateway that forwards a request or its tool arguments to a
  policy engine has moved identity-bearing data to a new destination. The
  right-to-erasure principle also supplies the mechanism for deletion requests
  without touching downstream authorization systems.
- **Chapter 06 — trust boundaries (and Chapter 00 "Working principles")**: add
  the trust-boundary-granularity axis the corpus lacks. The guide currently
  argues *where* enforcement lives; this source adds *how many* trust
  boundaries there are — the Kubernetes cluster as one implicit trust zone
  (Basic, perimeter enforcement) versus every workload as its own trust
  boundary (Advanced, mTLS via SVID everywhere, MFA mandatory, PEP in every
  workload, sender-constrained tokens). The corollary worth stating for the
  corpus's existing enforcement material: this paper's Basic pattern explicitly
  says "not all workloads require authorization, and you MAY enforce
  authorization only if you want" — a standards-shaped version of the
  guide's "default is full access" finding, and a reminder that perimeter
  enforcement leaves east-west agent traffic unguarded by design, not by
  accident.
- **Chapter 06 — supply-chain / credential material**: the Basic pattern's
  default client authentication to the identity provider is a shared static
  secret (`client_secret_post`), while the paper's own §1.2.1 recommends
  "the avoidance of long-lived credentials". Recommend citing this alongside
  the corpus's existing credential-hygiene notes
  (`blog-cncf-securing-cicd-credentials-verification`, Claims 3–5) so the
  guide's "no long-lived credentials" rule has a standards anchor on the
  identity-provider leg as well as the CI leg.

## Extraction Notes

- **Source actually read**: the 39-page PDF at `source_url`, extracted with
  `pypdf` (91,763 characters of text) and read in full, page by page — cover,
  executive summary, table of contents, §1 (Introduction: scope, why IAM matters,
  standards, actors, privacy), §2 (both reference patterns, both end-to-end
  flows), §3 (Basic requirements), §4 (Advanced requirements), §5 (conclusion),
  §6 (resources, glossary, references, acknowledgments), §7 (footnotes). The
  issue's own URL (the CNCF announcement post) was fetched separately and is
  the ~200-word "Read the whitepaper to discover:" bullet list; it carries no
  extractable claim of its own, which matches the Prospector's warning that the
  issue URL is not the content.
- **Quote discipline**: every `Quote` field and every quoted passage in Concrete
  Artifacts was checked character-for-character against the extracted PDF text
  before being written, including the source's curly quotation marks (e.g.
  "identity"), the en dash in "PEP–PDP", the `sub` claim's backticks, and the
  source's British/US spellings. Four source strings are hyphenated compounds
  that the PDF's text layer breaks across a line ("platform-specific",
  "relationship-based", "service-to-service", "user-managed"); they are quoted
  as the rendered page reads them, and none of the four appears inside a
  `Quote` field. The MCP/A2A exclusion quote in Claim 1 stops before the
  footnote marker that follows "(e.g., MCP, A2A)", per MINER §2a's rule on
  footnote-marker noise; the remainder of that sentence is recorded in the
  claim's Evidence field.
- **Quote/artifact fidelity caveat for the Assayer**: the PDF's text layer is
  the source of the quotes, so a text-extraction spot-check will see the same
  characters with line-wrap whitespace collapsed. The four line-wrap hyphen
  artifacts named above are the only known divergences between the text layer
  and the rendered page. The Table 1 and Table 2 blocks are the only two
  artifacts whose *layout* was changed (the PDF renders them as ruled tables;
  here each cell's text is listed unchanged, one row per line) — the cell
  strings themselves are verbatim.
- **Evidence ceiling**: this is a standards document. There are **no
  deployments, benchmarks, metrics, incidents, CVEs, or implementation
  examples** anywhere in it — the two reference flows are diagrams described in
  prose, and every figure is a conceptual diagram rather than a capture of a
  running system. Per the Prospector's signal note, the guide must not cite
  this source as evidence that a pattern works in production. Consequently no
  claim above is graded `anecdotal` (there is no anecdote to grade) and
  `confidence_overall` is `emerging`: the *content* of the document is settled
  (it is a published, consensus-shaped specification with RFC 2119 language),
  but the *architectural recommendations* it carries are unvalidated by field
  evidence, and the pattern-selection claims are graded `emerging` for that
  reason.
- **Extraction scope**: §1.1 explicitly excludes agent protocols (MCP, A2A) and
  asynchronous/long-running processing, and §1.5/§1.3 exclude policy management
  and identity-provider design. Claim 1 records this and every claim above is
  scoped accordingly; the guide must carry the scope note wherever this source
  is cited.
- **`miner-related-notes.md` disposition**: all ten candidate paths evaluated —
  three cited (`blog-cncf-cloud-native-agentic-ai-security-platform`,
  `docs-promptfoo-enterprise-audit-logging`,
  `docs-google-sre-ai-engineering-reliable-operations`) and seven explicitly
  dismissed (see Cross-References). Additional cross-references
  (`blog-cncf-agent-auth-lawyers-day-in-court`,
  `blog-cncf-network-boundary-ai-agents-nginx-otel`,
  `blog-cncf-4-body-problem-sre-context`,
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry`,
  `docs-litellm-a2a-agent-permissions`, `docs-litellm-gateway-auth-reference`,
  `docs-litellm-a2a-agent-gateway`, `docs-litellm-generic-guardrail-api`,
  `blog-promptfoo-red-team-gemini`,
  `blog-linsun-pod-deployment-unit-ai-agent`, `blog-linsun-sandboxing-agent-not-enough`,
  `blog-cncf-secret-sprawl-external-secrets-operator`,
  `blog-cncf-securing-cicd-credentials-verification`,
  `blog-cncf-policy-engine-offline-production-fidelity`) were found by searching
  `source-notes/`.
- **Cross-reference verification**: every `Claim N` cited from another source
  note was re-read in that note and the number verified against the claim
  heading before being written here (MINER.md §4b). The two notes whose claims
  are quoted from memory rather than paraphrased —
  `blog-cncf-agent-auth-lawyers-day-in-court` (Claims 5, 6, 11) and
  `blog-cncf-cloud-native-agentic-ai-security-platform` (Claims 2, 3) — were
  read in full during this extraction.
- **Contradiction check**: `CONTRADICTIONS.md` (no entries) and all 18 open
  `contradiction`-labeled issues were checked. No entry or issue covers IAM,
  PEP/PDP, SPIFFE, workload identity, or the two-identity decomposition, so no
  contradiction issue was filed. The three tensions examined and the reasoning
  for not filing are written out under Cross-References → Contradicts so the
  Assayer can overrule. The nearest existing issue, #1597 (promptfoo audit-log
  access coverage), is referenced as a strengthening reference rather than
  re-filed.
- **Date and metadata**: `date_published` is the announcement date of the
  whitepaper (2026-06-04); the PDF's own `CreationDate` metadata is 2026-06-01.
  `date_extracted` and `last_checked` are 2026-10-21 UTC, the date the PDF was
  fetched and every quote re-verified.
- **No `guide/` edits, no `registry/*` edits**: per the repo's hard rules,
  `registry/sources.json` and `registry/claims-index.json` are rebuilt after
  merge from source-note front-matter and claim headings
  (`scripts/build_registry.py`, `scripts/build_claims_index.py` /
  `registry-rebuild.yml`), and only the Smith edits `guide/`.
