// Scripervisor Shot Board — front-end.
//
// Renders from a single STATE object whose shape mirrors the backend
// session.state (shots / revision_log / activity / capability_gaps). Seeded
// here with the demo scenario so the board is explorable without a backend.
//
// To go live, replace `seed()` with a poll of the ADK server, e.g.:
//   const s = await fetch('/run', {method:'POST', body: JSON.stringify({...})})
//   STATE.shots = (await s.json()).state.shots;  // then render();
// The A2A card lives at /a2a/app/.well-known/agent.json.

const REVISION_COLORS = ["White", "Blue", "Pink", "Yellow", "Green", "Goldenrod"];

const STATE = {
  shots: [
    {
      shot_id: "S1", scene: "Night — detective loses her badge in the alley",
      status: "flagged", last_touched_by: "script-continuity",
      variants: [], skill_badges: [],
      flags: ["Continuity conflict — badge already lost in Scene 4 (story-day 2). Cannot be lost again."],
    },
    {
      shot_id: "S2", scene: "Detective searches empty badge holder, close-up",
      status: "drafted", last_touched_by: "storyboard",
      variants: [{ v: 1, angle: "wide" }, { v: 2, angle: "OTS" }, { v: 3, angle: "low" }],
      skill_badges: [], flags: [],
    },
    {
      shot_id: "S3", scene: "Establishing — rain-slick city street, neon",
      status: "assembled", last_touched_by: "post-production",
      variants: [{ v: 1, angle: "wide", pick: true }],
      skill_badges: ["day-for-night grading applied", "PLATE-014 · cleared"], flags: [],
    },
  ],
  revision_log: [
    { rev: 1, label: "Rev. White", shot_id: "S1", what_changed: "Initial shot breakdown from request", why: "Filmmaker request: add a night badge-loss scene" },
  ],
  capability_gaps: [
    { agent: "script-continuity", gap: "No rule for tracking eyeline across reversed shots", suggested_skill: "eyeline-continuity" },
  ],
  activity: [
    { seq: 1, agent: "front-desk", message: "received request, handed off to Line Producer" },
    { seq: 2, agent: "line-producer", message: "broke request into 3 shots; continuity-check first" },
    { seq: 3, agent: "script-continuity", message: "metadata_lookup('badge') → lost in Scene 4" },
    { seq: 4, agent: "script-continuity", message: "FLAG on S1: badge already lost" },
  ],
  skills: [
    { icon: "🌙", name: "day-for-night", desc: "Grade daytime plates to night" },
    { icon: "🎭", name: "character-consistency", desc: "Reference-anchored faces across shots" },
    { icon: "📐", name: "eyeline-continuity", desc: "Track gaze direction across cuts" },
  ],
};

const $ = (id) => document.getElementById(id);

function statusBadge(s) { return `<span class="badge ${s}">${s}</span>`; }

function renderShots() {
  $("count").textContent = `${STATE.shots.length} shots`;
  $("grid").innerHTML = STATE.shots.map((shot) => {
    const variants = shot.variants.length
      ? `<div class="variants">${shot.variants.map((v) =>
          `<span class="${v.pick ? "pick" : ""}">v${v.v}</span>`).join("")}</div>`
      : "";
    const badges = shot.skill_badges.length
      ? `<div class="skill-badges">${shot.skill_badges.map((b) => `<span class="sb">${b}</span>`).join("")}</div>`
      : "";
    const flag = shot.flags.length
      ? `<div class="flag">⚠ ${shot.flags[0]}
           <div class="actions">
             <button class="approve" data-approve="${shot.shot_id}">Approve anyway</button>
             <button data-revise="${shot.shot_id}">Revise</button>
           </div>
         </div>`
      : "";
    return `<div class="card">
      <div class="frame">
        <span class="id">${shot.shot_id}</span>
        ${shot.variants.length ? "storyboard frame" : "— no frame yet —"}
        ${variants}
      </div>
      <div class="card-body">
        <div class="scene">${shot.scene}</div>
        <div class="meta">${statusBadge(shot.status)} · touched by <b>${shot.last_touched_by}</b></div>
        ${badges}
      </div>
      ${flag}
    </div>`;
  }).join("");

  document.querySelectorAll("[data-approve]").forEach((b) =>
    b.onclick = () => approve(b.dataset.approve));
  document.querySelectorAll("[data-revise]").forEach((b) =>
    b.onclick = () => revise(b.dataset.revise));
}

function renderSide() {
  $("skills").innerHTML = STATE.skills.map((s) =>
    `<div class="skill"><div class="ic">${s.icon}</div>
       <div><div class="name">${s.name}</div><div class="desc">${s.desc}</div></div></div>`).join("");

  $("revlog").innerHTML = STATE.revision_log.map((r) => {
    const color = r.label.replace("Rev. ", "");
    return `<div class="rev"><div class="lbl ${color}">${r.label} · ${r.shot_id}</div>
      <div class="why"><b>${r.what_changed}.</b> ${r.why}</div></div>`;
  }).join("");

  $("gaps").innerHTML = STATE.capability_gaps.map((g) =>
    `<div class="gap"><b>${g.gap}</b> → needs skill <code>${g.suggested_skill}</code></div>`).join("")
    || `<div class="gap">none reported</div>`;

  $("activity").innerHTML = STATE.activity.slice().reverse().map((a) =>
    `<li><span class="seq">${a.seq}</span><span><span class="who">${a.who || a.agent}</span> ${a.message}</span></li>`).join("");
}

function logActivity(agent, message) {
  STATE.activity.push({ seq: STATE.activity.length + 1, agent, message });
}

function logRevision(shot_id, what_changed, why) {
  const color = REVISION_COLORS[Math.min(STATE.revision_log.length, REVISION_COLORS.length - 1)];
  STATE.revision_log.push({ rev: STATE.revision_log.length + 1, label: `Rev. ${color}`, shot_id, what_changed, why });
}

function approve(shotId) {
  const why = prompt("Approve despite the continuity flag — why? (this becomes the revision rationale)");
  if (why === null) return; // cancelled — HITL gate not passed
  const shot = STATE.shots.find((s) => s.shot_id === shotId);
  shot.status = "approved"; shot.flags = [];
  logRevision(shotId, "Continuity flag overridden by director", why || "(no reason given)");
  logActivity("line-producer", `override ${shotId}: ${why || "(no reason)"}`);
  render();
}

function revise(shotId) {
  const shot = STATE.shots.find((s) => s.shot_id === shotId);
  shot.status = "drafted"; shot.flags = [];
  shot.scene = shot.scene.replace("loses her badge", "reports her badge stolen");
  logActivity("line-producer", `revised ${shotId} to resolve conflict`);
  render();
}

function sendRequest(text) {
  if (!text.trim()) return;
  logActivity("front-desk", `received: "${text.trim()}" — handed off to Line Producer`);
  logActivity("line-producer", "planning shot breakdown…");
  $("request").value = "";
  render();
}

function render() { renderShots(); renderSide(); }

// Wire up controls
$("send").onclick = () => sendRequest($("request").value);
document.querySelectorAll("[data-fill]").forEach((c) =>
  c.onclick = () => { $("request").value = c.dataset.fill; });

render();
