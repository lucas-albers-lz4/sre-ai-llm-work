# Sources

Master index of every source this guide cites. Empty at MVP bootstrap — the
Miner and Smith populate this as notes merge.

| Source | Type | Notes |
|--------|------|-------|
| docs-google-sre-prodcast-01-09-postmortems | discussion | Google SRE Prodcast S1E09: postmortem definition, blamelessness, when-to-write rubric, action-item hygiene |
| docs-google-sre-reliable-data-processing-minimal-toil | docs | Google SRE paper: batch-job safety levels, staged release pipeline, population canarying, freshness/correctness SLOs |
| docs-google-sre-engagement-model | docs | Google SRE Workbook Ch18: 7-phase service-lifecycle engagement model, NYT shared-goals, "as quickly as is safe" pledge, SRE-to-developer ratio, hand-back conditions |
| docs-google-sre-incident-response | docs | Google SRE Workbook Ch9: resolve-vs-manage split, IC/CL/OL roles, declare-early, generic mitigations, mitigation-first, PagerDuty IR process and tooling, drills |
| docs-google-sre-on-call | docs | Google SRE Workbook Ch8: two-incident pager budget, pager-load anatomy, response-time tiers, gated alert introduction, staffing, shift/scheduling rules |
| docs-google-sre-postmortem-analysis | docs | Google SRE Workbook Appendix C: 68% push-driven outage triggers, root-cause taxonomy, standard-template → trend-analysis mechanism |
| docs-google-sre-reaching-beyond-walls | docs | Google SRE Workbook Ch19: platform reliability partnership, five-step customer-SRE methodology, tenant-selection frameworks |
| docs-google-sre-simplicity | docs | Google SRE Workbook Ch7: five systems-level complexity proxies, complexity-as-externality, simplification management (10% budget, celebrate code deletion, rotating whole-stack group), structured tool contracts (bag vs Protocol Buffers), shared-platform → tiered engagement |
| docs-google-sre-slo-engineering-case-studies | docs | Google SRE Workbook Ch3: Evernote/THD SLO adoption — SLI measurement design, VALET framework, TPS Reports SLI automation, error-budget prioritization, shared-SLO provider partnership, org-change mechanics |
| docs-google-sre-team-lifecycles | docs | Google SRE Workbook Ch20: three SRE principles, first-SRE hiring/embedding, Tuckman team formation, NYT in-place conversion, scaling to many teams, 1:5–1:50 staffing ratio, workload hand-back |
| docs-langfuse-agent-skill | docs | Langfuse vendor docs: the shipped Agent Skill — a SKILL.md + references/ folder implementing the open Agent Skills standard, progressive disclosure, install surfaces (skills CLI, Cursor plugin, clone+symlink), and the allowed-tools frontmatter allowlist |
| docs-langfuse-alerts | docs | Langfuse vendor docs: the shipped Alerts feature — score/metric-driven alert conditions, two-threshold ladder, severity state machine with per-transition notify semantics, no-data modes, renotify, delivery-failure circuit breaker, HMAC webhook schema, GitHub Actions workflow_dispatch channel |
| docs-langfuse-cli | docs | Langfuse vendor docs: the CLI wrapping the full OpenAPI-generated API — machine-readable exit-code taxonomy (usage/config/network/HTTP/local), env-var-only auth shared with the SDKs, editor-agent and CI/CD scripting use cases |
