// In-browser TalentFlow demo: same pages and rules as the FastAPI app, state kept in localStorage.
import { seedState } from './data.js';
import { Conflict, LABELS, STAGES, addCandidate, moveCandidate, stats } from './rules.js';

const KEY = 'talentflow-demo-v1';
const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || null; } catch { return null; } };
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* storage unavailable */ } };
let state = load() || seedState();

const root = document.getElementById('content');
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const initials = (name) => name.split(' ').slice(0, 2).map((w) => w[0]).join('').toUpperCase();
const jobOf = (id) => state.jobs.find((j) => j.id === id);
const scoreClass = (n) => `s${Math.floor(n / 20)}`;
const BOARD = ['new', 'screening', 'interview', 'technical', 'offer', 'hired', 'rejected'];

const views = {
  dashboard() {
    const s = stats(state);
    const base = s.funnel[0].count || 1;
    const top = state.candidates.filter((c) => !['rejected', 'hired'].includes(c.stage)).sort((a, b) => b.score - a.score || a.id - b.id).slice(0, 5);
    const open = state.jobs.filter((j) => j.status === 'open').slice(0, 4);
    return `<header class="top"><div><p class="eyebrow">Vue d'ensemble</p><h1>Bonjour, voici votre recrutement</h1></div><a class="btn" href="#/board">Ouvrir le pipeline</a></header>
    <section class="bento">
      <article class="card kpi"><span>Offres ouvertes</span><b>${s.openJobs}</b></article>
      <article class="card kpi"><span>Candidatures</span><b>${s.candidates}</b></article>
      <article class="card kpi accent"><span>Embauches</span><b>${s.hired}</b></article>
      <article class="card kpi"><span>Score moyen</span><b>${s.averageScore}<small>/100</small></b></article>
      <article class="card funnel"><h2>Entonnoir de recrutement</h2>
        ${s.funnel.map((f) => `<div class="bar-row"><span class="lbl">${f.label}</span><div class="track"><div class="fill" style="width:${Math.round((100 * f.count) / base)}%"></div></div><b>${f.count}</b></div>`).join('')}
        <p class="muted">Taux de conversion global : <strong>${s.conversionRate} %</strong></p></article>
      <article class="card list"><h2>Meilleurs profils en cours</h2>
        ${top.map((c) => `<div class="person"><span class="avatar">${initials(c.fullName)}</span><div><strong>${esc(c.fullName)}</strong><small>${esc(jobOf(c.jobId).title)}</small></div><span class="score ${scoreClass(c.score)}">${c.score}</span></div>`).join('')}</article>
      <article class="card jobs-mini"><h2>Offres à pourvoir</h2>
        ${open.map((j) => `<a class="job-line" href="#/board/${j.id}"><div><strong>${esc(j.title)}</strong><small>${esc(j.department)} · ${esc(j.location)} · ${esc(j.contract)}</small></div><span class="chip">${j.openings} poste${j.openings > 1 ? 's' : ''}</span></a>`).join('')}</article>
    </section>`;
  },

  board(jobId) {
    const selected = jobId || state.jobs.find((j) => j.status === 'open')?.id || state.jobs[0].id;
    const job = jobOf(selected);
    const cols = BOARD.map((stage) => {
      const cards = state.candidates.filter((c) => c.jobId === selected && c.stage === stage).sort((a, b) => b.score - a.score || a.id - b.id);
      return `<div class="col stage-${stage}" data-stage="${stage}"><h3>${LABELS[stage]} <span class="count">${cards.length}</span></h3><div class="drop">
        ${cards.map((c) => `<article class="cand" draggable="true" data-id="${c.id}"><div class="row"><span class="avatar">${initials(c.fullName)}</span><strong>${esc(c.fullName)}</strong><span class="score ${scoreClass(c.score)}">${c.score}</span></div>
          <p>${esc(c.headline)}</p><div class="tags">${c.skills.split(',').slice(0, 3).map((s) => `<span>${esc(s.trim())}</span>`).join('')}</div>
          <small>${c.years} an${c.years > 1 ? 's' : ''} · ${esc(c.source)}</small></article>`).join('')}</div></div>`;
    }).join('');
    return `<header class="top"><div><p class="eyebrow">Pipeline</p><h1>Suivi des candidats</h1></div>
      <select id="jobSelect" aria-label="Offre">${state.jobs.map((j) => `<option value="${j.id}" ${j.id === selected ? 'selected' : ''}>${esc(j.title)}${j.status === 'closed' ? ' (clôturée)' : ''}</option>`).join('')}</select></header>
      <p class="muted" id="msg" role="status">Glissez une carte d'une colonne à l'autre pour faire avancer un candidat.</p>
      <section class="board" id="board" data-job="${selected}">${cols}</section>
      <details class="card addbox"><summary>Ajouter un candidat à « ${esc(job.title)} »</summary>
        <form id="addForm" class="addform">
          <input id="fName" placeholder="Nom complet" required minlength="2"><input id="fEmail" type="email" placeholder="E-mail" required>
          <input id="fSkills" placeholder="Compétences (séparées par des virgules)"><input id="fYears" type="number" min="0" max="45" value="2" aria-label="Années d'expérience">
          <button class="btn" type="submit">Ajouter</button></form></details>`;
  },

  jobs() {
    return `<header class="top"><div><p class="eyebrow">Offres</p><h1>Postes ouverts et clôturés</h1></div></header>
    <section class="job-grid">${state.jobs.map((j) => {
      const list = state.candidates.filter((c) => c.jobId === j.id);
      const hired = list.filter((c) => c.stage === 'hired').length;
      return `<article class="card job"><div class="row between"><span class="chip ${j.status === 'closed' ? 'closed' : ''}">${j.status === 'closed' ? 'Clôturée' : 'Ouverte'}</span><small>${esc(j.contract)}</small></div>
        <h2>${esc(j.title)}</h2><p class="muted">${esc(j.department)} · ${esc(j.location)}</p>
        <div class="tags">${j.skills.split(',').map((s) => `<span>${esc(s.trim())}</span>`).join('')}</div>
        <div class="row between foot"><span><b>${list.length}</b> candidats</span><span><b>${hired}</b>/${j.openings} embauché${j.openings > 1 ? 's' : ''}</span></div>
        <a class="btn ghost" href="#/board/${j.id}">Voir le pipeline</a></article>`;
    }).join('')}</section>`;
  },
};

