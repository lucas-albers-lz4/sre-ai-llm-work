---
source_url: https://docs.litellm.ai/blog/security-hardening-april-2026
source_type: failure-report
platform: blog
title: "Security Update: Vulnerability Disclosures and Ongoing Hardening"
author: "Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-04-03
date_extracted: 2026-07-30
last_checked: 2026-07-30
status: current
confidence_overall: settled
issue: "#669"
---

# Failure Report: LiteLLM Security Hardening — OIDC Cache Collision, Config Update Privilege Escalation, and Password Hash Exposure (CVE-2026-35030, CVE-2026-35029, GHSA-69x8-hrgq-fjj8)

> Three distinct security vulnerabilities disclosed by LiteLLM in v1.83.0 together with a bug bounty program launch: (1) OIDC cache collision (CVE-2026-35030, Critical) — auth bypass via `token[:20]` cache key collision when JWT auth is enabled; (2) privilege escalation via `/config/update` (CVE-2026-35029, High) — missing role check allowed any authenticated user to modify runtime proxy configuration; (3) password hash exposure and pass-the-hash login (GHSA-69x8-hrgq-fjj8, High) — passwords stored as unsalted SHA-256 (sometimes plaintext), hashes returned by API endpoints, and `/v2/login` accepting the raw hash as a credential. All three issues fixed in v1.83.0.

## Source Context

- **Type**: failure-report (multi-vulnerability security disclosure via vendor blog post)
- **Platform**: Vendor blog post on `docs.litellm.ai/blog` (Docusaurus), published alongside three GitHub Security Advisories: GHSA-jjhc-v7c2-5hh6 (CVE-2026-35030), GHSA-53mr-6c8q-9789 (CVE-2026-35029), GHSA-69x8-hrgq-fjj8.
- **Author credibility**: High — authored by Krrish Dholakia (CEO) and Ishaan Jaffer (CTO) of LiteLLM/BerriAI. The post follows LiteLLM's standard disclosure format with clear root-cause descriptions, advisory references, and fix guidance. Vulnerability discovery attribution is provided for each issue (Veria Labs, Lakera, hamzayevmaqsud, iO Digital).
- **Scope**: Covers three distinct vulnerability classes affecting the LiteLLM proxy: (1) authentication cache key design flaw (OIDC), (2) authorization gap on management endpoints, (3) credential storage and authentication protocol weakness. Also covers the LiteLLM bug bounty program launch. Does not cover the supply chain incident that prompted the audit, or other security topics.

## What Was Attempted

- **Goal**: N/A — this is a proactive multi-vulnerability security disclosure published by the vendor. Each vulnerability represents a distinct design or implementation flaw discovered during an external security audit (Veria Labs) and through independent researcher reports.
- **Tool/approach**: LiteLLM Proxy (pip package `litellm`), versions prior to v1.83.0. The three affected subsystems are (1) OIDC/JWT authentication cache, (2) `/config/update` management endpoint, (3) password storage and `/v2/login` authentication endpoint.
- **Setup**: LLM gateway proxy deployments. The OIDC cache collision requires `enable_jwt_auth: true` (off by default). The privilege escalation and password hash issues affect any deployment with the proxy UI/management endpoints exposed.

## What Went Wrong

- **Symptoms**: Three separate vulnerability disclosures:
  1. **OIDC cache collision (CVE-2026-35030)**: With `enable_jwt_auth` enabled, OIDC userinfo was cached using `token[:20]` as the cache key. JWTs from the same signing algorithm share identical header prefixes, enabling an attacker with a valid API key to forge a JWT that collides with another user's cache entry and inherit their session.
  2. **Config update privilege escalation (CVE-2026-35029)**: `/config/update` performed no role check on the caller. Any authenticated user could modify runtime proxy configuration, leading to potential arbitrary file read, admin account takeover, or remote code execution.
  3. **Password hash exposure and pass-the-hash login**: Passwords stored as unsalted SHA-256 hashes (sometimes plaintext), several API endpoints returned the hash to any authenticated user, and `/v2/login` accepted the raw hash as a credential without re-hashing — making a stolen hash functionally equivalent to the password.
