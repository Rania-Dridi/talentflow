// Browser port of the Python business rules (app/services/pipeline.py, scoring.py, analytics.py).
// Same rules, same messages, so the demo behaves like the real API.

export const STAGES = ['new', 'screening', 'interview', 'technical', 'offer', 'hired', 'rejected'];
export const PIPELINE = ['new', 'screening', 'interview', 'technical', 'offer', 'hired'];
export const LABELS = {
  new: 'Nouveaux', screening: 'Présélection', interview: 'Entretien RH', technical: 'Test technique',
  offer: 'Offre', hired: 'Embauchés', rejected: 'Refusés',
};

export class Conflict extends Error {}
export class NotFound extends Error {}

const SKILLS_WEIGHT = 60;
const POINTS_PER_YEAR = 4;
const CAP_YEARS = 10;

export const parseSkills = (raw) => new Set(raw.split(',').map((s) => s.trim().toLowerCase()).filter(Boolean));

export function computeScore(requiredSkills, candidateSkills, years) {
  const required = parseSkills(requiredSkills);
  const have = parseSkills(candidateSkills);
  let overlap = 0;
  for (const s of required) if (have.has(s)) overlap += 1;
  const skillsPart = required.size ? SKILLS_WEIGHT * (overlap / required.size) : SKILLS_WEIGHT / 2;
  const experiencePart = Math.min(Math.max(years, 0), CAP_YEARS) * POINTS_PER_YEAR;
  return Math.round(Math.min(100, skillsPart + experiencePart));
}

const TERMINAL = new Set(['hired', 'rejected']);

/** state = { jobs: [...], candidates: [...] }. Mutates and returns the candidate, or throws. */
export function moveCandidate(state, candidateId, target) {
  const candidate = state.candidates.find((c) => c.id === candidateId);
  if (!candidate) throw new NotFound(`Candidate ${candidateId} not found`);
  const current = candidate.stage;
  if (current === target) return candidate;
  if (TERMINAL.has(current) && !(current === 'rejected' && target === 'new')) {
    throw new Conflict(`A candidate who is ${LABELS[current].toLowerCase()} cannot be moved`);
  }
  if (target === 'hired') hire(state, candidate);
  candidate.stage = target;
  return candidate;
}

function hire(state, candidate) {
  if (candidate.stage !== 'offer') throw new Conflict('A candidate can only be hired after an offer');
  const job = state.jobs.find((j) => j.id === candidate.jobId);
  const hired = state.candidates.filter((c) => c.jobId === job.id && c.stage === 'hired').length;
  if (hired >= job.openings) throw new Conflict('All openings for this job are already filled');
  if (hired + 1 >= job.openings) job.status = 'closed';
}

export function addCandidate(state, data) {
  const job = state.jobs.find((j) => j.id === data.jobId);
  if (!job) throw new NotFound(`Job ${data.jobId} not found`);
  if (job.status === 'closed') throw new Conflict('This job is closed to new applications');
  const email = data.email.toLowerCase();
  if (state.candidates.some((c) => c.jobId === job.id && c.email === email)) throw new Conflict('This candidate already applied to this job');
  const candidate = {
    id: Math.max(0, ...state.candidates.map((c) => c.id)) + 1, jobId: job.id, fullName: data.fullName, email,
    headline: data.headline ?? '', skills: data.skills ?? '', years: data.years ?? 0, source: data.source ?? 'Site carrière',
    score: computeScore(job.skills, data.skills ?? '', data.years ?? 0), stage: 'new',
  };
  state.candidates.push(candidate);
  return candidate;
}

export function stats(state, jobId) {
  const list = state.candidates.filter((c) => !jobId || c.jobId === jobId);
  const counts = Object.fromEntries(STAGES.map((s) => [s, list.filter((c) => c.stage === s).length]));
  const total = list.length;
  const hired = counts.hired;
  const funnel = PIPELINE.map((stage, i) => ({
    stage, label: LABELS[stage], count: PIPELINE.slice(i).reduce((sum, s) => sum + counts[s], 0),
  }));
  const all = state.candidates;
  return {
    openJobs: state.jobs.filter((j) => j.status === 'open').length,
    candidates: total,
    hired,
    averageScore: all.length ? Math.round((10 * all.reduce((s, c) => s + c.score, 0)) / all.length) / 10 : 0,
    conversionRate: total ? Math.round((1000 * hired) / total) / 10 : 0,
    funnel,
  };
}
