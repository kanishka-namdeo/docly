# DOX framework

- DOX is highly performant AGENTS.md hierarchy installed here
- Agent must follow DOX instructions across any edits

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it

## Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root AGENTS.md is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index
- Child AGENTS.md files own domain-specific instructions and their own Child DOX Index
- Each parent explains what its direct children cover and what stays owned by the parent
- The closer a doc is to the work, the more specific and practical it must be

## Child Doc Shape

- Create a child AGENTS.md when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards
- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty
- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists

Default section order:
- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

## Style

- Keep docs concise, current, and operational
- Document stable contracts, not diary entries
- Put broad rules in parent docs and concrete details in child docs
- Prefer direct bullets with explicit names
- Do not duplicate rules across many files unless each scope needs a local version
- Delete stale notes instead of explaining history
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist

## Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and any affected parents or children
3. Refresh every affected Child DOX Index
4. Remove stale or contradictory text
5. Run existing verification when relevant
6. Report any docs intentionally left unchanged and why

## User Preferences

When the user requests a durable behavior change, record it here or in the relevant child AGENTS.md

### Running the App

When the user asks to "run the app", "start the app", or "restart the app", always run the full Tauri desktop application with all services. Use `scripts/run_dev.sh` (or create it if missing). This starts:
1. Python FastAPI backend (port 8000)
2. Frontend dev server (via Tauri's beforeDevCommand)
3. Tauri desktop window

Never start only the backend or only the frontend — always launch the complete Tauri app.

### Proactive Web Search

Use `web_search` proactively when:
- User asks for current/recent information (news, releases, today's events)
- Knowledge cutoff (April 2025) is likely insufficient — post-cutoff topics, fast-moving areas, time-sensitive data
- Verifying factual claims that could have changed (APIs, versions, URLs, best practices)
- User phrases questions with "what's the latest…" or "has X changed…"
- Corroborating claims with multiple sources for high-stakes accuracy (security, medical, legal)
- Self-detected uncertainty — if hedging, verify rather than guess
- Obscure/niche topics under-represented in training data
- Real-world consequence answers — corroborate with authoritative sources
- User is researching/fact-checking (papers, presentations, purchasing decisions)
- Known controversy or active debate — surface multiple perspectives
- "Is there a better way…" or "current best practice for…" questions
- User references something unrecognized (new library, recent paper, trending topic)
- Providing URLs/citations/references — links rot, docs move
- Market/financial data — stock prices, exchange rates, product pricing, economic indicators
- Regulatory/compliance updates — policy changes, legal requirements, industry regulations
- Competitive intelligence — competitor analysis, market positioning, product comparisons
- Geographically-specific information — local regulations, regional events, location-dependent services
- Complex research requiring synthesis — multi-source analysis, comprehensive reports, due diligence
- Real-time data — weather, sports scores, live events, breaking news
- Dynamic/JavaScript-heavy content — modern web apps, SPAs, content requiring browser rendering
- Business development tasks — prospect research, customer analysis, vendor evaluation

Avoid searching for: stable knowledge well within training data, questions answerable from first principles, trivial lookups.

**Guiding principle**: search when the cost of being wrong exceeds the cost of the search.

### Proactive Memory

Memory is a write–manage–read loop, not append-only storage. Follow these rules to keep recall useful and trustworthy.

#### Task Transition Detection

Detect when the user shifts between domains, projects, or tasks. On transition:
- Recall memories scoped to the new context
- Suppress memories from the previous context — do not let them leak into unrelated answers
- If a recalled memory is from a different domain than the current task, explicitly disregard it rather than silently using it

#### Consolidation of Repeated Episodes

When the same correction, preference, or pattern appears across multiple sessions (roughly 3+ times), consolidate it into a single semantic fact via `retain`. Do not wait for the user to ask. One strong consolidated lesson beats several overlapping episodic captures.

#### Memory Influence Transparency

When a recalled memory materially shapes the answer, surface which memory influenced it. Example: "I'm suggesting X because you noted last month that you prefer Y." This builds trust and lets the user correct stale memories before they cause harm.

#### Privacy and Sensitivity Gating

Before storing anything via `retain` or `learn`, check for sensitive content:
- PII (names, IDs, emails, phone numbers, addresses)
- Credentials, tokens, secrets
- Health, relationship, or financial details
- Personality inferences or behavioral profiles

If detected: skip storage unless the user explicitly asked to remember it. When in doubt, ask.

#### Time-Sensitive Expiry

Tag memories with natural half-lives. Before storing, consider:
- Version-specific facts ("API v2.3 has a breaking change") → expire when version is superseded
- Sprint-scoped facts ("using staging server this sprint") → expire at sprint boundary
- Experimental results → flag as subject to new data

When you encounter evidence that a stored memory is outdated, proactively invalidate or update it. Do not leave stale facts competing with current ones.

#### Contradiction Detection

When current evidence contradicts a stored memory:
1. Invalidate the old memory (use `memory_edit` with `op: invalidate`, pointing at the replacement if one exists)
2. Store the corrected fact
3. Do not leave both versions alive — stale recall is worse than no recall

#### Procedural vs. Factual Capture

Distinguish what you are capturing:
- **Fact** (who, what, when, why, preference, decision) → `retain`
- **Procedure** (repeatable sequence of steps, debugging recipe, setup workflow) → `manage_skill`

One strong, specific lesson beats three vague ones. Capture sparingly — if it will not be reused, it does not belong in memory.

#### Preemptive Recall at Known Pain Points

Before the user hits a known snag, surface the warning. If you recall that a particular API version has a breaking change, a config caused a crash last time, or a dependency has a known issue — raise it proactively when the user approaches the same territory. Do not wait to be asked.

#### Cross-Domain Isolation

When recalling, scope the query to the current task context. If the user is working on task A, do not surface memories from unrelated task B. Similarity-based recall can leak across domains — compensate by being deliberate about what the recall query targets and by discarding off-domain results.

#### Memory Hygiene and Forgetting

Periodically review stored memories. Forget (`memory_edit` with `op: forget`) memories that are:
- Demonstrably outdated and not superseded by a stored replacement
- Low-importance and never recalled across sessions
- Superseded by better information (prefer `invalidate` with a replacement pointer when one exists)
- Captured speculatively and never confirmed useful

Memory that is not pulling its weight is noise that degrades recall quality.

**Guiding principle**: remember the right things at the right time at the right level of abstraction — and forget the rest.


## Child DOX Index

- **backend/** — Python FastAPI backend (app code, tests, configuration)
- **frontend/** — React 18 + TypeScript SPA (pages, components, services)
- **src-tauri/** — Tauri 2.x desktop application (Rust backend, sidecar management)
- **docs/** — User documentation (guides, API reference, architecture, troubleshooting)
- **scripts/** — Build and packaging scripts (backend, frontend, complete application)