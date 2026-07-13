---
source_url: https://sre.google/prodcast/
source_type: docs
title: "SRE Prodcast — Google's Podcast Index (Six Seasons of SRE)"
author: "Google SRE (Prodcast team: MP English, Jordan Greenberg, Steve McGhee, Florian Rathgeber, Matthew Siegler)"
date_published: 2022-03-31
date_extracted: 2026-07-13
last_checked: 2026-07-13
status: current
confidence_overall: settled
issue: "#32"
---

# SRE Prodcast — Google's Podcast Index (Six Seasons of SRE)

> An authoritative, Google-published index of the SRE Prodcast — a six-season
> oral-history companion to the SRE Book. Season 1 is a structured,
> chapter-by-chapter walkthrough of the SRE Book with Google domain experts
> (each episode mapped to specific SRE Book chapters as further reading), while
> later seasons are topical conversations. The index is valuable to the guide as
> the canonical episode-to-chapter map for SRE fundamentals (Ch02), incident
> management (Ch04), and automation/toil (Ch05), and as a locator for the growing
> set of AI/LLM-in-SRE episodes that later seasons dedicate to the topic.

## Source Context

- **Type**: docs (official Google SRE podcast index page; a curated landing page,
  not itself a deep technical document). The page indexes ~60 episodes across six
  seasons and links to full HTML and PDF transcripts for each.
- **Author credibility**: Google SRE — the originators of the SRE discipline.
  The Prodcast is produced and hosted by practicing Google SREs (MP English,
  Jordan Greenberg, Steve McGhee, Florian Rathgeber, Matthew Siegler, plus
  production by Salim Virji and Paul Guglielmino). Guests are named Google SREs
  and external practitioners (e.g., John Allspaw, Liz Fong-Jones, Niall Murphy,
  Ben Treynor Sloss, Todd Underwood). This is the highest-credibility source
  possible for SRE fundamentals and practitioner practice.
