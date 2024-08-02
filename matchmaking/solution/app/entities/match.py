from statistics import median
import logging
from typing import Any
from uuid import uuid4

from .team import Team

logger = logging.getLogger(__name__)


class Match:
    id: str
    red_team: Team
    blue_team: Team

    def __init__(self, red_team: Team, blue_team: Team):
        self.id = str(uuid4())
        self.red_team = red_team
        self.blue_team = blue_team

    def calculate_honesty(self) -> int:
        median_diff = self._calculate_median_diff()
        roles_diff_sum = self._calculate_roles_diff_sum()
        honesty = median_diff + roles_diff_sum
        return honesty

    def _calculate_median_diff(self) -> int:
        red_median = median([user.mmr for user in self.red_team.users])
        blue_median = median([user.mmr for user in self.blue_team.users])
        median_diff = abs(red_median - blue_median)
        return median_diff

    def _calculate_roles_diff_sum(self) -> int:
        roles = ["top", "mid", "bot", "sup", "jungle"]
        diff_sum = 0
        for role in roles:
            red_role_mmr = self.red_team.get_user_by_role(role).mmr
            blue_role_mmr = self.blue_team.get_user_by_role(role).mmr
            diff_sum += red_role_mmr - blue_role_mmr
        return abs(diff_sum)

    def calculate_satisfaction(self) -> int:
        satisfaction = self.red_team.calculate_roles_score() + self.blue_team.calculate_roles_score()
        return satisfaction

    def calculate_time(self) -> int:
        total_time = sum(user.waiting_time for user in self.red_team.users + self.blue_team.users)
        return total_time

    def to_json(self) -> dict[str, Any]:
        match_json = {
            "match_id": self.id,
            "teams": [self.red_team.to_json(), self.blue_team.to_json()]
        }
        return match_json
