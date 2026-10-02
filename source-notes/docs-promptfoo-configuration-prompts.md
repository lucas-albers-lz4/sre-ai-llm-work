---
source_url: https://www.promptfoo.dev/docs/configuration/prompts
source_type: docs
title: "Promptfoo Configuration: Prompts — Formats, Executable Generators, and External Registry Schemes"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-01
date_extracted: 2026-10-02
last_checked: 2026-10-02
status: current
confidence_overall: emerging
issue: "#1544"
---

# Promptfoo Configuration: Prompts

> Defines the prompt specification surface in promptfoo — inline strings, file-based prompts, multi-turn chat JSON, executable scripts that generate prompts, external prompt-management URIs (Langfuse/Portkey/Helicone), prompt labels/IDs and provider→prompt mapping, and debugging via rendered prompt inspection.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Configuration > Prompts" page)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor. Authoritative for product syntax and documented behavior; but vendor documentation contains no measured evidence (no eval traces, no reproduction runs, no incidents). All security/behavior claims are documented intent, not observed operational data.
- **Scope**: Covers prompt definition formats (.txt/.md/.j2/.csv with `---` separator and `PROMPTFOO_PROMPT_SEPARATOR` override, globs), chat-JSON multi-turn prompts, JavaScript/Python prompt functions, executable scripts via `exec:` (including security warnings), external prompt management via URI schemes (`langfuse://`, `portkey://`, `helicone://`), prompt IDs/labels, model-specific/provider→prompt mapping with filter semantics, `nunjucksFilters`, and viewing rendered prompts (`promptfoo view` with "Show full prompt in output cell").
- **Out of scope**: Assertion types, output transforms, caching (covered in other configuration pages). The page explicitly notes Python files (`.py`) are processed as Python prompt templates, not executables (use `exec:` prefix to run as executable).
- **Last updated**: Oct 1, 2026 (per footer in page); current as of extraction date.

## Extracted Claims

### Claim 1: Executable scripts run with the full permissions of the promptfoo process and can access environment variables including API keys
- **Evidence**: Security Considerations warning block under "Executable Scripts" section documenting process permissions, user-controlled `vars` as input, trusted-sources requirement, and environment access.
- **Confidence**: anecdotal (vendor warning; no incident data or measured blast radius provided)
- **Quote**: "Executable scripts run with full permissions of the promptfoo process. Be mindful of: User Input: Scripts receive user-controlled vars as JSON. Always validate and sanitize inputs before using them in commands. Untrusted Scripts: Only run scripts from trusted sources. Scripts can access files, make network calls, and execute commands. Environment Access: Scripts can access environment variables, including API keys. Timeout: Configure a timeout via config.timeout (default: 60 seconds) to prevent hanging scripts."
- **Our assessment**: This is an important trust-boundary claim: an eval config that includes an `exec:` prompt generator is executable code, not just declarative templates. The warning correctly frames `vars` as user-controlled JSON. However, the documentation provides no concrete hardening guidance (e.g., sandboxing, path constraints, least-privilege) beyond "only run trusted scripts" and timeouts. Confidence appropriately marked anecdotal given lack of empirical evidence.

### Claim 2: Executable prompts are invoked via `exec:` (explicit) or auto-detected for common script extensions; Python `.py` files are not auto-treated as executables
- **Evidence**: Usage examples showing explicit `exec:./generator.sh`/`exec:/usr/bin/my-prompt-tool` forms, and note that `.sh`, `.bash`, `.rb`, `.pl` are auto-detected when referenced directly; Python `.py` requires `exec:` prefix.
- **Confidence**: settled (documented syntax)
- **Quote**: "Or just reference the script directly (auto-detected for .sh, .bash, .rb, .pl, and other common script extensions):" and "Python files (.py) are processed as Python prompt templates, not executables. To run a Python script as an executable prompt, use the exec: prefix: exec:./generator.py"
- **Our assessment**: Syntax distinction matters operationally — teams might assume `.py` referenced directly becomes executable; the page explicitly corrects this. This prevents accidental misclassification between template-style Python prompt functions and arbitrary script execution.

