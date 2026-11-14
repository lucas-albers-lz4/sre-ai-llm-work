---
source_url: https://docs.litellm.ai/docs/learn/autorouter_cli
source_type: docs
title: "lite autoroute — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-10-23
last_checked: 2026-10-23
status: current
confidence_overall: emerging
issue: "#1854"
---

# lite autoroute (LiteLLM Docs)

> `lite autoroute` is a preview subcommand of the `lite` CLI that spins up a throwaway local proxy to trial LiteLLM's complexity-based auto-routing against an existing real proxy, with no `config.yaml` edit and no request bypassing the gateway; it rewrites Claude Code settings to point at the local proxy for the session and requires explicit cleanup/recovery if the process exits uncleanly.

## Source Context

- **Type**: docs (official LiteLLM product documentation, under "Developer Tools / lite CLI", labeled `Preview feature; we want your feedback`)
- **Author credibility**: Vendor-authored reference. Authoritative for CLI behavior (commands, install path, proxy forwarding, settings rewrite/restore, recovery). No benchmarks, cost numbers, or validated reliability data are provided.
- **Scope**: Quickstart for `lite autoroute configure|start|stop`; install requirements (`litellm[proxy]` from `main` via `install.sh` with `LITELLM_CLI_REF=main`); forwarding model (`every request back to your real proxy` with real key); Claude Code interception (`Routed to: <model>` in status line); lifecycle/cleanup (Ctrl-C restores settings; `lite autoroute stop` for unclean exit). Does NOT cover full routing internals, guarantees, or the separate CLI README's full caveat list beyond what is linked.

## Extracted Claims

### Claim 1: `lite autoroute` is a preview CLI harness for trying complexity-based auto-routing locally without mutating the shared proxy config
- **Evidence**: Intro states it "lets you try LiteLLM's complexity-based auto-routing locally, against models your key already has access to on your real, running proxy. It picks a cheaper or more expensive model depending on how complex a prompt looks, without editing your proxy's `config.yaml` and without any request bypassing it."
- **Confidence**: settled (documented behavior)
- **Quote**: "It lets you try LiteLLM's complexity-based auto-routing locally, against models your key already has access to on your real, running proxy. It picks a cheaper or more expensive model depending on how complex a prompt looks, without editing your proxy's `config.yaml` and without any request bypassing it."
- **Our assessment**: This is a distinct operational surface from server-side `complexity_router_config` (covered in `blog-litellm-auto-router-v2.md`). The value is trialability: per-developer experimentation against a live gateway without changing shared config. The "no request bypassing it" property is critical for governance (budgets/guardrails/fallbacks remain enforced via the real proxy).

### Claim 2: The harness runs a throwaway local proxy that forwards every request back to the real proxy, then points Claude Code at that local proxy for the session
- **Evidence**: Intro describes the architecture; step 5 says "The autorouter now automatically intercepts all Claude Code traffic" and shows `claude` run against the local proxy.
- **Confidence**: settled (documented behavior)
- **Quote**: "It stands up a throwaway local proxy that forwards every request back to your real proxy, then points Claude Code at that local proxy for the session."
- **Our assessment**: This is a local interception/proxy pattern (similar in shape to dev proxies) that rewires the client. The forwarding guarantee ("every request back to your real proxy") means the real gateway's auth/rate limits/spend tracking/guardrails apply. The trade-off is client reconfiguration with lifecycle risk (Claim 3).

### Claim 3: Claude Code settings are rewritten on start and restored on clean Ctrl-C; unclean exit leaves Claude Code pointed at a dead localhost proxy and requires `lite autoroute stop` for recovery
- **Evidence**: Step 4 states "Ctrl-C stops it and restores your Claude Code settings; if the process died any other way, `lite autoroute stop` does that cleanup." Step 5 notes interception happens for the session.
- **Confidence**: settled (documented behavior)
- **Quote**: "Start the ephemeral local proxy. It runs in the foreground and prints the proxy's request log. Ctrl-C stops it and restores your Claude Code settings; if the process died any other way, `lite autoroute stop` does that cleanup."
- **Our assessment**: This is the key operational hazard. A CLI that mutates agent client config and can leave it pointed at a dead localhost endpoint on crash/kill is a config-drift failure mode. Recovery is explicit via `lite autoroute stop`. This is guide-relevant for Chapter 06 (security/trust) and Chapter 05 (reliability). The page points to the CLI README for "recovery from an unclean shutdown and important caveats" (not fully enumerated here).

### Claim 4: Installation requires the full proxy runtime from `main` via `install.sh` with `LITELLM_CLI_REF=main`; the thin `install-cli.sh` (`litellm[cli]`) is insufficient and `uv` is bootstrapped if missing
- **Evidence**: Step 1 gives the curl command and explanation.
- **Confidence**: settled (documented install requirement)
- **Quote**: "`lite autoroute start` runs a throwaway proxy on your machine, so it needs the full proxy runtime: the thin `install-cli.sh` one-liner from the [CLI quick start](/docs/proxy/management_cli#quick-start) installs only `litellm[cli]`, which is not enough here, and the command below replaces that install. It installs `litellm[proxy]` from `main` with a single curl command; `uv` is bootstrapped automatically if it is missing."
- **Our assessment**: Unpinned-from-release install path (`main`) for a tool that intercepts all coding-agent traffic is a provenance/reproducibility concern (relevant to trust/supply chain). Operators need to be aware of tracking `main` rather than a release tag.

