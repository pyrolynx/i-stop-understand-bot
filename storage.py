import logging

import redis

# Enable logging

log = logging.getLogger(__name__)


class Storage:
    _redis: redis.Redis = None

    class Keys:
        all_groups = 'group:all'

        @classmethod
        def group(cls, group_id):
            return f'group:{group_id}'

        @classmethod
        def group_not_understand(cls, group_id):
            return f'group:{group_id}:not_understand'

        @classmethod
        def user_group(cls, user_id):
            return f'user:{user_id}'

    @classmethod
    def init(cls):
        # _redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        cls._redis = redis.Redis(decode_responses=True)

    @classmethod
    def close(cls):
        cls._redis.close()

    @classmethod
    def add_group(cls, group_id):
        if group_id in cls.get_all_groups():
            log.warning(f'Group {group_id} already exists')
            return False
        cls._redis.sadd(cls.Keys.all_groups, group_id)
        return True

    @classmethod
    def get_all_groups(cls):
        return cls._redis.smembers(cls.Keys.all_groups)

    @classmethod
    def get_group_members(cls, group_id: int):
        if group_id not in cls.get_all_groups():
            log.warning(f'Group {group_id} does not exists')
            return None
        return set(map(int, cls._redis.smembers(cls.Keys.group(group_id))))

    @classmethod
    def get_group_not_understand_members(cls, group_id: int):
        if group_id not in cls.get_all_groups():
            log.warning(f'Group {group_id} does not exists')
            return None
        return set(map(int, cls._redis.smembers(cls.Keys.group_not_understand(group_id))))

    @classmethod
    def add_user_to_group(cls, group_id: int, user_id: int):
        if group_id not in cls.get_all_groups():
            log.warning(f'User {user_id} try to add into unknown group {group_id}')
            return False
        cls._redis.sadd(cls.Keys.group(group_id), user_id)
        cls._redis.set(cls.Keys.user_group(user_id), group_id)
        return True

    @classmethod
    def get_user_group(cls, user_id: int):
        return cls._redis.get(cls.Keys.user_group(user_id))

    @classmethod
    def set_user_state(cls, user_id: int, understand: bool):
        group_id = cls.get_user_group(user_id)
        if not group_id:
            log.info(f'User {user_id} has no active groups')
            return False
        group_members = cls.get_group_members(group_id)
        if group_members is None:
            log.info(f'User {user_id} try to change state in unknown group {user_id}')
            return False

        if user_id not in group_members:
            log.warning(f'User {user_id} try change state without membership of group {group_id}')
            return False

        not_understand_members = cls.get_group_not_understand_members(group_id)
        if user_id in not_understand_members and understand:
            cls._redis.srem(cls.Keys.group_not_understand(group_id), user_id)
        elif user_id not in not_understand_members and not understand:
            cls._redis.sadd(cls.Keys.group_not_understand(group_id), user_id)
        return True

    @classmethod
    def get_user_state(cls, user_id):
        group_id = cls.get_user_group(user_id)
        if not group_id:
            log.info(f'User {user_id} has no active groups')
            return None
        group_members = cls.get_group_members(group_id)
        if group_members is None:
            log.info(f'User {user_id} try to get state of unknown group {user_id}')
            return None

        if user_id not in group_members:
            log.warning(f'User {user_id} try get state without membership of group {group_id}')
            return None

        return user_id not in cls.get_group_not_understand_members(group_id)