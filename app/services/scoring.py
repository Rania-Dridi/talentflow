"""Candidate scoring: a transparent, explainable 0-100 score.

60 points for the share of required skills the candidate has, up to 40 points for experience
(4 points per year, capped at 10 years).
"""

SKILLS_WEIGHT = 60
EXPERIENCE_POINTS_PER_YEAR = 4
EXPERIENCE_CAP_YEARS = 10


def parse_skills(raw: str) -> set[str]:
    return {s.strip().lower() for s in raw.split(",") if s.strip()}


def compute_score(required_skills: str, candidate_skills: str, years_experience: int) -> int:
    required = parse_skills(required_skills)
    have = parse_skills(candidate_skills)
    skills_part = SKILLS_WEIGHT * (len(required & have) / len(required)) if required else SKILLS_WEIGHT / 2
    experience_part = min(max(years_experience, 0), EXPERIENCE_CAP_YEARS) * EXPERIENCE_POINTS_PER_YEAR
    return round(min(100, skills_part + experience_part))