- **Severity**: Critical (CVE-2026-35030 — CVSS 9.x, authentication bypass) and High (CVE-2026-35029, GHSA-69x8-hrgq-fjj8). The critical issue only affects deployments with `enable_jwt_auth: true` (off by default). The two high-severity issues require the attacker to already have a valid API key. All three fixed in v1.83.0.
- **Reproducibility**: All three vulnerabilities are deterministic given the required preconditions.

### Vulnerability 1: OIDC Cache Collision (CVE-2026-35030, Critical)
- **Evidence**: Veria Labs discovered and reported the cache key design flaw.
- **Quote**: "LiteLLM cached OIDC userinfo using `token[:20]` as the cache key. Since JWTs from the same signing algorithm share identical header prefixes, an attacker with a valid API key could forge a JWT that hits another user's cache entry."
- **Confidence**: settled
- **Our assessment**: This is a subtle and novel vulnerability class specific to LLM proxies that cache authentication state. The truncation of the cache key to 20 characters is the root design error — it assumes that the first 20 characters of a token are sufficiently unique, which is false for JWTs where the first portion (the header) is identical for tokens using the same algorithm. The fix — keying on `sha256(token)` — is the correct approach because SHA-256 produces a fixed-length, collision-resistant digest of the full token. The exploitability constraint (requires `enable_jwt_auth: true`, off by default) limits real-world impact but does not diminish the architectural lesson.

### Vulnerability 2: Config Update Privilege Escalation (CVE-2026-35029, High)
- **Evidence**: Lakera reported the missing authorization check.
- **Quote**: "`/config/update` didn't check the caller's role. Any authenticated user could modify runtime proxy configuration, which could lead to arbitrary file read, admin account takeover, or remote code execution."
- **Confidence**: settled
- **Our assessment**: A missing authorization gate on a management endpoint — a classic CWE-862 (Missing Authorization) vulnerability. The architectural lesson is that every management/configuration endpoint in an LLM gateway must carry an explicit authorization check, even if the route is "internal." The fix — requiring the `proxy_admin` role — is a straightforward application of role-based access control. The downstream impact (arbitrary file read, admin takeover, RCE) is severe because runtime configuration changes in a proxy can alter routing rules, logging destinations, and credential handling.

