from typing import Iterable

from itertools import combinations

from .user_queue import UserQueue
from .entities.user import User
from .entities.match import Match
from .entities.team import Team


class Matchmaker:
    _queue: UserQueue

    def __init__(self, users: list[User]):
        self._queue = UserQueue(users)

    def is_next_match_available(self) -> bool:
        return self._queue.is_enough_users()

    def get_matches(self, is_acurately: bool = False) -> list[Match]:
        matches = []
        while self.is_next_match_available():
            match = self._distribute_match(is_acurately)
            matches.append(match)
        return matches

    def _distribute_match(self, is_accurately: bool = False) -> Match:
        self._queue.pick_next_current_users()
        red_team, blue_team = self._distribute_teams(is_accurately)
        match = Match(red_team, blue_team)
        return match

    def _distribute_teams(self, is_accurately: bool = False) -> tuple[Team, Team]:
        if is_accurately:
            red_users, blue_users = self._split_users_by_best_combination()
        else:
            red_users, blue_users = self._split_users_fast()
        red_team = Team(red_users, "red")
        blue_team = Team(blue_users, "blue")
        red_team.distribute_roles()
        blue_team.distribute_roles()
        return red_team, blue_team

    def _split_users_fast(self) -> tuple[list[User], list[User]]:
        paired_users = zip(self._queue.current_users[::2], self._queue.current_users[1::2])
        users_1 = []
        users_2 = []
        for i, (user_1, user_2) in enumerate(paired_users):
            min_user = min(user_1, user_2, key=lambda u: u.mmr)
            max_user = user_2 if user_1 is min_user else user_1
            if i % 2 == 0:
                users_1.append(min_user)
                users_2.append(max_user)
            else:
                users_1.append(max_user)
                users_2.append(min_user)
        return users_1, users_2

    def _split_users_by_best_combination(self) -> tuple[list[User], list[User]]:
        best_honesty_score = float("inf")
        best_split = None
        for combination in combinations(self._queue.current_users, r=5):
            users_1, users_2 = self._split_users_by_combination(combination)
            honesty_score = Matchmaker._calculate_potential_honesty(users_1, users_2)
            if honesty_score < best_honesty_score:
                best_split = (users_1, users_2)
                best_honesty_score = honesty_score
        return best_split

    def _split_users_by_combination(self, combination: Iterable[User]) -> tuple[list[User], list[User]]:
        users_1 = list(combination)
        users_2 = [user for user in self._queue.current_users if user not in users_1]
        return users_1, users_2

    @staticmethod
    def _calculate_potential_honesty(users_1: list[User], users_2: list[User]) -> int:
        honesty = 0
        for user_1, user_2 in zip(sorted(users_1, key=lambda u: u.mmr), sorted(users_2, key=lambda u: u.mmr)):
            honesty += user_1.mmr - user_2.mmr
        return abs(honesty)

    def get_users_left(self) -> list[User]:
        return self._queue.users_by_time
