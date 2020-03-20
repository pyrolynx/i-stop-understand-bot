import random

import pytest

import utils
from storage import Storage


@pytest.fixture(scope='module', autouse=True)
def storage():
    Storage.init()
    yield
    Storage.close()


@pytest.fixture
def group():
    group_id = utils.generate_group_id()
    Storage.add_group(group_id)
    yield group_id


def generate_user():
    return random.randint(10 ** 7, 10 ** 8)


def test_add_group():
    group_id = utils.generate_group_id()
    assert Storage.get_group_members(group_id) is None
    assert Storage.get_group_not_understand_members(group_id) is None
    assert group_id not in Storage.get_all_groups()

    user = generate_user()
    assert Storage.add_user_to_group(group_id, user) is False

    assert Storage.add_group(group_id)
    assert group_id in Storage.get_all_groups()

    assert not Storage.add_group(group_id)


def test_group_members(group):
    assert Storage.get_group_members(group) == set()
    assert Storage.get_group_not_understand_members(group) == set()
    user_1 = generate_user()
    Storage.add_user_to_group(group, user_1)

    assert Storage.get_user_group(user_1) == group
    assert Storage.get_group_members(group) == {user_1}
    assert user_1 not in Storage.get_group_not_understand_members(group)

    user_2 = generate_user()
    Storage.add_user_to_group(group, user_2)

    assert Storage.get_user_group(user_2) == group
    assert Storage.get_group_members(group) == {user_1, user_2}
    assert user_1 not in Storage.get_group_not_understand_members(group)


def test_user_state(group):
    user = generate_user()
    Storage.add_user_to_group(group, user)

    assert Storage.get_group_members(group) == {user}
    assert user not in Storage.get_group_not_understand_members(group)
    assert Storage.get_user_state(user) is True

    assert Storage.set_user_state(user, False)
    assert user in Storage.get_group_not_understand_members(group)
    assert Storage.get_user_state(user) is False

    assert Storage.set_user_state(user, True)
    assert user not in Storage.get_group_not_understand_members(group)
    assert Storage.get_user_state(user) is True

    user_2 = generate_user()
    assert Storage.set_user_state(user_2, False) is False
    assert Storage.get_user_state(user_2) is None

    Storage._redis.set(Storage.Keys.user_group(user_2), utils.generate_group_id())
    assert Storage.set_user_state(user_2, False) is False
    assert Storage.get_user_state(user_2) is None

    Storage._redis.set(Storage.Keys.user_group(user_2), group)
    assert Storage.set_user_state(user_2, False) is False
    assert Storage.get_user_state(user_2) is None
