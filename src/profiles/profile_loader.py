from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

PROFILES_DIR = Path(__file__).resolve().parents[2] / "config" / "profiles"


@dataclass(frozen=True)
class Profile:
    name: str
    description: str
    gestures: dict[str, str]  # nombre de gesto -> nombre de acción

    def action_for(self, gesture: str) -> str | None:
        return self.gestures.get(gesture)


def load_profile(profile_name: str) -> Profile:
    path = PROFILES_DIR / f"{profile_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"No existe el perfil '{profile_name}' en {PROFILES_DIR}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return Profile(
        name=data["name"],
        description=data.get("description", ""),
        gestures=data.get("gestures", {}),
    )
