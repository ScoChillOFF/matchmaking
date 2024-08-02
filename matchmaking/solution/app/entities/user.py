from typing import Any


class User:
    id: str
    mmr: int
    roles: dict[str, int]
    waiting_time: int
    current_role: str | None
    min_diff_mmr_id: str

    def __init__(
            self,
            id: str,
            mmr: int,
            roles: list[str],
            waiting_time: int,
    ):
        self.id = id
        self.mmr = mmr
        self.roles = User._make_role_preferences_dict(roles)
        self.waiting_time = waiting_time

    @staticmethod
    def _make_role_preferences_dict(roles: list[str]) -> dict[str, int]:
        preferences_values = {
            0: 3,
            1: 5,
            2: 8,
            3: 13,
            4: 21
        }
        preferences_dict = {}
        for role in roles:
            preferences_dict[role] = preferences_values[roles.index(role)]
        return preferences_dict

    def get_role_score(self) -> int | None:
        return self.roles.get(self.current_role)

    @classmethod
    def from_json(cls, json) -> "User":
        _id = json.get("user_id")
        mmr = json.get("mmr")
        roles = json.get("roles")
        waiting_time = json.get("waitingTime")
        return cls(_id, mmr, roles, waiting_time)

    def to_team_json(self) -> dict[str, Any]:
        user_json = {
            "id": self.id,
            "role": self.current_role
        }
        return user_json
