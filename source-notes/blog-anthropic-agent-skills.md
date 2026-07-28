---
source_url: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
source_type: blog-post
title: "Equipping agents for the real world with Agent Skills"
author: "Barry Zhang, Keith Lazuka, and Mahesh Murag (Anthropic Engineering)"
date_published: 2025-10-16
date_extracted: 2026-07-28
last_checked: 2026-07-28
status: current
confidence_overall: emerging
issue: "#608"
---

# Equipping agents for the real world with Agent Skills

> Anthropic Engineering introduces Agent Skills — a filesystem-based format
> (SKILL.md with YAML frontmatter, progressive disclosure across three levels,
> bundled Python scripts as executable tools) for packaging procedural knowledge
> into reusable, dynamically-loadable agent capabilities. Published October 2025;
> updated December 2025 as an open standard at agentskills.io.

## Source Context

- **Type**: blog-post (practitioner writeup from model provider)
- **Author credibility**: Highest available for the subject matter — Anthropic
  Engineering, the creators of Claude, writing about a new product they built
  and shipped. Authors (Barry Zhang, Keith Lazuka, Mahesh Murag) are named
  engineers at Anthropic. The post is a primary-source announcement of a new
  capability that was concurrently launched across Claude.ai, Claude Code,
  the Claude Agent SDK, and the Claude Developer Platform. Published Oct 16,
  2025 and updated Dec 18, 2025 when it was published as an open standard at
  agentskills.io.
- **Scope**: Covers (1) the definition of Agent Skills and their relationship
  to tools, prompts, and reusable agent capabilities; (2) the anatomy of a
  skill (SKILL.md, YAML frontmatter, progressive disclosure via linked files);
  (3) skills and the context window (how skills are triggered and loaded at
  runtime); (4) skills and code execution (deterministic Python scripts as
  tools); (5) best practices for authoring and evaluating skills; (6) security
  considerations. Does NOT cover: quantitative benchmarks, comparison to other
  agent-packaging formats (MCP, Langfuse Skills, etc.), failure rates, or
  operational metrics from production deployments of Agent Skills.

## Extracted Claims

### Claim 1: Agent Skills are organized folders of instructions, scripts, and resources that agents can discover and load dynamically to perform better at specific tasks
- **Evidence**: The post defines Agent Skills in its opening section with a
  concrete description of what they contain and how agents use them.
- **Confidence**: settled
- **Quote**: "This led us to create Agent Skills: organized folders of
  instructions, scripts, and resources that agents can discover and load
  dynamically to perform better at specific tasks."
- **Our assessment**: This is the core definition. The key design elements are
  (a) filesystem folders as the packaging unit, (b) dynamic discovery and
  loading rather than pre-loaded context, (c) instructions, scripts, and
  resources as the contents. The post grounds this in a concrete example (the
  PDF skill for form-filling) and a real deployment (Claude's document editing
  abilities).

### Claim 2: A skill is a directory containing a SKILL.md file with YAML frontmatter containing required metadata (name and description)
- **Evidence**: The post describes the anatomy of a skill and shows a diagram
  of the SKILL.md file format.
- **Confidence**: settled
- **Quote**: "At its simplest, a skill is a directory that contains a SKILL.md
  file. This file must start with YAML frontmatter that contains some required
  metadata: name and description."
- **Our assessment**: The YAML frontmatter is the structural foundation. The
  `name` and `description` are the minimum required fields. This is a concrete
  format specification that can be directly implemented.

### Claim 3: At startup, the agent pre-loads only the name and description of every installed skill into its system prompt — this is the first level of progressive disclosure
- **Evidence**: The post explicitly describes the startup behavior and the
  progressive disclosure design principle.
- **Confidence**: settled
- **Quote**: "At startup, the agent pre-loads the name and description of every
  installed skill into its system prompt."
