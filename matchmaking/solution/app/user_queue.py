import logging

from .entities.user import User


logger = logging.getLogger(__name__)


class UserQueue:
    users_by_time: list[User]
    _users_by_mmr: list[User]
    _current_users: list[User]

    def __init__(self, users: list[User]):
        self.users_by_time = sorted(
            users, key=(lambda u: u.waiting_time), reverse=True
        )
        self._users_by_mmr = sorted(
            users, key=(lambda u: u.mmr), reverse=True
        )

    @property
    def current_users(self) -> list[User]:
        return self._current_users

    def is_enough_users(self) -> bool:
        return len(self.users_by_time) >= 10

    def pick_next_current_users(self) -> None:
        self._current_users = []
        while len(self._current_users) < 10:
            self._pick_next_pair()

    def _pick_next_pair(self) -> None:
        user_1 = self.users_by_time[0]
        user_2 = self._get_user_with_min_mmr_diff(user_1)
        self._add_to_current_users(user_1, user_2)

    def _get_user_with_min_mmr_diff(self, user: User) -> User:
        user_mmr_index = self._users_by_mmr.index(user)
        if user_mmr_index == 0:
            target_user = self._users_by_mmr[user_mmr_index + 1]
        elif user_mmr_index == len(self._users_by_mmr) - 1:
            target_user = self._users_by_mmr[user_mmr_index - 1]
        else:
            target_user = min(
                self._users_by_mmr[user_mmr_index - 1],
                self._users_by_mmr[user_mmr_index + 1],
                key=lambda u1, u2=user: abs(u1.mmr - u2.mmr),
            )
        return target_user

    def _add_to_current_users(self, *users: User):
        self._current_users.extend(users)
        self._deque_users(*users)

    def _deque_users(self, *users: User) -> None:
        for user in users:
            try:
                self._try_to_deque_user(user)
            except ValueError:
                logger.warning("User is not in the queue")

    def _try_to_deque_user(self, user: User) -> None:
        self.users_by_time.remove(user)
        self._users_by_mmr.remove(user)