### Vulnerability 3: Password Hash Exposure and Pass-the-Hash Login (GHSA-69x8-hrgq-fjj8, High)
- **Evidence**: Reported by GitHub user hamzayevmaqsud (issue #15484), with the full chain identified by Luca Vandenweghe and Maarten De Rammelaere of iO Digital.
- **Quote**: "Passwords were stored as unsalted SHA-256 hashes — and in some cases plaintext. Several API endpoints returned the hash to any authenticated user. `/v2/login` accepted the raw hash as a credential without re-hashing it, making a stolen hash functionally equivalent to the password itself."
- **Confidence**: settled
- **Our assessment**: This is a multi-stage failure chain: weak storage (unsalted SHA-256, sometimes plaintext) → exposure (hashes returned by API endpoints) → exploitation (pass-the-hash login accepted raw hashes). Each stage independently compromises credential security, and together they form a compound failure that bypasses the entire authentication boundary. The fix (scrypt with random salts, stripping hashes from API responses) addresses all three stages. The pass-the-hash mechanism is particularly notable: by accepting raw hashes without re-hashing, `/v2/login` eliminated the value of hashing altogether — the hash was effectively the plaintext password.

## Root Cause

### Root Cause 1 (OIDC Cache): Truncated cache key assumes token prefix uniqueness
- **Author's diagnosis**: The cache key was truncated to 20 characters (`token[:20]`), which is insufficiently unique for JWTs.
- **Our assessment**: Agree. The root cause is a cache key design that made an incorrect uniqueness assumption. JWTs from the same signing algorithm share identical header portions (base64-encoded algorithm identifier and token type), making the first 20 characters nearly identical for all tokens from the same issuer. This is a textbook example of how cache key design affects security boundaries — the cache was shared across authentication sessions, so a cache key collision becomes a session collision.
- **Category**: genuine-bug (design flaw in cache key construction)
- **Fix**: Key the cache on `sha256(token)` instead of `token[:20]`.
- **Workaround**: Disable JWT auth if unable to upgrade.

### Root Cause 2 (Config Update): Missing authorization check on management endpoint
- **Author's diagnosis**: `/config/update` performed no role check.
- **Our assessment**: Agree. The root cause is CWE-862 — Missing Authorization. The endpoint was accessible to any authenticated user without verifying that the user had the necessary administrative role. The fix is straightforward: require the `proxy_admin` role.
- **Category**: genuine-bug (missing authorization gate)
- **Fix**: Require the `proxy_admin` role on `/config/update`.

### Root Cause 3 (Password Hash): Weak storage + exposure + pass-the-hash acceptance
- **Author's diagnosis**: Unsalted SHA-256 (sometimes plaintext) storage; API endpoints exposing hashes; `/v2/login` accepting raw hashes.
- **Our assessment**: Agree. This is a three-stage failure: (1) storage uses unsalted SHA-256, a weak password hashing algorithm that is trivially rainbow-tableable; (2) output paths return the hash to users, violating the principle that hashes should never be exposed; (3) the login endpoint accepts the hash as-is, meaning the hash is the credential. This chain means that any one of three separate failures (weak storage, exposed hash, or login acceptance) would be serious on its own; together they form a compound failure where the "security" of hashing is completely negated. The fix addresses all three stages: switch to scrypt with random salts (strong storage), strip hashes from API responses (no exposure), and presumably re-hash on login (no pass-the-hash).
- **Category**: genuine-bug (multi-stage credential management failure)
- **Fix**: Migrate to scrypt with random salts; strip hashes from all API responses.

## Recovery Path

- **What they switched to**: All fixes shipped in v1.83.0.
  1. OIDC cache key changed from `token[:20]` to `sha256(token)`.
  2. `/config/update` now requires the `proxy_admin` role.
  3. Password storage moved to scrypt with random salts; hashes stripped from API responses.
- **Action**: Upgrade to v1.83.0 or later.
- **Workaround for CVE-2026-35030**: Disable JWT auth if unable to upgrade. The default configuration (JWT auth disabled) is not affected by the OIDC cache collision.
- **Workaround for CVE-2026-35029**: Restrict network access to the `/config/update` endpoint or revoke API keys from non-admin users until the upgrade can be applied.
- **Workaround for GHSA-69x8-hrgq-fjj8**: Ensure non-admin users cannot access API endpoints that return password hashes; apply least-privilege access controls.
- **Unresolved**: None stated for the three disclosed issues. Veria Labs continues a broader audit of the proxy, meaning additional disclosures may follow.

## Concrete Artifacts

**Advisory references (verbatim from source):**
```
CVE-2026-35030 (Critical):
https://github.com/BerriAI/litellm/security/advisories/GHSA-jjhc-v7c2-5hh6

CVE-2026-35029 (High):
https://github.com/BerriAI/litellm/security/advisories/GHSA-53mr-6c8q-9789

GHSA-69x8-hrgq-fjj8 (High):
https://github.com/BerriAI/litellm/security/advisories/GHSA-69x8-hrgq-fjj8
```

**Impact scoping (verbatim from source):**
```
Both high-severity issues require the attacker to already have a valid
API key for the proxy — they are not exploitable by unauthenticated users.

The critical issue only affects deployments with enable_jwt_auth explicitly
enabled, which is off by default. The default LiteLLM configuration is not
affected, and no LiteLLM Cloud customers had this feature enabled.
```

**Vulnerability summaries (verbatim from source):**
```
Authentication bypass via OIDC cache collision (Critical)
- Cached OIDC userinfo using token[:20] as the cache key
- Since JWTs from the same signing algorithm share identical header
  prefixes, an attacker could forge a JWT that hits another user's
  cache entry
- Fix: keying the cache on sha256(token)
```

```
Privilege escalation via /config/update (High)
- /config/update didn't check the caller's role
- Any authenticated user could modify runtime proxy configuration,
  which could lead to arbitrary file read, admin account takeover,
  or remote code execution
- Fix: require the proxy_admin role on this endpoint
```

```
Password hash exposure and pass-the-hash login (High)
- Passwords were stored as unsalted SHA-256 hashes — and in some
  cases plaintext
- Several API endpoints returned the hash to any authenticated user
- /v2/login accepted the raw hash as a credential without re-hashing
  it, making a stolen hash functionally equivalent to the password
- Fix: moved to scrypt with random salts and stripped hashes from
  all API responses
```

**Bug bounty program (verbatim from source):**
| Severity | Bounty | Example |
|----------|--------|---------|
| Critical | $1,500 – $3,000 | Supply chain compromise |
| High | $500 – $1,500 | Unauthenticated access to protected data |

## Cross-References

- **Corroborates**:
  - `blog-litellm-may-townhall-updates.md` **Claim 3** (LiteLLM launched a paid bug bounty program) — the May townhall post confirms the same bug bounty program with identical scope ("the LiteLLM gateway and SDK"), and reports 89 vulnerabilities patched in the subsequent 4 weeks. This April security hardening post is the first announcement of the bug bounty program; the May note reports its ongoing operation and the volume of disclosures it produced. The May note's 89 vulnerabilities figure likely includes the three disclosed here plus additional findings from the Veria Labs audit referenced in this post ("Veria Labs is continuing to work with us on a broader audit of the proxy").
  - `blog-litellm-may-townhall-updates.md` **Claim 2** (89 vulnerabilities patched in 4 weeks, 78 from Veria scanner) — this April post is the beginning of that wave. It explicitly credits Veria Labs with finding the OIDC cache collision and notes "Veria Labs is continuing to work with us on a broader audit." The May metrics confirm the ongoing audit produced 78 Veria-reported vulnerabilities.
  - `failure-litellm-host-header-auth-bypass.md` — Same vendor (LiteLLM), same disclosure pattern (vendor blog post + GHSA). That note covers a Host-header route-resolution auth bypass (CVE-2026-49468); this note covers three additional attack classes in the same proxy. Together they establish that LiteLLM Proxy has had multiple critical/high-severity security vulnerabilities disclosed in rapid succession (April–June 2026).
  - `failure-litellm-proxy-sql-injection-cve-2026-42208.md` — Same vendor, same disclosure format. That note covers SQL injection through API key verification; this note covers three different vulnerability classes. Both are part of the broader security hardening wave that included the Veria Labs audit.
  - `failure-litellm-guardrail-logging-secret-exposure.md` — Same vendor, different failure class (credential leak through observability path). This note's password hash vulnerability also involves credential exposure through API response paths. Both establish that LiteLLM had multiple credential-handling weaknesses exposed during this period.
  - `failure-litellm-mcp-stdio-command-injection.md` — Same vendor, same disclosure pattern (vendor blog + CVE/GHSA). That note covers authenticated RCE through MCP stdio; this note covers additional authenticated attack vectors. Together they reinforce the pattern of recurring security vulnerabilities across LiteLLM Proxy's authentication, authorization, credential storage, and MCP subsystems.

- **Contradicts**: None. No existing source note claims that truncated token cache keys are safe, that management endpoints need no authorization checks, or that unsalted SHA-256 is an acceptable password storage mechanism for LLM gateways. No contradiction issue filed.

- **Extends / thematically adjacent**:
  - `blog-litellm-may-townhall-updates.md` — This April post is the chronological precursor to the May townhall's security metrics. The May post reports outcomes (89 vulnerabilities patched); this April post announces the first wave of disclosures from the Veria audit. Together they form a disclosure → resolution timeline.
  - `failure-litellm-host-header-auth-bypass.md` — Both are LiteLLM security advisories with CVEs. This note adds JWT/OIDC cache design issues and password storage failures to the corpus's LiteLLM vulnerability collection. The Host-header note covers route-resolution auth bypass; this note covers OIDC cache collision (another auth bypass mechanism through a completely different vector — caching, not routing).
  - `docs-google-sre-prodcast-04-01-security-sre-intersection.md` — Discusses security–SRE intersection at a principles level. The concept of "security controls applied at the correct layer" (auth at the gateway, not just the application) is relevant to the OIDC cache collision vulnerability, where the caching layer became an auth boundary.
  - `docs-langfuse-security-and-guardrails.md` — Covers guardrail library patterns for LLM security. The password storage vulnerability in this note (unsalted SHA-256, pass-the-hash) is a credential management failure orthogonal to guardrail architecture. Both address security patterns relevant to LLM infrastructure operators.

- **Novel**: This is the first source note in the corpus covering:
  1. **OIDC cache collision as an auth bypass mechanism** — a cache key design flaw specific to LLM proxies that cache authentication state. The use of `token[:20]` as a cache key is a vulnerability class (truncated token as cache key) not documented elsewhere in the corpus.
  2. **The `sha256(token)` cache key fix pattern** — using a full-token digest instead of a prefix as the cache key. This is a concrete, generalizable fix for any system that caches authentication state keyed on a bearer token.
  3. **Pass-the-hash login on an LLM gateway** — the specific pattern where `/v2/login` accepted raw password hashes as valid credentials. This is a credential management failure mode specific to LLM proxy authentication design.
  4. **Three vulnerability disclosure from a single security audit** — the Veria Labs audit of the LiteLLM proxy discovering multiple vulnerability classes (cache design, missing authorization, credential storage) in a single engagement, demonstrating the breadth of attack surfaces in LLM gateway software.
  5. **LiteLLM bug bounty program structure** — the bounty tiers ($1,500–$3,000 for Critical/P0, $500–$1,500 for High/P1) and scope definitions for an LLM infrastructure project.

## Guide Impact

- **Chapter 05 (Security & Hardening) — Authentication Cache Key Design**: Add a specific security requirement: "LLM gateways that cache OIDC/JWT authentication state MUST use a collision-resistant cache key derived from the full token (e.g., `sha256(token)`), NOT a truncated token prefix." Reference CVE-2026-35030 and GHSA-jjhc-v7c2-5hh6 as a real-world case study. Include the generalizable lesson: truncated auth tokens are unsafe as cache keys because tokens from the same issuer share prefix structure (e.g., JWT headers for the same signing algorithm).

- **Chapter 05 (Security & Hardening) — Authorization on Management Endpoints**: Add a specific security requirement: "Every management and runtime configuration endpoint in an LLM gateway MUST carry an explicit authorization check (role-based or equivalent). 'Authenticated' is not synonymous with 'authorized to modify configuration.'" Reference CVE-2026-35029 and GHSA-53mr-6c8q-9789 as a case study. Include the principle that `/config/update`-style endpoints are the highest-risk authorization targets because they can alter routing, credentials, and logging destinations.

- **Chapter 05 (Security & Hardening) — Credential Storage for LLM Gateway User Accounts**: Add specific requirements:
  1. "LLM gateway user passwords MUST be stored using a strong, salted, adaptive password hashing algorithm (e.g., scrypt, bcrypt, argon2). Unsalted SHA-256 is not acceptable."
  2. "Password hashes MUST NOT be returned by any API endpoint, including user management and profile endpoints."
  3. "Login endpoints MUST hash the provided credential and compare against the stored hash. Accepting the raw (already-hashed) value as a credential eliminates the value of hashing entirely." Reference GHSA-69x8-hrgq-fjj8 as a case study for the pass-the-hash attack chain.

- **Chapter 05 (Security & Hardening) — Bug Bounty Program for LLM Infrastructure**: Document the LiteLLM bug bounty program structure ($1,500–$3,000 Critical/P0, $500–$1,500 High/P1) as a reference pattern for LLM infrastructure projects launching coordinated disclosure programs. Note that the program scope covers both the gateway and SDK.

- **Chapter 03 (Production Deployment) — Upgrade impact for security patches**: Reference v1.83.0 as the vehicle for all three fixes. Note that all three disclosures were published simultaneously with the fix, following best practice for coordinated disclosure. The three-condition impact model (auth bypass requires specific feature enablement; high-severity issues require authenticated access) is useful for triage prioritization.

## Extraction Notes

- Primary source read in full: LiteLLM blog post (2026-04-03), with all quoted passages copied character-for-character from rendered HTML. The three referenced GitHub Security Advisories (GHSA-jjhc-v7c2-5hh6, GHSA-53mr-6c8q-9789, GHSA-69x8-hrgq-fjj8) are linked but were not independently fetched — the blog post's summaries and advisory links are sufficient for this extraction.
- The blog post is a concise multi-disclosure format (~2 KB of extractable content). It covers three distinct vulnerabilities plus the bug bounty program in a single page. All three issues are fixed in the same release (v1.83.0).
- The vulnerability summaries in the blog post are prose descriptions with advisory links but no code snippets, configuration examples, or CVSS vectors. The CVSS severity labels (Critical, High) are stated in the headings but no vector strings are provided — only the advisory links where full CVSS details would be found.
- The date_published (2026-04-03) was confirmed from the page metadata. The fix version v1.83.0 is consistent with the timeline (prior to the May townhall's v1.84.1 which bundled additional fixes).
- No sub-pages were followed beyond the blog post itself. The advisory links reference the GHSA pages where full technical details (CVSS vectors, patched version ranges) would be available, but extracting those is beyond the scope of this source note since the blog post provides the vulnerability descriptions needed for the guide impact assessment.
- The `miner-related-notes.md` candidates list was read per MINER.md §4. All 10 listed candidates were evaluated:
  - `docs-langfuse-security-and-guardrails.md` — cited under Extends (shared security pattern theme at the architectural level, though Langfuse covers guardrail libraries, not authentication cache or credential storage vulnerabilities).
  - `docs-langfuse-mcp-server.md` — not cited; MCP server documentation is unrelated to these security vulnerabilities.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — not cited; AI agent definitions and guardrail principles are not directly overlapping with specific CVE-level vulnerabilities.
  - `blog-litellm-may-townhall-updates.md` — cited extensively under Corroborates (chronological successor reporting the broader security hardening outcomes of the Veria audit).
  - `docs-google-sre-reliable-product-launches.md` — not cited; launch coordination engineering is unrelated to these specific vulnerabilities.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — not cited; SLO framework is unrelated.
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` — not cited; client migration patterns are unrelated.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — not cited; config paradigms are unrelated.
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — not cited; retail/gaming SRE is unrelated.
  - `blog-litellm-april-townhall-updates.md` — not cited directly; the April townhall post covers CI/CD and product roadmap, not these specific vulnerabilities. However, the bug bounty program and Veria audit are referenced across both posts. The townhall post was excluded because its focus (CI/CD v2, product roadmap) does not overlap with the vulnerability-specific content of this note.
  Additional cross-references were discovered by reading the existing LiteLLM failure notes listed in the Prospector's triage and by searching `source-notes/` for related LiteLLM security notes.
- No contradiction issue filed: verified against all existing source notes. The three vulnerability classes in this source (OIDC cache collision, config update privilege escalation, password hash exposure) are genuinely uncovered in the corpus. No existing source note makes claims that would contradict any of these findings. The closest overlaps are with other LiteLLM failure notes that cover different CVE/incident classes — they are orthogonal, not contradictory.