- **Our assessment**: This is the critical performance and context-window design
  decision. By loading only metadata at startup, the system can support many
  installed skills without consuming context window space for content that may
  not be needed in the current task. The agent only reads the full SKILL.md
  when it determines the skill is relevant.

### Claim 4: Progressive disclosure has three levels — metadata (level 1, loaded at startup), the SKILL.md body (level 2, loaded when the agent determines relevance), and linked files within the skill directory (level 3 and beyond, loaded on demand)
- **Evidence**: The post describes and diagrams all three levels with the PDF
  skill example.
- **Confidence**: settled
- **Quote**: "This metadata is the first level of progressive disclosure: it
  provides just enough information for Claude to know when each skill should be
  used without loading all of it into context. The actual body of this file is
  the second level of detail. If Claude thinks the skill is relevant to the
  current task, it will load the skill by reading its full SKILL.md into
  context."
- **Quote**: "These additional linked files are the third level (and beyond) of
  detail, which Claude can choose to navigate and discover only as needed."
- **Our assessment**: Progressive disclosure is the core design principle that
  makes skills scalable. The post compares it to a "well-organized manual that
  starts with a table of contents, then specific chapters, and finally a
  detailed appendix." The amount of context bundled into a skill is described
  as "effectively unbounded" because the agent with filesystem access does not
  need to read everything at once.

### Claim 5: Skills can include code (pre-written Python scripts) for Claude to execute as tools, which is more efficient and reliable than LLM token generation for operations like sorting or PDF form-field extraction
- **Evidence**: The post describes code execution in skills with the PDF skill
  example, contrasting deterministic code vs LLM generation.
- **Confidence**: settled
- **Quote**: "Large language models excel at many tasks, but certain operations
  are better suited for traditional code execution. For example, sorting a list
  via token generation is far more expensive than simply running a sorting
  algorithm."
- **Quote**: "In our example, the PDF skill includes a pre-written Python script
  that reads a PDF and extracts all form fields. Claude can run this script
  without loading either the script or the PDF into context. And because code is
  deterministic, this workflow is consistent and repeatable."
- **Our assessment**: This is an important architectural claim — skills bridge
  the gap between LLM capabilities and deterministic computation. The post
  positions code-as-tool as a conscious design choice: use LLMs for reasoning
  about when to act, use code for the action itself. This is consistent with
  the earlier "Building effective agents" post's simplicity-first philosophy.

### Claim 6: Recommended practice — start with evaluation by identifying specific gaps in agent capabilities on representative tasks, then build skills incrementally
- **Evidence**: Listed as the first guideline in the "Developing and evaluating
  skills" section.
- **Confidence**: emerging
- **Quote**: "Start with evaluation: Identify specific gaps in your agents'
  capabilities by running them on representative tasks and observing where they
  struggle or require additional context. Then build skills incrementally to
  address these shortcomings."
- **Our assessment**: This is a measurement-first approach to skill authorship.
  The guidance is to not pre-build skills speculatively, but to identify real
  gaps empirically. This aligns with the simplicity-first ethos of the earlier
  building-effective-agents post.

### Claim 7: Recommended practice — when SKILL.md becomes unwieldy, split content into separate files; mutually exclusive or rarely-used contexts should be kept in separate paths to reduce token usage
- **Evidence**: Listed as the second guideline in the "Developing and evaluating
  skills" section.
- **Confidence**: emerging
- **Quote**: "Structure for scale: When the SKILL.md file becomes unwieldy, split
  its content into separate files and reference them. If certain contexts are
  mutually exclusive or rarely used together, keeping the paths separate will
  reduce the token usage."
- **Our assessment**: Practical guidance for managing context window efficiency.
  The principle of separating mutually-exclusive contexts into separate paths
  mirrors the same design insight found in PagerDuty's SRE Agent routing layer
  (direct relevant context, skip irrelevant context). The post also notes that
  code can serve "as both executable tools and as documentation."

