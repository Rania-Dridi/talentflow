"""Demo data so the app is useful on first launch. Idempotent: does nothing if jobs already exist."""
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Candidate, Job, JobStatus, Stage
from app.models.entities import utcnow
from app.services.scoring import compute_score

JOBS = [
    ("Développeur full-stack senior", "Ingénierie", "Tunis", "CDI", "React, TypeScript, Node.js, PostgreSQL, Docker", 2),
    ("Ingénieur QA automatisation", "Qualité", "Tunis", "CDI", "Playwright, Selenium, Python, CI/CD, API testing", 1),
    ("Data analyst", "Data", "Sfax", "CDI", "SQL, Python, Power BI, Excel, Statistiques", 1),
    ("Product designer", "Produit", "Remote", "CDD", "Figma, Design system, Prototypage, Recherche utilisateur", 1),
    ("Chargé de recrutement IT", "RH", "Tunis", "CDI", "Sourcing, LinkedIn Recruiter, Entretien, ATS", 1),
]

# (job index, name, headline, skills, years, source, stage)
CANDIDATES = [
    (0, "Amine Bouzid", "Full-stack engineer, 6 ans", "React, TypeScript, Node.js, PostgreSQL, Docker", 6, "LinkedIn", Stage.OFFER),
    (0, "Sarra Mansouri", "Frontend lead", "React, TypeScript, GraphQL, Docker", 7, "Cooptation", Stage.TECHNICAL),
    (0, "Hichem Jlassi", "Développeur web", "React, Node.js, MySQL", 3, "Site carrière", Stage.INTERVIEW),
    (0, "Nour El Houda Ben Ali", "Ingénieure logiciel", "TypeScript, Node.js, PostgreSQL", 4, "LinkedIn", Stage.SCREENING),
    (0, "Fares Kallel", "Développeur backend", "Node.js, PostgreSQL, Docker, Redis", 5, "Welcome to the Jungle", Stage.TECHNICAL),
    (0, "Rim Chaouch", "Développeuse junior", "React, JavaScript", 1, "Site carrière", Stage.NEW),
    (0, "Oussama Triki", "Tech lead", "React, TypeScript, Node.js, PostgreSQL, Docker", 9, "Chasse de tête", Stage.REJECTED),
    (0, "Eya Gharbi", "Full-stack developer", "React, TypeScript, PostgreSQL", 3, "LinkedIn", Stage.NEW),
    (1, "Mariem Zouari", "QA engineer", "Playwright, Python, CI/CD, API testing", 4, "LinkedIn", Stage.OFFER),
    (1, "Skander Abid", "Testeur automatisation", "Selenium, Python, API testing", 3, "Cooptation", Stage.INTERVIEW),
    (1, "Ines Louati", "Analyste qualité", "Selenium, Excel", 2, "Site carrière", Stage.SCREENING),
    (1, "Marwen Dhaouadi", "SDET", "Playwright, Selenium, Python, CI/CD, API testing", 6, "Chasse de tête", Stage.TECHNICAL),
    (1, "Yosra Haddad", "QA manuel", "Tests fonctionnels, Jira", 2, "Indeed", Stage.REJECTED),
    (1, "Aymen Sassi", "Ingénieur QA", "Playwright, Python, API testing", 3, "LinkedIn", Stage.NEW),
    (2, "Khaoula Bejaoui", "Data analyst", "SQL, Python, Power BI, Excel", 3, "LinkedIn", Stage.HIRED),
    (2, "Wassim Rekik", "BI developer", "SQL, Power BI, Statistiques", 4, "Cooptation", Stage.REJECTED),
    (2, "Amira Khelifi", "Analyste de données", "SQL, Excel, Python", 2, "Site carrière", Stage.INTERVIEW),
    (2, "Bilel Nasri", "Data scientist junior", "Python, Statistiques, SQL", 1, "Indeed", Stage.SCREENING),
    (3, "Lina Ayari", "Product designer", "Figma, Design system, Prototypage, Recherche utilisateur", 5, "Dribbble", Stage.TECHNICAL),
    (3, "Mehdi Ferchichi", "UI designer", "Figma, Prototypage", 3, "LinkedIn", Stage.INTERVIEW),
    (3, "Syrine Makni", "UX researcher", "Recherche utilisateur, Figma", 4, "Cooptation", Stage.SCREENING),
    (3, "Taha Meddeb", "Graphiste", "Illustrator, Figma", 2, "Behance", Stage.NEW),
    (4, "Cyrine Ben Youssef", "Talent acquisition", "Sourcing, LinkedIn Recruiter, Entretien, ATS", 5, "LinkedIn", Stage.INTERVIEW),
    (4, "Anis Slimani", "Chargé de recrutement", "Sourcing, Entretien", 3, "Site carrière", Stage.SCREENING),
    (4, "Malek Ouerghi", "Assistant RH", "ATS, Entretien", 1, "Indeed", Stage.NEW),
]


def seed_demo_data(session: Session) -> None:
    if session.scalar(select(func.count()).select_from(Job)):
        return

    now = utcnow()
    jobs = []
    for index, (title, dept, location, contract, skills, openings) in enumerate(JOBS):
        job = Job(title=title, department=dept, location=location, contract=contract, skills=skills,
                  openings=openings, created_at=now - timedelta(days=30 - index * 4))
        session.add(job)
        jobs.append(job)
    session.flush()

    for offset, (job_index, name, headline, skills, years, source, stage) in enumerate(CANDIDATES):
        job = jobs[job_index]
        email = name.lower().replace(" ", ".").replace("é", "e").replace("è", "e") + "@example.com"
        session.add(Candidate(
            job_id=job.id, full_name=name, email=email, headline=headline, skills=skills,
            years_experience=years, source=source, stage=stage,
            score=compute_score(job.skills, skills, years), applied_at=now - timedelta(days=20 - offset % 18),
        ))

    # The data analyst opening is already filled.
    jobs[2].status = JobStatus.CLOSED
    session.commit()
