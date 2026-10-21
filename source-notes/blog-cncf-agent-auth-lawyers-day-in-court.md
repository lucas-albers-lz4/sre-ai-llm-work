---
source_url: https://www.cncf.io/blog/2026/06/23/agent-auth-a-lawyers-day-in-court
source_type: blog-post
title: "Agent Auth: A lawyer’s day in court"
author: "Lin Sun (CNCF Ambassador)"
date_published: 2026-06-23
date_extracted: 2026-10-21
last_checked: 2026-10-21
status: current
confidence_overall: emerging
issue: "#1690"
---

# Agent Auth: A lawyer’s day in court

> The single most transferable idea here: agent authentication has *two* identities to establish — which agent is acting and which user it acts for — and the delegation artifact between them carries four distinct facts, of which possession authorizes nothing on its own.

## Source Context

- **Type**: blog-post (CNCF blog; personal/positioning essay by a CNCF Ambassador)
- **Author credibility**: Lin Sun is a CNCF Ambassador and the author of two other notes in this corpus
  (`blog-linsun-sandboxing-agent-not-enough.md`, `blog-linsun-pod-deployment-unit-ai-agent.md`), where the
  claims are first-hand design arguments about running agents on Kubernetes. Here the author is writing
  about *identity* rather than deployment, and `agentgateway` — a Solo.io project the author is closely
  associated with — is one of the four named components of the proposed stack. **Conflict-of-interest
  caveat**: the CNCF post and the agentgateway documentation are not independent sources; treat
  agentgateway-specific statements as self-reported by the ecosystem, and lean on RFC 8693 and SPIFFE
  (both independent) for the load-bearing claims.
- **Scope**: A ~600-word conceptual essay. It decomposes agent authentication into agent identity,
  principal identity, and delegation; argues that a gateway/mesh should centralize the plumbing; and
  lists a five-item platform capability checklist. It contains **no code, no configuration, no metrics,
  no benchmarks, no incident report, no CVE, and no production evidence**. It names SPIFFE, cert-manager,
  Istio, and agentgateway as the substrate but does not show them wired together, and it does not discuss
  the failure modes of its own design. The value is the *vocabulary* and the decomposition, not an
  implementation.

## Extracted Claims

### Claim 1: Agent workloads are "microservices+" — they need strictly more than a traditional microservice, in three named dimensions (authentication, policy, observability)
- **Evidence**: The opening framing paragraph plus the three-item list that follows it. Argument only —
  no failure data, no comparison against a named baseline, no implementation.
- **Confidence**: emerging (a well-articulated framing position; the three additions are asserted, not demonstrated)
- **Quote**: "I’ve always thought about AI agents as microservices+." / "They need everything a traditional microservice needs, and:"
- **Our assessment**: The framing is doing real work: it tells an engineer reading the article that
  agent auth is *not* merely about adding mTLS to a service. The three dimensions are the right ones and they map
  cleanly onto what the corpus already knows separately — gateway-side tool authorization
  (`docs-litellm-generic-guardrail-api`, Claim 5), fail-open gateway defaults
  (`docs-litellm-a2a-agent-permissions`, Claim 1), and audit-trail requirements
  (`blog-litellm-april-townhall-updates`, Claim 11). The article's contribution is that it names the
  *extra* dimension (multi-principal action) that the corpus's gateway sources treat implicitly.

### Claim 2: The extra authentication requirement is specifically that one agent may act on behalf of many different users at once
- **Evidence**: First bullet of the opening list. Asserted as a property of agents; no example agent or
  deployment is described.
- **Confidence**: emerging (architectural claim, unvalidated in the source)
- **Quote**: "More authentication requirements because an agent may act on behalf of many different users."
- **Our assessment**: This is the crux of the whole essay and it deserves to be stated as a first-class
  rule rather than as a bullet. The corpus's gateway material reasons about a *calling key* and its
  *team* (`docs-litellm-a2a-agent-permissions`, Claims 1–3) — i.e. about the caller, not about the
  user on whose behalf the caller acts. Those are different axes, and the corpus currently collapses
  them. Worth stating plainly: a gateway key is not a principal. What the article does *not* say is
  what happens when one agent is legitimately used by 50 different users — the delegation-per-user
  question, which is the hard part and is deferred to the OBO section.