### Claim 8: Recommended practice — monitor how Claude uses the skill in real scenarios and iterate based on observations; pay special attention to name and description since Claude uses these to decide whether to trigger the skill
- **Evidence**: Listed as the third guideline.
- **Confidence**: emerging
- **Quote**: "Think from Claude's perspective: Monitor how Claude uses your skill
  in real scenarios and iterate based on observations: watch for unexpected
  trajectories or overreliance on certain contexts. Pay special attention to the
  name and description of your skill. Claude will use these when deciding
  whether to trigger the skill in response to its current task."
- **Our assessment**: This is a UX-for-agents principle. The name and description
  are the critical trigger signals — if they are poorly chosen, the agent will
  either miss opportunities to use the skill or load it inappropriately. This is
  the skill analog of ACI (Agent-Computer Interface) tool design from the
  earlier building-effective-agents post.

### Claim 9: Recommended practice — ask Claude to capture its successful approaches and common mistakes into reusable context and code within a skill; if it goes off track, ask it to self-reflect
- **Evidence**: Listed as the fourth guideline.
- **Confidence**: emerging
- **Quote**: "Iterate with Claude: As you work on a task with Claude, ask Claude
  to capture its successful approaches and common mistakes into reusable context
  and code within a skill. If it goes off track when using a skill to complete a
  task, ask it to self-reflect on what went wrong."
- **Our assessment**: This is a participatory skill-authoring workflow where the
  agent contributes to its own skill definitions. The post frames this as a way
  to "discover what context Claude actually needs, instead of trying to
  anticipate it upfront." This suggests a feedback loop where skills evolve
  through actual usage rather than upfront specification.

### Claim 10: Skills should only be installed from trusted sources; when installing from a less-trusted source, audit all bundled files, paying attention to code dependencies and instructions that connect to external network sources
- **Evidence**: Dedicated "Security considerations when using Skills" section.
- **Confidence**: settled
- **Quote**: "We recommend installing skills only from trusted sources. When
  installing a skill from a less-trusted source, thoroughly audit it before use.
  Start by reading the contents of the files bundled in the skill to understand
  what it does, paying particular attention to code dependencies and bundled
  resources like images or scripts. Similarly, pay attention to instructions or
  code within the skill that instruct Claude to connect to potentially untrusted
  external network sources."
