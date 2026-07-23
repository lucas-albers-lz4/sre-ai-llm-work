# Claude Code — SRE AI LLM Work

Follow [`AGENTS.md`](AGENTS.md) for remotes, pipeline, models, and hard rules.

## Claude Code specifics

- Repo agents in CI use `anthropics/claude-code-action` with Anthropic-compatible
  bases (DeepSeek or OpenRouter), **not** Claude OAuth.
- Local Claude Code in this checkout should still respect ownership boundaries:
  Miner owns `source-notes/`; Smith owns `guide/`; Assayer only reviews.
- Prefer `gh` against `lucas-albers-lz4/sre-ai-llm-work` (`origin`).
- After auth/routing changes, dispatch `claude-smoke-test.yml` (DeepSeek).
  Peak-fill / OpenRouter: `nemotron-smoke-test.yml` (needs `OPENROUTER_API_KEY`).
  Optional Hy3: `hy3-smoke-test.yml`.
- Filing a pipeline/bug/docs issue (not a source submission)? Apply **`no-triage`**
  at create time — see `AGENTS.md` hard rule 7. Do not add that guidance to
  `agents/*.md` (CI worker prompts).

## Quick pointers

- Role prompts: `agents/MINER.md`, `agents/ASSAYER.md`, `agents/SMITH.md`, …
- Workflows: `.github/workflows/`
- Configure helpers: `.github/actions/configure-deepseek/`,
  `.github/actions/configure-openrouter-hy3/` (optional Hy3 eval only)
