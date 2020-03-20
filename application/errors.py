class BotError(Exception):
    text: str


class InvalidGroupId(BotError):
    text = '*GROUP_ID* must be six-character string of digits and letters'


class JoinNotEnoghtArgument(BotError):
    text = 'Command /join require *GROUP_ID* argument'


class GroupNotFound(BotError):
    text = 'Group not found'


class UserHaveNoActiveGroup(BotError):
    text = 'You have no any active group. Please join group with command /join *GROUP_ID*'