### Claim 3: Policy enforcement is a first-class agent requirement because agent behavior is less predictable than a conventional service's
- **Evidence**: Second bullet of the opening list. Reasoned assertion; no incident or measurement.
- **Confidence**: emerging (argued position; the corpus has a *stronger*, implementation-backed version)
- **Quote**: "More policy requirements because an agent’s behavior can be less predictable, requiring guardrails and policy enforcement."
- **Our assessment**: Directionally right, and the corpus already holds a stronger form of it:
  `blog-cncf-cloud-native-agentic-ai-security-platform.md`, Claim 3 argues that agent safety
  constraints belong in policy-as-code (OPA + Kyverno) rather than in the system prompt, because
  prompt-reasoned constraints are nondeterministic, unversioned, and untestable. That note is
  first-hand design with a version-controlled, unit-tested policy artifact; this one is a slogan
  attached to a bullet. Read this claim as the thesis statement of that stronger note, not as a
  separate finding.

### Claim 4: Agent observability has to reach further than a traditional service's — into context, prompts, tool calls, and the contents of requests and responses
- **Evidence**: Third bullet of the opening list. Assertion; no instrumentation shown.
- **Confidence**: emerging (consistent with the corpus, independently unsupported here)
- **Quote**: "More observability requirements, especially around context, prompts, tool calls, and the contents of requests and responses."
- **Our assessment**: Consistent with `blog-cncf-network-boundary-ai-agents-nginx-otel.md`, Claim 3,
  which grounds agent observability in OpenTelemetry spans that carry the agent's tool-call trail, and
  with the guide's existing Ch06 rule to "Log the full agent decision trail" as structured, queryable
  records. The article adds nothing new on observability itself; it adds the claim that *why* an agent
  needs it is different from a microservice's (the content is model output, not a fixed request shape).

### Claim 5: Agent identity — knowing exactly *which* agent is making the request — is a precondition for trusting that agent
- **Evidence**: The courtroom analogy: the judge first asks the lawyer to prove who he is. This is the
  author's framing, not a described implementation.
- **Confidence**: emerging (framing argument; the underlying mechanism is standard and well-specified elsewhere)
- **Quote**: "This is agent identity. Before the system can trust an agent, it needs to know exactly which agent is making the request."
- **Our assessment**: The mechanism is boring and well-trodden (workload identity / mTLS / SPIFFE SVIDs),
  but the *framing* is not: it establishes agent identity as a question the system must answer before
  any principal question is even asked. That ordering matters for the guide's gateway section, which
  currently reasons about callers and keys but never about which agent is making the request. The article's own
  answer for agent identity — SPIFFE, cert-manager, Istio — is verified as real in the external
  grounding below, though notably *not* via agentgateway.

### Claim 6: Principal identity is a *separate* identity from agent identity — the system must know which user the agent is acting for, not just who the agent is
- **Evidence**: The second turn of the courtroom analogy. This is the article's distinguishing idea.
- **Confidence**: emerging (novel to this corpus; the decomposition is asserted, not demonstrated)
- **Quote**: "This is principal identity. The system needs to know not only who the agent is, but also which user the agent is acting for."
- **Our assessment**: This is the genuinely new material. `grep -rn "principal identity" guide/ source-notes/`
  returns nothing — the corpus has no vocabulary for this. The closest existing coverage is
  `docs-litellm-a2a-agent-permissions.md`, Claim 7, whose permission hierarchy separates End-user /
  Agent / Org levels; that is a *permission* hierarchy, not an *identity* decomposition, and it never
  states that a request carries two identities simultaneously. The guide's Ch06 "Function-calling
  authorization" section has the same blind spot: its `rbac`/`bfla`/`bola` split (who / which function /
  which object) presumes a single "who". Adopting this source means the guide gains a way to say
  the `rbac` level has two inputs rather than one.

### Claim 7: The delegation artifact — an On-Behalf-Of (OBO) token or equivalent — carries four distinct facts: principal identity, agent identity, delegated permissions, and the scope of the delegation
- **Evidence**: The lead-in sentence plus the four-item list that follows it in the article. The list is
  the specification-like content of the essay; no token format is shown.
- **Confidence**: emerging (the enumeration is the article's own; the token contents it describes are
  standardized in RFC 8693 — see external grounding)
