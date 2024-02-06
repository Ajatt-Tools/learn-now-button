import typing


class LearnNowConfigProtocol(typing.Protocol):

    def bool_keys(self):
        ...

    def keys(self):
        ...

    def get(self, _key):
        ...

    def __getitem__(self, _item):
        ...