- **Scope**: The landing page provides (a) the six-season theme structure, (b)
  per-episode titles, guests, and one-paragraph descriptions, (c) per-episode
  "Further reading" lists that reference specific SRE Book chapters and external
  practitioner resources, and (d) links to HTML and PDF transcripts for every
  episode. The page itself contains no code, configs, metrics, or deep technical
  argument — the substance lives in the linked transcripts (being mined
  separately under issues #33–45). Does NOT cover: any single topic in depth;
  AI/LLM operations are present only as episode topics (concentrated in Seasons
  4–6), not as developed methodology. This note extracts the page-level structure
  and the episode-to-chapter map; it does not substitute for transcript mining.

## Extracted Claims

### Claim 1: The Prodcast is Google's official podcast about Site Reliability Engineering and production software, produced for both internal Google and external SRE audiences
- **Evidence**: Page header and foreword. The foreword explains an explicit pivot
  "We wanted to make a podcast for more than just engineers at Google. We wanted
  to make something that would be of interest to folks across organizations and
  technical implementations." The page is published on the official sre.google
  domain.
- **Confidence**: settled
- **Quote**: "Prodcast is Google's podcast about Site Reliability Engineering and
  production software."
- **Our assessment**: This establishes the source as a primary, authoritative
  Google SRE artifact — the oral-history companion to the SRE Book. For the
  guide, it is the canonical locator for practitioner SRE interviews and the
  episode-to-chapter map. High credibility; no reason to discount.

### Claim 2: The series is organized into six themed seasons — SRE Fundamentals, Life of an SRE, Champions of the Internet, Friends and Trends, More Friends More Trends, and Prodcast Live!
- **Evidence**: The page lists six season headers with explicit theme statements:
  "`Season 1: SRE Fundamentals`", "`Season 2: Life of an SRE`", "`Season 3:
  Champions of the Internet`", "`Season 4: Friends and Trends`", "`Season 5: More
  Friends, More Trends`", "`Season 6: Prodcast Live!`". Season 1 discusses SRE
  Book concepts with experts; Season 2 examines the SRE career path; Season 3
  discusses systems built by SREs; Season 4–5 discuss upcoming trends (including
  AI); Season 6 is recorded live at conferences (SREcon).
- **Confidence**: settled
- **Quote**: "Season 1 Discusses concepts from the SRE Book with experts at
  Google."; "Season 4 is about SRE \" Friends and Trends \", We discuss what's
  coming up in the SRE space, from new technology to modernizing processes and
  more"
- **Our assessment**: The season structure is itself a useful taxonomy for the
  guide. Season 1 (fundamentals) maps to Ch02/Ch04/Ch05; Season 3 (systems built
  by SRE) and Season 4–5 (trends, AI) provide practitioner context. The guide can
  use this taxonomy to point readers to primary practitioner accounts per topic.

### Claim 3: Season 1 is explicitly a chapter-by-chapter walkthrough of the SRE Book, with each of its ten episodes paired to specific SRE Book chapters as further reading
- **Evidence**: Season 1's own description: "Season 1 Discusses concepts from the
  SRE Book with experts at Google." Every Season 1 episode lists explicit "SRE
  Book Chapter N - [title]" entries in its Further reading (verified: Ch3/5/9,
  Ch6, Ch10, Ch4, Ch17/27, Ch7/8, Ch11, Ch13/14/16, Ch15). This systematic
  mapping exists only in Season 1; later seasons reference SRE Book chapters only
  occasionally (e.g., S2E2 links "Introducing Non-Abstract Large System Design";
  S3E14 links Ch11; S4E4 links Ch12 and Ch23).
- **Confidence**: settled
- **Quote**: "Season 1 Discusses concepts from the SRE Book with experts at
  Google."
- **Our assessment**: This is the single most valuable structural fact on the
  page for the guide: Season 1 is the canonical, episode-by-episode SRE Book
  reading companion. The guide's Ch02/Ch04/Ch05 can reference the matching
  episode as a primary-source practitioner discussion of each foundational
  chapter (e.g., S1E1 ↔ Ch3/5/9 on risk/simplicity/toil; S1E7 ↔ Ch11 on-call;
  S1E8 ↔ Ch13/14 incident management; S1E9 ↔ Ch15 postmortems). Later seasons are
  topical, not systematically chapter-mapped, so Season 1 is the entry point.

### Claim 4: The Season 1 episode-to-chapter map spans the full SRE fundamentals lifecycle — risk/simplicity/toil, monitoring, alerting, SLOs, automation/release, on-call, incident management, postmortems, and testing/launches
- **Evidence**: Verified Season 1 chapter references: S1E1 → Ch3 Embracing Risk,
  Ch9 Simplicity, Ch5 Toil; S1E2 → Ch6 Monitoring Distributed Systems; S1E3 → Ch10
  Practical Alerting; S1E4 → Ch4 Service Level Objectives; S1E5 → Ch17 Testing for
  Reliability, Ch27 Reliable Product Launches at Scale; S1E6 → Ch7 Evolution of
  Automation at Google, Ch8 Release Engineering; S1E7 → Ch11 Being On-Call;
  S1E8 → Ch13 Emergency Response, Ch14 Managing Incidents, Ch16 Tracking Outages;
  S1E9 → Ch15 Postmortem Culture.
- **Confidence**: settled
- **Quote**: "SRE Book Chapter 3 - Embracing Risk"; "SRE Book Chapter 5 - Toil";
  "SRE Book Chapter 15 - Postmortem Culture: Learning from Failure"
- **Our assessment**: This confirms the Prodcast covers the exact domains the
  guide targets (Ch02 fundamentals, Ch04 incident management/on-call/postmortems,
  Ch05 automation/toil). The episode map gives the guide a vetted primary-source
  pointer for each foundational topic, which strengthens the guide's citations
  beyond the SRE Book alone.

### Claim 5: Every episode provides both an HTML transcript and a PDF transcript, plus a curated "Further reading" list — making the corpus fully machine-minable
- **Evidence**: Each of the ~60 episodes on the page shows the link trio "View
  transcript / View HTML transcript / View PDF transcript" followed by "Further
  reading". The HTML transcript URLs follow the pattern
  `https://sre.google/prodcast/transcripts/sre-prodcast-{SS}-{EE}` (verified: 60
  distinct transcript hrefs present in the page, e.g.,
  `/prodcast/transcripts/sre-prodcast-01-02`,
  `/prodcast/transcripts/sre-prodcast-04-09`).