- **Quote**: "In agent systems, this is often represented by an On-Behalf-Of (OBO) token or another delegation artifact. The token carries information about:"
- **Our assessment**: The four contents map cleanly onto RFC 8693's delegation token (see Concrete
  Artifacts → external grounding): the principal is `sub`, the agent is `act.sub`, the delegated
  permissions and the scope are `scope` (plus the target in `aud`). This is the article's most
  portable contribution, and it is the piece the corpus lacks — `docs-litellm-gateway-auth-reference.md`,
  Claim 2 records that LiteLLM's MCP gateway *has* an `oauth2_token_exchange` mode described as "RFC
  8693 On-Behalf-Of (OBO)", but the corpus has never recorded what such a token contains or why the
  delegation model differs from impersonation. The article's "or another delegation artifact" hedge
  is worth keeping in mind: OBO is one implementation of the concept, not the concept.

### Claim 8: Possessing a valid delegation is necessary but not sufficient — the requested action must still pass a policy and scope check specific to that request
- **Evidence**: The third turn of the courtroom analogy, where the judge verifies the lawyer may
  represent Alice *in this particular traffic case*. This is the article's most important safety claim
  and it is stated plainly.
- **Confidence**: emerging (asserted as a principle; corroborated by RFC 8693 §5 and by the corpus's
  fail-open findings, but not demonstrated here)
- **Quote**: "The judge must also verify that the lawyer is allowed to represent Alice in this particular traffic case. This is where policy enforcement comes in." / "Having a valid delegation does not automatically grant unlimited access. The requested action must still comply with the applicable policies and scopes."
- **Our assessment**: This is the rule the guide should adopt, and it is the one the corpus most needs:
  the corpus has *two* documented cases of a valid credential granting more than it should —
  `docs-litellm-a2a-agent-permissions.md`, Claim 1 (with neither key nor team level configured, the
  resolution table returns "Key can access **all** agents") and
  `blog-litellm-july-stability-update.md`, Claim 2 (Cached OAuth tokens going stale or crossing
  between users). Both are fail-open defaults at the gateway; the article names the general shape —
  authentication of the delegation is a separate question from authorization of the action. Note the
  article also does *not* say where that check runs: it says "the judge" does it, which is the gateway
  in the article's own architecture, but a reader could equally put it in the tool layer. The guide
  should say it runs at the enforcement point, which is the gateway or the policy decision point
  (OPA/Kyverno per `blog-cncf-cloud-native-agentic-ai-security-platform.md`, Claim 3) — not in the
  model's prompt.

### Claim 9: The article states a five-item platform capability checklist — strong agent identities, principal identity carried across requests, delegation token issuance and validation, authorization policy and scope enforcement, and observability/audit trails
- **Evidence**: The article's "An agent platform must be able to:" list. No implementation of any item
  is shown; the list is the deliverable.
- **Confidence**: emerging (a checklist, and a useful one, but an assertion)
- **Quote**: "An agent platform must be able to:" / "Establish strong agent identities" / "Carry principal identities across requests" / "Issue and validate delegation tokens" / "Enforce authorization policies and scopes" / "Provide observability and audit trails for agent actions"
- **Our assessment**: Two of the five items are already covered in the guide by stronger sources
  (item 1 → `blog-cncf-cloud-native-agentic-ai-security-platform.md`, Claim 2, cert-manager per-agent
  identities; item 4 → same note's Claim 3, OPA/Kyverno policy-as-code; item 5 → Ch06's existing
  audit-trail rule). Items 2 and 3 — *carry principal identities across requests* and *issue and
  validate delegation tokens* — are the genuinely new checklist entries, and they are exactly the two
  the corpus cannot answer today. Treat this list as a coverage matrix against the guide rather than
  as five new facts.

### Claim 10: The gateway and mesh should centralize identity propagation, delegation verification, policy enforcement, and auditing, rather than each agent implementing them
- **Evidence**: The article's architectural recommendation, with the "court clerk, bailiff, and records
  office" analogy as the justification.