### Claim 5: Configuration is key-scoped — `lite autoroute configure` discovers model groups the key can reach and asks to assign models to each complexity tier
- **Evidence**: Step 3 describes the wizard.
- **Confidence**: settled (documented behavior)
- **Quote**: "Run the interactive wizard. It discovers the model groups your key can reach and asks you to assign models to each complexity tier."
- **Our assessment**: This differs from server-side `config.yaml` tier definitions (global config). Tier assignment is driven by key-scoped discovery, enabling per-developer trial without changing shared routing config. This matches the "route tuning without mutating shared config" pattern.

### Claim 6: The feature is explicitly a preview with no benchmarks, cost numbers, or routing-quality guarantees; feedback is solicited via GitHub discussion
- **Evidence**: Preview callout and lack of metrics on page.
- **Confidence**: settled (documented status)
- **Quote**: "Preview feature; we want your feedback"
- **Our assessment**: All behavior should be treated as unsettled. The page defers full configuration reference to Auto Routing docs and important caveats to the CLI README.

## Concrete Artifacts

Verbatim from https://docs.litellm.ai/docs/learn/autorouter_cli (fetched 2026-10-23).

### Install command
```bash
curl -fsSL https://raw.githubusercontent.com/BerriAI/litellm/main/scripts/install.sh | \
  LITELLM_CLI_REF=main sh
```

### Environment setup
```bash
export LITELLM_PROXY_URL=http://localhost:4000
export LITELLM_PROXY_API_KEY=sk-...
```

### Configure/start/stop flow
```bash
lite autoroute configure
lite autoroute start
lite autoroute stop  # recovery for unclean exit
```

### Usage
```bash
claude
# Claude Code status line shows: Routed to: <model>
```

## Cross-References

- **Corroborates**:
  - `blog-litellm-auto-router-v2.md` — Covers server-side complexity-based routing (`auto_router/complexity_router`, tiers). This CLI is a client-side trial harness for that routing engine (same complexity-based routing concept), not a duplicate. Confirms complexity routing exists as a routing mode.
  - `blog-litellm-save-claude-code-costs.md` — Mentions complexity router as one of three auto-routing flavors for Claude Code cost reduction. This page provides the concrete operational mechanism (local proxy + settings rewrite) for trying it.

- **Contradicts**: None identified.
- **Extends**:
  - `blog-litellm-auto-router-v2.md` — Extends from server-side config surface to a per-developer trial mechanism that requires no `config.yaml` changes; adds lifecycle/cleanup details (settings restore, `lite autoroute stop`) absent from the blog post.
- **Novel** (new to the corpus):
  - **Client-side interception trial harness**: `lite autoroute` stands up a throwaway local proxy forwarding to real proxy with Claude Code settings rewrite/restore — no request bypasses gateway, no shared config mutation.
  - **Lifecycle/cleanup hazard**: Clean exit via Ctrl-C restores settings; unclean exit leaves Claude Code pointed at dead localhost proxy requiring `lite autoroute stop`.
  - **Install provenance**: Requires `litellm[proxy]` from `main` via `install.sh` with `LITELLM_CLI_REF=main` (thin `litellm[cli]` insufficient), `uv` bootstrapped if missing.
  - **Key-scoped tier discovery**: `configure` discovers model groups the key can reach and assigns tiers per-key rather than from shared config.

## Guide Impact

- **Chapter 05 (LLM Ops — Routing/Reliability)**: Add `lite autoroute` as a pre-production trial harness pattern for complexity routing — enables safe experimentation without mutating shared gateway config. Document the forwarding guarantee (all traffic through real proxy) so governance remains intact.
- **Chapter 06 (Security/Trust — Client Configuration)**: Add the settings-rewrite/restore failure mode as a config-drift hazard. Document recovery via `lite autoroute stop` and the risk of leaving an agent client pointed at a dead localhost proxy after crash/kill. Note install path uses `main` (provenance consideration).
- **Chapter 02 (Architecture — Proxy Patterns)**: Note the local-interception pattern (ephemeral local proxy forwarding upstream) as a developer-experience pattern distinct from server-side routing config.

## Extraction Notes

- Source fetched via webfetch from https://docs.litellm.ai/docs/learn/autoroute_cli on 2026-10-23. Read in full.
- Page is a short quickstart (5 steps). Treated as preview feature with emerging confidence; no benchmarks/cost data present so not inferred.
- Quotes copied verbatim from rendered content. Followed MINER.md §2a.
- Checked `miner-related-notes.md` candidates — all appeared unrelated to this CLI/interception pattern; dismissed explicitly. Also searched existing notes (no existing coverage of `lite autoroute`/`autorouter_cli` found).
- No contradiction identified; did not file contradiction issue.
