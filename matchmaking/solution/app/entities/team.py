from typing import Any

import munkres

from .user import User


class Team:
    side: str
    users: list[User]
    average_mmr: float | None = None

    def __init__(self, users: list[User], side: str):
        self.users = users
        self.side = side

    def get_user_by_role(self, role: str) -> User:
        for user in self.users:
            if user.current_role == role:
                return user

    def get_average_mmr(self) -> float:
        if self.average_mmr is None:
            user_mmr_sum = sum([user.mmr for user in self.users])
            user_count = len(self.users)
            self.average_mmr = user_mmr_sum / user_count
        return self.average_mmr

    def distribute_roles(self) -> None:
        roles = ["bot", "jungle", "sup", "top", "mid"]
        matrix = [
            [user.roles[roles[i]] for i, _ in enumerate(roles)] for user in self.users
        ]
        assignments = munkres.Munkres().compute(matrix)
        for user_i, role_i in assignments:
            user = self.users[user_i]
            role = roles[role_i]
            user.current_role = role

    def calculate_roles_score(self) -> int | None:
        if any(r is None for r in [user.current_role for user in self.users]):
            return None
        return sum(user.get_role_score() for user in self.users)

    def to_json(self) -> dict[str, Any]:
        team_json = {
            "side": self.side,
            "users": [user.to_team_json() for user in self.users],
        }
        return team_json
