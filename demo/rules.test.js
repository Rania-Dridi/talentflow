// Parity tests: the browser port must follow the same rules as the Python service (tests/test_pipeline.py).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { seedState } from './data.js';
import { Conflict, addCandidate, computeScore, moveCandidate, stats } from './rules.js';

const fresh = () => ({ jobs: [{ id: 1, title: 'QA', skills: 'python, playwright', openings: 1, status: 'open' }], candidates: [] });
const apply = (state, email = 'a@example.com') => addCandidate(state, { jobId: 1, fullName: 'Alice', email, skills: 'python', years: 2 });

test('score matches the Python formula', () => {
  assert.equal(computeScore('python, sql', 'Python, SQL, Docker', 15), 100);
  assert.equal(computeScore('python, sql', 'python', 3), 42);
  assert.equal(computeScore('', 'python', 0), 30);
  assert.equal(computeScore('python', 'python', -4), 60);
});

test('new candidate starts as new with a score', () => {
  const c = apply(fresh());
  assert.equal(c.stage, 'new');
  assert.equal(c.score, 38);
});

test('same e-mail cannot apply twice', () => {
  const s = fresh(); apply(s);
  assert.throws(() => apply(s), Conflict);
});

test('cannot hire without an offer; hiring the last opening closes the job', () => {
  const s = fresh(); const c = apply(s);
  assert.throws(() => moveCandidate(s, c.id, 'hired'), /after an offer/);
  moveCandidate(s, c.id, 'offer'); moveCandidate(s, c.id, 'hired');
  assert.equal(s.jobs[0].status, 'closed');
  assert.throws(() => apply(s, 'late@example.com'), /closed/);
});

test('hired is final and rejected can only be reconsidered as new', () => {
  const s = fresh(); s.jobs[0].openings = 2; const c = apply(s);
  moveCandidate(s, c.id, 'offer'); moveCandidate(s, c.id, 'hired');
  assert.throws(() => moveCandidate(s, c.id, 'interview'), Conflict);
  const d = apply(s, 'd@example.com');
  moveCandidate(s, d.id, 'rejected');
  assert.equal(moveCandidate(s, d.id, 'new').stage, 'new');
  moveCandidate(s, d.id, 'rejected');
  assert.throws(() => moveCandidate(s, d.id, 'interview'), Conflict);
});

test('demo data gives the same dashboard numbers as the Python seed', () => {
  const s = stats(seedState());
  assert.equal(s.candidates, 25);
  assert.equal(s.hired, 1);
  assert.equal(s.openJobs, 4);
  assert.equal(s.funnel[0].count, 22); // 25 candidates minus the 3 rejected ones
});