### Claim 3: External prompt management via URI schemes supports version pinning and label-based references (Langfuse/Portkey/Helicone)
- **Evidence**: "External Prompt Management Systems" section with concrete URI examples for Langfuse, Portkey, and Helicone showing both numeric version references and label-based references (`@production`, `@staging`, `@latest`).
- **Confidence**: settled (documented URI forms)
- **Quote**: "Langfuse is an open-source LLM engineering platform with collaborative prompt management: ... # Reference by version (numeric values) - langfuse://my-prompt:3:text - langfuse://chat-prompt:1:chat ... # Reference by label using @ syntax (recommended for clarity) - langfuse://my-prompt@production - langfuse://chat-prompt@staging:chat - langfuse://email-template@latest:text"
- **Our assessment**: Version pinning (`:3`) vs floating labels (`@production`, `@latest`) is operationally significant for reproducibility. A CI gate pinned to a specific version remains stable; a gate referencing a floating label can change behavior without config changes. This is directly relevant to drift control in eval/CI contexts.

### Claim 4: Langfuse URI syntax accepts both `@label` and colon-form string labels; format suffixes (`:text`, `:chat`) control prompt format
- **Evidence**: Langfuse examples showing format suffixes and two label syntaxes (`@production` vs colon with string detection).
- **Confidence**: settled (documented)
- **Quote**: "# Reference by label using : syntax (auto-detected strings) - langfuse://my-prompt:production # String detected as label - langfuse://chat-prompt:staging:chat # String detected as label"
- **Our assessment**: The page documents both forms; recommends `@` for clarity. The `:text`/`:chat` suffix explicitly selects the prompt format when the external prompt might be stored in multiple forms. This is a small but necessary detail for parsing correctness.

### Claim 5: Portkey and Helicone also expose external prompt URIs; Helicone examples show versioned references like `:1.0`, `:2.5`
- **Evidence**: Portkey examples (`portkey://pp-customer-support-v2`, `portkey://pp-email-generator-prod`) and Helicone examples with numeric versions.
- **Confidence**: settled (documented)
- **Quote**: "Helicone offers prompt management alongside observability features: prompts: - helicone://greeting-prompt:1.0 - helicone://support-chat:2.5"
- **Our assessment**: Confirms external registry surface across multiple vendors; version semantics appear consistent (numeric/string after colon). Variables from test cases are passed through to external prompts.

### Claim 6: Prompt selection supports model-specific mapping via provider `prompts` arrays and label-based filtering (exact, group prefix, `group:*` wildcard)
- **Evidence**: "Model-Specific Prompts" section showing different prompts attached to different providers via `prompts: [gpt_prompt]` / `[claude_prompt]`, and the filter semantics description.
- **Confidence**: settled (documented)
- **Quote**: "Prompt filters match labels exactly, support group prefixes (e.g. group matches group:...), and allow wildcard prefixes like group:*. The prompts field also works when providers are defined in external files (file://provider.yaml)."
- **Our assessment**: The ability to route different prompt definitions to different providers under the same eval config is key for multi-model regression runs. The filtering semantics (prefix/wildcard on labels) mean a rename or re-labeling can silently change which prompts run for which providers — an operational footgun worth surfacing.

### Claim 7: File-based prompts support multiple formats (.txt/.md/.j2/.csv), globs, and multi-prompt files separated by `---` with override via `PROMPTFOO_PROMPT_SEPARATOR`
- **Evidence**: "Supported File Formats", "Multiple Prompts in One File", "Using Globs" sections. Documents CSV label column behavior; `.md` and `.j2` (Jinja2) templates supported; multi-prompt splitting with `---`.
- **Confidence**: settled (documented)
- **Quote**: "In .txt files, put --- on its own line between prompts: ... To keep --- lines inside a prompt, choose a different separator in your config: env: PROMPTFOO_PROMPT_SEPARATOR: '%%%'. Use %%% on its own line between prompts."
- **Our assessment**: Separator override is necessary to avoid collisions when prompt content legitimately contains `---`. The CSV behavior (label column takes precedence; single-row keeps entry label) is documented but subtle. Globs allow loading multiple files as a prompt set.

### Claim 8: `nunjucksFilters` allows registering custom Nunjucks filters from external JS files
- **Evidence**: "Advanced Features" / filters section showing `nunjucksFilters` mapping to JS file paths and usage in templates.
- **Confidence**: settled (documented)
- **Quote**: "promptfooconfig.yaml\nnunjucksFilters:\n  uppercaseFirst: ./uppercase_first.js\nprompts:\n  - 'Dear {{ name | uppercaseFirst }}, {{ message }}'"
- **Our assessment**: Extends templating power; custom filters are defined in external JS files (another code execution surface if sourced from untrusted locations), though the page does not call this out as a security concern — contrast with explicit exec script warnings.