- **Confidence**: emerging (argued position, consistent with the corpus's gateway-centric guidance)
- **Quote**: "Rather than requiring every agent to independently implement identity propagation, delegation verification, policy enforcement, and auditing, the agent gateway and mesh can centralize these capabilities." / "The agent gateway and mesh become the equivalent of the court clerk, bailiff, and records office combined: ensuring identities are verified, delegations are valid, policies are enforced, and actions are auditable."
- **Our assessment**: This is the article's product thesis and it is not neutral — agentgateway is the
  beneficiary. But the *pattern* it names is already the corpus's established position: Ch06's
  "Gateway credential routing: declare, don't infer" and the gateway-side tool-authorization rule both
  argue that the enforcement point belongs at the gateway, not in the agent. The article's real
  contribution here is item 1 of that list — *identity propagation* — which is the part the corpus has
  no coverage for and which is the practical blocker: the principal's identity has to survive every
  hop between the user, the agent, and the tool. The "mesh" half of the claim is the weaker half;
  `blog-cncf-cloud-native-agentic-ai-security-platform.md`, Claim 2 argues the opposite direction
  (cert-manager per-agent mTLS + CiliumNetworkPolicy *instead of* a mesh, calling that "materially
  simpler"). That is a difference in deployment choice, not a contradiction of claims — different
  contexts, per MINER §4a — but the guide should not adopt the gateway-and-mesh pairing as a single
  recommendation.

### Claim 11: The proposed stack is SPIFFE + cert-manager + Istio + agentgateway, with the platform handling identity, delegation, policy enforcement, and observability while agents keep business logic
- **Evidence**: The article's stack sentence. Independently checkable, and partially confirmed:
  cert-manager and Istio are both listed in SPIFFE's own ecosystem tables, and agentgateway does
  implement RFC 8693 token exchange with a delegation actor token (both verified in external grounding
  below). **Not** confirmed: that agentgateway appears in SPIFFE's ecosystem tables — it does not, as
  of 2026-10-21.
- **Confidence**: emerging (named components are real; the composition is unbuilt and unstated as such)
- **Quote**: "Combined with existing identity and service-mesh technologies such as SPIFFE, cert-manager, Istio, and agentgateway, we can build an agent platform where agents focus on business logic while the platform handles identity, delegation, policy enforcement, and observability."
- **Our assessment**: The components check out individually — SPIFFE for workload identity, cert-manager
  for X.509 SVID issuance, Istio as a SPIFFE-based mesh, agentgateway as the gateway layer with
  RFC 8693 exchange. But note what the article's stack does *not* supply: nothing in it issues a
  delegation token on behalf of an end user. RFC 8693's exchange is performed by a *client* against an
  *authorization server*; agentgateway's `oauthTokenExchange` is configured with a static
  `subjectToken` source (a header) and a token endpoint host — it exchanges a credential it is handed,
  it does not mint a delegation artifact from an end-user session. So the article's "issue and validate
  delegation tokens" checklist item is the one its own named stack does not obviously cover. That is a
  genuine gap in the argument, and it is where the guide should be careful not to imply that dropping in
  the named components yields the checklist.

### Claim 12: The article's governing rule is that an agent is not the user — both operate under their own identity, acting for someone else under a specific delegation and a defined scope, and that relationship must be explicit, verifiable, and enforceable
- **Evidence**: The closing two-line aphorism and its one-sentence gloss. Pure statement; no evidence.
- **Confidence**: emerging (a rule of thumb, stated well; the closest thing in the source to a
  quotable invariant)
- **Quote**: "A lawyer is not the client." / "An agent is not the user." / "Both operate with their own identities while acting on behalf of someone else, under a specific delegation and within a defined scope. Agent auth is fundamentally about making that relationship explicit, verifiable, and enforceable."
- **Our assessment**: This is the line the guide should carry, because it is short enough to survive
  being quoted and it is exactly the distinction the corpus lacks. It is also directly falsifiable in
  a useful way: `docs-litellm-gateway-auth-reference.md`, Claim 10 records that end-user identity is
  *not* automatically forwarded downstream in the LiteLLM gateway, so the "agent is not the user"
  property is routinely lost in practice. The article is aspirational on this point — the article
  itself offers no mechanism for keeping the two identities distinct across hops, which is the gap
  its own "Carry principal identities across requests" checklist item admits.

## Concrete Artifacts

All artifacts below are verbatim from the source page, unless the block is under the
**External grounding** sub-heading, which is explicitly not from the source page.

### The three additions to "microservices+" (from the article's opening list, verbatim)

```
They need everything a traditional microservice needs, and:
- More authentication requirements because an agent may act on behalf of many different users.
- More policy requirements because an agent’s behavior can be less predictable, requiring guardrails and policy enforcement.
- More observability requirements, especially around context, prompts, tool calls, and the contents of requests and responses.
```

Attribution: "Agent Auth: A lawyer’s day in court", opening section.

### The four contents of the delegation artifact (from the article, verbatim)

```
In agent systems, this is often represented by an On-Behalf-Of (OBO) token or another delegation artifact. The token carries information about:
- The identity of the principal (Alice)
- The identity of the agent
- The delegated permissions
- The scope of the delegation
```

Attribution: "Agent Auth: A lawyer’s day in court", the On-Behalf-Of (OBO) token section.

### The five platform capabilities (from the article, verbatim)

```
An agent platform must be able to:
- Establish strong agent identities
- Carry principal identities across requests
- Issue and validate delegation tokens
- Enforce authorization policies and scopes
- Provide observability and audit trails for agent actions
```

Attribution: "Agent Auth: A lawyer’s day in court", the platform-capability list.

### External grounding consulted during extraction (NOT from the source page)

The article body contains no outbound hyperlinks, so there were no sub-pages to follow from it. The
blocks below are from independent primary documents consulted to check the article's terminology.
They are included so the Assayer can verify the mapping without re-fetching, and each is labelled with
its own source.

#### RFC 8693 §1.1 — delegation is not impersonation (https://www.rfc-editor.org/rfc/rfc8693.html)

```
Delegation semantics are different than impersonation semantics, though the two are closely related. With delegation semantics, principal A still has its own identity separate from B, and it is explicitly understood that while B may have delegated some of its rights to A, any actions taken are being taken by A representing B. In a sense, A is an agent for B.
```

#### RFC 8693 §A.2.5 — the issued delegation token (https://www.rfc-editor.org/rfc/rfc8693.html)

```
The subject ("sub") of the JWT is the same as the subject of the "subject_token" used to make the request. The actor ("act") of the JWT is the same as the subject of the "actor_token" used to make the request. This indicates delegation and identifies "admin@example.net" as the current actor to whom authority has been delegated to act on behalf of "user@example.net".
```

The RFC's own issued-token example, decoded, carries the four facts the article enumerates:

```
     {
       "aud":"urn:example:cooperation-context",
       "iss":"https://as.example.com",
       "exp":1441913610,
       "scope":"status feed",
       "sub":"user@example.net",
       "act":
       {
         "sub":"admin@example.net"
       }
     }
```

Attribution: RFC 8693, Appendix A.2.5, "Issued Token Claims". Mapping to the article: `sub` = the
identity of the principal (Alice); `act.sub` = the identity of the agent; `scope` = the delegated
permissions and the scope of the delegation; `aud` = the target the delegation is usable against.

#### RFC 8693 §4.1 — only the current actor counts for access control (https://www.rfc-editor.org/rfc/rfc8693.html)

```
For the purpose of applying access control policy, the consumer of a token MUST only consider the token's top-level claims and the party identified as the current actor by the "act" claim. Prior actors identified by any nested "act" claims are informational only and are not to be considered in access control decisions.
```

#### RFC 8693 §5 — scope is the abuse mitigation (https://www.rfc-editor.org/rfc/rfc8693.html)

```
The use of the "scope" claim (in addition to other typical constraints such as a limited token lifetime) is suggested to mitigate potential for such abuse, as it restricts the contexts in which the delegated rights can be exercised.
```

#### agentgateway — RFC 8693 exchange with a delegation actor token (https://agentgateway.dev/docs/standalone/latest/documentation/configuration/security/backend-authn/token-exchange/standard)

```
backendAuth:
  oauthTokenExchange:
    host: idp.example.com:443
    path: /token
    policies:
      backendTLS: {}
    actorToken:
      tokenType: urn:ietf:params:oauth:token-type:access_token
      source:
        header:
          name: x-actor-token
          prefix: "Bearer "
```

The page states: "For the RFC 8693 token exchange grant only, an actor token can be sent for delegation
(actor_token / actor_token_type). Unlike the subject token, the actor token has no default source, so a
source must be set." The subject-token form of the same block uses
`tokenType: urn:ietf:params:oauth:token-type:jwt` with a `header` source.

#### agentgateway — inbound JWT authentication defaults to fail-open (https://agentgateway.dev/docs/standalone/latest/documentation/configuration/security/jwt-authn)

The page lists three modes: "Strict: A valid token, issued by a configured issuer, must be present.";
"Optional (default): If a token exists, validate it." — annotated in the source with "Warning: This
allows requests without a JWT token!"; and "Permissive: Requests are never rejected." Also from the same
page: "If a token includes a not-before claim (nbf), agentgateway rejects the token when the nbf value
is more than 60 seconds in the future."

#### agentgateway — CEL authorization rule precedence (https://agentgateway.dev/docs/standalone/latest/documentation/configuration/security/http-authz)

The page's stated precedence: "If there are no rules, the request is allowed." / "If any deny rule
matches, the request is denied." / "If any require rule does not match, the request is denied. All
require rules must match for the request to proceed." / "If any allow rule matches, the request is
allowed." And: "A CEL expression that cannot be evaluated is treated as false." with the source's own
annotation: "A require expression that is false (or errors) denies the request (fail-closed)." and "A
deny expression that errors does not match, so it does not deny the request (fail-open)."

#### SPIFFE ecosystem tables (https://spiffe.io/docs/latest/spiffe-about/overview/)

The "Which Tools Work with SPIFFE?" tables list `SPIRE`, `Cert-manager`, `Consul`, `Dapr`, `Istio`
(Open Source Software that Works with SPIFFE) and `Envoy`, `Ghostunnel`, `Istio`, `Knox`,
`VMware Secrets Manager`, `SPIKE` (Open Source Software that Implements SPIFFE). `agentgateway` does
not appear anywhere in the SPIFFE overview as of 2026-10-21.

## Cross-References

- **Corroborates**:
  - `docs-litellm-gateway-auth-reference.md`, Claim 2 — the MCP gateway's
    `oauth2_token_exchange` mode is described as "RFC 8693 On-Behalf-Of (OBO)", i.e. the delegation
    artifact the article says an agent platform must issue and validate is already a shipping auth mode
    in one gateway. Claim 10 of the same note (end-user identity is not automatically forwarded
    downstream) is the practice-side evidence that the article's "agent is not the user" rule is
    routinely violated.
  - `blog-litellm-may-townhall-updates.md`, Claim 6 — on-behalf-of MCP OAuth with tokens vaulted at the
    proxy and refreshed transparently: a concrete implementation of the delegation path the article
    describes, and evidence that the client never sees a 401 (i.e. the principal's token lifecycle is
    hoisted to the platform layer, exactly the article's centralization thesis).
  - `blog-litellm-july-stability-update.md`, Claim 3 — the "declare, don't infer" typed credential
    resolver. Corroborates the article's insistence that agent identity be *established explicitly*
    (Claim 5) rather than inferred, and is the corpus's existing precedent for the guide's
    "Gateway credential routing: declare, don't infer" section.
  - `blog-cncf-network-boundary-ai-agents-nginx-otel.md`, Claim 4 (network control is not intent
    control) and Claim 1 (the gateway/proxy as the enforcement boundary) — the same argument as the
    article's Claim 8, from a different boundary: knowing *where* the request came from is not the same
    as knowing *what it may do*.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md`, Claim 2 (cert-manager per-agent
    identities, terminated at each agent's own transport) — a concrete instantiation of the article's
    "Establish strong agent identities"; and Claim 3 (OPA/Kyverno policy-as-code for agent safety
    constraints) — a concrete instantiation of "Enforce authorization policies and scopes", with the
    stronger evidence the article lacks.
  - `docs-litellm-a2a-agent-permissions.md`, Claim 1 — the fail-open default (neither key nor team
    level configured ⇒ "Key can access **all** agents") is a documented instance of the article's
    Claim 8 failure mode: a valid credential that grants more than the caller should have.
- **Extends**:
  - `blog-linsun-pod-deployment-unit-ai-agent.md`, Claim 18 — the same author asked "Should an agent’s
    identity really be tied to a Pod or its Service?" and left it open; this source answers it at the
    protocol level (agent identity is a first-class, issuer-assigned identity — SPIFFE/cert-manager —
    not a property of the deployment unit). Claim 20 of the same note already positions agentgateway
    as the mediation layer whose credential-injection design "starts from an empty default-deny
    policy"; this source supplies the identity vocabulary for why that mediation layer has to exist.
  - `blog-linsun-sandboxing-agent-not-enough.md`, Claim 3 — "necessary, but not sufficient":
    sandboxing answers *can the agent escape*, and this source names the layer that is left uncovered
    — *who is the agent, who is it acting for, and what was delegated to it*.
  - `docs-litellm-a2a-agent-permissions.md`, Claim 7 — the MCP permission hierarchy separates
    End-user / Agent / Org; this source supplies the *identity* counterpart of that separation (agent
    identity vs principal identity), which the permission-level note never states.
- **Contradicts**: none. No existing source note in the corpus asserts anything the article denies.
  Two apparent tensions are contextual, not contradictions, and are recorded here rather than filed
  (per MINER §4a, "When NOT to file"): (a) the article's framing of the agent gateway and mesh
  centralizing these capabilities versus
  `blog-cncf-cloud-native-agentic-ai-security-platform.md`, Claim 2's mesh-free
  cert-manager + CiliumNetworkPolicy topology — a deployment-choice difference, not opposed claims;
  (b) the article's aspiration that a platform be able to "Establish strong agent identities" versus
  agentgateway's documented
  default-on `jwtAuth mode: optional` (fail-open) — an implementation gap relative to the article's
  aspiration, not one source contradicting another. `CONTRADICTIONS.md` and the open
  `contradiction`-labeled issues were checked; no existing entry covers agent auth, delegation, or
  OBO, and no new contradiction issue is warranted.
- **Novel**:
  - The explicit two-identity decomposition — **agent identity** vs **principal identity** — stated as
    the answer to the question of who is making the request. `grep -rn "principal identity" guide/
    source-notes/` returns
    zero hits; this vocabulary does not exist anywhere in the corpus.
  - The four-fact enumeration of what a delegation artifact must carry (principal identity, agent
    identity, delegated permissions, delegation scope), and its mapping onto RFC 8693's
    `sub` / `act.sub` / `scope` / `aud`.
  - The one-line invariant "An agent is not the user" — stated as a rule rather than as a
    configuration detail.
  - The five-item platform capability checklist, in which the two entries the corpus cannot answer
    ("Carry principal identities across requests", "Issue and validate delegation tokens") are the
    genuinely new ones.
  - The distinction the corpus never draws: delegation ≠ impersonation. RFC 8693 §1.1 keeps the
    principal's identity visible in the token; the corpus's `docs-litellm-gateway-auth-reference.md`,
    Claim 2 records the OBO auth mode without ever stating that the delegation model preserves both
    identities.

## Guide Impact

- **Chapter 06 — "Function-calling authorization"** (currently the `rbac`/`bfla`/`bola` split, sourced to
  `blog-promptfoo-red-team-gemini`, Claim 9): the `rbac` level ("does the model respect user
  permissions?") assumes one identity. Recommend adding that authorization is evaluated against **two**
  inputs — the agent's own identity and the principal's — and that the three-level split applies to
  the principal's permissions while the agent identity scopes *which* tools the agent holds at all.
  This source supplies the vocabulary ("agent identity", "principal identity"); the guide currently has
  neither term.
- **Chapter 06 — "An agent gateway's default is full access"** (sourced to
  `docs-litellm-a2a-agent-permissions`, Claim 1): that section frames over-grant as a *key/team*
  configuration gap. Recommend adding the third axis: a delegation artifact's **scope** is what narrows
  what the acting agent may do on the principal's behalf, and RFC 8693 §5 states scope's purpose
  directly ("restricts the contexts in which the delegated rights can be exercised"). Paired with the
  source's rule that a valid delegation does not by itself authorize the request, this converts the
  section from a single over-grant axis (key/team) into three axes of over-grant — key, team, and
  delegation scope — and the third is the one that survives the hop.
- **Chapter 06 — "Gateway credential routing: declare, don't infer"**: add the inbound counterpart. The
  section's rule is that the *outbound* credential must be declared rather than inferred; this source
  establishes that the *inbound* identity must be too — the gateway must be told how agent identity is
  established (strict vs optional JWT validation), not left to infer it from whether a token happens to
  be present. The concrete artifact for this is agentgateway's three `jwtAuth` modes and their
  fail-open default, which is exactly the attach-whatever-is-there anti-pattern the section is about,
  moved to the inbound side.
- **Chapter 06 — "Agent auditability is becoming a compliance expectation"**: the existing rule ("Log
  the full agent decision trail — which tools were called, which MCP servers were consulted, what
  sub-agents were invoked") needs an answer to *who the record names*. Recommend adding that the
  audited principal is the **current actor** (`act`), with prior actors in a delegation chain retained
  as history and excluded from the access-control decision — RFC 8693 §4.1's rule that nested `act`
  claims "are informational only and are not to be considered in access control decisions" is a
  directly citable basis, and it prevents a subtle failure where a deeply delegated chain causes the
  audit record to name the wrong party.
- **Chapter 03 — "The emerging agent control plane" / "The control plane's four verbs"** (register,
  invoke, observe, govern): the four verbs are runtime/session-shaped and the identity chain is
  currently invisible in the guide. Recommend a scoped addition rather than a rewrite: identity
  establishment maps to *register*, principal propagation and delegation issuance to *invoke*,
  the decision trail to *observe*, and policy/scope enforcement to *govern*. Note the source is
  platform-specific (SPIFFE + mesh + gateway) and does not support a general claim about control
  planes, so the addition should be scoped to the identity/delegation axis and explicitly marked as
  emerging.
- **Chapter 06 — no contradiction-driven changes required**: nothing in the guide currently asserts the
  opposite of this source, so no existing rule needs retracting.

## Extraction Notes

- **Deep read**: full article read, paragraph by paragraph, plus the raw HTML (saved locally and
  parsed) to confirm that the quotes above are character-exact — including the typographic
  apostrophes (`’`) and the em-dash-free punctuation of the original. The article is short (~600
  words of body prose) but every paragraph was mined; the three-additions, four-token-contents,
  and five-capabilities lists are the article's only enumerable content, and all three are
  reproduced verbatim in Concrete Artifacts.
- **No sub-pages to follow**: the article body contains **zero outbound hyperlinks** (verified by
  scanning the raw HTML of the post body). The named technologies (SPIFFE, cert-manager, Istio,
  agentgateway) were therefore pursued directly: RFC 8693 §1.1/§2.1/§2.1.1/§4.1/§5/§A.2 were read in
  full, the SPIFFE overview's implementation/ecosystem tables were extracted, and agentgateway's
  `jwt-authn`, `http-authz`, and `token-exchange/standard` pages were fetched and parsed. That
  grounding is what lets Claim 11 be stated as partially confirmed rather than merely asserted, and it
  is what surfaced the gap in Claim 11's assessment (the named stack exchanges tokens it is handed; it
  does not mint an end-user delegation artifact).
- **Quote discipline**: every `Quote` field above is a verbatim fragment from the source page; the
  multi-part quotes are separated by " / " and each part is a contiguous fragment. RFC 8693, SPIFFE,
  and agentgateway quotations appear only in Concrete Artifacts → External grounding and in
  `Our assessment`, never in a `Quote` field, and each is attributed to its own document.
- **Evidence ceiling**: this source has no code, no configuration, no metrics, no failure data, and no
  production deployment. Every claim here is therefore rated `emerging` at best, and `confidence_overall`
  is `emerging`. It is an opinion/positioning piece whose value is conceptual framing; claims that
  duplicate stronger corpus sources (Claims 1, 3, 4, 9) are recorded so the corpus can cite them, not
  because they advance the evidence base.
- **Retrieval candidates** (`miner-related-notes.md`, 10 candidates — all addressed):
  - `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` — **cited** (Claims 2, 3,
    7, 10 cross-referenced above).
  - `source-notes/docs-litellm-gateway-auth-reference.md` — **cited** (Claims 2, 7, 10).
  - `source-notes/docs-litellm-a2a-agent-permissions.md` — **cited** (Claims 1, 7).
  - `source-notes/blog-litellm-july-stability-update.md` — **cited** (Claim 3).
  - `source-notes/blog-litellm-may-townhall-updates.md` — **cited** (Claim 6).
  - `source-notes/blog-cncf-agent-doc-access-tool-mix.md` — dismissed: agent doc-access/tool-mix
    concerns, not identity/delegation.
  - `source-notes/blog-litellm-valkey-semantic-caching.md` — dismissed: caching, not auth.
  - `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — dismissed: evaluation harness, not
    identity.
  - `source-notes/docs-google-sre-on-call.md` — dismissed: on-call practice, not agent auth.
  - `source-notes/docs-google-sre-eliminating-toil.md` — dismissed: toil reduction, not agent auth.
  - `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — dismissed: retail/gaming
    engineering, not agent auth.
  - `source-notes/docs-google-sre-prodcast-03-11-embracing-complexity.md` — dismissed: complexity
    management, not agent auth.
  - `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` — dismissed: imperative vs
    declarative APIs, not agent auth.
  - `source-notes/docs-google-sre-reliable-product-launches.md` — dismissed: launch reliability, not
    agent auth.
- **Cross-reference verification**: every `Claim N` cited from another source note was re-read in that
  note and the number verified against the claim heading before being written here.
- **Contradiction check**: `CONTRADICTIONS.md` and the open `contradiction`-labeled issues were checked.
  No entry or issue covers agent auth, delegation, OBO, or principal identity, and no claim here
  opposes an existing note, so no contradiction issue was filed. Reasoning for the two apparent
  tensions is recorded under Cross-References → Contradicts.
- **Registry**: `registry/sources.json` is not hand-edited here — per the repo's hard rules it is
  rebuilt from source-note front-matter by `scripts/build_registry.py` / `registry-rebuild.yml`.
