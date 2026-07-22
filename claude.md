# Scripervisor — build primer for Claude Code

Read `agentic-cinema-plan.md` first **if you have it** — it's the full architecture, UX design, demo arc, and skill-loader design for this Google Cloud Agentic Cinema hackathon submission. That brief is kept **private (maintainer-only)** and is intentionally excluded from this public repo (see `.gitignore`); if it isn't present, work from this primer and `README.md` alone. Everything below is a standing instruction for working in this repo; don't re-derive decisions the plan doc already made.

## Before writing any code

Invoke these local skills from `~/.claude/skills` (verify exact names/slugs via the skill listing — they may differ slightly from these labels):

- **"agent skill"** — general multi-agent scaffolding conventions, used for the Front Desk / Line Producer / role-agent structure.
- **"google adk skill"** — anything ADK-specific: `Runner`, `McpToolset`, `SequentialAgent`/`ParallelAgent`/`LoopAgent`, planners (`BuiltInPlanner`/`PlanReActPlanner`), `require_confirmation`, `SessionService`/`VertexAIMemoryBankService`.

## Build order

1. Scaffold the launch crew from the plan: **Front Desk** (thin router, no planning authority), **Line Producer** (orchestrator — owns requirement understanding, shot breakdown, delegation), and **Script/Continuity** + **Storyboard** as its sub-agents. Skip Rights & Clearance for now — it's a stretch goal per the plan's scoping section.
2. Wire the Post-Production/Asset agent against `McpToolset` using a **mock/local MCP server** (asset-search/metadata-lookup style stub) — the real partner endpoint isn't announced until the week of July 27. Design the connection so swapping in the real one later is a config change, not a re-architecture.
3. Build the Shot Board UI (three-panel layout: Front Desk request panel / Shot Board grid / Skills & Activity panel) — Design is judged equally with Technological Implementation, so this isn't a backend-only project.
4. Storyboard agent should generate 2-3 rough variant frames per shot (pick-then-polish), not one locked image per shot — see the plan's "grounding in real production" section for why.
5. Add the linear revision log (with rationale per entry) once the core loop works — small extension of the Activity Log, not a new subsystem.

## Things to confirm with the user, not guess

- Exact skill slugs for "agent skill" / "google adk skill" in this Claude Code environment.
- The real partner + MCP server domain once announced (week of July 27).
- Whether to expose the crew via A2A (mentioned as a stretch item in the plan, tied to the Insta360 case study).

## Repo setup (do this first, before any other work)

The hackathon requires a **public** repo with a **complete open-source license file**. Set it up with the default branch (**`master`**) protected so all changes land via PR, not direct push:

> **Status — done.** The repo already exists: [`github.com/jwlai-cloud/scripervisor`](https://github.com/jwlai-cloud/scripervisor) (public, Apache-2.0). Default branch is kept as **`master`** (not `main`), protected with **0 required approvals** (bot reviewers only — Sourcery/CodeRabbit), `enforce_admins` on, no force-push/delete, and conversation-resolution required before merge. The recipe below is the original plan — where it says `main`, read `master`; where it says `required_approving_review_count=1`, read `0`.

```bash
# create the repo (public, Apache-2.0 license, matches Scion's license so borrowed patterns are compatible)
gh repo create scripervisor --public --license apache-2.0 \
  --description "Scripervisor — an open, extensible multi-agent film production crew on Google ADK" \
  --clone
cd scripervisor

# protect main: require PRs, at least 1 approval, no direct pushes, no force-push/delete
gh api -X PUT "repos/:owner/scripervisor/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  -f required_status_checks=null \
  -F enforce_admins=true \
  -F required_pull_request_reviews.required_approving_review_count=1 \
  -F restrictions=null \
  -F allow_force_pushes=false \
  -F allow_deletions=false
```

Notes:
- `gh api` needs a real status-check config or `null` if you have no CI wired up yet — add `required_status_checks` once tests/lint exist.
- `enforce_admins=true` means even the repo owner can't bypass the PR requirement — worth turning off temporarily (`false`) if solo-hacking under time pressure makes PR-per-commit impractical, then back on before submission.
- All work after this point (including the first commit of the scaffolded agents) should go through a branch + PR, not a direct push to `main` — this itself is a small, honest demonstration of the "governance" language the hackathon prompt uses ("Studio Head enforcing... governance").

## Constraints from the plan, don't relitigate these

- No git-style branching/merging for the revision log — linear log only.
- No 3D scene generation (Three.js/Unity) — 2D storyboard frames only.
- Storyboard agent generates still images by default; a full video clip (Veo) is an optional "hero shot," not the backbone.
- Don't build a separate community/feedback platform — capability gaps get logged as structured reports by the agents themselves, not collected via a forum.