### Claim 9: Rendered prompt inspection is available via `promptfoo view` and "Show full prompt in output cell"
- **Evidence**: "Viewing Final Prompts" section instructs running `promptfoo view` and enabling the UI option to see the rendered prompt after variable substitution.
- **Confidence**: settled (documented)
- **Quote**: "To see the final rendered prompts: Run promptfoo view. Enable Table Settings > Show full prompt in output cell. This shows exactly what was sent to each provider after variable substitution."
- **Our assessment**: Important operational/debugging capability — lets operators verify what was actually sent (critical when using external registries, exec scripts, or complex templating). Supports reproducibility/debugging of eval runs.

## Concrete Artifacts

### Executable script with timeout and security note
```yaml
prompts:
  - label: 'Technical Prompt'
    raw:
      exec:
        ./generator.sh
    config:
      style: technical
      verbose: true
```
*(Attribution: Promptfoo docs "Executable Scripts" — shows passing config to exec script; security considerations note timeout default 60s.)*

### External prompt registry URIs (Langfuse)
```yaml
prompts:
  # Reference by version (numeric values)
  - langfuse://my-prompt:3:text
  - langfuse://chat-prompt:1:chat
  # Reference by label using @ syntax (recommended for clarity)
  - langfuse://my-prompt@production
  - langfuse://chat-prompt@staging:chat
  - langfuse://email-template@latest:text
```
*(Attribution: Promptfoo docs "Langfuse" section.)*

### Model-specific prompt routing
```yaml
prompts:
  - id: file://prompts/gpt_prompt.json
    label: gpt_prompt
  - id: file://prompts/claude_prompt.txt
    label: claude_prompt
providers:
  - id: openai:gpt-4o
    prompts: [gpt_prompt]
  - id: anthropic:claude-sonnet-5
    prompts: [claude_prompt]
```
*(Attribution: Promptfoo docs "Model-Specific Prompts".)*

### Multi-prompt file with custom separator
```yaml
env:
  PROMPTFOO_PROMPT_SEPARATOR: '%%%'

# prompts.txt uses %%% between prompts
```
*(Attribution: Promptfoo docs "Multiple Prompts in One File".)*

### Custom Nunjucks filters
```yaml
nunjucksFilters:
  uppercaseFirst: ./uppercase_first.js
prompts:
  - 'Dear {{ name | uppercaseFirst }}, {{ message }}'
```
*(Attribution: Promptfoo docs "Advanced Features".)*

## Cross-References

- **Corroborates**: `docs-promptfoo-configuration-guide.md` (#1513) — hub page that links to this page and defers prompt specification details here (as noted in triage). Also relates to external prompt management patterns seen in `docs-langfuse-prompt-management.md`, `docs-litellm-generic-prompt-management-api.md` (external prompt stores; this page documents promptfoo's client-side URI consumption).
- **Contradicts**: None identified. (The executable-prompt trust boundary guidance does not conflict with existing corpus claims; it adds a new operational surface.)
- **Extends**: `docs-promptfoo-configuration-guide.md` (#1513) by filling in the missing prompt-format matrix and external registry URI schemes that the earlier pass dismissed/overlooked (as noted in triage comments).
- **Novel**: The page is the first corpus source documenting promptfoo's external prompt registry URI schemes (`langfuse://`, `portkey://`, `helicone://`) with version vs label forms, the explicit exec-vs-template split for Python files, and the security warning that executable prompts inherit full process permissions with access to env/API keys in the context of promptfoo's prompt configuration surface.

## Guide Impact

- **Chapter 05 (LLM ops reliability)**: Should capture that prompt definitions in eval configs may be non-deterministic inputs when sourced via floating external registry labels (`@production`, `@latest`) or via executable generators; recommend pinning to explicit versions for CI gates to ensure reproducible green/red signals.
- **Chapter 06 (security and trust)**: Add guidance treating `prompts:` entries with `exec:` as code execution boundaries. Highlight that `vars` are user-controlled JSON passed to scripts, scripts run with full process permissions and can access env (including API keys) — so executable prompt generators must come from trusted sources, be reviewed, and run with appropriate timeouts/hardening in CI. Also note custom Nunjucks filters as another code surface.

## Extraction Notes

- Extracted via HTML fetch of https://www.promptfoo.dev/docs/configuration/prompts (Oct 2026). Focused on executable scripts (security), external registries (pinning semantics), prompt selection/mapping, file formats/separators, and rendered-prompt debugging — areas called out as high-value in triage. Skipped pure file-loading mechanics already covered broadly. No paywall encountered; content complete.
- Vendor documentation only — no measured evidence or incident reports. Confidence marked `emerging` overall; specific behavior claims marked accordingly in the note.
