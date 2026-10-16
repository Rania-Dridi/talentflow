import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    app_name: str = "TalentFlow"
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR.parent / 'talentflow.db'}")
    seed_demo_data: bool = os.getenv("SEED_DEMO_DATA", "1") == "1"


settings = Settings()
