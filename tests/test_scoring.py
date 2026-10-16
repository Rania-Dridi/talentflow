from app.services import compute_score


def test_full_skill_match_with_long_experience_is_capped_at_100():
    assert compute_score("python, sql", "Python, SQL, Docker", 15) == 100


def test_partial_match_and_experience():
    # 1 of 2 skills = 30 points, 3 years = 12 points
    assert compute_score("python, sql", "python", 3) == 42


def test_no_required_skills_gives_neutral_skill_score():
    assert compute_score("", "python", 0) == 30


def test_negative_experience_is_ignored():
    assert compute_score("python", "python", -4) == 60
