# Principles

> Mental models for using AI/LLMs in SRE work — and for treating LLM systems
> as production dependencies that need reliability engineering.

This chapter is a stub for MVP. The Smith fills it from source notes. Until
then, hold these working principles as `[editorial]`:

## Working principles (seed)

1. **Verification over generation.** AI can draft hypotheses faster than you
   can validate them against dashboards, traces, and blast radius. The scarce
   resource is confirmation, not text. `[editorial]`

2. **Keep humans on the paging path until trust is earned.** Shadow → suggest →
   act, never the reverse. `[editorial]`

3. **Encode ops knowledge outside the chat.** Runbooks, SLOs, and service
   catalogs beat prompt folklore. `[editorial]`

4. **Toil reduction must not create silent failure modes.** If an agent
   "fixes" something, the change must be observable and reversible. `[editorial]`

5. **LLM services need SLOs too.** Latency, error rate, eval drift, and cost
   are first-class reliability signals. `[editorial]`

---

*No sourced claims yet. Submit sources via issues; the pipeline will grow this chapter.*
