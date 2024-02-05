import typing


class LearnNowConfigProtocol(typing.Protocol):

    def bool_keys(self):
        return "bool_one", "bool_two"

    def keys(self):
        return "key_one", "key_two", "one_shortcut", "two_shortcut"

    def get(self, _key):
        return "Ctrl+x"

    def __getitem__(self, _item):
        return "Ctrl+x"

