from typing import Any
from statistics import median

import requests

from .entities.user import User
from .matchmaker import Matchmaker


class App:
    _server_url: str
    _test_name: str

    def __init__(self, server_url: str, test_name: str):
        self._server_url = server_url
        self._test_name = test_name

    def do_matchmaking(self) -> list[dict[str, Any]]:
        epoch = "00000000-0000-0000-0000-000000000000"
        is_last_epoch = False
        honesty, time, satisfaction = [], [], []
        user_pool = []
        with requests.Session() as session:
            while True:
                users = self._get_users_from_server(epoch, session) + user_pool
                is_accurately = len(users) < 1000
                matchmaker = Matchmaker(users)
                matches = matchmaker.get_matches(is_accurately)
                user_pool = matchmaker.get_users_left()
                matches_json = [match.to_json() for match in matches]
                matches_response = self._post_matches_and_get_response(matches_json, epoch, session)
                time.extend(match.calculate_time() for match in matches)
                honesty.extend(match.calculate_honesty() for match in matches)
                satisfaction.extend(match.calculate_satisfaction() for match in matches)
                if is_last_epoch:
                    self._print_statistics(honesty, satisfaction, time)
                    break
                is_last_epoch = matches_response.get("is_last_epoch")
                epoch = matches_response.get("new_epoch")

    def _get_users_from_server(self, epoch: str, session) -> list[User]:
        url = f"{self._server_url}/matchmaking/users?test_name={self._test_name}&epoch={epoch}"
        response = session.get(url, cookies=session.cookies.get_dict())
        users = [User.from_json(user) for user in response.json()]
        return users

    def _post_matches_and_get_response(self, matches: list[dict[str, Any]], epoch: str, session) -> dict[str, Any]:
        url = f"{self._server_url}/matchmaking/match?test_name={self._test_name}&epoch={epoch}"
        response = session.post(url, json=matches, cookies=session.cookies.get_dict())
        return response.json()

    def _print_statistics(self, honesty: list[int], satisfaction: list[int], time: list[int]) -> None:
        if honesty and satisfaction and time:
            print(f"{self._test_name}: {median(honesty)} {median(satisfaction)} {int(median(time) // 1000)}")