- **Our assessment**: The security model is straightforward — skills are
  instructions + code, so malicious skills can direct the agent to exfiltrate
  data or take unintended actions. The recommendation is defense-in-depth at the
  installation layer rather than runtime sandboxing. This is consistent with the
  broader agent-security corpus (e.g., Promptfoo's prompt injection findings)
  where instruction-following models can be directed to harmful actions by
  untrusted content.

### Claim 11: Skills complement MCP servers by teaching agents more complex workflows that involve external tools and software
- **Evidence**: Mentioned in the "The future of Skills" section.
- **Confidence**: emerging
- **Quote**: "We'll also explore how Skills can complement Model Context Protocol
  (MCP) servers by teaching agents more complex workflows that involve external
  tools and software."
- **Our assessment**: This positions Skills as a higher-level abstraction than
  MCP — MCP provides tools/servers, while Skills provide the workflow knowledge
  of HOW to use those tools. This is a notable architectural insight: skills
  package procedural knowledge (how to accomplish a task using tools), while
  MCP provides the tools themselves.

### Claim 12: Agent Skills were published as an open standard for cross-platform portability in December 2025
- **Evidence**: An update notice at the top of the post, plus a link to
  agentskills.io.
- **Confidence**: settled
- **Quote**: "Update: We've published Agent Skills as an open standard for
  cross-platform portability. (December 18, 2025)"
- **Our assessment**: This transforms the post from a product announcement to a
  standard specification. As of the December 2025 update, Agent Skills are not
  vendor-locked to Anthropic — any platform can implement the SKILL.md format.
  This is relevant to the guide's discussion of portable agent capabilities.

## Concrete Artifacts

### SKILL.md anatomy (reconstructed from the post's description and diagrams)

```
skill-directory/
├── SKILL.md              # Required: YAML frontmatter + body
│   └── YAML frontmatter:
│       name: <skill-name>
│       description: <one-line description>
├── reference.md          # Optional: additional reference context (level 3)
├── forms.md              # Optional: specialized instructions (level 3)
└── scripts/
    └── extract_fields.py # Optional: executable Python scripts
```

### Three-level progressive disclosure model

```
Level 1 (startup — loaded into system prompt):
  name + description for each installed skill
  Agent decides: "is this skill relevant to the current task?"

Level 2 (on demand — full SKILL.md body):
  Agent reads the full SKILL.md into context
  Contains core instructions, references to linked files

Level 3+ (on demand — linked files):
  Agent reads reference.md, forms.md, etc.
  Only when the specific sub-task is relevant
```

### Skill-triggering context window sequence (from the post)

```
1. Context window has: core system prompt + skill metadata (name/description)
   for all installed skills + user's initial message
2. Claude triggers a skill by invoking a Bash tool to read `skill/SKILL.md`
3. Claude optionally reads bundled files (e.g. `forms.md`)
4. Claude proceeds with the task using loaded skill instructions
```

### Developer guidelines (verbatim from the post)

```
- Start with evaluation: Identify specific gaps in your agents' capabilities
  by running them on representative tasks and observing where they struggle
- Structure for scale: When SKILL.md becomes unwieldy, split content into
  separate files
- Think from Claude's perspective: Monitor how Claude uses your skill in real
  scenarios; pay attention to name and description
- Iterate with Claude: Ask Claude to capture its successful approaches and
  common mistakes into reusable context and code within a skill
```

## Cross-References

- **Corroborates**:
  - `blog-anthropic-building-effective-agents.md` **Claim 3** (simplicity-first:
    start simple, add complexity only when needed). The skill format's progressive
    disclosure and filesystem-based design embody the same simplicity principle —
    skills are "a simple concept with a correspondingly simple format."
    **Claim 8** (ACI tool design is as important as prompt design). Skill name and
    description as trigger signals (Claim 8 in this note) is a direct application
    of ACI principles to skill design.

- **Distinguish** (term disambiguation):
  - `docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md` **Claim 6-8**.
    Google's "skills" model (capabilities on a coding harness called Antigravity,
    used for automated code migrations) uses the same term but describes a
    fundamentally different concept. Google's skills are harness-based capabilities
    written as code on a platform, while Anthropic's Agent Skills are
    filesystem-format instructions with progressive disclosure. Both package agent
    capabilities, but the mechanisms are architecturally different. This note
    covers Anthropic's filesystem-based skills; the Zelesko note covers the
    Google/Antigravity harness-based approach.

- **Extends**:
  - `blog-anthropic-building-effective-agents.md` — The earlier post provides the
    architectural taxonomy (workflow patterns, ACI principles). This post adds a
    concrete mechanism for packaging the procedural knowledge that those patterns
    operate on. Together they form a complete picture: what patterns to build
    (earlier) and how to package knowledge for reuse (this post).
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — Google's practitioner account
    of building AI agents for SRE describes agent capabilities (read/write,
    pre-on-caller triage, evaluation methodology) that would benefit from the
    structured skill packaging format this post introduces.

- **Novel**: To the corpus, this source introduces:
  - The **Agent Skills filesystem format** (SKILL.md with YAML frontmatter,
    linked files, executable scripts) — a concrete packaging standard for agent
    procedural knowledge
  - **Progressive disclosure as a design principle** for agent context loading —
    metadata → body → linked files, with effectively unbounded total context
  - **Code-as-tool within skills** — deterministic Python scripts embedded as
    agent tools within skill directories, bridging LLM reasoning and deterministic
    computation
  - **Skill authorship workflow** — start with eval, structure for scale, think
    from agent's perspective, iterate with Claude
  - **Security model for skills** — trust at install time, audit instructions
    and code
  - **Skills-MCP complementarity** — skills teach *workflows* over tools, MCP
    provides the tools
  - The **open standard** (agentskills.io) — cross-platform portability announced
    Dec 2025

