// Demo data, same content as app/seed.py. Scores are computed with the same formula.
import { computeScore } from './rules.js';

const JOBS = [
  ['Développeur full-stack senior', 'Ingénierie', 'Tunis', 'CDI', 'React, TypeScript, Node.js, PostgreSQL, Docker', 2],
  ['Ingénieur QA automatisation', 'Qualité', 'Tunis', 'CDI', 'Playwright, Selenium, Python, CI/CD, API testing', 1],
  ['Data analyst', 'Data', 'Sfax', 'CDI', 'SQL, Python, Power BI, Excel, Statistiques', 1],
  ['Product designer', 'Produit', 'Remote', 'CDD', 'Figma, Design system, Prototypage, Recherche utilisateur', 1],
  ['Chargé de recrutement IT', 'RH', 'Tunis', 'CDI', 'Sourcing, LinkedIn Recruiter, Entretien, ATS', 1],
];

// [job index, name, headline, skills, years, source, stage]
const CANDIDATES = [
  [0, 'Amine Bouzid', 'Full-stack engineer, 6 ans', 'React, TypeScript, Node.js, PostgreSQL, Docker', 6, 'LinkedIn', 'offer'],
  [0, 'Sarra Mansouri', 'Frontend lead', 'React, TypeScript, GraphQL, Docker', 7, 'Cooptation', 'technical'],
  [0, 'Hichem Jlassi', 'Développeur web', 'React, Node.js, MySQL', 3, 'Site carrière', 'interview'],
  [0, 'Nour El Houda Ben Ali', 'Ingénieure logiciel', 'TypeScript, Node.js, PostgreSQL', 4, 'LinkedIn', 'screening'],
  [0, 'Fares Kallel', 'Développeur backend', 'Node.js, PostgreSQL, Docker, Redis', 5, 'Welcome to the Jungle', 'technical'],
  [0, 'Rim Chaouch', 'Développeuse junior', 'React, JavaScript', 1, 'Site carrière', 'new'],
  [0, 'Oussama Triki', 'Tech lead', 'React, TypeScript, Node.js, PostgreSQL, Docker', 9, 'Chasse de tête', 'rejected'],
  [0, 'Eya Gharbi', 'Full-stack developer', 'React, TypeScript, PostgreSQL', 3, 'LinkedIn', 'new'],
  [1, 'Mariem Zouari', 'QA engineer', 'Playwright, Python, CI/CD, API testing', 4, 'LinkedIn', 'offer'],
  [1, 'Skander Abid', 'Testeur automatisation', 'Selenium, Python, API testing', 3, 'Cooptation', 'interview'],
  [1, 'Ines Louati', 'Analyste qualité', 'Selenium, Excel', 2, 'Site carrière', 'screening'],
  [1, 'Marwen Dhaouadi', 'SDET', 'Playwright, Selenium, Python, CI/CD, API testing', 6, 'Chasse de tête', 'technical'],
  [1, 'Yosra Haddad', 'QA manuel', 'Tests fonctionnels, Jira', 2, 'Indeed', 'rejected'],
  [1, 'Aymen Sassi', 'Ingénieur QA', 'Playwright, Python, API testing', 3, 'LinkedIn', 'new'],
  [2, 'Khaoula Bejaoui', 'Data analyst', 'SQL, Python, Power BI, Excel', 3, 'LinkedIn', 'hired'],
  [2, 'Wassim Rekik', 'BI developer', 'SQL, Power BI, Statistiques', 4, 'Cooptation', 'rejected'],
  [2, 'Amira Khelifi', 'Analyste de données', 'SQL, Excel, Python', 2, 'Site carrière', 'interview'],
  [2, 'Bilel Nasri', 'Data scientist junior', 'Python, Statistiques, SQL', 1, 'Indeed', 'screening'],
  [3, 'Lina Ayari', 'Product designer', 'Figma, Design system, Prototypage, Recherche utilisateur', 5, 'Dribbble', 'technical'],
  [3, 'Mehdi Ferchichi', 'UI designer', 'Figma, Prototypage', 3, 'LinkedIn', 'interview'],
  [3, 'Syrine Makni', 'UX researcher', 'Recherche utilisateur, Figma', 4, 'Cooptation', 'screening'],
  [3, 'Taha Meddeb', 'Graphiste', 'Illustrator, Figma', 2, 'Behance', 'new'],
  [4, 'Cyrine Ben Youssef', 'Talent acquisition', 'Sourcing, LinkedIn Recruiter, Entretien, ATS', 5, 'LinkedIn', 'interview'],
  [4, 'Anis Slimani', 'Chargé de recrutement', 'Sourcing, Entretien', 3, 'Site carrière', 'screening'],
  [4, 'Malek Ouerghi', 'Assistant RH', 'ATS, Entretien', 1, 'Indeed', 'new'],
];

export function seedState() {
  const jobs = JOBS.map(([title, department, location, contract, skills, openings], i) => ({
    id: i + 1, title, department, location, contract, skills, openings, status: 'open',
  }));
  jobs[2].status = 'closed'; // the data analyst opening is already filled
  const candidates = CANDIDATES.map(([jobIndex, fullName, headline, skills, years, source, stage], i) => ({
    id: i + 1, jobId: jobs[jobIndex].id, fullName, email: `${fullName.toLowerCase().replace(/ /g, '.')}@example.com`,
    headline, skills, years, source, stage, score: computeScore(jobs[jobIndex].skills, skills, years),
  }));
  return { jobs, candidates };
}