function bindBoard() {
  const board = document.getElementById('board');
  if (!board) return;
  const msg = document.getElementById('msg');
  const say = (text, bad = false) => { msg.textContent = text; msg.classList.toggle('bad', bad); };
  let dragged = null;
  board.addEventListener('dragstart', (e) => {
    const card = e.target.closest('.cand'); if (!card) return;
    dragged = card; card.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', card.dataset.id);
  });
  board.addEventListener('dragend', () => { dragged?.classList.remove('dragging'); board.querySelectorAll('.col').forEach((c) => c.classList.remove('over')); });
  board.addEventListener('dragover', (e) => {
    const col = e.target.closest('.col'); if (!col) return; e.preventDefault();
    board.querySelectorAll('.col').forEach((c) => c.classList.toggle('over', c === col));
  });
  board.addEventListener('drop', (e) => {
    const col = e.target.closest('.col'); if (!col || !dragged) return; e.preventDefault();
    try {
      moveCandidate(state, Number(dragged.dataset.id), col.dataset.stage);
      save(); render(); // re-render so counts, job status and order follow the rules
      document.getElementById('msg').textContent = 'Candidat déplacé.';
    } catch (err) {
      say(err instanceof Conflict ? err.message : 'Déplacement refusé', true);
    }
  });
  document.getElementById('jobSelect').addEventListener('change', (e) => { location.hash = `#/board/${e.target.value}`; });
  document.getElementById('addForm').addEventListener('submit', (e) => {
    e.preventDefault();
    try {
      addCandidate(state, {
        jobId: Number(board.dataset.job), fullName: document.getElementById('fName').value.trim(), email: document.getElementById('fEmail').value.trim(),
        skills: document.getElementById('fSkills').value, years: Number(document.getElementById('fYears').value) || 0, headline: 'Candidature spontanée',
      });
      save(); render();
    } catch (err) { say(err.message, true); }
  });
}

function render() {
  const [, page = '', arg] = location.hash.split('/');
  const route = ['board', 'jobs'].includes(page) ? page : 'dashboard';
  root.innerHTML = route === 'board' ? views.board(arg ? Number(arg) : null) : views[route]();
  document.querySelectorAll('.side nav a[data-page]').forEach((a) => a.classList.toggle('on', a.dataset.page === route));
  bindBoard();
  window.scrollTo(0, 0);
}

document.getElementById('reset').addEventListener('click', () => { state = seedState(); save(); render(); });
window.addEventListener('hashchange', render);
render();