- **Confidence**: settled
- **Quote**: (no single sentence; the recurring link labels "View HTML transcript"
  / "View PDF transcript" / "Further reading" appear under every episode)
- **Our assessment**: The transcript availability is what makes this index
  actionable as a mining source. The individual transcripts are being triaged and
  mined separately (issues #33–45); this note deliberately extracts only the
  page-level structure. The guide should treat transcripts as the deep evidence
  and this index as the table of contents.

### Claim 6: The Prodcast's editorial intent was to challenge, not merely recap, the SRE Book orthodoxy — explicitly reframing topics such as SLOs
- **Evidence**: The foreword by MP English states the team "turned to one of the
  most studied resources in SRE: the Google SRE Book" but "didn't want to rehash
  what the book already discussed in detail." Season 1 Episode 4 ("Rethinking
  SLOs with Narayan Desai") is singled out: "Narayan Desai explains why SLOs can
  be problematic and proposes alternative methods for monitoring complex,
  large-scale systems." This is consistent with the foreword's claim that the
  SLOs episode "entirely refram[es] the topic."
- **Confidence**: settled
- **Quote**: "a series of conversations with domain experts at Google that often
  challenged the orthodoxy of the SRE Book, sometimes entirely reframing the
  topic, as is particularly the case with our episode on SLOs"
- **Our assessment**: This is a high-value meta-claim: the Prodcast is not a
  recitation of the SRE Book but a practitioner critique of it. For the guide,
  this means the transcripts can carry *deviations* from canonical SRE advice
  (e.g., "SLOs can be problematic") that the Smith should weigh against the
  book's prescriptions. The SLOs reframing in particular is relevant to the
  guide's error-budget / SLO material and to the PagerDuty "March of 9s"
  discussion in blog-pagerduty-production-ai-agent-gaps.

### Claim 7: AI/LLM coverage grows sharply in later seasons (Seasons 4–6), signaling the SRE discipline's pivot toward AI-assisted operations as a core concern
- **Evidence**: Season 1 has zero AI content. Season 3 Episode 3 (Ben Treynor
  Sloss) first raises "how AI and ML significantly impacts SRE practices."
  Season 4 dedicates multiple episodes to AI (S4E3 "The One With AI and Todd
  Underwood"; S4E4 "The One With the Future of SRE and Matt Zelesko"; S4E9 "The
  One with AI Agents, Ramón Llamas, and Swapnil Haria"; S4E8 TPMs in the AI
  landscape). Season 5 is heavily AI-focused (S5E1 observability+AI; S5E3
  Agentic AI hackers; S5E4 AI transforming production workflows; S5E6 AI safety;
  S5E8 SRE for AI research labs). Season 6 continues (S6E4, S6E8 on AI in SRE).
- **Confidence**: emerging
- **Quote**: "In this episode, Todd Underwood , a reliability expert from
  Anthropic with experience at Google and OpenAI, discusses the current state and
  future of AI in SRE."
- **Our assessment**: This trend is an observable structural fact of the corpus,
  not a single authoritative claim, so confidence is emerging. But it is
  significant for the guide: it confirms that Google's own SRE practitioners now
  treat AI-assisted operations as a first-class, recurring topic — exactly the
  domain the guide covers. The later-season AI episodes are the practitioner
  primary sources the guide's AI chapters (Ch02/Ch04/Ch05) should draw from, and
  they are being mined via the transcript issues.

### Claim 8: Multiple Prodcast episodes describe concrete AI-assisted-SRE practice that maps directly onto the guide's AI topics — including AI agents for alert summarization, "golden data sets" for validation, and keeping humans in the loop
- **Evidence**: S4E9 describes AI agents "revolutionizing production management,
  from summarizing alerts and finding hidden errors to proactively preventing
  outages" and notes "the challenges of evaluating non-deterministic systems."
  S5E4 (Denia del Cid) describes "early outage detection, incident similarity
  analysis, and toil reduction" with "the critical importance of validating
  against 'golden data sets' and keeping humans in the loop to build trust."
  S5E1 (Stephanie Hippo) describes "how AI and observability build a
  self-reinforcing loop" and "AI can detect and respond to certain classes of
  incidents, leading to self-healing systems."
- **Confidence**: emerging
- **Quote**: "explore how AI agents are revolutionizing production management,
  from summarizing alerts and finding hidden errors to proactively preventing
  outages"; "Denia details practical applications like early outage detection,
  incident similarity analysis, and toil reduction. She explains the critical
  importance of validating against \"golden data sets\" and keeping humans in the
  loop to build trust."
- **Our assessment**: These episode descriptions independently corroborate themes
  already present in the guide's existing AI source notes: the "golden data sets"
  validation practice (S5E4) mirrors the evaluation/harness emphasis in the
  PagerDuty and incident.io notes; "evaluating non-deterministic systems" (S4E9)
  is the same evaluation problem the AI-agent literature flags; "self-healing
  systems" (S5E1) echoes the autonomy theme. The Prodcast adds Google-practitioner
  first-person accounts behind those themes. Deep evidence must come from the
  transcripts (issues #33–45), but the index confirms these are real,
  named practitioner discussions worth mining.

### Claim 9: Ben Treynor Sloss — the creator of SRE — appears in Season 3 Episode 3 ("Production Problems Are For All!"), where he discusses how AI/ML impacts SRE practices and the future of SRE
- **Evidence**: S3E3 guest description: "Ben Treynor Sloss (VP of Engineering,
  Google) ... share[s] the evolution of SRE and its impact on software
  development, how AI and ML significantly impacts SRE practices, and the future
  of SRE." The episode notes he "coined the term 'Site Reliability Engineering'
  for his team of (now) 4,000 software engineers."
- **Confidence**: emerging
- **Quote**: "how AI and ML significantly impacts SRE practices, and the future of
  SRE."
- **Our assessment**: This extends the existing `discussion-google-sre-ben-treynor-interview.md`
  source note, which is explicitly pre-LLM (its Claim 8 states the source
  "predates the LLM era and contains no AI/LLM content whatsoever"). The Prodcast
  S3E3 captures Treynor's *updated* view that AI/ML now significantly impacts SRE
  — a useful bridge between the foundational Treynor interview and the guide's
  AI-era material. The transcript (a separate mining issue) is the place to
  extract his specific claims; this index only confirms the episode exists and its
  topic.

### Claim 10: The Prodcast is produced and hosted by practicing Google SREs, and its guest list spans Google SRE leadership and prominent external SRE/incident practitioners
- **Evidence**: "Meet Your Hosts" lists Jordan Greenberg (Engineering Program
  Manager, GCP; Seasons 3+), Steve McGhee (Reliability Advocate, SRE; Seasons
  2+), Florian Rathgeber (SRE, GCP; Seasons 3+), Matthew Siegler (ML
  Infrastructure SRE; Seasons 4+), MP English (Systems Engineer; Seasons 1&2).
  Production by Salim Virji (SRE Education Program Manager) and Paul Guglielmino.
  Guests include Ben Treynor Sloss, Niall Murphy, Liz Fong-Jones, John Allspaw,
  Courtney Nash, Todd Underwood (Anthropic), and Matt Zelesko (VP of SRE,
  Google).
- **Confidence**: settled
- **Quote**: "Steve McGhee — Reliability Advocate, SRE — Seasons 2+"
- **Our assessment**: The practitioner-and-leadership guest roster is what makes
  the source credible as primary-source SRE oral history. For the guide, this
  means citations drawn from Prodcast transcripts can be attributed to named,
  senior practitioners (e.g., a claim about SLOs from Narayan Desai, or about
  incident response from Sarah Butt/Vrai Stacey in S3E6) rather than anonymous
  blog content. This strengthens the guide's citation quality.

## Concrete Artifacts

### The Six-Season Structure (verbatim theme statements)

```
Season 1: SRE Fundamentals
  "Season 1 Discusses concepts from the SRE Book with experts at Google."
Season 2: Life of an SRE
  "Season 2 ' Life of An SRE ', examines the career path and growth of
   individuals in SRE."
Season 3: Champions of the Internet
  "Season 3 ' Champions of the Internet ', discusses software systems
   designed and built by SRE."
Season 4: Friends and Trends
  "Season 4 is about SRE ' Friends and Trends ', We discuss what's coming
   up in the SRE space, from new technology to modernizing processes and
   more"
Season 5: More Friends, More Trends
Season 6: Prodcast Live!
  (recorded live at SREcon; e.g., John Allspaw two-part conversation,
   Courtney Nash on complex systems, Matt Zelesko on the future of SRE)
```

### Canonical Season 1 Episode → SRE Book Chapter Map

This is the structured entry point the guide should cite for foundational topics.

| Episode | Title | Guest | SRE Book chapters (Further reading) |
|---|---|---|---|
| S1E0 | Creating the SRE Prodcast | John Reese (JTR) | Prodcast Season 1 Forward |
| S1E1 | SRE Philosophy | Jennifer Mace (Macey) | Ch3 Embracing Risk, Ch9 Simplicity, Ch5 Toil, Generic Mitigations, Multi-Single Tenancy |
| S1E2 | Customer-Centric Monitoring | Silvia Esparrachiari | Ch6 Monitoring Distributed Systems |
| S1E3 | Alerting | Amelia Harrison | Ch10 Practical Alerting |
| S1E4 | Rethinking SLOs | Narayan Desai | Ch4 Service Level Objectives |
| S1E5 | Client-Transparent Migrations | Pavan Adharapurapu | Ch17 Testing for Reliability, Ch27 Reliable Product Launches at Scale |
| S1E6 | Automation | Pierre Palatin | Ch7 Evolution of Automation at Google, Ch8 Release Engineering |
| S1E7 | On-Call Rotations | Andrew Widdowson (APW) | Ch11 Being On-Call |
| S1E8 | Incident Management | Adrienne Walcer | Ch13 Emergency Response, Ch14 Managing Incidents, Ch16 Tracking Outages |
| S1E9 | Postmortems | Ayelet Sachto | Ch15 Postmortem Culture: Learning from Failure |

### Transcript URL Pattern (for deeper mining)

```
Base:     https://sre.google/prodcast/
Listing:  https://sre.google/prodcast/
HTML tx:  https://sre.google/prodcast/transcripts/sre-prodcast-{SS}-{EE}
PDF tx:   same path, PDF variant (e.g., /prodcast/transcripts/sre-prodcast-04-09)
Verified: 60 distinct transcript hrefs present in the index page
Examples: sre-prodcast-01-02, sre-prodcast-03-03 (Treynor), sre-prodcast-04-09 (AI Agents)
```

### AI/LLM-Relevant Episodes (pointers for the guide's AI chapters; transcripts mined via #33–45)

```
S3E3  Production Problems Are For All!        Ben Treynor Sloss   — AI/ML impact on SRE, future of SRE
S4E3  The One With AI and Todd Underwood      Todd Underwood (Anthropic) — AIOps limits, config authoring, troubleshooting
S4E4  The One With the Future of SRE          Matt Zelesko (VP SRE, Google) — AI as assistant for detection/mitigation/postmortems
S4E9  The One with AI Agents                  Ramón Llamas, Swapnil Haria — AI agents for alert summarization, non-deterministic eval
S4E10 The One with Ben Good / Kubernetes      Ben Good            — platform engineering, golden paths, DORA metrics
S5E1  The One With Stephanie Hippo            Steph Hippo (Honeycomb) — observability + AI self-healing loop
S5E3  The One With Heather Adkins             Heather Adkins      — Agentic AI hackers, polymorphic malware, Secure-by-Design
S5E4  The One with Denia del Cid              Denia del Cid       — golden data sets, humans in the loop, toil reduction
S5E6  The One with Parker Barnes / AI         Parker Barnes, F. Tiengo Ferreira — AI safety, drift detection, context observability
S5E8  The One With Damion Yates / AI systems  Damion Yates (DeepMind) — SRE for AI research labs, "luck is our enemy"
S6E4  Matt Zelesko and the Future of SRE      Matt Zelesko        — how AI is (and isn't) changing SRE
S6E8  Courtney Nash on Complex Systems        Courtney Nash       — human expertise as AI evolves
```

### Notable Non-AI Practitioner Episodes (foundational SRE oral history)

```
S1E9  Postmortems (Ayelet Sachto)        — blameless, actionable postmortem culture
S1E8  Incident Management (Adrienne Walcer)
S1E7  On-Call Rotations (Andrew Widdowson)
S1E6  Automation (Pierre Palatin)        — building confidence in automation, UI design
S3E6  Incident Response (Sarah Butt, Vrai Stacey) — tooling & software for incidents
S3E10 Maglev load balancer (Cody Smith, Trisha Weir)
S3E12 Human Factors (Casey Rosenthal, John Allspaw) — resilience, human adaptation
S4E7  STPA (Theo Klein, Jeffrey Snover)  — System Theoretic Process Analysis
```

## Cross-References

- **Corroborates**: None on specific technical claims — this index page states no
  technical claims of its own (the substance is in transcripts). It *locates*
  primary-source practitioner discussions that the existing notes address
  theoretically. The AI-relevant episode descriptions (Claim 8) corroborate the
  *existence and importance* of the themes in the AI source notes
  (blog-pagerduty-*, blog-incidentio-*, blog-honeycomb-*) without restating their
  mechanics.

- **Contradicts**: None identified. No claim on this index page opposes any claim
  in an existing source note. The foreword's note that the Prodcast "often
  challenged the orthodoxy of the SRE Book" (Claim 6) is a meta-observation about
  the *Book*, not a claim that contradicts our corpus; the actual challenges (e.g.,
  "SLOs can be problematic," S1E4) would need to be extracted from the S1E4
  transcript to assess against the guide's SLO material, and that is out of scope
  for this index note. No contradiction issue is filed.

- **Extends**:
  - **discussion-google-sre-ben-treynor-interview.md** — That note is explicitly
    pre-LLM (Claim 8: "predates the LLM era and contains no AI/LLM content
    whatsoever"). Prodcast S3E3 (Claim 9) captures Treynor's *later* statement
    that "AI and ML significantly impacts SRE practices, and the future of SRE,"
    extending the foundational interview into the AI era. The transcript (separate
    mining issue) is where Treynor's specific AI claims should be extracted.
  - **docs-google-sre-nalsd-classroom.md** — The Prodcast further-reading lists
    point to the same NALSD material the classroom note covers: S2E2 links
    "Introducing Non-Abstract Large System Design," and S4E4 links "Chapter 12
    from the SRE book: Non-Abstract Large System Design." The Prodcast thus
    corroborates NALSD as a key SRE design resource and provides a practitioner
    pointer to it.

- **Novel**: The page-level structure is new to the corpus:
  - The six-season Prodcast taxonomy and the explicit editorial intent to
    *challenge* the SRE Book (not recap it).
  - The Season 1 episode→SRE-Book-chapter canonical map (the only systematically
    chapter-mapped season).
  - The catalog of AI/LLM-in-SRE episodes across Seasons 3–6, which serves as a
    locator for primary-source practitioner accounts the guide's AI chapters can
    cite.
  - The transcript URL pattern enabling systematic deeper mining (issues #33–45).

## Guide Impact

- **Chapter 02 (SRE Fundamentals / Automation / Toil)**: Use the Season 1
  episode→chapter map (Concrete Artifact table) to cite a primary-source
  practitioner discussion alongside each foundational SRE Book chapter — e.g.,
  point readers to S1E1 for risk/simplicity/toil (Ch3/5/9), S1E6 for automation
  (Ch7/8), S1E9 for postmortems (Ch15). This gives Ch02 vetted, named-practitioner
  companions to the book's prescriptions and strengthens citation quality beyond
  the book alone. Also surface the foreword's meta-claim (Claim 6) that the
  Prodcast *challenges* SRE Book orthodoxy, so Ch02 presents SRE fundamentals as a
  living debate rather than settled dogma.

- **Chapter 04 (Incident Management / On-call / Postmortems / Alerting)**:
  Reference S1E7 (on-call, Ch11), S1E8 (incident management, Ch13/14/16), S1E9
  (postmortems, Ch15), and S1E3 (alerting, Ch10) as primary-source practitioner
  discussions. The incident-response practitioner episodes (S3E6 Sarah Butt/Vrai
  Stacey on incident tooling; S6E9 Adam Kramer on IRT psychological safety) are
  candidate deeper-mining sources for the incident-response section. Note also
  S4E9's "AI agents for summarizing alerts and finding hidden errors" as a
  practitioner account of the AI-assisted incident theme already covered
  theoretically in blog-incidentio-ai-sre-incident-run.

- **Chapter 05 (Automation & Toil)**: Reference S1E6 (Automation with Pierre
  Palatin, Ch7/8) for the canonical automation discussion, and S5E4 (Denia del
  Cid: "early outage detection, incident similarity analysis, and toil reduction"
  via AI, validated against "golden data sets" with humans in the loop) as a
  primary-source practitioner account of AI-assisted toil reduction. This
  directly extends the toil-reduction framing in the existing AI source notes.

- **Cross-cutting (AI in SRE)**: The AI/LLM episode catalog (Concrete Artifact)
  should seed the guide's AI-chapter citation list with Google-practitioner
  primary sources — especially Todd Underwood on AIOps limitations (S4E3),
  Ramón Llamas/Swapnil Haria on AI agents (S4E9), Denia del Cid on golden data
  sets (S5E4), and Damion Yates on SRE for AI research labs (S5E8). These
  transcripts are being mined separately (#33–45); this index note is the
  table of contents that should route the Smith to them.

## Extraction Notes

- The source is a single landing page on the official sre.google domain. It was
  fetched via `curl` (533 KB HTML) and stripped of scripts/styles; the full
  episode list and further-reading entries were extracted and read in full. No
  sub-pages were followed beyond confirming the transcript URL pattern, per
  MINER.md §1 — the transcripts themselves are out of scope here (filed
  separately as issues #33–45).

- The page carries `data-release-date="2022-03-31"`, which is used as
  `date_published`. The Prodcast spans multiple years and seasons; individual
  episode air dates are not published on this index page, so the date is an
  approximate series-launch date, not a per-episode date.

- All quotes marked direct were copied character-for-character from the extracted
  page text. Spot-check against the live URL https://sre.google/prodcast/. The
  recurring link labels "View HTML transcript" / "View PDF transcript" /
  "Further reading" appear verbatim under every episode (no single sentence
  quote was possible for Claim 5, so it is marked accordingly).

- No part of the source was paywalled. The index and all transcript links are
  publicly accessible on sre.google.

- This note is deliberately an *index/map* extraction, not a transcript
  extraction. It establishes the episode→chapter structure and the AI-episode
  catalog so the Smith can route to the deeper, transcript-level mining (issues
  #33–45) for specific claims. Confidence is `settled` for the structural facts
  (the page is authoritative and stable) and `emerging` for the trend/AI claims
  (which are observations about the corpus, to be confirmed by transcript mining).