## Guide Impact

- **Chapter 00 (Principles)**: Add the progressive disclosure principle as a
  general agent design pattern — load only what's needed, when it's needed. The
  "simple format, powerful results" framing supports the existing simplicity-first
  principle from the building-effective-agents note.

- **Chapter 03 (Agent Skills and Architecture Patterns)**: This source provides
  the primary reference for a new architectural primitive — Agent Skills as a
  packaging mechanism for agent capabilities. Add Agent Skills as a concrete
  pattern alongside the five workflow patterns from the earlier Anthropic post.
  Add the SKILL.md format specification (YAML frontmatter, progressive disclosure,
  linked files) as a reference. Add code-as-tool pattern — when to embed
  deterministic scripts vs use LLM generation. Add the skills-MCP complementarity:
  skills package the *how* (workflow knowledge), MCP provides the *what* (tools).

- **Chapter 04 (On-Call Tooling)**: Add skill authorship best practices for SRE
  — start by evaluating where on-call agents struggle, build skills incrementally,
  iterate based on observed agent behavior. The security guidance (audit skills
  before install, watch for external network connections) is directly applicable
  to production agent deployments.

## Extraction Notes

- Source was read in full via WebFetch (markdown extraction from the rendered
  Anthropic Engineering blog page). The post is self-contained with diagrams and
  code descriptions. The post links to agentskills.io, the PDF skill GitHub
  repository, the Skills docs, and the Skills cookbook — none were followed per
  MINER.md §1's "up to 5 linked pages" guidance, as the blog post is
  architecturally complete without them.
- All quoted passages were copied character-for-character from the fetched web
  content. The Assayer should spot-check key quotes against the live URL.
- Published October 16, 2025 and updated December 18, 2025. Both dates are within
  the freshness window. The open standard update (Dec 2025) is significant — it
  changes the source from a product announcement to a portable standard.
- `confidence_overall` set to `emerging`: while the format specification itself
  is settled (shipped across multiple platforms), the blog post is primarily a
  product announcement and best-practice guide, not a peer-reviewed analysis or a
  post-hoc evaluation of production deployments. The claims about what makes skills
  effective are experienced practitioner opinion, not benchmarked results.
- No contradiction issue filed: this source introduces a new concept (Agent Skills)
  that is complementary to all existing notes. The Google/Antigravity "skills"
  model uses the same term for a different mechanism but that is a terminology
  overload, not a substantive contradiction — both are valid approaches for
  different contexts.
- Miner-related-notes candidates processed (see miner-related-notes.md at repo
  root; read and cited or dismissed below):
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — **Dismissed**. Covers
    retail/gaming SRE, unrelated to agent skill packaging.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — **Cited** (Extends). Google's
    practitioner account of building AI agents provides operational context that
    Anthropic's skill packaging serves.
  - `docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md` — **Cited**
    (Distinguish). Google's "skills" on Antigravity harness is a different concept
    with the same term.
  - `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — **Dismissed**. Google's
    centralized AI for SRE team, no skill packaging mechanism.
  - `blog-anthropic-building-effective-agents.md` — **Cited** (Corroborates,
    Extends). Same author, complementary topic — workflow taxonomy vs skill
    packaging.
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` —
    **Dismissed**. Client transparency in migrations, unrelated.
  - `blog-pagerduty-sre-agent-architecture.md` — **Dismissed**. PagerDuty's agent
    architecture, no skill packaging format.
  - `blog-pagerduty-production-ai-agent-gaps.md` — **Dismissed**. Production gaps
    for AI agents, no skill packaging.
  - `blog-promptfoo-model-upgrades-break-agent-safety.md` — **Dismissed**. Model
    upgrade safety, not directly applicable to skill packaging.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — **Dismissed**. SLOs,
    unrelated.
